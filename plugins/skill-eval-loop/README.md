# Skill Eval Loop

Skill Eval Loop supplies persistent local baselines and bounded repair cycles. It validates suites, supplied case evidence, and independent rubric evidence without companion plugins. OpenAI Plugin Eval is an optional enhanced analyzer. Its code is not copied into this package.

## Safety boundary

- Evaluation reads the target and writes only under the plugin state root.
- Candidate edits happen in an isolated staging copy.
- Promotion back to the source requires an explicit approval token and an unchanged source fingerprint.
- Scheduling may be handed to LoopKit after a successful manual run. LoopKit is not required for local evaluation.

## Local CLI

```bash
python3 scripts/skill_eval_loop.py init /absolute/path/to/skill
python3 scripts/skill_eval_loop.py validate-suite /path/to/suite.json
python3 scripts/skill_eval_loop.py run /absolute/path/to/skill --case-results /path/to/results.json --rubric-results /path/to/rubric.json
python3 scripts/skill_eval_loop.py pin-baseline /absolute/path/to/skill RUN_ID
```

`run` uses `--evaluator-mode auto` by default. It adds Plugin Eval analysis when the evaluator is available and otherwise writes `evaluator_unavailable`, keeps plugin-specific score and grade fields null, and completes the local evidence decision. Use `--evaluator-mode enhanced` only when Plugin Eval must be present. Use `--evaluator-mode local` to skip the enhanced analyzer.
