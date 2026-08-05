---
name: graph-run
description: Initialize, execute, resume, and coordinate a validated operating graph with deterministic scheduling, bounded concurrency, node packets, artifact registration, policy-gated rewrites, and terminal verification. Use when the user asks to run or continue an operating graph.
---

# Graph Run

This Operating Graph skill is explicit-only. Load it only from a namespaced command, a genuine current Operating Graph imperative routed through `graph-engineering`, or an explicit plugin selection.

This workflow mutates runtime state. The controller is the sole writer of runtime records. Workers may write only within their assigned node-run and artifact directories.

1. Validate with `python3 scripts/graphctl.py validate <graph.json>`.
2. Initialize with `python3 scripts/graphctl.py init <graph.json> --run-root <directory>`.
3. Preview without mutation using `python3 scripts/graphctl.py dispatch-preview <run-directory> --json`. Detect worker capacity and reserve one controller slot.
4. Prepare bounded work with `python3 scripts/graphctl.py prepare-dispatch <run-directory> --json`. This creates `NodeTaskPacket` files, controller-owned dispatch receipts, and fresh-thread launch specifications for ready `subagent` nodes.
5. Launch each specification through `collaboration.spawn_agent` with `fork_turns: "none"`. Do not pass the parent transcript. Do not allow a node worker to spawn agents.
6. Persist each real request and response as a `ThreadLaunchRecord`, then run `python3 scripts/graphctl.py record-launch <run-directory> <record.json>`. The controller anchors the launch hash in a separate receipt. Only a validated successful launch may transition a node to `running`.
7. Require the worker to write a `NodeReturnPacket` at the canonical attempt path. Ingest it with `python3 scripts/graphctl.py ingest-return <run-directory> <return-packet.json>`. The controller validates hashes, scope, criteria, authority, and artifacts before changing state.
8. Inline, tool, and human nodes remain explicit execution modes. Never silently downgrade a `subagent` node to inline work when the thread surface is unavailable.
9. Evaluate rewrite triggers only after the events defined in [rewrite-policy.md](../../references/rewrite-policy.md). Reject stale returns after a graph-version change.
10. Continue until completion, escalation, cancellation, or a hard limit. Before resuming, run `python3 scripts/graphctl.py resume-check <run-directory>`.
11. Finish with `python3 scripts/graphctl.py verify <run-directory>` and report graph versions, thread evidence, artifacts, unresolved issues, and the exact verdict.

Stop automatic execution on event-chain corruption, missing thread evidence, stale packets, unavailable required model support, unsafe scope, or exhausted limits. Do not synthesize approvals, exceed budgets, or let workers edit controller-owned files.

The collaboration surface does not provide per-thread host filesystem confinement. Treat node write roots as a validated authority boundary. Require a separate sandbox surface when hard containment is part of acceptance.

Read [runtime-protocol.md](../../references/runtime-protocol.md) before execution.
