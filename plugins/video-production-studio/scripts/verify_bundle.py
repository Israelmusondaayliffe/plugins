#!/usr/bin/env python3
"""Verify a personal plugin bundle against its bundle specification."""

from __future__ import annotations

import json
import re
from pathlib import Path


PLANNING_ARTIFACTS = {
    "video-brief.md",
    "storyboard.md",
    "shot-list.md",
    "asset-ledger.md",
    "runtime-requirements.md",
    "delivery-checklist.md",
}


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
        claude_manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        spec = json.loads((root / "bundle-spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2
    if (
        manifest.get("name") != root.name
        or claude_manifest.get("name") != root.name
        or spec.get("plugin") != root.name
    ):
        fail(errors, "plugin name must match the source directory")
    versions = {manifest.get("version"), claude_manifest.get("version"), spec.get("version")}
    if len(versions) != 1:
        fail(errors, "plugin manifests and bundle spec versions differ")
    if spec.get("companion_policy") != "optional-at-runtime":
        fail(errors, "companion_policy must be optional-at-runtime")
    required_companions = {"hyperframes", "remotion", "browser", "computer-use"}
    if not required_companions.issubset(set(spec.get("companions", []))):
        fail(errors, "bundle must list the optional production companions")
    completion_states = spec.get("completion_states", {})
    planning = completion_states.get("planning-complete", {})
    rendered = completion_states.get("rendered-delivery-complete", {})
    if set(planning.get("required_artifacts", [])) != PLANNING_ARTIFACTS:
        fail(errors, "planning-complete must require the complete planning bundle")
    if planning.get("rendering_status") != "incomplete" or planning.get("visual_qc_status") != "incomplete":
        fail(errors, "planning-complete must leave rendering and visual QC incomplete")
    if rendered.get("requires_renderer") is not True or rendered.get("requires_video_delivery_qc") is not True:
        fail(errors, "rendered-delivery-complete must require a renderer and video delivery QC")
    if rendered.get("rendering_status") != "complete" or rendered.get("visual_qc_status") != "complete":
        fail(errors, "rendered-delivery-complete must require completed rendering and visual QC")
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
        expected_state = case.get("expected_completion_state")
        if expected_state is not None and expected_state not in completion_states:
            fail(errors, f"routing case expects an unknown completion state: {expected_state}")
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
    if not any(
        case.get("expected_skill") == "video-production-router"
        and case.get("expected_completion_state") == "planning-complete"
        for case in cases
    ):
        fail(errors, "routing cases must cover the no-renderer planning path")
    for required in ("README.md", "bundle-spec.json"):
        if not (root / required).is_file():
            fail(errors, f"missing {required}")
    result = {
        "valid": not errors,
        "plugin": root.name,
        "version": manifest.get("version"),
        "skill_count": len(actual),
        "coordinator_skill_count": len(spec.get("coordinator_skills", [])),
        "routing_case_count": len(cases),
        "completion_state_count": len(completion_states),
        "companion_policy": spec.get("companion_policy"),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
