# Practice Compiler

Practice Compiler reads session JSONL as operations data. It stores short redacted evidence snippets and stages proposals. It does not copy transcript dumps, change the host configuration, publish content, or promote knowledge automatically.

```bash
python3 scripts/practice_compiler.py scan
python3 scripts/practice_compiler.py report
python3 scripts/practice_compiler.py decide PROPOSAL_ID approve --note "approved for handoff"
```

Select each source root explicitly with `--sessions-root`; the tool never assumes a host history directory.

Approved proposals always produce a complete generic handoff. A named companion is only selected when the caller confirms it is available with `--available-owner`. Approval records the requested change and evidence. It does not authorize the receiving change.

## Explicit source selection

New scans require `--sessions-root`, `--adapter codex` or `--adapter claude`, and an exact `--since`/`--until` window. The former implicit home-directory selection is removed. For a read-only result use `--stdout`; it writes no cursor, proposal or handoff. Neutral Design exports use `ingest-design-export` with the same time boundary. Approving a proposal creates a bounded handoff, not a destination edit.
