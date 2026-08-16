---
name: visual-fidelity-gate
description: Lock and validate a source-bound visual target before full web implementation, then enforce an independent hero review, a 7 of 10 threshold, method-switch conditions, and honest incomplete status. Use for likeness-dependent, realistic, cinematic, procedural, shader, WebGL, WebGPU, 3D, simulation, motion-led, immersive, or reference-controlled web experiences where the picture is load-bearing.
---

# Visual Fidelity Gate

Prevent a working interface from being mistaken for a convincing one.

## Workflow

1. Inspect the brief, current rendered state, and one to three viewable reference assets.
2. Fill `assets/visual-contract-template.json`. Lock one first-glance sentence, exactly three required traits, exactly three forbidden failures, named viewports, framing, default and extreme states, selected medium, rejected media, an observable switch condition, and the current source path and hash.
3. Run `scripts/validate_visual_contract.py CONTRACT.json`. Resolve contradictions before implementation.
4. Build or inspect only the representative hero spike. Keep secondary features frozen unless they are part of the hero itself.
5. Capture fresh rendered comparisons at the contract viewports. Use Browser for rendered state and `view_image` for same-size image inspection.
6. Give the contract, references, and fresh captures to a reviewer who did not build the hero. The reviewer judges the image against `references/visual-fidelity-rubric.md` and fills `assets/visual-review-template.json`.
7. Put the validated contract path in the review, then run `scripts/validate_visual_review.py REVIEW.json`. The validator recomputes the contract, source, rendered-artifact, and review hashes and rejects stale or non-viewable evidence.
8. Proceed to `full-build` only when the score is at least 7, no P0, P1, or P2 visual gap remains, the visual gate is passed, no secondary feature started early, and all contract, source, and artifact hashes are current.
9. Below 7, repair the hero, switch the declared method, or report the work as blocked or visually incomplete.

## Boundary

Do not trigger this gate for ordinary colors, spacing, icons, charts, CRUD work, backend work, diagnostics, or a generic request to look clean unless resemblance or picture quality is an explicit acceptance condition.

Use Build Web Apps only after target lock. Web Product Studio keeps site-level ownership when Video Production Studio supplies a video asset or Brand World Studio supplies approved direction.

## Reliability

The validators prove evidence shape, bindings, and state transitions. They cannot judge beauty, realism, likeness, composition, or taste. The independent rendered review owns that judgment.
