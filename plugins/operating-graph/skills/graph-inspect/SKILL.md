---
name: graph-inspect
description: Inspect an operating graph run read-only, including event-chain integrity, graph version, node status, attempts, budgets, blockers, approvals, artifact lineage, rewrites, bottlenecks, dependencies, and a compact Mermaid view.
---

# Graph Inspect

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

Remain read-only. Do not transition nodes, register artifacts, apply rewrites, or repair files.

1. Validate replay and persisted state with `python3 scripts/graphctl.py resume-check <run-directory>`.
2. Read the current snapshot with `python3 scripts/graphctl.py status <run-directory>`.
3. Show ready work and blockers with `python3 scripts/graphctl.py ready <run-directory>`.
4. Render a compact text report with `python3 scripts/graphctl.py inspect <run-directory> --format text`.
5. Render topology with `python3 scripts/graphctl.py inspect <run-directory> --format mermaid`.
6. Report current graph version, epochs, attempts, budgets, node states, fresh-thread launch records, pending approvals, artifact lineage, applied and proposed rewrites, bottlenecks, and unsatisfied required dependencies.

If the event chain is broken, stop and route diagnosis to `$graph-debug`. Read [runtime-protocol.md](../../references/runtime-protocol.md) for record ownership and integrity rules.
