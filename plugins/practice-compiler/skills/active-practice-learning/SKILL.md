---
name: active-practice-learning
description: Compile bounded Codex or Claude Code traces and optional neutral Design exports into deduplicated, redacted, proposal-only workflow improvements. Use when the user asks the harness to learn from completed work, recurring friction, repeated repairs, missed tools, cost decisions, or a reusable method. Never scans passively or applies a proposal.
---

# Active Practice Learning

Practice Compiler owns the learning workflow when selected for this task. Other tools may provide user-selected evidence or receive an approved handoff. No companion plugin is required.

## Required source boundary

Choose one exact source and one inclusive time window. Never scan browser history, desktop history, unrelated folders, or all host data by default.

Run these commands from the plugin root.

```bash
python3 scripts/practice_compiler.py scan --adapter codex --sessions-root SELECTED_CODEX_SESSIONS --since YYYY-MM-DD --until YYYY-MM-DD --source-class user --stdout
python3 scripts/practice_compiler.py scan --adapter claude --sessions-root SELECTED_CLAUDE_PROJECTS --since YYYY-MM-DD --until YYYY-MM-DD --source-class user --stdout
python3 scripts/practice_compiler.py ingest-design-export --input REDACTED_EXPORT.json --since YYYY-MM-DD --until YYYY-MM-DD --stdout
```

`--sessions-root` is required and must name the exact directory selected for this scan. Remove `--stdout` only when persistence is authorized.

## What to keep

Keep recurring friction, repeated repair, wasted work, missed-tool opportunities, cost decisions, and reusable user-supplied methods. Redact secrets, email addresses, and paths. Require repeated evidence by default. Design exports must use opaque project IDs and stable fingerprints. When the same lesson appears in a raw trace and a Design export, keep the raw trace as the evidence source and do not count the export again.

Every result is a proposal. Approval may create a handoff record, but it never authorizes a plugin edit, host change, memory write, repository action, Notion action, or external service call.
