"""Tests for scripts/lint_prompt.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lint_prompt.py"

GOOD_PROMPT = """\
Goal: ship the AKIRA issue 04 editorial at a clarity level that beats the
reference set.

The bar: the reference openings at bar/refs/reference-openings.md. Judge the
work against them directly, never against a description of them.

Split the work into the smallest independently judgeable pieces. For each
piece run a builder, then a separate critic with fresh context that never
sees the builder's reasoning. Use blind comparison where possible: the critic
receives two unlabeled artifacts and picks the stronger one. Loop until the
work wins two consecutive blind comparisons or the user stops the run.

Maintain the live progress page (workbench.html) after every round. Write all
state to the run directory at .gauntlet/runs/20260729-1400-akira-editorial/.

Use subagents for every builder, critic, and verifier, and run at the highest
effort setting.

For each prose piece, run a reader-proxy pass and keep a claim ledger that is
audited every round.
"""


def run_script(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


class LintFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def lint(self, text, *extra, expect_exit=None):
        path = Path(self.tmp.name) / "prompt.md"
        path.write_text(text)
        proc = run_script(str(path), *extra)
        if expect_exit is not None:
            self.assertEqual(proc.returncode, expect_exit,
                             proc.stdout + proc.stderr)
        return json.loads(proc.stdout), proc.returncode


class TestLintPrompt(LintFixture):
    def test_good_prompt_passes(self):
        report, code = self.lint(GOOD_PROMPT, expect_exit=0)
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["failures"], [])
        self.assertLess(report["word_count"], 400)

    def test_good_prompt_passes_knowledge_domain(self):
        report, _ = self.lint(GOOD_PROMPT, "--domain", "prose", expect_exit=0)
        self.assertEqual(report["result"], "pass")

    def test_over_600_words_fails(self):
        text = GOOD_PROMPT + "\n" + " ".join(["steady"] * 600)
        report, code = self.lint(text, expect_exit=1)
        self.assertEqual(report["result"], "fail")
        self.assertGreater(report["word_count"], 600)
        self.assertTrue(any("600" in f for f in report["failures"]))

    def test_between_400_and_600_words_warns_but_passes(self):
        text = GOOD_PROMPT + "\n" + " ".join(["steady"] * 300)
        report, code = self.lint(text, expect_exit=0)
        self.assertEqual(report["result"], "pass")
        self.assertTrue(report["warnings"])

    def test_missing_required_clause_fails(self):
        text = GOOD_PROMPT.replace(
            "Use blind comparison where possible: the critic\n"
            "receives two unlabeled artifacts and picks the stronger one. ", ""
        ).replace("two consecutive blind comparisons", "two consecutive comparisons")
        self.assertNotIn("blind", text.lower())
        report, code = self.lint(text, expect_exit=1)
        self.assertTrue(any("blind" in f for f in report["failures"]))

    def test_missing_effort_subagent_instruction_fails(self):
        text = GOOD_PROMPT.replace(
            "Use subagents for every builder, critic, and verifier, and run at "
            "the highest\neffort setting.\n", "")
        report, code = self.lint(text, expect_exit=1)
        self.assertTrue(any("subagent" in f for f in report["failures"]))

    def test_missing_bar_path_fails(self):
        text = GOOD_PROMPT.replace(
            "The bar: the reference openings at bar/refs/reference-openings.md.",
            "The bar: excellent reference openings.")
        report, code = self.lint(text, expect_exit=1)
        self.assertTrue(any("bar" in f for f in report["failures"]))

    def test_architecture_file_list_fails(self):
        text = GOOD_PROMPT + ("\nCreate these modules:\n"
                              "- src/main.py\n- src/render.py\n- src/utils.py\n")
        report, code = self.lint(text, expect_exit=1)
        self.assertTrue(any("prescribes" in f for f in report["failures"]))

    def test_architecture_directory_tree_fails(self):
        text = GOOD_PROMPT + "\napp/\n├── src\n└── tests\n"
        report, code = self.lint(text, expect_exit=1)
        self.assertTrue(any("directory tree" in f for f in report["failures"]))

    def test_unmarked_tech_stack_fails_and_marked_passes(self):
        report, code = self.lint(GOOD_PROMPT + "\nBuild the page with React.\n",
                                 expect_exit=1)
        self.assertTrue(any("tech stack" in f for f in report["failures"]))
        report, code = self.lint(
            GOOD_PROMPT + "\nBuild the page with React (user-specified).\n",
            expect_exit=0)
        self.assertEqual(report["result"], "pass")

    def test_fixed_round_count_fails(self):
        report, code = self.lint(GOOD_PROMPT + "\nRun exactly 8 rounds per piece.\n",
                                 expect_exit=1)
        self.assertTrue(any("round count" in f for f in report["failures"]))

    def test_round_cap_language_is_allowed(self):
        report, code = self.lint(GOOD_PROMPT + "\nCap each piece at 10 rounds.\n",
                                 expect_exit=0)
        self.assertEqual(report["result"], "pass")

    def test_knowledge_domain_requires_reader_proxy_and_claim_ledger(self):
        text = GOOD_PROMPT.replace(
            "For each prose piece, run a reader-proxy pass and keep a claim "
            "ledger that is\naudited every round.\n", "")
        # Without a knowledge-work domain, still passes.
        report, code = self.lint(text, expect_exit=0)
        self.assertEqual(report["result"], "pass")
        # With one, both requirements fail.
        report, code = self.lint(text, "--domain", "research", expect_exit=1)
        self.assertTrue(any("reader-proxy" in f for f in report["failures"]))
        self.assertTrue(any("claim-ledger" in f for f in report["failures"]))

    def test_invalid_domain_is_usage_error(self):
        path = Path(self.tmp.name) / "prompt.md"
        path.write_text(GOOD_PROMPT)
        proc = run_script(str(path), "--domain", "poetry")
        self.assertEqual(proc.returncode, 2)

    def test_missing_file_is_usage_error(self):
        proc = run_script(str(Path(self.tmp.name) / "absent.md"))
        self.assertEqual(proc.returncode, 2)

    def test_help(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
