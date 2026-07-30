"""Tests for scripts/check_stops.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_stops.py"


def run_script(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_piece(piece_id="opening-section", **overrides):
    piece = {
        "id": piece_id,
        "name": piece_id,
        "domain": "prose",
        "lane": "a",
        "wave": 1,
        "status": "looping",
        "rounds_completed": 3,
        "rounds_cap": 10,
        "consecutive_wins": 0,
        "last_gap": "Second paragraph restates the first.",
        "no_gain_streak": 0,
    }
    piece.update(overrides)
    return piece


class CheckStopsFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "runs" / "20260729-1200-test"
        (self.run_dir / "sessions").mkdir(parents=True)

    def write_state(self, pieces=None, run_overrides=None, sessions=None, cost=None):
        run = {
            "run_id": "20260729-1200-test",
            "status": "running",
            "execution_shape": "S2",
            "domain_primary": "prose",
            "current_wave": 1,
            "stop_reason": None,
            "budgets": {
                "rounds_cap_per_piece": 10,
                "wave_cap": 4,
                "wall_clock_hours_per_session": 6,
                "subagent_cap_per_run": 400,
                "cost_ceiling": "user-set",
            },
        }
        run.update(run_overrides or {})
        (self.run_dir / "run.json").write_text(json.dumps(run))
        (self.run_dir / "pieces.json").write_text(json.dumps({
            "run_id": run["run_id"],
            "pieces": pieces if pieces is not None else [make_piece()],
        }))
        if sessions is not None:
            (self.run_dir / "sessions" / "sessions.json").write_text(
                json.dumps({"sessions": sessions}))
        if cost is not None:
            (self.run_dir / "cost.json").write_text(json.dumps(cost))

    def read_run(self):
        return json.loads((self.run_dir / "run.json").read_text())

    def read_pieces(self):
        return json.loads((self.run_dir / "pieces.json").read_text())["pieces"]

    def check(self, expect_exit=0):
        proc = run_script("--run-dir", str(self.run_dir))
        self.assertEqual(proc.returncode, expect_exit, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)


class TestCheckStops(CheckStopsFixture):
    def test_nothing_fires(self):
        self.write_state()
        result = self.check()
        self.assertFalse(result["fired"])
        self.assertEqual(result["action"], "continue")
        self.assertEqual(self.read_run()["status"], "running")

    def test_user_stop_flag(self):
        self.write_state()
        (self.run_dir / "STOP").write_text("")
        result = self.check()
        self.assertTrue(result["fired"])
        self.assertEqual(result["condition"], "user-stop")
        run = self.read_run()
        self.assertEqual(run["status"], "stopped")
        self.assertEqual(run["stop_reason"], "user-stop")

    def test_user_stop_wins_over_converged_piece(self):
        self.write_state(pieces=[make_piece(consecutive_wins=2)])
        (self.run_dir / "STOP").write_text("")
        result = self.check()
        self.assertEqual(result["condition"], "user-stop")
        # The piece was not touched: user stop fired first.
        self.assertEqual(self.read_pieces()[0]["status"], "looping")

    def test_piece_converges_on_two_wins(self):
        self.write_state(pieces=[make_piece(consecutive_wins=2)])
        result = self.check()
        self.assertEqual(result["condition"], "piece-converged")
        self.assertEqual(result["scope"], "opening-section")
        self.assertEqual(self.read_pieces()[0]["status"], "converged")

    def test_all_pieces_converged(self):
        self.write_state(pieces=[
            make_piece("a-piece", status="converged"),
            make_piece("b-piece", status="converged"),
        ])
        result = self.check()
        self.assertEqual(result["condition"], "all-pieces-converged")
        self.assertEqual(self.read_run()["status"], "converged")

    def test_round_cap_sets_capped_never_done(self):
        self.write_state(pieces=[make_piece(rounds_completed=10, rounds_cap=10,
                                            last_gap="Still restates.")])
        result = self.check()
        self.assertTrue(result["fired"])
        self.assertEqual(result["condition"], "round-cap")
        piece = self.read_pieces()[0]
        self.assertEqual(piece["status"], "capped")
        self.assertNotIn(piece["status"], ("converged", "done", "verified"))
        # Gap preserved.
        self.assertEqual(piece["last_gap"], "Still restates.")
        # Run status untouched: a piece cap is piece-scoped.
        self.assertEqual(self.read_run()["status"], "running")

    def test_no_gain_rule_escalates_and_stops_looping(self):
        # Streak 1 means the identical gap appeared in two consecutive rounds,
        # which is the SPEC 11.4 firing condition.
        self.write_state(pieces=[make_piece(no_gain_streak=1)])
        result = self.check()
        self.assertTrue(result["fired"])
        self.assertEqual(result["condition"], "no-gain")
        self.assertEqual(result["scope"], "opening-section")
        self.assertIn("re-split", result["action"])
        piece = self.read_pieces()[0]
        self.assertEqual(piece["status"], "blocked")
        self.assertNotIn(piece["status"], ("converged", "done"))

    def test_no_gain_rule_does_not_fire_on_first_occurrence(self):
        self.write_state(pieces=[make_piece(no_gain_streak=0)])
        result = self.check()
        self.assertFalse(result["fired"])

    def test_wave_cap_pauses(self):
        self.write_state(run_overrides={"current_wave": 5})
        result = self.check()
        self.assertEqual(result["condition"], "wave-cap")
        run = self.read_run()
        self.assertEqual(run["status"], "paused")
        self.assertEqual(run["stop_reason"], "wave-cap")

    def test_wall_clock_pauses_open_session(self):
        entered = iso(datetime.now(timezone.utc) - timedelta(hours=7))
        self.write_state(sessions=[{"index": 3, "entered": entered, "exited": None}])
        result = self.check()
        self.assertEqual(result["condition"], "wall-clock")
        self.assertEqual(result["scope"], "session-3")
        self.assertEqual(self.read_run()["status"], "paused")

    def test_wall_clock_ignores_exited_sessions(self):
        entered = iso(datetime.now(timezone.utc) - timedelta(hours=9))
        exited = iso(datetime.now(timezone.utc) - timedelta(hours=1))
        self.write_state(sessions=[{"index": 1, "entered": entered, "exited": exited}])
        result = self.check()
        self.assertFalse(result["fired"])

    def test_subagent_cap_pauses(self):
        self.write_state(cost={"subagents_total": 400})
        result = self.check()
        self.assertEqual(result["condition"], "subagent-cap")
        self.assertEqual(self.read_run()["status"], "paused")

    def test_cost_ceiling_fires_only_when_numeric(self):
        # Non-numeric ceiling never fires.
        self.write_state(cost={"cost_spent": 900})
        self.assertFalse(self.check()["fired"])
        # Numeric ceiling fires.
        self.write_state(run_overrides={"budgets": {"cost_ceiling": 500}},
                         cost={"cost_spent": 900})
        result = self.check()
        self.assertEqual(result["condition"], "cost-ceiling")
        self.assertEqual(self.read_run()["status"], "paused")

    def test_missing_run_json_is_validation_failure(self):
        proc = run_script("--run-dir", str(self.run_dir / "nope"))
        self.assertEqual(proc.returncode, 1)

    def test_help_and_usage_error(self):
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)
        proc = run_script()
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
