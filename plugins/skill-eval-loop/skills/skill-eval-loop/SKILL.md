---
name: skill-eval-loop
description: Use when a skill or plugin needs an evidence-backed eval loop with trigger tests, a pinned baseline, regression checks, and approval-gated repair. Routes suite design, test runs, and staged fixes.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Skill Eval Loop

Route the request to one phase. Keep evaluation, judgment, and source promotion separate so a candidate cannot approve its own change.

## Router

- New prompt corpus, trigger cases, functional checks, or rubric: read `../eval-suite-builder/SKILL.md` and `agents/agent-suite.md`.
- Run, compare, pin a baseline, or inspect evidence: read `../capability-regression-runner/SKILL.md` and `agents/agent-run.md`.
- Stage or promote a candidate repair: read `../capability-repair-cycle/SKILL.md` and `agents/agent-repair.md`.
- End-to-end request: suite, manual run, independent rubric, baseline decision, then staged repair only if needed.

## Handoff gates

- A run requires a valid suite with ten positive and ten negative trigger cases.
- A passing local receipt requires supplied case results, independent rubric evidence, unchanged source state, and all limits. Plugin Eval checks are additional evidence when available.
- Baseline pinning requires a passing receipt.
- Promotion requires explicit user approval and a matching source fingerprint.
- Scheduling may route to LoopKit after a successful manual end-to-end run.

Load `references/ownership-and-state.md` before changing ownership or state policy.

## Failure behavior

Stop on missing ground truth, an evaluator required by `enhanced` mode, repeated failure signature, exhausted limits, stale source fingerprint, or cancelled approval. In `auto` mode, a missing evaluator does not stop the local result. Report the exact missing evidence. Do not soften the suite.
