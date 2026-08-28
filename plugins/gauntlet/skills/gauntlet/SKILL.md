---
name: gauntlet
description: "Loads only when the user explicitly invokes the gauntlet by name with one of these trigger phrases: gauntlet, run the gauntlet, gauntlet loop, gauntlet mode, gauntlet run, the big one, mega project mode, max run, ultracode run, beat this bar, blind critic loop, Claude of Duty method, resume the gauntlet, gauntlet handoff. It is the front door and router for the gauntlet mega-project method. It prechecks the surface and routes to the brief, prompt, run, verify, evidence, and handoff stages. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet."
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Gauntlet front door and router

This skill is the only entry point to the gauntlet method. It decides which stage runs next. It never does stage work itself, and it never declares work done.

## Invocation contract

Explicit only. Refuse soft entry. If the user says "make this really good", "push this to the limit", or anything else that does not name the gauntlet, do not proceed and do not initialize any state. Point out that the gauntlet exists and must be invoked by name if they want it.

If this skill is already loaded from an earlier turn and the current request drifts toward starting a run without naming it, state plainly that a gauntlet run is heavy (real cost, subagent fan-out, work that may span days and sessions) and ask for explicit confirmation before initializing any state. No confirmation, no run.

## Surface precheck

Before initializing a run, verify the surface can actually run a gauntlet. Run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/precheck.py
```

It detects four capabilities: clean-context subagent spawning (invariants 2 and 4 depend on it), filesystem read and write (state, resumability, evidence), command execution (inspection methods `run`, `test`, `measure`, `screenshot`, `render`), and network fetch (only when the domain needs `source-reach`).

Three outcomes, and only these behaviors:

| Result | Behavior |
|---|---|
| `full` | Proceed normally. |
| `degraded` | Proceed only after naming the missing capability and its cost to the user. Record `"context_isolation": "degraded"` or `"execution": "degraded"` in `run.json`. Every handoff document and every evidence report from this run carries a banner naming the degradation. |
| `unsupported` | Refuse to initialize a run. Explain that the method needs an agentic harness. Offer brief-only mode: run `gauntlet-brief` and `gauntlet-prompt`, produce `CONTEXT.md`, `PLAN.md`, `bar/`, and `prompt.md`, and hand the user a prompt to run in Claude Code. |

A plain chat surface with no subagents and no filesystem is `unsupported`. Brief-only mode is the correct answer there. Never simulate a loop: no faked rounds, no imagined critics, no narrated iteration.

Record the precheck result in the run's `run.json`. If no run directory exists yet, carry the result into `gauntlet-brief`, which writes it when `init_run.py` creates `run.json`.

Degraded subagent mode means each judge runs as a separate task invocation seeded only from files on disk, with no shared conversational context. That is weaker than a clean context window and must be labeled as such everywhere it appears.

## The seven invariants

When any choice conflicts with one of these, the invariant wins.

1. **INV-1.** The bar is external and inspectable: a real artifact, source set, test suite, benchmark, or measurement. Never a self-authored mid-run rubric, never prose adjectives.
2. **INV-2.** The builder never grades itself. Critics and verifiers run in fresh context with no builder history, rationale, or summary. Enforced by spawning code and validated by script.
3. **INV-3.** Judgment inspects the real thing: rendered pixels, a running process, actual test output, the finished prose read end to end, the actual sources. Never a description written by whoever made it.
4. **INV-4.** Quality and integrity are judged separately, by different verifiers with different mandates and different context.
5. **INV-5.** Nothing is done without re-runnable evidence: paths, commands, exit codes, hashes, screenshots, source URLs. Absence of evidence is reported as absence, never as a pass.
6. **INV-6.** Continuity is written from state by script, not narrated by the outgoing agent. The departing agent may append clearly labeled judgment notes and nothing more.
7. **INV-7.** Caps pause, they do not certify. A piece that hits a round cap, wave cap, wall clock, or cost ceiling is `capped`, never `done`.

## Routing

First match wins. Read run state from disk before routing (see `references/routing.md` for how to locate an existing run directory).

| Signal | Route |
|---|---|
| No run directory for this goal | Surface precheck, then `gauntlet-brief` |
| Precheck returns `unsupported` | Brief-only mode, then stop |
| Brief exists, no `prompt.md` | `gauntlet-prompt` |
| `prompt.md` exists, status not `running` | `gauntlet-run` |
| "resume", new session, or stale `run.lock` | `gauntlet-handoff` read mode, then `gauntlet-run` |
| Session ending, or "hand this off" | `gauntlet-handoff` write mode |
| Status `stopped` or `converged`, no consensus | `gauntlet-verify` |
| Consensus exists and is `verified` or `verified-with-dissent` | `gauntlet-evidence` |
| Consensus is `failed` or `unverifiable` | `gauntlet-run` with the gaps as new work |
| "is it actually done" | `gauntlet-verify`, never the report first |

Two hard rules:

1. The router may not report completion. Completion claims come only from `gauntlet-evidence`, reading verified consensus from disk.
2. The router may not skip verification to reach the report. A request for the report on an unverified run routes to `gauntlet-verify` first, every time.

For per-row detail, run-directory discovery, and degraded or unsupported behavior, read `references/routing.md` in this skill.
