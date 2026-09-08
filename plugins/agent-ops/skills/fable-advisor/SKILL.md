---
name: fable-advisor
description: Use only after the user explicitly says "Use Fable Advisor" or gives an equivalent imperative. Adaptive parent-orchestrated workflow on Claude Code where the activating Fable 5.1 session at high effort plans, dispatches, integrates, and reviews; native Fable 5.1 subagents execute bounded packets by default, with Codex workers through the official Codex plugin as a per-task option. Packet validation, model attestation, parent final review, and no implicit activation.
---

# Fable Advisor

Fable Advisor is a hidden, explicit-only, user-invoked adaptive multi-task workflow on Claude Code. The activating session is the parent: model `claude-fable-5-1` at `high` effort. It plans, dispatches, integrates, reviews, and synthesizes. By default, native Claude Code subagents pinned to `claude-fable-5-1`, `agent-ops:fa-worker` and `agent-ops:fa-verifier`, build and verify tasks. Codex, through the official `codex@openai-codex` plugin, remains an available worker runtime that the RunManifest authorizes per task; it is never a silent fallback and never silently replaced.

It is unrelated to Claude Code's built-in advisor feature (`advisorModel`, `--advisor`). Do not conflate them.

## Activation

Require an explicit request: "Use Fable Advisor" or an equivalent imperative such as "run this as a Fable Advisor multi-session run." Quoted, explanatory, negated, conditional, and incidental references are not activation. Complexity, model names, agent language, or a request that merely has several tasks never activate it. A later same-request revocation ("but don't activate it", an immediate "no") cancels activation. Record the quoted imperative in the RunManifest as the activation record.

If activation is absent or revoked, use the normal routing owners (agent-ops-router, loopkit, outcome-engine, or plain in-session work).

## Mutual exclusion with the gauntlet

Fable Advisor and the gauntlet are peer explicit-only top-level workflows. They never auto-activate, nest, or compose each other. Whichever workflow the user explicitly invokes owns that run. If the user names both for one run, or invokes either workflow while the other has an active run on the target, stop, create no run state, and ask the user to choose one workflow or end the active run.

Detect an active gauntlet run read-only by checking the target for a non-terminal `.gauntlet/runs/*/run.json`. Neither workflow silently supersedes the other.

## Roles and authority

| Role | Runtime identity | Authority |
| --- | --- | --- |
| Parent | The activating session, model `claude-fable-5-1`, effort `high` | Plan, obtain approval, execute bounded work itself within the approved plan and write scope, dispatch, validate, integrate, perform final review, synthesize, issue the final answer and terminal verdict, and stop the run |
| Worker | `agent-ops:fa-worker`, a fresh subagent pinned to `claude-fable-5-1` at `high` effort. The Agent tool's agent ID is its identity. | Execute one write-enabled TaskPacket within its declared scope, run task-level checks, and write its ReturnPacket |
| Verifier | `agent-ops:fa-verifier`, a fresh read-only subagent pinned to `claude-fable-5-1` at `high` effort | Execute one `verify` TaskPacket and return checkable evidence as text; the parent transcribes the ReturnPacket |
| Codex worker (option) | One job through the official Codex plugin, authorized per task with runtime `codex`. The companion job ID is its identity. Model `codex-default` or an explicit Codex model ID. | Execute one TaskPacket within its declared scope, run task-level checks, and return evidence. A `verify` Codex task is read-only. |

The parent never substitutes one runtime for another after authorization and never passes a `model` override to the Agent tool. When it delegates, native Fable 5.1 workers are the default. When it executes work itself, the rules in Parent execution apply. If `agent-ops:fa-worker` or `agent-ops:fa-verifier` is not among the Agent tool's available types, native tasks cannot run; if the official Codex plugin cannot be invoked, codex-authorized tasks cannot run. Either case stops with an exact blocker report.

Choose Codex for a task only when the user asks for it or the approved plan names it (for example, a task that benefits from a second model family, or a Codex-native toolchain). Record the choice in the task authorization; the default for every unmarked task is native.

Workers never approve, integrate, perform final review, contact the user, issue a final answer, or change run authority. A ReturnPacket is evidence, not acceptance.

