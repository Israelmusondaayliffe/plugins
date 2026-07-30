"""Tests for scripts/lock.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lock.py"


def run_script(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


class LockFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "runs" / "20260729-1200-test"
        self.run_dir.mkdir(parents=True)
        self.lock_path = self.run_dir / "run.lock"

    def lock(self, command, *extra):
        return run_script("--run-dir", str(self.run_dir), command, *extra)

    def write_locks(self, locks):
        self.lock_path.write_text(json.dumps(locks))

    def read_locks(self):
        return json.loads(self.lock_path.read_text())

    def write_sessions(self, sessions):
        sessions_dir = self.run_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        (sessions_dir / "sessions.json").write_text(json.dumps({"sessions": sessions}))


class TestLock(LockFixture):
    def test_acquire_fresh_lane(self):
        proc = self.lock("acquire", "--lane", "a", "--holder", "session-1")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(proc.stdout)
        self.assertTrue(result["ok"])
        self.assertFalse(result["reclaimed"])
        locks = self.read_locks()
        self.assertEqual(locks["a"]["holder"], "session-1")
        self.assertEqual(locks["a"]["lane"], "a")
        self.assertIn("acquired", locks["a"])
        self.assertIn("heartbeat", locks["a"])

    def test_live_lock_refuses_other_holder(self):
        self.write_locks({"a": {
            "lane": "a", "holder": "session-1",
            "acquired": iso(datetime.now(timezone.utc)),
            "heartbeat": iso(datetime.now(timezone.utc)),
        }})
        proc = self.lock("acquire", "--lane", "a", "--holder", "session-2")
        self.assertEqual(proc.returncode, 1)
        result = json.loads(proc.stdout)
        self.assertFalse(result["ok"])
        # Lock untouched.
        self.assertEqual(self.read_locks()["a"]["holder"], "session-1")

    def test_stale_heartbeat_is_reclaimed(self):
        old = iso(datetime.now(timezone.utc) - timedelta(hours=3))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": old, "heartbeat": old}})
        proc = self.lock("acquire", "--lane", "a", "--holder", "session-2")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(proc.stdout)
        self.assertTrue(result["ok"])
        self.assertTrue(result["reclaimed"])
        self.assertEqual(self.read_locks()["a"]["holder"], "session-2")

    def test_exited_holder_is_reclaimed_despite_fresh_heartbeat(self):
        now = iso(datetime.now(timezone.utc))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": now, "heartbeat": now}})
        self.write_sessions([{"index": 1, "entered": now, "exited": now,
                              "exit_reason": "wall-clock"}])
        proc = self.lock("acquire", "--lane", "a", "--holder", "session-2")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.read_locks()["a"]["holder"], "session-2")

    def test_same_holder_reacquires_own_live_lock(self):
        now = iso(datetime.now(timezone.utc))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": now, "heartbeat": now}})
        proc = self.lock("acquire", "--lane", "a", "--holder", "session-1")
        self.assertEqual(proc.returncode, 0)

    def test_heartbeat_updates_timestamp(self):
        old = iso(datetime.now(timezone.utc) - timedelta(hours=1))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": old, "heartbeat": old}})
        proc = self.lock("heartbeat", "--lane", "a", "--holder", "session-1")
        self.assertEqual(proc.returncode, 0)
        self.assertNotEqual(self.read_locks()["a"]["heartbeat"], old)

    def test_heartbeat_wrong_holder_fails(self):
        now = iso(datetime.now(timezone.utc))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": now, "heartbeat": now}})
        proc = self.lock("heartbeat", "--lane", "a", "--holder", "session-2")
        self.assertEqual(proc.returncode, 1)

    def test_release_removes_lock(self):
        now = iso(datetime.now(timezone.utc))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": now, "heartbeat": now}})
        proc = self.lock("release", "--lane", "a", "--holder", "session-1")
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("a", self.read_locks())

    def test_release_wrong_holder_fails(self):
        now = iso(datetime.now(timezone.utc))
        self.write_locks({"a": {"lane": "a", "holder": "session-1",
                                "acquired": now, "heartbeat": now}})
        proc = self.lock("release", "--lane", "a", "--holder", "session-2")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("a", self.read_locks())

    def test_multiple_lanes_share_one_lock_file(self):
        self.lock("acquire", "--lane", "a", "--holder", "session-1")
        proc = self.lock("acquire", "--lane", "b", "--holder", "session-2")
        self.assertEqual(proc.returncode, 0)
        locks = self.read_locks()
        self.assertEqual(set(locks), {"a", "b"})
        self.assertEqual(locks["b"]["holder"], "session-2")

    def test_status_reports_liveness(self):
        stale = iso(datetime.now(timezone.utc) - timedelta(hours=5))
        now = iso(datetime.now(timezone.utc))
        self.write_locks({
            "a": {"lane": "a", "holder": "session-1", "acquired": stale, "heartbeat": stale},
            "b": {"lane": "b", "holder": "session-2", "acquired": now, "heartbeat": now},
        })
        proc = self.lock("status")
        self.assertEqual(proc.returncode, 0)
        result = json.loads(proc.stdout)
        self.assertFalse(result["locks"]["a"]["live"])
        self.assertTrue(result["locks"]["b"]["live"])
        # Single-lane status.
        proc = self.lock("status", "--lane", "c")
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(json.loads(proc.stdout)["locked"])

    def test_usage_errors(self):
        proc = self.lock("acquire", "--holder", "session-1")
        self.assertEqual(proc.returncode, 2)
        proc = self.lock("acquire", "--lane", "a")
        self.assertEqual(proc.returncode, 2)
        proc = run_script("--help")
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
