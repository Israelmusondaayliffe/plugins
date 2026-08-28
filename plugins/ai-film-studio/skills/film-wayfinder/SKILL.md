---
name: film-wayfinder
description: "Explicit-only film concept wayfinding that turns an uncertain idea into a testable dramatic premise."
---

# Film Wayfinder

Activation: explicit-only, either by direct request for `film-wayfinder` or a routed Film Advisor packet.

Use this skill when the work is specifically about a film concept, not for general career, life, or project wayfinding. The local method below is complete without another plugin. If `strategy-room:strategy-room-router` is available and the user requests a broader decision interview, it may extend the interview. It does not replace this film record.

## Outcome

Create the concept portion of a `FilmBrief`: format, audience promise, premise, protagonist pressure, opposition, irreversible choice, emotional question, visual world, and a smallest test scene.

## Decision grill

Resolve intent, audience, story, runtime, visual language, sound language, resources, budget, schedule, rights, target models, distribution, risk, and the approval policy. Ask only the next material question. Preserve alternatives and the reason a choice won.

Run the local grill in this order:

1. Inspect supplied records and state what is already decided, assumed, contradicted, or open.
2. Ask for the audience promise and the change the film should produce in that audience.
3. Resolve format, duration, premise, protagonist pressure, opposition, irreversible choice, emotional question, and the smallest test scene.
4. Resolve the visual world, sound world, continuity risks, available assets, budget, schedule, rights, safety limits, target models, intended distribution, and external-action approvals.
5. For each answer, record the decision, alternatives considered, why the choice won, source or owner, confidence, and proof still needed.
6. Ask one question at a time. Skip a question only when a supplied record answers it. Reopen a choice when later evidence conflicts with it.
7. Stop with a named open decision when an answer would materially change the premise, test scene, cost, rights, or safety boundary. Do not fill that gap by guessing.

The local decision record must contain `decided`, `assumed`, `open`, `alternatives`, `decision_reasons`, `source_evidence`, and `next_proof`. A concept is ready only when every material field is decided or explicitly left open with a stop gate.

## Method

1. Separate what the user has decided from what is still an assumption.
2. Find the dramatic engine: someone wants a concrete change, a force resists it, and the cost of failure is legible.
3. Turn abstract theme into observable pressure, choices, objects, places, and behavior.
4. Define the smallest scene that can prove the concept without spending on generation.
5. Record unanswered choices as open decisions. Ask only film-specific questions that would materially change the premise or test scene.

Avoid treating a mood, genre label, or image reference as a complete concept. Do not silently invent plot, period, cast, or visual rules.

## Handoff

Write or update `templates/FilmBrief.json` using `schemas/FilmBrief.schema.json`. Route a production-ready concept to `ai-film-studio`; route a still-uncertain artistic choice back to the user with named options.
