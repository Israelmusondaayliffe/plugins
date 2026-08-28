# Benchmark execution workflow

## Backend routing

- Local harness: use when the model endpoint and dataset can be invoked reproducibly in the current environment.
- Hugging Face Jobs: use when remote compute, dataset access, or tracked community evaluation is needed and the companion is installed.
- External authorized runner: use when credentials or production infrastructure must remain outside the host platform. Export the frozen plan and require the stable raw result contract on return.

## No execution backend

Do not block planning, schema validation, or normalization of supplied raw results when no execution backend exists. If a requested run has no authorized local runner or installed remote backend, write an execution-blocked handoff from `../assets/execution-blocked-template.json` and validate it with `../scripts/validate_blocked_handoff.py`.

The handoff must contain the frozen plan hash, backend requirement, case count, safety stops, and missing credential names or tools without their values. Include an exact rerun command or name the owner who can execute the plan. Mark execution, measured results, model selection, and the winner as incomplete. Do not create raw run records or infer scores, latency, cost, safety results, model selection, or a winner.

## Raw result contract

Each case record must include a unique identifier, candidate configuration, pass state, numeric score, latency in milliseconds, and marginal request cost. Record failures explicitly. Do not encode a failed execution as a score of zero unless the frozen metric defines that treatment.

## Handoff gate

The normalized run is comparable only when candidate coverage, plan hash, dataset, environment, and stopping-rule treatment match. A partial run can be preserved but cannot support model selection.
