---
name: gauntlet-plan
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet-plan to plan a mega-project through exploration, structured grilling, finite limits, acceptance criteria, and a user approval gate. Never use implicitly.
---

# Gauntlet Plan

Create an approved, durable project plan before any Gauntlet execution starts.

## Invocation contract

This skill is explicit-only. Never infer it from words such as mega-project, subagents, high effort, or complex work. Do not continue a prior Gauntlet session unless the user explicitly invokes a Gauntlet skill again.

Do not change the parent model, reasoning effort, collaboration mode, service tier, budget, or user-owned task topology. Record the current capability envelope and work within it.

## Required inputs

- The user's requested outcome and constraints.
- The project root.
- Existing project contracts, source files, and relevant evidence.
- Any approvals already granted in the current task.

## Load before acting

Read:

- `../../references/gauntlet-method.md`
- `../../references/grill-me-method.md`
- `../../references/project-constitution.md`
- `../../references/quality-bars.md`
- `../../references/knowledge-work-bars.md`
- `../../references/state-machine.md`
- `../../assets/plan.md`

## Workflow

1. Explore the project and its closest instructions before asking questions.
2. If `.gauntlet/state.json` is absent, initialize the project:

   `python3 ../../scripts/gauntletctl.py init --project-root <root> --name <name> --actor lead-agent`

3. Record observable runtime capabilities:

   `python3 ../../scripts/gauntletctl.py capabilities --project-root <root> ...`

4. Move from `intake` to `grilling`. Use the Grill Me method to expose ambiguity, dependencies, risk, quality standards, and approval boundaries.
5. Draft `.gauntlet/plan.md` from the supplied template. Make scope, exclusions, evidence, acceptance criteria, stop conditions, and a finite resource envelope concrete.
6. Update the project, decisions, assumptions, risks, open questions, source register, and progress files after each material event.
7. Transition to `plan_proposed`.
8. Present the plan and ask for explicit approval. This is a hard stop. Do not compile or execute.
9. After approval, record it and transition to `plan_approved`.
10. Validate the workspace:

   `python3 ../../scripts/gauntletctl.py validate --project-root <root>`

## Resource envelope

Every plan must bound:

- elapsed time;
- total agent launches;
- maximum concurrency;
- maximum critic rounds per workstream;
- extension conditions.

Any extension requires user approval. “No fixed round count” is invalid.

## Output contract

Produce:

- `.gauntlet/project.md`
- `.gauntlet/brief.md`
- `.gauntlet/plan.md`
- `.gauntlet/state.json`
- `.gauntlet/decisions.md`
- `.gauntlet/assumptions.md`
- `.gauntlet/risks.md`
- `.gauntlet/open-questions.md`
- `.gauntlet/source-register.md`
- `.gauntlet/runtime-capabilities.json`

## Authority and prohibitions

You may read, plan, initialize Gauntlet state, and ask decision-critical questions.

You may not begin implementation, issue external messages, create user-owned Codex tasks, change account or permission state, exceed granted scope, or treat technical access as authorization.

## Completion

Complete only when the plan is approved, the state is `plan_approved`, the finite resource envelope is recorded, and project validation passes.

If approval or required evidence is missing, transition to `waiting_for_user` or `blocked`, write the exact next action, create a handoff if the session may end, and stop.
