"""Unit tests for scripts/init_run.py (SPEC sections 7 and 8.2)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_run.py"

BASE_ARGS = [
    "--slug", "akira-editorial",
    "--goal", "Ship AKIRA issue 04 at a clarity level that beats the reference set.",
    "--domain", "prose",
    "--shape", "S2",
    "--created", "2026-07-29T14:00:00Z",
]


def run_init(root, extra=None):
    args = [sys.executable, str(SCRIPT), "--root", str(root)] + BASE_ARGS
    if extra:
        args += extra
    return subprocess.run(args, capture_output=True, text=True)


class TestInitRun(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # resolve() so fixture paths match the script's resolved paths
        # (on macOS /var is a symlink to /private/var).
        self.root = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)

    def test_help_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0)

    def test_creates_full_skeleton_with_valid_json(self):
        proc = run_init(self.root)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        run_dir = Path(payload["run_dir"])
        self.assertEqual(run_dir.name, "20260729-1400-akira-editorial")
        self.assertTrue(run_dir.is_dir())

        # Directory skeleton per SPEC section 7.
        for rel in ("bar", "bar/refs", "waves", "rounds", "claims",
                    "verification", "sessions"):
            self.assertTrue((run_dir / rel).is_dir(), "missing dir: %s" % rel)
        self.assertTrue((run_dir / "CONTEXT.md").is_file())
        self.assertTrue((run_dir / "PLAN.md").is_file())

        # Sealed dir sits outside runs/ (SPEC 11.2).
        sealed = self.root / ".gauntlet" / "sealed" / run_dir.name
        self.assertTrue(sealed.is_dir())
        self.assertEqual(Path(payload["sealed_dir"]), sealed)

        # Every seeded JSON file parses and carries the schema-correct
        # empty structure.
        run = json.loads((run_dir / "run.json").read_text())
        self.assertEqual(run["run_id"], run_dir.name)
        self.assertEqual(run["status"], "briefed")
        self.assertEqual(run["domain_primary"], "prose")
        self.assertEqual(run["execution_shape"], "S2")
        self.assertEqual(run["created"], "2026-07-29T14:00:00Z")
        self.assertEqual(run["current_wave"], 1)
        self.assertIsNone(run["plan_hash"])
        self.assertIsNone(run["stop_reason"])
        self.assertEqual(run["context_isolation"], "clean")
        self.assertEqual(
            run["budgets"],
            {
                "rounds_cap_per_piece": 10,
                "wave_cap": 4,
                "wall_clock_hours_per_session": 6,
                "subagent_cap_per_run": 400,
                "cost_ceiling": "user-set",
            },
        )
        self.assertEqual(run["project_root"], str(self.root.resolve()))

        pieces = json.loads((run_dir / "pieces.json").read_text())
        self.assertEqual(pieces["run_id"], run_dir.name)
        self.assertEqual(pieces["decomposition_owner"], "lead-agent")
        self.assertEqual(pieces["pieces"], [])

        lanes = json.loads((run_dir / "lanes.json").read_text())
        self.assertEqual(lanes, {"shape": "S2", "lanes": []})

        cost = json.loads((run_dir / "cost.json").read_text())
        self.assertEqual(cost["rounds_total"], 0)
        self.assertEqual(cost["subagents_total"], 0)
        self.assertEqual(cost["sessions_total"], 0)
        self.assertEqual(cost["tokens"], "unknown")

        sessions = json.loads((run_dir / "sessions" / "sessions.json").read_text())
        self.assertEqual(sessions, {"sessions": []})

        # stdout mirrors run.json.
        self.assertEqual(payload["run"], run)

    def test_refuses_existing_run_dir(self):
        first = run_init(self.root)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = run_init(self.root)
        self.assertEqual(second.returncode, 1)
        self.assertIn("already exists", second.stderr)

    def test_invalid_domain_is_usage_error(self):
        proc = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--root", str(self.root),
                "--slug", "x", "--goal", "g",
                "--domain", "poetry", "--shape", "S1",
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_invalid_shape_is_usage_error(self):
        proc = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--root", str(self.root),
                "--slug", "x", "--goal", "g",
                "--domain", "code", "--shape", "S9",
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_invalid_slug_is_usage_error(self):
        proc = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--root", str(self.root),
                "--slug", "Bad Slug!", "--goal", "g",
                "--domain", "code", "--shape", "S1",
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_invalid_created_is_usage_error(self):
        proc = run_init(self.root, extra=None)
        self.assertEqual(proc.returncode, 0)
        bad = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--root", str(self.root),
                "--slug", "other", "--goal", "g",
                "--domain", "code", "--shape", "S1",
                "--created", "yesterday-ish",
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
