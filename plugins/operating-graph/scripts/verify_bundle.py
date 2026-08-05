#!/usr/bin/env python3
"""Verify the Operating Graph plugin bundle and its explicit-only contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors: list[str] = []
    try:
        manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        spec = json.loads((root / "bundle-spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}, indent=2))
        return 2

    if manifest.get("name") != "operating-graph" or spec.get("plugin") != "operating-graph":
        errors.append("manifest and bundle spec must identify operating-graph")
    version = manifest.get("version", "")
    if version != "0.2.0":
        errors.append("manifest version must be 0.2.0")
    if spec.get("version") != version:
        errors.append("manifest and bundle spec versions differ")
    try:
        claude_manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        claude_manifest = {}
        errors.append(f"invalid Claude manifest: {error}")
    if claude_manifest.get("name") != manifest.get("name") or claude_manifest.get("version") != version:
        errors.append("Codex and Claude manifests must have matching name and version")
    if spec.get("explicit_only") is not True:
        errors.append("bundle spec must declare explicit_only=true")

    expected_skills = set(spec.get("skills", []))
    actual_skills = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    if expected_skills != actual_skills:
        errors.append(
            f"skill inventory mismatch: missing={sorted(expected_skills - actual_skills)} "
            f"extra={sorted(actual_skills - expected_skills)}"
        )
    for name in sorted(actual_skills):
        metadata = root / "skills" / name / "agents" / "openai.yaml"
        if not metadata.is_file() or "allow_implicit_invocation: false" not in metadata.read_text(encoding="utf-8"):
            errors.append(f"skill is not explicit-only: {name}")

    for name in spec.get("required_templates", []):
        path = root / "assets" / "templates" / name
        if not path.is_file():
            errors.append(f"missing template: {name}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"invalid JSON template {name}: {error}")

    graphctl = root / "scripts" / "graphctl.py"
    graphctl_text = graphctl.read_text(encoding="utf-8") if graphctl.is_file() else ""
    for command in spec.get("required_commands", []):
        if f'command("{command}")' not in graphctl_text or f'"{command}":' not in graphctl_text:
            errors.append(f"graphctl command is not fully wired: {command}")
    for required in ("scripts/graph_engine/dispatch.py", "scripts/verify_bundle.py", "tests/test_dispatch.py"):
        if not (root / required).is_file():
            errors.append(f"missing required runtime file: {required}")

    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json", ".yaml"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if ("[" + "TODO") in text or ("template" + "-placeholder") in text:
                errors.append(f"placeholder remains in {path.relative_to(root)}")

    diamond = root / "assets/templates/diamond-graph.json"
    if diamond.is_file() and graphctl.is_file():
        completed = subprocess.run(
            [sys.executable, str(graphctl), "validate", str(diamond), "--json"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            errors.append(f"diamond template failed graph validation: {completed.stdout}{completed.stderr}")

    result = {
        "valid": not errors,
        "plugin": manifest.get("name"),
        "version": version,
        "skill_count": len(actual_skills),
        "explicit_only_skill_count": sum(
            1
            for name in actual_skills
            if "allow_implicit_invocation: false"
            in (root / "skills" / name / "agents" / "openai.yaml").read_text(encoding="utf-8")
        ),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
