# PLUGIN SPEC: gauntlet
## Version 3.0, build-ready

Target: Claude Code (primary), Claude Cowork (packaged secondary).
Author: Community Maintainers.
Method source: Matt Shumer, "How to Run a Gauntlet Loop" (somethingbig.ai, 2026-07-27)
and github.com/mshumer/Claude-of-Duty.

This is a mega-project plugin. It is invoked by name. It assumes high effort settings, real
cost, and work that may span days, sessions, threads, and surfaces. While a run is active it
sits at the top of the stack and supersedes overlapping skills.

Where a section says a script decides something, a model must not decide it. Where a section
names a closed set, no other value is valid.

---

# 1. INVOCATION CONTRACT

**Explicit only. This plugin never loads on its own.**

Every skill description must open with an explicit-invocation clause and must not contain
generic triggers such as improve, review, make this better, plan, research, draft, or write.
Those belong to other skills and must keep working untouched.

Trigger classes, and only these:

```
gauntlet
run the gauntlet
gauntlet loop
gauntlet mode
gauntlet run
the big one
mega project mode
max run
ultracode run
beat this bar
blind critic loop
Claude of Duty method
resume the gauntlet
gauntlet handoff
```

Anti-trigger line, written verbatim into every description in this plugin:

> Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any
> request that does not name the gauntlet.

The front door refuses a soft entry. If someone says "make this really good" without naming
the gauntlet, the plugin does not load. If it is already loaded from an earlier turn, it
states that a gauntlet run is heavy and asks for explicit confirmation before initializing
any state.

---

# 2. SURFACE PRECHECK

Before initializing a run, the front door checks that the surface can actually run a
gauntlet, and records the result in `run.json`.

Capabilities checked:

| Capability | Why it matters |
|---|---|
| Clean-context subagent spawning | Invariants 2 and 4 depend on it. Without it there is no independent judgment |
| Filesystem read and write | The entire state layout, resumability, and evidence trail |
| Command execution | Inspection methods `run`, `test`, `measure`, `screenshot`, `render` |
| Network fetch | Only when the domain needs `source-reach` |

Three outcomes:

| Result | Behavior |
|---|---|
| `full` | Proceed normally |
| `degraded` | Proceed only after naming the missing capability and its cost to the user. Record `"context_isolation": "degraded"` or `"execution": "degraded"` in `run.json`. Every handoff document and every evidence report from this run carries a banner naming the degradation |
| `unsupported` | Refuse to initialize a run. Explain that the method needs an agentic harness. Offer brief-only mode: run `gauntlet-brief` and `gauntlet-prompt`, produce `CONTEXT.md`, `PLAN.md`, `bar/`, and `prompt.md`, and hand the user a prompt to run in Claude Code |

A plain chat surface with no subagents and no filesystem is `unsupported`. Brief-only mode is
the correct answer there. Never simulate a loop.

Degraded mode for subagents means each judge runs as a separate task invocation seeded only
from files on disk, with no shared conversational context. That is weaker than a clean
context window and must be labeled as such everywhere it appears.

---

# 3. THE METHOD AND ITS INVARIANTS

Give a lead agent a goal and a bar it cannot argue with. Let the lead split the goal into the
smallest independently judgeable pieces. Each piece gets a builder and a separate critic with
fresh context. The critic compares the work against the bar, blind where possible, names the
single largest gap, and sends it back. Loop until the work wins or the run is stopped. Verify
with agents that never saw the build. Report with receipts.

```
split -> build -> inspect -> blind judge against the bar -> name one gap -> repeat
                                    |
                              converged or capped
                                    |
                          independent verification
                                    |
                              evidence report
```

Seven invariants. When any design choice conflicts with one, the invariant wins.

**INV-1. The bar is external and inspectable.** A real artifact, source set, test suite,
benchmark, or measurement. Never a rubric the agent authored for itself mid-run. Never prose
adjectives.

**INV-2. The builder never grades itself.** Critics and verifiers run in fresh context with
no builder history, no builder rationale, no builder summary. Enforced by the spawning code
and validated by script, not by asking agents nicely.

**INV-3. Judgment inspects the real thing.** Rendered pixels, a running process, actual test
output, the finished prose read end to end, the actual sources. Never a description written
by whoever made it.

**INV-4. Quality and integrity are judged separately.** A beautiful document that invents a
statistic passes a quality critic and fails the work. Every run has both a quality verifier
and an integrity verifier, with different mandates and different context.

**INV-5. Nothing is done without re-runnable evidence.** Paths, commands, exit codes, hashes,
screenshots, source URLs. Absence of evidence is reported as absence, never as a pass.

**INV-6. Continuity is written from state, not narrated by the outgoing agent.** Handoff
documents are generated by script from durable state. The departing agent may append clearly
labeled judgment notes and nothing more. A self-authored progress narrative is the same
failure mode as self-grading.

**INV-7. Caps pause, they do not certify.** A piece that hits a round cap, a wave cap, a wall
clock, or a cost ceiling is `capped`, never `done`.

---

# 4. DOMAINS AND ADAPTERS

The core loop never changes. What changes per domain is: what a piece is, what the bar looks
like, how the artifact is inspected, whether blind comparison is feasible, and what the
integrity verifier checks.

Those five answers live in `references/domains/<domain>.md`. Load exactly one at a time.
Never inline eight domains into a SKILL.md. A mixed project declares a primary domain plus
per-piece overrides in `pieces.json`.

## 4.1 Summary table

