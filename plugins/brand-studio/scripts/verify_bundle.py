#!/usr/bin/env python3
"""Verify this public plugin package: identity, inventory, links, prompt default, independence."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETIRED = ("brand-world-studio", "gpt-image-2-unified", "nano-banana-unified", "image-prompt-architect")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
MANIFESTS = (".codex-plugin", ".claude-plugin")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
    manifests = {}
    for folder in MANIFESTS:
        path = ROOT / folder / "plugin.json"
        if path.is_file():
            manifests[folder] = json.loads(path.read_text(encoding="utf-8"))
    if not manifests:
        errors.append("missing plugin manifest (.codex-plugin/plugin.json or .claude-plugin/plugin.json)")
    for folder, manifest in manifests.items():
        if manifest.get("name") != spec.get("plugin") or manifest.get("name") != ROOT.name:
            errors.append(f"{folder}: manifest name, bundle spec, and directory name must agree")
        if manifest.get("version") != spec.get("version"):
            errors.append(f"{folder}: manifest and bundle spec versions differ")
        if not SEMVER.match(str(manifest.get("version", ""))):
            errors.append(f"{folder}: version must be plain semver")
    if len(manifests) == 2:
        for field in ("name", "version", "description", "keywords"):
            if manifests[".codex-plugin"].get(field) != manifests[".claude-plugin"].get(field):
                errors.append(f"manifest {field} differs between Codex and Claude manifests")
    skills = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
    if skills != sorted(spec.get("skills", [])):
        errors.append(f"skill inventory mismatch: spec={sorted(spec.get('skills', []))} actual={skills}")
    for skill_file in (ROOT / "skills").glob("*/SKILL.md"):
        text = skill_file.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) < 3 or not re.search(r"^name: " + re.escape(skill_file.parent.name) + r"$", parts[1], re.M):
            errors.append(f"{skill_file.parent.name}: frontmatter name must match the directory")
        if not re.search(r"^description: .+", parts[1] if len(parts) > 1 else "", re.M):
            errors.append(f"{skill_file.parent.name}: missing description")
        for name in RETIRED:
            if name in text:
                errors.append(f"{skill_file.parent.name}: names retired skill {name}")
        for quota in ("exactly 7 prompts", "exactly 10 prompts", "exactly seven prompts", "exactly ten prompts"):
            if quota in text.lower():
                errors.append(f"{skill_file.parent.name}: fixed prompt quota remains ({quota})")
    for md in ROOT.rglob("*.md"):
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", md.read_text(encoding="utf-8", errors="replace")):
            target = target.strip("<>").split("#")[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                (errors if md.name == "SKILL.md" else warnings).append(f"{md.relative_to(ROOT)}: unresolved link {target}")
    for check in spec.get("required_text", []):
        path = ROOT / check["file"]
        if not path.is_file() or check["contains"] not in path.read_text(encoding="utf-8"):
            errors.append(f"{check['file']} must contain: {check['contains']}")
    for check in spec.get("artifact_checks", []):
        cmd = [sys.executable, str(ROOT / check["script"]), str(ROOT / check["artifact"]), "--schema", str(ROOT / check["schema"])]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"artifact check failed: {check['artifact']}: {result.stdout.strip()[:300]}")
    for name in spec.get("forbidden_dependencies", []):
        for skill_file in (ROOT / "skills").glob("*/SKILL.md"):
            if re.search(r"(require|depend|must install|load .* from) [^.]*" + re.escape(name), skill_file.read_text(encoding="utf-8"), re.I):
                errors.append(f"{skill_file.parent.name}: appears to depend on {name}")
    print(json.dumps({"valid": not errors, "plugin": spec.get("plugin"), "version": spec.get("version"),
                      "manifests": sorted(manifests), "skill_count": len(skills), "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
