# Practice Compiler

Practice Compiler reads session JSONL as operations data. It stores short redacted evidence snippets and stages proposals. It does not copy transcript dumps, change the host configuration, publish content, or promote knowledge automatically.

```bash
python3 scripts/practice_compiler.py scan
python3 scripts/practice_compiler.py report
python3 scripts/practice_compiler.py decide PROPOSAL_ID approve --note "approved for handoff"
```

On Codex, the default source is `~/.codex/sessions`. Add `--include-claude` to include `~/.claude/projects`, or pass `--sessions-root` once per source root. On Claude Code, use `--include-claude` or pass the exact exported or local session root with `--sessions-root`.

Approved proposals always produce a complete generic handoff. A named companion is only selected when the caller confirms it is available with `--available-owner`. Approval records the requested change and evidence. It does not authorize the receiving change.
