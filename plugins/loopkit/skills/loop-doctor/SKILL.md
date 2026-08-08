---
name: loop-doctor
description: Diagnose and repair LoopKit loops that repeat, stall, drift, overrun limits, lose state, fail verification, misuse scheduling, or claim completion without evidence. Use when a user says the loop is stuck, keeps doing the same thing, wastes tokens, forgot progress, passed bad output, schedule drifted, or asks for a LoopKit audit. Preserve the intended outcome and change only material defects.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Doctor

Identify the failing layer before changing the prompt. Contract, execution, verification, state, hooks, and scheduling have different remedies.

## Workflow

1. Read the run's contract, state, events, checkpoint, receipts, and schedule record when present.
2. Run the structural doctor:

```bash
python3 scripts/doctor_run.py RUN_DIR
```

3. Classify findings:
   - Contract: finish line, boundaries, caps, or stops are missing or unverifiable.
   - Execution: actions are too broad, stale, unsafe, or unrelated to the highest-value failure.
   - Verification: checks are weak, self-approved, skipped, stale, or misleading.
   - State: generations conflict, receipts are missing, or progress was not serialized.
   - Hooks: checkpoint refresh or restore is absent, noisy, oversized, or untrusted.
   - Scheduler: the task was not manually tested, has no no-op behavior, or runs on the wrong cadence.
4. Rank findings by severity and evidence.
5. Propose the smallest repair that preserves the intended outcome.
6. Re-run the failing validation and one bounded cycle before declaring the repair effective.

## Failure patterns

Load `references/failure-modes.md` when evidence suggests confident garbage, context loss, repetition, permission drift, or scheduler drift.

Do not rewrite a sound loop for style. Do not change the goal, authority, or limits without user approval.