| Domain | Piece is | Bar is | Inspection | Blind | Integrity checks |
|---|---|---|---|---|---|
| `code` | module, system, function cluster | reference implementation, test suite, latency or memory target | `run`, `test`, `measure` | partial, on behavior | no stubs, no dead paths, tests execute, claimed coverage real |
| `visual` | component, section, asset | screenshots of best-in-class work | `screenshot`, `render` | strong | builds and renders at every target viewport, no placeholder assets |
| `prose` | argument, opening, section, paragraph class, transitions | reference paragraphs at target clarity and compression | `read` plus `reader-proxy`, blind prose pairing | strong | claims traced, no invented quotes or sources |
| `research` | question, source set, claim ledger, synthesis | primary-source coverage requirement, claim-to-citation ratio, reference review, disconfirming-evidence quota | `claim-audit`, `source-reach`, `reader-proxy` | partial | sources reachable and saying what is claimed, no fabricated citations, disagreement represented |
| `deck` | narrative arc, individual slide, visual system | reference decks in the category | `render`, `reader-proxy` | strong | no fabricated figures, every number sourced |
| `strategy` | options set, assumption register, recommendation, risks, reversibility | reference decision-memo standard plus adversarial pass | `red-team`, `reader-proxy` | weak, rubric plus red-team | evidence separated from judgment, assumptions labeled with confidence, kill conditions stated |
| `prompt-system` | a mode, a router rule, a template, a description | benchmark set of test inputs with expected behavior | `run` against the set | strong, blind A/B of outputs | triggers as described, does not fabricate tool behavior or templates |
| `brand` | positioning line, identity element, asset class, channel piece | reference identity systems plus the project's hard constraints | `render`, cross-asset consistency | strong | hard constraints hold, including the strictly monochrome personal palette with no chromatic accents |

## 4.2 Adapter file contract

Every `references/domains/<domain>.md` contains exactly these headings:

```
## What counts as a piece
## What a valid bar looks like here
## Three worked bar examples
## Inspection methods, in priority order
## Blind comparison feasibility and how to set it up
## What the integrity verifier checks in this domain
## Common failure modes
## When this domain is the wrong adapter
```

Adding a domain later means adding one file. Nothing in the core changes.

## 4.3 Notes per domain that must appear in the adapter

**code.** Blind comparison works on behavior and output, not on source. Do not ask a critic
to blind-compare two implementations by reading them; ask it to compare what they produce.

**visual.** The bar is screenshots, not descriptions of screenshots. Fetch and store real
reference images in `bar/refs/`. A missing reference file fails bar validation.

**prose.** The reference is a floor for clarity and information density, not a voice to copy.
State this explicitly, because a critic handed reference paragraphs will otherwise push the
work toward pastiche. The gap it names must be about density, argument order, or deletability,
never about sounding more like the reference author.

**research.** The bar has three parts: a coverage requirement (how many primary sources, of
what kind), a citation ratio floor, and a disconfirming-evidence quota. A research gauntlet
without a disconfirming quota converges on a confident, one-sided document.

**deck.** Reader-proxy question set is fixed: what is the ask, what is the evidence, what is
the next step, what would make you say no.

**strategy.** No fair comparator usually exists. Use a rubric frozen at brief time with its
hash recorded, plus an adversarial red-team pass. A rubric edited during a run is an
integrity failure, not a refinement.

**prompt-system.** The benchmark set is built at brief time and frozen. Test inputs must
include success cases, boundary cases, and cases that should produce refusal or no-load.
Blind A/B compares outputs on identical inputs.

**brand.** Hard constraints are non-negotiable and checked by the integrity verifier, not the
quality critic. The monochrome constraint is a pass or fail, never a matter of taste.

---

# 5. MAKING KNOWLEDGE WORK INSPECTABLE

A gauntlet needs something to inspect. Prose, research, and strategy do not compile or
render. Four mechanisms close that gap. Every knowledge-work piece uses at least one, and
`read` alone never qualifies.

## 5.1 Blind prose pairing

The critic receives two passages, ours and the reference, labeled A and B, no provenance. It
reads both fully and picks the one with more information per sentence, cleaner argument
order, and fewer sentences that could be deleted without loss. Then it names the single
largest gap in the loser.

Setup: `blind_pair.py` copies both to neutral paths with neutral filenames and strips
metadata. The critic is told one is a reference and one is a candidate, without which is
which, and is instructed not to seek provenance.

## 5.2 Reader-proxy test

The knowledge-work equivalent of running the code, and the highest-value mechanism in this
plugin. Spawn a fresh subagent, give it the artifact and a target reader profile, nothing
else. Ask it to do the thing the artifact exists to enable.

| Artifact | Reader-proxy task |
|---|---|
| Spec | Build the first component from it. Report every place you had to guess |
| Research brief | Answer the questions the brief was commissioned to answer |
| Decision memo | State the decision, the strongest counter-argument, and what would change it |
| Skill or system prompt | Execute it on three test inputs |
| Deck | State the ask, the evidence, the next step, and what would make you say no |
| Editorial | Say what it argues and why a reader continues past line three |

Every guess, every unanswerable question, every wrong answer is a gap. The reader-proxy
output is stored as inspection evidence and is what the critic and the verifier judge.

Mandatory for `prose`, `research`, `strategy`, `deck`, and `prompt-system` pieces. Question
sets are declared per piece at brief time and frozen with the plan hash, so they cannot be
softened once the answers start coming back wrong.

## 5.3 Claim ledger and source reach

The model produces the ledger. A script validates it. Extraction is judgment, validation is
arithmetic.

Ledger row fields: `claim_text`, `location`, `support_type`, `source`, `supporting_quote`,
`confidence`.

`support_type` closed set: `primary`, `secondary`, `user-supplied`, `own-analysis`,
`unsupported`.

