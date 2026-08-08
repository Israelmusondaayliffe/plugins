---
name: loop-scheduler
description: Prepare, activate, observe, pause, or remove a scheduled task (Codex scheduled tasks, or Claude Code scheduled cloud routines via /schedule) for a manually tested LoopKit run. Use when a user asks to schedule this loop, run it every day or week, make the workflow recurring, test an automation, or diagnose a scheduled LoopKit run. Uses the host scheduling surface, not cron or a shell loop.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Scheduler

Use the host scheduling surface as the trigger and LoopKit state as persistence: Codex scheduled tasks on Codex, scheduled cloud routines (`/schedule`) on Claude Code / Cowork. For recurrence inside a live Claude Code session, `/loop` is the lighter tool and does not need this skill. Keep the scheduler simple. It should start the task, not decide whether the result is good.

## Readiness gate

Before activation, require:

- one successful manual execution under the same permissions and tools;
- a self-contained task prompt naming the workspace and run contract;
- cadence and timezone;
- clean no-op behavior when nothing changed;
- evidence to return on meaningful change;
- a stop or pause condition;
- a current Browser or Computer Use capability check when the task needs UI automation.

## Workflow

1. Create a schedule record from `references/schedule-schema.md`.
2. Record it from the plugin root:

```bash
python3 scripts/write_schedule.py RUN_DIR /absolute/path/to/schedule-draft.json
```

3. Use the active scheduling controls for the host (Codex desktop or web scheduled-task controls on Codex, `/schedule` on Claude Code / Cowork) to create the schedule. Do not emulate this with cron, `launchd`, `systemd`, or an endless shell process.
4. Observe the first scheduled execution and inspect its run receipt.
5. Confirm the schedule honors no-op, evidence, permission, and stop behavior.
6. Pause or remove the temporary schedule after verification when it was created only for testing.

## Safety

Scheduling is separate authority. A run that may write externally, send messages, purchase, delete, change production, or access privacy-sensitive data still needs the corresponding approvals. Report when the current surface cannot create or inspect scheduled tasks rather than claiming activation.
