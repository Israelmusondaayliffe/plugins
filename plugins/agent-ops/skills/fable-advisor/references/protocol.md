# Fable Advisor Protocol

Protocol version 1. Adaptive topology on Claude Code. Derived from the Sol Advisor protocol; runtime evidence is Claude-native.

## Activation and runtime mapping

Activation must be a genuine imperative request, recorded verbatim in the RunManifest. Quoted, explanatory, negated, conditional, and incidental references are not activation; a same-request revocation cancels it.

| Role | Model (exact ID) | Effort | Agent definition | Runtime proof |
| --- | --- | --- | --- | --- |
| Parent | `claude-fable-5` | high (session) | none (activating session) | Session settings record plus runtime record in the manifest; self-report alone is marked `partially-verified` |
| Light worker | `claude-sonnet-5` | low or medium | `fa-worker-light` | Spawn record plus model attestation |
| Complex worker (baseline) | `claude-opus-4-8` | xhigh | `fa-worker-complex` | Spawn record plus model attestation |
| Complex worker (authorized alternates) | `claude-opus-5` / `claude-opus-4-6` | xhigh / high | `fa-worker-complex-opus5` / `fa-worker-complex-46` | Spawn record plus model attestation; manifest must record the evidence for choosing the alternate |
| Reviewer | `claude-fable-5` | xhigh | `fa-reviewer` | Fresh spawn record per round; agent ID never reused across rounds |

There is no silent model or effort substitution. A missing or contradicted attestation quarantines the affected work. An unsupported mapping on the executing runtime stops that dispatch before launch.

**Spawn record** (`evidence/<task-or-review-id>.spawn.json`, written by the parent immediately after spawn): JSON binding `run_id`, `task_id` (or `review_round`), `agent_definition`, `requested_model`, `requested_effort`, `mechanism` (`agent_tool` or `headless`), the returned `agent_id` or `session_id`, and `spawned_at`.

**Model attestation** (`evidence/<id>.model.json`): for `agent_tool` workers, the models observed in the worker's transcript records plus the transcript path when readable, else `attestation: "partially-verified"` with the reason; for `headless` workers, the verbatim `modelUsage` object from `--output-format json`. Requested model absent from observed models = mismatch = fail closed.

## RunManifest

The approved packet constitution. Required top-level keys, exactly: `packet_type` (`FableAdvisorRunManifest`), `protocol_version` (1), `run_id`, `mode` (`standalone` or `composed`), `activation` (`{type: "explicit", quoted_request, recorded_at}`), `plan` (`{status: "approved", version, path, sha256}`, hash verified against the file), `goal`, `criteria` (unique `{id, description}`), `runtime` (`{claude_code_version, entrypoint, parent_session_id, spawn_mechanism}`), `task_dag`, `task_authorization`, `budget`, `write_policy`, `prohibited_actions`, `authority`.

Each task authorization binds: `task_id`, `classification` (`light` or `complex`), `role` (`worker`), `agent_definition`, `model` (exact ID from the role table), `effort`, `dependencies`, `allowed_write_paths`, `input_paths` (`{path, sha256}`, hash verified), `expected_output` (`{description, paths}` inside the write paths), `acceptance_criteria` (exact copies of approved criteria), `tools`, `evidence_commands`, `stop_conditions`, `limits` (`{max_attempts <= 3, max_turns, max_elapsed_minutes}`). The DAG and the authorizations name the same task IDs with identical dependencies; cycles, self-dependencies, and unauthorized dependencies are rejected. Every approved criterion is assigned to at least one task.

`budget` requires finite positive `max_task_launches`, `max_concurrency`, `max_review_rounds`, `max_repair_rounds`, `max_elapsed_minutes`. One budget covers the full user request. Conservative defaults: `max_task_launches` 6 (workers plus reviewers), `max_concurrency` 4, `max_review_rounds` 1, `max_repair_rounds` 1, plus one compact final verification pass; larger values require a recorded cost warning and explicit user approval. `write_policy` requires `mode` (`disjoint_targets`, `separate_worktrees`, or `serialized`), `require_disjoint_active_scopes: true`, `allow_unlisted_writes: false`, and `allowed_write_roots` that contain every task write scope; under `disjoint_targets`, scopes of different tasks must not overlap. `prohibited_actions` is the exact set: `approve_work`, `issue_final_answer`, `issue_terminal_verdict`, `reviewer_repairs`, `spawn_peer_workers`, `contact_user`, `integrate_workstreams`, `modify_run_state`. `authority` names an owner for `state`, `budget`, `approval`, `integration`, `final_answer`, `terminal_verdict`: `parent` in standalone mode, `gauntlet` in composed mode.

## TaskPacket

