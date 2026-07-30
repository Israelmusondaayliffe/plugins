---
name: gauntlet-brief
description: Loads only when the user explicitly starts a gauntlet run, says grill me for the gauntlet, or asks to set the bar for a gauntlet. Runs the gauntlet intake interview, sets and validates the external bar, gates brief completeness, sizes the run, and emits the hashed run state that every later gauntlet stage depends on. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Israel Ayliffe
  version: 0.1.0
---

# Gauntlet brief

Turn a goal into a decision-complete, script-validated run definition. The brief is finished when the bar passes `validate_bar.py`, the eleven fields pass `brief_complete.py`, the pieces pass `validate_pieces.py`, and the plan hash is recorded. A run that starts on a soft brief burns Max-effort compute against a target that moves.

## Workflow

### 1. Explore before asking

Read the conversation, the repo or folder, attached references, Notion, Gmail, and past chats. Never ask for what is already discoverable. State every inference inline so the user can correct it cheaply.

### 2. Choose intake mode

- **Quick intake.** S1 runs only. Up to three questions at genuine forks.
- **Grill intake.** Default for S2 and S3, and available on request for S1. A multi-turn interview that walks the decision tree until the brief is decision-complete. The ordinary ask-sparingly budget does not apply here.

Grill rules:

- One question per turn. Tappable options where the answer is closed, open text where it is not.
- Explore before every question, not once at the start.
- Track branches. When an answer opens a dependent decision, record it as open and return to it. Do not drop threads.
- Write each answer to `PLAN.md` as it arrives.

### 3. Pick the domain adapter

Load exactly one `${CLAUDE_PLUGIN_ROOT}/references/domains/<domain>.md`. The closed set of domains: `code`, `visual`, `prose`, `research`, `deck`, `strategy`, `prompt-system`, `brand`. Never load more than one at a time and never inline adapter content that belongs in the file. A mixed project declares a primary domain plus per-piece overrides in `pieces.json`.

The adapter answers five things for this run: what a piece is, what the bar looks like, how the artifact is inspected, whether blind comparison is feasible, and what the integrity verifier checks.

### 4. Set the bar, then gate it

The bar is external and inspectable (INV-1): a real artifact, source set, test suite, benchmark, or measurement. Write it to `bar/bar.md` with what it is, why it is fair, how to inspect against it, and the rubric hash if a rubric is used. Real reference artifacts go in `bar/refs/`.

Then run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_bar.py --run-dir <path to .gauntlet/runs/<run-id>>
```

`validate_bar.py` fails the bar when:

- no file, command, source set, or measurement backs it
- it is only adjectives
- it references an artifact this run will produce
- the inspection method is missing
- a rubric is present without a frozen hash
- a reference file path does not resolve

A failed bar blocks the stage. Fix the bar or interview for a better one; never proceed past a failed bar. See `references/choosing-a-bar.md` in this skill for how to turn soft bars concrete.

### 5. Completeness gate

Run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brief_complete.py --run-dir <path to .gauntlet/runs/<run-id>>
```

It blocks until every field is present and non-empty:

```
goal_one_line
success_criteria           # 3 to 7, each independently checkable
bar_definition             # backed by a file, command, source set, or measurement
bar_rationale              # why this comparator is fair
done_means                 # blind win | measured threshold | user judgment
domain_primary             # plus per-piece overrides
execution_shape            # S1 | S2 | S3
budget_ceiling             # rounds, wall clock, cost, or all three
out_of_scope               # what this run will not attempt
non_negotiables            # hard constraints, brand rules, forbidden approaches
inspection_feasibility     # per proposed piece, one method from the closed set
```

Missing fields become questions, one at a time, until the gate passes. The script decides completeness, not the model.

### 6. Size and shape

Estimate piece count, waves, and expected rounds, then pick one execution shape:

- **S1, single session.** Ten pieces or fewer, one wave, one lane. No handoff machinery beyond a final report. Quick intake is allowed.
- **S2, sequential multi-session.** Many pieces, one lane at a time, work spans sessions. Handoff written at every session exit. Default for most mega projects. Grill intake required.
- **S3, parallel lanes.** Pieces partition cleanly by artifact path. Multiple concurrent sessions or threads, one lane each, lane-level locks, merge and smoothing at wave boundaries. Grill intake required. `validate_pieces.py` refuses S3 when two lanes claim the same artifact path.

The shape and all caps and budgets (rounds cap per piece, wave cap, wall clock per session, subagent cap, cost ceiling) are recorded in `run.json`. The shape can change at a wave boundary, never mid-wave.

### 7. First-pass decomposition, marked provisional

Propose pieces with id, name, domain, lane, wave, artifact paths, inspection methods from the closed set, bar refs, blind feasibility, acceptance criterion, and verifier counts. Set `"decomposition_owner": "lead-agent"` in `pieces.json`. The plugin proposes pieces; the lead agent during the run is expected to re-split. Success criteria are copied verbatim from `PLAN.md` into each piece's `acceptance`.

### 8. Emit and hash

- Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_run.py` to create the run directory, run ID (`YYYYMMDD-HHMM-<slug>`), and `run.json`, recording the front door's precheck result. If the run directory was already initialized earlier in intake so grill answers had a home, update it rather than creating a second one.
- Write `CONTEXT.md` from `assets/context-template.md` and `PLAN.md` from `assets/plan-template.md` (both bundled in this skill). Write `bar/`, `pieces.json`, `lanes.json`.
- Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hash_plan.py --run-dir <run-dir>` to record the success-criteria and rubric hashes.
- Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_pieces.py --run-dir <run-dir>` to enforce the inspection closed set, reject unjudgeable pieces, and reject overlapping lane paths.
- Set `status` to `briefed`.

## CONTEXT.md and PLAN.md are different documents

- `CONTEXT.md` is append-only and permanent. What the project is, what the bar is, what was decided and when. Every session reads it first. Corrections are appended with a date and a reason, never edited in place.
- `PLAN.md` is the wave plan. Success criteria, execution shape, decomposition, budgets, what each wave attempts. Versioned per wave at `waves/<n>/PLAN.md`, with the root copy pointing at the current wave.

Success criteria live in `PLAN.md` and are copied verbatim into each piece's `acceptance`. `gauntlet-verify` reads criteria from `PLAN.md`, never from later state. A hash mismatch at verification time is an integrity failure.
