#!/usr/bin/env python3
"""Validate an execution-blocked Benchmark Runner handoff."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from validate_skill_output import load_json, validate


PLAN_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|token|secret|password|credential)\b"
    r"\s*[:=]\s*\S+"
)
SECRET_TOKEN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{8,}|hf_[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9_-]{8,})\b"
)
FORBIDDEN_RESULT_FIELDS = {
    "results",
    "aggregates",
    "scores",
    "latency_ms",
    "cost_usd",
    "safety_results",
    "selected_option",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_blocked_handoff.py HANDOFF.json", file=sys.stderr)
        return 2
    artifact = Path(sys.argv[1])
    schema = Path(__file__).resolve().parent.parent / "assets/execution-blocked-schema.json"
    try:
        result = validate(schema, artifact)
        data = load_json(artifact, "artifact")
    except ValueError as exc:
        result = {"valid": False, "skill": "benchmark-runner", "errors": [str(exc)]}
        data = {}
    errors = list(result.get("errors", []))
    if isinstance(data, dict):
        plan_hash = data.get("plan_hash")
        if not isinstance(plan_hash, str) or not PLAN_HASH.fullmatch(plan_hash):
            errors.append("plan_hash must use sha256 followed by 64 lowercase hexadecimal characters")
        case_count = data.get("case_count")
        if isinstance(case_count, bool) or not isinstance(case_count, int) or case_count <= 0:
            errors.append("case_count must be a positive integer")
        for field in (
            "execution_complete",
            "measured_results_complete",
            "model_selection_complete",
        ):
            if data.get(field) is not False:
                errors.append(f"{field} must be false for an execution-blocked handoff")
        if data.get("winner") is not None:
            errors.append("winner must be null for an execution-blocked handoff")
        rerun_command = data.get("rerun_command")
        named_owner = data.get("named_owner")
        if not any(
            isinstance(value, str) and value.strip()
            for value in (rerun_command, named_owner)
        ):
            errors.append("provide a non-empty rerun_command or named_owner")
        missing = data.get("missing_credentials_or_tools", [])
        if isinstance(missing, list):
            if not missing:
                errors.append("missing_credentials_or_tools must not be empty")
            for index, item in enumerate(missing):
                if not isinstance(item, str) or not item.strip():
                    errors.append(
                        f"missing_credentials_or_tools[{index}] must be a non-empty string"
                    )
                elif SECRET_ASSIGNMENT.search(item) or SECRET_TOKEN.search(item):
                    errors.append(
                        f"missing_credentials_or_tools[{index}] exposes a secret value"
                    )
        safety_stops = data.get("safety_stops", [])
        if isinstance(safety_stops, list):
            if not safety_stops:
                errors.append("safety_stops must not be empty")
            for index, item in enumerate(safety_stops):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"safety_stops[{index}] must be a non-empty string")
        present_forbidden = sorted(FORBIDDEN_RESULT_FIELDS.intersection(data))
        if present_forbidden:
            errors.append(
                "execution-blocked handoff must omit measured result fields: "
                f"{present_forbidden}"
            )
    output = {"valid": not errors, "skill": "benchmark-runner", "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
