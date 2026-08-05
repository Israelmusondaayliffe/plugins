# Sol Advisor Composition Contract

Sol Advisor supplies bounded TaskPacket, ReturnPacket, and workstream ReviewPacket artifacts to an explicitly approved Gauntlet run. It is a subordinate packet protocol, not a second orchestration authority.

## Ownership

| Surface | Sole owner in a composed run |
| --- | --- |
| Canonical state | Gauntlet |
| Budget and launch ledger | Gauntlet |
| User approval | Gauntlet |
| Integration | Gauntlet |
| Final user answer | Gauntlet |
| Terminal verdict | Gauntlet |

The adapter may perform only a delegated Gauntlet registration. It never creates a second RunManifest, state machine, review authority, final answer, or terminal verdict.

## Preconditions

Before compiling or registering a task, the adapter requires:

1. a compiled Gauntlet program in `gauntlet_compiled` or `executing` state;
2. an approved plan, approval record, matching plan version, and canonical `plan_sha256`;
3. a RunManifest in `gauntlet_composed` mode with exact Gauntlet ownership and host-metadata parent proof;
4. an exact manifest task DAG and task authorization;
5. current, hash-verified worker creation request and successful response evidence with `threadId` and `hostId`;
6. canonical `.gauntlet/runtime-task-records.json` owned by Gauntlet and bound to the same run and plan;
7. remaining launch, current-concurrency, time, critic-round, and repair-round capacity;
8. dependency-ready, non-cyclic, non-overlapping, compiled workstream scopes; and
9. the preserved three-perspective Gauntlet verification panel.

Caller-supplied active task lists are forbidden. Active overlap and concurrency are derived from the canonical task records.

## Compile a task

Gauntlet supplies the RunManifest, workstream ID, task ID, classification, exact write root, finite task limits, and workstream-local output path. The adapter checks every value against the canonical authorization and compiled workstream, including that expected outputs resolve inside the task write roots. It commits the new TaskPacket and the canonical `compiled` record in one in-process rollback transaction. A later write failure removes the new packet and restores the record so the task can be retried.

    python3 scripts/sol_advisor_adapter.py --protocol-root AGENT_OPS_ROOT compile-task --project-root PROJECT --run-manifest RUN.json --workstream-id WS-A --task-id TASK-1 --classification complex --write-target APPROVED_ROOT --max-retries 0 --max-elapsed-minutes 60 --output PROJECT/.gauntlet/workstreams/WS-A/sol-advisor/TASK-1.json

The adapter does not consume or extend the Gauntlet budget. Gauntlet records actual launches and remains the budget owner.

## Register a return

Gauntlet supplies the same RunManifest, the canonical TaskPacket, a ReturnPacket, and a workstream-local receipt path. The adapter rechecks the live compiled workstream, canonical TaskPacket path and hash, task authorization, dependencies, budget, runtime evidence, actual scope, expected artifact paths, evidence commands, artifact hashes, and criterion-to-evidence mapping.

    python3 scripts/sol_advisor_adapter.py --protocol-root AGENT_OPS_ROOT register-return --project-root PROJECT --run-manifest RUN.json --task-packet TASK.json --return-packet RETURN.json --output PROJECT/.gauntlet/workstreams/WS-A/sol-advisor/TASK-1-registration.json

On a valid return, the adapter stages updates to existing Gauntlet-owned records only: `runtime-task-records.json`, `artifact-register.md`, `source-register.md`, `progress.md`, and an append-only event in `state.json`. The workstream receipt is part of that same in-process rollback transaction. A write failure restores every committed canonical file and removes the new receipt. This is rollback-protected, not crash-atomic across files. The receipt indexes the resulting file hashes. The adapter does not change `gauntlet.yaml`, `budget-ledger.json`, plan approval, integration, final answer, or a terminal verdict.

Pass `--protocol-root` explicitly and point it at the public Agent Ops source or installed bundle that contains the canonical Sol Advisor validator. The public adapter never searches local personal sources, private caches, or home-directory plugin paths. A missing or invalid explicit protocol root is a stop condition, not a reason to substitute another runtime.

An optional ReviewPacket may be supplied for validation. It must match the authorized fresh reviewer and remain read-only. The adapter never treats it as acceptance or as a substitute for the required verification panel.

## Context policy

The protocol preserves the 150000-token checkpoint as observation only. `observed_above_without_crossing` and `telemetry-unavailable` do not mutate configuration. Numeric occupancy is null when telemetry is unavailable.
