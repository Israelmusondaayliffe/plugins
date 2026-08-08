#!/usr/bin/env python3
"""Route a request through the personal capability registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_routes import load_json, plugin_index, validate_registry, validate_route


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def contains_all(task: str, phrases: list[str]) -> bool:
    return all(normalize(phrase) in task for phrase in phrases)


def build_route(
    plugin: str,
    skill: str,
    route_type: str,
    reason: str,
    companions: list[str] | None = None,
    excluded: list[str] | None = None,
    verification: list[str] | None = None,
) -> dict[str, Any]:
    primary = f"{plugin}:{skill}"
    return {
        "primary_route": primary,
        "route_type": route_type,
        "plugin": plugin,
        "skill": skill,
        "reason": reason,
        "load_order": [primary],
        "companions": companions or [],
        "excluded_routes": excluded or [],
        "verification_needed": verification or ["Verify the selected skill is visible in the current task."],
    }


def route_task(
    task_text: str,
    registry: dict[str, Any],
    explicit_plugin: str | None = None,
    explicit_skill: str | None = None,
) -> dict[str, Any]:
    task = normalize(task_text)
    index = plugin_index(registry)

    if explicit_skill:
        owners = [name for name, record in index.items() if explicit_skill in record.get("owned_skills", [])]
        if len(owners) != 1:
            raise ValueError(f"explicit skill must have one plugin owner: {explicit_skill}")
        owner = owners[0]
        if explicit_plugin and explicit_plugin != owner:
            raise ValueError(f"{explicit_plugin} does not own {explicit_skill}")
        route_type = "plugin-router" if index[owner].get("front_door") == explicit_skill else "plugin-skill"
        return build_route(owner, explicit_skill, route_type, "The user's explicit skill selection wins.")

    if explicit_plugin:
        if explicit_plugin not in index:
            raise ValueError(f"unknown explicit plugin: {explicit_plugin}")
        record = index[explicit_plugin]
        if record.get("explicit_only"):
            for direct in record.get("direct_routes", []):
                if contains_all(task, direct.get("triggers", [])):
                    return build_route(explicit_plugin, direct["skill"], "plugin-skill", "The explicit protocol request matches this ProofLoop action.")
            raise ValueError("ProofLoop requires an explicit run, audit, or memory-review action")
        return build_route(explicit_plugin, record["front_door"], "plugin-router", "The user's explicit plugin selection wins.")

    for rule in registry.get("collision_rules", []):
        if contains_all(task, rule.get("match_all", [])):
            return build_route(
                rule["plugin"],
                rule["skill"],
                rule["route_type"],
                rule["reason"],
                rule.get("companions"),
                rule.get("excluded_routes"),
                rule.get("verification_needed"),
            )

    direct_matches: list[tuple[int, str, str]] = []
    for plugin, record in index.items():
        if record.get("explicit_only") and "proofloop" not in task:
            continue
        for direct in record.get("direct_routes", []):
            triggers = direct.get("triggers", [])
            score = sum(1 for phrase in triggers if normalize(phrase) in task)
            if score:
                direct_matches.append((score, plugin, direct["skill"]))
    if direct_matches:
        direct_matches.sort(reverse=True)
        best_score = direct_matches[0][0]
        best = [item for item in direct_matches if item[0] == best_score]
        if len(best) == 1:
            _, plugin, skill = best[0]
            route_type = "plugin-router" if index[plugin].get("front_door") == skill else "plugin-skill"
            return build_route(plugin, skill, route_type, "The request names one focused action owned by this skill.")

    composite_matches: list[tuple[int, str]] = []
    for plugin, record in index.items():
        if record.get("explicit_only"):
            continue
        score = sum(1 for phrase in record.get("composite_triggers", []) if normalize(phrase) in task)
        if score:
            composite_matches.append((score, plugin))
    if composite_matches:
        composite_matches.sort(reverse=True)
        best_score = composite_matches[0][0]
        best = [item for item in composite_matches if item[0] == best_score]
        if len(best) == 1:
            plugin = best[0][1]
            return build_route(plugin, index[plugin]["front_door"], "plugin-router", "The request spans several stages within one plugin domain.")

    return build_route(
        "capability-operator",
        "capability-router",
        "plugin-router",
        "Ownership is unclear or several plugin domains remain plausible.",
        verification=["Inspect the detailed routing policy and confirm one primary route before loading companions."],
    )


def default_registry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "routing-registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--plugin")
    parser.add_argument("--skill")
    parser.add_argument("--registry", type=Path, default=default_registry_path())
    args = parser.parse_args()
    try:
        registry = load_json(args.registry)
        errors = validate_registry(registry)
        if errors:
            raise ValueError("registry validation failed: " + "; ".join(errors))
        route = route_task(args.task, registry, args.plugin, args.skill)
        route_errors = validate_route(route, registry)
        if route_errors:
            raise ValueError("route validation failed: " + "; ".join(route_errors))
    except ValueError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(route, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
