---
name: gauntlet-compile
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet-compile to compile an approved plan into bounded workstreams, dependency waves, fresh critic contracts, write ownership, and an independent verification panel. Never use implicitly.
---

# Gauntlet Compile

Transform an approved plan into an executable program without starting the work.

## Invocation contract

This skill is explicit-only. Require `.gauntlet/state.json` with state `plan_approved`. Never infer Gauntlet use or approval from complexity, model choice, or prior sessions.

## Load before acting

Read:

- `.gauntlet/project.md`
- `.gauntlet/plan.md`
- `.gauntlet/state.json`
- `.gauntlet/runtime-capabilities.json`
- `../../references/workstream-design.md`
- `../../references/critic-contract.md`
- `../../references/multi-thread-execution.md`
- `../../references/integration-waves.md`
- `../../references/verification-panel.md`
- `../../references/state-machine.md`
- `../../assets/workstream-charter.md`
- `../../assets/critic-report.json`
- `../../schemas/gauntlet.schema.json`

## Preflight

Run:

`python3 ../../scripts/gauntletctl.py validate --project-root <root>`

Stop if the plan is not approved, capabilities are unknown in a consequential way, the resource envelope is missing, or the requested execution exceeds user authority.

## Compile the program

Write `.gauntlet/gauntlet.yaml` as JSON-compatible YAML.

For every workstream define:

- unique ID, objective, owner role, dependencies, and integration wave;
- bounded inputs and outputs;
- exact write targets;
- evidence and acceptance criteria;
- builder charter;
- independent critic charter;
- maximum critic rounds;
- retry, block, and stop rules.

Define a directed acyclic dependency graph. Parallel work is allowed only when write targets are disjoint or isolated in separate worktrees. Otherwise serialize it.

## Agent and task topology

Use subagents for bounded work inside the current task when agent tools are available. A fresh critic must be created with no inherited turns, equivalent to `fork_turns: "none"`.

Do not create user-owned Codex tasks unless the user separately authorizes that external topology change. Do not resume an old task as a substitute for a fresh critic.

Never silently override the parent model, reasoning effort, collaboration mode, service tier, or cost controls. “Highest available” means the highest level already selected and supported by the host.

## Verification panel

Compile at least three independent perspectives:

- acceptance and scope;
- evidence and correctness;
- integration and adversarial failure.

The builder cannot issue the final verdict. Panel members must be fresh and have bounded evidence inputs.

## Output contract

Produce:

- `.gauntlet/gauntlet.yaml`
- `.gauntlet/threads/lead.md`
- `.gauntlet/workstreams/<id>/charter.md`
- `.gauntlet/integration/integration-plan.md`
- `.gauntlet/verification/acceptance-matrix.md`
- updated decisions, risks, assumptions, and progress.

Set program status to `compiled`, increment its version, and transition to `gauntlet_compiled`.

## Completion

Complete only when every deliverable maps to a workstream and acceptance criterion, the graph is executable, write ownership is conflict-free, the finite budget is preserved, the independent panel exists, and strict project validation passes.

If compilation cannot be made safe or complete, transition to `blocked` or `waiting_for_user`, record the missing decision, create a handoff, and stop.
