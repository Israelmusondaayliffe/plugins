---
name: asset-bible-director
description: "Explicit-only direction of reusable character, location, prop, and state records for AI film production."
---

# Asset Bible Director

Activation: explicit-only, either by direct request for `asset-bible-director` or a routed Film Advisor packet.

## Asset rule

An asset record represents one reusable identity in one approved state. Keep materially different wardrobe, damage, weather, time-of-day, or prop states separate when they would otherwise conflict in a shot. Use one stable identifier in records and handoffs.

## Build and review

1. Name the asset, type, state, descriptor, reference role, and downstream use.
2. For a character, protect a clear identity reference, a full-body view, a back or alternate view, neutral controllable lighting, visible material detail, and living eyes. Do not bake scene-specific grade or camera style into an identity asset.
3. For a location, record a playable anchor, depth planes, entrances, light rationale, material logic, and an explicit reverse-angle test when continuity requires it.
4. For a prop, record scale, material, state, hand or placement relationship, and any readable content that must be verified visually.
5. Define a stress test that exercises the asset in the actual conditions it must survive. Mark an asset `approved` only against named evidence, never a model reputation.

Edit discipline: make one isolated change, preserve the approved master, and avoid treating a full-frame rerender as harmless. A repair plan must identify what changes and what remains identical.

## Handoff

Validate `AssetRecord` against `schemas/AssetRecord.schema.json`. A character that needs behavioral consistency also requires `performance-director`; a location that supports repeated shots also requires `visual-development-director`.
