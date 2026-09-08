# Native Worker Operations

How the Fable Advisor parent dispatches, monitors, collects, and retries native Claude Code worker subagents, the default worker runtime (`claude-code`). The parent reads this before dispatching, monitoring, or collecting any native worker. The packet-level encoding is the required TaskPacket `dispatch` object defined in `protocol.md`. Tasks authorized with runtime `codex` follow `codex-transport-operations.md` instead; a task never changes runtime after authorization.

## Roles and models

- Parent: the activating session, `claude-fable-5-1` at `high` effort. Plans, approves, dispatches, validates, integrates, reviews, synthesizes.
- Worker: `agent-ops:fa-worker`, pinned in its agent definition to `claude-fable-5-1` at `high` effort, with write tools. One write-enabled TaskPacket per instance.
- Verifier: `agent-ops:fa-verifier`, pinned to `claude-fable-5-1` at `high` effort, read-only tools. One `verify` TaskPacket per instance.

Both definitions ship under the plugin's `agents/` directory. Confirm both appear among the Agent tool's available subagent types before creating run state; if either is missing, stop and report the exact blocker.

## Dispatch

Dispatch parallel, long, or substantial target-state mutations and repository diagnoses to a worker or verifier. The parent may execute bounded work itself within the approved plan and write scope under the SKILL.md Parent execution rules, with the same evidence and review requirements. The parent never substitutes another subagent type and never passes a `model` override to the Agent tool (the definitions pin the model).

The Agent tool call names `subagent_type: "agent-ops:fa-worker"` for `fa_worker` packets or `"agent-ops:fa-verifier"` for `fa_verifier` packets. The prompt carries the TaskPacket path, the run root, the required working directory, and the evidence directory, and nothing else: bounded packet context and named reference paths only, exactly as the TaskPacket `context` object declares. Never send the parent transcript or hidden reasoning.

`execution_mode: "foreground"` (`run_in_background: false`) is for exactly one small bounded task whose result the parent needs before anything else can proceed. `execution_mode: "background"` is for multi-step, long-running, parallel, or substantial write work. When in doubt, background: it preserves the sparse-parent posture and keeps the session responsive.

The agent ID the Agent tool returns is the runtime identity. Write the spawn record immediately with that ID as `runtime_id` and the subagent type as `agent_type`.

## Effort

Worker effort is fixed at `high` by the agent definitions; the Agent tool has no per-call effort override. Every packet records `effort: "high"`. A different rung needs a new agent definition in a new plugin version approved by the user, never a per-run change. `/tasks` shows the model and effort each running subagent uses and is the live cross-check.

## Monitoring

The harness notifies the parent when a background subagent finishes. Between notifications, check a specific agent only on the packet cadence (`monitoring.cadence_seconds`, default 300) and never more often, with `TaskOutput` for that agent ID only: `status_scope: "agent_id_only"`. Never sweep all tasks. Never supervise individual worker tool actions. Collect once at a terminal status: `result_collection: "terminal_only"`.

## Collection and attestation

At a terminal status, locate the subagent transcript at `~/.claude/projects/<project-slug>/<parent-session-id>/subagents/agent-<agent-id>.jsonl` and read the distinct `model` values recorded on its assistant messages.

- Exactly `claude-fable-5-1` observed: job record `attestation: "verified"`, `observed_model: "claude-fable-5-1"`, `source: "subagent_transcript"`, `reason: null`.
- Transcript missing or unreadable: `attestation: "partially-verified"`, `observed_model: null`, a non-empty `reason`. Record the limitation in the run log.
- Any other model observed: contradiction. Fail closed, quarantine the task's work, and report. Claude Code runs a blocked model value on the inherited model with only a warning, so the transcript is the proof, not the request.

`raw` carries at least `agent_id`, `transcript_path`, `models_observed`, and `task_status`. Then validate the ReturnPacket. Write-enabled workers author their own ReturnPacket; the parent transcribes a verifier's text into a ReturnPacket with `authored_by: "parent"`.

## Retry

Every dispatch is fresh. There is no resume of a worker across packets: a stopped, partial, or untrusted worker is never continued. Permit at most one fresh retry per task (`attempt_policy.max_fresh_retries`, 0 or 1) after a failure, always inside the task attempt limit and the run launch cap, then stop and report honestly.

## Cleanup

Stop unfinished workers with `TaskStop` when a run ends, is cancelled, or exhausts its budget. Preserve compact durable evidence for every worker: the spawn record, the job record with the transcript path and observed models, the ReturnPacket, command evidence, status-change notes in the run log, and the terminal state. Never delete run evidence.
