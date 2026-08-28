# Suite phase

## Scope

Design target-specific trigger, functional, deterministic, and judgment checks. Do not execute the suite or edit the target.

## Workflow

1. Read the target and its ownership boundary.
2. Write at least ten realistic should-trigger and ten near-miss should-stay-silent prompts.
3. Add functional cases tied to observable artifacts or command results.
4. Write rubric criteria before repair instructions. Name external ground truth for each criterion.
5. Run `python3 scripts/skill_eval_loop.py validate-suite SUITE.json` from the plugin root.

## Output

Return the validated suite path and the evidence source for every non-deterministic criterion. Hand execution back to the front door.
