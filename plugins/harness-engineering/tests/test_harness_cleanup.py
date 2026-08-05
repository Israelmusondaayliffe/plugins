from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "harness_cleanup.py"
SPEC = importlib.util.spec_from_file_location("harness_cleanup", SCRIPT)
assert SPEC and SPEC.loader
harness_cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness_cleanup)


def set_age(path: Path, days: int) -> None:
    stamp = time.time() - days * 86400
    os.utime(path, (stamp, stamp), follow_symlinks=False)


def tree_snapshot(root: Path) -> dict[str, int]:
    snapshot: dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            item = Path(dirpath) / name
            snapshot[str(item)] = item.lstat().st_size
    return snapshot


class Fixture:
    """A miniature Claude home with stale, fresh, protected, and decoy data."""

    def __init__(self, root: Path) -> None:
        self.home = root.resolve() / "claude-home"
        h = self.home
        (h / "projects" / "proj-a" / "memory").mkdir(parents=True)
        (h / "cache" / "nested").mkdir(parents=True)
        (h / "shell-snapshots").mkdir()
        (h / "plugins" / "cache" / "mkt" / "plug").mkdir(parents=True)
        (h / "plugins" / "cache" / "mkt" / "ghost" / "9.9.9").mkdir(parents=True)
        (h / "settings.json").write_text("{}\n")
        (h / "CLAUDE.md").write_text("live instructions\n")

        proj = h / "projects" / "proj-a"
        self.stale_transcript = proj / "stale.jsonl"
        self.stale_transcript.write_text("{}\n" * 10)
        set_age(self.stale_transcript, 120)
        self.recent_transcript = proj / "recent.jsonl"
        self.recent_transcript.write_text("{}\n")
        set_age(self.recent_transcript, 3)
        self.referenced_transcript = proj / "referenced.jsonl"
        self.referenced_transcript.write_text("{}\n")
        set_age(self.referenced_transcript, 120)
        (proj / "memory" / "MEMORY.md").write_text(
            f"- important continuity record: {self.referenced_transcript}\n")

        self.stale_cache = h / "cache" / "nested" / "stale.txt"
        self.stale_cache.write_text("old cache data\n")
        set_age(self.stale_cache, 30)
        self.fresh_cache = h / "cache" / "fresh.txt"
        self.fresh_cache.write_text("fresh cache data\n")
        set_age(self.fresh_cache, 2)
        self.decoy_claude_md = h / "cache" / "CLAUDE.md"
        self.decoy_claude_md.write_text("must never be discovered\n")
        set_age(self.decoy_claude_md, 30)
        self.symlinked_cache = h / "cache" / "old-link"
        self.symlinked_cache.symlink_to(h / "settings.json")
        set_age(self.symlinked_cache, 30)

        self.stale_snapshot = h / "shell-snapshots" / "snap-old.sh"
        self.stale_snapshot.write_text("echo old\n")
        set_age(self.stale_snapshot, 45)
        self.fresh_snapshot = h / "shell-snapshots" / "snap-new.sh"
        self.fresh_snapshot.write_text("echo new\n")
        set_age(self.fresh_snapshot, 5)

        plug = h / "plugins" / "cache" / "mkt" / "plug"
        self.old_version = plug / "1.0.0"
        (self.old_version / "skills").mkdir(parents=True)
        (self.old_version / "plugin.json").write_text('{"version": "1.0.0"}\n')
        for item in [self.old_version / "plugin.json", self.old_version / "skills",
                     self.old_version]:
            set_age(item, 60)
        self.current_version = plug / "2.0.0"
        self.current_version.mkdir()
        (self.current_version / "plugin.json").write_text('{"version": "2.0.0"}\n')
        for item in [self.current_version / "plugin.json", self.current_version]:
            set_age(item, 60)
        self.linked_version = plug / "1.5.0"
        self.linked_version.mkdir()
        (self.linked_version / "escape").symlink_to(h / "CLAUDE.md")
        for item in [self.linked_version / "escape", self.linked_version]:
            set_age(item, 60)
        self.ghost_version = h / "plugins" / "cache" / "mkt" / "ghost" / "9.9.9"
        (self.ghost_version / "plugin.json").write_text('{"version": "9.9.9"}\n')
        for item in [self.ghost_version / "plugin.json", self.ghost_version]:
            set_age(item, 60)

        (h / "plugins" / "installed_plugins.json").write_text(json.dumps({
            "version": 2,
            "plugins": {
                "plug@mkt": [{
                    "scope": "user",
                    "installPath": str(self.current_version),
                    "version": "2.0.0",
                }],
            },
        }))

    def run(self, *extra: str) -> int:
        return harness_cleanup.main(["--home", str(self.home), *extra])

    def latest_receipt(self) -> dict:
        receipts = sorted((self.home / "cleanup-receipts").glob("*.json"))
        assert receipts, "no receipt written"
        return json.loads(receipts[-1].read_text())


class HarnessCleanupTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.fx = Fixture(Path(self._temp.name))

    def test_dry_run_never_mutates(self) -> None:
        before = tree_snapshot(self.fx.home)
        code = self.fx.run()
        after = tree_snapshot(self.fx.home)
        added = set(after) - set(before)
        self.assertEqual(code, 0)
        self.assertTrue(all("cleanup-receipts" in path for path in added))
        removed = set(before) - set(after)
        self.assertEqual(removed, set())
        receipt = self.fx.latest_receipt()
        self.assertEqual(receipt["mode"], "dry-run")
        self.assertEqual(receipt["deleted_total"]["count"], 0)
        self.assertGreater(receipt["candidates_total"]["count"], 0)

    def test_apply_deletes_only_allowlisted_stale_unreferenced(self) -> None:
        code = self.fx.run("--apply")
        self.assertEqual(code, 0)
        self.assertFalse(self.fx.stale_transcript.exists())
        self.assertFalse(self.fx.stale_cache.exists())
        self.assertFalse(self.fx.stale_snapshot.exists())
        self.assertFalse(self.fx.old_version.exists())
        receipt = self.fx.latest_receipt()
        self.assertEqual(receipt["deleted_total"]["count"], 4)
        self.assertEqual(set(receipt["deleted_by_category"]),
                         {"archived_transcripts", "cache_temp", "shell_snapshots",
                          "inactive_plugin_versions"})

    def test_recent_files_survive(self) -> None:
        self.fx.run("--apply")
        self.assertTrue(self.fx.recent_transcript.exists())
        self.assertTrue(self.fx.fresh_cache.exists())
        self.assertTrue(self.fx.fresh_snapshot.exists())

    def test_open_files_survive(self) -> None:
        with self.fx.stale_cache.open("r"):
            code = self.fx.run("--apply")
        self.assertEqual(code, 0)
        self.assertTrue(self.fx.stale_cache.exists())
        receipt = self.fx.latest_receipt()
        reasons = {(s["path"], s["reason"]) for s in receipt["skipped"]}
        self.assertIn((str(self.fx.stale_cache), "open-file"), reasons)

    def test_current_plugin_and_skill_versions_survive(self) -> None:
        self.fx.run("--apply")
        self.assertTrue(self.fx.current_version.exists())
        self.assertTrue((self.fx.current_version / "plugin.json").exists())
        self.assertTrue(self.fx.ghost_version.exists(),
                        "plugin without manifest entry must survive")

    def test_memory_referenced_paths_survive(self) -> None:
        self.fx.run("--apply")
        self.assertTrue(self.fx.referenced_transcript.exists())
        receipt = self.fx.latest_receipt()
        reasons = {(s["path"], s["reason"]) for s in receipt["skipped"]}
        self.assertIn((str(self.fx.referenced_transcript), "referenced-by-memory"), reasons)

    def test_symlinks_survive(self) -> None:
        self.fx.run("--apply")
        self.assertTrue(self.fx.symlinked_cache.is_symlink())
        self.assertTrue(self.fx.linked_version.exists())
        self.assertTrue((self.fx.linked_version / "escape").is_symlink())
        self.assertTrue((self.fx.home / "CLAUDE.md").exists())
        self.assertTrue((self.fx.home / "settings.json").exists())

    def test_forbidden_paths_never_discovered(self) -> None:
        self.fx.run()
        receipt = self.fx.latest_receipt()
        all_candidates = [p for entry in receipt["candidates_by_category"].values()
                          for p in entry["paths"]]
        for forbidden in [self.fx.decoy_claude_md, self.fx.home / "CLAUDE.md",
                          self.fx.home / "settings.json",
                          self.fx.home / "plugins" / "installed_plugins.json",
                          self.fx.home / "projects" / "proj-a" / "memory" / "MEMORY.md"]:
            self.assertNotIn(str(forbidden), all_candidates)
        self.fx.run("--apply")
        self.assertTrue(self.fx.decoy_claude_md.exists())

    def test_candidate_ceiling_stops_before_deletion(self) -> None:
        code = self.fx.run("--apply", "--max-candidates", "1")
        self.assertEqual(code, harness_cleanup.EXIT_SAFETY_STOP)
        self.assertTrue(self.fx.stale_transcript.exists())
        self.assertTrue(self.fx.stale_cache.exists())
        receipt = self.fx.latest_receipt()
        self.assertIn("candidate ceiling exceeded", receipt["stop_reason"])
        self.assertEqual(receipt["deleted_total"]["count"], 0)

    def test_byte_ceiling_stops_before_deletion(self) -> None:
        code = self.fx.run("--apply", "--max-bytes", "1")
        self.assertEqual(code, harness_cleanup.EXIT_SAFETY_STOP)
        self.assertTrue(self.fx.stale_transcript.exists())
        receipt = self.fx.latest_receipt()
        self.assertIn("byte ceiling exceeded", receipt["stop_reason"])
        self.assertEqual(receipt["deleted_total"]["count"], 0)

    def test_ceilings_and_retention_cannot_be_loosened(self) -> None:
        code = self.fx.run("--retention-cache", "1", "--max-candidates", "999999")
        self.assertEqual(code, 0)
        receipt = self.fx.latest_receipt()
        self.assertEqual(receipt["thresholds_days"]["cache_temp"], 14)
        self.assertEqual(receipt["ceilings"]["max_candidates"], 10_000)
        self.assertTrue(self.fx.fresh_cache.exists())

    def test_second_run_after_cleanup_is_noop(self) -> None:
        self.assertEqual(self.fx.run("--apply"), 0)
        self.assertEqual(self.fx.run(), 0)
        receipt = self.fx.latest_receipt()
        self.assertEqual(receipt["candidates_total"]["count"], 0)
        self.assertEqual(receipt["deleted_total"]["count"], 0)

    def test_receipts_are_complete_valid_json(self) -> None:
        self.fx.run()
        self.fx.run("--apply")
        receipts = sorted((self.fx.home / "cleanup-receipts").glob("*.json"))
        self.assertGreaterEqual(len(receipts), 2)
        required = {"tool", "tool_version", "mode", "home", "started", "finished",
                    "thresholds_days", "ceilings", "candidates_by_category",
                    "candidates_total", "deleted_by_category", "deleted_total",
                    "skipped", "safety_checks", "warnings", "stop_reason",
                    "exit_code", "complete"}
        for receipt_path in receipts:
            receipt = json.loads(receipt_path.read_text())
            self.assertEqual(required - set(receipt), set())
            self.assertTrue(receipt["complete"])
            self.assertEqual(receipt["tool_version"], harness_cleanup.TOOL_VERSION)

    def test_home_guards(self) -> None:
        for bad in [str(Path.home()), "~/nope", "$HOME/.claude", "relative/path",
                    str(self.fx.home / "projects")]:
            with self.assertRaises(harness_cleanup.CleanupError):
                harness_cleanup.discover_home(bad)
        repo_home = Path(self._temp.name) / "repo-home"
        (repo_home / ".git").mkdir(parents=True)
        (repo_home / "settings.json").write_text("{}\n")
        (repo_home / "plugins").mkdir()
        with self.assertRaises(harness_cleanup.CleanupError):
            harness_cleanup.discover_home(str(repo_home))

    def test_single_run_lock(self) -> None:
        lock = self.fx.home / harness_cleanup.LOCK_NAME
        lock.write_text(json.dumps({"pid": os.getpid(), "started": "now"}))
        code = self.fx.run()
        self.assertEqual(code, harness_cleanup.EXIT_LOCKED)
        self.assertTrue(self.fx.stale_cache.exists())
        lock.unlink()


if __name__ == "__main__":
    unittest.main()
