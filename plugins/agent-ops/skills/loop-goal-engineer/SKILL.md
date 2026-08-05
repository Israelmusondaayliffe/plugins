---
name: loop-goal-engineer
description: Explicit-only compatibility shim for the historical Loop Goal Engineer name. Use only when the user explicitly says loop-goal-engineer or Loop Goal Engineer. Redirect loop design, scheduling, and diagnosis, on Claude Code, Claude Cowork, or Codex, to LoopKit. Generic loop, Goal, recurring-task, and schedule requests should trigger LoopKit directly.
metadata:
  author: Community Maintainers
  version: 1.3.0-compat
---

# Loop Goal Engineer compatibility shim

This historical name remains available through Agent Ops 0.3.x. LoopKit now owns generic Goal and loop contracts on Claude Code, Claude Cowork, and Codex.

Route the explicit request as follows:

- Design a Goal or loop contract: `loopkit:loop-designer`.
- Prepare a recurring task on the current host: `loopkit:loop-scheduler`.
- Diagnose a stalled or unsafe loop: `loopkit:loop-doctor`.
- Multi-stage or ambiguous work: `loopkit:loopkit`.

Target the current host's native Goals and scheduled tasks (Claude Code and Cowork /goal and scheduled tasks, Codex Goals and Automations). Do not emit external agent CLI commands, shell loop runners, or a second state protocol. Use the LoopKit contract validator before initialization.

This shim is scheduled for removal in Agent Ops 0.4.0 after LoopKit reaches 0.2.0.
