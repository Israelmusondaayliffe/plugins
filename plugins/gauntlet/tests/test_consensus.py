"""Tests for scripts/consensus.py: all four consensus outcomes and the
precedence rules from SPEC section 9.5."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "consensus.py")


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True)


class ConsensusTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-demo")
        self.piece = "opening-section"
        self.vdir = os.path.join(self.run_dir, "verification", self.piece)
        os.makedirs(self.vdir)

    def write_verdict(self, vtype, index, result, reason="", phm=True):
        payload = {
            "piece_id": self.piece,
            "verifier_type": vtype,
            "verifier_index": index,
            "result": result,
            "criterion_applied": "Blind critic picks ours in 2 rounds.",
            "evidence_inspected": ["rounds/x/001/inspection/out.json"],
            "reason": reason,
            "plan_hash_matched": phm,
        }
        path = os.path.join(self.vdir, "{0}-{1}.json".format(vtype, index))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)

    def compute(self):
        proc = run_script("--run-dir", self.run_dir, "--piece", self.piece)
        return proc, (json.loads(proc.stdout) if proc.stdout.strip() else None)

    def read_consensus_file(self):
        with open(os.path.join(self.vdir, "consensus.json"),
                  encoding="utf-8") as handle:
            return json.load(handle)

    def test_all_pass_is_verified(self):
        for i in (1, 2, 3):
            self.write_verdict("quality", i, "pass")
            self.write_verdict("integrity", i, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(out["consensus"], "verified")
        self.assertEqual(out["quality_votes"],
                         {"pass": 3, "fail": 0, "cannot-verify": 0})
        self.assertEqual(out["dissent"], [])
        self.assertTrue(out["plan_hash_matched"])
        self.assertEqual(out["computed_by"], "scripts/consensus.py")
        # The file on disk is the same content the script printed.
        self.assertEqual(self.read_consensus_file(), out)

    def test_majority_quality_pass_is_verified_with_dissent(self):
        self.write_verdict("quality", 1, "pass")
        self.write_verdict("quality", 2, "pass")
        self.write_verdict("quality", 3, "fail",
                           reason="Second paragraph restates the first.")
        for i in (1, 2, 3):
            self.write_verdict("integrity", i, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["consensus"], "verified-with-dissent")
        # Dissent preserved verbatim.
        self.assertTrue(any("Second paragraph restates the first." in d
                            for d in out["dissent"]))

    def test_any_integrity_fail_is_failed(self):
        for i in (1, 2, 3):
            self.write_verdict("quality", i, "pass")
        self.write_verdict("integrity", 1, "pass")
        self.write_verdict("integrity", 2, "fail",
                           reason="Invented citation at L42.")
        self.write_verdict("integrity", 3, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        # Quality votes do not rescue an integrity fail.
        self.assertEqual(out["consensus"], "failed")

    def test_majority_quality_fail_is_failed(self):
        self.write_verdict("quality", 1, "fail", reason="Gap A.")
        self.write_verdict("quality", 2, "fail", reason="Gap B.")
        self.write_verdict("quality", 3, "pass")
        for i in (1, 2):
            self.write_verdict("integrity", i, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["consensus"], "failed")
        # Gaps unioned into dissent.
        joined = " ".join(out["dissent"])
        self.assertIn("Gap A.", joined)
        self.assertIn("Gap B.", joined)

    def test_any_cannot_verify_is_unverifiable(self):
        for i in (1, 2, 3):
            self.write_verdict("quality", i, "pass")
        self.write_verdict("integrity", 1, "pass")
        self.write_verdict("integrity", 2, "cannot-verify",
                           reason="Two ledger rows cite an unreachable URL.")
        self.write_verdict("integrity", 3, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["consensus"], "unverifiable")
        self.assertTrue(any("unreachable URL" in d for d in out["dissent"]))

    def test_integrity_fail_beats_cannot_verify(self):
        self.write_verdict("quality", 1, "cannot-verify", reason="No output.")
        self.write_verdict("quality", 2, "pass")
        self.write_verdict("integrity", 1, "fail", reason="Stubbed test.")
        self.write_verdict("integrity", 2, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["consensus"], "failed")

    def test_plan_hash_mismatch_propagates(self):
        self.write_verdict("quality", 1, "pass")
        self.write_verdict("quality", 2, "pass")
        self.write_verdict("integrity", 1, "cannot-verify",
                           reason="Plan hash mismatch.", phm=False)
        self.write_verdict("integrity", 2, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out["consensus"], "unverifiable")
        self.assertFalse(out["plan_hash_matched"])

    def test_missing_verifier_type_is_a_validation_failure(self):
        self.write_verdict("quality", 1, "pass")
        self.write_verdict("quality", 2, "pass")
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error", out)
        self.assertFalse(os.path.exists(
            os.path.join(self.vdir, "consensus.json")))

    def test_result_outside_closed_set_is_rejected(self):
        self.write_verdict("quality", 1, "pass")
        self.write_verdict("integrity", 1, "pass")
        bad = os.path.join(self.vdir, "integrity-2.json")
        with open(bad, "w", encoding="utf-8") as handle:
            json.dump({"piece_id": self.piece, "verifier_type": "integrity",
                       "verifier_index": 2, "result": "mostly-pass",
                       "plan_hash_matched": True}, handle)
        proc, out = self.compute()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
