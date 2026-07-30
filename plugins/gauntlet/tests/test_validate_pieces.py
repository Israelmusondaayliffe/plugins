"""Unit tests for scripts/validate_pieces.py."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN_ROOT, "scripts", "validate_pieces.py")


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True,
    )


def checks(payload):
    return {f["check"] for f in payload["findings"]}


def piece(pid, lane, artifact, inspection, domain="prose",
          status="pending"):
    return {
        "id": pid,
        "name": pid,
        "domain": domain,
        "lane": lane,
        "wave": 1,
        "artifact_paths": [artifact],
        "inspection": inspection,
        "status": status,
    }


PROSE_INSPECTION = [
    {"method": "reader-proxy",
     "questions": ["What is this arguing?"]},
    {"method": "claim-audit",
     "inspection_command":
     "python3 scripts/claim_audit.py --run-dir . --piece p1"},
]


class ValidatePiecesTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-test")
        os.makedirs(self.run_dir)

    def tearDown(self):
        self.tmp.cleanup()

    def write_state(self, pieces, shape="S2", lanes=None):
        if lanes is None:
            lanes = [{"id": "a",
                      "owned_pieces": [p["id"] for p in pieces],
                      "owned_paths": ["drafts/out.md"],
                      "status": "active"}]
        with open(os.path.join(self.run_dir, "pieces.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"run_id": "t", "pieces": pieces}, fh)
        with open(os.path.join(self.run_dir, "lanes.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"shape": shape, "lanes": lanes}, fh)

    def test_valid_configuration_passes(self):
        self.write_state([
            piece("p1", "a", "drafts/out.md#opening", PROSE_INSPECTION),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])

    def test_read_only_prose_piece_rejected(self):
        self.write_state([
            piece("p1", "a", "drafts/out.md", [{"method": "read"}]),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("read-alone", checks(payload))
        self.assertIn("knowledge-read-unpaired", checks(payload))

    def test_knowledge_read_must_pair_with_proxy_or_claim_audit(self):
        # read plus red-team on a prose piece still fails the pairing rule.
        self.write_state([
            piece("p1", "a", "drafts/out.md", [
                {"method": "read"},
                {"method": "red-team",
                 "inspection_command": "python3 x.py"},
            ]),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("knowledge-read-unpaired", checks(payload))
        self.assertNotIn("read-alone", checks(payload))

    def test_read_paired_on_code_domain_passes(self):
        self.write_state([
            piece("p1", "a", "src/mod.py", [
                {"method": "read"},
                {"method": "test",
                 "inspection_command": "python3 -m unittest"},
            ], domain="code"),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])

    def test_unknown_method_rejected(self):
        self.write_state([
            piece("p1", "a", "drafts/out.md", [{"method": "vibe-check"}]),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("unknown-method", checks(payload))

    def test_no_inspection_method_rejected(self):
        self.write_state([
            piece("p1", "a", "drafts/out.md", []),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("no-inspection", checks(payload))

    def test_missing_inspection_command_rejected(self):
        self.write_state([
            piece("p1", "a", "src/mod.py", [
                {"method": "test"},
                {"method": "read"},
            ], domain="code"),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("missing-inspection-command", checks(payload))

    def test_unknown_status_rejected(self):
        self.write_state([
            piece("p1", "a", "drafts/out.md", PROSE_INSPECTION,
                  status="half-done"),
        ])
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("unknown-status", checks(payload))

    def test_s3_overlapping_lane_paths_refused(self):
        pieces = [
            piece("p1", "a", "drafts/one.md", PROSE_INSPECTION),
            piece("p2", "b", "drafts/two.md", PROSE_INSPECTION),
        ]
        lanes = [
            {"id": "a", "owned_pieces": ["p1"],
             "owned_paths": ["drafts/one.md", "drafts/shared.md"],
             "status": "active"},
            {"id": "b", "owned_pieces": ["p2"],
             "owned_paths": ["drafts/two.md", "drafts/shared.md"],
             "status": "active"},
        ]
        self.write_state(pieces, shape="S3", lanes=lanes)
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("lane-path-overlap", checks(payload))

    def test_s3_cross_lane_artifact_overlap_refused(self):
        pieces = [
            piece("p1", "a", "drafts/out.md#opening", PROSE_INSPECTION),
            piece("p2", "b", "drafts/out.md#closing", PROSE_INSPECTION),
        ]
        lanes = [
            {"id": "a", "owned_pieces": ["p1"],
             "owned_paths": ["drafts/a"], "status": "active"},
            {"id": "b", "owned_pieces": ["p2"],
             "owned_paths": ["drafts/b"], "status": "active"},
        ]
        self.write_state(pieces, shape="S3", lanes=lanes)
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("cross-lane-artifact-overlap", checks(payload))

    def test_s3_disjoint_lanes_pass(self):
        pieces = [
            piece("p1", "a", "drafts/one.md", PROSE_INSPECTION),
            piece("p2", "b", "drafts/two.md", PROSE_INSPECTION),
        ]
        lanes = [
            {"id": "a", "owned_pieces": ["p1"],
             "owned_paths": ["drafts/one.md"], "status": "active"},
            {"id": "b", "owned_pieces": ["p2"],
             "owned_paths": ["drafts/two.md"], "status": "active"},
        ]
        self.write_state(pieces, shape="S3", lanes=lanes)
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])

    def test_same_lane_shared_artifact_allowed_under_s3(self):
        pieces = [
            piece("p1", "a", "drafts/out.md#opening", PROSE_INSPECTION),
            piece("p2", "a", "drafts/out.md#closing", PROSE_INSPECTION),
        ]
        lanes = [
            {"id": "a", "owned_pieces": ["p1", "p2"],
             "owned_paths": ["drafts/out.md"], "status": "active"},
        ]
        self.write_state(pieces, shape="S3", lanes=lanes)
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_missing_pieces_json_fails(self):
        proc = run_script("--run-dir", self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("pieces-missing", checks(payload))

    def test_missing_run_dir_is_usage_error(self):
        proc = run_script("--run-dir", os.path.join(self.tmp.name, "nope"))
        self.assertEqual(proc.returncode, 2, proc.stdout)


if __name__ == "__main__":
    unittest.main()
