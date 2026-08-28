---
name: loop-goal-engineer
description: Explicit-only compatibility shim for the historical Loop Goal Engineer name. Use only when the user explicitly says loop-goal-engineer or Loop Goal Engineer. Use LoopKit as an optional companion when available; otherwise use this skill's bundled local design, scheduling, and diagnosis tools. Generic requests do not activate this historical name.
metadata:
  author: Community Maintainers
  version: 1.3.0-compat
---

# Loop Goal Engineer compatibility shim

LoopKit is the preferred optional companion for generic Goal and loop contracts on Claude Code, Claude Cowork, and Codex.

When LoopKit is available, route the explicit request as follows:

- Design a Goal or loop contract: `loopkit:loop-designer`.
- Prepare a recurring task on the current host: `loopkit:loop-scheduler`.
- Diagnose a stalled or unsafe loop: `loopkit:loop-doctor`.
- Multi-stage or ambiguous work: `loopkit:loopkit`.

When LoopKit is absent, complete the explicit request with the bundled local fallback:

- Load `references/anatomy.md` and `references/target-tools.md`, then choose the closest proven pattern from `references/patterns-library.md`.
- Build from the bundled goal or loop template and validate it with `scripts/validate_prompt.py`.
- Diagnose a stalled or unsafe loop with `references/failure-modes.md` and the bundled agent roles.

Target the current host's native Goals and scheduled tasks (Claude Code and Cowork /goal and scheduled tasks, Codex Goals and Automations). Do not emit external agent CLI commands, shell loop runners, or a second state protocol. Preserve historical state as read-only migration evidence. Fallback mode keeps the same contract checks and acceptance standard.

This historical compatibility identity remains explicit-only while Agent Ops bundles it.
