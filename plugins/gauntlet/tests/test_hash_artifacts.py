"""Unit tests for scripts/hash_artifacts.py (SPEC 9.6 section 6, INV-5)."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "hash_artifacts.py"


def run_hash(run_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
    )


class TestHashArtifacts(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # resolve() so fixture paths match the script's resolved paths
        # (on macOS /var is a symlink to /private/var).
        self.root = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)

        self.run_dir = self.root / ".gauntlet" / "runs" / "20260729-1400-fixture"
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "run.json").write_text(
            json.dumps(
                {
                    "run_id": "20260729-1400-fixture",
                    "project_root": str(self.root),
                }
            )
        )
        (self.run_dir / "pieces.json").write_text(
            json.dumps(
                {
                    "pieces": [
                        {
                            "id": "opening-section",
                            "artifact_paths": [
                                "drafts/issue.md#opening",
                                "drafts/never-written.md",
                            ],
                        }
                    ]
                }
            )
        )

        drafts = self.root / "drafts"
        drafts.mkdir()
        self.artifact = drafts / "issue.md"
        self.artifact.write_text("The opening argues one thing, cleanly.\n")

        snapshot_dir = self.run_dir / "rounds" / "opening-section" / "001" / "artifact"
        snapshot_dir.mkdir(parents=True)
        self.snapshot = snapshot_dir / "issue.md"
        self.snapshot.write_text("Round one snapshot.\n")

    def test_hashes_artifact_paths_and_round_snapshots(self):
        proc = run_hash(self.run_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)

        expected = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        hashed = [a for a in payload["artifacts"] if not a["missing"]]
        self.assertEqual(len(hashed), 1)
        self.assertEqual(hashed[0]["sha256"], expected)
        self.assertEqual(hashed[0]["piece_id"], "opening-section")
        # The fragment is preserved in "path" but stripped for resolution.
        self.assertEqual(hashed[0]["path"], "drafts/issue.md#opening")
        self.assertEqual(hashed[0]["resolved_path"], str(self.artifact))

        expected_snapshot = hashlib.sha256(self.snapshot.read_bytes()).hexdigest()
        self.assertEqual(len(payload["round_snapshots"]), 1)
        snap = payload["round_snapshots"][0]
        self.assertEqual(snap["sha256"], expected_snapshot)
        self.assertEqual(snap["piece_id"], "opening-section")
        self.assertEqual(snap["round"], "001")

    def test_missing_artifact_recorded_as_missing_not_skipped(self):
        proc = run_hash(self.run_dir)
        payload = json.loads(proc.stdout)
        missing = [a for a in payload["artifacts"] if a["missing"]]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["path"], "drafts/never-written.md")
        self.assertIsNone(missing[0]["sha256"])

    def test_writes_artifact_hashes_json_in_run_dir(self):
        proc = run_hash(self.run_dir)
        out_file = self.run_dir / "artifact-hashes.json"
        self.assertTrue(out_file.is_file())
        self.assertEqual(
            json.loads(out_file.read_text()), json.loads(proc.stdout)
        )

    def test_hashes_stable_across_runs(self):
        first = run_hash(self.run_dir)
        first_file = (self.run_dir / "artifact-hashes.json").read_text()
        second = run_hash(self.run_dir)
        second_file = (self.run_dir / "artifact-hashes.json").read_text()
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first_file, second_file)

    def test_falls_back_to_run_dir_without_project_root(self):
        (self.run_dir / "run.json").write_text(
            json.dumps({"run_id": "20260729-1400-fixture"})
        )
        local = self.run_dir / "drafts"
        local.mkdir()
        (local / "issue.md").write_text("Run-dir local artifact.\n")
        proc = run_hash(self.run_dir)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["project_root"], str(self.run_dir))
        hashed = [a for a in payload["artifacts"] if not a["missing"]]
        self.assertEqual(hashed[0]["resolved_path"], str(local / "issue.md"))

    def test_missing_pieces_json_is_failure(self):
        (self.run_dir / "pieces.json").unlink()
        proc = run_hash(self.run_dir)
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
