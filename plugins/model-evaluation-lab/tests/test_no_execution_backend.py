#!/usr/bin/env python3
"""Test the execution-blocked contract and sibling-free fallback."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNNER = ROOT / "skills/benchmark-runner"
VALIDATOR = RUNNER / "scripts/validate_blocked_handoff.py"
TEMPLATE = RUNNER / "assets/execution-blocked-template.json"


def validate(validator: Path, artifact: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(validator), str(artifact)],
        capture_output=True,
        text=True,
        check=False,
    )


class NoExecutionBackendTests(unittest.TestCase):
    def test_bundle_and_docs_declare_no_backend_contract(self) -> None:
        spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        policy = spec["execution_backend_policy"]
        self.assertEqual(policy["no_backend_state"], "execution-blocked")
        self.assertTrue(policy["planning_available"])
        self.assertTrue(policy["schema_validation_available"])
        self.assertTrue(policy["normalize_supplied_results_available"])
        skill = (RUNNER / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Execution-blocked handoff", skill)
        self.assertIn("Set `winner` to null", skill)

    def test_blocked_template_passes_and_has_no_measured_results(self) -> None:
        result = validate(VALIDATOR, TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertFalse(data["execution_complete"])
        self.assertFalse(data["measured_results_complete"])
        self.assertFalse(data["model_selection_complete"])
        self.assertIsNone(data["winner"])
        for field in ("results", "scores", "latency_ms", "cost_usd", "safety_results"):
            self.assertNotIn(field, data)

    def test_blocked_handoff_rejects_false_completion_and_winner_claims(self) -> None:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        data["execution_complete"] = True
        data["winner"] = "candidate-model"
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "blocked.json"
            artifact.write_text(json.dumps(data), encoding="utf-8")
            result = validate(VALIDATOR, artifact)
        self.assertEqual(result.returncode, 1)
        self.assertIn("execution_complete must be false", result.stdout)
        self.assertIn("winner must be null", result.stdout)

    def test_blocked_handoff_rejects_secret_values(self) -> None:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        for exposed_value in (
            "api_key=secret-value",
            "OPENAI_API_KEY=supersecretvalue",
        ):
            with self.subTest(exposed_value=exposed_value):
                data["missing_credentials_or_tools"] = [exposed_value]
                with tempfile.TemporaryDirectory() as temporary_directory:
                    artifact = Path(temporary_directory) / "blocked.json"
                    artifact.write_text(json.dumps(data), encoding="utf-8")
                    result = validate(VALIDATOR, artifact)
                self.assertEqual(result.returncode, 1)
                self.assertIn("exposes a secret value", result.stdout)

    def test_blocked_handoff_requires_missing_requirements_and_safety_stops(self) -> None:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        data["missing_credentials_or_tools"] = []
        data["safety_stops"] = []
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "blocked.json"
            artifact.write_text(json.dumps(data), encoding="utf-8")
            result = validate(VALIDATOR, artifact)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing_credentials_or_tools must not be empty", result.stdout)
        self.assertIn("safety_stops must not be empty", result.stdout)

    def test_sibling_free_copy_validates_blocked_handoff_and_supplied_raw_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            isolated = Path(temporary_directory) / "model-evaluation-lab"
            shutil.copytree(ROOT, isolated)
            isolated_runner = isolated / "skills/benchmark-runner"
            blocked = validate(
                isolated_runner / "scripts/validate_blocked_handoff.py",
                isolated_runner / "assets/execution-blocked-template.json",
            )
            self.assertEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            normalized = Path(temporary_directory) / "normalized.json"
            normalization = subprocess.run(
                [
                    sys.executable,
                    str(isolated_runner / "scripts/normalize_results.py"),
                    str(isolated / "tests/fixtures/raw-support-routing.json"),
                    str(normalized),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                normalization.returncode,
                0,
                normalization.stdout + normalization.stderr,
            )
            checked = subprocess.run(
                [
                    sys.executable,
                    str(isolated_runner / "scripts/validate_output.py"),
                    str(normalized),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
