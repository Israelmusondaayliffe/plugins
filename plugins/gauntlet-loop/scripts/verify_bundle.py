#!/usr/bin/env python3
"""Verify the complete Gauntlet Loop plugin bundle."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_SKILLS = {
    "gauntlet",
    "gauntlet-plan",
    "gauntlet-compile",
    "gauntlet-run",
    "gauntlet-handoff",
    "gauntlet-verify",
}
REQUIRED_REFERENCES = {
    "gauntlet-method.md",
    "grill-me-method.md",
    "project-constitution.md",
    "quality-bars.md",
    "knowledge-work-bars.md",
    "workstream-design.md",
    "critic-contract.md",
    "multi-thread-execution.md",
    "session-handoffs.md",
    "integration-waves.md",
    "verification-panel.md",
    "evidence-report.md",
    "state-machine.md",
    "sol-advisor-composition.md",
}
REQUIRED_ASSETS = {
    "project.md",
    "plan.md",
    "handoff.md",
    "thread-charter.md",
    "workstream-charter.md",
    "critic-report.json",
    "verifier-report.json",
    "evidence-report.md",
}
REQUIRED_SCHEMAS = {
    "state.schema.json",
    "gauntlet.schema.json",
    "critic-report.schema.json",
    "verifier-report.schema.json",
    "source-register.schema.json",
    "budget-ledger.schema.json",
    "sol-advisor-composition.schema.json",
}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def verify(root: Path) -> dict[str, object]:
    errors: list[str] = []
    manifest_path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        manifest = {}
        errors.append(f"invalid manifest: {exc}")
    if manifest.get("name") != "gauntlet-loop":
        errors.append("manifest name must be gauntlet-loop")
    version = manifest.get("version", "")
    if version != "1.2.0":
        errors.append("manifest version must be 1.2.0")
    claude_manifest_path = root / ".claude-plugin" / "plugin.json"
    try:
        claude_manifest = json.loads(claude_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        claude_manifest = {}
        errors.append(f"invalid Claude manifest: {exc}")
    if claude_manifest.get("name") != manifest.get("name") or claude_manifest.get("version") != version:
        errors.append("Codex and Claude manifests must have matching name and version")
    for key in ["description", "author", "license", "keywords", "skills", "interface"]:
        if not manifest.get(key):
            errors.append(f"manifest missing {key}")
    if "[TODO:" in json.dumps(manifest):
        errors.append("manifest contains TODO placeholder")

    skills_root = root / "skills"
    actual_skills = {path.name for path in skills_root.iterdir() if path.is_dir()} if skills_root.is_dir() else set()
    if actual_skills != REQUIRED_SKILLS:
        errors.append(f"skill inventory mismatch: expected {sorted(REQUIRED_SKILLS)}, found {sorted(actual_skills)}")
    for name in sorted(REQUIRED_SKILLS):
        skill_path = skills_root / name / "SKILL.md"
        metadata_path = skills_root / name / "agents" / "openai.yaml"
        if not skill_path.is_file():
            errors.append(f"missing skill: {skill_path}")
            continue
        text = skill_path.read_text(encoding="utf-8")
        data = frontmatter(text)
        if data.get("name") != name:
            errors.append(f"skill name mismatch: {name}")
        description = data.get("description", "")
        if not description or len(description) > 1024 or "<" in description or ">" in description:
            errors.append(f"invalid description: {name}")
        if len(text.splitlines()) > 500:
            errors.append(f"skill exceeds 500 lines: {name}")
        if not metadata_path.is_file():
            errors.append(f"missing skill metadata: {metadata_path}")
        else:
            metadata = metadata_path.read_text(encoding="utf-8")
            if "allow_implicit_invocation: false" not in metadata:
                errors.append(f"skill is not explicit-only: {name}")

    for folder, expected in [
        ("references", REQUIRED_REFERENCES),
        ("assets", REQUIRED_ASSETS),
        ("schemas", REQUIRED_SCHEMAS),
    ]:
        present = {path.name for path in (root / folder).iterdir() if path.is_file()} if (root / folder).is_dir() else set()
        missing = sorted(expected - present)
        if missing:
            errors.append(f"missing {folder}: {missing}")

    required_scripts = {
        "gauntletctl.py",
        "verify_bundle.py",
        "validate_manifest.py",
        "initialize_project.py",
        "validate_project.py",
        "create_handoff.py",
        "validate_handoff.py",
        "update_state.py",
        "assemble_evidence_report.py",
        "detect_capabilities.py",
        "record_usage.py",
        "sol_advisor_adapter.py",
    }
    script_names = {path.name for path in (root / "scripts").glob("*.py")}
    missing_scripts = sorted(required_scripts - script_names)
    if missing_scripts:
        errors.append(f"missing scripts: {missing_scripts}")

    for json_path in list((root / "schemas").glob("*.json")) + list((root / "assets").glob("*.json")):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {json_path}: {exc}")

    if not (root / "tests").is_dir():
        errors.append("missing tests directory")
    if not (root / "examples").is_dir():
        errors.append("missing examples directory")

    return {
        "valid": not errors,
        "plugin": str(root),
        "version": version,
        "skill_count": len(actual_skills),
        "errors": errors,
    }


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    result = verify(root)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
