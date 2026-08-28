---
name: visual-development-director
description: "Explicit-only visual development and scene geography direction for repeatable blocking."
---

# Visual Development Director

Activation: explicit-only, either by direct request for `visual-development-director` or a routed Film Advisor packet.

## Outcome

Create a visual-development decision set plus one scene geography lock. It is a map of the place and its usable visual rules, not a prose description of the entire story.

## Method

1. Define visual priorities: material logic, palette derived from the brief, depth, an anchor, and one motivated light rationale. Do not invent an unapproved style reference.
2. Identify fixed landmarks, entrances, playable routes, foreground, midground, background, and a camera-side rule.
3. Name the screen axis and whether it may be crossed. Record positions relative to a landmark and useful distances, not only relative screen words.
4. Record one motivated primary light direction and any exposure priority that later shots must retain.
5. Define each character's allowed starting position, facing, gaze target, movement path, and important prop contact for the relevant shot.
6. Re-state the required relationship in every independently generated shot. Do not rely on an earlier clip to supply continuity.

Use one clearly visible spatial anchor rather than a vague "left side of the room" instruction. A reverse or new angle is a continuity test, not evidence that the unseen space is already known.

## Handoff

Validate visual work against `ProductionPlan` and the geography lock. `shot-continuity-director` consumes the lock and must copy its ID into every continuity-sensitive `ShotRecord`.
