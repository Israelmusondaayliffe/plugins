---
name: ai-film-studio
description: "Explicit-only film-brief direction that turns an approved concept into a durable FilmBrief."
---

# AI Film Studio

Activation: explicit-only, by `$ai-film-studio:ai-film-studio`, `Use AI Film Studio`, a direct request for `ai-film-studio`, or a validated routed Film Advisor packet.

This skill owns film-specific production context. It does not replace a generic brief primitive owned elsewhere. Its durable interface is `FilmBrief`.

## Front-door sequence

1. Detect an existing project state from durable records. Do not infer approval from conversational momentum.
2. If the outcome is unresolved, route film-specific questions through `film-wayfinder`. Its bundled grill and decision record are the complete local path. Strategy Room is optional.
3. Draft a `FilmBrief` covering the required decisions below and stop for approval.
4. After approval, route architecture through `production-architect` and the eleven-stage workflow in `references/production-workflow.md`.
5. Use the specialist skills for assets, performance, visual development, continuity, prompt handoff, iteration, and post.
6. Before any live external action, return the exact approval gate and cost or destination evidence required.

## Required decisions

Build a brief that names:

- format, duration range, delivery intent, and audience;
- story premise, central pressure, and scene objective;
- continuity-sensitive cast, locations, props, states, and sound needs;
- visual rules, geography risks, and prohibited assumptions;
- proof required at each handoff;
- cost, rights, safety, and external-action gates.

## Method

1. Turn the approved concept into facts, constraints, and unresolved choices.
2. Make every claim trace to a user decision, a supplied record, or a labelled assumption.
3. Define what a location, asset, shot, and delivery result must prove before it can advance.
4. Keep target-model claims out of the brief unless evidence is supplied for the actual selected surface.

## Handoff

Persist the brief as a valid `FilmBrief`. Stop until its status is `approved`. Route approved work to `production-architect`, reusable identities to `asset-bible-director`, and shots to `shot-continuity-director` only after the required assets and geography are approved.
