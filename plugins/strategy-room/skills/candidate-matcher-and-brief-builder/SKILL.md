---
name: candidate-matcher-and-brief-builder
description: Match a bounded outcome to a qualified person, agent, tool, product, or service, compare candidates against common must-haves, and create a ready-to-use handoff brief when a candidate qualifies. Use when the decision is who or what should do the work. Do not use for plugin portfolio governance, Capability Operator routing, broader strategy, or inferring private traits, price, or availability.
---

# Candidate Matcher And Brief Builder

Choose against the job, then make the handoff usable.

## Activation contract

Use this specialist only through an explicit `$candidate-matcher-and-brief-builder` invocation or a Strategy Room Router handoff to `match`.

Use it when a bounded outcome must be matched to a person, agent, tool, product, or service. Do not use it to decide plugin ownership, installation, skill discovery, or harness routing. Those belong to Capability Operator. Do not use it for broad strategy decisions whose central question is not candidate fit.

## Define the match

State the outcome, audience, deliverable, must-have capabilities, preferences, constraints, timing, supplied budget, collaboration needs, exclusions, permissions, and acceptance evidence. Separate qualification gates from preferences.

## Build the candidate set

- Preserve user-supplied candidates unless they are clearly ineligible.
- Add candidates only when the supplied set is insufficient and current research is authorized or required.
- Use current public professional evidence when features, work, price, geography, compatibility, or availability could change the result.
- For people, use only public professional information. Do not infer sensitive traits, private circumstances, willingness, capacity, or availability.
- Mark unverified cost, capacity, geography, fit, and compatibility as unknown.

## Decide

Apply every must-have as a qualification gate and compare all viable candidates against the same visible criteria. Return exactly one status:

- `qualified match`: one recommended candidate plus a ranked shortlist.
- `provisional match`: a lead candidate whose named unknown could still disqualify it.
- `no qualified match`: failed must-haves plus the smallest next search or fallback.

For each finalist, show evidence, gaps, tradeoffs, and disqualifiers. Do not force a winner, infer missing facts, or create false precision from thin evidence.

## Build the handoff

Use `assets/candidate-match-template.md`. Create a final handoff brief only for a qualified match. For a provisional match, create a draft clearly marked as non-authorizing. For no qualified match, create a search or fallback brief.

Contacting a person, assigning work, buying a product, installing a tool, changing permissions, or sending the brief requires separate user authorization.
