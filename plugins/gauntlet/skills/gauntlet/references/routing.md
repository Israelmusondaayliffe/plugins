# Gauntlet routing reference

The router reads durable state from disk and dispatches to exactly one stage skill. First match wins. The router never does stage work and never reports completion.

## Locating an existing run directory

Before routing, determine whether a run already exists for this goal:

1. Search `.gauntlet/runs/` under the current project root (the working directory, or the git repository root if inside a repo).
2. If nothing is found there, search `.gauntlet/runs/` under the workspace root (`~/Claude Code/`).
3. Run IDs follow `YYYYMMDD-HHMM-<slug>`. Match the slug and the `goal_one_line` in each candidate's `run.json` against the user's stated goal.
4. One clear match: use it. Multiple plausible matches: list them with run ID, goal, and status, and ask the user which one. Zero matches: this is a new run, route to precheck then `gauntlet-brief`.

Never guess between candidate runs, and never create a second run directory for a goal that already has one unless the user explicitly asks for a fresh run.

Once a run directory is selected, read `run.json` first, then `pieces.json`, then check for `prompt.md`, `run.lock`, and `verification/*/consensus.json`. Those five inputs decide every row below.

## The routing table, row by row

| Signal | Route | Why |
|---|---|---|
| No run directory for this goal | Surface precheck, then `gauntlet-brief` | Nothing exists yet. The precheck runs first because an `unsupported` surface must not initialize loop state at all, and a `degraded` one must be disclosed before the user commits budget. |
| Precheck returns `unsupported` | Brief-only mode, then stop | The surface cannot host the loop (no subagents, no filesystem, or no execution). Run `gauntlet-brief` and `gauntlet-prompt` only, produce `CONTEXT.md`, `PLAN.md`, `bar/`, and `prompt.md`, hand the user the prompt to run in Claude Code, and stop. Never simulate a loop. |
| Brief exists, no `prompt.md` | `gauntlet-prompt` | The run is briefed (`status: briefed`) but no launch prompt has been generated and linted. The prompt stage must pass `lint_prompt.py` before anything runs. |
| `prompt.md` exists, status not `running` | `gauntlet-run` | Brief and prompt are done; the loop has not started or is between states. `gauntlet-run` reads state from disk and begins or continues rounds. |
| "resume", new session, or stale `run.lock` | `gauntlet-handoff` read mode, then `gauntlet-run` | A fresh session must reconstruct from disk, never from conversation memory. Read mode reads `CONTEXT.md`, the newest `HANDOFF.md`, then `run.json`, `PLAN.md`, `pieces.json`, `lanes.json`, checks the lock for a stale holder (heartbeat older than two hours, or holder session marked exited), claims the lane, then hands control to `gauntlet-run`. |
| Session ending, or "hand this off" | `gauntlet-handoff` write mode | Exit requires a script-generated handoff (`write_handoff.py`), a `sessions.json` exit record, and lock release. The outgoing agent may append only the labeled judgment-notes section. |
| Status `stopped` or `converged`, no consensus | `gauntlet-verify` | The loop has ended but nothing has been independently verified. Convergence is a critic outcome, not a verdict. Verification spawns fresh quality and integrity verifiers that never saw the build. |
| Consensus exists and is `verified` or `verified-with-dissent` | `gauntlet-evidence` | Only now may a report exist. The evidence skill reads every number, path, command, and hash from files in `.gauntlet/`; it computes nothing and recalls nothing. |
| Consensus is `failed` or `unverifiable` | `gauntlet-run` with the gaps as new work | A failed or unverifiable consensus routes back to the loop, never forward to the report. The verifier gaps become the new work items. |
| "is it actually done" | `gauntlet-verify`, never the report first | A doneness question is a verification request. Answering it from run state or from memory would be self-grading at the run level. |

## Hard rules restated

- The router may not report completion. If asked "is it done", route to `gauntlet-verify`. If verification has already produced `verified` or `verified-with-dissent`, route to `gauntlet-evidence` and let the report speak.
- The router may not skip verification to reach the report. There is no path from `running`, `stopped`, `converged`, or `paused` directly to `gauntlet-evidence`, and a run whose pieces are capped without consensus does not reach the report either.

## Degraded behavior

`precheck.py` returned `degraded` (typically: subagents exist but clean-context isolation cannot be confirmed, or command execution is limited).

- Proceed only after naming the missing capability and its concrete cost to the user, and getting their go-ahead.
- Record the degradation in `run.json`: `"context_isolation": "degraded"` or `"execution": "degraded"`.
- Degraded context isolation means each judge runs as a separate task invocation seeded only from files on disk, with no shared conversational context. That is weaker than a clean context window. Never claim isolation the platform did not provide.
- Every handoff document and every evidence report from a degraded run carries a banner naming the degradation. The banner is not optional and not removable when the report looks good.
- On cross-surface resume, the incoming surface runs its own precheck and records its own result. If it comes back weaker than the previous session's, the run continues in degraded mode with the banner, or waits. It never silently proceeds at lower isolation.

## Unsupported behavior

`precheck.py` returned `unsupported` (no clean-context subagents and no filesystem, or no way to execute inspection at all). A plain chat surface is the canonical case.

- Refuse to initialize a run. Explain that the method needs an agentic harness: independent judgment requires spawning fresh-context critics, and resumability requires durable files.
- Offer brief-only mode: run `gauntlet-brief` and `gauntlet-prompt`, produce `CONTEXT.md`, `PLAN.md`, `bar/`, and `prompt.md`, and hand the user a single fenced prompt to run in Claude Code.
- Never simulate a loop. No narrated rounds, no imaginary critics, no "as a critic I would say" stand-ins. A simulated gauntlet is self-grading wearing a costume, and it is the exact failure the method exists to prevent.