`claim_audit.py` computes: total claims, unsupported count, claim-to-citation ratio, source
reachability per row (HTTP fetch or file existence), duplicate-source concentration, and
quote-presence-in-source where the source is fetchable.

Any `unsupported` row in a factual artifact is an integrity failure, not a style note.

## 5.4 Frozen rubric plus red-team

For pieces that resist pairing. A rubric fixed at brief time, hashed, never edited mid-run,
scored by a fresh critic, plus an adversarial pass that tries to break the recommendation.
`hash_plan.py` records the hash. A mismatch at verification time is an integrity failure with
the same weight as a fabricated citation.

---

# 6. PROJECT SHAPE

Five levels:

```
campaign    the whole run, one goal, one bar family, one run directory
  wave      a pass over the campaign, ends with a merge and a smoothing pass
    lane    a parallel thread or session, owns a disjoint set of artifact paths
      piece   the smallest independently judgeable unit
        round   build, inspect, blind judge, name one gap
```

Execution shape is chosen at brief time and recorded in `run.json`. It can change at a wave
boundary, never mid-wave.

**S1, single session.** Ten pieces or fewer, one wave, one lane. No handoff machinery beyond
a final report. Quick intake is allowed.

**S2, sequential multi-session.** Many pieces, one lane at a time, work spans sessions.
Handoff written at every session exit. Default for most mega projects. Grill intake required.

**S3, parallel lanes.** Pieces partition cleanly by artifact path. Multiple concurrent
sessions or threads, one lane each, lane-level locks, merge and smoothing at wave boundaries.
Grill intake required. `validate_pieces.py` refuses S3 when two lanes claim the same artifact
path. Two lanes writing one file is the fastest way to lose a day of Max-effort compute.

---

# 7. STATE LAYOUT

Everything durable lives on disk in plain files. A run must be resumable by an agent that has
never seen the conversation, on a different surface, possibly a different model.

```
.gauntlet/
  runs/
    <run-id>/                        # YYYYMMDD-HHMM-<slug>
      run.json                       # status, shape, domain, budgets, caps, platform, precheck
      CONTEXT.md                     # canonical, append-only
      PLAN.md                        # current wave plan, pointer to waves/<n>/PLAN.md
      bar/
        bar.md                       # what, why, how to inspect, rubric hash if used
        rubric.md                    # optional, frozen
        refs/                        # real reference artifacts, or fetch_refs.sh
      pieces.json
      lanes.json
      waves/
        <n>/
          PLAN.md
          merge.md
      rounds/
        <piece-id>/
          <nnn>/
            artifact/                # snapshot of our output this round
            inspection/              # screenshots, test output, reader-proxy results
            verdict.json
            gap.md
      claims/
        <piece-id>/ledger.json
        <piece-id>/audit.json
      verification/
        <piece-id>/
          quality-1.json ... quality-N.json
          integrity-1.json ... integrity-N.json
          consensus.json
      sessions/
        sessions.json
        <n>/HANDOFF.md
      cost.json
      run.lock
      workbench.html                 # generated, never hand-authored
      EVIDENCE.md
      EVIDENCE.json
  sealed/
    <run-id>/<piece-id>/<round>/map.json    # blind label mapping, outside runs/
```

`CONTEXT.md` is the one file a new agent reads first. Append-only. Corrections are appended
with a date and a reason, never edited in place.

`sealed/` sits outside `runs/` deliberately. Critic subagents receive paths inside `runs/`
only.

Optional Notion mirror: `CONTEXT.md`, `PLAN.md`, `bar.md`, and `EVIDENCE.md` can be pushed to
a Notion page for cross-surface reading. Treat this as an adapter that degrades silently to
files-only. Notion is never the source of truth.

---

# 8. SCHEMAS

No skill invents a shape. These are the shapes.

## 8.1 Inspection methods, closed set

```
run  test  measure  screenshot  render  reader-proxy  claim-audit  source-reach  red-team  read
```

Rules enforced by `validate_pieces.py`:
- Every piece declares at least one method.
- Every method except `read` and `reader-proxy` declares an `inspection_command`.
- `read` alone is never sufficient. On any knowledge-work piece it must pair with
  `reader-proxy` or `claim-audit`.
- A piece that cannot be inspected by any method in the set is not a valid piece. Split it or
  drop it.

## 8.2 run.json

```json
{
  "run_id": "20260729-1400-akira-editorial",
  "goal_one_line": "Ship AKIRA issue 04 at a clarity level that beats the reference set.",
  "domain_primary": "prose",
  "execution_shape": "S2",
  "status": "running",
  "created": "2026-07-29T14:00:00Z",
  "plan_hash": "sha256:...",
  "precheck": {
    "result": "full",
    "subagents": true,
    "filesystem": true,
    "command_execution": true,
    "network": true
  },
  "context_isolation": "clean",
  "budgets": {
    "rounds_cap_per_piece": 10,
    "wave_cap": 4,
    "wall_clock_hours_per_session": 6,
    "subagent_cap_per_run": 400,
    "cost_ceiling": "user-set"
  },
  "current_wave": 1,
  "stop_reason": null
}
```

`status` closed set: `briefed`, `prompted`, `running`, `paused`, `stopped`, `converged`,
`verifying`, `verified`, `failed`, `unverifiable`, `reported`.

## 8.3 pieces.json

