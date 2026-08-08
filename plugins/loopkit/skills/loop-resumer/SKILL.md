---
name: loop-resumer
description: Resume a nonterminal LoopKit run after interruption, restart, or context compaction by restoring its checkpoint and validating durable state. Use when a user says resume the loop, continue where it stopped, restore the active Goal, pick up after compaction, or recover a blocked or waiting run. Do not infer run state from chat memory.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Resumer

Resume from files, not recollection. The checkpoint is a compact index. The contract, state, events, receipts, and fresh workspace remain authoritative.

## Workflow

1. Use the named run directory. If none is named, resolve the host home first (`~/.claude` on Claude Code / Cowork, `${CODEX_HOME:-~/.codex}` on Codex), then locate the newest active run for the resolved current workspace under `<host-home>/loopkit/runs/<workspace-hash>/`.
2. Read `contract.json`, `state.json`, `checkpoint.md`, and the newest receipt.
3. Confirm the run id matches across files, the status is nonterminal, and the current generation is known.
4. Refresh the checkpoint:

```bash
python3 scripts/checkpoint_run.py RUN_DIR
```

5. Inspect fresh workspace state and determine whether the previous next action is still valid.
6. Route:
   - `waiting_input`: ask only for the missing decision.
   - `blocked`: verify whether the named prerequisite has cleared.
   - `scheduled`: confirm whether this is a scheduled invocation or a manual test.
   - `running`: continue with `loop-runner`.
7. Use a generation-checked transition before changing status.

## Recovery

If files disagree, state is malformed, evidence is missing, or the generation changed while reading, stop normal execution and route to `loop-doctor`. Do not repair by guessing.

## Pre-port runs

Runs created before the dual-host port live under the Codex root (`~/.codex/loopkit/runs/`). They are not migrated. Resume one by naming its run directory explicitly.

Load `references/resume-integrity.md` for the integrity checklist.
