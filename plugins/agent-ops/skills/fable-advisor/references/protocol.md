# Fable Advisor Protocol

Protocol version 3. Adaptive topology on Claude Code. The activating Claude parent, `claude-fable-5-1` at `high` effort, plans, dispatches, integrates, and performs final review. Worker tasks run on one of two authorized runtimes: the default, native Claude Code subagents pinned to `claude-fable-5-1` (runtime `claude-code`), or, by explicit per-task authorization, Codex through the official `codex@openai-codex` plugin (runtime `codex`). Protocol 2 packets fail validation.

## Activation and runtime mapping

Activation must be a genuine imperative request, recorded verbatim in the RunManifest. Quoted, explanatory, negated, conditional, and incidental references are not activation. A same-request revocation cancels it.

| Role | Runtime and model | Responsibility | Runtime proof |
| --- | --- | --- | --- |
| Parent | Activating session, model `claude-fable-5-1`, effort `high` | Plan, approve, execute bounded work itself within the approved plan and write scope (logged with evidence, reviewed like any candidate), dispatch, validate, integrate, perform final review, write the final answer, and issue the terminal verdict | Manifest runtime record, parent session ID, and run-log entries for parent-executed work |
| Native worker (default) | `agent-ops:fa-worker`, a fresh subagent spawned through the Agent tool, pinned to `claude-fable-5-1` at `high` effort | Execute one bounded write-enabled task and write its ReturnPacket | Spawn record plus job record. The Agent tool's agent ID is the runtime identity |
| Native verifier (default) | `agent-ops:fa-verifier`, a fresh read-only subagent pinned to `claude-fable-5-1` at `high` effort | Execute one `verify` task and return checkable evidence as text for the parent to transcribe | Spawn record, job record, parent-authored ReturnPacket, and command evidence |
| Codex worker (option) | One job through the official Codex plugin. Model `codex-default` or an explicit Codex model ID. Effort `default` or an explicit companion effort | Execute one bounded task (write-enabled, or read-only `verify`) and produce a ReturnPacket | Spawn record plus job record. The companion job ID is the runtime identity |

There is no silent runtime, model, effort, or dispatch substitution. The parent never passes a `model` override to the Agent tool and never swaps a task's authorized runtime. Missing or contradicted attestation quarantines the affected work.

## Evidence records

