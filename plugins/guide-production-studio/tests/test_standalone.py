#!/usr/bin/env python3
"""Prove the public guide workflow works without sibling plugins."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


fixtures = load_module("guide_validator_fixtures", ROOT / "tests" / "test_validators.py")


class StandaloneTests(unittest.TestCase):
    def test_local_trigger_suite_has_no_sibling_dependency(self):
        runner = ROOT / "tests" / "run_guide_trigger_cases.py"
        self.assertNotIn("capability-operator", runner.read_text(encoding="utf-8"))
        completed = subprocess.run(
            ["python3", str(runner)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual(result["summary"], {"total": 20, "passed": 20, "failed": 0})

    def test_contract_review_scan_and_human_gate_work_locally(self):
        self.assertEqual(fixtures.contract_validator.validate(fixtures.valid_contract()), [])
        review = fixtures.valid_ready_review()
        self.assertEqual(fixtures.review_validator.validate(review), [])
        self.assertEqual(
            fixtures.public_validator.scan("Compare the source and revision at the same size."),
            [],
        )
        self.assertTrue(fixtures.public_validator.scan("The validator passed."))
        attempted_approval = copy.deepcopy(review)
        attempted_approval["status"] = "human_approved"
        self.assertTrue(fixtures.review_validator.validate(attempted_approval, True))


if __name__ == "__main__":
    unittest.main()