```json
{
  "run_id": "20260729-1400-akira-editorial",
  "plan_hash": "sha256:...",
  "decomposition_owner": "lead-agent",
  "pieces": [{
    "id": "opening-section",
    "name": "Opening section of the editorial",
    "domain": "prose",
    "lane": "a",
    "wave": 1,
    "artifact_paths": ["drafts/akira-issue-04.md#opening"],
    "inspection": [
      {
        "method": "reader-proxy",
        "questions": [
          "What is this piece arguing?",
          "Why would a reader continue past line three?"
        ]
      },
      {
        "method": "claim-audit",
        "inspection_command": "python scripts/claim_audit.py --piece opening-section"
      }
    ],
    "bar_refs": ["bar/refs/reference-openings.md"],
    "blind_feasible": true,
    "acceptance": "Blind critic picks ours over the reference in 2 consecutive rounds, and reader-proxy answers both questions without guessing.",
    "verifiers": {"quality": 3, "integrity": 3},
    "status": "looping",
    "rounds_completed": 3,
    "rounds_cap": 10,
    "consecutive_wins": 0,
    "last_gap": "Second paragraph restates the first at lower density.",
    "no_gain_streak": 1
  }]
}
```

`status` closed set: `pending`, `looping`, `converged`, `capped`, `blocked`, `dropped`.

## 8.4 lanes.json

```json
{
  "shape": "S2",
  "lanes": [{
    "id": "a",
    "owned_pieces": ["opening-section", "argument-spine"],
    "owned_paths": ["drafts/akira-issue-04.md"],
    "lock_holder": "session-3",
    "heartbeat": "2026-07-29T16:12:04Z",
    "status": "active"
  }]
}
```

`validate_pieces.py` rejects any configuration where two lanes share an owned path.

## 8.5 verdict.json

```json
{
  "piece_id": "opening-section",
  "round": 3,
  "blind": true,
  "seed": 918273,
  "winner": "B",
  "winner_is_ours": false,
  "confidence": "high",
  "reasoning": "B carries more argument per sentence and its second paragraph advances rather than restates.",
  "largest_gap": "Second paragraph restates the first at lower density.",
  "gap_is_actionable": true,
  "inspection_evidence": ["rounds/opening-section/003/inspection/reader-proxy.json"],
  "rubric_hash": null,
  "critic_saw_builder_context": false,
  "critic_context_source": "files-only"
}
```

`winner_is_ours` is written by the lead after unsealing, never by the critic.
`critic_saw_builder_context` and `critic_context_source` are asserted by the spawning code,
not self-reported. `round_record.py` rejects any verdict where `critic_saw_builder_context`
is true or `critic_context_source` is anything other than `files-only`. That rejection is the
enforcement layer behind INV-2.

## 8.6 Verifier verdict

```json
{
  "piece_id": "opening-section",
  "verifier_type": "integrity",
  "verifier_index": 2,
  "result": "cannot-verify",
  "criterion_applied": "Every factual claim traced to a reachable source.",
  "evidence_inspected": ["claims/opening-section/ledger.json"],
  "reason": "Two ledger rows cite a URL that returned 404 at verification time.",
  "plan_hash_matched": true
}
```

`verifier_type` closed set: `quality`, `integrity`.
`result` closed set: `pass`, `fail`, `cannot-verify`.

## 8.7 consensus.json

```json
{
  "piece_id": "opening-section",
  "quality_votes": {"pass": 3, "fail": 0, "cannot-verify": 0},
  "integrity_votes": {"pass": 1, "fail": 0, "cannot-verify": 2},
  "consensus": "unverifiable",
  "dissent": ["Verifier 2: two ledger rows cite an unreachable URL."],
  "plan_hash_matched": true,
  "computed_by": "scripts/consensus.py",
  "computed_at": "2026-07-29T18:30:00Z"
}
```

`consensus` closed set: `verified`, `verified-with-dissent`, `failed`, `unverifiable`.

## 8.8 Claim ledger row

```json
{
  "claim_text": "Primary-source coverage rose across the sample.",
  "location": "drafts/akira-issue-04.md:L42",
  "support_type": "primary",
  "source": "sources/ons-2026-report.pdf#p12",
  "supporting_quote": "coverage increased from 41% to 58%",
  "confidence": "high"
}
```

## 8.9 sessions.json

```json
{
  "sessions": [{
    "index": 3,
    "surface": "claude-code",
    "model": "claude-opus-5",
    "effort": "recorded-at-runtime",
    "lane": "a",
    "entered": "2026-07-29T14:00:00Z",
    "exited": "2026-07-29T19:40:00Z",
    "rounds_completed": 11,
    "subagents_spawned": 46,
    "exit_reason": "wall-clock",
    "handoff": "sessions/3/HANDOFF.md"
  }]
}
```

## 8.10 cost.json

```json
{
  "rounds_total": 34,
  "subagents_total": 141,
  "sessions_total": 3,
  "wall_clock_hours": 14.2,
  "cost_spent": 0,
  "tokens": "unknown",
  "notes": "Token counts not exposed by this surface."
}
```

Unknown is written as `unknown`. Never estimated. `cost_spent` is numeric spend in the
user's cost unit, updated by the lead when the surface exposes cost; `check_stops.py`
compares it against `budgets.cost_ceiling` and the cost-ceiling stop only fires when both
are numeric.

---

# 9. SKILLS

Seven skills. Each is a folder: `SKILL.md` for instruction and routing, `references/` for
knowledge, `assets/` for templates. Shared scripts live at plugin root `scripts/` and are
invoked via `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`. Shared agent instruction sets live at
plugin root `agents/`. Descriptions are written in the third person, trigger-dense, with the
anti-trigger line.

## 9.1 `gauntlet` (front door, router)

Routing, first match wins:

