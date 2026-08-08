"""Fail-closed tests for the Fable Advisor packet validator (stdlib unittest)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parents[1] / "skills" / "fable-advisor" / "scripts" / "validate_packets.py"
spec = importlib.util.spec_from_file_location("fa_validate_packets", VALIDATOR)
vp = importlib.util.module_from_spec(spec)
sys.modules["fa_validate_packets"] = vp
spec.loader.exec_module(vp)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, data: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return sha_file(path)


class Fixture:
    """Builds one complete, internally consistent run under a tmp root."""

    def __init__(self, root: Path):
        self.root = root
        self.run = ".fable-advisor/runs/r1"
        self.run_dir = root / self.run

    def rel(self, *parts: str) -> str:
        return "/".join((self.run, *parts))

    def build(self, *, second_task_scope: str | None = None, dag_override=None, auth_model=None,
              auth_definition=None) -> dict:
        plan_path = self.run_dir / "plan.md"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text("# Approved plan\n", encoding="utf-8")
        plan = {"status": "approved", "version": 1, "path": self.rel("plan.md"), "sha256": sha_file(plan_path)}

        authorization = {
            "task_id": "T1",
            "classification": "complex",
            "role": "worker",
            "agent_definition": auth_definition or "fa-worker-complex",
            "model": auth_model or "claude-opus-4-8",
            "effort": "xhigh",
            "dependencies": [],
            "allowed_write_paths": [self.rel("artifacts/T1")],
            "input_paths": [{"path": plan["path"], "sha256": plan["sha256"]}],
            "expected_output": {"description": "one output file", "paths": [self.rel("artifacts/T1/output.md")]},
            "acceptance_criteria": [{"id": "C1", "description": "output exists"}],
            "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            "evidence_commands": ["test -f output.md"],
            "stop_conditions": ["scope violation"],
            "limits": {"max_attempts": 3, "max_turns": 80, "max_elapsed_minutes": 60},
        }
        authorizations = [authorization]
        dag = [{"task_id": "T1", "dependencies": []}]
        if second_task_scope is not None:
            second = dict(authorization)
            second.update(
                task_id="T2",
                classification="light",
                agent_definition="fa-worker-light",
                model="claude-sonnet-5",
                effort="medium",
                allowed_write_paths=[second_task_scope],
                expected_output={"description": "second output", "paths": [second_task_scope + "/out2.md"]},
                limits={"max_attempts": 3, "max_turns": 40, "max_elapsed_minutes": 30},
            )
            authorizations.append(second)
            dag.append({"task_id": "T2", "dependencies": []})
        if dag_override is not None:
            dag = dag_override

        manifest = {
            "packet_type": "FableAdvisorRunManifest",
            "protocol_version": 1,
            "run_id": "r1",
            "mode": "standalone",
            "activation": {"type": "explicit", "quoted_request": "Use Fable Advisor to build X", "recorded_at": "2026-08-08T15:00:00Z"},
            "plan": plan,
            "goal": "build X",
            "criteria": [{"id": "C1", "description": "output exists"}],
            "runtime": {
                "claude_code_version": "2.1.222",
                "entrypoint": "claude-desktop",
                "parent_session_id": "sess-1",
                "parent_model": "claude-fable-5",
                "spawn_mechanism": "agent_tool",
            },
            "task_dag": dag,
            "task_authorization": authorizations,
            "budget": {"max_task_launches": 24, "max_concurrency": 8, "max_review_rounds": 3, "max_repair_rounds": 3, "max_elapsed_minutes": 240},
            "write_policy": {
                "mode": "disjoint_targets",
                "require_disjoint_active_scopes": True,
                "allow_unlisted_writes": False,
                "allowed_write_roots": [self.rel("artifacts")],
            },
            "prohibited_actions": sorted(vp.PROHIBITED_ACTIONS),
            "authority": {surface: "parent" for surface in vp.AUTHORITY_SURFACES},
        }
        manifest_path = self.run_dir / "run-manifest.json"
        manifest_sha = write_json(manifest_path, manifest)

        packet = {
            "packet_type": "FableAdvisorTaskPacket",
            "protocol_version": 1,
            "run_id": "r1",
            "task_id": "T1",
            "run_manifest_path": self.rel("run-manifest.json"),
            "run_manifest_sha256": manifest_sha,
            "plan": plan,
            "task": {"classification": "complex", "objective": "produce output.md", "dependencies": []},
            "authorization": authorization,
            "worker": {"role": "worker", "agent_definition": authorization["agent_definition"], "model": authorization["model"], "effort": authorization["effort"], "fresh_instance": True, "mechanism": "agent_tool"},
            "input_paths": authorization["input_paths"],
            "expected_output": authorization["expected_output"],
            "acceptance_criteria": authorization["acceptance_criteria"],
            "tools": authorization["tools"],
            "scope": {"allowed_write_paths": authorization["allowed_write_paths"], "read_paths": [plan["path"]]},
            "evidence_commands": authorization["evidence_commands"],
            "stop_conditions": authorization["stop_conditions"],
            "limits": authorization["limits"],
            "context": {"delivery": "bounded_packet_only", "include_parent_transcript": False, "include_hidden_reasoning": False, "reference_paths": []},
        }
        packet_path = self.run_dir / "tasks" / "T1.task.json"
        packet_sha = write_json(packet_path, packet)

        artifact_path = self.run_dir / "artifacts" / "T1" / "output.md"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("built output\n", encoding="utf-8")

        spawn_sha = write_json(self.run_dir / "evidence" / "T1.spawn.json", {
            "record_type": "FableAdvisorSpawnRecord",
            "protocol_version": 1,
            "run_id": "r1",
            "subject_type": "task",
            "subject_id": "T1",
            "agent_definition": authorization["agent_definition"],
            "requested_model": authorization["model"],
            "requested_effort": authorization["effort"],
            "mechanism": "agent_tool",
            "runtime_id": "agent-abc",
            "spawned_at": "2026-08-08T15:01:00Z",
        })
        model_sha = write_json(self.run_dir / "evidence" / "T1.model.json", {
            "record_type": "FableAdvisorModelRecord",
            "protocol_version": 1,
            "run_id": "r1",
            "subject_type": "task",
            "subject_id": "T1",
            "requested_model": authorization["model"],
            "observed_models": [authorization["model"]],
            "attestation": "verified",
            "source": "agent transcript",
            "reason": None,
        })
        cmd_sha = write_json(self.run_dir / "evidence" / "T1-cmd0.json", {
            "record_type": "FableAdvisorCommandEvidence",
            "protocol_version": 1,
            "run_id": "r1",
            "subject_type": "task",
            "subject_id": "T1",
            "bound_packet_path": self.rel("tasks/T1.task.json"),
            "bound_packet_sha256": packet_sha,
            "command": "test -f output.md",
            "exit_code": 0,
            "stdout": "",
            "stdout_sha256": sha_text(""),
            "stderr": "",
            "stderr_sha256": sha_text(""),
        })

        ret = {
            "packet_type": "FableAdvisorReturnPacket",
            "protocol_version": 1,
            "run_id": "r1",
            "task_id": "T1",
            "task_packet_path": self.rel("tasks/T1.task.json"),
            "task_packet_sha256": packet_sha,
            "plan": plan,
            "status": "succeeded",
            "status_evidence": "output built and command exit 0",
            "scope": {"allowed_write_paths": authorization["allowed_write_paths"], "writes_observed": [self.rel("artifacts/T1/output.md")]},
            "artifacts": [{"path": self.rel("artifacts/T1/output.md"), "sha256": sha_file(artifact_path), "kind": "document"}],
            "criterion_results": [{"id": "C1", "result": "met", "evidence": "file exists"}],
            "commands": [{"command": "test -f output.md", "exit_code": 0, "evidence_path": self.rel("evidence/T1-cmd0.json"), "evidence_sha256": cmd_sha}],
            "runtime_attestation": {
                "agent_definition": authorization["agent_definition"],
                "requested_model": authorization["model"],
                "requested_effort": authorization["effort"],
                "runtime_id": "agent-abc",
                "spawn_record": {"path": self.rel("evidence/T1.spawn.json"), "sha256": spawn_sha},
                "model_record": {"path": self.rel("evidence/T1.model.json"), "sha256": model_sha},
            },
            "uncertainties": [],
            "risks": [],
            "next_action": "integrate",
        }
        return_path = self.run_dir / "returns" / "T1.return.json"
        return_sha = write_json(return_path, ret)

        review_spawn_sha = write_json(self.run_dir / "evidence" / "review-1.spawn.json", {
            "record_type": "FableAdvisorSpawnRecord",
            "protocol_version": 1,
            "run_id": "r1",
            "subject_type": "review",
            "subject_id": "round-1",
            "agent_definition": "fa-reviewer",
            "requested_model": "claude-fable-5",
            "requested_effort": "xhigh",
            "mechanism": "agent_tool",
            "runtime_id": "agent-rev1",
            "spawned_at": "2026-08-08T15:20:00Z",
        })
        review_cmd_sha = write_json(self.run_dir / "evidence" / "review-1-cmd0.json", {
            "record_type": "FableAdvisorCommandEvidence",
            "protocol_version": 1,
            "run_id": "r1",
            "subject_type": "review",
            "subject_id": "round-1",
            "bound_packet_path": None,
            "bound_packet_sha256": None,
            "command": "test -f output.md",
            "exit_code": 0,
            "stdout": "",
            "stdout_sha256": sha_text(""),
            "stderr": "",
            "stderr_sha256": sha_text(""),
        })
        review = {
            "packet_type": "FableAdvisorReviewPacket",
            "protocol_version": 1,
            "run_id": "r1",
            "review_round": 1,
            "verdict": "accepted",
            "reviewed": [{
                "task_packet": {"path": self.rel("tasks/T1.task.json"), "sha256": packet_sha},
                "return_packet": {"path": self.rel("returns/T1.return.json"), "sha256": return_sha},
            }],
            "plan": plan,
            "candidate": [{"path": self.rel("artifacts/T1/output.md"), "sha256": sha_file(artifact_path)}],
            "reproduction_commands": [{"command": "test -f output.md", "exit_code": 0, "evidence_path": self.rel("evidence/review-1-cmd0.json"), "evidence_sha256": review_cmd_sha}],
            "findings": [],
            "reviewer_attestation": {
                "agent_definition": "fa-reviewer",
                "model": "claude-fable-5",
                "effort": "xhigh",
                "runtime_id": "agent-rev1",
                "fresh_instance": True,
                "spawn_record": {"path": self.rel("evidence/review-1.spawn.json"), "sha256": review_spawn_sha},
                "prior_review_runtime_ids": [],
            },
            "uncertainties": [],
            "next_action": "parent may synthesize",
        }
        review_path = self.run_dir / "reviews" / "1-candidate.review.json"
        write_json(review_path, review)

        return {
            "manifest": manifest_path,
            "packet": packet_path,
            "return": return_path,
            "review": review_path,
            "artifact": artifact_path,
        }


def errors_for(root: Path, path: Path) -> list[str]:
    return vp.validate_packet_file(path, root)


class FableAdvisorPacketTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_valid_chain_passes(self):
        paths = Fixture(self.tmp_path).build()
        for key in ("manifest", "packet", "return", "review"):
            self.assertEqual(errors_for(self.tmp_path, paths[key]), [], key)


    def test_artifact_tamper_fails_return_and_review(self):
        paths = Fixture(self.tmp_path).build()
        paths["artifact"].write_text("tampered\n", encoding="utf-8")
        self.assertTrue(any("sha256 does not match" in e for e in errors_for(self.tmp_path, paths["return"])))
        self.assertTrue(errors_for(self.tmp_path, paths["review"]))


    def test_overlapping_scopes_fail_manifest(self):
        fixture = Fixture(self.tmp_path)
        paths = fixture.build(second_task_scope=fixture.rel("artifacts/T1"))
        self.assertTrue(any("overlap" in e for e in errors_for(self.tmp_path, paths["manifest"])))


    def test_dag_cycle_fails(self):
        fixture = Fixture(self.tmp_path)
        dag = [{"task_id": "T1", "dependencies": ["T1"]}]
        paths = fixture.build(dag_override=dag)
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("depend on itself" in e or "cycle" in e for e in errors))


    def test_unauthorized_dependency_fails(self):
        fixture = Fixture(self.tmp_path)
        dag = [{"task_id": "T1", "dependencies": ["T9"]}]
        paths = fixture.build(dag_override=dag)
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("unauthorized dependency" in e or "exactly match" in e for e in errors))


    def test_model_definition_mismatch_fails(self):
        paths = Fixture(self.tmp_path).build(auth_model="claude-opus-5")
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("does not pin" in e for e in errors))


    def test_unauthorized_model_fails(self):
        paths = Fixture(self.tmp_path).build(auth_model="claude-haiku-4-5", auth_definition="fa-worker-complex")
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("not an authorized" in e for e in errors))


    def test_model_attestation_mismatch_fails(self):
        fixture = Fixture(self.tmp_path)
        paths = fixture.build()
        model_path = fixture.run_dir / "evidence" / "T1.model.json"
        record = json.loads(model_path.read_text())
        record["observed_models"] = ["claude-sonnet-5"]
        new_sha = write_json(model_path, record)
        ret = json.loads(paths["return"].read_text())
        ret["runtime_attestation"]["model_record"]["sha256"] = new_sha
        write_json(paths["return"], ret)
        errors = errors_for(self.tmp_path, paths["return"])
        self.assertTrue(any("observed_models" in e for e in errors))


    def test_succeeded_with_failing_command_fails(self):
        fixture = Fixture(self.tmp_path)
        paths = fixture.build()
        cmd_path = fixture.run_dir / "evidence" / "T1-cmd0.json"
        record = json.loads(cmd_path.read_text())
        record["exit_code"] = 1
        new_sha = write_json(cmd_path, record)
        ret = json.loads(paths["return"].read_text())
        ret["commands"][0]["exit_code"] = 1
        ret["commands"][0]["evidence_sha256"] = new_sha
        write_json(paths["return"], ret)
        errors = errors_for(self.tmp_path, paths["return"])
        self.assertTrue(any("exit 0" in e for e in errors))


    def test_reviewer_reuse_fails(self):
        paths = Fixture(self.tmp_path).build()
        review = json.loads(paths["review"].read_text())
        review["reviewer_attestation"]["prior_review_runtime_ids"] = ["agent-rev1"]
        write_json(paths["review"], review)
        errors = errors_for(self.tmp_path, paths["review"])
        self.assertTrue(any("never repeat" in e for e in errors))


    def test_accepted_with_blocking_finding_fails(self):
        paths = Fixture(self.tmp_path).build()
        review = json.loads(paths["review"].read_text())
        review["findings"] = [{"id": "F1", "severity": "blocking", "description": "broken"}]
        write_json(paths["review"], review)
        errors = errors_for(self.tmp_path, paths["review"])
        self.assertTrue(any("blocking" in e for e in errors))


    def test_authorization_drift_fails_task_packet(self):
        paths = Fixture(self.tmp_path).build()
        packet = json.loads(paths["packet"].read_text())
        packet["authorization"]["effort"] = "high"
        write_json(paths["packet"], packet)
        errors = errors_for(self.tmp_path, paths["packet"])
        assert errors


if __name__ == "__main__":
    unittest.main()
