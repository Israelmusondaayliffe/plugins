---
name: gauntlet-handoff
description: Loads only when the user explicitly says hand off the gauntlet, resume the gauntlet, or continue the gauntlet in a new session, or when a gauntlet session is ending. Writes the script-generated session handoff from durable state and, on resume, reconstructs the run from disk before routing back into the loop. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Israel Ayliffe
  version: 0.1.0
---

# Gauntlet handoff

Continuity is written from state, not narrated by the outgoing agent (INV-6). A self-authored progress narrative is the same failure mode as self-grading. This skill has two modes: write mode at session exit, read mode at session entry. The full multi-session and multi-thread protocol, including S3 parallel lanes, wave boundaries, and cross-surface moves, is in `references/multi-session.md` in this skill.

## Write mode

Triggered by session exit: wall clock, user stop, wave boundary, or an explicit "hand this off".

Generate the handoff by script, never by hand:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/write_handoff.py --run-dir <path to .gauntlet/runs/<run-id>>
```

It writes `sessions/<n>/HANDOFF.md` from durable state, with these twelve sections, in this order (structure in `assets/handoff-template.md`):

1. Run ID, one-line goal, one-line bar, absolute path to the run directory
2. How to read state: which files, in what order, starting with `CONTEXT.md`
3. Wave and lane status table, generated
4. Converged and verified pieces with consensus values
5. In flight per lane, with the last gap verbatim
6. Capped or blocked, and why
7. Decisions already made that must not be reopened, each with a pointer to where it was recorded
8. Do-not-redo list
9. First three actions for the incoming agent
10. How to verify any statement in this document, with commands
11. Surface notes: platform, model, and effort of this session, what tools it had, what the next agent may lack
12. Budget spent and remaining

Then, and only then, the departing agent may append exactly one section, titled `## Judgment notes (unverified)`. That is the only permitted append. Everything above it came from state; everything inside it is opinion, labeled as such. No edits to the generated sections, no second appended section, no narrative woven into the tables.

Write mode also releases the lane lock and writes the `sessions.json` exit record. If the run is degraded, the banner appears at the top of the handoff; it is not removable.

**Portability rules.** `HANDOFF.md` must be portable: plain markdown, absolute paths, no tool-specific syntax, and no assumption that the next reader is Claude Code or even Claude. A handoff that only makes sense inside the session that wrote it has failed.

## Read mode

Triggered by "resume the gauntlet", a new session on an existing run, or a stale `run.lock`.

1. Read state in exactly this order: `CONTEXT.md`, then the newest `HANDOFF.md`, then `run.json`, `PLAN.md`, `pieces.json`, `lanes.json`.
2. Check `run.lock` for a stale holder before claiming a lane, via `${CLAUDE_PLUGIN_ROOT}/scripts/lock.py` (see its `--help` for the acquire, heartbeat, and stale-check operations; it takes `--run-dir`). A lock is stale when its heartbeat is older than two hours or its holder session is marked exited. Never claim a lane over a live lock.
3. Claim the lane, write the `sessions.json` entry, and restate the contract in one line: the goal, the bar, and the lane being claimed.
4. Route to `gauntlet-run`. Read mode never runs rounds itself.

**Never resume from the handoff alone.** When state files are available, they are the truth and the handoff is a reading aid. If the handoff and the state files disagree, state wins and the discrepancy is surfaced to the user, not silently reconciled. Resuming from a handoff narrative while ignoring `pieces.json` is resuming from someone's opinion.
