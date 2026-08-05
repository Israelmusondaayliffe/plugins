"""Fresh-thread dispatch, runtime attestation, and return-ingestion contracts."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.graph_engine.artifacts import ArtifactRegistry
from scripts.graph_engine.constants import NodeStatus, RunStatus
from scripts.graph_engine.dispatch import (
    PacketValidationError,
    ingest_return,
    prepare_dispatch,
    preview_dispatch,
    record_launch,
    sha256_file,
)
from scripts.graph_engine.events import EventStore
from scripts.graph_engine.models import Graph, NodeRuntimeState, RuntimeState
from scripts.graph_engine.rewrites import RewriteEngine
from scripts.graph_engine.state import StateMachine
from scripts.graph_engine.verification import Verifier
from tests.test_rewrites import TIMESTAMP, edge, node


def threaded_graph_data() -> dict[str, object]:
    report = {"artifactType": "report", "required": True}
    evaluation = {"artifactType": "evaluation-report", "required": True}
    worker = node("researcher", "worker", outputs=[report])
    worker["execution"] = {"mode": "subagent", "skill": None, "modelHint": None}
    worker["successCriteria"] = ["Research is grounded."]
    evaluator = node("skeptic", "evaluator", inputs=[report], outputs=[evaluation])
    evaluator["execution"] = {"mode": "subagent", "skill": None, "modelHint": None}
    evaluator["successCriteria"] = ["The report is independently challenged."]
    return {
        "schemaVersion": "1.0",
        "graphId": "threaded-test",
        "name": "Threaded Test",
        "goal": {
            "statement": "Produce a checked report.",
            "deliverables": [{"id": "report", "artifactType": "report", "description": "The report."}],
            "completionCriteria": ["The report exists and is independently checked."],
            "authorityNodeId": "authority",
        },
        "limits": {
            "maxConcurrentWorkers": 2,
            "maxNodeRuns": 12,
            "maxGraphVersions": 4,
            "maxEpochs": 2,
            "maxAutoRewrites": 1,
            "defaultMaxAttempts": 2,
        },
        "nodes": [
            node("authority", "authority"),
            node("controller", "controller"),
            worker,
            evaluator,
        ],
        "edges": [
            edge("authority-controller", "authority", "controller", "goal"),
            edge("controller-researcher", "controller", "researcher", "assign"),
            edge("researcher-skeptic", "researcher", "skeptic", "verify", artifact_types=["report"]),
        ],
        "rewritePolicy": {
            "automaticRiskLevels": ["low"],
            "approvalRiskLevels": ["medium", "high"],
            "prohibitedMutations": [],
        },
        "metadata": {"createdBy": "tests", "createdAt": TIMESTAMP},
    }


class DispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run_directory = Path(self.temporary.name) / "run-threaded-test"
        self.graph = Graph.from_dict(threaded_graph_data())
        self.initial = RuntimeState(
            run_id="run-threaded-test",
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
        RewriteEngine.initialize(self.run_directory, self.graph, self.initial, timestamp=TIMESTAMP)
        (self.run_directory / "artifacts.jsonl").write_text("", encoding="utf-8")
        (self.run_directory / "approvals.jsonl").write_text("", encoding="utf-8")

    def runtime(self):
        store = EventStore(self.run_directory, self.initial.run_id)
        state = StateMachine.resume(self.run_directory, store).state
        registry = ArtifactRegistry(self.run_directory, state.run_id, store)
        return state, store, registry

    def prepare(self):
        state, store, registry = self.runtime()
        launches = prepare_dispatch(
            self.run_directory,
            self.graph,
            state,
            store,
            registry,
            (),
            timestamp=TIMESTAMP,
        )
        self.assertEqual([item["nodeId"] for item in launches], ["researcher"])
        return launches[0]

    def launch(self, *, fork_turns: str = "none") -> dict[str, object]:
        prepared = self.prepare()
        record = {
            "packetType": "ThreadLaunchRecord",
            "protocolVersion": 1,
            "runId": self.initial.run_id,
            "graphVersion": 1,
            "epoch": 1,
            "nodeId": "researcher",
            "attempt": 1,
            "taskPacketPath": "node-runs/researcher/attempt-1/task-packet.json",
            "taskPacketSha256": prepared["taskPacketSha256"],
            "request": {
                **prepared["launchSpec"],
                "forkTurns": fork_turns,
                "reasoningEffort": None,
                "requestedAt": TIMESTAMP,
            },
            "response": {
                "successful": True,
                "agentId": "agent-researcher-1",
                "canonicalTaskName": "/root/og_researcher_1",
                "respondedAt": TIMESTAMP,
                "error": None,
            },
        }
        path = self.run_directory / "launch-input.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        state, store, _ = self.runtime()
        return record_launch(
            self.run_directory,
            self.graph,
            state,
            store,
            path,
            timestamp=TIMESTAMP,
        )

    def write_success_return(self) -> Path:
        artifact_path = self.run_directory / "artifacts" / "researcher" / "report.md"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("checked research", encoding="utf-8")
        launch_path = self.run_directory / "node-runs" / "researcher" / "attempt-1" / "thread-launch.json"
        task_path = launch_path.with_name("task-packet.json")
        return_path = launch_path.parent / "worker" / "return-packet.json"
        return_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "packetType": "NodeReturnPacket",
            "protocolVersion": 1,
            "runId": self.initial.run_id,
            "graphVersion": 1,
            "epoch": 1,
            "nodeId": "researcher",
            "attempt": 1,
            "agentId": "agent-researcher-1",
            "taskPacketPath": "node-runs/researcher/attempt-1/task-packet.json",
            "taskPacketSha256": sha256_file(task_path),
            "launchRecordPath": "node-runs/researcher/attempt-1/thread-launch.json",
            "launchRecordSha256": sha256_file(launch_path),
            "status": "succeeded",
            "summary": "The bounded research artifact is complete.",
            "actualWritePaths": ["artifacts/researcher/report.md"],
            "artifacts": [
                {
                    "artifactType": "report",
                    "path": "artifacts/researcher/report.md",
                    "sha256": sha256_file(artifact_path),
                    "mediaType": "text/markdown",
                }
            ],
            "evidence": [
                {
                    "path": "artifacts/researcher/report.md",
                    "sha256": sha256_file(artifact_path),
                    "kind": "artifact-inspection",
                }
            ],
            "criteria": [
                {
                    "criterion": "Research is grounded.",
                    "result": "met",
                    "evidencePaths": ["artifacts/researcher/report.md"],
                }
            ],
            "unresolvedIssues": [],
            "risks": [],
            "recommendedSignals": [],
            "authority": {
                "maySpawnWorkers": False,
                "mayApprove": False,
                "mayIntegrate": False,
                "mayUpdateControllerState": False,
                "mayAnswerUser": False,
                "mayIssueTerminalVerdict": False,
            },
        }
        return_path.write_text(json.dumps(payload), encoding="utf-8")
        return return_path

    def test_preview_is_read_only_and_prepare_creates_one_fresh_launch_spec(self) -> None:
        state, store, registry = self.runtime()
        preview = preview_dispatch(self.graph, state, registry, ())
        self.assertEqual([node.id for node in preview], ["researcher"])
        self.assertEqual(state.node_states["researcher"].status, NodeStatus.PENDING)

        prepared = self.prepare()

        self.assertEqual(prepared["launchSpec"]["tool"], "collaboration.spawn_agent")
        self.assertEqual(prepared["launchSpec"]["forkTurns"], "none")
        task = json.loads(Path(prepared["taskPacketPath"]).read_text(encoding="utf-8"))
        self.assertFalse(task["context"]["includeParentTranscript"])
        self.assertFalse(task["authorization"]["maySpawnWorkers"])
        current, _, _ = self.runtime()
        self.assertEqual(current.node_states["researcher"].status, NodeStatus.READY)

    def test_launch_requires_fresh_non_fork_runtime_evidence(self) -> None:
        with self.assertRaisesRegex(PacketValidationError, "forkTurns=none"):
            self.launch(fork_turns="all")

    def test_successful_launch_and_return_are_bound_to_state_and_artifacts(self) -> None:
        launched = self.launch()
        self.assertEqual(launched["status"], "running")
        return_path = self.write_success_return()
        state, store, registry = self.runtime()

        result = ingest_return(
            self.run_directory,
            self.graph,
            state,
            store,
            registry,
            return_path,
            timestamp=TIMESTAMP,
        )

        self.assertEqual(result["nodeStatus"], "succeeded")
        self.assertEqual(len(registry.active_artifacts("report")), 1)
        current, _, _ = self.runtime()
        self.assertEqual(current.node_states["researcher"].status, NodeStatus.SUCCEEDED)

    def test_stale_or_out_of_scope_return_fails_closed(self) -> None:
        self.launch()
        return_path = self.write_success_return()
        payload = json.loads(return_path.read_text(encoding="utf-8"))
        for change, message in (
            (("graphVersion", 2), "graphVersion"),
            (("actualWritePaths", ["../escape.txt"]), "escapes"),
        ):
            with self.subTest(change=change):
                candidate = deepcopy(payload)
                candidate[change[0]] = change[1]
                return_path.write_text(json.dumps(candidate), encoding="utf-8")
                state, store, registry = self.runtime()
                with self.assertRaisesRegex(PacketValidationError, message):
                    ingest_return(
                        self.run_directory,
                        self.graph,
                        state,
                        store,
                        registry,
                        return_path,
                        timestamp=TIMESTAMP,
                    )

    def test_task_and_launch_records_are_anchored_outside_worker_write_authority(self) -> None:
        prepared = self.prepare()
        task_path = Path(prepared["taskPacketPath"])
        dispatch_receipt = task_path.with_name("dispatch-receipt.json")
        packet = json.loads(task_path.read_text(encoding="utf-8"))
        self.assertEqual(packet["scope"]["allowedWriteRoots"][0], str((task_path.parent / "worker").resolve()))
        self.assertTrue(dispatch_receipt.is_file())

        packet["task"]["objective"] = "tampered objective"
        task_path.write_text(json.dumps(packet), encoding="utf-8")
        record = {
            "packetType": "ThreadLaunchRecord",
            "protocolVersion": 1,
            "runId": self.initial.run_id,
            "graphVersion": 1,
            "epoch": 1,
            "nodeId": "researcher",
            "attempt": 1,
            "taskPacketPath": "node-runs/researcher/attempt-1/task-packet.json",
            "taskPacketSha256": sha256_file(task_path),
            "request": {**prepared["launchSpec"], "reasoningEffort": None, "requestedAt": TIMESTAMP},
            "response": {"successful": True, "agentId": "agent-researcher-1", "canonicalTaskName": "/root/og_researcher_1", "respondedAt": TIMESTAMP, "error": None},
        }
        path = self.run_directory / "tampered-launch.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        state, store, _ = self.runtime()
        with self.assertRaisesRegex(PacketValidationError, "dispatch receipt"):
            record_launch(self.run_directory, self.graph, state, store, path, timestamp=TIMESTAMP)

    def test_return_rejects_a_launch_record_changed_after_controller_receipt(self) -> None:
        self.launch()
        launch_path = self.run_directory / "node-runs/researcher/attempt-1/thread-launch.json"
        launch = json.loads(launch_path.read_text(encoding="utf-8"))
        launch["request"]["taskName"] = "tampered-task-name"
        launch_path.write_text(json.dumps(launch), encoding="utf-8")
        return_path = self.write_success_return()
        state, store, registry = self.runtime()

        with self.assertRaisesRegex(PacketValidationError, "launchRecordSha256"):
            ingest_return(
                self.run_directory,
                self.graph,
                state,
                store,
                registry,
                return_path,
                timestamp=TIMESTAMP,
            )

    def test_terminal_verification_rejects_succeeded_subagent_without_thread_evidence(self) -> None:
        state, store, _ = self.runtime()
        machine = StateMachine(self.run_directory, state, store)
        machine.transition_node("researcher", NodeStatus.READY, timestamp=TIMESTAMP)
        machine.transition_node("researcher", NodeStatus.RUNNING, timestamp=TIMESTAMP)
        machine.transition_node("researcher", NodeStatus.SUCCEEDED, timestamp=TIMESTAMP)

        result = Verifier(self.run_directory).verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status.value, "fail")
        self.assertTrue(any("lacks task evidence" in issue for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
