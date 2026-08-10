---
name: gauntlet-run
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet-run to execute an approved compiled program through bounded builder-critic workstreams, integration waves, durable state, and evidence capture. Never use implicitly.
---

# Gauntlet Run

Execute the compiled program without relaxing its authority, evidence, or resource boundaries.

## Invocation contract

This skill is explicit-only. Require `.gauntlet/state.json` in `gauntlet_compiled`, `executing`, `integrating`, or a repairable post-verification state. Require a compiled `.gauntlet/gauntlet.yaml`.

Do not silently change the parent model, reasoning effort, collaboration mode, service tier, cost controls, or user-owned task topology.

## Load before acting

Read:

- `.gauntlet/project.md`
- `.gauntlet/plan.md`
- `.gauntlet/gauntlet.yaml`
- `.gauntlet/state.json`
- `.gauntlet/handoff.md`
- `.gauntlet/runtime-capabilities.json`
- `../../references/multi-thread-execution.md`
- `../../references/critic-contract.md`
- `../../references/integration-waves.md`
- `../../references/session-handoffs.md`
- `../../references/state-machine.md`

Read each active workstream charter and its dependencies.

## Preflight

Run project validation. Confirm:

- current authorization covers the actions;
- the resource envelope has capacity;
- dependencies are satisfied;
- write targets are disjoint, worktree-isolated, or serialized;
- acceptance and evidence contracts are testable;
- agent tools actually available match the compiled assumptions.

If capability drift changes the safe topology, stop and recompile or ask the user. Do not improvise a broader program.

## Execute workstreams

1. Transition to `executing`.
2. Dispatch only dependency-ready workstreams.
3. Give each builder the bounded charter, allowed inputs, write targets, tests, evidence requirements, and stop conditions.
4. Group completed low-risk workstreams into one integration wave. Start one fresh critic with no inherited turns, equivalent to `fork_turns: "none"`, for the integrated wave. Use an individual critic only for high-risk or independently consequential work.
5. Give the critic the approved goals, integrated outputs, tests, and evidence, not builder discussions.
6. Accept, revise, block, or fail according to the critic contract. One critic launch may produce the required schema reports for several covered low-risk workstreams.
7. Enforce the total run budget and the compiled critic limits.
8. Persist target-state changes, unresolved count, primary artifacts, support-artifact count, failures, and the canonical handoff after every material event.

Critic reports must cover every compiled workstream criterion and point only to existing inspectable evidence files. A nonempty evidence string is not evidence.

After agent launches, critic rounds, target changes, support-artifact changes, concurrency changes, or meaningful elapsed time, update the resource ledger:

`python3 ../../scripts/gauntletctl.py usage --project-root <root> --elapsed-minutes <n> --agent-launches <n> --peak-concurrency <n> --target-changes <n> --support-artifacts <n>`

Progress means integrated deliverable delta. New reports, receipts, tests, or critic packets do not count as progress. Stop and re-plan when support artifacts grow while target changes or unresolved-work reduction stays flat.

The lead agent owns orchestration and integration. A builder never issues its own acceptance verdict.

## Optional Sol Advisor composition

Use the Sol Advisor adapter only after both Gauntlet and Sol Advisor were explicitly invoked and the composition preconditions pass. Read ../../references/sol-advisor-composition.md before compiling a packet. Gauntlet remains the sole state, budget, approval, integration, final-answer, and terminal-verdict owner. The adapter may create bounded workstream packets. Only as a delegated Gauntlet operation, it registers validated return evidence in existing Gauntlet-owned records using an in-process rollback transaction. This operation is not crash-atomic across files. Its receipt is non-authoritative.

A fresh Sol XHigh reviewer is a workstream critic only. It cannot build, repair, write, or replace the three-perspective verification panel.

## Integrate in waves

When a dependency wave completes:

1. transition to `integrating`;
2. inspect cross-workstream consistency;
3. run checks only on changed or affected surfaces;
4. record contradictions and provenance;
5. repair within the approved plan and remaining budget;
6. return to `executing` for the next wave.

Do not merge incompatible claims silently. Preserve competing evidence until resolved.

## Boundaries

- External messages, uploads, purchases, permission changes, and destructive actions require the authority defined by the parent task.
- Creating a user-owned Codex task requires separate explicit authorization.
- Resource-envelope extension requires user approval.
- Stop when an acceptance criterion is impossible, evidence is unavailable, authorization is missing, or the budget is exhausted.

## Output contract

Maintain:

- `.gauntlet/workstreams/<id>/current-state.md`
- builder artifacts and test evidence;
- fresh critic reports;
- `.gauntlet/progress.md`
- `.gauntlet/artifact-register.md`
- `.gauntlet/source-register.md`
- integration reports and contradiction register;
- `.gauntlet/handoff.md`

When all workstreams and integration waves satisfy their gates, transition to `ready_for_verification`. Do not issue a final verdict.

## Completion

Complete only when execution and integration are finished within the approved scope and budget, required work is resolved, evidence is indexed, non-required issues are explicit, validation passes, and the state is `ready_for_verification`. Required unresolved work fails completion.
