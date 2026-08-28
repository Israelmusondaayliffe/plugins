---
name: shot-continuity-director
description: "Explicit-only direction of a single legible film shot from approved records and continuity locks."
---

# Shot Continuity Director

Activation: explicit-only, either by direct request for `shot-continuity-director` or a routed Film Advisor packet.

## Preconditions

Use a current project record. For continuity-sensitive work, require approved asset IDs and a geography lock. If an asset or place is still only a candidate, name that gate instead of pretending the shot is ready.

## Build a Shot Record

1. Describe only the current shot. Remove inactive characters, stale asset references, prior-scene summaries, and inherited assumptions.
2. Set first-frame occupancy deliberately. State who and what is visible, their positions, facing, gaze, and contact with landmarks.
3. Choose a single format structure: continuous take or an explicitly described sequence of cuts. A multi-shot sequence must state each cut's purpose and continuity locks.
4. Write action as bounded time blocks. Each block must be physically possible and state the active position, action, camera behavior, and critical prop or sound condition.
5. Match optics and camera behavior to the narrative task. Prioritize observed spatial or portrait outcome over brand or metadata labels.
6. Name physics, light direction, audio limits, and positive constraints only where they protect an identified risk.
7. Attach a performance adaptation for each visible character and preserve the locked voice descriptor when a line is spoken.

Do not emit a model-specific final prompt unless an available formatter owns that grammar. Always make the complete normalized handoff described by `film-prompt-director`. `video-production-studio:video-prompt-builder` is an optional model-specific formatter.

## Handoff

Validate `ShotRecord` using `schemas/ShotRecord.schema.json`, then route it to `film-prompt-director` for a format decision or `iteration-supervisor` for a no-spend test plan.
