# Astra Advisor protocol

Protocol version 1 defines a fixed topology. It is not an adaptive agent pool.

## Activation and exact runtime mapping

Activation must be a genuine imperative request. Quoted, explanatory, negated, conditional, and incidental references are not activation.

| Role | Model | Reasoning effort | Runtime proof |
| --- | --- | --- | --- |
| Parent | `gpt-6-astra` | xhigh | Host metadata or an explicit unavailable record |
| Routine worker | `gpt-6-astra` | xhigh | Fresh `create_thread` request and successful response |
| Complex worker | `gpt-6-astra` | xhigh | Fresh `create_thread` request and successful response |
| Workstream critic | `gpt-6-astra` | high | Fresh non-fork `create_thread` request and successful response |

There is no model or effort substitution. A missing or forged runtime record stops dispatch. Parent effective-model evidence may come only from host metadata or be explicitly unavailable. Configuration and self-report are not parent effective-model evidence.

## RunManifest

The RunManifest is the approved packet constitution. It requires mode, run type, explicit activation, an approved plan with version, root-relative path, and SHA-256. Validation loads that plan file and verifies the declared hash before accepting the remaining goal, criteria, topology, parent runtime attestation, exact task DAG and authorization, runtime mapping, one full-request budget, write policy, prohibited actions, context policy, and authority ownership.

The DAG and authorization use the same task IDs and dependencies. Each authorization binds the task role, model, effort, work type, expected observable delta, unresolved count, support-artifact limit, immediate decision for read-only tasks, reviewer, inputs with hashes, expected output, acceptance criteria, tools, evidence commands, stop conditions, finite limits, and exact write roots. The fixed topology contains only these edges:

1. parent to routine worker
2. parent to complex worker
3. routine worker to reviewer
4. complex worker to reviewer

For standalone runs, the parent owns state, budget, approval, integration, final answer, and terminal verdict. For `gauntlet_composed` runs, every one of those surfaces belongs to Gauntlet. The default full-request budget allows six total worker or reviewer launches, four concurrent tasks, one integrated critic round, one repair round, and one final verification pass. Higher launch or concurrency caps require an explicit cost warning and approval. The absolute validator ceiling is 24 launches and 8 concurrent tasks.

## TaskPacket

A TaskPacket includes the source RunManifest path and hash and copies one exact authorization. The validator first binds the run, plan, task authorization, and DAG dependencies. It then checks the worker role, model, effort, runtime evidence, inputs, expected output, criteria, tools, write scope, evidence commands, stop conditions, limits, and context references. Input records must carry the approved plan path and hash. Every expected output must resolve beneath an authorized write root.

Workers may implement, test, and return evidence only. They may not spawn workers, approve work, integrate workstreams, modify Gauntlet state or budget, answer the user, or issue a verdict.

## ReturnPacket

A ReturnPacket reports work. Its statuses are `succeeded`, `blocked`, `failed`, and `escalate`. It includes the source TaskPacket path and hash, actual scope, artifact paths and hashes, evidence, criterion mapping, commands, uncertainty, risks, and next action.

The validator loads the TaskPacket and checks the run, task, plan, scope, artifacts, commands, and criteria in standalone and composed runs. Every artifact must match an expected output and resolve beneath an authorized write root.

Ordinary low-risk commands use one inline summary. Reserve hash-verified `AstraAdvisorCommandEvidence` records for destructive, security, release, or installation operations. Packet validation checks the selected record mode but does not execute commands or claim independent reproduction.

Every status requires evidence. `succeeded` maps every criterion to `met` and requires every evidence command to exit zero. Blocked, failed, and escalated returns map at least one criterion to the matching outcome and may record failed commands.

Every ReturnPacket records `observable_delta`, `primary_output_count`, `unresolved_before`, `unresolved_after`, `support_artifact_count`, and `next_target_action`. For implementation work, success requires a non-empty delta, at least one primary output, and a smaller unresolved count when unresolved work existed. Support artifacts may not exceed the task authorization limit.

## ReviewPacket

Only the fresh Astra High critic issues a ReviewPacket. Its verdicts are `accepted`, `revise`, `blocked`, and `unable_to_verify`. By default, one reviewer inspects the integrated result and may emit bounded summaries for affected workstreams. The same reviewer ID may be shared across those authorizations.

The packet includes exact TaskPacket and ReturnPacket paths and hashes, plan identity, artifacts, evidence, reproduction commands, findings, fresh-task attestation, uncertainty, risks, and next action. Reviewed artifacts must equal the ReturnPacket artifact set and stay within the TaskPacket write authority.

The reviewer remains read-only and non-terminal. An `accepted` verdict requires every reproduction command to exit zero. The reviewer may not build, repair, write, accept work on behalf of Gauntlet, update state or budget, integrate, or replace the three-perspective verification panel.

## Runtime and context evidence

Task and review runtime attestation binds run ID, task ID, reviewer ID where applicable, role, exact model ID, effort, the structured Codex task target, freshness, `codex_app__create_thread`, non-fork status, request timestamp/hash, and successful response timestamp/hash with `threadId` and `hostId`. Both referenced JSON records must repeat those bindings exactly.

`checkpoint_tokens` is exactly 150000 and `checkpoint_type` is `observation_checkpoint`. Permitted semantic records are `below_checkpoint`, `observed_above_without_crossing`, and `telemetry-unavailable`. The latter requires null numeric occupancy. No checkpoint record authorizes a configuration change.

## Failure handling

Fail closed for implicit activation, model substitution, unavailable required runtime proof, unbounded or impractically large unapproved limits, cycles, unauthorized task IDs, unresolved dependencies, exhausted budgets, unsafe or overlapping scopes, competing authority, zero-delta implementation success, support-artifact overflow, and missing or hash-mismatched evidence.

## Task creation authority

Before any dispatch, verify that the user explicitly requested separate tasks. Advisor activation does not imply permission to create sidebar tasks. Require the Codex desktop task-creation surface and exact model/effort support; otherwise return an unsupported-runtime handoff without dispatch. Subagent receipts do not satisfy this protocol.
