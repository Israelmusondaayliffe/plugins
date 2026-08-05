---
name: graph-debug
description: Diagnose operating graph failures read-only by replaying events, checking hashes and graph versions, reconstructing transitions, validating artifacts, finding deadlocks, and distinguishing node, edge, state, policy, and budget failures. Use when a graph run is stuck, corrupt, inconsistent, or unexpectedly failed.
---

# Graph Debug

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

Remain read-only unless the user explicitly requests a separate repair workflow.

1. Replay with `python3 scripts/graphctl.py replay <run-directory>`.
2. Check resumability and integrity with `python3 scripts/graphctl.py resume-check <run-directory>`.
3. Inspect the graph with `python3 scripts/graphctl.py inspect <run-directory> --format text` and `python3 scripts/graphctl.py inspect <run-directory> --format mermaid`.
4. Reconstruct node transitions and graph-version changes from the hash-chained events.
5. Check missing, corrupt, invalidated, superseded, or wrongly owned artifacts.
6. Detect same-epoch deadlocks, impossible dependencies, illegal transitions, policy blockage, and exhausted node or run budgets.
7. Classify the primary cause as node failure, edge failure, state corruption, policy blockage, or exhausted budget.
8. Produce a bounded repair proposal without applying it or weakening controls.

Treat a broken event chain or immutable graph-version mismatch as corruption and stop automatic execution. Read [runtime-protocol.md](../../references/runtime-protocol.md) and [rewrite-policy.md](../../references/rewrite-policy.md).
