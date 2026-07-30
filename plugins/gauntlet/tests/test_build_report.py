"""Unit tests for scripts/build_report.py (SPEC 9.6)."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_report.py"

SECTION_TITLES = [
    "1. Verdict",
    "2. Goal and bar",
    "3. Per-piece table",
    "4. Re-run the checks",
    "5. Claim audit summary",
    "6. Artifact integrity",
    "7. What was not verified",
    "8. Known remaining gaps",
    "9. Budget spent",
]


def run_report(run_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
    )


def section_body(md, number):
    """Return the body of section <number> from EVIDENCE.md text."""
    pattern = r"## %d\. .*?\n(.*?)(?=\n## |\Z)" % number
    match = re.search(pattern, md, re.DOTALL)
    assert match, "section %d not found" % number
    return match.group(1)


class BuildReportFixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # resolve() so fixture paths match the script's resolved paths
        # (on macOS /var is a symlink to /private/var).
        self.root = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = self.root / ".gauntlet" / "runs" / "20260729-1400-fixture"
        for rel in ("bar", "rounds", "claims", "verification", "sessions"):
            (self.run_dir / rel).mkdir(parents=True)

        self.write_run_json()
        (self.run_dir / "pieces.json").write_text(
            json.dumps(
                {
                    "run_id": "20260729-1400-fixture",
                    "pieces": [
                        {
                            "id": "opening-section",
                            "domain": "prose",
                            "status": "converged",
                            "rounds_completed": 3,
                            "consecutive_wins": 2,
                            "artifact_paths": ["drafts/issue.md#opening"],
                            "inspection": [
                                {
                                    "method": "claim-audit",
                                    "inspection_command": "python3 scripts/claim_audit.py --piece opening-section",
                                }
                            ],
                        },
                        {
                            "id": "argument-spine",
                            "domain": "prose",
                            "status": "looping",
                            "rounds_completed": 2,
                            "consecutive_wins": 0,
                            "artifact_paths": ["drafts/issue.md#spine"],
                            "inspection": [{"method": "reader-proxy"}],
                        },
                    ],
                }
            )
        )
        (self.run_dir / "bar" / "bar.md").write_text(
            "Beat the reference openings in bar/refs/ on blind pairing.\n"
        )
        # cost.json deliberately missing wall_clock_hours.
        (self.run_dir / "cost.json").write_text(
            json.dumps(
                {
                    "rounds_total": 5,
                    "subagents_total": 21,
                    "sessions_total": 1,
                    "tokens": "unknown",
                    "notes": "Token counts not exposed by this surface.",
                }
            )
        )
        gap_dir = self.run_dir / "rounds" / "argument-spine" / "002"
        gap_dir.mkdir(parents=True)
        (gap_dir / "gap.md").write_text(
            "Second paragraph restates the first at lower density.\n"
        )
        (self.run_dir / "rounds" / "opening-section" / "003").mkdir(parents=True)

    def write_run_json(self, context_isolation="clean"):
        (self.run_dir / "run.json").write_text(
            json.dumps(
                {
                    "run_id": "20260729-1400-fixture",
                    "goal_one_line": "Ship the fixture editorial.",
                    "domain_primary": "prose",
                    "status": "verifying",
                    "plan_hash": "sha256:abc123",
                    "context_isolation": context_isolation,
                    "stop_reason": None,
                    "project_root": str(self.root),
                }
            )
        )

    def write_consensus(self, piece_id, consensus_value, quality=None, integrity=None):
        piece_dir = self.run_dir / "verification" / piece_id
        piece_dir.mkdir(parents=True, exist_ok=True)
        (piece_dir / "consensus.json").write_text(
            json.dumps(
                {
                    "piece_id": piece_id,
                    "quality_votes": quality or {"pass": 3, "fail": 0, "cannot-verify": 0},
                    "integrity_votes": integrity or {"pass": 3, "fail": 0, "cannot-verify": 0},
                    "consensus": consensus_value,
                    "dissent": [],
                    "plan_hash_matched": True,
                }
            )
        )


class TestRefusal(BuildReportFixture):
    def test_refuses_when_verification_never_ran(self):
        proc = run_report(self.run_dir)
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"], "refused")
        self.assertEqual(payload["reason"], "verification-not-run")
        self.assertFalse((self.run_dir / "EVIDENCE.md").exists())
        self.assertFalse((self.run_dir / "EVIDENCE.json").exists())


class TestBuiltReport(BuildReportFixture):
    def setUp(self):
        super().setUp()
        self.write_consensus("opening-section", "verified")

    def test_builds_all_nine_sections_in_order(self):
        proc = run_report(self.run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        positions = [md.find("## %s" % title) for title in SECTION_TITLES]
        for title, pos in zip(SECTION_TITLES, positions):
            self.assertNotEqual(pos, -1, "missing section: %s" % title)
        self.assertEqual(positions, sorted(positions))
        self.assertTrue((self.run_dir / "EVIDENCE.json").is_file())

    def test_missing_cost_value_prints_not_recorded_and_lands_in_section_7(self):
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn("- Wall clock hours: not recorded", section_body(md, 9))
        self.assertIn("wall_clock_hours", section_body(md, 7))

    def test_unverified_piece_listed_in_section_7(self):
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        body = section_body(md, 7)
        self.assertIn("argument-spine", body)
        self.assertIn("no consensus.json", body)

    def test_partial_verification_verdict_is_unverifiable(self):
        proc = run_report(self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["verdict"], "unverifiable")
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn("unverifiable", section_body(md, 1))

    def test_last_gap_appears_verbatim_in_section_8(self):
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn(
            "Second paragraph restates the first at lower density.",
            section_body(md, 8),
        )

    def test_missing_artifact_hashes_is_not_recorded(self):
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn("not recorded", section_body(md, 6))
        self.assertIn("artifact-hashes.json", section_body(md, 7))

    def test_no_degraded_banner_when_clean(self):
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertNotIn("DEGRADED MODE", md)


class TestFailedAndDegraded(BuildReportFixture):
    def test_failed_consensus_still_builds_with_verdict_verbatim(self):
        self.write_consensus(
            "opening-section",
            "failed",
            integrity={"pass": 2, "fail": 1, "cannot-verify": 0},
        )
        self.write_consensus("argument-spine", "verified")
        proc = run_report(self.run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["verdict"], "failed")
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn("failed", section_body(md, 1))

    def test_unverifiable_consensus_still_builds(self):
        self.write_consensus(
            "opening-section",
            "unverifiable",
            integrity={"pass": 1, "fail": 0, "cannot-verify": 2},
        )
        self.write_consensus("argument-spine", "verified")
        proc = run_report(self.run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["verdict"], "unverifiable")
        md = (self.run_dir / "EVIDENCE.md").read_text()
        # The cannot-verify votes surface in section 7.
        self.assertIn("cannot-verify", section_body(md, 7))

    def test_degraded_isolation_puts_banner_in_section_1(self):
        self.write_run_json(context_isolation="degraded")
        self.write_consensus("opening-section", "verified")
        self.write_consensus("argument-spine", "verified")
        run_report(self.run_dir)
        md = (self.run_dir / "EVIDENCE.md").read_text()
        self.assertIn("DEGRADED MODE", section_body(md, 1))


if __name__ == "__main__":
    unittest.main()
