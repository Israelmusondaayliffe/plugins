#!/usr/bin/env python3
"""Verify Guide Production Studio source structure and deterministic checks."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    try:
        manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        spec = json.loads((root / "bundle-spec.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2

    if manifest.get("name") != spec.get("plugin"):
        errors.append("manifest and bundle-spec plugin names differ")
    if manifest.get("version") != spec.get("version"):
        errors.append("manifest and bundle-spec versions differ")
    prompts = manifest.get("interface", {}).get("defaultPrompt")
    if not isinstance(prompts, list) or len(prompts) < 3:
        errors.append("interface.defaultPrompt must contain at least three prompts")

    expected = set(spec.get("skills", []))
    actual = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    if actual != expected:
        errors.append(f"skill mismatch: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    for name in sorted(actual):
        path = root / "skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE)
        if not match or match.group(1) != name:
            errors.append(f"{name}: frontmatter name does not match folder")
        if len(text.splitlines()) > 500:
            errors.append(f"{name}: SKILL.md exceeds 500 lines")

    for relative in spec.get("required_files", []):
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    benchmark_path = root / ".plugin-eval/benchmark.json"
    try:
        benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        if len(benchmark.get("scenarios", [])) < 5:
            errors.append("benchmark must contain at least five scenarios")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid benchmark: {exc}")

    try:
        triggers = json.loads((root / "tests/trigger-cases.json").read_text(encoding="utf-8"))["cases"]
        positives = sum(case.get("should_trigger") is True for case in triggers)
        negatives = sum(case.get("should_trigger") is False for case in triggers)
        if positives != 10 or negatives != 10:
            errors.append(f"trigger suite must contain 10 positive and 10 negative cases, got {positives}/{negatives}")
        outcomes = json.loads((root / "tests/outcome-cases.json").read_text(encoding="utf-8"))["cases"]
        if len(outcomes) != 10:
            errors.append("outcome suite must contain ten regression cases")
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f"invalid case suite: {exc}")

    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".py"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            placeholder_token = "[" + "TODO"
            scaffold_token = "template" + "-placeholder"
            if placeholder_token in text or scaffold_token in text:
                errors.append(f"placeholder remains in {path.relative_to(root)}")

    completed = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append(f"unit tests failed: {completed.stdout}{completed.stderr}")

    result = {
        "valid": not errors,
        "plugin": manifest.get("name"),
        "version": manifest.get("version"),
        "skill_count": len(actual),
        "trigger_cases": 20,
        "outcome_cases": 10,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