## Worker execution

Dispatch only through the Agent tool: `subagent_type: "agent-ops:fa-worker"` for write-enabled packets, `"agent-ops:fa-verifier"` for `verify` packets. The prompt names the TaskPacket path, the run root, the working directory, and the evidence directory, and nothing else from the parent's context. Use `run_in_background: true` for background execution. Never pass `model`: the agent definitions pin `claude-fable-5-1` and `effort: high`, and a different rung needs a new agent definition in a new plugin version, never a silent change.

The agent ID the Agent tool returns is the runtime identity and names the subagent transcript (`agent-<id>.jsonl`). The parent writes the spawn record at dispatch and the job record at collection from the transcript's observed model. Before dispatching, monitoring, or collecting any worker, read `references/native-worker-operations.md`.

Write-enabled workers write their own ReturnPacket inside the run directory. Verifiers return text, and the parent transcribes the ReturnPacket with `authored_by: "parent"`. Never enable hooks, gates, credentials, or credential changes from inside a run.

For a task authorized with runtime `codex`, dispatch through the official plugin only: the `codex:codex-rescue` subagent via the Agent tool, or the companion CLI (`node <codex-plugin-root>/scripts/codex-companion.mjs task|status|result --json`) when the target directory differs or when collecting results. The companion job ID is the runtime identity; the parent writes the spawn record at dispatch and the job record from `result <job-id> --json`. Before any Codex dispatch, resume, monitoring, or collection, read `references/codex-transport-operations.md`. The plugin's automatic stop-time review gate stays disabled.

## Parent execution

The parent is Fable 5.1 at high effort, and it may do bounded implementation itself rather than only orchestrate. Parent execution is allowed when the approved plan names the work (or the user asks for it), the writes stay inside the plan's approved write scope, and the work is small enough that a dispatch would cost more than it saves: a critical-path fix, an integration-adjacent edit, a change the parent must understand fully to review the rest.

Parent execution keeps every ownership and evidence rule. The parent records each parent-executed task in the run log with its objective, the write scope used, the observable target-state delta, and the evidence commands it ran, captured as command evidence records or inline low-risk command entries exactly as a worker would report them. It does not write a TaskPacket for itself and never counts parent-executed work against the worker launch cap, but it does count the elapsed time against the run budget. Parent-executed work is a candidate like any other: it goes through the same final review, reproduction commands, and hash freeze before acceptance, and the parent must not treat having written something as having reviewed it. Delegation stays the default for parallel, long, or substantial work, with native Fable 5.1 workers first and Codex by explicit authorization.

## Sparse-parent posture

Fable 5.1 is expensive. The parent plans, gets approval, executes only the bounded work it has reserved for itself, dispatches the rest, and then stays out of the way. It wakes for blockers, completion notifications, ReturnPacket collection and validation, material replanning, integration, and final review. It never supervises individual worker tool actions. It never checks a background worker more often than the packet cadence. The default is to collect at completion, not to poll.

## Work-first execution

Execution against the requested target is the primary work. Exploration, plans, tests, receipts, and criticism are support. They count as progress only when they directly enable or verify a requested target-state change. Progress is measured as observable target-state delta plus a falling unresolved-work count. Passing validators never outweighs required items still unfinished.

Every implementation worker owns a direct deliverable or target-system mutation. A successful ReturnPacket carries a `work_report` with `observable_delta`, `primary_output_count`, `unresolved_before`, `unresolved_after`, `support_artifact_count`, and `next_target_action`. The parent rejects implementation success when the observable delta is empty or unresolved required work did not improve. Audit-only workers are exceptional. Each names the immediate decision it informs, and they never outnumber implementation workers on an implementation run.

## Procedure

