---
name: harness-builder
description: Apply an approved Harness Engineering operations plan to local Claude Code, Cowork connected-folder, or Codex files with dry-run, hash preconditions, backups, atomic writes, receipts, and rollback. Use when a user approves a harness plan, asks to create the workspace and instruction files, fill approved harness gaps, or execute a defined batch of local configuration changes.
---

# Harness Builder

Apply only the approved operation groups. Do not reinterpret the plan during execution.

## Start gate

1. Validate the operations plan.
2. Run dry-run and review the receipt.
3. Confirm approved groups and allowed roots. On Cowork, allowed roots must resolve inside a connected folder, and every applied change must be committed back to the user's device before it counts as landed.
4. Re-read current hashes. Stop on drift.

## Apply

Use:

```text
python3 ../../scripts/harnessctl.py apply PLAN.json --mode dry-run --receipt DRY.json
python3 ../../scripts/harnessctl.py apply PLAN.json --mode apply --approved GROUP --backup-dir BACKUPS --receipt APPLY.json --manifest MANIFEST.json
```

Run one approval group at a time. Preserve unrelated files. If reality invalidates the plan, log the deviation and return to planning.

For task-start capability changes, apply one reversible wave at a time. Stop on the first route, behavior, parity, discovery, or unexpected-manifest regression. Re-run the accepted behavior suite after every change that affects default context, not only after `AGENTS.md` edits.

## Rollback

Use `python3 ../../scripts/harnessctl.py rollback MANIFEST.json --receipt ROLLBACK.json`. Verify restored hashes before reporting recovery. On Cowork, roll back on the device copy too, not only the staged copy.
