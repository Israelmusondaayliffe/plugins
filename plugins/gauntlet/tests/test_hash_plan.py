"""Tests for scripts/hash_plan.py: record, check, and mismatch detection
after the success criteria or rubric are edited mid-run."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "hash_plan.py")

PLAN_TEXT = """# Wave 1 plan

## Success criteria

- Blind critic picks ours over the reference in 2 consecutive rounds.
- Reader-proxy answers both questions without guessing.
- Every factual claim traced to a reachable source.

## Decomposition

- opening-section
- argument-spine
"""

RUBRIC_TEXT = """# Rubric

- Evidence separated from judgment.
- Assumptions labeled with confidence.
"""


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True)


class HashPlanTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-demo")
        os.makedirs(os.path.join(self.run_dir, "bar"))
        self.plan_path = os.path.join(self.run_dir, "PLAN.md")
        with open(self.plan_path, "w", encoding="utf-8") as handle:
            handle.write(PLAN_TEXT)
        self.rubric_path = os.path.join(self.run_dir, "bar", "rubric.md")
        with open(self.rubric_path, "w", encoding="utf-8") as handle:
            handle.write(RUBRIC_TEXT)
        for name, payload in (
                ("run.json", {"run_id": "20260729-1200-demo",
                              "status": "briefed"}),
                ("pieces.json", {"run_id": "20260729-1200-demo",
                                 "pieces": []})):
            with open(os.path.join(self.run_dir, name), "w",
                      encoding="utf-8") as handle:
                json.dump(payload, handle)

    def record(self):
        return run_script("--run-dir", self.run_dir, "--record")

    def check(self):
        return run_script("--run-dir", self.run_dir, "--check")

    def read_json(self, name):
        with open(os.path.join(self.run_dir, name), encoding="utf-8") as handle:
            return json.load(handle)

    def test_record_writes_hash_into_run_and_pieces(self):
        proc = self.record()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertTrue(out["plan_hash"].startswith("sha256:"))
        self.assertTrue(out["rubric_hash"].startswith("sha256:"))
        run_data = self.read_json("run.json")
        pieces_data = self.read_json("pieces.json")
        self.assertEqual(run_data["plan_hash"], out["plan_hash"])
        self.assertEqual(pieces_data["plan_hash"], out["plan_hash"])
        # Existing fields survive the update.
        self.assertEqual(run_data["status"], "briefed")

    def test_check_matches_after_record(self):
        self.record()
        proc = self.check()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertTrue(out["ok"])
        self.assertEqual(out["results"]["PLAN.md"], "match")
        self.assertEqual(out["results"]["bar/rubric.md"], "match")

    def test_editing_success_criteria_is_detected(self):
        self.record()
        with open(self.plan_path, "w", encoding="utf-8") as handle:
            handle.write(PLAN_TEXT.replace(
                "in 2 consecutive rounds", "in 1 round"))
        proc = self.check()
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertEqual(out["results"]["PLAN.md"], "mismatch")
        self.assertEqual(out["results"]["bar/rubric.md"], "match")

    def test_editing_rubric_is_detected(self):
        self.record()
        with open(self.rubric_path, "a", encoding="utf-8") as handle:
            handle.write("- A softer criterion added mid-run.\n")
        proc = self.check()
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertEqual(out["results"]["PLAN.md"], "match")
        self.assertEqual(out["results"]["bar/rubric.md"], "mismatch")

    def test_editing_outside_the_criteria_block_still_matches(self):
        self.record()
        with open(self.plan_path, "w", encoding="utf-8") as handle:
            handle.write(PLAN_TEXT.replace(
                "- argument-spine", "- argument-spine\n- closing-section"))
        proc = self.check()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        out = json.loads(proc.stdout)
        self.assertEqual(out["results"]["PLAN.md"], "match")

    def test_removed_rubric_is_a_mismatch(self):
        self.record()
        os.remove(self.rubric_path)
        proc = self.check()
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertEqual(out["results"]["bar/rubric.md"], "mismatch")

    def test_check_without_record_fails(self):
        proc = self.check()
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertEqual(out["results"]["PLAN.md"], "not-recorded")

    def test_no_rubric_records_and_checks_clean(self):
        os.remove(self.rubric_path)
        proc = self.record()
        self.assertEqual(proc.returncode, 0)
        self.assertIsNone(json.loads(proc.stdout)["rubric_hash"])
        proc = self.check()
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(out["results"]["bar/rubric.md"], "absent")

    def test_plan_without_criteria_block_cannot_be_recorded(self):
        with open(self.plan_path, "w", encoding="utf-8") as handle:
            handle.write("# Wave 1 plan\n\n## Decomposition\n\n- one\n")
        proc = self.record()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error", json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main()
