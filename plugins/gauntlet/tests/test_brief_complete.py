"""Unit tests for scripts/brief_complete.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN_ROOT, "scripts", "brief_complete.py")

CRITERIA_4 = (
    "- Blind critic picks ours in 2 consecutive rounds\n"
    "- Reader-proxy answers all declared questions without guessing\n"
    "- Claim audit reports zero unsupported rows\n"
    "- Every section survives a deletability pass\n"
)


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True,
    )


def make_plan(omit=(), criteria=CRITERIA_4):
    sections = [
        ("Success criteria", criteria),
        ("Bar definition", "Beat bar/refs/reference-openings.md, judged "
         "blind on density."),
        ("Bar rationale", "Same category, same length class, published "
         "quality floor."),
        ("Done means", "Blind win, 2 consecutive rounds per piece."),
        ("Budget ceiling", "10 rounds per piece, 6 hour sessions, 4 waves."),
        ("Out of scope", "No redesign of the publication template."),
        ("Non negotiables", "Strictly monochrome palette, no invented "
         "quotes."),
        ("Inspection feasibility", "- opening: reader-proxy\n"
         "- claims: claim-audit"),
    ]
    lines = ["# PLAN", ""]
    for title, body in sections:
        key = title.lower().replace(" ", "_")
        if key in omit:
            continue
        lines.append("## " + title)
        lines.append("")
        lines.append(body)
        lines.append("")
    return "\n".join(lines)


class BriefCompleteTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-test")
        os.makedirs(self.run_dir)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, content):
        path = os.path.join(self.run_dir, rel)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def write_run_json(self, shape="S2"):
        self.write("run.json", json.dumps({
            "run_id": "20260729-1200-test",
            "goal_one_line": "Ship the editorial at reference clarity.",
            "domain_primary": "prose",
            "execution_shape": shape,
        }))

    def test_complete_brief_passes(self):
        self.write_run_json()
        self.write("PLAN.md", make_plan())
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["missing"], [])
        self.assertEqual(payload["invalid"], {})

    def test_missing_out_of_scope_blocks(self):
        self.write_run_json()
        self.write("PLAN.md", make_plan(omit=("out_of_scope",)))
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("out_of_scope", payload["missing"])

    def test_empty_field_counts_as_missing(self):
        self.write_run_json()
        plan = make_plan(omit=("non_negotiables",))
        plan += "\n## Non negotiables\n\n\n"
        self.write("PLAN.md", plan)
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("non_negotiables", payload["missing"])

    def test_too_few_success_criteria_blocks(self):
        self.write_run_json()
        two = ("- Blind critic picks ours\n"
               "- Claim audit reports zero unsupported rows\n")
        self.write("PLAN.md", make_plan(criteria=two))
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("success_criteria", payload["invalid"])

    def test_too_many_success_criteria_blocks(self):
        self.write_run_json()
        eight = "".join("- criterion number %d\n" % n for n in range(8))
        self.write("PLAN.md", make_plan(criteria=eight))
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("success_criteria", payload["invalid"])

    def test_bad_execution_shape_blocks(self):
        self.write_run_json(shape="S9")
        self.write("PLAN.md", make_plan())
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("execution_shape", payload["invalid"])

    def test_no_plan_and_no_run_json_reports_all_missing(self):
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertEqual(len(payload["missing"]), 11)

    def test_missing_run_dir_is_usage_error(self):
        proc = run_script("--run-dir", os.path.join(self.tmp.name, "nope"))
        self.assertEqual(proc.returncode, 2, proc.stdout)


if __name__ == "__main__":
    unittest.main()
