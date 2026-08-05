# Graph Contract

Use JSON with `schemaVersion`, `graphId`, `name`, `goal`, `limits`, `nodes`, `edges`, `rewritePolicy`, and `metadata`.

## Goal and authority

The goal contains a statement, typed deliverables, completion criteria, and `authorityNodeId`. Treat these as immutable after run creation. Define exactly one enabled `authority` node and one enabled `controller` node. Every enabled node must be reachable from authority.

## Node contract

Each node defines `id`, `kind`, `label`, `purpose`, `enabled`, `critical`, `priority`, `execution`, `capabilities`, typed `inputs` and `outputs`, `successCriteria`, `budget`, and `localLoop`.

Allowed kinds are `authority`, `controller`, `worker`, `state`, `evaluator`, `distributor`, and `signal`. Allowed execution modes are `inline`, `subagent`, `tool`, and `human`.

Local loops are bounded work inside one node. They cannot add nodes, reroute edges, alter authority, or write runtime state. Graph-level failure triggers start only after the node's local loop is exhausted.

`subagent` execution means a fresh, non-forked, bounded thread. It is never a synonym for scheduler eligibility and never falls back to inline execution. `modelHint` is optional; when present it is an exact requested model and unavailable support blocks dispatch. When absent, record the host-selected runtime evidence that is actually available.

## Edge contract

Each edge defines `id`, `source`, `target`, `kind`, `enabled`, `required`, `temporal`, `artifactTypes`, and `activation`. Activation declares its mode, required node states, artifacts, and approvals.

Allowed kinds are `goal`, `assign`, `read`, `write`, `verify`, `approve`, `publish`, `measure`, `escalate`, and `learn`. Temporal values are `same_epoch` and `next_epoch`.

The enabled same-epoch execution projection must be acyclic. Every directed feedback cycle needs a `next_epoch` edge and a finite positive `limits.maxEpochs`.

## Required invariants

- IDs are unique and use lowercase letters, digits, and hyphens.
- Every edge endpoint exists and disabled nodes cannot satisfy dependencies.
- Every required deliverable has a producer and independent evaluator path.
- A node cannot evaluate or approve its own output.
- Every external side-effect node has an approval predecessor.
- Limits are positive integers and graph versions are sequential and immutable.
- Conditions contain no executable source code and paths cannot escape the run directory.
- A subagent worker cannot spawn workers, approve, integrate, update controller state, answer the user, or issue a terminal verdict.
- A succeeded subagent node requires bound task, launch, return, criterion, scope, and artifact evidence for the current graph version.

Validate with `python3 scripts/graphctl.py validate <graph.json>`.
