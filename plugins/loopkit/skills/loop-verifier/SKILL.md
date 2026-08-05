---
name: loop-verifier
description: Verify a LoopKit run, artifact, or completion claim against its durable contract and fresh evidence. Use when a user asks is this actually done, verify the loop, review a run receipt, check completion against the spec, or requires independent evidence before a Goal is closed. Do not modify the artifact while acting as verifier.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Verifier

Treat the contract as the finish line and fresh results as evidence. Keep verification separate from repair so the actor does not approve its own narrative.

## Workflow

1. Read `contract.json` without relying on the builder's summary.
2. Inspect the artifact and current workspace state.
3. Run each `evidence.machine_checks` command exactly as recorded when safe and authorized.
4. Evaluate each judgment criterion with file, line, screenshot, or command evidence. For high-impact work, use a fresh review context when available.
5. Build a receipt using `loop-runner/references/receipt-schema.md`.
6. Validate it:

```bash
python3 scripts/validate_receipt.py RUN_DIR /absolute/path/to/receipt.json
```

7. If every required check and criterion passes, record a `completed` receipt. Otherwise record `running`, `blocked`, `waiting_input`, `exhausted`, or `failed` with precise failures and the smallest next action.

## Verifier boundaries

- Do not relax the contract or tests.
- Do not swallow command errors.
- Do not accept a renamed, stubbed, skipped, or deleted check as proof.
- Do not use old output when the workspace may have changed.
- Do not claim independence if no fresh context was available.

Load `references/adversarial-checks.md` when a run looks complete but the evidence is weak.
