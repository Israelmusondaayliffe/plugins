# Suite schema

`suite.json` contains:

- `schema_version`: integer `1`.
- `target`: absolute target path.
- `limits`: positive `max_iterations`, `max_minutes`, and optional `max_tokens`.
- `trigger_cases`: at least ten `should_trigger: true` and ten `should_trigger: false` cases.
- `functional_cases`: at least one case with an objective expectation.
- `rubric`: named judgment criteria and the ground-truth source for each criterion.

Every case has a stable string `id`, a realistic `prompt`, and an `expected` description. Trigger results use `{id, passed, evidence}`. Functional results use the same shape. Rubric results use `{criterion_id, passed, evidence}`.

The runner rejects missing cases, duplicate IDs, soft limits, or rubric criteria without ground truth. It does not invent results for tests that were not run. Local receipts compare case and rubric pass rates with a pinned local baseline. Plugin Eval score and grade remain null when the optional evaluator is unavailable.
