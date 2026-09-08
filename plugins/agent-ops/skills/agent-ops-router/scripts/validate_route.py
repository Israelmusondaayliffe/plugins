#!/usr/bin/env python3
"""Validate an Agent Ops route."""

import json
import sys
from pathlib import Path

ROUTES = {"agent-design", "audit", "loopkit-handoff", "astra-advisor-explicit", "fable-advisor-explicit"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_route.py ROUTE.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2
    errors = []
    if data.get("route") in {"astra-advisor-explicit", "fable-advisor-explicit"} and data.get("activation") != "explicit-only":
        errors.append("advisor routes require explicit-only activation")
    if data.get("route") not in ROUTES:
        errors.append("route is invalid")
    for field in ("outcome", "evidence_surface", "stop_condition", "rationale"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if not isinstance(data.get("boundaries"), list) or not data["boundaries"]:
        errors.append("boundaries must be a non-empty list")
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
