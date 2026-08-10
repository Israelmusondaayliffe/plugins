#!/usr/bin/env python3
"""Verify a plugin installation and source-cache parity on Claude Code or Codex."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Optional


EXCLUDES = {".DS_Store", "__pycache__"}


def file_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDES for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def default_cache_root() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    return codex_home / "plugins" / "cache"


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))).expanduser()


def claude_cache_root(home: Optional[Path] = None) -> Path:
    return (home or claude_home()) / "plugins" / "cache"


def claude_listing(home: Optional[Path] = None) -> dict[str, Any]:
    """Build a Codex-shaped installation listing from Claude Code's registry.

    Reads installed_plugins.json (schema version 2) plus the enabledPlugins map
    in settings.json, so the same select_installation logic serves both hosts.
    """
    base = home or claude_home()
    registry_path = base / "plugins" / "installed_plugins.json"
    if not registry_path.is_file():
        raise RuntimeError(f"Claude Code plugin registry not found: {registry_path}")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    enabled_map: dict[str, Any] = {}
    settings_path = base / "settings.json"
    if settings_path.is_file():
        try:
            enabled_map = json.loads(settings_path.read_text(encoding="utf-8")).get("enabledPlugins", {})
        except (OSError, json.JSONDecodeError):
            enabled_map = {}
    installed = []
    for key, installs in (registry.get("plugins") or {}).items():
        name, _, marketplace = str(key).partition("@")
        for install in installs if isinstance(installs, list) else []:
            installed.append(
                {
                    "name": name,
                    "marketplaceName": marketplace or None,
                    "version": install.get("version"),
                    "enabled": bool(enabled_map.get(key, True)),
                }
            )
    return {"installed": installed}


def select_installation(
    listing: dict[str, Any], plugin_name: str, version: str, marketplace: Optional[str]
) -> tuple[dict[str, Any], str]:
    matches = [
        item
        for item in listing.get("installed", [])
        if item.get("name") == plugin_name
        and item.get("version") == version
        and item.get("enabled") is True
    ]
    if marketplace:
        matches = [item for item in matches if item.get("marketplaceName") == marketplace]
    if not matches:
        target = marketplace or "any configured marketplace"
        raise RuntimeError(f"no enabled {plugin_name} {version} installation found in {target}")
    if len(matches) > 1:
        choices = sorted({str(item.get("marketplaceName")) for item in matches})
        raise RuntimeError("multiple matching installations found; pass --marketplace: " + ", ".join(choices))
    selected_marketplace = matches[0].get("marketplaceName")
    if not isinstance(selected_marketplace, str) or not selected_marketplace:
        raise RuntimeError("matching installation has no marketplaceName")
    return matches[0], selected_marketplace


def verify_install(
    source: Path,
    listing: dict[str, Any],
    marketplace: Optional[str] = None,
    cache_root: Optional[Path] = None,
) -> dict[str, Any]:
    source = source.resolve()
    manifest_path = source / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        manifest_path = source / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plugin_name = manifest["name"]
    version = manifest["version"]
    _, selected_marketplace = select_installation(listing, plugin_name, version, marketplace)
    cache_base = (cache_root or default_cache_root()).expanduser().resolve()
    cache = cache_base / selected_marketplace / plugin_name / version
    if not cache.is_dir():
        raise RuntimeError(f"installed cache is missing: {cache}")
    source_files = file_map(source)
    cache_files = file_map(cache)
    if source_files != cache_files:
        missing = sorted(set(source_files) - set(cache_files))
        extra = sorted(set(cache_files) - set(source_files))
        changed = sorted(path for path in set(source_files) & set(cache_files) if source_files[path] != cache_files[path])
        raise RuntimeError(f"source-cache mismatch missing={missing} extra={extra} changed={changed}")
    return {
        "plugin": plugin_name,
        "marketplace": selected_marketplace,
        "version": version,
        "cache": str(cache),
        "files": len(source_files),
        "parity": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Plugin source directory",
    )
    parser.add_argument(
        "--platform",
        choices=("auto", "claude", "codex"),
        default="auto",
        help="Host to verify against; auto preserves the legacy Codex flow when the codex CLI "
        "is available and falls back to Claude Code's plugin registry otherwise",
    )
    parser.add_argument(
        "--marketplace",
        help="Marketplace name; required when matching installs are ambiguous",
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        help="Base plugin cache directory; defaults to the resolved host's cache "
        "($CLAUDE_CONFIG_DIR or ~/.claude on Claude Code, $CODEX_HOME or ~/.codex on Codex)",
    )
    args = parser.parse_args()
    platform = args.platform
    if platform == "auto":
        # Behavior-preserving: machines where the legacy Codex flow worked keep it.
        platform = "codex" if shutil.which("codex") else "claude"
    if platform == "claude":
        listing_data = claude_listing()
        cache_root = args.cache_root or claude_cache_root()
    else:
        listing = subprocess.run(["codex", "plugin", "list", "--json"], check=True, capture_output=True, text=True)
        listing_data = json.loads(listing.stdout)
        cache_root = args.cache_root
    result = verify_install(args.source, listing_data, args.marketplace, cache_root)
    result["platform"] = platform
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"install verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
