---
name: gauntlet-handoff
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet-handoff to create and validate a continuity package preserving state, evidence, decisions, failures, exact next actions, and resume boundaries. Never use implicitly.
---

# Gauntlet Handoff

Write a durable continuity package that another agent can execute without hidden context.

## Invocation contract

This skill is explicit-only. Require an active `.gauntlet` workspace. A handoff does not authorize continuation, execution, external actions, or a new user-owned task. The next session must explicitly invoke a Gauntlet skill.

## Load before acting

Read:

- `.gauntlet/project.md`
- `.gauntlet/state.json`
- `.gauntlet/plan.md`
- `.gauntlet/gauntlet.yaml`
- `.gauntlet/decisions.md`
- `.gauntlet/assumptions.md`
- `.gauntlet/risks.md`
- `.gauntlet/open-questions.md`
- `.gauntlet/progress.md`
- `../../references/session-handoffs.md`
- `../../references/state-machine.md`
- `../../assets/handoff.md`

Read current workstream, integration, critic, source, artifact, and verification records when they exist.

## When to update

Update the canonical handoff after every material event:

- approval or decision;
- state transition;
- completed or failed workstream;
- integration wave;
- newly discovered risk or blocker;
- verification finding;
- likely compaction or session boundary.

Do not rely on a last-minute pre-compaction update.

## Create the handoff

Run:

`python3 ../../scripts/gauntletctl.py handoff --project-root <root> --actor <actor> --objective <objective> --completed <work> --next-action <action> ...`

Supply exact artifact and evidence paths. Name failures, unresolved critic findings, blocked workstreams, and decisions awaiting approval. Separate observed facts from assumptions.

The command updates `.gauntlet/handoff.md` and adds an immutable session record under `.gauntlet/sessions/`.

## Validate

Run:

`python3 ../../scripts/gauntletctl.py validate-handoff --project-root <root>`

Then conduct a fresh-context comprehension check when agent tools are available:

1. Start one bounded reader with no inherited turns, equivalent to `fork_turns: "none"`.
2. Give it only the project root and instruct it to read `.gauntlet/project.md` and `.gauntlet/handoff.md`.
3. Ask it to state the objective, current state, completed work, unresolved risks, exact next action, forbidden redo, and forbidden assumptions.
4. Repair discrepancies and rerun validation.

Do not let the reader edit files or continue the project.

## Output contract

The handoff must contain all 25 template sections, including:

- approved plan and current state;
- completed work and changed artifacts;
- evidence and known weaknesses;
- decisions, assumptions, risks, and open findings;
- workstream, source, and integration status;
- exact next actions and commands;
- first files to read;
- work not to redo;
- assumptions not to make;
- user instructions and provenance.

## Completion

Complete only when structural validation passes and the handoff lets a fresh reader recover the project accurately.

If required state is missing or contradictory, record the contradiction, transition to `blocked` when authorized, and stop. Never invent continuity.
