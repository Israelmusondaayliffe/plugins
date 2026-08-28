# Scan phase

## Scope

Read session JSONL and stage redacted evidence. Do not edit harness, skill, content, or configuration files.

## Workflow

1. Confirm source roots. Add Claude roots only after explicit opt-in.
2. Run `python3 scripts/practice_compiler.py scan` from the plugin root.
3. Inspect scan counts, skipped hashes, and redaction behavior.
4. Treat malformed lines as recorded errors, not empty evidence.

## Output

Return the scan ID, signal count, proposal count, skipped files, and error count. Hand review back to the front door.