1. **Audit.** Confirm the session model is `claude-fable-5-1` and that `agent-ops:fa-worker` and `agent-ops:fa-verifier` are available subagent types. Record `claude_code_version`, `entrypoint`, `parent_session_id`, `parent_model`, `parent_effort`, `dispatch_interface: "agent_tool"`, and `worker_model` in the manifest. If any task will use runtime `codex`, also locate the newest installed official Codex plugin, run its companion `setup --json` check, and record `codex_plugin_version` and `codex_dispatch_interface`. Fail closed and report the exact blocker if anything a planned task needs is missing.
2. **Plan.** Decompose the request into a task DAG. Interview the user only for shape-changing unknowns. Write the RunManifest from `assets/run-manifest.template.json` with finite limits, exact write roots, and per-task authorization. Read `references/protocol.md` before writing packets.
3. **Approve.** Present the RunManifest summary, including total planned launches and expected usage, and get explicit user approval before dispatch. No blanket approvals.
4. **Dispatch or execute.** For each ready task the parent has reserved for itself, execute it under Parent execution and log it. For every other ready task, write and validate a TaskPacket (native packets carry `dispatch`; Codex packets carry the optional `transport`), launch it through the runtime the authorization names, and write the spawn record with the returned agent ID or companion job ID. Respect concurrency, launch, dependency, and write-scope limits.
5. **Collect.** At completion, write the job record (native: from the subagent transcript; Codex: from `result <job-id> --json`), validate the ReturnPacket, and compare the attestation with the TaskPacket. Quarantine any contradiction. Retry only within the packet and manifest limits.
6. **Assemble.** Integrate inside declared scopes only, serialize shared-file edits, freeze the candidate, and record its hashes.
7. **Final review.** The parent re-runs reproduction commands, consults evidence from any `verify` tasks, and writes the ReviewPacket with `reviewer: "parent"`, `model: "claude-fable-5-1"`, and `effort: "high"`. Re-verify candidate hashes before issuing a verdict.
8. **Revise loop.** On `revise`, write narrow repair TaskPackets bound to the findings and dispatch fresh workers. Stop at the manifest round limit and report honestly.
9. **Synthesize.** Only after an accepted parent review, write the final deliverable and completion claim with evidence.
10. **Clean up.** Stop unfinished native workers with `TaskStop` and cancel unfinished Codex jobs with the official `cancel` command, close the run record with status and costs, and report output paths. Never delete evidence.

## Run directory

`<target-project-root>/.fable-advisor/runs/<run-id>/` contains `run-manifest.json`, `tasks/`, `returns/`, `reviews/`, `evidence/`, and `run-log.jsonl`. All packet paths are root-relative. Pass the target project root to the validator with `--root`. The run directory is durable state. A fresh session resumes an open run only after the user explicitly re-invokes Fable Advisor.

## Limits

One resource budget covers discovery, audit, implementation, review, repair, and final verification. Defaults: at most 6 total launches, 4 concurrent tasks, 1 integrated review round, 1 repair round, 1 compact final verification pass, and 240 elapsed minutes. Retries use a fresh worker and count against the launch cap. Higher limits require a concrete cost warning and explicit user approval. On rate limits, halve concurrency and back off. When a cap is reached, stop dispatching and report. "As many as needed" never means unbounded.

## Failure handling

Fail closed on implicit activation, protocol mismatch, undiscoverable worker agents, an unavailable or unauthenticated Codex plugin on a codex-authorized task, parent model or effort mismatch, worker model or effort contradiction, unbounded limits, DAG cycles, unauthorized task IDs, unresolved dependencies, exhausted budgets, overlapping write scopes, competing authority, and missing or hash-mismatched evidence. A missing runtime is a hard stop with an exact blocker report, never a silent substitution onto the other runtime.

## Completion

The run ends in exactly one recorded terminal state: `accepted-and-synthesized`, `blocked`, `failed`, `cancelled`, or `budget-exhausted`. Report the state with evidence paths. Never label unreviewed work accepted.

## Mutable lifecycle record

Keep `run-manifest.json` immutable after its hash is bound by a TaskPacket. Maintain a separate adjacent `run-state.json` with `run_id`, `manifest_sha256`, `status` (`active`, `completed`, `failed`, or `cancelled`), `updated_at` (UTC timestamp), and `evidence` (root-relative record paths). Create `active` only after activation and collision checks. Record a terminal state only after the corresponding completion evidence, recorded failure, or explicit cancellation. Status does not grant task or publication authority. Gauntlet checks this record and its manifest hash; missing, malformed, or mismatched state requires reconciliation, not inferred activity or completion.
