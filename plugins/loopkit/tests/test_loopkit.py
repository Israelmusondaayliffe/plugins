from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from loopkit_core import (  # noqa: E402
    LoopKitError,
    diagnose_run,
    init_run,
    load_json,
    record_receipt,
    state_root,
    transition_run,
    validate_contract,
    validate_receipt,
    workspace_id,
    write_schedule,
)


def valid_contract() -> dict:
    return {
        "schema_version": 1,
        "goal": {"title": "Test loop", "outcome": "result.txt exists and contains ok"},
        "evidence": {
            "machine_checks": [{"id": "result", "command": "test -s result.txt"}],
            "judgment_criteria": [],
        },
        "boundaries": {
            "allowed_paths": ["result.txt"],
            "forbidden_paths": [],
            "external_actions": [],
        },
        "iteration": {"max_iterations": 3, "no_progress_limit": 2},
        "stops": {
            "success": "result check passes",
            "failure": "state is invalid",
            "blocked": "required local dependency is unavailable",
            "exhausted": "iteration or no-progress cap is reached",
        },
    }


class StateRootTests(unittest.TestCase):
    def test_claudecode_env_selects_claude_home(self) -> None:
        env = {"CLAUDECODE": "1", "CODEX_HOME": "/tmp/codex-home"}
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop("LOOPKIT_STATE_ROOT", None)
            self.assertEqual(state_root(), (Path.home() / ".claude" / "loopkit").resolve())

    def test_codex_home_wins_without_claudecode(self) -> None:
        with mock.patch.dict(os.environ, {"CODEX_HOME": "/tmp/codex-home"}, clear=False):
            for var in ("LOOPKIT_STATE_ROOT", "CLAUDECODE"):
                os.environ.pop(var, None)
            self.assertEqual(state_root(), Path("/tmp/codex-home/loopkit").resolve())


