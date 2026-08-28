---
name: brand-world-router
description: Routes brand visual work across decision brief, identity system, image-model selection, production prompt pack, and consistency verification. Use when a brand, campaign, logo system, visual world, or image series needs one coherent production path. Keeps positioning upstream, selects only the skills needed, and validates a primary route before generation.
---

# Brand World Router

## Overview

Choose the brand-production stage before generating images. Brand World owns the visual system after positioning and business strategy are settled.

## Workflow

1. Confirm the business or product context, audience, positioning source, visual deliverables, source assets, and forbidden directions.
2. If positioning is missing, use the local positioning fallback below instead of choosing a visual route.
3. Choose one primary route with references/workflow.md.
4. Run the plugin companion preflight only for an optional connected surface selected for the task.
5. Fill assets/output-template.json and run scripts/validate_output.py.
6. Use brand-brief-builder for decisions, brandkit for identity boards, brand-model-router for model choice, the selected image prompter for production prompts, and brand-consistency-verifier for series review.
7. Do not invent positioning or brand claims that the supplied strategy does not support.

## Local positioning fallback

- Strategy Room is optional. If it is available and explicitly selected, hand it the unresolved positioning decision.
- When Strategy Room is absent, write `<approved-output-root>/brand-world-studio/positioning-gap.md` with the known context, missing decisions, unsupported claims, evidence boundaries, and exact next decision.
- Use an output root supplied by the active host or explicitly authorized by the user. If no root is authorized, ask for one before writing and keep the complete handoff in the current task until approval.
- Stop after the positioning-gap handoff. Do not invent strategy or continue into visual production.

## Owned production fallback

Creative Production, Canva, and Writing Quality are optional. Without production companions, keep the owned visual brief, prompt-pack, brandkit, and consistency-review path through the bundled skills.

## Error Handling

- If positioning is missing, use Strategy Room only when available and explicitly selected. Otherwise return the local positioning-gap handoff.
- If source assets are required but missing, request or record them before an edit route.
- If visual directions conflict, choose one primary system and record rejected directions.

## Reliability Notes

The model selects the creative route. The validator enforces one allowed route, a named brand job, a rationale, and a positioning-source decision.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
