"""Unit tests for scripts/precheck.py (SPEC section 2)."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "precheck.py"


def run_precheck(*args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def env_without_claude_vars():
    """A copy of the environment with the subagent-heuristic vars removed."""
    return {
        key: value
        for key, value in os.environ.items()
        if key != "CLAUDECODE" and not key.startswith("CLAUDE_CODE")
    }


class TestPrecheck(unittest.TestCase):
    def test_help_exits_zero(self):
        proc = run_precheck("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--surface", proc.stdout)
        self.assertIn("--expect-network", proc.stdout)

    def test_stdout_is_json_with_required_keys(self):
        proc = run_precheck("--surface", "claude-code")
        payload = json.loads(proc.stdout)
        for key in ("result", "subagents", "filesystem", "command_execution", "network"):
            self.assertIn(key, payload)
        self.assertIn(payload["result"], ("full", "degraded", "unsupported"))

    def test_claude_code_surface_is_full(self):
        proc = run_precheck("--surface", "claude-code")
        payload = json.loads(proc.stdout)
        self.assertIs(payload["subagents"], True)
        self.assertIs(payload["filesystem"], True)
        self.assertIs(payload["command_execution"], True)
        self.assertIsNone(payload["network"])
        self.assertEqual(payload["result"], "full")
        self.assertIsNone(payload["remediation"])
        self.assertEqual(proc.returncode, 0)

    def test_chat_surface_has_no_subagents_and_degrades(self):
        # Filesystem and execution probes still pass on this machine, so a
        # chat hint yields degraded (not unsupported) with a remediation line.
        proc = run_precheck("--surface", "chat")
        payload = json.loads(proc.stdout)
        self.assertIs(payload["subagents"], False)
        self.assertEqual(payload["result"], "degraded")
        self.assertIsNotNone(payload["remediation"])
        self.assertIn("subagent", payload["remediation"])
        self.assertTrue(proc.stderr.strip())
        self.assertEqual(proc.returncode, 0)

    def test_auto_with_claudecode_env_detects_subagents(self):
        env = env_without_claude_vars()
        env["CLAUDECODE"] = "1"
        proc = run_precheck("--surface", "auto", env=env)
        payload = json.loads(proc.stdout)
        self.assertIs(payload["subagents"], True)

    def test_auto_with_claude_code_prefixed_env_detects_subagents(self):
        env = env_without_claude_vars()
        env["CLAUDE_CODE_ENTRYPOINT"] = "cli"
        proc = run_precheck("--surface", "auto", env=env)
        payload = json.loads(proc.stdout)
        self.assertIs(payload["subagents"], True)

    def test_auto_without_env_is_unknown_and_degraded(self):
        proc = run_precheck("--surface", "auto", env=env_without_claude_vars())
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["subagents"], "unknown")
        self.assertEqual(payload["result"], "degraded")
        self.assertIsNotNone(payload["remediation"])
        self.assertEqual(proc.returncode, 0)

    def test_cowork_surface_does_not_assume_parity(self):
        # SPEC 11.1: confirm the Cowork subagent surface at runtime rather
        # than assuming parity. Without env evidence the answer is unknown.
        proc = run_precheck("--surface", "cowork", env=env_without_claude_vars())
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["subagents"], "unknown")
        self.assertEqual(payload["result"], "degraded")

    def test_network_is_null_unless_expected(self):
        proc = run_precheck("--surface", "claude-code")
        payload = json.loads(proc.stdout)
        self.assertIsNone(payload["network"])

    def test_bad_surface_is_usage_error(self):
        proc = run_precheck("--surface", "carrier-pigeon")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