| Signal | Route |
|---|---|
| No run directory for this goal | Section 2 precheck, then `gauntlet-brief` |
| Precheck returns `unsupported` | Brief-only mode, then stop |
| Brief exists, no `prompt.md` | `gauntlet-prompt` |
| `prompt.md` exists, status not `running` | `gauntlet-run` |
| "resume", new session, or stale `run.lock` | `gauntlet-handoff` read mode, then `gauntlet-run` |
| Session ending, or "hand this off" | `gauntlet-handoff` write mode |
| Status `stopped` or `converged`, no consensus | `gauntlet-verify` |
| Consensus exists and is `verified` or `verified-with-dissent` | `gauntlet-evidence` |
| Consensus is `failed` or `unverifiable` | `gauntlet-run` with the gaps as new work |
| "is it actually done" | `gauntlet-verify`, never the report first |

Two hard rules. The router may not report completion. The router may not skip verification to
reach the report.

Bundled: `references/routing.md`. Uses `scripts/precheck.py`.

## 9.2 `gauntlet-brief`

### Workflow

**1. Explore before asking.** Read the conversation, the repo or folder, attached references,
Notion, Gmail, and past chats. Never ask for what is already discoverable. State every
inference inline so the user can correct it cheaply.

**2. Choose intake mode.**

- *Quick intake.* S1 runs only. Up to three questions at genuine forks.
- *Grill intake.* Default for S2 and S3, and available on request for S1. A multi-turn
  interview that walks the decision tree until the brief is decision-complete. The ordinary
  ask-sparingly budget does not apply here.

Grill rules:
- One question per turn. Tappable options where the answer is closed, open text where it is
  not.
- Explore before every question, not once at the start.
- Track branches. When an answer opens a dependent decision, record it as open and return to
  it. Do not drop threads.
- Write each answer to `PLAN.md` as it arrives.

**3. Pick the domain adapter.** Load exactly one `references/domains/<domain>.md`. Mixed
projects declare a primary plus per-piece overrides.

**4. Set the bar, then gate it.** `validate_bar.py` fails the bar when:
- no file, command, source set, or measurement backs it
- it is only adjectives
- it references an artifact this run will produce
- the inspection method is missing
- a rubric is present without a frozen hash
- a reference file path does not resolve

A failed bar blocks the stage.

**5. Completeness gate.** `brief_complete.py` blocks until every field is present and
non-empty:

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

Missing fields become questions, one at a time, until the gate passes.

**6. Size and shape.** Estimate piece count, waves, and expected rounds. Pick S1, S2, or S3.
Write caps and budgets into `run.json`.

**7. First-pass decomposition, marked provisional.** Set
`"decomposition_owner": "lead-agent"`. The plugin proposes pieces. The lead agent during the
run is expected to re-split.

**8. Emit and hash.** Write `CONTEXT.md`, `PLAN.md`, `bar/`, `pieces.json`, `lanes.json`,
`run.json`. Run `hash_plan.py` to record the success-criteria and rubric hashes. Status
becomes `briefed`.

### CONTEXT.md and PLAN.md are different documents

- `CONTEXT.md` is append-only and permanent. What the project is, what the bar is, what was
  decided and when. Every session reads it first.
- `PLAN.md` is the wave plan. Success criteria, execution shape, decomposition, budgets, what
  each wave attempts. Versioned per wave at `waves/<n>/PLAN.md`, with the root copy pointing
  at the current wave.

Success criteria live in `PLAN.md` and are copied verbatim into each piece's `acceptance`.
`gauntlet-verify` reads criteria from `PLAN.md`, never from later state. A hash mismatch at
verification time is an integrity failure.

Bundled: `references/choosing-a-bar.md`, `assets/context-template.md`,
`assets/plan-template.md`. Uses root `references/domains/*.md` and scripts
`validate_bar.py`, `brief_complete.py`, `init_run.py`, `hash_plan.py`, `validate_pieces.py`.

## 9.3 `gauntlet-prompt`

The design rule that decides whether this plugin works: **the output prompt is short.**
Prescribing architecture replaces the model's judgment with yours. Enforce it with a linter.

`lint_prompt.py` fails the prompt when it:
- exceeds 600 words, warns above 400
- prescribes architecture, file layout, module lists, or a tech stack the user did not specify
- fixes a round count
- omits any required clause below
- omits the effort and subagent instruction
- for knowledge-work domains, omits the reader-proxy and claim-ledger requirements

Required clauses:

```
the goal
the bar, with real paths
split into the smallest independently judgeable pieces
builder plus separate critic with fresh context
blind comparison where possible
loop until it wins or the user stops
maintain the live progress page
write state to the named run directory
use subagents and the highest effort setting
```

Output goes to `prompt.md` and is surfaced to the user in one fenced code block containing
nothing but the prompt.

Platform facts verified 2026-07-29: the Claude Code effort ladder is
`low / medium / high / xhigh / max`; `ultracode` is the current multi-agent opt-in token;
the built-in `/loop` surface exists for interval pacing, but `gauntlet-run` owns gauntlet
iteration because the round loop is a deterministic state machine.

Bundled: `assets/prompt-template.md`, `references/prompt-antipatterns.md`. Uses
`scripts/lint_prompt.py`.

## 9.4 `gauntlet-run`

### Round algorithm

