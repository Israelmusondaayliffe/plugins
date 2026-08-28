#!/usr/bin/env python3
"""Render a validated local plugin portfolio ledger from source manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_routes import load_json, validate_registry


def source_manifest(plugin_root: Path, plugin: str) -> dict:
    paths = [
        path
        for path in (
            plugin_root / ".codex-plugin" / "plugin.json",
            plugin_root / ".claude-plugin" / "plugin.json",
        )
        if path.is_file()
    ]
    if not paths:
        raise SystemExit(f"source manifest is missing for {plugin}")
    manifests = [load_json(path) for path in paths]
    identities = {(item.get("name"), item.get("version")) for item in manifests}
    if len(identities) != 1:
        raise SystemExit(f"Claude and Codex manifests differ for {plugin}")
    return manifests[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("plugin_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    registry = load_json(args.registry)
    errors = validate_registry(registry, args.plugin_root)
    if errors:
        raise SystemExit("registry validation failed: " + "; ".join(errors))

    entries = []
    for record in registry["plugins"]:
        plugin = record["plugin"]
        manifest = source_manifest(args.plugin_root / plugin, plugin)
        if manifest.get("name") != plugin or not isinstance(manifest.get("version"), str):
            raise SystemExit(f"invalid source manifest for {plugin}")
        entries.append({
            "plugin": plugin,
            "display_name": record["display_name"],
            "source_version": manifest["version"],
            "lifecycle": record["lifecycle"]["state"],
            "front_door": record.get("front_door"),
            "explicit_only": bool(record.get("explicit_only")),
            "owned_skill_count": len(record["owned_skills"]),
            "owned_skills": record["owned_skills"],
            "source_root": str(args.plugin_root / plugin),
        })
    ledger = {
        "schema_version": "1.0.0",
        "snapshot_date": registry["generated_on"],
        "needs_semantic_review": bool(registry.get("needs_semantic_review")),
        "source_registry": str(args.registry),
        "plugin_count": len(entries),
        "owned_skill_count": sum(item["owned_skill_count"] for item in entries),
        "plugins": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
