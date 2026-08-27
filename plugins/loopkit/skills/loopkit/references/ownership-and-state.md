# Ownership and state

## Ownership

- LoopKit owns generic loop and goal contracts (Codex Goals or Claude Code `/goal`), execution, receipts, resume, scheduling, and runtime diagnosis on Claude Code, Claude Cowork, and Codex.
- Optional agent-design companions remain responsible for their own reusable-agent contracts and routing.
- General idea-to-result workflows remain outside LoopKit when no feedback loop is needed.
- Optional learning protocols remain outside LoopKit and require explicit selection.

## State lookup

Resolve the state root in this order:

1. `LOOPKIT_STATE_ROOT` for tests or an explicit isolated run.
2. Otherwise resolve the host home first (`~/.claude` on Claude Code / Cowork, `${CODEX_HOME:-~/.codex}` on Codex), then use `<host-home>/loopkit`.

Each workspace uses a 12-character hash of its resolved path. Every run contains a contract, current state, append-only events, compact checkpoint, and evidence directory.

## Authority

LoopKit records authority but does not create it. Scheduled tasks, external messages, destructive actions, privacy-sensitive access, purchases, and production changes remain separately approval-gated.
