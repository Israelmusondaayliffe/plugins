# Ownership and state

Skill Eval Loop owns target-specific suites, run evidence, pinned baselines, regression decisions, and staged candidate copies.

It can coordinate with these optional owners:

- OpenAI Plugin Eval can add static analysis, measurement plans, benchmarks, comparisons, and metric packs.
- Skill Creator Pro can advise on skill authoring patterns and trigger descriptions.
- LoopKit can own generic schedules and sustained loop operations.
- Capability Operator can add inventory, overlap analysis, portfolio records, and fresh discovery proof.

The local evaluator remains complete without those companions. It validates suites and supplied evidence, fingerprints the source and candidate, enforces limits and approval gates, compares local baseline pass rates, and writes the terminal receipt. Missing enhanced analysis is recorded without an invented score or grade.

State lives under `${CODEX_HOME}/skill-eval-loop` when `CODEX_HOME` is set, otherwise `~/.codex/skill-eval-loop`. The target ID combines a readable name with a hash of the resolved path.

Promotion is never part of evaluation. A candidate must be staged, evaluated, pinned to a passing run, explicitly approved, and checked against the original source fingerprint before promotion.
