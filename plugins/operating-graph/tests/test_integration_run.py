"""Deterministic end-to-end and adversarial Operating Graph tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.graph_engine.artifacts import (
    ArtifactRegistry,
    UnsafeArtifactPathError,
    resolve_artifact_path,
)
from scripts.graph_engine.constants import (
    ApprovalStatus,
    ApprovalSubjectType,
    Confidence,
    EventType,
    NodeStatus,
    RunStatus,
    VerificationStatus,
)
from scripts.graph_engine.events import EventChainError, EventStore
from scripts.graph_engine.invariants import validate_graph_invariants
from scripts.graph_engine.models import (
    Approval,
    Evidence,
    Graph,
    NodeRuntimeState,
    RewriteProposal,
    RuntimeState,
)
from scripts.graph_engine.rewrites import (
    ProhibitedMutationError,
    RewriteEngine,
    RewritePolicyError,
    apply_operations,
)
from scripts.graph_engine.scheduler import get_ready_nodes
from scripts.graph_engine.state import StateMachine, replay_events
from scripts.graph_engine.validation import parse_and_validate_graph, parse_and_validate_rewritten_graph
from scripts.graph_engine.verification import Verifier
from tests.test_invariants import codes, graph as invariant_graph, valid_graph_data
from tests.test_rewrites import (
    approval as rewrite_approval,
    edge,
    graph_data as rewrite_graph_data,
    node,
    operation,
    proposal as rewrite_proposal,
)


TIMESTAMP = "2026-07-18T12:00:00Z"


def integration_graph_data() -> dict[str, object]:
    research = {"artifactType": "verified-research", "required": True}
    report = {"artifactType": "report", "required": True}
    data = {
        "schemaVersion": "1.0",
        "graphId": "integration-run",
        "name": "Integration Run",
        "goal": {
            "statement": "Produce a verified deliverable from trusted research.",
            "deliverables": [
                {"id": "final-report", "artifactType": "report", "description": "The verified report."}
            ],
            "completionCriteria": [
                "The original requested report exists and has independent approval."
            ],
            "authorityNodeId": "authority",
        },
        "limits": {
            "maxConcurrentWorkers": 1,
            "maxNodeRuns": 10,
            "maxGraphVersions": 3,
            "maxEpochs": 2,
            "maxAutoRewrites": 1,
            "defaultMaxAttempts": 2,
        },
        "nodes": [
            node("authority", "authority"),
            node("controller", "controller"),
            node("researcher", "worker", outputs=[research]),
            node("builder", "worker", critical=False, inputs=[research], outputs=[report]),
            node("evaluator", "evaluator", inputs=[report]),
        ],
        "edges": [
            edge("authority-controller", "authority", "controller", "goal"),
            edge("controller-researcher", "controller", "researcher", "assign"),
            edge(
                "researcher-builder",
                "researcher",
                "builder",
                "write",
                artifact_types=["verified-research"],
            ),
            edge(
                "builder-evaluator",
                "builder",
                "evaluator",
                "verify",
                artifact_types=["report"],
            ),
        ],
        "rewritePolicy": {
            "automaticRiskLevels": ["low"],
            "approvalRiskLevels": ["medium", "high"],
            "prohibitedMutations": [],
        },
        "metadata": {"createdBy": "tests", "createdAt": TIMESTAMP},
    }
    for item in data["nodes"]:
        item["priority"] = {
            "authority": 100,
            "controller": 90,
            "researcher": 80,
            "builder": 70,
            "evaluator": 60,
        }[item["id"]]
    return data


def replacement_node() -> dict[str, object]:
    research = {"artifactType": "verified-research", "required": True}
    report = {"artifactType": "report", "required": True}
    replacement = node(
        "replacement-builder",
        "worker",
        inputs=[research],
        outputs=[report],
    )
    replacement["label"] = "Replacement Builder"
    replacement["purpose"] = "Build the report with an approved alternate strategy."
    replacement["priority"] = 75
    return replacement


class FakeExecutor:
    """Test-only deterministic executor that drives controller APIs."""

    def __init__(self, run_directory: Path) -> None:
        self.run_directory = run_directory
        self.graph = Graph.from_dict(integration_graph_data())
        initial = RuntimeState(
            run_id="run-integration",
            graph_id=self.graph.graph_id,
            graph_version=1,
            epoch=1,
            status=RunStatus.RUNNING,
            node_states={
                item.id: NodeRuntimeState(
                    item.id,
                    NodeStatus.SUCCEEDED if item.id in {"authority", "controller"} else NodeStatus.PENDING,
                    completed_epoch=1 if item.id in {"authority", "controller"} else None,
                )
                for item in self.graph.nodes
            },
        )
        self.engine = RewriteEngine.initialize(
            run_directory, self.graph, initial, timestamp=TIMESTAMP
        )
        self.store = EventStore(run_directory, initial.run_id)
        self.machine = StateMachine.resume(run_directory, self.store)
        self.registry = ArtifactRegistry(run_directory, initial.run_id, self.store)
        (run_directory / "approvals.jsonl").write_text("", encoding="utf-8")
        self.failed_artifact_paths: list[str] = []

    @property
    def state(self) -> RuntimeState:
        return self.machine.state

    def _ready(self, node_id: str) -> None:
        ready = get_ready_nodes(
            self.current_graph(),
            self.state,
            artifact_registry=self.registry,
            approvals=self.approvals(),
        )
        self.assert_ids(ready, node_id)
        self.machine.transition_node(node_id, NodeStatus.READY, timestamp=TIMESTAMP)

    @staticmethod
    def assert_ids(nodes: tuple[object, ...], expected: str) -> None:
        actual = [item.id for item in nodes]
        if expected not in actual:
            raise AssertionError(f"expected {expected!r} in ready nodes {actual!r}")

    def succeed(self, node_id: str) -> None:
        self._ready(node_id)
        self.machine.transition_node(node_id, NodeStatus.RUNNING, timestamp=TIMESTAMP)
        self.machine.transition_node(node_id, NodeStatus.SUCCEEDED, timestamp=TIMESTAMP)

    def fail(self, node_id: str, attempt: int) -> None:
        if attempt == 1:
            self._ready(node_id)
        else:
            self.machine.transition_node(
                node_id,
                NodeStatus.READY,
                timestamp=TIMESTAMP,
                max_attempts=2,
                required_inputs_exist=True,
                approval_outstanding=False,
            )
        self.machine.transition_node(node_id, NodeStatus.RUNNING, timestamp=TIMESTAMP)
        relative = f"artifacts/{node_id}/failed-attempt-{attempt}.md"
        path = self.run_directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"untrusted failed attempt {attempt}", encoding="utf-8")
        self.failed_artifact_paths.append(relative)
        self.machine.transition_node(
            node_id,
            NodeStatus.FAILED,
            timestamp=TIMESTAMP,
            error=f"deterministic failure {attempt}",
        )

    def register(
        self,
        *,
        artifact_id: str,
        node_id: str,
        artifact_type: str,
        content: str,
    ) -> None:
        relative = f"artifacts/{node_id}/{artifact_id}.md"
        path = self.run_directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.registry.register(
            artifact_id=artifact_id,
            node_id=node_id,
            graph_version=self.state.graph_version,
            artifact_type=artifact_type,
            path=relative,
            media_type="text/markdown",
            evidence=[Evidence("source://integration", "Deterministic integration evidence.", Confidence.HIGH)],
            timestamp=TIMESTAMP,
        )

    def record_approval(self, approval: Approval) -> None:
        path = self.run_directory / "approvals.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(approval.to_dict(), sort_keys=True, separators=(",", ":")) + "\n")
        self.store.append(
            EventType.APPROVAL_GRANTED,
            {"approval": approval.to_dict()},
            self.state.graph_version,
            timestamp=TIMESTAMP,
        )

    def approvals(self) -> tuple[Approval, ...]:
        path = self.run_directory / "approvals.jsonl"
        return tuple(
            Approval.from_dict(json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
        )

    def apply_replacement(self) -> None:
        candidate = RewriteProposal.from_dict(
            {
                "proposalId": "rewrite-replace-builder",
                "runId": self.state.run_id,
                "baseGraphVersion": 1,
                "trigger": "repeated-node-failure",
                "evidenceEventIds": [
                    event.event_id
                    for event in self.store.read_all()
                    if event.type == EventType.NODE_FAILED
                ],
                "riskLevel": "high",
                "reason": "The builder failed twice using the same strategy.",
                "predictedEffect": "Use an approved replacement builder.",
                "operations": [
                    operation("disable_node", nodeId="builder"),
                    operation("disable_edge", edgeId="researcher-builder"),
                    operation("disable_edge", edgeId="builder-evaluator"),
                    operation("add_node", node=replacement_node()),
                    operation(
                        "add_edge",
                        edge=edge(
                            "researcher-replacement",
                            "researcher",
                            "replacement-builder",
                            "write",
                            artifact_types=["verified-research"],
                        ),
                    ),
                    operation(
                        "add_edge",
                        edge=edge(
                            "replacement-evaluator",
                            "replacement-builder",
                            "evaluator",
                            "verify",
                            artifact_types=["report"],
                        ),
                    ),
                ],
                "approvalRequired": True,
                "rollbackVersion": 1,
            }
        )
        self.engine.propose(candidate, timestamp=TIMESTAMP)
        rewrite_approval = Approval(
            approval_id="approval-rewrite",
            run_id=self.state.run_id,
            subject_type=ApprovalSubjectType.REWRITE,
            subject_id=candidate.proposal_id,
            requested_by="controller",
            required_from="authority",
            status=ApprovalStatus.GRANTED,
            requested_at=TIMESTAMP,
            resolved_at=TIMESTAMP,
            resolved_by="authority",
            reason="Approved deterministic replacement.",
        )
        self.record_approval(rewrite_approval)
        self.store.append(
            EventType.REWRITE_APPROVED,
            {"proposalId": candidate.proposal_id, "approvalId": rewrite_approval.approval_id},
            self.state.graph_version,
            timestamp=TIMESTAMP,
        )
        self.engine.apply(
            candidate.proposal_id,
            approvals=[rewrite_approval],
            timestamp=TIMESTAMP,
        )
        self.machine = StateMachine.resume(self.run_directory, self.store)

    def current_graph(self) -> Graph:
        return Graph.from_dict(
            json.loads((self.run_directory / "graph.json").read_text(encoding="utf-8"))
        )

    def write_packet(self, node_id: str) -> dict[str, object]:
        node = next(item for item in self.current_graph().nodes if item.id == node_id)
        available = [item.to_dict() for item in self.registry.active_artifacts()]
        required_types = {item.artifact_type for item in node.inputs if item.required}
        packet = {
            "runId": self.state.run_id,
            "graphVersion": self.state.graph_version,
            "epoch": self.state.epoch,
            "node": node.to_dict(),
            "goal": self.current_graph().goal.to_dict(),
            "requiredInputs": [item for item in available if item["type"] in required_types],
            "availableArtifacts": available,
            "successCriteria": list(node.success_criteria),
            "outputDirectory": str((self.run_directory / "artifacts" / node_id).resolve()),
            "constraints": [
                "Do not modify graph state.",
                "Do not modify another node's files.",
                "Do not perform external side effects without explicit approval.",
                "Return uncertainty and blockers explicitly.",
            ],
        }
        path = self.run_directory / "node-runs" / node_id / "attempt-1" / "packet.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(packet, sort_keys=True), encoding="utf-8")
        return packet


class IntegrationRunTests(unittest.TestCase):
    def test_repeated_failure_rewrite_and_replacement_complete_deterministically(self) -> None:
        with TemporaryDirectory() as directory:
            executor = FakeExecutor(Path(directory))
            original_version = (Path(directory) / "graph-versions" / "v0001.json").read_bytes()

            executor.succeed("researcher")
            executor.register(
                artifact_id="art-research",
                node_id="researcher",
                artifact_type="verified-research",
                content="trusted research",
            )
            executor.fail("builder", 1)
            executor.fail("builder", 2)

            self.assertFalse(executor.registry.satisfies_activation(["report"]))
            self.assertEqual(
                [item.path for item in executor.registry.read_all()],
                ["artifacts/researcher/art-research.md"],
            )
            executor.apply_replacement()

            packet = executor.write_packet("replacement-builder")
            self.assertEqual(
                [item["artifactId"] for item in packet["requiredInputs"]],
                ["art-research"],
            )
            self.assertEqual(packet["goal"], Graph.from_dict(integration_graph_data()).goal.to_dict())
            executor.succeed("replacement-builder")
            executor.register(
                artifact_id="art-report",
                node_id="replacement-builder",
                artifact_type="report",
                content="verified report",
            )
            executor.succeed("evaluator")
            executor.record_approval(
                Approval(
                    approval_id="approval-report",
                    run_id=executor.state.run_id,
                    subject_type=ApprovalSubjectType.ARTIFACT,
                    subject_id="art-report",
                    requested_by="controller",
                    required_from="evaluator",
                    status=ApprovalStatus.GRANTED,
                    requested_at=TIMESTAMP,
                    resolved_at=TIMESTAMP,
                    resolved_by="evaluator",
                    reason="Independent evaluator approved the replacement output.",
                )
            )

            verification = Verifier(Path(directory)).verify(timestamp=TIMESTAMP)
            self.assertEqual(verification.status, VerificationStatus.PASS)
            self.assertEqual(
                [item["criterion"] for item in verification.criteria],
                Graph.from_dict(integration_graph_data()).goal.completion_criteria,
            )
            executor.machine = StateMachine.resume(Path(directory), executor.store)

            events = executor.store.read_all()
            self.assertEqual(events[-1].type, EventType.RUN_COMPLETED)
            self.assertTrue(all(event.event_hash == event.calculated_hash() for event in events))
            self.assertEqual([event.sequence for event in events], list(range(1, len(events) + 1)))
            self.assertEqual(executor.state.graph_version, 2)
            self.assertEqual(executor.state.status, RunStatus.COMPLETED)
            self.assertEqual(
                sorted(path.name for path in (Path(directory) / "graph-versions").glob("v*.json")),
                ["v0001.json", "v0002.json"],
            )
            self.assertEqual(
                (Path(directory) / "graph-versions" / "v0001.json").read_bytes(),
                original_version,
            )
            self.assertEqual(replay_events(events).to_dict(), executor.state.to_dict())
            self.assertTrue(
                any(
                    event.type == EventType.VERIFICATION_STARTED
                    and event.payload["originalGraphVersion"] == 1
                    for event in events
                )
            )


class AdversarialSafetyTests(unittest.TestCase):
    def test_worker_cannot_change_its_own_status_file(self) -> None:
        from scripts.graphctl import RuntimeCorruptionError, _runtime

        with TemporaryDirectory() as directory:
            run_directory = Path(directory)
            FakeExecutor(run_directory)
            state_path = run_directory / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["nodeStates"]["researcher"]["status"] = "succeeded"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeCorruptionError, "differs from event replay"):
                _runtime(run_directory)

    def test_graph_condition_containing_python_code_is_rejected(self) -> None:
        data = integration_graph_data()
        data["nodes"][2]["localLoop"]["stopCondition"] = "__import__('os').system('touch /tmp/owned')"

        self.assertIn("OGI-19", codes(parse_and_validate_graph(data).violations))

    def test_path_traversal_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(UnsafeArtifactPathError, "escapes"):
                resolve_artifact_path(Path(directory), "builder", "artifacts/builder/../../state.json")

    def test_evaluator_cannot_approve_its_own_output(self) -> None:
        data = valid_graph_data()
        data["edges"].append(edge("evaluator-self-approval", "evaluator", "evaluator", "approve"))

        self.assertIn("OGI-11", codes(validate_graph_invariants(invariant_graph(data))))

    def test_rewrite_cannot_change_original_goal(self) -> None:
        original = Graph.from_dict(valid_graph_data())
        changed = deepcopy(valid_graph_data())
        changed["goal"]["statement"] = "Replace the user's original goal."

        result = parse_and_validate_rewritten_graph(changed, original_graph=original)

        self.assertIn("OGI-07", codes(result.violations))

    def test_rewrite_cannot_remove_required_approval(self) -> None:
        graph = Graph.from_dict(valid_graph_data())

        with self.assertRaisesRegex(ProhibitedMutationError, "approval boundary"):
            apply_operations(graph, [operation("disable_edge", edgeId="authority-to-publisher")])

    def test_rewrite_cannot_exceed_graph_version_limit(self) -> None:
        data = rewrite_graph_data()
        data["limits"]["maxGraphVersions"] = 1
        graph = Graph.from_dict(data)
        state = RuntimeState(
            "run-001",
            graph.graph_id,
            1,
            1,
            RunStatus.RUNNING,
            {item.id: NodeRuntimeState(item.id, NodeStatus.PENDING) for item in graph.nodes},
        )
        with TemporaryDirectory() as directory:
            engine = RewriteEngine.initialize(Path(directory), graph, state, timestamp=TIMESTAMP)
            candidate = rewrite_proposal(operation("set_priority", nodeId="producer", priority=70))
            engine.propose(candidate, timestamp=TIMESTAMP)

            with self.assertRaisesRegex(RewritePolicyError, "version budget is exhausted"):
                engine.apply(candidate.proposal_id, timestamp=TIMESTAMP)

    def test_corrupted_event_history_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            run_directory = Path(directory)
            executor = FakeExecutor(run_directory)
            event_path = run_directory / "events.jsonl"
            event_path.write_text(
                event_path.read_text(encoding="utf-8").replace("graph.created", "graph.validated", 1),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(EventChainError, "event hash mismatch"):
                executor.store.read_all()

    def test_infinite_same_epoch_cycle_is_rejected(self) -> None:
        data = valid_graph_data()
        data["edges"].append(edge("evaluator-producer-loop", "evaluator", "producer", "learn"))

        violations = codes(validate_graph_invariants(invariant_graph(data)))

        self.assertIn("OGI-13", violations)
        self.assertIn("OGI-14", violations)

    def test_unbounded_next_epoch_cycle_is_rejected(self) -> None:
        data = valid_graph_data()
        feedback = edge("evaluator-producer-feedback", "evaluator", "producer", "learn")
        feedback["temporal"] = "next_epoch"
        data["edges"].append(feedback)
        data["limits"]["maxEpochs"] = 0

        self.assertIn("OGI-15", codes(validate_graph_invariants(invariant_graph(data))))

    def test_publication_without_authority_approval_is_rejected(self) -> None:
        data = valid_graph_data()
        data["edges"][4]["enabled"] = False

        self.assertIn("OGI-12", codes(validate_graph_invariants(invariant_graph(data))))

    def test_disabled_critical_node_cannot_satisfy_completion(self) -> None:
        data = rewrite_graph_data()
        graph = Graph.from_dict(data)
        state = RuntimeState(
            "run-001",
            graph.graph_id,
            1,
            1,
            RunStatus.RUNNING,
            {
                item.id: NodeRuntimeState(item.id, NodeStatus.SUCCEEDED, completed_epoch=1)
                for item in graph.nodes
            },
        )
        with TemporaryDirectory() as directory:
            run_directory = Path(directory)
            engine = RewriteEngine.initialize(run_directory, graph, state, timestamp=TIMESTAMP)
            candidate = rewrite_proposal(
                operation("disable_node", nodeId="critical-helper"),
                risk="high",
            )
            approval = rewrite_approval()
            engine.propose(candidate, timestamp=TIMESTAMP)
            engine.apply(candidate.proposal_id, approvals=[approval], timestamp=TIMESTAMP)
            (run_directory / "approvals.jsonl").write_text(
                json.dumps(approval.to_dict(), sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            artifact_path = run_directory / "artifacts" / "producer" / "report.md"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("verified report", encoding="utf-8")
            ArtifactRegistry(
                run_directory,
                state.run_id,
                EventStore(run_directory, state.run_id),
            ).register(
                artifact_id="art-report",
                node_id="producer",
                graph_version=2,
                artifact_type="report",
                path="artifacts/producer/report.md",
                media_type="text/markdown",
                evidence=[Evidence("source://report", "The report is supported.", Confidence.HIGH)],
                timestamp=TIMESTAMP,
            )

            result = Verifier(run_directory).verify(timestamp=TIMESTAMP)

            self.assertEqual(result.status, VerificationStatus.FAIL)
            self.assertTrue(any("critical node 'critical-helper' is disabled" in issue for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
