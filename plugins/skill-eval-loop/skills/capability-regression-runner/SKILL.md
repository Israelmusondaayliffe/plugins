---
name: capability-regression-runner
description: Use when a skill or plugin needs a regression check, candidate comparison, pinned baseline, or receipt. Runs local case and rubric checks without editing source, with optional OpenAI Plugin Eval analysis.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Capability Regression Runner

1. Initialize the target if needed with `python3 scripts/skill_eval_loop.py init TARGET`.
2. Require a suite that passes `validate-suite`.
3. Supply real case and rubric result files. Missing results remain missing and prevent a pass.
4. Run the target or an isolated staged candidate with `run`.
5. Let `auto` add OpenAI Plugin Eval analysis only when the installed evaluator can be resolved. Use `enhanced` when that analysis is required.
6. Read the structured run files. Treat `receipt.json` as the status source.
7. Pin a baseline only from a passing receipt with `pin-baseline`.

If Plugin Eval is unavailable in `auto` mode, record `evaluator_unavailable`, keep its score and grade null, and finish the local evaluation. Stop when the source changes or a limit is exhausted. Do not widen limits silently.
