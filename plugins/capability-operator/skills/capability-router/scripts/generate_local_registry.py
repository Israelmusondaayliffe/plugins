#!/usr/bin/env python3
"""Generate a deterministic routing-registry starting point from local inventory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_routes import NAME_RE, validate_registry


ROUTING_PRECEDENCE = [
    "explicit-selection",
    "focused-owned-skill",
    "plugin-front-door",
    "cross-plugin-router",
    "namespaced-before-loose",
    "companions-at-handoff",
    "outcome-contract-preserved",
    "connector-before-workflow",
]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def infer_front_door(plugin: str, skills: list[str]) -> str | None:
    """Return one conservative front-door candidate or require explicit skills."""
    preferred = [f"{plugin}-router", plugin]
    for candidate in preferred:
        if candidate in skills:
            return candidate
    routers = [skill for skill in skills if skill.endswith("-router")]
    if len(routers) == 1:
        return routers[0]
    if len(skills) == 1:
        return skills[0]
    return None


def inventory_date(inventory: dict[str, Any], override: str | None) -> str:
    value = override or str(inventory.get("generated_at", ""))[:10]
    if not DATE_RE.fullmatch(value):
        raise ValueError("provide --snapshot-date YYYY-MM-DD when inventory.generated_at has no date")
    return value


def build_registry(
    inventory: dict[str, Any],
    selected_plugins: list[str] | None = None,
    snapshot_date: str | None = None,
) -> dict[str, Any]:
    sources = inventory.get("plugin_sources")
    if not isinstance(sources, list):
        raise ValueError("inventory.plugin_sources must be a list")
    installed = inventory.get("installed_plugins", [])
    if not isinstance(installed, list):
        raise ValueError("inventory.installed_plugins must be a list")
    selected = set(selected_plugins or [])

    by_name: dict[str, dict[str, Any]] = {}
    for layer, records in (("source", sources), ("installed", installed)):
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"inventory.{layer}_plugins entries must be objects")
            if layer == "installed" and (record.get("installed") is False or record.get("enabled") is False):
                continue
            name = record.get("name")
            skills = record.get("skills")
            if not isinstance(name, str) or not NAME_RE.fullmatch(name):
                raise ValueError(f"invalid {layer} plugin name: {name}")
            if selected and name not in selected:
                continue
            if not isinstance(skills, list):
                if layer == "installed" and name in by_name:
                    by_name[name]["visibility"] = "source+installed"
                    continue
                raise ValueError(f"{name}: {layer} skills must be a list")
            if not skills:
                if layer == "installed" and name in by_name:
                    by_name[name]["visibility"] = "source+installed"
                    continue
                if layer == "installed":
                    continue
                raise ValueError(f"{name}: skills must be a non-empty list")
            if any(not isinstance(skill, str) or not NAME_RE.fullmatch(skill) for skill in skills):
                raise ValueError(f"{name}: skill names must be kebab-case strings")
            if len(skills) != len(set(skills)):
                raise ValueError(f"{name}: duplicate skill names")
            if name in by_name:
                if layer == "source":
                    raise ValueError(f"duplicate plugin source: {name}")
                by_name[name]["visibility"] = "source+installed"
                continue
            by_name[name] = {
                "name": name,
                "skills": sorted(skills),
                "visibility": layer,
            }

    requested = sorted(selected or by_name)
    if not requested:
        raise ValueError("select at least one source or installed plugin with inventoried skills")
    missing = sorted(set(requested) - set(by_name))
    if missing:
        raise ValueError(f"selected plugins are absent from inventory: {missing}")

    plugins = []
    for name in requested:
        skills = by_name[name]["skills"]
        front_door = infer_front_door(name, skills)
        display_name = name.replace("-", " ").title()
        plugins.append({
            "plugin": name,
            "display_name": display_name,
            "purpose": "Generated from local inventory. Confirm this capability boundary before implicit routing.",
            "front_door": front_door,
            "composite_triggers": [f"use {name.replace('-', ' ')}"] if front_door else [],
            "owned_skills": skills,
            "direct_routes": [
                {"skill": skill, "triggers": [skill.replace("-", " ")]}
                for skill in skills
                if skill != front_door
            ],
            "companions": [],
            "handoffs": [],
            "exclusions": [
                "Generated entry: review purpose, front door, triggers, companions, handoffs, exclusions, and lifecycle before implicit routing."
            ],
            "explicit_only": front_door is None,
            "lifecycle": {"state": "active", "visibility": by_name[name]["visibility"]},
        })

    registry = {
        "schema_version": "1.0.0",
        "registry_kind": "generated-local-starting-point",
        "generated_on": inventory_date(inventory, snapshot_date),
        "generated_from": "capability-inventory.plugin_sources+installed_plugins",
        "needs_semantic_review": True,
        "expected_owned_skill_count": sum(len(item["owned_skills"]) for item in plugins),
        "required_plugins": requested,
        "routing_precedence": ROUTING_PRECEDENCE,
        "external_companions": [],
        "collision_rules": [],
        "plugins": plugins,
    }
    errors = validate_registry(registry)
    if errors:
        raise ValueError("generated registry is invalid: " + "; ".join(errors))
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plugin", action="append", dest="plugins")
    parser.add_argument("--snapshot-date")
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        registry = build_registry(inventory, args.plugins, args.snapshot_date)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2), file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "valid": True,
        "output": str(args.output),
        "plugin_count": len(registry["plugins"]),
        "owned_skill_count": registry["expected_owned_skill_count"],
        "needs_semantic_review": registry["needs_semantic_review"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
