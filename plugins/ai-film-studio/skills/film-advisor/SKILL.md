---
name: film-advisor
description: "Explicit-only front door for a bounded AI film-production workflow."
---

# Film Advisor

Activation: explicit-only. Use this skill only when the user deliberately invokes `$ai-film-studio:film-advisor`, `Use Film Advisor`, `film-advisor`, `/film-advisor`, or `@ai-film-studio/film-advisor`, or when a validated Film Advisor packet carries the same explicit activation evidence.

Do not activate for a quoted name, a negated request, a conditional example, an incidental mention, or ordinary filmmaking language. This skill is separate from Agent Ops Sol Advisor.

## Host-aware runtime

Read `references/film-advisor-topology.json` and inventory the host's available models, effort levels, fresh-task controls, write boundaries, and receipt evidence before choosing a topology.

When the host proves every enhanced-topology requirement, use this bounded topology:

1. One Sol High planner owns the grill, approved production contract, task graph, state, approvals, packetization, integration, and final user response.
2. Fresh, non-forked Terra Max builders perform initial research, writing, planning, prompt construction, and production work in bounded tasks.
3. A fresh, non-forked Sol XHigh auditor is read-only and returns findings only.
4. A different fresh, non-forked Sol XHigh fixer receives accepted findings and exact authorized paths, then performs one bounded repair pass.
5. A third fresh, non-forked Sol XHigh verifier is read-only and checks the repaired artifacts.
6. Serialize overlapping writes. Bind every task to hashed inputs, dependencies, exact paths, expected outputs, evidence, and authority.
7. A failed final verification returns to the Sol High planner for re-planning or user escalation. It never starts an uncontrolled repair loop.

This runtime is independent from Agent Ops Sol Advisor and never invokes it.

If any enhanced-topology requirement is unproved, use the complete local bounded planner:

1. Keep the current task as planner, integrator, approval owner, and final-response owner.
2. Run the bundled `film-wayfinder`, record workflow, production specialists, prompt packet builder, approval gates, and validators in sequence.
3. Separate drafting, audit, one bounded repair pass, and final verification as named phases. Do not claim fresh-task or model independence that the host did not prove.
4. Serialize writes, hash important inputs, cap repair at one pass, and return to planning when verification fails.
5. If the requested result specifically requires independent fresh workers or a named unavailable model, return an unsupported-topology handoff naming the missing capability, completed local work, unresolved proof, and exact next action. Do not stop ordinary local planning merely because the enhanced topology is unavailable.

## Operating contract

1. Read the request as a film-specific production request, not a generic wayfinding request.
2. Confirm the activation evidence. If it is absent, do not claim Film Advisor is active.
3. Classify the request into one route: `concept`, `brief`, `architecture`, `assets`, `performance`, `geography`, `shots`, `adapter`, `iteration`, or `finish`.
4. State the next durable record and the acceptance evidence before drafting it.
5. Stop before any paid generation, sign-in, upload, purchase, destructive replacement, publication, or external delivery unless the user gives separate explicit approval for the exact action and target.

Use [the runtime protocol](../../references/film-advisor-protocol.md) and [approval gates](../../references/approval-gates.md). For machine packets, use `scripts/film_advisor.py`; it returns routing and stop decisions only.

## Output

Return a compact Film Advisor result with:

- explicit activation evidence;
- selected route and owned skill;
- required input record(s);
- requested next artifact or decision;
- stop gate, if any.

Worker, auditor, fixer, and verifier roles do not approve, integrate, or issue the final verdict. The Sol High planner alone integrates verified work and responds to the user. No role may claim a live model action occurred without matching evidence.