Binds one authorization to one worker. Required keys: `packet_type` (`FableAdvisorTaskPacket`), `protocol_version`, `run_id`, `task_id`, `run_manifest_path` + `run_manifest_sha256` (hash verified; the manifest is loaded, revalidated, and cross-checked), `plan` (identical to the manifest's), `task` (`{classification, objective, dependencies}`), `authorization` (byte-identical copy of the manifest authorization for this task), `worker` (`{role, agent_definition, model, effort, fresh_instance: true, mechanism}` matching the authorization), `input_paths`, `expected_output`, `acceptance_criteria`, `tools`, `scope` (`{allowed_write_paths, read_paths}`), `evidence_commands`, `stop_conditions`, `limits`, `context` (`{delivery: "bounded_packet_only", include_parent_transcript: false, include_hidden_reasoning: false, reference_paths}` all inside `read_paths`).

The approved plan's path and hash must appear in `input_paths`. Workers implement, test, and return evidence only. They may spawn bounded local subagents one level down; they may not perform any prohibited action.

## ReturnPacket

Reports work; never acceptance. Required keys: `packet_type` (`FableAdvisorReturnPacket`), `protocol_version`, `run_id`, `task_id`, `task_packet_path` + `task_packet_sha256` (verified and loaded), `plan`, `status` (`succeeded`, `blocked`, `failed`, `escalate`), `status_evidence`, `scope` (actual write paths, all inside the packet scope), `artifacts` (`{path, sha256, kind}`, exactly the expected output paths, hashes verified, inside write scope), `criterion_results` (every packet criterion mapped to `met`, `blocked`, `failed`, or `escalate`), `commands`, `work_report`, `runtime_attestation` (`{agent_definition, requested_model, requested_effort, agent_id or session_id, spawn_record {path, sha256}, model_record {path, sha256}}` with both evidence files hash-verified and their bindings checked), `uncertainties`, `risks`, `next_action`.

`work_report` binds the work-first contract: `observable_delta` (list of target-state changes actually made), `primary_output_count`, `unresolved_before`, `unresolved_after`, `support_artifact_count`, `next_target_action`. `succeeded` requires a non-empty `observable_delta` and unresolved required work that improved (`unresolved_after` below `unresolved_before`, or both zero).

Command records are risk-tiered. An ordinary low-risk command inlines its result: `{command, exit_code, risk: "low", summary}`, no separate evidence file. A destructive, security, release, installation, or similarly high-risk command binds `command`, `exit_code`, `evidence_path`, `evidence_sha256`, where the evidence file is a hash-verified `FableAdvisorCommandEvidence` JSON record binding `run_id`, `task_id`, `task_packet_path`, `task_packet_sha256`, the exact command, exit code, and SHA-256 hashes of recorded stdout and stderr. Validation checks records; it does not execute commands. `succeeded` requires every criterion `met` and every evidence command exit 0.

## ReviewPacket

Issued only by a fresh `fa-reviewer` instance. Required keys: `packet_type` (`FableAdvisorReviewPacket`), `protocol_version`, `run_id`, `review_round` (>= 1), `verdict` (`accepted`, `revise`, `blocked`, `unable_to_verify`), `reviewed` (list of `{task_packet {path, sha256}, return_packet {path, sha256}}`, each verified), `plan`, `candidate` (`{path, sha256}` records for the frozen candidate, hashes verified), `reproduction_commands` (same evidence format as ReturnPacket commands, run by the reviewer), `findings` (`{id, severity in {blocking, major, minor, info}, description}`), `reviewer_attestation` (`{agent_definition: "fa-reviewer", model: "claude-fable-5", effort: "xhigh", agent_id, fresh_instance: true, spawn_record {path, sha256}, prior_review_agent_ids}` where `agent_id` must not appear in `prior_review_agent_ids`), `uncertainties`, `next_action`.

`accepted` requires every reproduction command exit 0 and no `blocking` finding. `revise` requires at least one `blocking` or `major` finding. The reviewer is read-only and non-terminal: it may not build, repair, write artifacts, accept work on the user's behalf, update run state, integrate, or synthesize. After review returns, the parent re-verifies candidate hashes; any change is an integrity failure.

## Failure handling

Fail closed for: implicit activation, model or effort substitution, unavailable required runtime proof, unbounded limits, DAG cycles, unauthorized task IDs, unresolved dependencies, exhausted budgets, unsafe or overlapping scopes, competing authority, reviewer reuse across rounds, and missing or hash-mismatched evidence.

## Composed mode

In a gauntlet-composed run, gauntlet owns state, budget, approval, integration, final answer, and terminal verdict. Fable Advisor supplies only bounded packets and workstream criticism, and its authority object names `gauntlet` on every surface.
