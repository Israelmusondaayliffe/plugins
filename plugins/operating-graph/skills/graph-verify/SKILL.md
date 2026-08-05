---
name: graph-verify
description: Verify an operating graph outcome against its immutable original goal, completion criteria, deliverables, artifact integrity, evaluator independence, evidence provenance, critical-node status, approvals, and mutation history. Use for terminal verification or completion decisions.
---

# Graph Verify

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

Verification is read-only with respect to graph topology and worker output. Disclose before execution that the CLI writes controller-owned verification audit events.

1. Stop if integrity fails: run `python3 scripts/graphctl.py resume-check <run-directory>`.
2. Return to the immutable original goal and enumerate every completion criterion.
3. Verify deliverable existence, ownership, hash integrity, and evidence provenance.
4. Verify each required deliverable has an independent evaluator and no node evaluated or approved its own output.
5. Check unresolved failed or blocked critical nodes, required approvals, and prohibited mutations.
6. For every executed `subagent` node, verify controller-owned dispatch and launch receipts, a fresh non-fork launch record, matching agent identity, bounded return packet, and graph-version binding.
7. Run `python3 scripts/graphctl.py verify <run-directory>`.
8. Return exactly `pass`, `conditional-pass`, or `fail`, with criterion-level evidence and unresolved issues.

Never mark a run complete merely because all workers stopped. A worker return is evidence, not acceptance. Never repair evidence or relax criteria during verification.

Read [graph-contract.md](../../references/graph-contract.md) and [runtime-protocol.md](../../references/runtime-protocol.md) when tracing criteria or evidence.
