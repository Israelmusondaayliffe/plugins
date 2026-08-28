# Capability Routing Policy

## Purpose

Use this policy when ownership is unclear or a request spans more than one plugin in the selected local registry. A focused request should load the owned skill directly.

Explicit selection chooses the operating method, not the definition of done. The parent retains the requested target state, unresolved-work accounting, resource cap, and final completion decision across every route and handoff.

## Collision decisions

A collision rule is local policy. Add one only after reviewing the participating capabilities and recording:

- `match_all`: the minimum phrases that distinguish the collision.
- `plugin` and `skill`: one owned primary route.
- `route_type`: `plugin-router` for a front door or `plugin-skill` for a focused skill.
- `companions`: optional later routes, empty when no handoff is required.
- `excluded_routes`: plausible routes deliberately not selected.
- `reason`: why the primary owns this stage.
- `verification_needed`: evidence required before execution or handoff.

Keep `collision_rules` empty when the local inventory has no reviewed collisions. The generator does not infer them from names.

## Handoffs

Add a handoff only when the primary route cannot complete a later stage and the receiving capability is actually present. A companion is optional until its documented handoff condition becomes true. Absence of a sibling plugin must not stop the primary route from completing its owned work.

## Connector order

Select the connector that owns the data first. Then select the workflow capability that operates on the retrieved material. Connector choice does not decide workflow ownership.

Browser, Computer Use, and artifact tools are execution surfaces. Prefer them when they fit rendered web state, native interfaces, or structured deliverables. Verify only surfaces used by the task or changed by the work.

## Fallbacks

Prefer a namespaced plugin skill. Use an identical loose skill only when the user explicitly selected it or the plugin is missing from the fresh task. Record the fallback and require discovery verification.

If no deterministic route matches, require an explicit plugin or skill instead of inventing ownership. A generated registry with `needs_semantic_review: true` is a starting point, not approval for implicit routing.
