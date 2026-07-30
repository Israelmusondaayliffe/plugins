"""Tests for scripts/render_workbench.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_workbench.py"


def run_script(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


class WorkbenchFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "runs" / "20260729-1200-test"
        self.run_dir.mkdir(parents=True)

        (self.run_dir / "run.json").write_text(json.dumps({
            "run_id": "20260729-1200-test",
            "goal_one_line": "Ship the editorial past the reference set.",
            "status": "running",
            "execution_shape": "S2",
            "domain_primary": "prose",
            "current_wave": 1,
            "stop_reason": None,
            "budgets": {"rounds_cap_per_piece": 10, "wave_cap": 4,
                        "wall_clock_hours_per_session": 6,
                        "subagent_cap_per_run": 400,
                        "cost_ceiling": "user-set"},
        }))
        (self.run_dir / "pieces.json").write_text(json.dumps({"pieces": [
            {"id": "opening-section", "name": "Opening section", "lane": "a",
             "wave": 1, "status": "looping", "rounds_completed": 4,
             "rounds_cap": 10, "consecutive_wins": 1, "no_gain_streak": 0,
             "last_gap": "Gap four <script>alert(1)</script>"},
            {"id": "argument-spine", "name": "Argument spine", "lane": "a",
             "wave": 1, "status": "pending", "rounds_completed": 0,
             "rounds_cap": 10, "consecutive_wins": 0, "no_gain_streak": 0,
             "last_gap": None},
        ]}))
        (self.run_dir / "lanes.json").write_text(json.dumps({"shape": "S2", "lanes": [
            {"id": "a", "owned_pieces": ["opening-section", "argument-spine"],
             "owned_paths": ["drafts/editorial.md"], "lock_holder": "session-1",
             "heartbeat": "2026-07-29T12:00:00Z", "status": "active"},
        ]}))
        (self.run_dir / "cost.json").write_text(json.dumps({
            "rounds_total": 4, "subagents_total": 17, "sessions_total": 1,
            "wall_clock_hours": 2.5, "tokens": "unknown",
        }))

        gap_texts = {
            "001": "Gap one: the lede buries the argument.",
            "002": "Gap two: second paragraph restates the first.",
            "003": "Gap three: transitions carry no information.",
            "004": "Gap four <script>alert(1)</script>",
        }
        for round_name, text in gap_texts.items():
            round_dir = self.run_dir / "rounds" / "opening-section" / round_name
            round_dir.mkdir(parents=True)
            (round_dir / "gap.md").write_text(text)
        inspection = self.run_dir / "rounds" / "opening-section" / "004" / "inspection"
        inspection.mkdir()
        (inspection / "reader-proxy.txt").write_text(
            "Reader guessed at the second question about the ask.")
        self.gap_texts = gap_texts

    def render(self):
        proc = run_script("--run-dir", str(self.run_dir))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return (self.run_dir / "workbench.html").read_text()


class TestRenderWorkbench(WorkbenchFixture):
    def test_includes_piece_ids_and_gaps(self):
        page = self.render()
        self.assertIn("opening-section", page)
        self.assertIn("argument-spine", page)
        # Last three gaps present, oldest gap absent.
        self.assertIn("Gap two: second paragraph restates the first.", page)
        self.assertIn("Gap three: transitions carry no information.", page)
        self.assertIn("Gap four", page)
        self.assertNotIn("Gap one: the lede buries the argument.", page)

    def test_run_header_lanes_cost_and_stops(self):
        page = self.render()
        self.assertIn("20260729-1200-test", page)
        self.assertIn("status: running", page)
        self.assertIn("Ship the editorial past the reference set.", page)
        self.assertIn("session-1", page)                 # lane lock holder
        self.assertIn("subagents_total", page)           # budget spent
        self.assertIn("Stop condition distances", page)
        self.assertIn("wave cap", page)

    def test_inspection_excerpt_rendered(self):
        page = self.render()
        self.assertIn("Reader guessed at the second question", page)

    def test_html_is_escaped_and_self_contained(self):
        page = self.render()
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        # Self-contained: no external asset references.
        for marker in ("http://", "https://", "<link", "src="):
            self.assertNotIn(marker, page)
        # Phone-readable: viewport meta and inline responsive CSS.
        self.assertIn('name="viewport"', page)
        self.assertIn("@media", page)

    def test_regeneration_overwrites(self):
        self.render()
        (self.run_dir / "run.json").write_text(json.dumps({
            "run_id": "20260729-1200-test", "status": "paused",
            "goal_one_line": "Ship it.", "current_wave": 2}))
        page = self.render()
        self.assertIn("status: paused", page)

    def test_missing_run_json_fails(self):
        proc = run_script("--run-dir", str(self.run_dir / "nope"))
        self.assertEqual(proc.returncode, 1)

    def test_help(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
