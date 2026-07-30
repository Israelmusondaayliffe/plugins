"""Unit tests for scripts/validate_bar.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN_ROOT, "scripts", "validate_bar.py")

GOOD_BAR = (
    "# Bar\n\n"
    "Beat the 3 reference openings stored in bar/refs/reference-openings.md "
    "on information density, judged blind.\n"
)


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True,
    )


def checks(payload):
    return {f["check"] for f in payload["findings"]}


class ValidateBarTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-test")
        os.makedirs(os.path.join(self.run_dir, "bar", "refs"))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, content):
        path = os.path.join(self.run_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path

    def write_pieces(self, bar_refs, artifact_paths):
        self.write("pieces.json", json.dumps({
            "run_id": "20260729-1200-test",
            "pieces": [{
                "id": "opening",
                "domain": "prose",
                "lane": "a",
                "bar_refs": bar_refs,
                "artifact_paths": artifact_paths,
                "status": "pending",
            }],
        }))

    def test_valid_bar_passes(self):
        self.write("bar/refs/reference-openings.md", "Reference text.\n")
        self.write("bar/bar.md", GOOD_BAR)
        self.write_pieces(
            ["bar/refs/reference-openings.md"], ["drafts/out.md"])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["findings"], [])

    def test_adjective_only_bar_fails(self):
        # Backed by a real reference file, but the definition itself has no
        # path, command, URL, or number: only adjectives.
        self.write("bar/refs/reference-openings.md", "Reference text.\n")
        self.write(
            "bar/bar.md",
            "# Bar\n\nThe writing must be excellent, compelling, "
            "world-class, and truly polished.\n",
        )
        self.write_pieces(
            ["bar/refs/reference-openings.md"], ["drafts/out.md"])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("bar-adjective-only", checks(payload))
        # Refs exist, so the unbacked check must not fire here.
        self.assertNotIn("bar-unbacked", checks(payload))

    def test_soft_unbacked_bar_fails(self):
        # No refs anywhere and adjective-only text: soft bar, two findings.
        self.write(
            "bar/bar.md",
            "# Bar\n\nMake it feel premium, sharp, and impressive.\n",
        )
        self.write_pieces([], ["drafts/out.md"])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("bar-unbacked", checks(payload))
        self.assertIn("bar-adjective-only", checks(payload))

    def test_unresolvable_ref_fails(self):
        self.write("bar/bar.md", GOOD_BAR)
        self.write_pieces(
            ["bar/refs/reference-openings.md"], ["drafts/out.md"])
        # The referenced file was never created.
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("ref-unresolvable", checks(payload))

    def test_self_referential_bar_fails(self):
        self.write("bar/bar.md", GOOD_BAR)
        self.write("bar/refs/reference-openings.md", "Reference text.\n")
        self.write("drafts/out.md", "Our own draft.\n")
        self.write_pieces(
            ["bar/refs/reference-openings.md", "drafts/out.md"],
            ["drafts/out.md#opening"],
        )
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("bar-self-referential", checks(payload))

    def test_rubric_without_hash_fails(self):
        self.write("bar/refs/reference-openings.md", "Reference text.\n")
        self.write("bar/bar.md", GOOD_BAR)
        self.write("bar/rubric.md", "## Rubric\n\n- clarity\n")
        self.write_pieces(
            ["bar/refs/reference-openings.md"], ["drafts/out.md"])
        self.write("run.json", json.dumps({"run_id": "20260729-1200-test"}))
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("rubric-unhashed", checks(payload))

    def test_rubric_with_recorded_hash_passes(self):
        self.write("bar/refs/reference-openings.md", "Reference text.\n")
        self.write("bar/bar.md", GOOD_BAR)
        self.write("bar/rubric.md", "## Rubric\n\n- clarity\n")
        self.write_pieces(
            ["bar/refs/reference-openings.md"], ["drafts/out.md"])
        self.write("run.json", json.dumps({
            "run_id": "20260729-1200-test",
            "rubric_hash": "sha256:" + "ab12" * 16,
        }))
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertNotIn("rubric-unhashed", checks(payload))

    def test_missing_bar_file_fails(self):
        self.write_pieces([], ["drafts/out.md"])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("bar-missing", checks(payload))

    def test_missing_run_dir_is_usage_error(self):
        proc = run_script("--run-dir", os.path.join(self.tmp.name, "nope"))
        self.assertEqual(proc.returncode, 2, proc.stdout)


if __name__ == "__main__":
    unittest.main()
