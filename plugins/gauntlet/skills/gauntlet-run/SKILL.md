---
name: gauntlet-run
description: Loads only when a gauntlet prompt and bar exist and the user explicitly says run the gauntlet, gauntlet run, gauntlet loop, or resume the gauntlet. Executes the gauntlet round loop as a deterministic state machine over disk state, spawning fresh-context builders and blind critics, running declared inspections, and writing every round durably before the next begins. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Israel Ayliffe
  version: 0.1.0
---

# Gauntlet run

Execute the round loop. Preconditions: a run directory exists, `prompt.md` exists, and the bar passed validation at brief time. This skill is the loop's owner; it is a deterministic state machine driven from disk state, and the built-in `/loop` surface never replaces it (at most `/loop` re-invokes this skill for session pacing across long unattended stretches).

The lead agent (you) orchestrates. Builders build, critics judge, scripts decide. Where a step below names a script, the script's output is binding; a model may not override it.

## Round algorithm

Follow this structure exactly, every round.

### 1. Read state and acquire the lock

Read state from disk: `run.json`, `pieces.json`, `lanes.json`, the current wave's `PLAN.md`. Acquire the lane lock:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lock.py --run-dir <path to .gauntlet/runs/<run-id>> acquire --lane <lane>
```

Select eligible pieces: status `looping`, under caps, in the current wave, owned by this lane. Lock rules and lane ownership are detailed in `references/parallelism-and-locks.md` in this skill; read it before running any S3 shape.

### 2. For each eligible piece, up to the concurrency cap

**a. Spawn the BUILDER, fresh context**, using the instruction set at `${CLAUDE_PLUGIN_ROOT}/agents/builder.md`.

- Given: the goal, the bar refs, the piece definition, the current artifact, the last `gap.md`.
- Not given: earlier critic reasoning, other pieces, its own prior rationale.

**b. Snapshot.** The builder edits the real artifact. The lead snapshots it to `rounds/<piece>/<n>/artifact/`.

**c. Run the declared inspection methods.** The lead runs every method the piece declares in `pieces.json`, and only methods from the closed set. For knowledge work this includes spawning the reader-proxy subagent from `${CLAUDE_PLUGIN_ROOT}/agents/reader-proxy.md` against the piece's frozen question set (mechanism in `references/reader-proxy.md` in this skill) and, where declared, producing the claim ledger and validating it:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/claim_audit.py --run-dir <run-dir> --piece <piece-id>
```

All inspection output goes to `rounds/<piece>/<n>/inspection/`. For every
`inspection_command` executed, append a row `{"command": <exact command string>,
"exit_code": <int>, "ran_at": <ISO timestamp>}` to
`rounds/<piece>/<n>/inspection/results.json` (a JSON list). `build_report.py` reads exit
codes for the evidence report only from these recorded rows; an unrecorded command prints
`not recorded` in the report and is flagged in its section 7.

**If inspection fails or produces nothing, the round FAILS.** Record the failure, send it back to the builder as the gap, and do not proceed to judgment. Never judge a broken or un-inspected artifact. A crashed build, a failed render, an empty reader-proxy report, or a claim audit that could not run all mean no critic is spawned this round.

**d. Blind pairing.** Run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/blind_pair.py --run-dir <run-dir> --piece <piece-id> --round <n>
```

It produces neutral A and B copies plus a sealed label map written outside `runs/`, at `<run-dir>/../../sealed/<run-id>/<piece-id>/<round>/map.json`. The critic is never given any path into `sealed/`. Where the piece has `blind_feasible` false, skip pairing, set `"blind": false`, and judge against the frozen rubric; never fabricate a blind comparison.

**e. Spawn the CRITIC, fresh context**, using the instruction set at `${CLAUDE_PLUGIN_ROOT}/agents/critic.md`.

- Given: the goal, the bar description, the two neutral inspection outputs, the acceptance criterion.
- Not given: which is ours, builder history, prior verdicts, other pieces.

**f. Validate the verdict.** The critic returns a verdict plus exactly one largest gap, phrased so a builder can act on it. Record it:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/round_record.py --run-dir <run-dir> --piece <piece-id> --round <n>
```

`round_record.py` appends the round atomically and rejects any verdict where `critic_saw_builder_context` is true or `critic_context_source` is anything other than `files-only`. Those fields are asserted by you as the spawning code, never self-reported by the critic. A rejected verdict is a failed round: fix the spawning, re-run the round, and never hand-edit a verdict to pass. The lead unseals the map and writes `winner_is_ours` after validation; the critic never writes it.

**g. Win and loss handling.**

- Ours lost: write the gap to `rounds/<piece>/<n>/gap.md`, reset `consecutive_wins` to 0, increment the round counter, loop.
- Ours won: increment `consecutive_wins`. Two consecutive wins converges the piece: set its status to `converged` and stop looping it.

### 3. Wave boundary

When every piece in the wave is `converged`, `capped`, or `blocked`: all lanes stop, lanes merge, and you spawn the SMOOTHER, fresh context, from `${CLAUDE_PLUGIN_ROOT}/agents/smoother.md`. It sees the whole artifact and the goal, not piece history. It resolves conflicts between independently improved pieces and may not redesign or add. Record its changes as a round of type `smooth` so they appear in the evidence trail, and write `waves/<n>/merge.md`. Full boundary protocol in `references/parallelism-and-locks.md`.

### 4. Regenerate the live page

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_workbench.py --run-dir <run-dir>
```

After every round, by script, from state. No agent hand-authors `workbench.html`.

### 5. Stops and heartbeat

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_stops.py --run-dir <run-dir>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lock.py --run-dir <run-dir> heartbeat --lane <lane>
```

`check_stops.py` evaluates every stop condition; first to fire wins. If a stop fired, set the status it names and, for session-level stops (wall clock, subagent cap, cost ceiling, user stop at session end), route to `gauntlet-handoff` write mode. Caps pause, they never certify: a capped piece is `capped`, not `done`.

## Write state after every round

Write all state (`pieces.json`, `run.json`, round records, `cost.json`) after every round, not at the end of a session. A session that dies mid-wave must lose at most one round of work.

## Resume behavior

Reconstruct from disk only. Never from conversation memory, never from a summary of what happened earlier in this thread. If disk and context disagree, disk wins, and the discrepancy is surfaced to the user rather than silently reconciled. On any resume signal (new session, "continue the run", stale `run.lock`), go through `gauntlet-handoff` read mode first: read `CONTEXT.md`, the newest `HANDOFF.md`, then `run.json`, `PLAN.md`, `pieces.json`, `lanes.json`, check the lock for staleness, claim the lane, then re-enter the round algorithm at step 1.
