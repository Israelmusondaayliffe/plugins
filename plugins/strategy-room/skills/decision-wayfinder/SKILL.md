---
name: decision-wayfinder
description: Map a large uncertain effort into its destination, decision map, fog, frontier, and next blocking edge. Use only when the user explicitly asks to wayfind, map an uncertain effort, find the next decision, or determine what must be decided before planning. Keep local-first decision state and resolve one blocking decision per context. Do not use for ordinary planning, task breakdown, or execution.
---

# Decision Wayfinder

Make uncertainty legible without pretending the full route is known. The deliverable is a decision map and the next blocking edge, not a complete project plan.

## Operating contract

- Start from the destination: the observable state that would mean the effort succeeded.
- Read the current local sources before asking for known facts.
- Separate fog, which is not yet understood, from frontier, which is understood enough to decide next.
- Map dependencies between decisions. A blocking edge is a decision whose resolution makes one or more downstream decisions possible.
- Resolve one blocking decision per working context. Do not spread attention across the whole map.
- Keep the map in a local file when the user authorizes file output. External tracker updates require separate authority.
- Stop before execution. Hand accepted decisions to Outcome Engine.

## Workflow

1. State the destination, owner, horizon, evidence of arrival, and explicit exclusions.
2. Inspect the conversation and closest sources. Preserve already-settled decisions.
3. List material decision nodes. Connect each node to prerequisites and downstream choices.
4. Mark each node as `settled`, `frontier`, `fog`, `blocked`, or `deferred`.
5. Identify the frontier decision with the greatest effect on downstream decisions. This is the next blocking edge.
6. Name what evidence or user judgment can resolve it. Recommend a default when evidence supports one.
7. Resolve only that decision, update the map, and recalculate the frontier.
8. Stop when the next blocking edge is named, or continue one edge at a time if the user asks.

## Decision map

Use `assets/decision-map-template.md`. Keep each node compact: stable ID and precise label, status, prerequisites, decisions made possible, owner, evidence source, current options, recommendation, acceptance test, and decision record when settled.

## Completion contract

Return the destination, current fog, frontier, next blocking edge, why it blocks progress, the decision just settled if any, and the recommended next action. The result is complete when another fresh context can locate the map and take up exactly one next decision without rereading the full conversation.

Route a settled destination that needs a brief or action slices to Outcome Engine. Route durable cross-task continuation to Continuity Vault.
