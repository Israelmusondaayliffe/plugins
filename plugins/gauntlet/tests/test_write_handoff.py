"""Unit tests for scripts/write_handoff.py (SPEC 9.7, INV-6)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "write_handoff.py"

SECTION_TITLES = [
    "## 1. Run identity and location",
    "## 2. How to read state",
    "## 3. Wave and lane status",
    "## 4. Converged and verified pieces",
    "## 5. In flight",
    "## 6. Capped or blocked",
    "## 7. Decisions already made",
    "## 8. Do-not-redo list",
    "## 9. First three actions",
    "## 10. How to verify this document",
    "## 11. Surface notes",
    "## 12. Budget spent and remaining",
]


def run_handoff(run_dir, session, extra=None):
    args = [
        sys.executable, str(SCRIPT),
        "--run-dir", str(run_dir),
        "--session", str(session),
    ]
    if extra:
        args += extra
    return subprocess.run(args, capture_output=True, text=True)


class TestWriteHandoff(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # resolve() so fixture paths match the script's resolved run dir
        # (on macOS /var is a symlink to /private/var).
        self.root = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = self.root / ".gauntlet" / "runs" / "20260729-1400-fixture"
        for rel in ("bar", "rounds", "verification", "sessions"):
            (self.run_dir / rel).mkdir(parents=True)

        (self.run_dir / "run.json").write_text(
            json.dumps(
                {
                    "run_id": "20260729-1400-fixture",
                    "goal_one_line": "Ship the fixture editorial.",
                    "status": "paused",
                    "current_wave": 1,
                    "context_isolation": "clean",
                    "stop_reason": "wall-clock",
                    "precheck": {"result": "full"},
                    "budgets": {
                        "rounds_cap_per_piece": 10,
                        "wave_cap": 4,
                        "wall_clock_hours_per_session": 6,
                        "subagent_cap_per_run": 400,
                        "cost_ceiling": "user-set",
                    },
                }
            )
        )
        (self.run_dir / "pieces.json").write_text(
            json.dumps(
                {
                    "pieces": [
                        {
                            "id": "opening-section",
                            "lane": "a",
                            "status": "converged",
                            "rounds_completed": 3,
                            "rounds_cap": 10,
                        },
                        {
                            "id": "argument-spine",
                            "lane": "a",
                            "status": "looping",
                            "rounds_completed": 2,
                            "rounds_cap": 10,
                            "last_gap": "Second paragraph restates the first at lower density.",
                        },
                        {
                            "id": "closing-turn",
                            "lane": "a",
                            "status": "capped",
                            "rounds_completed": 10,
                            "rounds_cap": 10,
                            "last_gap": "Ending resolves before the argument earns it.",
                        },
                    ]
                }
            )
        )
        (self.run_dir / "lanes.json").write_text(
            json.dumps(
                {
                    "shape": "S2",
                    "lanes": [
                        {
                            "id": "a",
                            "owned_pieces": ["opening-section", "argument-spine"],
                            "owned_paths": ["drafts/issue.md"],
                            "lock_holder": "session-1",
                            "heartbeat": "2026-07-29T16:12:04Z",
                            "status": "active",
                        }
                    ],
                }
            )
        )
        (self.run_dir / "cost.json").write_text(
            json.dumps(
                {
                    "rounds_total": 15,
                    "subagents_total": 61,
                    "sessions_total": 1,
                    "wall_clock_hours": 5.5,
                    "tokens": "unknown",
                    "notes": "",
                }
            )
        )
        (self.run_dir / "sessions" / "sessions.json").write_text(
            json.dumps(
                {
                    "sessions": [
                        {
                            "index": 1,
                            "surface": "claude-code",
                            "model": "claude-fable-5",
                            "effort": "high",
                            "lane": "a",
                            "entered": "2026-07-29T14:00:00Z",
                        }
                    ]
                }
            )
        )
        (self.run_dir / "CONTEXT.md").write_text(
            "# Context\n\n- Decision: the bar is the reference openings, "
            "not a rubric (2026-07-29).\n"
        )
        consensus_dir = self.run_dir / "verification" / "opening-section"
        consensus_dir.mkdir(parents=True)
        (consensus_dir / "consensus.json").write_text(
            json.dumps(
                {
                    "piece_id": "opening-section",
                    "quality_votes": {"pass": 3, "fail": 0, "cannot-verify": 0},
                    "integrity_votes": {"pass": 3, "fail": 0, "cannot-verify": 0},
                    "consensus": "verified",
                    "plan_hash_matched": True,
                }
            )
        )

    def handoff_path(self, session=1):
        return self.run_dir / "sessions" / str(session) / "HANDOFF.md"

    def test_contains_all_twelve_sections_in_order(self):
        proc = run_handoff(self.run_dir, 1)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self.handoff_path().read_text()
        positions = [text.find(title) for title in SECTION_TITLES]
        for title, pos in zip(SECTION_TITLES, positions):
            self.assertNotEqual(pos, -1, "missing section: %s" % title)
        self.assertEqual(positions, sorted(positions))

    def test_script_appends_nothing_after_section_12(self):
        run_handoff(self.run_dir, 1)
        text = self.handoff_path().read_text()
        self.assertNotIn("## Judgment notes", text)
        self.assertEqual(text.count("\n## "), len(SECTION_TITLES))

    def test_absolute_paths_and_verification_commands(self):
        run_handoff(self.run_dir, 1)
        text = self.handoff_path().read_text()
        self.assertIn(str(self.run_dir), text)
        self.assertIn('python3 -m json.tool "%s"' % (self.run_dir / "run.json"), text)
        self.assertIn('python3 -m json.tool "%s"' % (self.run_dir / "pieces.json"), text)

    def test_state_values_are_generated_not_narrated(self):
        run_handoff(self.run_dir, 1)
        text = self.handoff_path().read_text()
        # Consensus, in-flight gap, capped reason, and decision all come
        # from state files.
        self.assertIn("verified", text)
        self.assertIn("Second paragraph restates the first at lower density.", text)
        self.assertIn("Ending resolves before the argument earns it.", text)
        self.assertIn("Decision: the bar is the reference openings", text)
        self.assertIn("claude-fable-5", text)

    def test_updates_sessions_json_exit_record(self):
        proc = run_handoff(
            self.run_dir, 1,
            extra=["--exit-reason", "wall-clock", "--rounds", "5", "--subagents", "12"],
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        doc = json.loads((self.run_dir / "sessions" / "sessions.json").read_text())
        entry = next(s for s in doc["sessions"] if s["index"] == 1)
        self.assertEqual(entry["exit_reason"], "wall-clock")
        self.assertEqual(entry["rounds_completed"], 5)
        self.assertEqual(entry["subagents_spawned"], 12)
        self.assertEqual(entry["handoff"], "sessions/1/HANDOFF.md")
        self.assertTrue(entry["exited"])

    def test_creates_exit_record_for_unknown_session(self):
        proc = run_handoff(self.run_dir, 2, extra=["--exit-reason", "user-stop"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self.handoff_path(2).is_file())
        doc = json.loads((self.run_dir / "sessions" / "sessions.json").read_text())
        entry = next(s for s in doc["sessions"] if s["index"] == 2)
        self.assertEqual(entry["exit_reason"], "user-stop")

    def test_stdout_is_json_with_handoff_path(self):
        proc = run_handoff(self.run_dir, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"], "written")
        self.assertEqual(Path(payload["handoff"]), self.handoff_path())

    def test_missing_run_json_is_failure(self):
        (self.run_dir / "run.json").unlink()
        proc = run_handoff(self.run_dir, 1)
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
