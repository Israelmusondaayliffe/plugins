---
name: fable-advisor
description: Use only after the user explicitly says "Use Fable Advisor" or gives an equivalent imperative such as "run this as a Fable Advisor multi-session run." Adaptive parent-orchestrated worker fleet with packet validation, exact-model workers, fresh Fable 5 review, and no implicit activation.
---

# Fable Advisor

Fable Advisor is a hidden, explicit-only, adaptive multi-worker workflow for bounded multi-task work on Claude Code. The session that activates it (the parent) plans, dispatches, integrates, and synthesizes. Workers build. A fresh reviewer criticizes. Nothing activates it except a genuine current imperative from the user.

It is unrelated to Claude Code's built-in "advisor" feature (`advisorModel`, `--advisor`); do not conflate them.

## Activation

Require an explicit request: "Use Fable Advisor" or an equivalent imperative such as "run this as a Fable Advisor multi-session run." Quoted, explanatory, negated, conditional, and incidental references are not activation. Complexity, model names, agent language, or a request that merely has several tasks never activate it. A later same-request revocation ("but don't activate it", an immediate "no") cancels activation. Record the quoted imperative in the RunManifest as the activation record.

If activation is absent or revoked, use the normal routing owners (agent-ops-router, loopkit, outcome-engine, or plain in-session work).

## Roles and authority

| Role | Runtime identity | Authority |
| --- | --- | --- |
| Parent | The activating session (expected model `claude-fable-5`) | Plan, obtain user approval, dispatch, validate packets, integrate, spawn reviewers, synthesize, claim completion, stop the run |
| Worker | Fresh instance of `fa-worker-light` (`claude-sonnet-5`) or `fa-worker-complex` (`claude-opus-4-8` baseline; `fa-worker-complex-opus5` / `fa-worker-complex-46` only when the manifest authorizes it on recorded evidence) | Execute exactly one TaskPacket inside its write roots; run evidence commands; return a ReturnPacket. May delegate bounded lookups to its own nested subagents (one level). |
| Reviewer | Fresh instance of `fa-reviewer` (`claude-fable-5`, xhigh), new instance every round, never resumed | Read the approved spec, candidate artifacts, and evidence; reproduce declared checks; return accepted, revise, blocked, or unable_to_verify. Read-only. |

Workers never approve, integrate, review, contact the user, or spawn peer workers. The reviewer never builds, repairs, writes, approves on the user's behalf, synthesizes, or becomes lead. A ReturnPacket is evidence, not acceptance. Only the parent produces the final answer, and only after an `accepted` verdict.

## Procedure

1. **Audit.** Verify the runtime supports every model the run needs (Opus 5 requires Claude Code >= 2.1.219). Record runtime versions and session identity in the RunManifest. Fail closed on unsupported mappings: stop and ask, never substitute silently.
2. **Plan.** Decompose into a task DAG. Interview the user (knowing-your-unknowns) for shape-changing unknowns. Write the RunManifest from `assets/run-manifest.template.json` with finite limits, exact write roots, and per-task model authorization. Read `references/protocol.md` before writing packets.
3. **Approve.** Present the RunManifest summary to the user and get explicit approval before any dispatch. No blanket approvals.
4. **Dispatch adaptively.** For each ready task: write a TaskPacket, validate it (`python3 scripts/validate_packets.py --root RUN_ROOT PACKET.json`), spawn the worker in the background with the packet path as its brief, and write the spawn evidence record. Add workers as the DAG unblocks; retire them as tasks finish. Respect the manifest's concurrency and launch caps. Repo-mutating tasks use worktree isolation or serialized dependencies.
5. **Collect.** Validate every ReturnPacket. Check attestation (requested model versus observed model); a mismatch quarantines the task's artifacts and forces re-dispatch or a user decision. Retry failed tasks up to the packet's limit with fresh instances.
6. **Assemble.** Integrate inside declared scopes only, serialize shared-file edits, freeze the candidate, and record its hashes.
7. **Review.** Spawn a fresh `fa-reviewer` with only: the approved spec, the candidate paths and hashes, the evidence records, and the packet paths. Never planner reasoning or worker transcripts. Validate the ReviewPacket. After review returns, re-verify the candidate hashes; any change is an integrity failure that stops the run.
8. **Revise loop.** On `revise`, write narrow repair TaskPackets bound to the findings, rebuild, and submit to a new fresh reviewer instance. Never reuse a reviewer agent ID across rounds. Stop at the manifest's round limit and report honestly.
9. **Synthesize.** Only after `accepted`: the parent writes the final deliverable and the completion claim, citing verdicts and evidence.
10. **Clean up.** Stop remaining background agents, remove unchanged worktrees, close the run record with status and costs, and announce output paths. Never delete evidence.

## Run directory

`<target-project-root>/.fable-advisor/runs/<run-id>/` with `run-manifest.json`, `tasks/`, `returns/`, `reviews/`, `evidence/`, and `run-log.jsonl`. All packet paths are root-relative; pass the run root to the validator with `--root`. The run directory is the durable state: a fresh session resumes an open run by reading the manifest and task states after the user explicitly re-invokes Fable Advisor.

## Limits (defaults, user-overridable in the manifest)

Start 3 concurrent workers, cap 8. Max 24 worker launches per run. Retries: 2 per task, fresh instance each time. Review rounds: 3. Elapsed: 240 minutes. Worker-local nesting: one level. On rate limits, halve concurrency and back off. When a cap is reached, stop dispatching and report; "as many as needed" never means unbounded.

## Failure handling

Fail closed on: implicit activation, model or effort mismatch, missing attestation, unbounded limits, DAG cycles, unauthorized task IDs, unresolved dependencies, exhausted budgets, overlapping write scopes, competing authority, and missing or hash-mismatched evidence. A worker's Fable-refusal or classifier stop is `blocked`, and re-dispatch on another model requires the user's recorded approval.

## Collisions

- Gauntlet: while a gauntlet run is active, gauntlet owns state, budget, approval, integration, final answer, and terminal verdict. Fable Advisor activates inside it only if the user explicitly composes them, and then supplies only bounded packets and workstream criticism.
- Generic goals, loops, schedules: loopkit owns them. Agent design and audit: agent-ops-router owns them.
- Dynamic workflows / ultracode: separate opt-in surfaces; Fable Advisor neither requires nor implies them.

## Completion

The run ends in exactly one recorded terminal state: `accepted-and-synthesized`, `blocked`, `failed`, `cancelled`, or `budget-exhausted`. Report which one, with evidence paths. Never label unreviewed work accepted.
