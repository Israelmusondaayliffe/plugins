#!/usr/bin/env python3
"""Validate the capability registry and route decision artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_ROUTE_FIELDS = {
    "primary_route",
    "route_type",
    "plugin",
    "skill",
    "reason",
    "load_order",
    "companions",
    "excluded_routes",
    "verification_needed",
}
ROUTE_TYPES = {"plugin-router", "plugin-skill", "standalone-skill"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def string_list(value: Any, label: str, errors: list[str], *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{label} must be a list of non-empty strings")
        return []
    if not allow_empty and not value:
        errors.append(f"{label} must not be empty")
    if len(value) != len(set(value)):
        errors.append(f"{label} must not contain duplicates")
    return value


def plugin_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    plugins = registry.get("plugins", [])
    if not isinstance(plugins, list):
        return {}
    return {
        item.get("plugin"): item
        for item in plugins
        if isinstance(item, dict) and isinstance(item.get("plugin"), str)
    }


def validate_registry(registry: Any, inventory_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry root must be an object"]

    required_plugins = string_list(registry.get("required_plugins"), "required_plugins", errors, allow_empty=False)
    precedence = string_list(registry.get("routing_precedence"), "routing_precedence", errors, allow_empty=False)
    expected_precedence = [
        "explicit-selection",
        "focused-owned-skill",
        "plugin-front-door",
        "cross-plugin-router",
        "namespaced-before-loose",
        "companions-at-handoff",
        "outcome-contract-preserved",
        "connector-before-workflow",
    ]
    if precedence and precedence != expected_precedence:
        errors.append("routing_precedence is missing or reordered")

    plugins = registry.get("plugins")
    if not isinstance(plugins, list):
        return errors + ["plugins must be a list"]
    index = plugin_index(registry)
    if len(index) != len(plugins):
        errors.append("plugin names must be present and unique")
    if set(index) != set(required_plugins):
        errors.append(
            f"required plugin mismatch: missing={sorted(set(required_plugins) - set(index))} "
            f"extra={sorted(set(index) - set(required_plugins))}"
        )

    external = set(string_list(registry.get("external_companions", []), "external_companions", errors))
    all_owned: dict[str, str] = {}
    for name, record in sorted(index.items()):
        if not NAME_RE.fullmatch(name):
            errors.append(f"invalid plugin name: {name}")
        front_door = record.get("front_door")
        if front_door is not None and (not isinstance(front_door, str) or not NAME_RE.fullmatch(front_door)):
            errors.append(f"{name}: invalid front_door")
        if record.get("explicit_only") and front_door is not None:
            errors.append(f"{name}: explicit-only plugin must not have a front door")
        if not record.get("explicit_only") and front_door is None:
            errors.append(f"{name}: active plugin requires a front door")

        owned = string_list(record.get("owned_skills"), f"{name}.owned_skills", errors, allow_empty=False)
        for skill in owned:
            if not NAME_RE.fullmatch(skill):
                errors.append(f"{name}: invalid skill name {skill}")
            if skill in all_owned:
                errors.append(f"skill {skill} is owned by both {all_owned[skill]} and {name}")
            all_owned[skill] = name
        if front_door is not None and front_door not in owned:
            errors.append(f"{name}: front door is not an owned skill")

        routes = record.get("direct_routes")
        if not isinstance(routes, list):
            errors.append(f"{name}.direct_routes must be a list")
            routes = []
        seen_direct: set[str] = set()
        for route in routes:
            if not isinstance(route, dict):
                errors.append(f"{name}.direct_routes entries must be objects")
                continue
            skill = route.get("skill")
            if skill not in owned:
                errors.append(f"{name}: direct route owns unknown skill {skill}")
            if isinstance(skill, str) and skill in seen_direct:
                errors.append(f"{name}: duplicate direct route for {skill}")
            if isinstance(skill, str):
                seen_direct.add(skill)
            string_list(route.get("triggers"), f"{name}.{skill}.triggers", errors, allow_empty=False)

        companions = string_list(record.get("companions"), f"{name}.companions", errors)
        for companion in companions:
            if companion not in index and companion not in external:
                errors.append(f"{name}: unknown companion {companion}")
        lifecycle = record.get("lifecycle")
        if not isinstance(lifecycle, dict) or lifecycle.get("state") not in {"active", "experimental", "deprecated"}:
            errors.append(f"{name}: lifecycle state is invalid")

        if inventory_root is not None:
            source = inventory_root / name / "skills"
            actual = {path.parent.name for path in source.glob("*/SKILL.md")} if source.is_dir() else set()
            if actual != set(owned):
                errors.append(
                    f"{name}: inventory mismatch missing={sorted(set(owned) - actual)} "
                    f"extra={sorted(actual - set(owned))}"
                )

    expected_count = registry.get("expected_owned_skill_count")
    if expected_count is not None and expected_count != len(all_owned):
        errors.append(f"owned skill count is {len(all_owned)}, expected {expected_count}")

    collisions = registry.get("collision_rules")
    if not isinstance(collisions, list) or len(collisions) != 9:
        errors.append("collision_rules must contain exactly nine cases")
        collisions = []
    seen_collision_ids: set[str] = set()
    for rule in collisions:
        if not isinstance(rule, dict):
            errors.append("collision rule must be an object")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or rule_id in seen_collision_ids:
            errors.append(f"collision rule id must be unique: {rule_id}")
        else:
            seen_collision_ids.add(rule_id)
        string_list(rule.get("match_all"), f"collision.{rule_id}.match_all", errors, allow_empty=False)
        plugin = rule.get("plugin")
        skill = rule.get("skill")
        if plugin not in index or skill not in index.get(plugin, {}).get("owned_skills", []):
            errors.append(f"collision {rule_id}: primary route is not owned")
        expected_type = "plugin-router" if index.get(plugin, {}).get("front_door") == skill else "plugin-skill"
        if rule.get("route_type") != expected_type:
            errors.append(f"collision {rule_id}: route_type must be {expected_type}")
        for key in ("companions", "excluded_routes", "verification_needed"):
            string_list(rule.get(key), f"collision.{rule_id}.{key}", errors)

    return errors


def validate_route(route: Any, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(route, dict):
        return ["route root must be an object"]
    keys = set(route)
    if keys != REQUIRED_ROUTE_FIELDS:
        errors.append(
            f"route fields mismatch: missing={sorted(REQUIRED_ROUTE_FIELDS - keys)} "
            f"extra={sorted(keys - REQUIRED_ROUTE_FIELDS)}"
        )
    route_type = route.get("route_type")
    if route_type not in ROUTE_TYPES:
        errors.append(f"invalid route_type: {route_type}")
    plugin = route.get("plugin")
    skill = route.get("skill")
    if not isinstance(skill, str) or not NAME_RE.fullmatch(skill):
        errors.append("skill must be a kebab-case name")
    if not isinstance(route.get("reason"), str) or not route.get("reason", "").strip():
        errors.append("reason must be a non-empty string")

    index = plugin_index(registry)
    if route_type == "standalone-skill":
        if plugin is not None:
            errors.append("standalone-skill requires plugin=null")
        expected_primary = skill
    else:
        if plugin not in index:
            errors.append(f"unknown plugin: {plugin}")
            expected_primary = None
        else:
            if skill not in index[plugin].get("owned_skills", []):
                errors.append(f"{plugin} does not own {skill}")
            expected_type = "plugin-router" if index[plugin].get("front_door") == skill else "plugin-skill"
            if route_type != expected_type:
                errors.append(f"route_type must be {expected_type} for {plugin}:{skill}")
            expected_primary = f"{plugin}:{skill}"
    if expected_primary and route.get("primary_route") != expected_primary:
        errors.append(f"primary_route must be {expected_primary}")

    load_order = string_list(route.get("load_order"), "load_order", errors, allow_empty=False)
    if load_order and load_order[0] != route.get("primary_route"):
        errors.append("load_order must start with primary_route")
    for key in ("companions", "excluded_routes", "verification_needed"):
        string_list(route.get(key), key, errors)
    return errors


def default_registry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "routing-registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=default_registry_path())
    parser.add_argument("--route", type=Path)
    parser.add_argument("--inventory-root", type=Path)
    args = parser.parse_args()

    try:
        registry = load_json(args.registry)
        errors = validate_registry(registry, args.inventory_root.expanduser() if args.inventory_root else None)
        if args.route:
            route = load_json(args.route)
            errors.extend(validate_route(route, registry))
    except ValueError as exc:
        errors = [str(exc)]
        registry = {}

    result = {
        "valid": not errors,
        "registry": str(args.registry),
        "plugin_count": len(plugin_index(registry)) if isinstance(registry, dict) else 0,
        "owned_skill_count": sum(len(item.get("owned_skills", [])) for item in registry.get("plugins", [])) if isinstance(registry, dict) else 0,
        "collision_rule_count": len(registry.get("collision_rules", [])) if isinstance(registry, dict) else 0,
        "route_checked": str(args.route) if args.route else None,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
