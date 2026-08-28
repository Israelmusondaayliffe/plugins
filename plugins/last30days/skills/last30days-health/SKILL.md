---
name: last30days-health
description: Diagnose and repair the last30days runtime, permissions, credentials, source coverage, and post-run failures. Use when setup is incomplete, Python is too old, a source is missing, browser-cookie access is requested, or research returned partial coverage.
---

# Last30days Health

Set `SKILL_DIR` to the directory containing this file. The plugin runner is at `$SKILL_DIR/../../scripts/run_last30days.sh`.

## Read-only checks

Run the narrowest applicable check:

```bash
bash "$SKILL_DIR/../../scripts/run_last30days.sh" --preflight
bash "$SKILL_DIR/../../scripts/run_last30days.sh" --diagnose
bash "$SKILL_DIR/../../scripts/run_last30days.sh" doctor
bash "$SKILL_DIR/../../scripts/run_last30days.sh" doctor --postmortem
bash "$SKILL_DIR/../../scripts/run_last30days.sh" doctor --probe
```

Use `--preflight` for planned access and writes, `--diagnose` for machine-readable availability, plain `doctor` for current health, `doctor --postmortem` after a weak run, and `doctor --probe` for bounded live checks of free sources.

## Repair workflow

1. Read `../last30days/SKILL.md` completely before setup or credential work.
2. State which source or runtime is broken and what evidence supports that diagnosis.
3. Prefer the least invasive fix. The bundled runner selects Python 3.12+ and the existing `uv` runtime when available.
4. Before setup that reads browser cookies, ask for explicit consent. Before installing optional tools or writing credentials, describe the commands and destinations.
5. Re-run the exact failed check and report the four-state source result: working, turned on but unverified, not working, or could be on.

Never echo raw credentials. A configured source is not proven healthy until the doctor output or a real research run verifies it.