```
1. Read state from disk. Acquire the lane lock via lock.py. Select eligible pieces
   (status = looping, under caps, in the current wave, owned by this lane).

2. For each eligible piece, up to the concurrency cap:

   a. Spawn BUILDER, fresh context.
      Given: goal, bar refs, the piece definition, current artifact, last gap.md.
      Not given: earlier critic reasoning, other pieces, its own prior rationale.

   b. Builder edits the real artifact. Lead snapshots to rounds/<piece>/<n>/artifact/.

   c. Lead runs the declared inspection methods. For knowledge work this includes the
      reader-proxy subagent and, where declared, the claim ledger plus claim_audit.py.
      Output to rounds/<piece>/<n>/inspection/.
      If inspection fails or produces nothing, the round FAILS. Record the failure, send it
      back to the builder, do not proceed to judgment. Never judge a broken or un-inspected
      artifact.

   d. blind_pair.py produces neutral A and B plus a sealed map outside runs/.

   e. Spawn CRITIC, fresh context.
      Given: goal, bar description, the two neutral inspection outputs, the acceptance
      criterion.
      Not given: which is ours, builder history, prior verdicts, other pieces.

   f. Critic returns verdict plus exactly one largest gap, phrased so a builder can act on it.
      round_record.py validates the verdict and rejects it if the fresh-context assertions
      fail.

   g. Ours lost: write gap.md, increment round, loop.
      Ours won: increment consecutive_wins. Two consecutive wins converges the piece.

3. Wave boundary: merge lanes, run the SMOOTHER, write waves/<n>/merge.md.

4. Regenerate workbench.html by script from state.

5. Run check_stops.py. Heartbeat the lock. If a stop fired, set status and, for session-level
   stops, route to gauntlet-handoff write mode.
```

### Resume behavior

Reconstruct from disk only. Never from conversation memory. If disk and context disagree,
disk wins and the discrepancy is surfaced to the user rather than silently reconciled.

Bundled: `references/parallelism-and-locks.md`, `references/reader-proxy.md`. Uses root
`agents/*.md`, `references/domains/*.md`, and scripts `blind_pair.py`, `round_record.py`,
`render_workbench.py`, `check_stops.py`, `claim_audit.py`, `lock.py`.

## 9.5 `gauntlet-verify`

### Rules

- **Two verifier types, always both.** Quality verifiers judge the artifact against the bar
  and the acceptance criterion. Integrity verifiers judge whether the artifact is honest and
  functional.
- **N per type, default 3, minimum 2.** Odd numbers preferred.
- Each verifier receives: the goal from `CONTEXT.md`, the success criteria from `PLAN.md`,
  the bar, the acceptance criterion, the artifact, and the inspection output. Nothing else.
  No round history, no critic verdicts, no builder notes, no other verifier's result.
- Verifiers may run in parallel but must not share context.
- `cannot-verify` is a first-class outcome and must survive into the report. Missing
  inspection output, unreachable source, absent artifact, moved rubric, or a plan hash
  mismatch all produce it.
- Every verifier checks `plan_hash_matched` before anything else. A mismatch is reported and
  the result is `cannot-verify` regardless of what the artifact looks like.

### Integrity verifier mandate

Claims traced to reachable sources that say what is claimed. Commands ran and tests executed.
Stated constraints hold. Rubric and success criteria unmoved. No stubs, no dead paths, no
placeholder assets. Existence of files is not evidence of work. A plausible summary is not
evidence of anything.

### Consensus, computed by `consensus.py`, never by a model

| Condition | Consensus |
|---|---|
| All pass, both types | `verified` |
| Majority pass with dissent, no integrity fail, no cannot-verify | `verified-with-dissent`, dissent preserved verbatim |
| Any integrity fail | `failed`, regardless of quality votes |
| Any `cannot-verify` | `unverifiable` |
| Majority quality fail | `failed`, gaps unioned |

`failed` or `unverifiable` routes back to `gauntlet-run` with the gaps as new work. Never
forward to the report.

Bundled: `references/verification-independence.md`. Uses root `agents/quality-verifier.md`,
`agents/integrity-verifier.md`, and scripts `consensus.py`, `claim_audit.py`.

## 9.6 `gauntlet-evidence`

Fixed section order in `EVIDENCE.md`:

1. **Verdict.** One line, the consensus value verbatim. No softening, no upgrading. Degraded
   mode banner here if applicable.
2. **Goal and bar.** What was asked, what it was measured against, why that bar is fair. Plan
   hash and whether it matched.
3. **Per-piece table.** Piece, rounds, final blind result, quality votes, integrity votes,
   consensus, artifact path.
4. **Re-run the checks.** Every inspection command with its exit code, copy-pasteable.
5. **Claim audit summary.** Claim count, unsupported count, citation ratio, unreachable
   sources, per knowledge-work piece.
6. **Artifact integrity.** SHA-256 of every artifact file at report time.
7. **What was not verified.** Mandatory, never omitted. Every `cannot-verify`, every capped
   piece, every skipped inspection, every part of the goal that never became a piece.
8. **Known remaining gaps.** The last `gap.md` of every non-converged piece, verbatim.
9. **Budget spent.** Rounds, subagents, sessions, wall clock, cost ledger, stop reason.

Hard constraint: every number, path, command, and hash is read from a file in `.gauntlet/`.
This skill may not compute, estimate, recall, or infer any of them. A missing value prints
`not recorded`, and every `not recorded` is itself listed in section 7.

`EVIDENCE.json` carries the same content machine-readably.

Bundled: `assets/evidence-report-template.md`. Uses scripts `hash_artifacts.py`,
`build_report.py`.

## 9.7 `gauntlet-handoff`

### Write mode

`write_handoff.py` generates `sessions/<n>/HANDOFF.md` from state. Required sections, in
order:

1. Run ID, one-line goal, one-line bar, absolute path to the run directory
2. How to read state: which files, in what order, starting with `CONTEXT.md`
3. Wave and lane status table, generated
4. Converged and verified pieces with consensus values
5. In flight per lane, with the last gap verbatim
6. Capped or blocked, and why
7. Decisions already made that must not be reopened, each with a pointer to where it was
   recorded
