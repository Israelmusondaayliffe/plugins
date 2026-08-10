#!/usr/bin/env python3
"""Render a human routing reference from the capability registry."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_routes import load_json, validate_registry


def front_door(record: dict) -> str:
    value = record.get("front_door")
    return f"`{record['plugin']}:{value}`" if value else "Explicit ProofLoop skill only"


def render(registry: dict) -> str:
    lines = [
        "# Capability Routing Reference",
        "",
        "> Generated from `capability-operator:capability-router/assets/routing-registry.json`. Edit the registry, then regenerate this file.",
        "",
        f"Snapshot date: {registry['generated_on']}",
        "",
        "## Routing precedence",
        "",
    ]
    labels = {
        "explicit-selection": "An explicit plugin or skill selection wins.",
        "focused-owned-skill": "A narrow action calls the owned skill directly.",
        "plugin-front-door": "A multi-stage request uses the plugin front door.",
        "cross-plugin-router": "Unclear or cross-plugin ownership uses `capability-operator:capability-router`.",
        "namespaced-before-loose": "Prefer namespaced plugin skills; keep loose mirrors as explicit or visibility fallbacks.",
        "companions-at-handoff": "Load companions only at documented handoff points.",
        "outcome-contract-preserved": "A selected plugin controls method, while the parent preserves the user's outcome and definition of done.",
        "connector-before-workflow": "Select the data-owning connector before the workflow plugin.",
    }
    for number, key in enumerate(registry["routing_precedence"], 1):
        lines.append(f"{number}. {labels[key]}")
    lines.extend([
        "",
        "## Portfolio routes",
        "",
        "| Capability | Front door | Use the front door when | Direct skills |",
        "| --- | --- | --- | --- |",
    ])
    for record in registry["plugins"]:
        triggers = "; ".join(record.get("composite_triggers", [])) or "Only when explicitly requested"
        direct = ", ".join(f"`{item['skill']}`" for item in record.get("direct_routes", [])) or "None"
        lines.append(f"| {record['display_name']} | {front_door(record)} | {triggers}. | {direct} |")
    lines.extend(["", "## Required handoffs", ""])
    for record in registry["plugins"]:
        for handoff in record.get("handoffs", []):
            lines.append(f"- {record['display_name']}: {handoff}")
    lines.extend(["", "## Collision rules", ""])
    for rule in registry["collision_rules"]:
        route = f"`{rule['plugin']}:{rule['skill']}`"
        excluded = ", ".join(rule.get("excluded_routes", [])) or "none"
        companions = ", ".join(rule.get("companions", [])) or "none"
        lines.append(f"- `{rule['id']}`: {route}. Companions: {companions}. Excluded: {excluded}.")
    lines.extend([
        "",
        "## Lifecycle and fallback",
        "",
        "All listed personal plugins are active. Prefer their namespaced skills when visible in the task. Use an identical loose mirror only after an explicit selection or a verified plugin-visibility failure.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    registry = load_json(args.registry)
    errors = validate_registry(registry)
    if errors:
        raise SystemExit("registry validation failed: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(registry), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
