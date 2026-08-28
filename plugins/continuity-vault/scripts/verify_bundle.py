#!/usr/bin/env python3
"""Verify a personal plugin bundle against its bundle specification."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path


GRAPHIFY_TREE_SHA256 = "0b7f1e8371ca407516fe7a5a3a9d4eb5b9c4d0b53126e1d818078e05554d7762"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def skill_name(skill_file: Path) -> str | None:
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"""^name:\s*["']?([a-z0-9-]+)["']?\s*$""", text, re.MULTILINE)
    return match.group(1) if match else None


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii")
        digest.update(relative + b"\0" + file_digest + b"\n")
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    try:
        manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        spec = json.loads((root / "bundle-spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2
    if manifest.get("name") != root.name or spec.get("plugin") != root.name:
        fail(errors, "plugin name must match the source directory")
    if manifest.get("version") != spec.get("version"):
        fail(errors, "manifest and bundle spec versions differ")
    if claude_manifest.get("name") != manifest.get("name") or claude_manifest.get("version") != manifest.get("version"):
        fail(errors, "Claude and Codex manifest identity differs")
    expected = set(spec.get("skills", []))
    actual = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    if actual != expected:
        fail(errors, f"skill set mismatch: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    for name in sorted(actual):
        file = root / "skills" / name / "SKILL.md"
        if skill_name(file) != name:
            fail(errors, f"{name}: frontmatter name does not match directory")
    for name in spec.get("coordinator_skills", []):
        skill_root = root / "skills" / name
        for part in ("scripts", "references", "assets"):
            directory = skill_root / part
            if not directory.is_dir() or not any(directory.iterdir()):
                fail(errors, f"{name}: missing non-empty {part} directory")
        for path in skill_root.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".py", ".json"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                if "[TODO" in text or "template-placeholder" in text:
                    fail(errors, f"{name}: placeholder remains in {path.relative_to(root)}")
    prompts = manifest.get("interface", {}).get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts:
        fail(errors, "interface.defaultPrompt must be a non-empty list")
    cases = spec.get("routing_cases", [])
    if len(cases) < 3:
        fail(errors, "at least three routing cases are required")
    for case in cases:
        if case.get("expected_skill") not in expected:
            fail(errors, f"routing case expects an unbundled skill: {case.get('expected_skill')}")
        evidence_file = case.get("evidence_file")
        evidence_contains = case.get("evidence_contains")
        if not isinstance(evidence_file, str) or not isinstance(evidence_contains, str):
            fail(errors, "routing case must name evidence_file and evidence_contains")
            continue
        evidence_path = root / evidence_file
        if not evidence_path.is_file():
            fail(errors, f"routing evidence file is missing: {evidence_file}")
            continue
        evidence_text = evidence_path.read_text(encoding="utf-8", errors="replace")
        if evidence_contains not in evidence_text:
            fail(errors, f"routing evidence not found in {evidence_file}: {evidence_contains}")
    for required in ("README.md", "bundle-spec.json"):
        if not (root / required).is_file():
            fail(errors, f"missing {required}")
    companions = spec.get("companions", [])
    expected_companions = {
        "claude-mem",
        "google-drive",
        "knowledge-work-superpowers",
        "notion",
        "writing-quality",
    }
    if not isinstance(companions, list) or {
        item.get("name") for item in companions if isinstance(item, dict)
    } != expected_companions:
        fail(errors, "optional companion set differs")
    elif any(item.get("required") is not False for item in companions):
        fail(errors, "every companion must be optional")
    graphify_root = root / "skills" / "graphify"
    if tree_sha256(graphify_root) != GRAPHIFY_TREE_SHA256:
        fail(errors, "protected Graphify subtree differs from the Wave 4 freeze")
    fallback_script = root / "skills" / "continuity-router" / "scripts" / "local_fallback.py"
    if not fallback_script.is_file():
        fail(errors, "bounded local fallback script is missing")
    fallback_contracts = {
        "README.md": [
            "exact workspace roots the user authorized",
            "returns `no-evidence`",
            "direct evidence digest",
        ],
        "skills/continuity-router/SKILL.md": [
            "Bounded local fallback",
            "roots the user authorized in the current task",
            "Notion and Google Drive remain optional and source-owned",
            "never promotes, overwrites, deletes, writes a companion, or resolves conflicts",
        ],
        "skills/continuity-router/references/workflow.md": [
            "bounded `continuity-router` local fallback otherwise",
            "direct local digest otherwise",
            "Return `no-evidence`",
        ],
    }
    for relative, phrases in fallback_contracts.items():
        text = (root / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                fail(errors, f"fallback contract missing from {relative}: {phrase}")
    result = {
        "valid": not errors,
        "plugin": root.name,
        "version": manifest.get("version"),
        "skill_count": len(actual),
        "coordinator_skill_count": len(spec.get("coordinator_skills", [])),
        "routing_case_count": len(cases),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
