# Model Evaluation Lab

Model Evaluation Lab replaces model-choice impressions with a fixed plan, reproducible execution records, normalized results, and a deployment decision with explicit limitations.

## Owned workflow

1. `model-evaluation-router` is the front door. It inspects the request and current artifacts, then selects the next stage or stops on a missing prerequisite.
2. `model-evaluation-plan` fixes the decision, cases, metrics, budget, backend, and stopping rules before results are visible.
3. `benchmark-runner` executes or delegates the plan and normalizes raw case results into a stable schema.
4. `model-selection-memo` separates measured findings from judgment and states deployment conditions.

## Companion boundary

The plugin does not copy Model Prompt Lab or Hugging Face skills. Model Prompt Lab can design prompt-focused cases. Hugging Face can provide datasets, jobs, community evals, and run tracking. Data Storytelling Studio and Writing Quality can format the final decision artifact. Each companion remains independently installed and owned.

An execution backend is optional for planning, schema validation, and normalization of supplied raw results. If no local or remote backend is available for a requested run, Benchmark Runner returns a validated execution-blocked handoff. The handoff records the frozen plan hash, backend requirement, missing credential names or tools without their values, case count, safety stops, and an exact rerun command or named owner. It marks execution, measured results, model selection, and any winner as incomplete.

Run `python3 scripts/check_companions.py` before selecting an execution backend. Run `python3 scripts/verify_bundle.py` before installation or release.

## Maintenance

Edit `plugins/model-evaluation-lab`, increment both version fields, run the unit suite and validators, then reinstall through this marketplace. Treat installed caches as evidence, not source.
