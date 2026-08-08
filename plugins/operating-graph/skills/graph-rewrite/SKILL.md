---
name: graph-rewrite
description: Diagnose inadequate operating graph topology and propose or apply the smallest bounded rewrite with evidence, primitive operations, risk classification, policy checks, full-graph validation, approval handling, and rollback information.
---

# Graph Rewrite

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

Drafting a proposal file is read-only with respect to the run. Submitting it with `propose-rewrite` persists a controller-owned rewrite record. Applying it mutates graph versions and runtime state through the controller.

1. Inspect triggering events and diagnose the topology failure.
2. Produce the smallest sufficient proposal using only `add_node`, `update_node`, `disable_node`, `add_edge`, `disable_edge`, and `set_priority`.
3. State evidence event IDs, predicted benefit, possible regressions, risk level, approval requirement, and rollback version.
4. When the user requests persisted submission, use `python3 scripts/graphctl.py propose-rewrite <run-directory> <proposal.json>`. Do not submit a draft-only proposal.
5. Apply with `python3 scripts/graphctl.py apply-rewrite <run-directory> <proposal-id>` only when policy permits and every required approval already exists.
6. Confirm the new immutable version with `python3 scripts/graphctl.py status <run-directory>` and validate it with `python3 scripts/graphctl.py validate <run-directory>/graph.json`.

Never change the original goal, completion criteria, authority, permissions, approval boundaries, or hard limits without required approval. Never weaken controls after corruption. Preserve every prior graph version and rollback reference.

Read [rewrite-policy.md](../../references/rewrite-policy.md) before drafting or applying a proposal.
