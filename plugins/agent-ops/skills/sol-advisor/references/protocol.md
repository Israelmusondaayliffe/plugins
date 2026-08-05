# Sol Advisor Protocol

Protocol version 1 defines a fixed topology. It is not an adaptive agent pool.

## Activation and exact runtime mapping

Activation must be a genuine imperative request. Quoted, explanatory, negated, conditional, and incidental references are not activation.

| Role | Model | Reasoning effort | Runtime proof |
| --- | --- | --- | --- |
| Parent | `gpt-5.6-sol` | high | Host metadata or an explicit unavailable record |
| Routine worker | `gpt-5.6-luna` | max | Fresh `create_thread` request and successful response |
| Complex worker | `gpt-5.6-terra` | max | Fresh `create_thread` request and successful response |
| Workstream critic | `gpt-5.6-sol` | xhigh | Fresh non-fork `create_thread` request and successful response |

There is no model or effort substitution. A missing or forged runtime record stops dispatch. Parent effective-model evidence may come only from host metadata or be explicitly unavailable. Configuration and self-report are not parent effective-model evidence.

## Portable runtime profiles

`assets/runtime-profiles.json` names the Codex, Claude Code, and Cowork profiles. Each has one explicit record for fresh-task creation, exact model and effort selection, scheduling, durable state, hooks, and fresh-task discovery. A profile records its required proof and a fail-closed action for unavailable support.

The fixed Sol Advisor topology can run only where every required capability has current proof. Codex requires a successful non-fork `create_thread` record and host-attested exact model and effort support. Claude Code and Cowork retain their profiles for portable packet interpretation, but their shipped profiles stop fixed-topology dispatch until a host-native fresh-task and exact-model proof is supplied. Scheduling and hooks are not implicit substitutes for task creation, state, or discovery.

## RunManifest

The RunManifest is the approved packet constitution. It requires mode, explicit activation, an approved plan with version, root-relative path, and SHA-256. Validation loads that plan file and verifies the declared hash before accepting the remaining goal, criteria, topology, parent runtime attestation, exact task DAG and authorization, runtime mapping, finite launch/concurrency/time/critic/repair limits, write policy, prohibited actions, context policy, and authority ownership.

The DAG and authorization use the same task IDs and dependencies. Each authorization binds the task role, model, effort, reviewer, inputs with hashes, expected output, acceptance criteria, tools, evidence commands, stop conditions, finite limits, and exact write roots. The fixed topology contains only these edges:

1. parent to routine worker
2. parent to complex worker
3. routine worker to reviewer
4. complex worker to reviewer

For standalone runs, the parent owns state, budget, approval, integration, final answer, and terminal verdict. For `gauntlet_composed` runs, every one of those surfaces belongs to Gauntlet.

## TaskPacket

A TaskPacket includes the source RunManifest path and hash and copies one exact RunManifest authorization. The validator loads the referenced RunManifest and binds run, plan, task authorization, and DAG dependencies before checking the worker role/model/effort, runtime creation request and response evidence, input paths and hashes, expected output, criteria, tools, write scope, evidence commands, stop conditions, finite limits, and bounded context references. Its input records must include the same approved plan path and hash, and every expected output must resolve beneath an authorized write root.

Workers may implement, test, and return evidence only. They may not spawn workers, approve work, integrate workstreams, modify Gauntlet state or budget, answer the user, or issue a verdict.

## ReturnPacket

A ReturnPacket reports work. Its only statuses are `succeeded`, `blocked`, `failed`, and `escalate`. It includes the source TaskPacket path and hash, actual scope, artifact paths and hashes, evidence, criterion-to-evidence mapping, commands, uncertainty, risks, and next action. The validator loads the referenced TaskPacket and requires exact run, task, plan, scope, artifact, command, and criterion bindings in both standalone and composed runs. Every artifact must exactly match an expected output and resolve beneath that TaskPacket's authorized write roots.

Every command evidence file is a hash-verified `SolAdvisorCommandEvidence` JSON record. It binds the run, task, TaskPacket path and hash, exact command, exit code, and SHA-256 hashes of its recorded stdout and stderr. Packet validation checks that record; it does not execute a command or claim independent reproduction. Every status has status evidence. `succeeded` maps every criterion to `met` and requires every evidence command to exit zero; blocked, failed, and escalated returns map at least one criterion to the matching outcome and may record failed commands.

## ReviewPacket

A ReviewPacket is issued only by the fresh Sol XHigh workstream critic. Its only verdicts are `accepted`, `revise`, `blocked`, and `unable_to_verify`. It includes exact TaskPacket and ReturnPacket paths and hashes, plan path/version/hash, artifacts, evidence paths and hashes, recorded reproduction commands, structured findings, fresh task request and response attestation, uncertainties, risks, and next action. The reviewed artifact records must exactly equal the referenced ReturnPacket artifact set and remain within the TaskPacket write authority.

The reviewer remains read-only and non-terminal. An `accepted` verdict requires every reproduction command to exit zero. The reviewer may not build, repair, write, accept work on behalf of Gauntlet, update state or budget, integrate, or replace the three-perspective verification panel.

## Runtime and context evidence

Task and review runtime attestation binds run ID, task ID, reviewer ID where applicable, role, exact model ID, effort, the structured Codex task target, freshness, `codex_app__create_thread`, non-fork status, request timestamp/hash, and successful response timestamp/hash with `threadId` and `hostId`. Both referenced JSON records must repeat those bindings exactly.

`checkpoint_tokens` is exactly 150000 and `checkpoint_type` is `observation_checkpoint`. Permitted semantic records are `below_checkpoint`, `observed_above_without_crossing`, and `telemetry-unavailable`. The latter requires null numeric occupancy. No checkpoint record authorizes a configuration change.

## Failure handling

Fail closed for implicit activation, model substitution, unavailable required runtime proof, unbounded limits, cycles, unauthorized task IDs, unresolved dependencies, exhausted budgets, unsafe or overlapping scopes, competing authority, and missing or hash-mismatched evidence.
