---
name: outcome-engine
description: "Coordinate a path from unclear idea to verified result across research, writing, creative work, operations, planning, and software. Use when the user asks to run Outcome Engine, take an idea from start to finish, turn a fuzzy goal into a plan, resume a multi-phase workflow, or combine clarification, briefing, action slicing, evidence-first delivery, and system review."
---

# Outcome Engine

Route the request to the smallest useful capability. Chain phases only when the user asks for a larger outcome or the current phase clearly requires the next one.

## Router

- Unclear idea, unresolved tradeoffs, or pressure test: load `decision-grill`.
- Mixed or ambiguous intake whose next mode is unclear: load `references/intake-triage.md`, then choose exactly one primary route.
- High-risk assumption that should be tested before a full brief or build: load `references/bounded-test.md`, define the decision rule, then use `evidence-driven-delivery` for the test only.
- Settled context that needs a durable brief: load `to-outcome-brief`.
- Approved brief or plan that needs tasks, tickets, or work packages: load `to-action-slices`.
- Approved slice that needs execution and proof: load `evidence-driven-delivery`.
- Repeated structural friction or upkeep review: load `improve-system-architecture`.
- End-to-end request: run the full flow below.

Load `references/routing-examples.md` when the request is a near match for several routes.

Load `references/measurement-notes.md` when evaluating plugin cost, benchmark usage, or static token estimates.

## Full flow

1. Clarify with `decision-grill` until material branches are resolved or explicitly deferred.
2. Synthesize the result with `to-outcome-brief`.
3. Validate the brief when it is a local file.
4. Break the brief down with `to-action-slices`.
5. Validate the dependency graph when it is a local JSON plan.
6. Execute one unblocked slice with `evidence-driven-delivery`.
7. Report fresh proof before moving to the next slice.
8. Use `improve-system-architecture` when repeated friction points to a structural problem rather than a one-time task.

## Handoff gates

- Do not synthesize a final brief while consequential decisions remain hidden.
- Do not create action slices from an unapproved or invalid brief.
- Do not execute a slice without an observable acceptance check and proof surface.
- Do not mark the plan complete until every required slice has fresh proof.
- Do not execute more than one fresh-context-sized slice unless the task explicitly authorizes the next slice.
- Route a durable cross-task or delegated-slice handoff to Continuity Vault instead of relying on conversation history.
- Do not publish, send, assign, purchase, delete, or change external state without task-specific authorization.

## Resume logic

Inspect the artifacts already present before restarting the flow. If the user has an approved brief, begin with action slices. If valid slices exist, begin with the first unblocked slice. If proof exists, verify that it is fresh and covers the stated acceptance checks.

## Ambiguity rule

When two routes remain plausible after source inspection, ask one focused question. Otherwise state the chosen route and proceed.
