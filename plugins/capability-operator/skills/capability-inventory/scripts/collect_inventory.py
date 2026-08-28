#!/usr/bin/env python3
"""Collect a read-only local capability inventory."""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def skill_records(root: Path, layer: str) -> list[dict]:
    records = []
    if not root.exists():
        return records
    for skill_file in sorted(root.glob("*/SKILL.md")):
        records.append({
            "name": skill_file.parent.name,
            "layer": layer,
            "path": str(skill_file.parent),
            "skill_sha256": hashlib.sha256(skill_file.read_bytes()).hexdigest(),
        })
    return records


def plugin_records(root: Path, errors: list[str]) -> list[dict]:
    records = []
    if not root.exists():
        return records
    for plugin_root in sorted(path for path in root.iterdir() if path.is_dir()):
        manifests = [
            path
            for path in (
                plugin_root / ".codex-plugin" / "plugin.json",
                plugin_root / ".claude-plugin" / "plugin.json",
            )
            if path.is_file()
        ]
        if not manifests:
            continue
        parsed = []
        for manifest in manifests:
            try:
                parsed.append(json.loads(manifest.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{manifest}: {exc}")
        if len(parsed) != len(manifests):
            continue
        identities = {(item.get("name"), item.get("version")) for item in parsed}
        if len(identities) != 1:
            errors.append(f"{plugin_root}: Claude and Codex manifests differ")
            continue
        data = parsed[0]
        if data.get("name") != plugin_root.name or not isinstance(data.get("version"), str):
            errors.append(f"{plugin_root}: manifest name or version is invalid")
            continue
        skills = sorted(path.parent.name for path in plugin_root.glob("skills/*/SKILL.md"))
        records.append({
            "name": data.get("name", plugin_root.name),
            "version": data.get("version"),
            "path": str(plugin_root),
            "skills": skills,
            "manifest_sources": [str(path.relative_to(plugin_root)) for path in manifests],
        })
    return records


def installed_plugins(errors: list[str]) -> list[dict]:
    try:
        run = subprocess.run(
            ["codex", "plugin", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        records = json.loads(run.stdout).get("installed", [])
        for record in records:
            source = record.get("source") if isinstance(record, dict) else None
            source_path = source.get("path") if isinstance(source, dict) else None
            plugin_root = Path(source_path) if isinstance(source_path, str) else None
            record["skills"] = (
                sorted(path.parent.name for path in plugin_root.glob("skills/*/SKILL.md"))
                if plugin_root is not None and plugin_root.is_dir()
                else []
            )
        return records
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        errors.append(f"codex plugin list failed: {exc}")
        return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-skills", type=Path, default=Path.home() / ".codex/skills")
    parser.add_argument("--agent-skills", type=Path, default=Path.home() / ".agents/skills")
    parser.add_argument("--plugins", type=Path, default=Path.home() / "plugins")
    parser.add_argument("--skip-installed", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    errors: list[str] = []
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roots": {
            "codex_skills": str(args.codex_skills),
            "agent_skills": str(args.agent_skills),
            "plugins": str(args.plugins),
        },
        "loose_skills": (
            skill_records(args.codex_skills, "codex")
            + skill_records(args.agent_skills, "agents")
        ),
        "plugin_sources": plugin_records(args.plugins, errors),
        "installed_plugins": [] if args.skip_installed else installed_plugins(errors),
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "errors": len(errors)}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