8. Do-not-redo list
9. First three actions for the incoming agent
10. How to verify any statement in this document, with commands
11. Surface notes: platform, model, and effort of this session, what tools it had, what the
    next agent may lack
12. Budget spent and remaining

Then, and only then, the departing agent may append one section titled
`## Judgment notes (unverified)`. Everything above it came from state. Everything inside it is
opinion, labeled as such.

`HANDOFF.md` must be portable: plain markdown, absolute paths, no tool-specific syntax, no
assumption that the next reader is Claude Code or even Claude.

### Read mode

Read `CONTEXT.md`, then the newest `HANDOFF.md`, then `run.json`, `PLAN.md`, `pieces.json`,
`lanes.json`. Check `run.lock` for a stale holder and a dead heartbeat before claiming a lane.
Restate the contract in one line, name the lane being claimed, then route to `gauntlet-run`.

Never resume from a handoff document alone when state files are available. The document is a
reading aid. State is the truth.

Bundled: `assets/handoff-template.md`, `references/multi-session.md`. Uses scripts
`write_handoff.py`, `lock.py`.

---

# 10. MULTI-SESSION AND MULTI-THREAD PROTOCOL

**Session entry.** Read mode of `gauntlet-handoff`. Check the lock. A lock is stale when its
heartbeat is older than two hours or its holder session is marked exited. Claim the lane,
write a `sessions.json` entry, restate the contract in one line.

**During a session.** Heartbeat the lock every round. Write state after every round, not at
the end. A session that dies mid-wave must lose at most one round of work.

**Session exit.** Triggered by wall clock, user stop, wave boundary, or explicit request.
Release the lock, write the `sessions.json` exit record, generate `HANDOFF.md`.

**Parallel lanes, S3 only.** Each lane holds its own lock. Lanes own disjoint artifact paths,
validated at brief time. A lane may not touch a path it does not own, including to read-and-
rewrite. Cross-lane changes wait for the wave boundary merge.

**Wave boundary.** All lanes stop. Merge. Run the smoother across the whole artifact. Write
`waves/<n>/merge.md`. Re-validate `pieces.json`. Only then does the next wave open.

**Cross-surface handoff.** A run started in Claude Code can continue in Cowork or elsewhere
if the run directory is reachable. The incoming surface runs the section 2 precheck and
records its own result. If it comes back weaker than the previous session's, the run
continues in degraded mode with the banner, or waits. It never silently proceeds at lower
isolation.

---

# 11. CROSS-CUTTING MECHANICS

## 11.1 Subagents per platform

**Claude Code.** Builder, critic, reader-proxy, quality verifier, integrity verifier, and
smoother are defined as plugin-level agent instruction sets in root `agents/`, each spawned
with its own clean context window.

**Cowork.** Confirm the subagent surface at runtime via precheck rather than assuming parity.
If clean-context isolation is unavailable, run the documented degraded mode: each judge is a
separate task invocation seeded only from disk, `run.json` records
`"context_isolation": "degraded"`, and every handoff and report from that run carries a
banner. Never claim isolation the platform did not provide.

## 11.2 Blind mechanics

`blind_pair.py` seeds an RNG and records the seed, assigns labels, copies both artifacts to
neutral paths with neutral filenames, strips metadata, and writes the map to
`.gauntlet/sealed/`, outside anything the critic is given.

Enforcement is structural plus instructional. It is strong, not airtight: a determined agent
could infer provenance from residual signals. State that honestly in
`references/verification-independence.md` rather than overclaiming.

Where blind comparison is impossible, set `"blind": false` and use the frozen rubric. Never
fabricate a blind comparison.

## 11.3 Smoother

Runs at wave boundaries. Fresh context. Sees the whole artifact and the goal, not piece
history. Mandate is narrow: resolve conflicts between independently improved pieces and make
the result feel like one thing. It may not redesign or add. Its changes are recorded as a
round of type `smooth` so they appear in the evidence trail.

## 11.4 Stop conditions

First to fire wins. Evaluated by `check_stops.py`.

| Condition | Default | Result |
|---|---|---|
| User stop | any time | `stopped`, state intact, resumable |
| Piece converged | 2 consecutive blind wins | piece `converged` |
| All pieces converged | | run `converged` |
| Round cap per piece | 10 | piece `capped`, gap preserved |
| No-gain rule | same largest gap twice with no A/B movement | escalate to lead for re-split, stop looping this piece |
| Wave cap | 4 | `paused` at wave boundary |
| Wall clock | 6h per session | `paused`, handoff written |
| Subagent cap | 400 per run | `paused` |
| Cost ceiling | user-set at brief | `paused` |

All caps are user-overridable at brief time. Caps pause and preserve. They never certify.

## 11.5 Cost ledger

`cost.json` records rounds, subagents spawned, sessions, wall clock per session, and token
counts where the surface exposes them. Unknown is written as `unknown`, never estimated.

## 11.6 Live progress

`workbench.html` is regenerated by `render_workbench.py` from state after every round. No
agent hand-authors it. It shows: run status, per-lane and per-piece tables, the last three
gaps, latest inspection thumbnails or excerpts, budget spent, and the current stop-condition
distances. Openable from a phone.

---

# 12. SCRIPTS

Exactness lives in code. Judgment lives in the model. Python 3, `--help` on every script,
machine-readable output, non-zero exit on failure, no network unless the job requires it.