**Spawn record** (`evidence/<task-id>.spawn.json`) is written by the parent at dispatch. Its exact keys are: `record_type` (`FableAdvisorSpawnRecord`), `protocol_version` (3), `run_id`, `subject_type`, `subject_id`, `runtime` (`claude-code` or `codex`), `mechanism` (`fa_worker` or `fa_verifier` for `claude-code`; `codex_rescue` or `codex_companion` for `codex`), `requested_model`, `requested_effort`, `write_enabled` (boolean), `runtime_id` (the Agent tool's agent ID, or the companion job ID), and `spawned_at` (ISO-8601). Native spawns carry one more required key, `agent_type` (`agent-ops:fa-worker` for `fa_worker`, `agent-ops:fa-verifier` for `fa_verifier`); Codex spawns must omit it.

**Job record** (`evidence/<task-id>.job.json`) is written by the parent at collection. Its exact keys are: `record_type` (`FableAdvisorJobRecord`), `protocol_version` (3), `run_id`, `subject_type`, `subject_id`, `job_id` (equal to the spawn runtime ID), `status`, `requested_model`, `observed_model`, `attestation` (`verified` or `partially-verified`), `source`, `reason`, and `raw`. It may carry one optional `observed_effort` key, null or a non-empty string.

- Native: the record is written from the subagent transcript, `~/.claude/projects/<project>/<parent-session-id>/subagents/agent-<agent-id>.jsonl`. `verified` requires `source: "subagent_transcript"`, an observed model equal to the requested model, and a null reason. `partially-verified` requires a null observed model and a non-empty reason. `raw` carries at least the transcript path, the distinct model values observed, and the task's terminal status. Claude Code runs a blocked model value on the inherited model with only a warning, which is why the transcript is the proof.
- Codex: the record is written from the companion `result <job-id> --json` payload, with `raw` holding that verbatim object. `verified` requires a non-empty observed model and a null reason; for an explicit requested model the observed model must match. `partially-verified` requires a non-empty reason and is acceptable only for `codex-default` requests.
- Either runtime: an observed model or effort that contradicts an explicit request fails closed.

**Command evidence record** is a hash-verified `FableAdvisorCommandEvidence` JSON object with the exact keys `record_type`, `protocol_version`, `run_id`, `subject_type`, `subject_id`, `bound_packet_path`, `bound_packet_sha256`, `command`, `exit_code`, `stdout`, `stdout_sha256`, `stderr`, and `stderr_sha256`. It binds the command result to its task packet or to review subject `round-N`.

## RunManifest

The approved packet constitution. Required top-level keys, exactly: `packet_type` (`FableAdvisorRunManifest`), `protocol_version` (3), `run_id`, `activation` (`{type: "explicit", quoted_request, recorded_at}`), `plan` (`{status: "approved", version, path, sha256}`), `goal`, `criteria`, `runtime`, `task_dag`, `task_authorization`, `budget`, `write_policy`, `prohibited_actions`, and `authority`.

`runtime` has the required keys `claude_code_version`, `entrypoint`, `parent_session_id`, `parent_model` (`claude-fable-5-1`), `parent_effort` (`high`), `dispatch_interface` (`agent_tool`), and `worker_model` (`claude-fable-5-1`). When any task authorization uses the `codex` runtime it must also carry `codex_plugin_version` (from the audited plugin) and `codex_dispatch_interface` (`codex_rescue` or `codex_companion`); both are optional otherwise.

Each task authorization binds exactly: `task_id`, `classification` (`light`, `complex`, or `verify`), `role` (`worker`), `runtime` (`claude-code` or `codex`), `model`, `effort`, `write_enabled`, `dependencies`, `allowed_write_paths`, `input_paths`, `expected_output`, `acceptance_criteria`, `evidence_commands`, `stop_conditions`, and `limits`. For `claude-code`, model is `claude-fable-5-1` and effort is `high`, the values pinned by the plugin's agent definitions; a different native rung needs a new agent definition in a new plugin version, never a per-run change. For `codex`, model is `codex-default` or an explicit Codex model ID and effort is `default`, `none`, `minimal`, `low`, `medium`, `high`, or `xhigh`. A verify task is read-only. The DAG and authorizations name the same task IDs with identical dependencies. Cycles, self-dependencies, unauthorized dependencies, unassigned criteria, path escapes, and unsafe scope overlap are rejected.

One finite budget covers the request. Defaults are 6 launches, 4 concurrent tasks, 1 review round, 1 repair round, one compact final verification pass, and 240 elapsed minutes. Higher limits require a recorded cost warning and explicit approval. The prohibited-action set remains `approve_work`, `issue_final_answer`, `issue_terminal_verdict`, `reviewer_repairs`, `spawn_peer_workers`, `contact_user`, `integrate_workstreams`, and `modify_run_state`. Every authority surface, `state`, `budget`, `approval`, `integration`, `final_answer`, and `terminal_verdict`, must be owned by `parent`.

## TaskPacket

A TaskPacket binds one authorization to one worker. Required keys are `packet_type`, `protocol_version`, `run_id`, `task_id`, `run_manifest_path`, `run_manifest_sha256`, `plan`, `task`, `authorization`, `worker`, `input_paths`, `expected_output`, `acceptance_criteria`, `scope`, `evidence_commands`, `stop_conditions`, `limits`, and `context`, plus the runtime-specific extension below.

The worker object has exactly `role`, `runtime`, `model`, `effort`, `write_enabled`, `fresh_instance`, and `mechanism`. Role is `worker`, `fresh_instance` is true, and the runtime, model, effort, and write policy match the authorization exactly. `mechanism` must belong to the runtime: `fa_worker` or `fa_verifier` for `claude-code`, `codex_rescue` or `codex_companion` for `codex`. A native `verify` task must use `fa_verifier`, and `fa_verifier` requires `write_enabled: false`. The input, output, criteria, evidence commands, stop conditions, and limits mirror the authorization exactly. The referenced RunManifest is hash-verified, loaded, revalidated, and cross-checked.

**Native dispatch extension.** A `claude-code` packet carries a required `dispatch` object with exactly `execution_mode` (`foreground` or `background`), `monitoring`, and `attempt_policy`. `monitoring` has exactly `cadence_seconds` (a positive integer, default 300), `status_scope` (`agent_id_only`), and `result_collection` (`terminal_only`). `attempt_policy` has exactly `max_fresh_retries`, 0 or 1, always inside the existing task attempt and run launch limits. Every native dispatch is fresh. A `claude-code` packet must not carry `transport`. The operating rules live in `references/native-worker-operations.md`.

**Codex transport extension.** A `codex` packet may carry one optional `transport` object governing how its Codex job is dispatched, monitored, resumed, retried, and collected; `codex` packets without it remain valid, and new Codex packets include it (the bundled `task-packet.codex.template.json` carries it). When present it is validated strictly, with the exact keys `execution_mode` (`foreground` or `background`), `dispatch_mode` (`fresh` or `resume`), `resume_lineage`, `monitoring`, `attempt_policy`, `transfer_policy`, and `review_policy`. `resume_lineage` is null for a fresh dispatch; for a resume it has exactly `prior_job_id`, `prior_thread_id`, and `scope_requirement` (`same_or_narrower`). A `verify` task never resumes. `monitoring` has exactly `cadence_seconds` (positive integer, default 300), `status_scope` (`job_id_only`), and `result_collection` (`terminal_only`). `attempt_policy` has exactly `max_resume_continuations` and `max_fresh_retries`, each 0 or 1. `transfer_policy` is `explicit_emergency_diagnostic_only`. `review_policy` has exactly `instance` (`fresh`), `write_enabled` (false), `authority` (`advisory`), and `acceptance` (`parent`). A `codex` packet must not carry `dispatch`. The operating rules live in `references/codex-transport-operations.md`.

## ReturnPacket

A ReturnPacket reports work and never grants acceptance. Its required keys remain `packet_type`, `protocol_version`, `run_id`, `task_id`, `task_packet_path`, `task_packet_sha256`, `plan`, `status`, `status_evidence`, `scope`, `artifacts`, `criterion_results`, `commands`, `work_report`, `runtime_attestation`, `uncertainties`, `risks`, and `next_action`.

`runtime_attestation` has exactly `runtime`, `mechanism`, `requested_model`, `requested_effort`, `runtime_id`, `authored_by`, `spawn_record`, and `job_record`. Runtime, mechanism, model, and effort match the TaskPacket worker exactly; runtime ID is the Agent tool's agent ID or the companion job ID. `authored_by` is `worker` for write-enabled tasks. It may be `parent` only for a read-only task whose returned text the parent transcribed.

`work_report` retains `observable_delta`, `primary_output_count`, `unresolved_before`, `unresolved_after`, `support_artifact_count`, and `next_target_action`. A succeeded packet requires every criterion met, every evidence command at exit 0, a non-empty observable delta, and improved unresolved required work. Ordinary low-risk command records inline `{command, exit_code, risk: "low", summary}`. Other command records bind `{command, exit_code, evidence_path, evidence_sha256}` to a command evidence record.

## ReviewPacket

The parent session performs final review. Required top-level keys remain `packet_type`, `protocol_version`, `run_id`, `review_round`, `verdict`, `reviewed`, `plan`, `candidate`, `reproduction_commands`, `findings`, `reviewer_attestation`, `uncertainties`, and `next_action`.

`reviewer_attestation` has exactly `reviewer` (`parent`), `model` (`claude-fable-5-1`), `effort` (`high`), `session_id`, and `verification_task_ids` (unique `verify` task IDs consulted by the parent, on either runtime, with an empty list allowed). Reproduction commands use subject type `review` and subject ID `round-N`, and the parent runs them. `accepted` requires every reproduction command at exit 0 and no blocking finding. `revise` requires at least one blocking or major finding.

## Failure handling

Fail closed for implicit activation, protocol mismatch, undiscoverable native worker agents, unavailable or unauthenticated Codex plugin on a codex-authorized task, parent model or effort mismatch, worker model or effort contradiction, unbounded limits, DAG failures, exhausted budgets, unsafe or overlapping scopes, competing authority, and missing or hash-mismatched evidence. Runtime unavailability is a hard stop with an exact blocker report, never a silent substitution onto the other runtime.

## Mutual exclusion with the gauntlet

Fable Advisor and the gauntlet are peer explicit-only workflows. Neither activates, nests, or composes the other automatically. Whichever workflow the user explicitly invokes owns that run. If both are invoked for one run, or one is invoked while the other has an active run on the target, the parent stops and asks the user to choose one workflow or end the active run before creating any state. A manifest naming `gauntlet` on any authority surface is invalid.

## Mutable lifecycle record

Keep `run-manifest.json` immutable after its hash is bound by a TaskPacket. Maintain a separate adjacent `run-state.json` with `run_id`, `manifest_sha256`, `status` (`active`, `completed`, `failed`, or `cancelled`), `updated_at` (UTC timestamp), and `evidence` (root-relative record paths). Create `active` only after activation and collision checks. Record a terminal state only after the corresponding completion evidence, recorded failure, or explicit cancellation. Status does not grant task or publication authority. Gauntlet checks this record and its manifest hash; missing, malformed, or mismatched state requires reconciliation, not inferred activity or completion.
