#!/usr/bin/env python3
"""Verify Signal to System package structure and cross-host metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-beta.1"
SKILLS = {
    "curiosity-compass": "curiosity-compass-template.md",
    "signal-scout": "signal-scout-template.md",
    "research-to-decision-map": "research-to-decision-template.md",
    "workflow-clinic": "workflow-clinic-template.md",
    "capability-matcher-and-brief-builder": "capability-match-template.md",
    "experiment-designer-and-ledger": "experiment-design-template.md",
    "workshop-workbench": "workshop-package-template.md",
    "creative-project-control-room": "creative-control-pack-template.md",
    "session-compounder": "session-compounder-template.md",
    "proof-to-product-mapper": "productization-brief-template.md",
}
SHARED_REFERENCES = {
    "source-and-tool-policy.md",
    "evidence-and-artifact-policy.md",
    "advanced-execution.md",
}
MULTI_TURN_EVALS = {3, 7, 9}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition: bool, message: str, findings: list[str]) -> None:
    if not condition:
        findings.append(message)


def verify() -> list[str]:
    findings: list[str] = []
    codex = load_json(ROOT / ".codex-plugin" / "plugin.json")
    claude = load_json(ROOT / ".claude-plugin" / "plugin.json")

    for field in ("name", "version", "description", "author", "license", "keywords"):
        check(codex.get(field) == claude.get(field), f"manifest mismatch: {field}", findings)
    check(codex.get("name") == "signal-to-system", "incorrect plugin name", findings)
    check(codex.get("version") == VERSION, "incorrect plugin version", findings)
    check("cowork" not in codex.get("keywords", []), "Cowork support is not approved", findings)

    actual_skills = {
        path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
    }
    check(actual_skills == set(SKILLS), "skill inventory differs from the approved ten", findings)

    for name, template in SKILLS.items():
        skill_root = ROOT / "skills" / name
        skill_path = skill_root / "SKILL.md"
        agent_path = skill_root / "agents" / "openai.yaml"
        template_path = skill_root / "assets" / template
        for path in (skill_path, agent_path, template_path):
            check(path.is_file(), f"missing required file: {path.relative_to(ROOT)}", findings)
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([^\s]+)\s*$", text, re.MULTILINE)
        check(bool(match) and match.group(1) == name, f"frontmatter mismatch: {name}", findings)
        check("[TODO:" not in text, f"unfinished scaffold text: {name}", findings)
        check("../../references/source-and-tool-policy.md" in text, f"source policy not linked: {name}", findings)
        check("../../references/evidence-and-artifact-policy.md" in text, f"evidence policy not linked: {name}", findings)
        if agent_path.is_file():
            agent_text = agent_path.read_text(encoding="utf-8")
            check("$" + name in agent_text, f"default prompt does not name skill: {name}", findings)

    actual_references = {
        path.name for path in (ROOT / "references").iterdir() if path.is_file()
    }
    check(SHARED_REFERENCES <= actual_references, "shared reference inventory is incomplete", findings)

    bundle = load_json(ROOT / "bundle-spec.json")
    bundled = {
        name for names in bundle.get("stages", {}).values() for name in names
    }
    check(bundled == set(SKILLS), "bundle-spec skill inventory differs", findings)

    evals = load_json(ROOT / "evals" / "evals.json")
    eval_records = evals.get("evals", [])
    check(len(eval_records) == 10, "expected ten behavior evals", findings)
    check(
        {record.get("expected_skill") for record in eval_records} == set(SKILLS),
        "behavior evals must cover every approved skill exactly once",
        findings,
    )
    for record in eval_records:
        eval_id = record.get("id")
        if eval_id in MULTI_TURN_EVALS:
            check(bool(record.get("follow_up_prompt")), f"eval {eval_id} needs a follow-up turn", findings)
        for relative_path in record.get("files", []):
            check((ROOT / relative_path).is_file(), f"missing eval fixture: {relative_path}", findings)

    routing = load_json(ROOT / "evals" / "trigger-cases.json")
    routing_cases = routing.get("cases", [])
    routing_ids = [case.get("id") for case in routing_cases]
    check(len(routing_ids) == len(set(routing_ids)), "routing case IDs must be unique", findings)
    check(
        all(case.get("expected_skill") in SKILLS for case in routing_cases),
        "every routing case must name an approved expected skill",
        findings,
    )
    for kind in ("positive", "near_neighbor"):
        covered = {
            case.get("expected_skill")
            for case in routing_cases
            if case.get("kind") == kind
        }
        check(covered == set(SKILLS), f"{kind} routing cases must cover every skill", findings)
    check(bool(routing.get("exclusions")), "routing exclusions are required", findings)

    ledger_header = (ROOT / "skills" / "experiment-designer-and-ledger" / "assets" / "experiment-ledger.csv").read_text(encoding="utf-8")
    for field in (
        "record_version",
        "planned_at",
        "run_at",
        "result_recorded_at",
        "invalidation_reason",
        "confounders",
        "raw_evidence_location",
    ):
        check(field in ledger_header.splitlines()[0].split(","), f"experiment ledger missing field: {field}", findings)
    return findings


def main() -> int:
    findings = verify()
    if findings:
        print(json.dumps({"status": "FAIL", "findings": findings}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "skills": len(SKILLS), "version": VERSION}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
