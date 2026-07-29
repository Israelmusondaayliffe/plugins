---
name: gauntlet
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet to orchestrate a mega-project across approved planning, bounded workstreams, fresh critics, durable handoffs, integration, and independent verification. Never use implicitly.
---

# Gauntlet

Operate the full Gauntlet Loop as a durable, bounded state machine.

## Explicit-only contract

This front door runs only when the user explicitly invokes `$gauntlet-loop:gauntlet`. Never infer it from project size, subagent requests, high reasoning effort, model choice, urgency, or the word “gauntlet.”

Continuation in a later session also requires explicit invocation. Do not inject this skill into ordinary prompts.

## Core guarantees

- Explore before planning.
- Obtain user approval before compilation or execution.
- Keep the parent model, reasoning effort, collaboration mode, service tier, and cost controls user-selected.
- Use finite elapsed-time, launch, concurrency, and critic-round limits.
- Isolate or serialize overlapping writes.
- Give critics and final judges fresh context with no inherited turns.
- Separate builders from acceptance and final verdicts.
- Persist decisions, evidence, state, and handoffs after material events.
- Treat technical access as capability, not authority.

## Startup

1. Find the project root and read its closest instructions.
2. Inspect `.gauntlet/state.json` if present.
3. Load `../../references/gauntlet-method.md`, `../../references/state-machine.md`, and the sibling skill file for the required stage.
4. Validate the workspace before resuming an existing project.
5. Record capability drift. Never assume subagents, user-owned task tools, maximum concurrency, or a named effort level exist.

## Stage routing

The front door does not magically call sibling skills. Read the relevant sibling `SKILL.md` completely, then follow it in this task.

| Current condition | Load and follow |
|---|---|
| No workspace, `intake`, `grilling`, or `plan_proposed` | `../gauntlet-plan/SKILL.md` |
| `plan_approved` | `../gauntlet-compile/SKILL.md` |
| `gauntlet_compiled`, `executing`, `integrating`, or repair execution | `../gauntlet-run/SKILL.md` |
| Material event or session boundary | `../gauntlet-handoff/SKILL.md` |
| `ready_for_verification`, `verifying`, or verification retry | `../gauntlet-verify/SKILL.md` |

At any transition, consult `../../references/state-machine.md`.

## Planning gate

The first stage explores, grills ambiguity, writes the plan, and asks for explicit approval. Stop at `plan_proposed`. Only an approval in the current task authorizes transition to `plan_approved`.

## Execution topology

Use bounded subagents inside the current task when available. Fresh critics and judges must be started with no inherited turns, equivalent to `fork_turns: "none"`.

Creating a user-owned Codex task is a different external topology and requires separate explicit authorization. Resuming an old task is not fresh context.

Parallel work requires disjoint write targets or separate worktrees. Otherwise serialize it. The lead owns the dependency graph, integration waves, budget ledger, and state transitions.

## Continuity

Update `.gauntlet/handoff.md` eagerly after decisions, failures, workstream completion, integration, and verification findings. Run the handoff stage before a likely session boundary. Never depend on hidden conversation context for recovery.

## Verification

Execution ends at `ready_for_verification`. Load the verification stage and run a fresh independent panel. Builders cannot issue the final verdict.

Allowed terminal verdicts are `verified`, `verified_with_caveats`, `failed_verification`, and `unable_to_verify`. Every passed criterion needs observable evidence.

## Stop conditions

Stop and record the exact next action when:

- required user approval is missing;
- scope or authority would expand;
- the resource envelope is exhausted;
- safe write isolation is impossible;
- a critical dependency or evidence source is unavailable;
- the project cannot satisfy a material acceptance criterion;
- runtime capabilities materially differ from the compiled plan.

Use `waiting_for_user`, `blocked`, `paused`, or `stopped` as appropriate. Do not conceal an incomplete project behind a completion claim.

## Completion

The full loop completes only when the independent panel has issued an evidence-based verdict, the evidence report and handoff are current, project validation passes, and the user receives exact artifact paths and caveats.
