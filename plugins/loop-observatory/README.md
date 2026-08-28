# Loop Observatory

Loop Observatory is the read-only measurement layer for bounded agent loops. It ingests LoopKit runs and explicitly registered Operating Graph run roots, then produces comparable JSON and Markdown evidence.

It tracks machine completion, human acceptance, iteration count, duration, stop and escalation reasons, and cost or token data when those fields exist. Missing evidence remains unknown. It never edits source runs or repairs loops itself.

## Commands

```bash
python3 scripts/loop_observatory.py register-root /absolute/graph/run/root
python3 scripts/loop_observatory.py ingest
python3 scripts/loop_observatory.py report
python3 scripts/loop_observatory.py audit
python3 scripts/loop_observatory.py repair-handoff RECORD_ID
```

Use `CODEX_HOME` to test against an isolated state directory.

The repair handoff is local and read-only. It records the source run, normalized evidence, disagreement, owner class, requested outcome, and missing proof. Named repair plugins are optional destinations. When none is installed, return the generic handoff without claiming a repair occurred.
