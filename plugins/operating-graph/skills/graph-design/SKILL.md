---
name: graph-design
description: Convert a goal into a typed, validated operating graph with explicit authority, approvals, node contracts, dependencies, deliverables, independent evaluation, budgets, and safe parallel work. Use for new graph design or topology planning before execution.
---

# Graph Design

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

This workflow writes graph design artifacts but does not start a run.

1. Restate the immutable goal, deliverables, completion criteria, authority node, approvals, permissions, and hard limits.
2. Choose the smallest sufficient set of typed nodes. Separate authority, controller, production, shared state, and independent evaluation responsibilities.
3. Draw only real dependencies. Independent work should fan out in parallel; do not serialize lanes because chat would have presented them sequentially.
4. Separate producers from skeptics and synthesis. Prefer the diamond pattern when appropriate: planner, parallel specialists, independent skeptic, synthesis, final evaluation, human decision.
5. Define every node contract and typed edge. Mark optional work explicitly and use `next_epoch` for every feedback cycle.
6. Add an independent evaluator path for every required deliverable. Add an approval predecessor for every external side-effect node.
7. Save the definition as `graph.json` and a Mermaid representation. Preview scheduling before automation.
8. Run `python3 scripts/graphctl.py validate <graph.json>` and fix every violation before presenting the graph.
9. Ask for approval before handing the graph to `$graph-run` when material external actions exist.

Do not execute the graph or apply rewrites. Never change authority or weaken completion criteria to make validation pass.

Read [graph-contract.md](../../references/graph-contract.md) before authoring the JSON. Use [graph.json](../../assets/templates/graph.json) for a minimal inline graph or [diamond-graph.json](../../assets/templates/diamond-graph.json) for a checked parallel workflow.
