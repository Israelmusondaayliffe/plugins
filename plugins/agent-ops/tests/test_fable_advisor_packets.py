"""Fail-closed tests for the Fable Advisor protocol 3 packet validator (stdlib unittest).

Native claude-fable-5-1 subagents are the default worker runtime; Codex workers
through the official plugin remain a per-task option. Both paths are covered.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FABLE_ADVISOR = PLUGIN_ROOT / "skills" / "fable-advisor"
VALIDATOR = FABLE_ADVISOR / "scripts" / "validate_packets.py"
TEMPLATES = FABLE_ADVISOR / "assets"
AGENTS = PLUGIN_ROOT / "agents"
spec = importlib.util.spec_from_file_location("fa_validate_packets", VALIDATOR)
vp = importlib.util.module_from_spec(spec)
sys.modules["fa_validate_packets"] = vp
spec.loader.exec_module(vp)

NATIVE = "claude-code"
CODEX = "codex"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, data: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return sha_file(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fields: dict[str, str] = {}
    for line in (match.group(1) if match else "").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def fresh_dispatch(execution_mode: str = "background") -> dict:
    return {
        "execution_mode": execution_mode,
        "monitoring": {"cadence_seconds": 300, "status_scope": "agent_id_only", "result_collection": "terminal_only"},
        "attempt_policy": {"max_fresh_retries": 1},
    }


def fresh_transport(execution_mode: str = "background") -> dict:
    return {
        "execution_mode": execution_mode,
        "dispatch_mode": "fresh",
        "resume_lineage": None,
        "monitoring": {"cadence_seconds": 300, "status_scope": "job_id_only", "result_collection": "terminal_only"},
        "attempt_policy": {"max_resume_continuations": 1, "max_fresh_retries": 1},
        "transfer_policy": "explicit_emergency_diagnostic_only",
        "review_policy": {"instance": "fresh", "write_enabled": False, "authority": "advisory", "acceptance": "parent"},
    }


def resume_transport() -> dict:
    transport = fresh_transport()
    transport["dispatch_mode"] = "resume"
    transport["resume_lineage"] = {
        "prior_job_id": "job-prior",
        "prior_thread_id": "thread-prior",
        "scope_requirement": "same_or_narrower",
    }
    return transport


class Fixture:
    """Builds one complete, internally consistent run under a tmp root."""

    def __init__(self, root: Path):
        self.root = root
        self.run = ".fable-advisor/runs/r1"
        self.run_dir = root / self.run

    def rel(self, *parts: str) -> str:
        return "/".join((self.run, *parts))

    def build(
        self,
        *,
        runtime: str = NATIVE,
        classification: str = "complex",
        requested_model: str | None = None,
        observed_model: str | None = None,
        effort: str = "high",
        dispatch: dict | None = None,
        transport: dict | None = None,
        observed_effort: str | None = None,
        second_task_scope: str | None = None,
        second_task_runtime: str = NATIVE,
        dag_override=None,
        include_codex_runtime: bool | None = None,
    ) -> dict:
        native = runtime == NATIVE
        if requested_model is None:
            requested_model = "claude-fable-5-1" if native else "codex-default"
        if observed_model is None:
            observed_model = "claude-fable-5-1" if native else "gpt-5.4-codex"
        write_enabled = classification != "verify"
        if native:
            mechanism = "fa_verifier" if classification == "verify" else "fa_worker"
        else:
            mechanism = "codex_rescue"
        runtime_id = "agent-abc" if native else "job-abc"
        if include_codex_runtime is None:
            include_codex_runtime = (not native) or second_task_runtime == CODEX

        plan_path = self.run_dir / "plan.md"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text("# Approved plan\n", encoding="utf-8")
        plan = {"status": "approved", "version": 1, "path": self.rel("plan.md"), "sha256": sha_file(plan_path)}

        authorization = {
            "task_id": "T1",
            "classification": classification,
            "role": "worker",
            "runtime": runtime,
            "model": requested_model,
            "effort": effort,
            "write_enabled": write_enabled,
            "dependencies": [],
            "allowed_write_paths": [self.rel("artifacts/T1")],
            "input_paths": [{"path": plan["path"], "sha256": plan["sha256"]}],
            "expected_output": {"description": "one output file", "paths": [self.rel("artifacts/T1/output.md")]},
            "acceptance_criteria": [{"id": "C1", "description": "output exists"}],
            "evidence_commands": ["test -f output.md"],
            "stop_conditions": ["scope violation"],
            "limits": {"max_attempts": 3, "max_turns": 80, "max_elapsed_minutes": 60},
        }
        authorizations = [authorization]
        dag = [{"task_id": "T1", "dependencies": []}]
        if second_task_scope is not None:
            second = dict(authorization)
            second_native = second_task_runtime == NATIVE
            second.update(
                task_id="T2",
                classification="light",
                runtime=second_task_runtime,
                model="claude-fable-5-1" if second_native else "codex-default",
                effort="high" if second_native else "default",
                write_enabled=True,
                allowed_write_paths=[second_task_scope],
                expected_output={"description": "second output", "paths": [second_task_scope + "/out2.md"]},
                limits={"max_attempts": 3, "max_turns": 40, "max_elapsed_minutes": 30},
            )
            authorizations.append(second)
            dag.append({"task_id": "T2", "dependencies": []})
        if dag_override is not None:
            dag = dag_override

        manifest_runtime = {
            "claude_code_version": "2.1.246",
            "entrypoint": "claude-desktop",
            "parent_session_id": "sess-1",
            "parent_model": "claude-fable-5-1",
            "parent_effort": "high",
            "dispatch_interface": "agent_tool",
            "worker_model": "claude-fable-5-1",
        }
        if include_codex_runtime:
            manifest_runtime["codex_plugin_version"] = "1.0.6"
            manifest_runtime["codex_dispatch_interface"] = "codex_rescue"

        manifest = {
            "packet_type": "FableAdvisorRunManifest",
            "protocol_version": 3,
            "run_id": "r1",
            "activation": {"type": "explicit", "quoted_request": "Use Fable Advisor to build X", "recorded_at": "2026-09-06T15:00:00Z"},
            "plan": plan,
            "goal": "build X",
            "criteria": [{"id": "C1", "description": "output exists"}],
            "runtime": manifest_runtime,
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
            "protocol_version": 3,
            "run_id": "r1",
            "task_id": "T1",
            "run_manifest_path": self.rel("run-manifest.json"),
            "run_manifest_sha256": manifest_sha,
            "plan": plan,
            "task": {"classification": classification, "objective": "produce output.md", "dependencies": []},
            "authorization": authorization,
            "worker": {
                "role": "worker",
                "runtime": runtime,
                "model": requested_model,
                "effort": effort,
                "write_enabled": write_enabled,
                "fresh_instance": True,
                "mechanism": mechanism,
            },
            "input_paths": authorization["input_paths"],
            "expected_output": authorization["expected_output"],
            "acceptance_criteria": authorization["acceptance_criteria"],
            "scope": {"allowed_write_paths": authorization["allowed_write_paths"], "read_paths": [plan["path"]]},
            "evidence_commands": authorization["evidence_commands"],
            "stop_conditions": authorization["stop_conditions"],
            "limits": authorization["limits"],
            "context": {"delivery": "bounded_packet_only", "include_parent_transcript": False, "include_hidden_reasoning": False, "reference_paths": []},
        }
        if native:
            packet["dispatch"] = dispatch if dispatch is not None else fresh_dispatch()
        elif transport is not None:
            packet["transport"] = transport
        packet_path = self.run_dir / "tasks" / "T1.task.json"
        packet_sha = write_json(packet_path, packet)

        artifact_path = self.run_dir / "artifacts" / "T1" / "output.md"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("built output\n", encoding="utf-8")

        spawn = {
            "record_type": "FableAdvisorSpawnRecord",
            "protocol_version": 3,
            "run_id": "r1",
            "subject_type": "task",
            "subject_id": "T1",
            "runtime": runtime,
            "mechanism": mechanism,
            "requested_model": requested_model,
            "requested_effort": effort,
            "write_enabled": write_enabled,
            "runtime_id": runtime_id,
            "spawned_at": "2026-09-06T15:01:00Z",
        }
        if native:
            spawn["agent_type"] = vp.NATIVE_WORKER_AGENTS[mechanism]
        spawn_sha = write_json(self.run_dir / "evidence" / "T1.spawn.json", spawn)

        job_record = {
            "record_type": "FableAdvisorJobRecord",
            "protocol_version": 3,
            "run_id": "r1",
            "subject_type": "task",
            "subject_id": "T1",
            "job_id": runtime_id,
            "status": "completed",
            "requested_model": requested_model,
            "observed_model": observed_model,
            "attestation": "verified",
            "source": "subagent_transcript" if native else "codex companion result --json",
            "reason": None,
            "raw": (
                {
                    "agent_id": runtime_id,
                    "transcript_path": "~/.claude/projects/proj/sess-1/subagents/agent-abc.jsonl",
                    "models_observed": [observed_model],
                    "task_status": "completed",
                }
                if native
                else {"job_id": runtime_id, "status": "completed", "model": observed_model}
            ),
        }
        if observed_effort is not None:
            job_record["observed_effort"] = observed_effort
        job_sha = write_json(self.run_dir / "evidence" / "T1.job.json", job_record)
        cmd_sha = write_json(self.run_dir / "evidence" / "T1-cmd0.json", {
            "record_type": "FableAdvisorCommandEvidence",
            "protocol_version": 3,
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
            "protocol_version": 3,
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
            "commands": [
                {"command": "test -f output.md", "exit_code": 0, "evidence_path": self.rel("evidence/T1-cmd0.json"), "evidence_sha256": cmd_sha},
                {"command": "wc -l output.md", "exit_code": 0, "risk": "low", "summary": "1 line"},
            ],
            "work_report": {
                "observable_delta": ["artifacts/T1/output.md created"],
                "primary_output_count": 1,
                "unresolved_before": 1,
                "unresolved_after": 0,
                "support_artifact_count": 0,
                "next_target_action": "integrate",
            },
            "runtime_attestation": {
                "runtime": runtime,
                "mechanism": mechanism,
                "requested_model": requested_model,
                "requested_effort": effort,
                "runtime_id": runtime_id,
                "authored_by": "worker" if write_enabled else "parent",
                "spawn_record": {"path": self.rel("evidence/T1.spawn.json"), "sha256": spawn_sha},
                "job_record": {"path": self.rel("evidence/T1.job.json"), "sha256": job_sha},
            },
            "uncertainties": [],
            "risks": [],
            "next_action": "integrate",
        }
        return_path = self.run_dir / "returns" / "T1.return.json"
        return_sha = write_json(return_path, ret)

        review_cmd_sha = write_json(self.run_dir / "evidence" / "review-1-cmd0.json", {
            "record_type": "FableAdvisorCommandEvidence",
            "protocol_version": 3,
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
            "protocol_version": 3,
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
                "reviewer": "parent",
                "model": "claude-fable-5-1",
                "effort": "high",
                "session_id": "sess-1",
                "verification_task_ids": [],
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
        self.fixture = Fixture(self.tmp_path)

    # helpers

    def assert_chain_valid(self, paths: dict) -> None:
        for key in ("manifest", "packet", "return", "review"):
            self.assertEqual(errors_for(self.tmp_path, paths[key]), [], key)

    def _mutate_manifest(self, paths, mutate) -> list[str]:
        manifest = load_json(paths["manifest"])
        mutate(manifest)
        write_json(paths["manifest"], manifest)
        return errors_for(self.tmp_path, paths["manifest"])

    def _mutate_packet(self, paths, mutate) -> list[str]:
        packet = load_json(paths["packet"])
        mutate(packet)
        write_json(paths["packet"], packet)
        return errors_for(self.tmp_path, paths["packet"])

    def _mutate_return(self, paths, mutate) -> list[str]:
        ret = load_json(paths["return"])
        mutate(ret)
        write_json(paths["return"], ret)
        return errors_for(self.tmp_path, paths["return"])

    def _mutate_review(self, paths, mutate) -> list[str]:
        review = load_json(paths["review"])
        mutate(review)
        write_json(paths["review"], review)
        return errors_for(self.tmp_path, paths["review"])

    def _rebind_evidence(self, paths, name: str, attestation_key: str, mutate) -> list[str]:
        """Mutate an evidence record and rebind its hash in the ReturnPacket."""
        record_path = self.fixture.run_dir / "evidence" / name
        record = load_json(record_path)
        mutate(record)
        new_sha = write_json(record_path, record)
        ret = load_json(paths["return"])
        ret["runtime_attestation"][attestation_key]["sha256"] = new_sha
        write_json(paths["return"], ret)
        return errors_for(self.tmp_path, paths["return"])

    def _make_job_partially_verified(self, paths, *, observed_model=None) -> list[str]:
        def mutate(job):
            job["attestation"] = "partially-verified"
            job["reason"] = "runtime did not report a model"
            job["observed_model"] = observed_model
        return self._rebind_evidence(paths, "T1.job.json", "job_record", mutate)

    # native default chain

    def test_native_chain_passes(self):
        self.assert_chain_valid(self.fixture.build())

    def test_native_verify_chain_passes(self):
        self.assert_chain_valid(self.fixture.build(classification="verify"))

    def test_artifact_tamper_fails_return_and_review(self):
        paths = self.fixture.build()
        paths["artifact"].write_text("tampered\n", encoding="utf-8")
        self.assertTrue(any("sha256 does not match" in e for e in errors_for(self.tmp_path, paths["return"])))
        self.assertTrue(errors_for(self.tmp_path, paths["review"]))

    def test_overlapping_scopes_fail_manifest(self):
        paths = self.fixture.build(second_task_scope=self.fixture.rel("artifacts/T1"))
        self.assertTrue(any("overlap" in e for e in errors_for(self.tmp_path, paths["manifest"])))

    def test_dag_cycle_fails(self):
        paths = self.fixture.build(dag_override=[{"task_id": "T1", "dependencies": ["T1"]}])
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("depend on itself" in e or "cycle" in e for e in errors))

    def test_unauthorized_dependency_fails(self):
        paths = self.fixture.build(dag_override=[{"task_id": "T1", "dependencies": ["T9"]}])
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("unauthorized dependency" in e or "exactly match" in e for e in errors))

    def test_unknown_runtime_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(runtime="gemini"))
        self.assertTrue(any("runtime must be claude-code" in e for e in errors))

    def test_native_worker_model_must_be_fable_5(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(model="claude-fable-5"))
        self.assertTrue(any("model must be claude-fable-5-1" in e for e in errors))

    def test_native_worker_effort_must_be_pinned_high(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(effort="medium"))
        self.assertTrue(any("effort must be high" in e for e in errors))

    def test_invalid_effort_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(effort="ultra"))
        self.assertTrue(any("effort" in e for e in errors))

    def test_verify_task_with_write_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(classification="verify", write_enabled=True))
        self.assertTrue(any("verify tasks must be read-only" in e for e in errors))

    def test_native_verify_requires_fa_verifier(self):
        paths = self.fixture.build(classification="verify")
        errors = self._mutate_packet(paths, lambda p: p["worker"].update(mechanism="fa_worker"))
        self.assertTrue(any("verify tasks must dispatch through fa_verifier" in e for e in errors))

    def test_fa_verifier_must_be_readonly(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p["worker"].update(mechanism="fa_verifier"))
        self.assertTrue(any("fa_verifier is read-only" in e for e in errors))

    def test_mechanism_must_belong_to_runtime(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p["worker"].update(mechanism="codex_rescue"))
        self.assertTrue(any("mechanism must belong to the worker runtime" in e for e in errors))

    def test_unknown_mechanism_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p["worker"].update(mechanism="fa_planner"))
        self.assertTrue(any("mechanism must be fa_worker, fa_verifier, codex_rescue, or codex_companion" in e for e in errors))

    def test_native_packet_rejects_transport_key(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p.update(transport=fresh_transport()))
        self.assertTrue(any("TaskPacket.transport is the Codex extension" in e for e in errors))

    def test_native_packet_requires_dispatch(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p.pop("dispatch"))
        self.assertTrue(any("TaskPacket.dispatch" in e for e in errors))

    def test_spawn_agent_type_must_bind_mechanism(self):
        paths = self.fixture.build()
        errors = self._rebind_evidence(paths, "T1.spawn.json", "spawn_record", lambda s: s.update(agent_type="agent-ops:fa-verifier"))
        self.assertTrue(any("agent_type must be the subagent bound" in e for e in errors))

    def test_spawn_mechanism_must_belong_to_runtime(self):
        paths = self.fixture.build()
        errors = self._rebind_evidence(paths, "T1.spawn.json", "spawn_record", lambda s: s.update(runtime="codex"))
        self.assertTrue(any("runtime does not bind the spawn" in e or "mechanism must belong to the spawn runtime" in e for e in errors))

    def test_authored_by_parent_requires_readonly(self):
        paths = self.fixture.build()
        errors = self._mutate_return(paths, lambda r: r["runtime_attestation"].update(authored_by="parent"))
        self.assertTrue(any("authored_by parent" in e for e in errors))

    def test_return_runtime_must_match_packet_worker(self):
        paths = self.fixture.build()
        errors = self._mutate_return(paths, lambda r: r["runtime_attestation"].update(runtime="codex", mechanism="codex_rescue"))
        self.assertTrue(any("runtime must exactly match the TaskPacket worker" in e for e in errors))

    def test_native_observed_model_contradiction_fails(self):
        paths = self.fixture.build(observed_model="claude-sonnet-5")
        errors = errors_for(self.tmp_path, paths["return"])
        self.assertTrue(any("observed_model contradicts" in e for e in errors))

    def test_native_partially_verified_without_observation_passes(self):
        paths = self.fixture.build()
        self.assertEqual(self._make_job_partially_verified(paths), [])

    def test_native_partially_verified_with_observed_model_fails(self):
        paths = self.fixture.build()
        errors = self._make_job_partially_verified(paths, observed_model="claude-fable-5-1")
        self.assertTrue(any("requires observed_model null" in e for e in errors))

    def test_native_verified_requires_transcript_source(self):
        paths = self.fixture.build()
        errors = self._rebind_evidence(paths, "T1.job.json", "job_record", lambda j: j.update(source="worker self-report"))
        self.assertTrue(any("requires source subagent_transcript" in e for e in errors))

    def test_observed_effort_contradiction_fails(self):
        paths = self.fixture.build(observed_effort="medium")
        self.assertTrue(any("observed_effort contradicts the requested effort" in e for e in errors_for(self.tmp_path, paths["return"])))

    def test_observed_effort_match_passes(self):
        paths = self.fixture.build(observed_effort="high")
        self.assertEqual(errors_for(self.tmp_path, paths["return"]), [])

    # manifest runtime and authority

    def test_protocol_2_rejected(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m.update(protocol_version=2))
        self.assertTrue(any("protocol_version" in e for e in errors))

    def test_composed_mode_rejected(self):
        paths = self.fixture.build()

        def mutate(manifest):
            manifest["protocol_version"] = 1
            manifest["mode"] = "composed"
            manifest["authority"] = {surface: "gauntlet" for surface in vp.AUTHORITY_SURFACES}
        errors = self._mutate_manifest(paths, mutate)
        self.assertTrue(any("removed in protocol 2" in e for e in errors))
        self.assertTrue(any("authority" in e and "must be parent" in e for e in errors))

    def test_gauntlet_authority_rejected(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m.update(authority={surface: "gauntlet" for surface in vp.AUTHORITY_SURFACES}))
        self.assertTrue(any("authority" in e and "must be parent" in e for e in errors))

    def test_parent_model_must_be_fable_5_1(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["runtime"].update(parent_model="claude-fable-5"))
        self.assertTrue(any("parent_model must be one of" in e for e in errors))

    def test_parent_effort_must_be_high(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["runtime"].update(parent_effort="medium"))
        self.assertTrue(any("parent_effort must be high" in e for e in errors))

    def test_dispatch_interface_must_be_agent_tool(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["runtime"].update(dispatch_interface="codex_rescue"))
        self.assertTrue(any("dispatch_interface must be agent_tool" in e for e in errors))

    def test_runtime_worker_model_key_must_be_fable_5(self):
        paths = self.fixture.build()
        errors = self._mutate_manifest(paths, lambda m: m["runtime"].update(worker_model="claude-fable-5"))
        self.assertTrue(any("worker_model must be claude-fable-5-1" in e for e in errors))

    def test_codex_runtime_keys_optional_without_codex_tasks(self):
        paths = self.fixture.build(include_codex_runtime=True)
        self.assert_chain_valid(paths)

    def test_mixed_runtime_manifest_valid(self):
        paths = self.fixture.build(second_task_scope=self.fixture.rel("artifacts/T2"), second_task_runtime=CODEX)
        self.assertEqual(errors_for(self.tmp_path, paths["manifest"]), [])

    # review

    def test_reviewer_must_be_parent(self):
        paths = self.fixture.build()
        errors = self._mutate_review(paths, lambda r: r["reviewer_attestation"].update(reviewer="fa-reviewer"))
        self.assertTrue(any("reviewer must be parent" in e for e in errors))

    def test_reviewer_model_must_be_parent_model(self):
        paths = self.fixture.build()
        errors = self._mutate_review(paths, lambda r: r["reviewer_attestation"].update(model="claude-fable-5"))
        self.assertTrue(any("reviewer_attestation.model must be one of" in e for e in errors))

    def test_reviewer_effort_must_be_high(self):
        paths = self.fixture.build()
        errors = self._mutate_review(paths, lambda r: r["reviewer_attestation"].update(effort="xhigh"))
        self.assertTrue(any("reviewer_attestation.effort must be high" in e for e in errors))

    def test_succeeded_with_failing_command_fails(self):
        paths = self.fixture.build()
        cmd_path = self.fixture.run_dir / "evidence" / "T1-cmd0.json"
        record = load_json(cmd_path)
        record["exit_code"] = 1
        new_sha = write_json(cmd_path, record)

        def mutate(ret):
            ret["commands"][0]["exit_code"] = 1
            ret["commands"][0]["evidence_sha256"] = new_sha
        errors = self._mutate_return(paths, mutate)
        self.assertTrue(any("exit 0" in e for e in errors))

    def test_accepted_with_blocking_finding_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_review(paths, lambda r: r.update(findings=[{"id": "F1", "severity": "blocking", "description": "broken"}]))
        self.assertTrue(any("blocking" in e for e in errors))

    def test_succeeded_with_empty_observable_delta_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_return(paths, lambda r: r["work_report"].update(observable_delta=[]))
        self.assertTrue(any("observable_delta" in e for e in errors))

    def test_succeeded_without_unresolved_improvement_fails(self):
        paths = self.fixture.build()
        errors = self._mutate_return(paths, lambda r: r["work_report"].update(unresolved_before=2, unresolved_after=2))
        self.assertTrue(any("unresolved required work to improve" in e for e in errors))

    def test_authorization_drift_fails_task_packet(self):
        paths = self.fixture.build()
        errors = self._mutate_packet(paths, lambda p: p["authorization"].update(effort="medium"))
        self.assertTrue(errors)

    # native dispatch extension

    def _dispatch_errors(self, mutate) -> list[str]:
        paths = self.fixture.build()
        return self._mutate_packet(paths, lambda p: mutate(p["dispatch"]))

    def test_foreground_dispatch_valid(self):
        paths = self.fixture.build(dispatch=fresh_dispatch("foreground"))
        self.assertEqual(errors_for(self.tmp_path, paths["packet"]), [])

    def test_invalid_execution_mode_fails(self):
        errors = self._dispatch_errors(lambda d: d.update(execution_mode="detached"))
        self.assertTrue(any("execution_mode must be foreground or background" in e for e in errors))

    def test_dispatch_cadence_must_be_positive_int(self):
        errors = self._dispatch_errors(lambda d: d["monitoring"].update(cadence_seconds=0))
        self.assertTrue(any("cadence_seconds" in e for e in errors))

    def test_dispatch_status_scope_and_collection_strict(self):
        errors = self._dispatch_errors(lambda d: d["monitoring"].update(status_scope="all_tasks", result_collection="streaming"))
        self.assertTrue(any("status_scope must be agent_id_only" in e for e in errors))
        self.assertTrue(any("result_collection must be terminal_only" in e for e in errors))

    def test_dispatch_attempt_policy_limit(self):
        errors = self._dispatch_errors(lambda d: d["attempt_policy"].update(max_fresh_retries=2))
        self.assertTrue(any("max_fresh_retries must be 0 or 1" in e for e in errors))

    def test_dispatch_rejects_resume_fields(self):
        errors = self._dispatch_errors(lambda d: d["attempt_policy"].update(max_resume_continuations=1))
        self.assertTrue(any("unsupported keys" in e and "max_resume_continuations" in e for e in errors))

    def test_unknown_dispatch_key_fails(self):
        errors = self._dispatch_errors(lambda d: d.update(streaming=True))
        self.assertTrue(any("unsupported keys" in e and "streaming" in e for e in errors))

    # retained Codex option

    def test_codex_chain_passes(self):
        self.assert_chain_valid(self.fixture.build(runtime=CODEX))

    def test_codex_chain_with_transport_passes(self):
        self.assert_chain_valid(self.fixture.build(runtime=CODEX, transport=fresh_transport()))

    def test_codex_verify_chain_passes(self):
        self.assert_chain_valid(self.fixture.build(runtime=CODEX, classification="verify", effort="default"))

    def test_codex_task_requires_manifest_codex_runtime_keys(self):
        paths = self.fixture.build(runtime=CODEX, include_codex_runtime=False)
        errors = errors_for(self.tmp_path, paths["manifest"])
        self.assertTrue(any("codex_plugin_version is required" in e for e in errors))
        self.assertTrue(any("codex_dispatch_interface is required" in e for e in errors))

    def test_codex_dispatch_interface_strict(self):
        paths = self.fixture.build(runtime=CODEX)
        errors = self._mutate_manifest(paths, lambda m: m["runtime"].update(codex_dispatch_interface="agent_tool"))
        self.assertTrue(any("codex_dispatch_interface" in e for e in errors))

    def test_codex_invalid_effort_fails(self):
        paths = self.fixture.build(runtime=CODEX)
        errors = self._mutate_manifest(paths, lambda m: m["task_authorization"][0].update(effort="ultra"))
        self.assertTrue(any("authorized Codex companion effort" in e for e in errors))

    def test_codex_packet_rejects_dispatch_key(self):
        paths = self.fixture.build(runtime=CODEX)
        errors = self._mutate_packet(paths, lambda p: p.update(dispatch=fresh_dispatch()))
        self.assertTrue(any("TaskPacket.dispatch is the native extension" in e for e in errors))

    def test_codex_mechanism_must_be_codex(self):
        paths = self.fixture.build(runtime=CODEX)
        errors = self._mutate_packet(paths, lambda p: p["worker"].update(mechanism="fa_worker"))
        self.assertTrue(any("mechanism must belong to the worker runtime" in e for e in errors))

    def test_codex_spawn_rejects_agent_type(self):
        paths = self.fixture.build(runtime=CODEX)
        errors = self._rebind_evidence(paths, "T1.spawn.json", "spawn_record", lambda s: s.update(agent_type="agent-ops:fa-worker"))
        self.assertTrue(any("agent_type is a native-runtime key" in e for e in errors))

    def test_codex_named_model_partially_verified_fails(self):
        paths = self.fixture.build(runtime=CODEX, requested_model="gpt-5.4-codex", observed_model="gpt-5.4-codex")
        errors = self._make_job_partially_verified(paths)
        self.assertTrue(any("only acceptable for codex-default" in e for e in errors))

    def test_codex_default_partially_verified_passes(self):
        paths = self.fixture.build(runtime=CODEX)
        self.assertEqual(self._make_job_partially_verified(paths), [])

    def test_codex_observed_model_contradiction_fails(self):
        paths = self.fixture.build(runtime=CODEX, requested_model="gpt-5.4-codex", observed_model="gpt-5.3-codex-spark")
        self.assertTrue(any("observed_model contradicts" in e for e in errors_for(self.tmp_path, paths["return"])))

    def test_codex_default_effort_ignores_observed_effort(self):
        paths = self.fixture.build(runtime=CODEX, effort="default", observed_effort="medium")
        self.assertEqual(errors_for(self.tmp_path, paths["return"]), [])

    # retained Codex transport extension

    def _transport_errors(self, mutate) -> list[str]:
        paths = self.fixture.build(runtime=CODEX, transport=fresh_transport())
        return self._mutate_packet(paths, lambda p: mutate(p["transport"]))

    def test_resume_lineage_valid(self):
        paths = self.fixture.build(runtime=CODEX, transport=resume_transport())
        self.assertEqual(errors_for(self.tmp_path, paths["packet"]), [])

    def test_resume_without_lineage_fails(self):
        errors = self._transport_errors(lambda t: t.update(dispatch_mode="resume"))
        self.assertTrue(any("resume_lineage" in e for e in errors))

    def test_fresh_with_lineage_fails(self):
        errors = self._transport_errors(lambda t: t.update(resume_lineage=resume_transport()["resume_lineage"]))
        self.assertTrue(any("must be null for a fresh dispatch" in e for e in errors))

    def test_scope_requirement_must_be_same_or_narrower(self):
        def mutate(transport):
            transport.update(resume_transport())
            transport["resume_lineage"]["scope_requirement"] = "wider"
        errors = self._transport_errors(mutate)
        self.assertTrue(any("scope_requirement must be same_or_narrower" in e for e in errors))

    def test_transport_attempt_policy_limits(self):
        errors = self._transport_errors(lambda t: t["attempt_policy"].update(max_resume_continuations=2, max_fresh_retries=2))
        self.assertTrue(any("max_resume_continuations must be 0 or 1" in e for e in errors))
        self.assertTrue(any("max_fresh_retries must be 0 or 1" in e for e in errors))

    def test_transfer_policy_strict(self):
        errors = self._transport_errors(lambda t: t.update(transfer_policy="routine"))
        self.assertTrue(any("transfer_policy must be explicit_emergency_diagnostic_only" in e for e in errors))

    def test_review_policy_advisory_boundary(self):
        errors = self._transport_errors(lambda t: t.update(review_policy={"instance": "resumed", "write_enabled": True, "authority": "binding", "acceptance": "codex"}))
        self.assertTrue(any("review_policy.instance must be fresh" in e for e in errors))
        self.assertTrue(any("review_policy.acceptance must be parent" in e for e in errors))

    def test_unknown_transport_key_fails(self):
        errors = self._transport_errors(lambda t: t.update(streaming=True))
        self.assertTrue(any("unsupported keys" in e and "streaming" in e for e in errors))

    def test_verify_task_transport_must_be_fresh(self):
        errors: list[str] = []
        vp.validate_transport(resume_transport(), "t", errors, classification="verify")
        self.assertTrue(any("verify tasks must use a fresh dispatch" in e for e in errors))
        errors = []
        vp.validate_transport(fresh_transport(), "t", errors, classification="verify")
        self.assertEqual(errors, [])

    # shipped templates and agent definitions

    def test_native_templates_are_protocol_3_defaults(self):
        manifest = load_json(TEMPLATES / "run-manifest.template.json")
        task = load_json(TEMPLATES / "task-packet.template.json")
        ret = load_json(TEMPLATES / "return-packet.template.json")
        review = load_json(TEMPLATES / "review-packet.template.json")
        for packet in (manifest, task, ret, review):
            self.assertEqual(packet["protocol_version"], 3)
        self.assertEqual(manifest["runtime"]["parent_model"], "claude-fable-5-1")
        self.assertEqual(manifest["runtime"]["parent_effort"], "high")
        self.assertEqual(manifest["runtime"]["dispatch_interface"], "agent_tool")
        self.assertEqual(manifest["runtime"]["worker_model"], "claude-fable-5-1")
        self.assertEqual(manifest["task_authorization"][0]["runtime"], NATIVE)
        self.assertEqual(task["worker"]["runtime"], NATIVE)
        self.assertEqual(task["worker"]["mechanism"], "fa_worker")
        self.assertNotIn("transport", task)
        errors: list[str] = []
        vp.validate_dispatch(task["dispatch"], "template.dispatch", errors)
        self.assertEqual(errors, [])
        self.assertEqual(ret["runtime_attestation"]["runtime"], NATIVE)
        self.assertEqual(ret["runtime_attestation"]["requested_model"], "claude-fable-5-1")
        self.assertEqual(review["reviewer_attestation"]["model"], "claude-fable-5-1")
        self.assertEqual(review["reviewer_attestation"]["effort"], "high")

    def test_codex_template_is_valid_codex_shape(self):
        task = load_json(TEMPLATES / "task-packet.codex.template.json")
        self.assertEqual(task["protocol_version"], 3)
        self.assertEqual(task["worker"]["runtime"], CODEX)
        self.assertEqual(task["worker"]["mechanism"], "codex_rescue")
        self.assertNotIn("dispatch", task)
        errors: list[str] = []
        vp.validate_transport(task["transport"], "template.transport", errors, classification="complex")
        self.assertEqual(errors, [])

    def test_agent_definitions_pin_fable_5(self):
        worker = frontmatter(AGENTS / "fa-worker.md")
        verifier = frontmatter(AGENTS / "fa-verifier.md")
        for fields in (worker, verifier):
            self.assertEqual(fields["model"], "claude-fable-5-1")
            self.assertEqual(fields["effort"], "high")
            self.assertIn("Agent", fields["disallowedTools"])
        self.assertNotRegex(verifier["tools"], r"\b(Write|Edit)\b")
        self.assertIn("Write", verifier["disallowedTools"])

    def test_codex_transport_reference_retained(self):
        self.assertTrue((FABLE_ADVISOR / "references" / "codex-transport-operations.md").is_file())
        self.assertTrue((FABLE_ADVISOR / "references" / "native-worker-operations.md").is_file())

    def test_sol_advisor_is_explicit_legacy_compatibility(self):
        text = (PLUGIN_ROOT / "skills" / "sol-advisor" / "SKILL.md").read_text()
        self.assertIn("Legacy compatibility", text)
        self.assertIn("Do not silently reinterpret existing Sol packets", text)


if __name__ == "__main__":
    unittest.main()
