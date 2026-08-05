#!/usr/bin/env python3
"""Validate the public, fail-closed Sol Advisor runtime profile contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HOSTS = {"codex": "Codex", "claude-code": "Claude Code", "cowork": "Claude Cowork"}
CAPABILITIES = {"fresh_task", "exact_model", "scheduling", "state", "hooks", "discovery"}
STOP_ACTIONS = {"stop", "stop_if_requested"}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[1] / "assets" / "runtime-profiles.json"
    errors: list[str] = []
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2

    if document.get("protocol_version") != 1:
        errors.append("protocol_version must be 1")
    profiles = document.get("profiles")
    if not isinstance(profiles, dict) or set(profiles) != set(HOSTS):
        errors.append("profiles must contain exactly codex, claude-code, and cowork")
        profiles = {}

    for key, host in HOSTS.items():
        profile = profiles.get(key, {})
        if not isinstance(profile, dict) or profile.get("host") != host:
            errors.append(f"{key} host name is invalid")
            continue
        capabilities = profile.get("capabilities")
        if not isinstance(capabilities, dict) or set(capabilities) != CAPABILITIES:
            errors.append(f"{key} must define every runtime capability")
            continue
        for capability, record in capabilities.items():
            if not isinstance(record, dict):
                errors.append(f"{key}.{capability} must be an object")
                continue
            if record.get("required") not in {True, False}:
                errors.append(f"{key}.{capability}.required must be boolean")
            if record.get("supported") not in {True, False, "attested"}:
                errors.append(f"{key}.{capability}.supported must be true, false, or attested")
            if record.get("on_missing") not in STOP_ACTIONS:
                errors.append(f"{key}.{capability}.on_missing must stop explicitly")
            if not isinstance(record.get("evidence"), str) or not record["evidence"].strip():
                errors.append(f"{key}.{capability}.evidence must be non-empty")
            if record.get("supported") is False and record.get("mechanism") is not None:
                errors.append(f"{key}.{capability} must not name a substitute mechanism")
            if record.get("required") is True and record.get("on_missing") != "stop":
                errors.append(f"{key}.{capability} must stop when required support is missing")

    print(json.dumps({"valid": not errors, "profiles": sorted(profiles), "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
