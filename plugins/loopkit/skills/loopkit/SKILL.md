---
name: loopkit
description: Route Claude Code, Claude Cowork, or Codex work among bounded loop design, execution, verification, resume, scheduled tasks, and diagnosis. Use when a user says build a loop, run this until done, make this recurring, resume the active run, schedule this task, verify the loop, diagnose repetition, or asks for a durable Plan-Act-Verify workflow with state on disk. Use this front door for multi-stage loop work. Do not use for quick one-shot questions, general agent architecture, or external agent CLI configuration.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# LoopKit

Route a repeatable host-platform workflow to one primary owner. A loop is appropriate only when fresh feedback can change the next action. Keep the contract, state, and evidence on disk so interruption or compaction cannot silently change the finish line.

## Router

1. Classify the request and load only the matching phase agent.
2. Follow the agent's handoff to one owned skill.
3. For an end-to-end request, use this order: design, run, verify, then schedule only if recurrence is requested.

Routes:

- Design a new loop or Goal contract: load `agents/agent-design.md`, then `loop-designer`.
- Execute a ready contract: load `agents/agent-run.md`, then `loop-runner`.
- Verify a run or artifact: load `agents/agent-verify.md`, then `loop-verifier`.
- Resume interrupted work: load `agents/agent-resume.md`, then `loop-resumer`.
- Prepare or operate a scheduled task: load `agents/agent-schedule.md`, then `loop-scheduler`.
- Diagnose drift, repetition, unsafe authority, or false completion: load `agents/agent-diagnose.md`, then `loop-doctor`.

If the user asks for a reusable agent definition or an agent-system audit, use an installed agent-design companion only when the user selected it or its documented handoff applies. When none is available, state that the request is outside LoopKit and continue only with any requested loop work. If the user explicitly names `goal-runner`, `loop-goal-engineer`, or `loopy`, an installed compatibility shim may be used during its transition window.

## Handoff gates

- Run requires a valid `contract.json` and `state.status` of `ready`, `scheduled`, `waiting_input`, or `blocked` with its prerequisite cleared.
- Verify requires an artifact or run directory and the contract that defines completion.
- Resume requires an existing nonterminal run directory.
- Schedule requires one successful manual run and a clear no-op plus stop policy.
- Completion requires a valid receipt with every required machine check passing.

## Shared protocol

Load `references/ownership-and-state.md` when route ownership or on-disk state is unclear. State is host-scoped: resolve the host home first (`~/.claude` on Claude Code / Cowork, `${CODEX_HOME:-~/.codex}` on Codex), then use `<host-home>/loopkit/`. A loop never grants authority beyond the active task's permissions and approvals.

## Failure behavior

Do not invent a success condition, tool, cadence, budget, path, or permission. Ask one focused question only when the missing answer changes safety or the contract materially. Otherwise record the unknown and proceed with the smallest reversible step.
