#!/usr/bin/env python3
"""Verify the Writing Quality bundle and its protected 47-pattern engine."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


SOURCE_ENGINE_SHA256 = "512f4daa985c7b52503c9c2cb7fb32c1cb4c36efd649d4072e3fec692d4131a6"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def skill_name(skill_file: Path) -> str | None:
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"""^name:\s*["']?([a-z0-9-]+)["']?\s*$""", text, re.MULTILINE)
    return match.group(1) if match else None


def tree_digest(root: Path) -> tuple[int, str]:
    files = sorted(path for path in root.rglob("*") if path.is_file())
    payload = b"".join(
        str(path.relative_to(root)).encode("utf-8")
        + b"\0"
        + hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii")
        + b"\n"
        for path in files
    )
    return len(files), hashlib.sha256(payload).hexdigest()


def load_json(path: Path, errors: list[str]) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"cannot read {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(errors, f"{path.name} must contain an object")
        return {}
    return value


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    codex_manifest = load_json(root / ".codex-plugin/plugin.json", errors)
    claude_manifest = load_json(root / ".claude-plugin/plugin.json", errors)
    spec = load_json(root / "bundle-spec.json", errors)

    names = {codex_manifest.get("name"), claude_manifest.get("name"), spec.get("plugin")}
    if names != {root.name}:
        fail(errors, "plugin names must match the source directory")
    versions = {
        codex_manifest.get("version"),
        claude_manifest.get("version"),
        spec.get("version"),
    }
    if versions != {"0.2.1"}:
        fail(errors, "plugin manifests and bundle spec must agree on version 0.2.1")

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

    prompts = codex_manifest.get("interface", {}).get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts:
        fail(errors, "interface.defaultPrompt must be a non-empty list")

    engine = spec.get("writing_enforcer_engine", {})
    required_engine = {
        "pattern_count": 47,
        "manifest": "skills/writing-enforcer/references/unslop-engine-manifest.json",
        "migration_source_sha256": SOURCE_ENGINE_SHA256,
        "runtime_dependency_on_harness_unslop": False,
        "contextual_score_floor": 8.0,
        "contextual_score_target": 10.0,
        "raw_script_scores_are_verdicts": False,
    }
    if engine != required_engine:
        fail(errors, "writing_enforcer_engine does not match the qualified contract")

    engine_script = root / "skills/writing-enforcer/scripts/engine_check.py"
    engine_result: dict[str, object] = {}
    if not engine_script.is_file():
        fail(errors, "Writing Enforcer engine check is missing")
    else:
        checked = subprocess.run(
            [sys.executable, str(engine_script)],
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            engine_result = json.loads(checked.stdout)
        except json.JSONDecodeError:
            fail(errors, "Writing Enforcer engine check returned invalid JSON")
        if checked.returncode != 0 or engine_result.get("status") != "complete":
            fail(errors, f"Writing Enforcer engine check failed: {engine_result.get('errors')}")

    enforcer = root / "skills/writing-enforcer"
    core = (enforcer / "references/unslop-engine/ai-pattern-taxonomy.md").read_text(encoding="utf-8")
    extended = (enforcer / "references/unslop-engine/extended-patterns.md").read_text(encoding="utf-8")
    patterns = {
        int(value)
        for value in re.findall(r"^#{2,3} Pattern (\d+):", core + "\n" + extended, re.MULTILINE)
    }
    if patterns != set(range(1, 48)):
        fail(errors, "Writing Enforcer must contain pattern headings 1 through 47")

    protected = spec.get("protected_subtrees", {})
    for relative, expected_record in sorted(protected.items()):
        subtree = root / relative
        count, digest = tree_digest(subtree)
        if count != expected_record.get("files") or digest != expected_record.get("inventory_sha256"):
            fail(errors, f"protected subtree drift: {relative}")

    ownership = spec.get("ownership", {})
    if ownership.get("ordinary_prose_owner") != "writing-quality":
        fail(errors, "Writing Quality must own ordinary prose")
    if ownership.get("harness_and_plugin_maintenance_owner") != "harness-engineering:unslop-harness-repair":
        fail(errors, "Harness Unslop ownership record is missing")
    for key in ("writing_quality_requires_harness_unslop", "harness_unslop_requires_writing_quality"):
        if ownership.get(key) is not False:
            fail(errors, f"{key} must be false")

    cases = spec.get("routing_cases", [])
    if len(cases) < 3:
        fail(errors, "at least three routing cases are required")
    for case in cases:
        if case.get("expected_skill") not in expected:
            fail(errors, f"routing case expects an unbundled skill: {case.get('expected_skill')}")
            continue
        evidence_file = case.get("evidence_file")
        evidence_contains = case.get("evidence_contains")
        if not isinstance(evidence_file, str) or not isinstance(evidence_contains, str):
            fail(errors, "routing case must name evidence_file and evidence_contains")
            continue
        evidence_path = root / evidence_file
        if not evidence_path.is_file() or evidence_contains not in evidence_path.read_text(
            encoding="utf-8", errors="replace"
        ):
            fail(errors, f"routing evidence failed: {evidence_file} | {evidence_contains}")

    required_files = (
        "README.md",
        "bundle-spec.json",
        "skills/writing-enforcer/references/unslop-engine/THIRD_PARTY_NOTICES.md",
        "skills/writing-enforcer/references/unslop-engine/source-provenance.md",
        "skills/writing-enforcer/references/unslop-engine/unslop-policy.md",
        "skills/writing-enforcer/scripts/unslop-engine/protected_material_validator.py",
        "skills/writing-enforcer/scripts/protected_scope_validator.py",
    )
    for relative in required_files:
        if not (root / relative).is_file():
            fail(errors, f"missing required Writing Enforcer file: {relative}")

    for path in enforcer.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "plugins/harness-engineering" in text or "from unslop_harness" in text:
            fail(errors, f"Writing Enforcer has a Harness Unslop runtime path: {path.relative_to(root)}")

    result = {
        "valid": not errors,
        "plugin": root.name,
        "version": codex_manifest.get("version"),
        "skill_count": len(actual),
        "coordinator_skill_count": len(spec.get("coordinator_skills", [])),
        "routing_case_count": len(cases),
        "pattern_count": len(patterns),
        "engine_file_count": engine_result.get("file_count"),
        "engine_inventory_sha256": engine_result.get("inventory_sha256"),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
