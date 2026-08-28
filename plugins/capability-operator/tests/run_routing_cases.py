#!/usr/bin/env python3
"""Run the deterministic capability routing acceptance cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROUTER = ROOT / "skills" / "capability-router"
sys.path.insert(0, str(ROUTER / "scripts"))

from generate_local_registry import build_registry  # noqa: E402
from route_request import route_task  # noqa: E402
from validate_routes import load_json, validate_registry, validate_route  # noqa: E402


def main() -> int:
    registry_path = ROUTER / "assets" / "routing-registry.json"
    cases_path = Path(__file__).resolve().parent / "routing-cases.json"
    registry = load_json(registry_path)
    registry_errors = validate_registry(registry, ROOT.parent)
    failures: list[dict] = []
    if registry_errors:
        failures.append({"id": "registry", "errors": registry_errors})

    data = load_json(cases_path)
    cases = data.get("cases", [])
    for case in cases:
        try:
            route = route_task(
                case["task"],
                registry,
                case.get("explicit_plugin"),
                case.get("explicit_skill"),
            )
            errors = validate_route(route, registry)
            expected = case["expected"]
            for key, value in expected.items():
                if route.get(key) != value:
                    errors.append(f"{key}: expected {value!r}, got {route.get(key)!r}")
            if route.get("load_order", []).count(route.get("primary_route")) != 1:
                errors.append("primary route must appear exactly once in load_order")
            if errors:
                failures.append({"id": case["id"], "errors": errors, "route": route})
        except Exception as exc:  # test harness must report every failing fixture
            failures.append({"id": case.get("id", "unknown"), "errors": [str(exc)]})

    guardrails: list[str] = []
    try:
        route_task("Use this unknown thing", registry, explicit_plugin="not-installed")
        guardrails.append("unknown plugin was accepted")
    except ValueError:
        pass
    sample_inventory = {
        "generated_at": "2026-08-27T12:00:00+00:00",
        "plugin_sources": [
            {"name": "alpha-tools", "skills": ["alpha-router", "alpha-check"]},
            {"name": "solo-tool", "skills": ["solo-action"]},
        ],
    }
    generated = build_registry(sample_inventory)
    if generated != build_registry(sample_inventory):
        guardrails.append("registry generation was not deterministic")
    generated_errors = validate_registry(generated)
    if generated_errors:
        guardrails.extend(generated_errors)
    invalid_registry = json.loads(json.dumps(generated))
    invalid_registry["required_plugins"].append("missing-plugin")
    if not validate_registry(invalid_registry):
        guardrails.append("schema-invalid registry was accepted")
    missing_review_flag = json.loads(json.dumps(generated))
    missing_review_flag.pop("needs_semantic_review")
    if not validate_registry(missing_review_flag):
        guardrails.append("registry without a semantic-review flag was accepted")
    try:
        route_task("Use alpha tools", missing_review_flag)
        guardrails.append("registry without a semantic-review flag allowed implicit routing")
    except ValueError:
        pass
    if not generated.get("needs_semantic_review"):
        guardrails.append("generated registry did not require semantic review")
    try:
        route_task("Use alpha tools", generated)
        guardrails.append("unreviewed generated registry allowed implicit routing")
    except ValueError:
        pass
    generated_route = route_task("Use the selected plugin", generated, explicit_plugin="solo-tool")
    if generated_route.get("primary_route") != "solo-tool:solo-action":
        guardrails.append("single-skill generated plugin did not route through its inferred front door")
    explicit_generated = route_task("Use this", generated, explicit_skill="alpha-check")
    if explicit_generated.get("primary_route") != "alpha-tools:alpha-check":
        guardrails.append("generated registry did not preserve explicit skill selection")
    installed_only = build_registry({
        "generated_at": "2026-08-27T12:00:00+00:00",
        "plugin_sources": [],
        "installed_plugins": [
            {
                "name": "installed-tool",
                "skills": ["installed-router", "installed-check"],
                "installed": True,
                "enabled": True,
            },
            {
                "name": "unselected-tool",
                "skills": ["not.routeable"],
                "installed": True,
                "enabled": True,
            }
        ],
    }, ["installed-tool"])
    installed_route = route_task(
        "Use the installed tool",
        installed_only,
        explicit_plugin="installed-tool",
    )
    if installed_route.get("primary_route") != "installed-tool:installed-router":
        guardrails.append("installed-only inventory did not produce an explicit plugin route")
    if installed_only["plugins"][0]["lifecycle"]["visibility"] != "installed":
        guardrails.append("installed-only inventory lost its visibility layer")
    if "source inventory" in installed_only["plugins"][0]["purpose"]:
        guardrails.append("installed-only inventory claimed source provenance")
    if guardrails:
        failures.append({"id": "guardrails", "errors": guardrails})

    result = {
        "valid": not failures,
        "case_count": len(cases),
        "passed": len(cases) - sum(1 for item in failures if item.get("id") not in {"registry", "guardrails"}),
        "composite_cases": sum(1 for case in cases if case.get("kind") == "composite"),
        "focused_cases": sum(1 for case in cases if case.get("kind") == "focused"),
        "collision_cases": sum(1 for case in cases if case.get("kind") == "collision"),
        "guardrail_checks": 13,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
