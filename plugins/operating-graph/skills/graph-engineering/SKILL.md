---
name: graph-engineering
description: Use only after the user explicitly invokes Operating Graph through a namespaced skill or a genuine imperative such as "Use Operating Graph." Route the request to graph design, run, inspect, rewrite, debug, or verification without inferring activation from complexity or graph-related discussion.
---

# Graph Engineering

Operating Graph is explicit-only and user-invoked. Accept a namespaced invocation or a genuine direct imperative such as `Use Operating Graph` or `Run this as an Operating Graph`. Quoted, explanatory, negated, conditional, incidental, complexity-only, multi-task, and generic adaptive-topology wording do not activate it.

Before designing a graph, check fit. A graph is useful when work has multiple dependent steps, genuinely independent lanes, separate checking, meaningful risk, or human approvals. Use the smallest topology that improves the result. Remove artificial waiting and keep a simple task on an inline path.

Identify the requested operation before touching a run:

- Design a new topology: use `$graph-design`.
- Execute or resume a graph: use `$graph-run`.
- Read current state or lineage: use `$graph-inspect`.
- Change topology: use `$graph-rewrite`.
- Diagnose corruption, deadlock, or failure: use `$graph-debug`.
- Judge the final outcome: use `$graph-verify`.

Explain the boundary when relevant: local loops correct work inside one node, while Operating Graph coordinates and reorganizes work across nodes. Operating Graph owns topology and scheduling even when a node uses an optional local loop capability. It does not require that companion.

Operating Graph is an agent-workflow graph, not a knowledge graph. It may consume knowledge artifacts, but knowledge-relationship indexing belongs to its source-owning capability.

Treat routing and explanation as read-only. Do not initialize a run, mutate topology, or perform an external action unless the user requests the corresponding workflow. Never infer approval for material external actions.

Use `python3 scripts/graphctl.py validate <graph.json>` before handing any graph to execution.

Read [graph-contract.md](../../references/graph-contract.md) when graph semantics or authority boundaries matter.
