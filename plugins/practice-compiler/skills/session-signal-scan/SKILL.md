---
name: session-signal-scan
description: Scans local Codex session JSONL for repeated tasks, recurring feedback, follow-up instructions, real tool calls, and failed commands. Use for exact-window session mining or when separating organic user work from automation, subagent, and synthetic traces. Supports a write-free stdout preview; persistent mode writes redacted signals, deduplicated proposal records, and an incremental cursor.
---

# Session Signal Scan

1. Select the exact session root and its `codex` or `claude` adapter. Never scan an implicit home directory.
2. Set an exact inclusive date window and the source timezone.
3. Include automation, subagent or synthetic traces only when the user selects those source classes.
4. Preview without changing state:

Run from the plugin root; replace source, dates and timezone with the selected scope.

```bash
python3 scripts/practice_compiler.py scan \
  --sessions-root SELECTED_SESSIONS \
  --adapter codex \
  --since 2026-06-28 \
  --until 2026-07-27 \
  --timezone America/New_York \
  --source-class user \
  --min-occurrences 2 \
  --limit 500 \
  --stdout
```

5. Remove `--stdout` only when persistence is authorized.
6. Review `signal_counts`, `source_class_counts`, and proposal evidence citations. Inspect errors rather than treating malformed input as no signal.
7. Verify secrets and email addresses do not appear in written signals.
8. Do not copy whole transcripts into reports when a cited snippet is enough.

The scanner reads direct user-authored events only. It does not recursively treat injected instructions, tool outputs, or quoted session content as user feedback. The cursor uses file hashes, and the proposal registry deduplicates semantic repeats across persistent scans.