class StandaloneContractTests(unittest.TestCase):
    def test_plugin_declares_complete_local_operation_without_siblings(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        compatibility = (ROOT / "docs/compatibility.md").read_text(encoding="utf-8")
        router = (ROOT / "skills/loopkit/SKILL.md").read_text(encoding="utf-8")
        ownership = (ROOT / "skills/loopkit/references/ownership-and-state.md").read_text(encoding="utf-8")
        bundle = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        evals = (ROOT / "evals/evals.json").read_text(encoding="utf-8")
        self.assertIn("does not depend on sibling plugins", readme)
        self.assertIn("remain complete when they are absent", readme)
        self.assertIn("does not require Agent Ops", compatibility)
        self.assertNotIn("scheduled for removal", compatibility)
        self.assertEqual(bundle["compatibility"]["agent_ops"], "optional")
        self.assertNotIn("remove_in", bundle["compatibility"])
        self.assertNotIn("route to Agent Ops", router)
        self.assertIn("When none is available", router)
        self.assertNotIn("ProofLoop", ownership)
        self.assertNotIn("Routes to Agent Ops", evals)
        self.assertIn("when that optional companion is available", evals)


class LoopKitCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.contract_path = self.root / "contract.json"
        self.contract_path.write_text(json.dumps(valid_contract()), encoding="utf-8")
        self.env = mock.patch.dict(os.environ, {"LOOPKIT_STATE_ROOT": str(self.root / "state")})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        self.temp.cleanup()

    def new_run(self) -> Path:
        return init_run(self.contract_path, self.workspace, "unit")

    def test_contract_validation_accepts_complete_contract(self) -> None:
        self.assertEqual(validate_contract(valid_contract()), [])

    def test_contract_validation_rejects_missing_caps_and_checks(self) -> None:
        contract = valid_contract()
        contract["iteration"]["max_iterations"] = 0
        contract["evidence"]["machine_checks"] = []
        errors = validate_contract(contract)
        self.assertTrue(any("max_iterations" in error for error in errors))
        self.assertTrue(any("machine_checks" in error for error in errors))

    def test_init_creates_workspace_scoped_layout(self) -> None:
        run_dir = self.new_run()
        self.assertEqual(run_dir.parent.name, workspace_id(self.workspace))
        for relative in ("contract.json", "state.json", "events.jsonl", "checkpoint.md", "evidence"):
            self.assertTrue((run_dir / relative).exists())
        self.assertEqual(load_json(run_dir / "state.json")["status"], "ready")

    def test_transition_uses_generation_compare_and_swap(self) -> None:
        run_dir = self.new_run()
        state = transition_run(run_dir, "running", 0, "start")
        self.assertEqual(state["generation"], 1)
        with self.assertRaisesRegex(LoopKitError, "generation mismatch"):
            transition_run(run_dir, "blocked", 0, "stale writer")

    def test_completion_requires_receipt(self) -> None:
        run_dir = self.new_run()
        transition_run(run_dir, "running", 0, "start")
        with self.assertRaisesRegex(LoopKitError, "completion receipt"):
            transition_run(run_dir, "completed", 1, "claim done")

    def test_recorded_completion_updates_state_and_checkpoint(self) -> None:
        run_dir = self.new_run()
        transition_run(run_dir, "running", 0, "start")
        evidence = run_dir / "evidence" / "result.txt"
        evidence.write_text("ok\n", encoding="utf-8")
        receipt = {
            "schema_version": 1,
            "run_id": load_json(run_dir / "contract.json")["run_id"],
            "iteration": 1,
            "status": "completed",
            "action": "Created and checked the result",
            "evidence_paths": ["evidence/result.txt"],
            "checks": [{"id": "result", "passed": True, "evidence": "test -s result.txt exited 0"}],
            "judgments": [],
            "outcome": "The required result exists",
            "next_action": "Stop with completion evidence",
            "progressed": True,
        }
        receipt_path = self.root / "receipt.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        target, state = record_receipt(run_dir, receipt_path, 1)
        self.assertTrue(target.exists())
        self.assertEqual(state["status"], "completed")
        self.assertIn("Status: completed", (run_dir / "checkpoint.md").read_text(encoding="utf-8"))
        self.assertLessEqual(len((run_dir / "checkpoint.md").read_bytes()), 4096)

    def test_receipt_rejects_missing_evidence(self) -> None:
        run_dir = self.new_run()
        receipt = {
            "schema_version": 1,
            "run_id": load_json(run_dir / "contract.json")["run_id"],
            "iteration": 1,
            "status": "running",
            "action": "Tried work",
            "evidence_paths": ["evidence/missing.txt"],
            "checks": [{"id": "result", "passed": False, "evidence": "file missing"}],
            "outcome": "No artifact",
            "next_action": "Create the artifact",
        }
        self.assertTrue(any("does not exist" in error for error in validate_receipt(receipt, run_dir)))

    def test_completion_requires_judgment_evidence(self) -> None:
        contract = valid_contract()
        contract["evidence"]["judgment_criteria"] = ["Result is readable"]
        self.contract_path.write_text(json.dumps(contract), encoding="utf-8")
        run_dir = self.new_run()
        evidence = run_dir / "evidence" / "result.txt"
        evidence.write_text("ok\n", encoding="utf-8")
        receipt = {
            "schema_version": 1,
            "run_id": load_json(run_dir / "contract.json")["run_id"],
            "iteration": 1,
            "status": "completed",
            "action": "Created the result",
            "evidence_paths": ["evidence/result.txt"],
            "checks": [{"id": "result", "passed": True, "evidence": "test exited 0"}],
            "judgments": [],
            "outcome": "Result exists",
            "next_action": "Stop",
        }
        errors = validate_receipt(receipt, run_dir)
        self.assertTrue(any("missing required judgment criteria" in error for error in errors))
        receipt["judgments"] = [
            {"criterion": "Result is readable", "passed": True, "evidence": "Reviewed evidence/result.txt"}
        ]
        self.assertEqual(validate_receipt(receipt, run_dir), [])

    def test_receipt_cannot_advance_terminal_run(self) -> None:
        run_dir = self.new_run()
        transition_run(run_dir, "running", 0, "start")
        evidence = run_dir / "evidence" / "result.txt"
        evidence.write_text("ok\n", encoding="utf-8")
        base = {
            "schema_version": 1,
            "run_id": load_json(run_dir / "contract.json")["run_id"],
            "action": "Checked result",
            "evidence_paths": ["evidence/result.txt"],
            "checks": [{"id": "result", "passed": True, "evidence": "test exited 0"}],
            "judgments": [],
            "outcome": "Result exists",
            "next_action": "Stop",
            "progressed": True,
        }
        first = dict(base, iteration=1, status="completed")
        first_path = self.root / "first.json"
        first_path.write_text(json.dumps(first), encoding="utf-8")
        record_receipt(run_dir, first_path, 1)
        second = dict(base, iteration=2, status="running")
        second_path = self.root / "second.json"
        second_path.write_text(json.dumps(second), encoding="utf-8")
        with self.assertRaisesRegex(LoopKitError, "invalid receipt transition"):
            record_receipt(run_dir, second_path, 2)

    def test_schedule_requires_manual_test_record(self) -> None:
        run_dir = self.new_run()
        with self.assertRaisesRegex(LoopKitError, "manual_tested_at"):
            write_schedule(run_dir, {"cadence": "daily", "task_prompt": "run", "stop_condition": "pause"})

    def test_doctor_catches_completed_state_without_receipt(self) -> None:
        run_dir = self.new_run()
        state = load_json(run_dir / "state.json")
        state["status"] = "completed"
        (run_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
        report = diagnose_run(run_dir)
        self.assertEqual(report["findings"][0]["code"], "missing-receipt")

    def test_session_hook_is_silent_without_active_run_and_injects_checkpoint_when_active(self) -> None:
        hook = ROOT / "hooks" / "loopkit_hooks.py"
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(ROOT)
        payload = json.dumps({"cwd": str(self.workspace), "source": "resume"})
        silent = subprocess.run(
            [sys.executable, str(hook), "session-start"],
            input=payload,
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        self.assertEqual(silent.stdout, "")
        run_dir = self.new_run()
        transition_run(run_dir, "running", 0, "start")
        active = subprocess.run(
            [sys.executable, str(hook), "session-start"],
            input=payload,
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        response = json.loads(active.stdout)
        context = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("# LoopKit checkpoint", context)
        self.assertLessEqual(len(context.encode("utf-8")), 4096)


if __name__ == "__main__":
    unittest.main()
