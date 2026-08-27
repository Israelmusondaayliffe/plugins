#!/usr/bin/env python3
"""Verify a capability plugin bundle against its bundle specification."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def skill_name(skill_file: Path) -> str | None:
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"""^name:\s*["']?([a-z0-9-]+)["']?\s*$""", text, re.MULTILINE)
    return match.group(1) if match else None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    try:
        manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        spec = json.loads((root / "bundle-spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2
    if manifest.get("name") != root.name or spec.get("plugin") != root.name:
        fail(errors, "plugin name must match the source directory")
    if manifest.get("version") != spec.get("version"):
        fail(errors, "manifest and bundle spec versions differ")
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
    router = root / "skills/capability-router"
    router_files = [
        "assets/route-schema.json",
        "assets/route-template.json",
        "assets/routing-registry.json",
        "references/routing-policy.md",
        "scripts/generate_local_registry.py",
        "scripts/render_routing_reference.py",
        "scripts/render_portfolio_ledger.py",
        "scripts/route_request.py",
        "scripts/validate_routes.py",
    ]
    for relative in router_files:
        if not (router / relative).is_file():
            fail(errors, f"capability-router is missing {relative}")
    routing_tests = root / "tests/run_routing_cases.py"
    if routing_tests.is_file():
        completed = subprocess.run(
            ["python3", str(routing_tests)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            fail(errors, f"routing cases failed: {completed.stdout}{completed.stderr}")
    else:
        fail(errors, "missing tests/run_routing_cases.py")
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
