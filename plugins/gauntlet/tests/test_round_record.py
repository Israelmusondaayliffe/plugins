"""Tests for scripts/round_record.py: schema and closed-set validation,
rejection of fresh-context violations (INV-2 enforcement), atomic round
recording, and convergence after two consecutive wins."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "round_record.py")

BASE_VERDICT = {
    "piece_id": "opening-section",
    "round": 1,
    "blind": True,
    "seed": 918273,
    "winner": "B",
    "winner_is_ours": False,
    "confidence": "high",
    "reasoning": "B carries more argument per sentence.",
    "largest_gap": "Second paragraph restates the first at lower density.",
    "gap_is_actionable": True,
    "inspection_evidence": [
        "rounds/opening-section/001/inspection/reader-proxy.json"],
    "rubric_hash": None,
    "critic_saw_builder_context": False,
    "critic_context_source": "files-only",
}


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True)


class RoundRecordTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-demo")
        os.makedirs(self.run_dir)
        self.pieces_path = os.path.join(self.run_dir, "pieces.json")
        self.write_pieces({
            "run_id": "20260729-1200-demo",
            "plan_hash": "sha256:abc",
            "pieces": [{
                "id": "opening-section",
                "status": "looping",
                "rounds_completed": 0,
                "rounds_cap": 10,
                "consecutive_wins": 0,
                "last_gap": None,
                "no_gain_streak": 0,
            }],
        })

    def write_pieces(self, payload):
        with open(self.pieces_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)

    def read_piece(self):
        with open(self.pieces_path, encoding="utf-8") as handle:
            return json.load(handle)["pieces"][0]

    def record(self, verdict, round_number=None, piece="opening-section"):
        if round_number is None:
            round_number = verdict.get("round", 1)
        verdict_path = os.path.join(
            self.tmp.name, "verdict-in-{0}.json".format(round_number))
        with open(verdict_path, "w", encoding="utf-8") as handle:
            json.dump(verdict, handle)
        return run_script("--run-dir", self.run_dir,
                          "--piece", piece,
                          "--round", str(round_number),
                          "--verdict", verdict_path)

    def make_verdict(self, **overrides):
        verdict = copy.deepcopy(BASE_VERDICT)
        verdict.update(overrides)
        return verdict

    def recorded_verdict_path(self, round_number):
        return os.path.join(self.run_dir, "rounds", "opening-section",
                            "{0:03d}".format(round_number), "verdict.json")

    def test_valid_loss_is_recorded(self):
        proc = self.record(self.make_verdict())
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertTrue(out["accepted"])
        path = self.recorded_verdict_path(1)
        self.assertTrue(os.path.isfile(path))
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), self.make_verdict())
        piece = self.read_piece()
        self.assertEqual(piece["rounds_completed"], 1)
        self.assertEqual(piece["consecutive_wins"], 0)
        self.assertEqual(piece["last_gap"], BASE_VERDICT["largest_gap"])
        self.assertEqual(piece["status"], "looping")

    def test_rejects_critic_saw_builder_context(self):
        proc = self.record(self.make_verdict(critic_saw_builder_context=True))
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertFalse(out["accepted"])
        self.assertTrue(any("critic_saw_builder_context" in e
                            for e in out["errors"]))
        # Nothing written, state untouched.
        self.assertFalse(os.path.exists(self.recorded_verdict_path(1)))
        self.assertEqual(self.read_piece()["rounds_completed"], 0)

    def test_rejects_non_files_only_context_source(self):
        proc = self.record(self.make_verdict(
            critic_context_source="conversation"))
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertFalse(out["accepted"])
        self.assertTrue(any("critic_context_source" in e
                            for e in out["errors"]))
        self.assertFalse(os.path.exists(self.recorded_verdict_path(1)))

    def test_rejects_empty_largest_gap(self):
        proc = self.record(self.make_verdict(largest_gap="   "))
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertTrue(any("largest_gap" in e for e in out["errors"]))
        self.assertFalse(os.path.exists(self.recorded_verdict_path(1)))

    def test_rejects_confidence_outside_closed_set(self):
        proc = self.record(self.make_verdict(confidence="certain"))
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertTrue(any("confidence" in e for e in out["errors"]))

    def test_rejects_winner_outside_closed_set(self):
        proc = self.record(self.make_verdict(winner="ours"))
        self.assertEqual(proc.returncode, 1)

    def test_rejects_missing_field(self):
        verdict = self.make_verdict()
        del verdict["inspection_evidence"]
        proc = self.record(verdict)
        self.assertEqual(proc.returncode, 1)

    def test_rejects_empty_inspection_evidence(self):
        proc = self.record(self.make_verdict(inspection_evidence=[]))
        self.assertEqual(proc.returncode, 1)

    def test_rejects_round_mismatch(self):
        proc = self.record(self.make_verdict(round=2), round_number=1)
        self.assertEqual(proc.returncode, 1)

    def test_rejects_unknown_piece(self):
        proc = self.record(self.make_verdict(piece_id="ghost-piece"),
                           piece="ghost-piece")
        self.assertEqual(proc.returncode, 1)
        out = json.loads(proc.stdout)
        self.assertTrue(any("not found" in e for e in out["errors"]))

    def test_two_consecutive_wins_converge_the_piece(self):
        win_one = self.make_verdict(
            round=1, winner="A", winner_is_ours=True,
            largest_gap="Reference opening buries its claim.")
        proc = self.record(win_one)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        piece = self.read_piece()
        self.assertEqual(piece["consecutive_wins"], 1)
        self.assertEqual(piece["status"], "looping")

        win_two = self.make_verdict(
            round=2, winner="A", winner_is_ours=True,
            inspection_evidence=[
                "rounds/opening-section/002/inspection/reader-proxy.json"],
            largest_gap="Reference opening buries its claim.")
        proc = self.record(win_two)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        piece = self.read_piece()
        self.assertEqual(piece["consecutive_wins"], 2)
        self.assertEqual(piece["rounds_completed"], 2)
        self.assertEqual(piece["status"], "converged")

    def test_loss_resets_the_win_streak(self):
        self.record(self.make_verdict(winner="A", winner_is_ours=True))
        proc = self.record(self.make_verdict(round=2))
        self.assertEqual(proc.returncode, 0)
        piece = self.read_piece()
        self.assertEqual(piece["consecutive_wins"], 0)
        self.assertEqual(piece["status"], "looping")

    def test_repeated_gap_increments_no_gain_streak(self):
        gap = "Second paragraph restates the first at lower density."
        self.record(self.make_verdict(round=1, largest_gap=gap))
        self.assertEqual(self.read_piece()["no_gain_streak"], 0)
        self.record(self.make_verdict(round=2, largest_gap=gap))
        self.assertEqual(self.read_piece()["no_gain_streak"], 1)
        self.record(self.make_verdict(
            round=3, largest_gap="Closing line lands on a weaker verb."))
        self.assertEqual(self.read_piece()["no_gain_streak"], 0)


if __name__ == "__main__":
    unittest.main()
