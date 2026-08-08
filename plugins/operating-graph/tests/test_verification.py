"""Terminal verification and report rendering contracts."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.graph_engine.artifacts import ArtifactRegistry
from scripts.graph_engine.constants import Confidence, NodeStatus, RunStatus, VerificationStatus
from scripts.graph_engine.events import EventStore
from scripts.graph_engine.models import Evidence, Graph, NodeRuntimeState, RuntimeState
from scripts.graph_engine.reporting import render_json, render_mermaid, render_text
from scripts.graph_engine.rewrites import RewriteEngine
from scripts.graph_engine.verification import Verifier
from tests.test_rewrites import TIMESTAMP, graph_data


class VerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run_directory = Path(self.temporary.name)

    def initialize(
        self,
        *,
        statuses: dict[str, NodeStatus] | None = None,
        with_artifact: bool = True,
        with_evidence: bool = True,
        graph_payload: dict[str, object] | None = None,
    ) -> Verifier:
        graph = Graph.from_dict(graph_payload or graph_data())
        node_states = {
            node.id: NodeRuntimeState(
                node.id,
                (statuses or {}).get(node.id, NodeStatus.SUCCEEDED),
                completed_epoch=1,
            )
            for node in graph.nodes
        }
        state = RuntimeState("run-001", graph.graph_id, 1, 1, RunStatus.RUNNING, node_states)
        RewriteEngine.initialize(self.run_directory, graph, state, timestamp=TIMESTAMP)
        if with_artifact:
            artifact_path = self.run_directory / "artifacts" / "producer" / "report.md"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("verified report", encoding="utf-8")
            registry = ArtifactRegistry(
                self.run_directory,
                "run-001",
                EventStore(self.run_directory, "run-001"),
            )
            registry.register(
                artifact_id="art-report",
                node_id="producer",
                graph_version=1,
                artifact_type="report",
                path="artifacts/producer/report.md",
                media_type="text/markdown",
                evidence=(
                    [Evidence("source://report", "The report is supported.", Confidence.HIGH)]
                    if with_evidence
                    else []
                ),
                timestamp=TIMESTAMP,
            )
        return Verifier(self.run_directory)

    def test_successful_completion_returns_pass_and_emits_terminal_event(self) -> None:
        result = self.initialize().verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.PASS)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.evidence_artifact_ids, ["art-report"])
        event_types = [item.type.value for item in EventStore(self.run_directory, "run-001").read_all()]
        self.assertEqual(
            event_types[-3:],
            ["verification.started", "verification.passed", "run.completed"],
        )
        state = RuntimeState.from_dict(
            json.loads((self.run_directory / "state.json").read_text(encoding="utf-8"))
        )
        self.assertEqual(state.status, RunStatus.COMPLETED)

    def test_missing_deliverable_fails_against_the_original_goal(self) -> None:
        result = self.initialize(with_artifact=False).verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("deliverable 'report'" in issue and "missing" in issue for issue in result.issues))
        state = RuntimeState.from_dict(
            json.loads((self.run_directory / "state.json").read_text(encoding="utf-8"))
        )
        self.assertEqual(state.status, RunStatus.RUNNING)

    def test_failed_artifact_integrity_check_fails(self) -> None:
        verifier = self.initialize()
        (self.run_directory / "artifacts" / "producer" / "report.md").write_text("tampered", encoding="utf-8")

        result = verifier.verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("SHA-256 mismatch" in issue for issue in result.issues))

    def test_missing_independent_evaluation_fails(self) -> None:
        verifier = self.initialize(statuses={"reviewer": NodeStatus.PENDING})

        result = verifier.verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("independent evaluator" in issue for issue in result.issues))

    def test_incomplete_required_approval_fails_without_creating_one(self) -> None:
        payload = deepcopy(graph_data())
        payload["edges"][1]["activation"]["approvals"] = ["approval-producer"]
        verifier = self.initialize(graph_payload=payload)

        result = verifier.verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("approval 'approval-producer' is not granted" in issue for issue in result.issues))
        self.assertFalse((self.run_directory / "approvals.jsonl").exists())

    def test_unresolved_critical_node_fails(self) -> None:
        result = self.initialize(statuses={"critical-helper": NodeStatus.BLOCKED}).verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("critical node 'critical-helper' remains blocked" in issue for issue in result.issues))

    def test_noncritical_limitations_return_conditional_pass_with_explicit_issue(self) -> None:
        result = self.initialize(statuses={"optional-helper": NodeStatus.FAILED}).verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.CONDITIONAL_PASS)
        self.assertTrue(any("non-critical node 'optional-helper' remains failed" in issue for issue in result.issues))
        state = RuntimeState.from_dict(
            json.loads((self.run_directory / "state.json").read_text(encoding="utf-8"))
        )
        self.assertEqual(state.status, RunStatus.COMPLETED)

    def test_terminal_deliverable_requires_evidence_provenance(self) -> None:
        result = self.initialize(with_evidence=False).verify(timestamp=TIMESTAMP)

        self.assertEqual(result.status, VerificationStatus.FAIL)
        self.assertTrue(any("has no evidence provenance" in issue for issue in result.issues))

    def test_text_json_and_mermaid_reports_are_deterministic_and_machine_readable(self) -> None:
        verifier = self.initialize()
        result = verifier.verify(timestamp=TIMESTAMP)
        graph = Graph.from_dict(json.loads((self.run_directory / "graph.json").read_text()))
        state = RuntimeState.from_dict(json.loads((self.run_directory / "state.json").read_text()))

        text_report = render_text(result)
        json_report = render_json(result)
        mermaid_report = render_mermaid(graph, state, result)

        self.assertIn("Verification: pass", text_report)
        self.assertEqual(json.loads(json_report)["status"], "pass")
        self.assertIn("flowchart TD", mermaid_report)
        self.assertIn("producer --> reviewer", mermaid_report)
        self.assertIn("class producer succeeded", mermaid_report)


if __name__ == "__main__":
    unittest.main()
