# Brand World Studio

Brand World Studio packages the path from approved positioning to a visual brief, identity system, image-model choice, production prompt pack, and consistency review.

## Owned skills

- brand-world-router
- brand-brief-builder
- brand-model-router
- brand-consistency-verifier
- brandkit
- gpt-image-2-unified
- nano-banana-unified

## Optional companion capabilities

- Creative Production for broader visual exploration when installed
- Canva for asset production and delivery
- Writing Quality for final customer-facing copy validation
- Strategy Room for unresolved positioning decisions

Run `scripts/check_companions.py` to see which optional companions are installed. Missing optional companions do not block owned workflows.

## Local fallbacks

- If positioning is missing and Strategy Room is absent, write `<approved-output-root>/brand-world-studio/positioning-gap.md`. Record the known context, missing decisions, unsupported claims, evidence boundaries, and exact next decision, then stop without inventing strategy.
- The approved output root comes from the active host or the user's explicit file authorization. If neither supplies one, ask the user to approve a local root before writing and keep the complete handoff in the current task until approval.
- Without production companions, retain the owned visual brief, prompt-pack, brandkit, and consistency-review path through the bundled skills.

## Boundaries

- Positioning and commercial claims stay upstream.
- Image edits require the source assets named by the brief.
- A visually strong result still fails if it conflicts with the approved system.

## Verification

Run `scripts/verify_bundle.py` from any directory. Installation is trusted only after plugin validation, skill validation, source-to-cache parity, live listing, real-artifact validation, and clean-task discovery all pass.
