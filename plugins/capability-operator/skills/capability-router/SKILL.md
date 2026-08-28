---
name: capability-router
description: Routes unclear, multi-stage, or cross-plugin requests on Claude Code, Claude Cowork, or Codex to one primary local plugin or owned skill, with bounded companions, handoffs, exclusions, load order, and verification needs. Use when plugin versus skill ownership is unclear, several local plugins overlap, a request spans capability domains, or the harness needs a deterministic routing decision. Explicit user selections still win, and focused requests should call the narrow owned skill directly.
---

# Capability Router

Choose one primary route across the selected local plugin inventory. Keep the decision small enough for progressive disclosure: load only the selected front door or focused skill, then add companions when a documented handoff is reached.

## Routing precedence

1. Honor an explicit plugin or skill selection as the operating method. Preserve the user's outcome and the parent's work-first definition of done.
2. Route a narrow action to the owned individual skill.
3. Route a multi-stage request within one domain to that plugin's front door.
4. Use this router when several plugin domains compete or ownership is unclear.
5. Prefer a namespaced plugin skill when its plugin is visible. Use a loose mirror only when explicitly selected or the plugin is not visible.
6. Load companion plugins only at a documented handoff.
7. Choose a data-owning connector before choosing the workflow plugin.
8. Prefer Browser, Computer Use, or Artifacts when they are the best execution surface. Do not add blanket checks for unused connectors or surfaces.

## Workflow

1. Read the selected registry for ownership, front doors, direct skills, companions, handoffs, exclusions, and lifecycle state. `assets/routing-registry.json` is a public example, not a local portfolio.
2. Read `references/routing-policy.md` when the request crosses domains or a collision rule applies.
3. Identify the narrowest complete route. Do not return several equal primaries.
4. Fill every field in `assets/route-template.json`.
5. Run `scripts/validate_routes.py --route <route-json>` before relying on a saved route artifact.
6. Load only the primary skill. Add a companion later when its handoff condition becomes true.
7. Confirm the route keeps the requested target-state delta, unresolved count, and total resource cap.

For repeatable checks, run `scripts/route_request.py --registry <registry-json> --task "<request>"`. The script applies explicit trigger and collision rules. Use judgment for requests that fall outside those deterministic rules, then validate the output schema.

## Build a local registry

1. Run `../capability-inventory/scripts/collect_inventory.py --plugins <plugin-root> --output <inventory-json>`. Add `--skip-installed` for a source-only inventory. Installed entries include skills when their local plugin source is readable.
2. Run `scripts/generate_local_registry.py --inventory <inventory-json> --output <registry-json>`. Repeat `--plugin <name>` to select a subset.
3. Review every generated semantic field. The generator marks its output `needs_semantic_review: true` and does not invent companions or collision rules. Explicit routes work during review; implicit routes remain blocked if the field is true, missing, or invalid.
4. Run `scripts/validate_routes.py --registry <registry-json>`. Add `--inventory-root <plugin-root>` only when every selected plugin comes from that source root. Omit it for installed-only validation.
5. Test explicit plugin and skill routes with `scripts/route_request.py`. Set `needs_semantic_review` to `false` only after reviewing implicit triggers.
6. Render a human reference with `scripts/render_routing_reference.py <registry-json> <output-md>`.
7. Render the portfolio ledger with `scripts/render_portfolio_ledger.py <registry-json> <plugin-root> <output-json>` only when a matching source plugin root is available. The human routing reference works with source or installed inventory.

## Output contract

Return exactly these fields:

- `primary_route`: namespaced route in `plugin:skill` form.
- `route_type`: `plugin-router`, `plugin-skill`, or `standalone-skill`.
- `plugin`: owning plugin, or `null` for a true standalone skill.
- `skill`: selected skill.
- `reason`: short evidence-based routing reason.
- `load_order`: ordered namespaced skills to load now.
- `companions`: later routes allowed only at their handoff points.
- `excluded_routes`: plausible routes deliberately not selected.
- `verification_needed`: checks required before execution or handoff.

## Guardrails

- Do not treat a plugin as a runtime action. Runtime routing lands on a skill, app tool, or MCP tool.
- Do not load the full registry into context.
- Do not turn technical filesystem access into authority for unrelated writes, messages, uploads, purchases, account changes, or deletions.
- Stop and report an invalid registry or route artifact. Do not guess around failed validation.

## Error recovery

- Unknown explicit plugin: report it and use `capability-inventory` to refresh the portfolio.
- Unknown explicit skill: check namespaced plugin skills, then loose fallbacks. Do not fabricate a route.
- Missing visible plugin: use the identical loose skill only when it exists, record the fallback, and require fresh-task discovery verification.
- Registry drift: run `scripts/validate_routes.py --registry <registry-json> --inventory-root <plugin-root>`, repair the registry, then render the human reference again.

## Reliability boundary

The LLM interprets intent and handoff state. Scripts enforce names, ownership, route shape, collision fixtures, and registry-to-reference consistency.
