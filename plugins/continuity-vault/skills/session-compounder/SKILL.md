---
name: session-compounder
description: Inspect completed meeting, interview, workshop, or working-session notes; preserve source authority and reuse permission; recommend worthwhile outputs; and create only the user-selected, permission-safe set. Use when a session should produce durable decisions, follow-ups, knowledge, or derivative outputs rather than only a summary.
---

# Session Compounder

Preserve what happened, then compound only what is worth reusing.

## Inspect

1. Name the session, date, purpose, participants or roles, source location, source completeness, recorded audience, and privacy or attribution limits.
2. Extract four categories without upgrading status:
   - decisions actually made
   - follow-ups actually stated, with an owner or timing only when the source names them
   - durable knowledge such as explanations, methods, stories, and examples
   - derivative outputs, kept separate from faithful extraction because they are newly created material
3. Link every extracted item to its source evidence. Use an exact quote only when the wording is present in the source.
4. Record reuse permission, allowed audience, attribution, and de-identification requirements for every item. Never infer consent, a decision, an owner, a date, or permission from context.

## Permission invariant

An output is creatable only when every contributing item has recorded permission that allows the exact intended audience. `unknown` or `prohibited` permission blocks any output using that item. `restricted` permission allows only an audience explicitly recorded for that item and must preserve every restriction.

When permission is unresolved, add a marked gap naming the affected source item and candidate output. Do not create that output until the gap is resolved. Do not assume an internal audience is allowed, and do not treat de-identification as permission. Apply de-identification only when the source permits it.

## Recommend, select, create

1. Recommend only worthwhile outputs. Rank candidates by value, evidence strength, audience fit, effort, and sensitivity.
2. State why each output is or is not worth creating, then ask the user to select the set. If the current request already names outputs, treat only those outputs as selected, while still stating the recommendation before creation.
3. Create only selected outputs whose permission check passes. Preserve links to the source and label newly proposed material.
4. Use [the Session Compounder template](assets/session-compounder-template.md) as the human-facing selection and provenance record. When a structured record is useful, adapt `assets/output-template.json` and run `scripts/validate_output.py`.

## Ownership and external-action boundaries

- Continuity Vault owns the durable handoff and source-authority record across fresh sessions.
- Decision mapping and practice learning are optional companion handoffs. Use an available, user-selected tool for either role; otherwise keep the source-backed decision or repeated-practice note in the local handoff. An absent companion never blocks the selected session outputs.
- A companion handoff grants no authority to scan other traces, stage a proposal, or edit its destination.
- Do not publish, message participants, share, upload, or write to a connected destination without explicit authority for that action.

## Stop conditions

- Stop the affected output when its provenance, permission, allowed audience, selection, or required attribution is unresolved.
- Keep unsupported owners, dates, consent, decisions, and quotes as marked gaps.
- A recommendation or handoff records evidence. It grants no authority to create another output or change external state.
