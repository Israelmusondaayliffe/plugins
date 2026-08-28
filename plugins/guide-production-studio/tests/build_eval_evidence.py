#!/usr/bin/env python3
"""Build reproducible Skill Eval Loop evidence from the installed guide contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FILES = {
    "router": ROOT / "skills/guide-production-router/SKILL.md",
    "architect": ROOT / "skills/practical-guide-architect/SKILL.md",
    "builder": ROOT / "skills/practical-guide-builder/SKILL.md",
    "reviewer": ROOT / "skills/guide-acceptance-review/SKILL.md",
    "architecture": ROOT / "skills/guide-production-router/references/guide-architecture.md",
    "rubric": ROOT / "skills/guide-production-router/references/human-acceptance-rubric.md",
    "provenance": ROOT / "skills/guide-production-router/references/provenance-policy.md",
    "visuals": ROOT / "skills/guide-production-router/references/visual-evidence.md",
}

FUNCTIONAL_CHECKS = {
    "f01": [
        ("architect", "Place examples before blanks"),
        ("builder", "completed example before a template"),
    ],
    "f02": [
        ("router", "real, rights-safe example"),
        ("provenance", "Prefer a real, rights-safe example over fiction"),
    ],
    "f03": [("provenance", "Privacy and provenance are separate decisions")],
    "f04": [("router", "Own the teaching product, not merely its prose"), ("architect", "reader problem it solves")],
    "f05": [("architect", "Make components earn their place"), ("architect", "Remove default packaging")],
    "f06": [
        ("visuals", "reader still needs to see the evidence"),
        ("router", "visual evidence or are labeled reference-only"),
    ],
    "f07": [
        ("reviewer", "Require distinct producer and reviewer identities"),
        ("rubric", "only the named human owner can approve"),
    ],
    "f08": [("rubric", "explained at first use")],
    "f09": [("rubric", "purpose, inputs, limits, and judgment criteria")],
    "f10": [
        ("reviewer", "Follow the quick start or first useful action"),
        ("rubric", "complete the first useful action"),
    ],
}

RUBRIC_CHECKS = {
    "r01": [("architecture", "Start with the reader's job"), ("router", "reader understand the idea")],
    "r02": [("rubric", "enough background to understand why the workflow exists")],
    "r03": [("rubric", "explained at first use")],
    "r04": [("builder", "input, action, expected result")],
    "r05": [("provenance", "Label the example's run status at first use")],
    "r06": [("provenance", "Privacy and provenance are separate decisions")],
    "r07": [("rubric", "purpose, inputs, limits, and judgment criteria")],
    "r08": [("rubric", "smallest useful next action, and a stop rule")],
    "r09": [
        ("rubric", "Every page and attachment earns its place"),
        ("visuals", "reader still needs to see the evidence"),
    ],
    "r10": [("rubric", "The producer cannot be the reviewer"), ("reviewer", "Bulk guide work remains blocked")],
}


def run_checks(checks: dict[str, list[tuple[str, str]]]) -> list[dict[str, object]]:
    texts = {name: path.read_text(encoding="utf-8") for name, path in FILES.items()}
    results: list[dict[str, object]] = []
    for case_id, requirements in checks.items():
        missing = [(name, marker) for name, marker in requirements if marker not in texts[name]]
        passed = not missing
        evidence = "; ".join(
            f"{FILES[name]} contains {marker!r}"
            for name, marker in requirements
            if (name, marker) not in missing
        )
        if missing:
            evidence += "; missing=" + repr(missing)
        results.append({"id": case_id, "passed": passed, "evidence": evidence})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trigger-results", type=Path, required=True)
    parser.add_argument("--case-results", type=Path, required=True)
    parser.add_argument("--rubric-results", type=Path, required=True)
    args = parser.parse_args()

    trigger_payload = json.loads(args.trigger_results.read_text(encoding="utf-8"))
    functional = run_checks(FUNCTIONAL_CHECKS)
    rubric = run_checks(RUBRIC_CHECKS)
    cases = {"results": [*trigger_payload["results"], *functional]}
    rubric_payload = {"results": rubric}
    args.case_results.parent.mkdir(parents=True, exist_ok=True)
    args.rubric_results.parent.mkdir(parents=True, exist_ok=True)
    args.case_results.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    args.rubric_results.write_text(json.dumps(rubric_payload, indent=2) + "\n", encoding="utf-8")
    summary = {
        "case_count": len(cases["results"]),
        "case_failures": [item["id"] for item in cases["results"] if item["passed"] is not True],
        "rubric_count": len(rubric),
        "rubric_failures": [item["id"] for item in rubric if item["passed"] is not True],
        "scope": (
            "Machine evidence for plugin behavior and instruction contract. "
            "This is not human approval of a guide."
        ),
    }
    print(json.dumps(summary, indent=2))
    return 0 if not summary["case_failures"] and not summary["rubric_failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
