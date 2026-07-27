# LoopKit

LoopKit is a dual-host plugin for bounded, resumable work on Claude Code, Claude Cowork, and Codex. It separates a loop contract from execution, verification, persistence, scheduling, and diagnosis so each failure has a clear owner.

## What it includes

- `loopkit`: front door and route selector
- `loop-designer`: contract design and validation
- `loop-runner`: bounded execution with receipts
- `loop-verifier`: independent and deterministic completion checks
- `loop-resumer`: checkpoint restoration after interruption or compaction
- `loop-scheduler`: scheduled-task preparation and first-run checks
- `loop-doctor`: diagnosis for repetition, drift, weak verification, and unsafe authority

State is host-scoped. Resolve the host home first (`~/.claude` on Claude Code / Cowork, `${CODEX_HOME:-~/.codex}` on Codex), then store runs under `<host-home>/loopkit/runs/<workspace-hash>/`. LoopKit does not depend on external agent CLIs, MCP servers, or network access.

## Install

On Codex, add the marketplace, then install the plugin:

```bash
codex plugin marketplace add Israelmusondaayliffe/plugins
codex plugin add loopkit@israel-codex-plugins
```

On Claude Code, add this repository as a plugin marketplace (`/plugin marketplace add Israelmusondaayliffe/plugins`), then install `loopkit` from the `/plugin` UI. On Claude Cowork, install from the in-app marketplace or a delivered `.plugin` file.

Review and trust the plugin hooks in `/hooks`. The hooks only refresh or restore a compact checkpoint for an active run in the current workspace.

## Validate

```bash
python3 scripts/verify_bundle.py
python3 -m unittest discover -s tests -v
```

## Safety boundary

Creating or running a loop does not expand the host platform's permissions. Schedules, external messages, destructive actions, production changes, purchases, and privacy-sensitive access still require the authority and approvals of the active task.