| Script | Skill | Job |
|---|---|---|
| `precheck.py` | front door | Detect subagents, filesystem, execution, network. Return `full`, `degraded`, or `unsupported` |
| `init_run.py` | brief | Create the run directory, IDs, `run.json` |
| `validate_bar.py` | brief | Fail soft, self-referential, unresolvable, or unhashed-rubric bars |
| `brief_complete.py` | brief | Block until every required brief field is present |
| `hash_plan.py` | brief, verify | Hash success criteria and rubric, compare at verification |
| `validate_pieces.py` | brief, run | Enforce the inspection closed set, reject unjudgeable pieces and overlapping lane paths |
| `lint_prompt.py` | prompt | Length, required clauses, no-prescription enforcement |
| `blind_pair.py` | run | Seeded blind labeling, metadata strip, sealed map |
| `round_record.py` | run | Atomic round append, reject verdicts failing fresh-context assertions |
| `claim_audit.py` | run, verify | Ledger validation, source reachability, citation ratio, quote presence |
| `render_workbench.py` | run | Regenerate the live page from state |
| `check_stops.py` | run | Evaluate every stop condition, return the trigger |
| `lock.py` | run, handoff | Acquire, heartbeat, detect and reclaim stale lane locks |
| `consensus.py` | verify | Compute consensus with no model judgment |
| `hash_artifacts.py` | evidence | SHA-256 every artifact file |
| `build_report.py` | evidence | Assemble the report, fail loudly on missing values |
| `write_handoff.py` | handoff | Generate `HANDOFF.md` from state |

Every value in an evidence report and every value in a handoff document passes through a
script. Nothing important is narrated.

---

# 13. AGENT INSTRUCTION SETS

Six files at plugin root `agents/`. Short, imperative, with the blindness constraint stated in
the first three lines.

**builder.md**

> Build or fix one piece. You will be judged by someone who has not seen your reasoning, so do
> not write explanations for the judge. Change the real artifact, not a copy or a summary.
> Close the stated gap and nothing else. Scope creep is a failure even when the extra work is
> good. If the gap cannot be closed without touching something you do not own, say so and
> stop.

**critic.md**

> You are comparing two artifacts. One is a reference, one is a candidate. You are not told
> which, and you must not try to find out. Inspect both directly and fully. Pick the better
> one, say why in one paragraph, then name the single largest gap in the loser, phrased so a
> builder can act on it tomorrow. One gap, not a list. Grade the output, not the effort behind
> it. For prose, the reference is a floor for clarity and information density, not a voice to
> copy: never name a gap that amounts to sounding more like the reference author.

**reader-proxy.md**

> You are the intended reader. You have the artifact and nothing else. Do the task the artifact
> exists to enable. Report every place you had to guess, every question you could not answer,
> and every instruction you could not follow. The guesses are the finding. Do not be
> charitable, do not fill gaps from your own knowledge, and do not assume the author meant
> something reasonable.

**quality-verifier.md**

> You did not build this. Compare it against the stated acceptance criterion using the
> evidence provided. Return pass, fail, or cannot-verify. If you could not actually inspect
> the thing, return cannot-verify. Check the plan hash first: if it does not match, return
> cannot-verify regardless of how the artifact looks.

**integrity-verifier.md**

> You are not judging quality. Check whether this artifact is honest and functional. Trace
> every factual claim to its source and confirm the source says it. Check that commands ran
> and tests executed. Check that stated constraints hold. Check that the rubric and success
> criteria were not moved. Existence of files is not evidence of work. A plausible summary is
> not evidence of anything. Return pass, fail, or cannot-verify, and name the specific row,
> line, or command behind your result.

**smoother.md**

> Make separately improved pieces feel like one artifact. Fix conflicts and inconsistencies in
> voice, structure, naming, and visual system. Do not redesign, do not add, do not touch what
> is already coherent. Record what you changed and why in one paragraph per change.

---

# 14. EVALS

Grade against explicit assertions, not impressions.

| Case | Passes when |
|---|---|
| "make this really good", gauntlet not named | plugin does not load |
| Gauntlet named on a surface with no subagents | precheck returns `unsupported`, brief-only mode offered, no loop simulated |
| Soft bar submitted | brief blocks and asks for a concrete comparator |
| Reference path does not resolve | bar validation fails, run does not start |
| Brief missing `out_of_scope` | completeness gate blocks, asks one question |
| S3 requested with two lanes on one file | `validate_pieces.py` refuses S3 at brief time |
| Piece declares `read` only, prose domain | `validate_pieces.py` rejects the piece |
| Over-specified goal | generated prompt drops the architecture, stays under 400 words |
| Builder writes a flattering summary | summary never reaches the critic |
| Critic asked which artifact is ours | no path to the sealed map exists in its inputs |
| Verdict arrives with `critic_context_source` not `files-only` | `round_record.py` rejects it |
| Inspection command fails mid-round | round marked failed, no verdict produced |
| Reader-proxy cannot answer two of five questions | those become gaps, piece does not converge |
| Research artifact with one invented citation | integrity verifier fails, consensus is `failed`, quality votes do not rescue it |
| Rubric or success criteria edited mid-run | hash mismatch, consensus is `failed` or `cannot-verify` |
| Two verifiers pass, one `cannot-verify` | consensus is `unverifiable`, report says so |
| Report requested before verification | router refuses, routes to verify |
| Session killed mid-wave, new session, no chat history | resumes from disk, no invented rounds, lane lock reclaimed |
| Handoff written by an agent that adds its own progress narrative | narrative is confined to the labeled judgment section, generated sections unaffected |
| All pieces capped without converging | verdict is not "done" |
| Evidence report with a missing state value | prints `not recorded` and lists it in section 7 |

A mega-project plugin that produces a confident completion report from a capped, unverified,
or hallucinating run is worse than no plugin at all.
