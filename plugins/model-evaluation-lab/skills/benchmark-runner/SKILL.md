---
name: benchmark-runner
description: Executes or delegates a frozen model evaluation plan, records reproducible run conditions, and normalizes raw case results into a stable comparison schema. Use when running model, prompt, agent, or tool benchmarks locally or through Hugging Face jobs, or when completed raw runs need validation and aggregation.
---

# Benchmark Runner

## Overview

Execute the frozen plan on the authorized backend or normalize completed case results. Preserve raw evidence, record conditions, and stop when plan comparability breaks.

## Workflow

1. Validate that the evaluation plan is frozen and `plan_ready` is true.
2. Load `references/workflow.md`.
3. If completed raw case results were supplied, run `scripts/normalize_results.py RAW.json NORMALIZED.json`, then run `scripts/validate_output.py NORMALIZED.json`. Normalization does not require an execution backend.
4. Otherwise, check for an authorized local runner or installed remote backend.
5. If a backend is available, record the plan hash, model and prompt identifiers, environment, dataset version, tool state, repetitions, and cost-accounting method.
6. Execute every frozen case or delegate it to the named backend. Do not add cases after results are visible.
7. Save raw case-level results before aggregation, then normalize and validate them.
8. If no backend is available, use the Execution-blocked handoff below and stop.

## Execution-blocked handoff

Fill `assets/execution-blocked-template.json` and run `scripts/validate_blocked_handoff.py HANDOFF.json`. Record:

- the frozen plan hash and case count;
- the required backend;
- missing credential names or tools without secret values;
- the frozen safety stops;
- an exact rerun command or the named owner who can run it.

Set `execution_complete`, `measured_results_complete`, and `model_selection_complete` to false. Set `winner` to null. Do not create run records, scores, latency, cost, safety results, a model selection, or a winner claim. Planning, schema validation, and normalization of supplied raw results remain available.

## Boundaries

The runner does not invent missing executions, scores, latency, cost, safety outcomes, model selection, or a winner. It does not change the frozen plan to improve a candidate's result.

## Error recovery

Mark the run partial when an execution fails or coverage differs. Preserve successful raw records, list the failed case identifiers, and require an equivalent rerun before comparison. Stop immediately when the plan's safety rule fires.

## Reliability

Backend invocation depends on the installed execution surface. Result normalization, aggregation, blocked-handoff validation, and completeness checks are deterministic scripts.
