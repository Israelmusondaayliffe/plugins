"""End-to-end graphctl command and exit-code contracts."""

from __future__ import annotations

from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.graph_engine.artifacts import ArtifactRegistry
from scripts.graph_engine.constants import Confidence, NodeStatus, RunStatus
from scripts.graph_engine.dispatch import sha256_file
from scripts.graph_engine.events import EventStore
from scripts.graph_engine.models import Evidence, Graph, NodeRuntimeState, RuntimeState
from scripts.graph_engine.rewrites import RewriteEngine
from tests.test_dispatch import threaded_graph_data
from tests.test_rewrites import TIMESTAMP, graph_data, node, operation


REPOSITORY = Path(__file__).resolve().parents[1]
GRAPHCTL = REPOSITORY / "scripts" / "graphctl.py"


class GraphctlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.graph_path = self.root / "graph.json"
        self.graph_path.write_text(json.dumps(graph_data()), encoding="utf-8")

    def command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GRAPHCTL), *arguments],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )

    def json_command(self, *arguments: str, expected: int = 0) -> dict[str, object]:
        completed = self.command(*arguments, "--json")
        self.assertEqual(completed.returncode, expected, completed.stderr or completed.stdout)
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            self.fail(f"invalid JSON output for {arguments}: {error}: {completed.stdout!r}")

    def init_run(self) -> Path:
        payload = self.json_command("init", str(self.graph_path), "--run-root", str(self.root / "runs"))
        return Path(str(payload["runDirectory"]))

    def test_every_documented_command_is_connected_and_json_is_valid(self) -> None:
        self.assertTrue(self.json_command("validate", str(self.graph_path))["valid"])
        run_directory = self.init_run()

        status = self.json_command("status", str(run_directory))
        self.assertEqual(status["state"]["graphVersion"], 1)
        ready = self.json_command("ready", str(run_directory))
        self.assertIn("authority", ready["readyNodeIds"])
        for target in ("ready", "running", "succeeded"):
            transition = self.json_command(
                "transition", str(run_directory), "authority", target
            )
            self.assertEqual(transition["nodeStatus"], target)

        artifact_path = run_directory / "artifacts" / "producer" / "draft.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("draft", encoding="utf-8")
        registered = self.json_command(
            "register-artifact",
            str(run_directory),
            "producer",
            "draft",
            str(artifact_path),
        )
        self.assertEqual(registered["artifact"]["nodeId"], "producer")
        signal = self.json_command("signal", str(run_directory), "budget-ratio", "0.5")
        self.assertEqual(signal["value"], 0.5)

        proposal_path = self.root / "proposal.json"
        proposal_path.write_text(
            json.dumps(
                {
                    "proposalId": "rewrite-0001",
                    "runId": "run-rewrite-test",
                    "baseGraphVersion": 1,
                    "trigger": "manual-test",
                    "evidenceEventIds": [],
                    "riskLevel": "low",
                    "reason": "Prioritize a bounded optional node.",
                    "predictedEffect": "Scheduling priority changes.",
                    "operations": [operation("set_priority", nodeId="optional-helper", priority=75)],
                    "approvalRequired": False,
                    "rollbackVersion": 1,
                }
            ),
            encoding="utf-8",
        )
        proposed = self.json_command("propose-rewrite", str(run_directory), str(proposal_path))
        self.assertEqual(proposed["proposalId"], "rewrite-0001")
        applied = self.json_command("apply-rewrite", str(run_directory), "rewrite-0001")
        self.assertEqual(applied["graphVersion"], 2)

        replay = self.json_command("replay", str(run_directory))
        self.assertEqual(replay["state"]["graphVersion"], 2)
        resume = self.json_command("resume-check", str(run_directory))
        self.assertTrue(resume["resumable"])
        text_inspection = self.json_command(
            "inspect", str(run_directory), "--format", "text"
        )
        self.assertIn("Run: run-rewrite-test", text_inspection["report"])
        mermaid = self.json_command(
            "inspect", str(run_directory), "--format", "mermaid"
        )
        self.assertIn("flowchart TD", mermaid["report"])

    def test_fresh_thread_commands_form_a_complete_cli_protocol(self) -> None:
        self.graph_path.write_text(json.dumps(threaded_graph_data()), encoding="utf-8")
        run_directory = self.init_run()
        for node_id in ("authority", "controller"):
            for target in ("ready", "running", "succeeded"):
                self.json_command("transition", str(run_directory), node_id, target)

        preview = self.json_command("dispatch-preview", str(run_directory))
        self.assertEqual(preview["readySubagentNodeIds"], ["researcher"])
        prepared = self.json_command("prepare-dispatch", str(run_directory))
        launch = prepared["launches"][0]
        launch_input = self.root / "thread-launch.json"
        launch_input.write_text(
            json.dumps(
                {
                    "packetType": "ThreadLaunchRecord",
                    "protocolVersion": 1,
                    "runId": "run-threaded-test",
                    "graphVersion": 1,
                    "epoch": 1,
                    "nodeId": "researcher",
                    "attempt": 1,
                    "taskPacketPath": "node-runs/researcher/attempt-1/task-packet.json",
                    "taskPacketSha256": launch["taskPacketSha256"],
                    "request": {
                        **launch["launchSpec"],
                        "reasoningEffort": None,
                        "requestedAt": TIMESTAMP,
                    },
                    "response": {
                        "successful": True,
                        "agentId": "agent-cli-test",
                        "canonicalTaskName": "/root/og_researcher_1",
                        "respondedAt": TIMESTAMP,
                        "error": None,
                    },
                }
            ),
            encoding="utf-8",
        )
        recorded = self.json_command(
            "record-launch", str(run_directory), str(launch_input)
        )
        self.assertEqual(recorded["status"], "running")

        artifact = run_directory / "artifacts/researcher/report.md"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("bounded CLI result", encoding="utf-8")
        attempt = run_directory / "node-runs/researcher/attempt-1"
        task_packet = attempt / "task-packet.json"
        launch_record = attempt / "thread-launch.json"
        return_packet = attempt / "worker" / "return-packet.json"
        return_packet.parent.mkdir(parents=True, exist_ok=True)
        return_packet.write_text(
            json.dumps(
                {
                    "packetType": "NodeReturnPacket",
                    "protocolVersion": 1,
                    "runId": "run-threaded-test",
                    "graphVersion": 1,
                    "epoch": 1,
                    "nodeId": "researcher",
                    "attempt": 1,
                    "agentId": "agent-cli-test",
                    "taskPacketPath": "node-runs/researcher/attempt-1/task-packet.json",
                    "taskPacketSha256": sha256_file(task_packet),
                    "launchRecordPath": "node-runs/researcher/attempt-1/thread-launch.json",
                    "launchRecordSha256": sha256_file(launch_record),
                    "status": "succeeded",
                    "summary": "The CLI protocol result is complete.",
                    "actualWritePaths": ["artifacts/researcher/report.md"],
                    "artifacts": [{"artifactType": "report", "path": "artifacts/researcher/report.md", "sha256": sha256_file(artifact), "mediaType": "text/markdown"}],
                    "evidence": [{"path": "artifacts/researcher/report.md", "sha256": sha256_file(artifact), "kind": "artifact-inspection"}],
                    "criteria": [{"criterion": "Research is grounded.", "result": "met", "evidencePaths": ["artifacts/researcher/report.md"]}],
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
            ),
            encoding="utf-8",
        )
        ingested = self.json_command(
            "ingest-return", str(run_directory), str(return_packet)
        )
        self.assertEqual(ingested["nodeStatus"], "succeeded")
        status = self.json_command("status", str(run_directory))
        self.assertEqual(status["threads"][0]["agentId"], "agent-cli-test")
        inspection = self.json_command("inspect", str(run_directory), "--format", "text")
        self.assertIn("Fresh threads:", inspection["report"])
        self.assertIn("fork=none", inspection["report"])

    def test_verify_command_returns_zero_only_for_pass_or_conditional_pass(self) -> None:
        run_directory = self.root / "complete-run"
        graph = Graph.from_dict(graph_data())
        state = RuntimeState(
            "run-complete",
            graph.graph_id,
            1,
            1,
            RunStatus.RUNNING,
            {node.id: NodeRuntimeState(node.id, NodeStatus.SUCCEEDED, completed_epoch=1) for node in graph.nodes},
        )
        RewriteEngine.initialize(run_directory, graph, state, timestamp=TIMESTAMP)
        artifact_path = run_directory / "artifacts" / "producer" / "report.md"
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("complete", encoding="utf-8")
        ArtifactRegistry(run_directory, "run-complete", EventStore(run_directory, "run-complete")).register(
            artifact_id="art-report",
            node_id="producer",
            graph_version=1,
            artifact_type="report",
            path="artifacts/producer/report.md",
            media_type="text/markdown",
            evidence=[Evidence("source://report", "Report evidence.", Confidence.HIGH)],
            timestamp=TIMESTAMP,
        )

        result = self.json_command("verify", str(run_directory))

        self.assertEqual(result["verification"]["status"], "pass")

    def test_validation_or_policy_failure_uses_exit_two_and_names_the_rule(self) -> None:
        invalid = deepcopy(graph_data())
        invalid["nodes"].append(deepcopy(invalid["nodes"][0]))
        invalid_path = self.root / "invalid.json"
        invalid_path.write_text(json.dumps(invalid), encoding="utf-8")

        completed = self.command("validate", str(invalid_path))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("OGI-01", completed.stderr)
        self.assertIn("violated rule", completed.stderr)

    def test_corrupt_runtime_state_uses_exit_three(self) -> None:
        run_directory = self.init_run()
        events = run_directory / "events.jsonl"
        events.write_text(events.read_text().replace("graph.created", "graph.damaged"), encoding="utf-8")

        result = self.json_command("status", str(run_directory), expected=3)

        self.assertEqual(result["exitCode"], 3)
        self.assertIn("corrupt", result["error"])

    def test_missing_rewrite_approval_uses_exit_four_and_is_never_synthesized(self) -> None:
        run_directory = self.init_run()
        alternate = node("alternate", "worker")
        proposal_path = self.root / "medium.json"
        proposal_path.write_text(
            json.dumps(
                {
                    "proposalId": "rewrite-0002",
                    "runId": "run-rewrite-test",
                    "baseGraphVersion": 1,
                    "trigger": "manual-test",
                    "evidenceEventIds": [],
                    "riskLevel": "medium",
                    "reason": "Add bounded alternate work.",
                    "predictedEffect": "A new worker becomes available.",
                    "operations": [
                        operation("add_node", node=alternate),
                        operation(
                            "add_edge",
                            edge={
                                "id": "controller-alternate", "source": "controller", "target": "alternate",
                                "kind": "assign", "enabled": True, "required": True, "temporal": "same_epoch",
                                "artifactTypes": [],
                                "activation": {"mode": "all", "nodeStates": [], "artifacts": [], "approvals": []},
                            },
                        ),
                    ],
                    "approvalRequired": True,
                    "rollbackVersion": 1,
                }
            ),
            encoding="utf-8",
        )
        self.json_command("propose-rewrite", str(run_directory), str(proposal_path))

        result = self.json_command(
            "apply-rewrite", str(run_directory), "rewrite-0002", expected=4
        )

        self.assertEqual(result["exitCode"], 4)
        self.assertEqual((run_directory / "approvals.jsonl").read_text(encoding="utf-8"), "")
        self.assertFalse((run_directory / "graph-versions" / "v0002.json").exists())

    def test_unexpected_internal_failure_uses_exit_one(self) -> None:
        import scripts.graphctl as graphctl

        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(graphctl, "_dispatch", side_effect=RuntimeError("unexpected")):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = graphctl.main(["validate", str(self.graph_path), "--json"])

        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout.getvalue())["exitCode"], 1)


if __name__ == "__main__":
    unittest.main()
