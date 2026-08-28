# Regression run phase

## Scope

Execute a validated suite and compare it with a pinned baseline. Do not edit or promote the target.

## Workflow

1. Confirm case and rubric result files came from real runs.
2. Run `python3 scripts/skill_eval_loop.py run TARGET --case-results CASES.json --rubric-results RUBRIC.json`.
3. Inspect `checks.json`, `rubric.json`, `diff.json`, and `receipt.json` rather than relying on console prose.
4. Pin only a receipt whose status is `passed`.

## Output

Return the run directory, regression result, stop reason, and smallest evidence-backed next action.
