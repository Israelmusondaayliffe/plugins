#!/usr/bin/env python3
"""Guarded stale-data cleanup for a Claude Code home.

Fail-closed allowlist cleaner owned by the harness-maintainer skill.
Dry-run is the default; mutation requires an explicit --apply. Every run
writes an atomic JSON receipt and exits nonzero on any safety failure.

Allowlisted categories (nothing outside these is ever a candidate):
  archived_transcripts      <home>/projects/<proj>/*.jsonl        older than 90 days
  cache_temp                <home>/cache/**                        older than 14 days
  shell_snapshots           <home>/shell-snapshots/**              older than 30 days
  inactive_plugin_versions  <home>/plugins/cache/<mkt>/<plugin>/<ver>/
                            not the installed version, tree older than 30 days

Retention thresholds can only be raised from the CLI, ceilings only lowered.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1.0.0"

DEFAULT_RETENTION_DAYS = {
    "archived_transcripts": 90,
    "cache_temp": 14,
    "shell_snapshots": 30,
    "inactive_plugin_versions": 30,
}
DEFAULT_MAX_CANDIDATES = 10_000
DEFAULT_MAX_BYTES = 2 * 1024 ** 3  # 2 GiB

LOCK_NAME = ".harness-cleanup.lock"

# Deny gate: even inside an allowlisted root, these names are never deletable.
DENY_BASENAMES = {
    "CLAUDE.md",
    "MEMORY.md",
    "settings.json",
    "settings.local.json",
    ".credentials.json",
    "installed_plugins.json",
    "known_marketplaces.json",
    "config.json",
}
DENY_PARTS = {
    "memory",
    "scheduled-tasks",
    "hooks",
    "agents",
    "commands",
    "skills",
    "backups",
    "marketplaces",
    "data",
}

EXIT_OK = 0
EXIT_SAFETY_STOP = 2
EXIT_LOCKED = 3
EXIT_BAD_HOME = 4
EXIT_RECEIPT_FAILURE = 5


class CleanupError(RuntimeError):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_home(override: str | None) -> Path:
    raw = override or os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    if "$" in raw or raw.startswith("~"):
        raise CleanupError(f"refusing unresolved home path: {raw!r}", EXIT_BAD_HOME)
    home = Path(raw)
    if not home.is_absolute():
        raise CleanupError(f"refusing relative home path: {raw!r}", EXIT_BAD_HOME)
    if home.is_symlink():
        raise CleanupError(f"refusing symlinked home: {home}", EXIT_BAD_HOME)
    resolved = home.resolve()
    if not resolved.exists():
        raise CleanupError(f"home does not exist: {resolved}", EXIT_BAD_HOME)
    if resolved == Path("/") or len(resolved.parts) < 3:
        raise CleanupError(f"refusing broad root as home: {resolved}", EXIT_BAD_HOME)
    if resolved == Path.home().resolve():
        raise CleanupError("refusing user home directory as Claude home", EXIT_BAD_HOME)
    if (resolved / ".git").exists():
        raise CleanupError(f"refusing repository root as home: {resolved}", EXIT_BAD_HOME)
    if not (resolved / "settings.json").is_file():
        raise CleanupError(f"{resolved} lacks settings.json; not a Claude home", EXIT_BAD_HOME)
    if not (resolved / "plugins").is_dir() and not (resolved / "projects").is_dir():
        raise CleanupError(f"{resolved} lacks plugins/ and projects/; not a Claude home", EXIT_BAD_HOME)
    return resolved


def acquire_lock(home: Path, warnings: list[str]) -> Path:
    lock = home / LOCK_NAME
    payload = json.dumps({"pid": os.getpid(), "started": utc_now_iso()}).encode()
    for attempt in range(2):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, payload)
            os.close(fd)
            return lock
        except FileExistsError:
            try:
                holder = json.loads(lock.read_text())
                pid = int(holder.get("pid", -1))
            except (OSError, ValueError):
                pid = -1
            alive = False
            if pid > 0:
                try:
                    os.kill(pid, 0)
                    alive = True
                except ProcessLookupError:
                    alive = False
                except PermissionError:
                    alive = True
            if alive:
                raise CleanupError(f"another cleanup run holds the lock (pid {pid})", EXIT_LOCKED)
            if attempt == 0:
                warnings.append(f"removed stale lock left by dead pid {pid}")
                lock.unlink(missing_ok=True)
                continue
            raise CleanupError("could not acquire lock", EXIT_LOCKED)
    raise CleanupError("could not acquire lock", EXIT_LOCKED)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def has_symlink_in_tree(root: Path) -> bool:
    if root.is_symlink():
        return True
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            if (Path(dirpath) / name).is_symlink():
                return True
    return False


def newest_mtime(root: Path) -> float:
    newest = root.lstat().st_mtime
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            try:
                mtime = (Path(dirpath) / name).lstat().st_mtime
            except OSError:
                continue
            newest = max(newest, mtime)
    return newest


def tree_bytes(root: Path) -> int:
    if root.is_file() or root.is_symlink():
        return root.lstat().st_size
    total = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            try:
                total += (Path(dirpath) / name).lstat().st_size
            except OSError:
                continue
    return total


def deny_gate(path: Path, home: Path) -> str | None:
    """Return a reason string when a path must never be touched."""
    rel = path.relative_to(home)
    if path.name in DENY_BASENAMES:
        return f"deny-basename:{path.name}"
    for part in rel.parts:
        if part in DENY_PARTS:
            return f"deny-part:{part}"
    return None


def load_reference_texts(home: Path, extra_files: list[Path]) -> list[str]:
    """Text of live memory and continuity records; candidate paths found here survive."""
    texts: list[str] = []
    sources: list[Path] = []
    projects = home / "projects"
    if projects.is_dir():
        sources.extend(projects.glob("*/memory/**/*.md"))
    claude_md = home / "CLAUDE.md"
    if claude_md.is_file():
        sources.append(claude_md)
    scheduled = home / "scheduled-tasks"
    if scheduled.is_dir():
        sources.extend(scheduled.glob("*/SKILL.md"))
    sources.extend(extra_files)
    for source in sources:
        try:
            texts.append(source.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return texts


def referenced_by_memory(path: Path, home: Path, texts: list[str]) -> bool:
    needles = {str(path), str(path.relative_to(home))}
    return any(needle in text for text in texts for needle in needles)


def installed_plugin_state(home: Path) -> tuple[set[tuple[str, str, str]], set[Path], set[tuple[str, str]]]:
    """Installed (marketplace, plugin, version) triples, resolved install paths, and known plugin pairs."""
    triples: set[tuple[str, str, str]] = set()
    paths: set[Path] = set()
    pairs: set[tuple[str, str]] = set()
    manifest = home / "plugins" / "installed_plugins.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for key, entries in data.get("plugins", {}).items():
        if "@" not in key:
            continue
        plugin, marketplace = key.rsplit("@", 1)
        pairs.add((marketplace, plugin))
        for entry in entries:
            version = str(entry.get("version", ""))
            triples.add((marketplace, plugin, version))
            install_path = entry.get("installPath")
            if install_path:
                try:
                    paths.add(Path(install_path).resolve())
                except OSError:
                    continue
    return triples, paths, pairs


def discover_candidates(home: Path, retention: dict[str, int], now: float,
                        skipped: list[dict], warnings: list[str],
                        reference_texts: list[str]) -> list[dict]:
    candidates: list[dict] = []

    def age_days(mtime: float) -> float:
        return (now - mtime) / 86400.0

    def consider(path: Path, category: str, is_dir: bool, mtime: float) -> None:
        if path.is_symlink():
            skipped.append({"path": str(path), "category": category, "reason": "symlink"})
            return
        if not is_within(path, home) or not is_within(path.resolve(), home):
            skipped.append({"path": str(path), "category": category, "reason": "escapes-home"})
            return
        reason = deny_gate(path, home)
        if reason:
            skipped.append({"path": str(path), "category": category, "reason": reason})
            return
        if age_days(mtime) <= retention[category]:
            return
        if referenced_by_memory(path, home, reference_texts):
            skipped.append({"path": str(path), "category": category, "reason": "referenced-by-memory"})
            return
        candidates.append({
            "path": str(path),
            "category": category,
            "is_dir": is_dir,
            "bytes": tree_bytes(path),
            "mtime": datetime.fromtimestamp(mtime, timezone.utc).isoformat(),
        })

    projects = home / "projects"
    if projects.is_dir():
        for project_dir in sorted(projects.iterdir()):
            if not project_dir.is_dir() or project_dir.is_symlink():
                continue
            for transcript in sorted(project_dir.glob("*.jsonl")):
                if transcript.is_file():
                    consider(transcript, "archived_transcripts", False, transcript.lstat().st_mtime)

    cache = home / "cache"
    if cache.is_dir():
        for dirpath, _dirnames, filenames in os.walk(cache):
            for name in sorted(filenames):
                item = Path(dirpath) / name
                consider(item, "cache_temp", False, item.lstat().st_mtime)

    snapshots = home / "shell-snapshots"
    if snapshots.is_dir():
        for dirpath, _dirnames, filenames in os.walk(snapshots):
            for name in sorted(filenames):
                item = Path(dirpath) / name
                consider(item, "shell_snapshots", False, item.lstat().st_mtime)

    plugin_cache = home / "plugins" / "cache"
    if plugin_cache.is_dir():
        try:
            triples, install_paths, known_pairs = installed_plugin_state(home)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            warnings.append(f"installed_plugins.json unreadable ({exc}); skipping plugin-version cleanup")
            triples, install_paths, known_pairs = set(), set(), set()
            plugin_cache = None
        if plugin_cache is not None:
            for marketplace_dir in sorted(plugin_cache.iterdir()):
                if not marketplace_dir.is_dir() or marketplace_dir.is_symlink():
                    continue
                for plugin_dir in sorted(marketplace_dir.iterdir()):
                    if not plugin_dir.is_dir() or plugin_dir.is_symlink():
                        continue
                    pair = (marketplace_dir.name, plugin_dir.name)
                    if pair not in known_pairs:
                        skipped.append({"path": str(plugin_dir),
                                        "category": "inactive_plugin_versions",
                                        "reason": "plugin-not-in-manifest"})
                        continue
                    for version_dir in sorted(plugin_dir.iterdir()):
                        if not version_dir.is_dir():
                            continue
                        triple = (pair[0], pair[1], version_dir.name)
                        if triple in triples or version_dir.resolve() in install_paths:
                            continue
                        if has_symlink_in_tree(version_dir):
                            skipped.append({"path": str(version_dir),
                                            "category": "inactive_plugin_versions",
                                            "reason": "symlink-in-tree"})
                            continue
                        consider(version_dir, "inactive_plugin_versions", True,
                                 newest_mtime(version_dir))
    return candidates


def open_paths_via_lsof(paths: list[Path]) -> tuple[set[str], bool]:
    """Return the subset of paths lsof reports as open. Second value: check ran."""
    lsof = shutil.which("lsof")
    if lsof is None:
        return set(), False
    open_set: set[str] = set()
    files = [p for p in paths if not p.is_dir()]
    dirs = [p for p in paths if p.is_dir()]
    for batch_start in range(0, len(files), 150):
        batch = files[batch_start:batch_start + 150]
        try:
            result = subprocess.run([lsof, "-Fn", "--", *[str(p) for p in batch]],
                                    capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            open_set.update(str(p) for p in batch)  # cannot verify: fail closed
            continue
        for line in result.stdout.splitlines():
            if line.startswith("n"):
                open_set.add(line[1:])
    for directory in dirs:
        try:
            result = subprocess.run([lsof, "-Fn", "+D", str(directory)],
                                    capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.SubprocessError):
            open_set.add(str(directory))  # cannot verify: fail closed
            continue
        for line in result.stdout.splitlines():
            if line.startswith("n"):
                open_set.add(str(directory))
                break
    return open_set, True


def process_owned_paths(paths: list[Path]) -> set[str]:
    """Paths that appear in any live process command line."""
    try:
        result = subprocess.run(["ps", "-axo", "args"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return {str(p) for p in paths}  # cannot verify: fail closed
    table = result.stdout
    return {str(p) for p in paths if str(p) in table}


def write_receipt_atomic(receipt_dir: Path, receipt: dict) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = receipt_dir / f"harness_cleanup_receipt_{stamp}_{receipt['mode']}.json"
    counter = 0
    while target.exists():
        counter += 1
        target = receipt_dir / f"harness_cleanup_receipt_{stamp}_{receipt['mode']}_{counter}.json"
    data = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", dir=receipt_dir, prefix=f".{target.name}.",
                                     delete=False, encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        temp_name = handle.name
    os.replace(temp_name, target)
    return target


def summarize(candidates: list[dict], key: str = "bytes") -> dict:
    summary: dict[str, dict] = {}
    for item in candidates:
        entry = summary.setdefault(item["category"], {"count": 0, "bytes": 0, "paths": []})
        entry["count"] += 1
        entry["bytes"] += item[key] if key in item else item["bytes"]
        entry["paths"].append(item["path"])
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true",
                        help="actually delete; without this flag the run is a dry-run")
    parser.add_argument("--home", help="Claude home override (default: $CLAUDE_CONFIG_DIR or ~/.claude)")
    parser.add_argument("--receipt-dir", help="receipt directory (default: <home>/cleanup-receipts)")
    parser.add_argument("--continuity-file", action="append", default=[],
                        help="extra continuity/registry file whose referenced paths must survive")
    parser.add_argument("--retention-transcripts", type=int, default=DEFAULT_RETENTION_DAYS["archived_transcripts"])
    parser.add_argument("--retention-cache", type=int, default=DEFAULT_RETENTION_DAYS["cache_temp"])
    parser.add_argument("--retention-snapshots", type=int, default=DEFAULT_RETENTION_DAYS["shell_snapshots"])
    parser.add_argument("--retention-plugin-versions", type=int,
                        default=DEFAULT_RETENTION_DAYS["inactive_plugin_versions"])
    parser.add_argument("--max-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args(argv)

    # Thresholds may only move in the conservative direction.
    retention = {
        "archived_transcripts": max(args.retention_transcripts, DEFAULT_RETENTION_DAYS["archived_transcripts"]),
        "cache_temp": max(args.retention_cache, DEFAULT_RETENTION_DAYS["cache_temp"]),
        "shell_snapshots": max(args.retention_snapshots, DEFAULT_RETENTION_DAYS["shell_snapshots"]),
        "inactive_plugin_versions": max(args.retention_plugin_versions,
                                        DEFAULT_RETENTION_DAYS["inactive_plugin_versions"]),
    }
    max_candidates = min(args.max_candidates, DEFAULT_MAX_CANDIDATES)
    max_bytes = min(args.max_bytes, DEFAULT_MAX_BYTES)

    mode = "apply" if args.apply else "dry-run"
    started = utc_now_iso()
    warnings: list[str] = []
    skipped: list[dict] = []
    safety_checks: list[str] = []
    stop_reason = None
    exit_code = EXIT_OK
    lock_path = None
    home = None
    deleted: list[dict] = []
    receipt_dir = Path(args.receipt_dir).resolve() if args.receipt_dir else None

    try:
        home = discover_home(args.home)
        safety_checks.append("home-discovery-and-marker-check")
        if receipt_dir is None:
            receipt_dir = home / "cleanup-receipts"
        lock_path = acquire_lock(home, warnings)
        safety_checks.append("single-run-lock")

        extra_refs = [Path(p).resolve() for p in args.continuity_file]
        reference_texts = load_reference_texts(home, extra_refs)
        safety_checks.append("memory-and-continuity-reference-scan")

        now = time.time()
        candidates = discover_candidates(home, retention, now, skipped, warnings, reference_texts)
        safety_checks.append("fail-closed-allowlist-discovery")

        total_bytes = sum(c["bytes"] for c in candidates)
        if len(candidates) > max_candidates:
            stop_reason = f"candidate ceiling exceeded: {len(candidates)} > {max_candidates}"
            exit_code = EXIT_SAFETY_STOP
        elif total_bytes > max_bytes:
            stop_reason = f"byte ceiling exceeded: {total_bytes} > {max_bytes}"
            exit_code = EXIT_SAFETY_STOP
        safety_checks.append("candidate-and-byte-ceilings")

        if args.apply and stop_reason is None and candidates:
            paths = [Path(c["path"]) for c in candidates]
            open_set, lsof_ran = open_paths_via_lsof(paths)
            if not lsof_ran:
                stop_reason = "lsof unavailable; open-file check cannot run"
                exit_code = EXIT_SAFETY_STOP
            else:
                safety_checks.append("open-file-check-lsof")
                proc_set = process_owned_paths(paths)
                safety_checks.append("process-ownership-check-ps")
                for candidate in candidates:
                    path = Path(candidate["path"])
                    if str(path) in open_set:
                        skipped.append({"path": str(path), "category": candidate["category"],
                                        "reason": "open-file"})
                        continue
                    if str(path) in proc_set:
                        skipped.append({"path": str(path), "category": candidate["category"],
                                        "reason": "process-owned"})
                        continue
                    # Re-verify immediately before deletion.
                    if path.is_symlink() or not is_within(path.resolve(), home) or deny_gate(path, home):
                        skipped.append({"path": str(path), "category": candidate["category"],
                                        "reason": "final-gate"})
                        continue
                    if not path.exists():
                        skipped.append({"path": str(path), "category": candidate["category"],
                                        "reason": "vanished"})
                        continue
                    try:
                        if candidate["is_dir"]:
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        deleted.append(candidate)
                    except OSError as exc:
                        warnings.append(f"delete failed for {path}: {exc}")
                        exit_code = EXIT_SAFETY_STOP
                        stop_reason = stop_reason or f"delete failed for {path}"
    except CleanupError as exc:
        stop_reason = str(exc)
        exit_code = exc.exit_code
        if receipt_dir is None:
            receipt_dir = (home / "cleanup-receipts") if home else \
                Path(tempfile.gettempdir()) / "harness-cleanup-receipts"
        candidates = []
    finally:
        if lock_path is not None:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    receipt = {
        "tool": "harness_cleanup.py",
        "tool_version": TOOL_VERSION,
        "mode": mode,
        "home": str(home) if home else None,
        "started": started,
        "finished": utc_now_iso(),
        "thresholds_days": retention,
        "ceilings": {"max_candidates": max_candidates, "max_bytes": max_bytes},
        "candidates_by_category": summarize(candidates),
        "candidates_total": {"count": len(candidates), "bytes": sum(c["bytes"] for c in candidates)},
        "deleted_by_category": summarize(deleted),
        "deleted_total": {"count": len(deleted), "bytes": sum(c["bytes"] for c in deleted)},
        "skipped": skipped,
        "safety_checks": safety_checks,
        "warnings": warnings,
        "stop_reason": stop_reason,
        "exit_code": exit_code,
        "complete": True,
    }
    try:
        receipt_path = write_receipt_atomic(receipt_dir, receipt)
    except OSError as exc:
        print(json.dumps({"error": f"receipt write failed: {exc}"}), file=sys.stderr)
        return EXIT_RECEIPT_FAILURE

    print(json.dumps({
        "receipt": str(receipt_path),
        "mode": mode,
        "candidates": receipt["candidates_total"],
        "deleted": receipt["deleted_total"],
        "stop_reason": stop_reason,
        "exit_code": exit_code,
    }, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
