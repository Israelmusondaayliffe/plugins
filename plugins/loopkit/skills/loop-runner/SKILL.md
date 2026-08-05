---
name: loop-runner
description: Execute an initialized LoopKit run through bounded observe, choose, act, verify, and record iterations. Use when a user says run this loop, continue until the contract is satisfied, execute the ready Goal, or carry a durable run to a named terminal state. Requires a valid LoopKit run directory. Do not use to design agents or create an untested schedule.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Runner

Execute one bounded action per iteration and write evidence before reporting progress. For sustained work, create or use the host's goal surface (a Codex Goal, or Claude Code `/goal`) so the run has a visible thread-level outcome. The goal surface does not replace LoopKit's durable state.

## Start gate

1. Read `contract.json`, `state.json`, and `checkpoint.md` from the run directory.
2. Confirm the contract still matches the user's request and authority.
3. Read fresh workspace state. Preserve unrelated changes.
4. Start `ready`, `scheduled`, `waiting_input`, or `blocked` work with an allowed generation-checked transition:

```bash
python3 scripts/transition_run.py RUN_DIR running --expected-generation N --reason "Prerequisites confirmed"
```

## Iteration

1. Observe fresh state and the last receipt.
2. Choose the highest-value in-scope action that can create measurable progress.
3. Act once. Keep the change reversible when possible.
4. Run every relevant check under current conditions.
5. Create a receipt using `references/receipt-schema.md`.
6. Validate and record it atomically:

```bash
python3 scripts/validate_receipt.py RUN_DIR /absolute/path/to/receipt.json
python3 scripts/record_receipt.py RUN_DIR /absolute/path/to/receipt.json --expected-generation N
```

7. Re-read `state.json`. Repeat only if the status is `running`, progress remains measurable, and the caps remain.

## Stops

- `completed`: all required checks pass and judgment criteria are verified.
- `waiting_input`: the next safe action needs a user decision.
- `blocked`: a named external prerequisite is unavailable.
- `exhausted`: the iteration or no-progress cap is reached.
- `failed`: the contract or state is invalid and cannot be repaired in scope.
- `cancelled`: the user stops the run.

Do not convert a failed, blocked, or exhausted run into success. Do not widen paths, permissions, external actions, or the goal during execution.

## Handoff

Send completion candidates to `loop-verifier`. Use `loop-resumer` after interruption and `loop-doctor` after repetition, drift, or inconsistent evidence.
