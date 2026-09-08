# Codex Transport Operations

How the Fable Advisor parent dispatches, monitors, resumes, retries, and collects Codex work through the official plugin, for tasks the RunManifest authorizes with runtime `codex`. Native Fable 5.1 subagents are the default worker runtime (see `native-worker-operations.md`); Codex is the retained option, chosen per task with explicit authorization. The parent reads this before dispatching, resuming, monitoring, or collecting any Codex job. The packet-level encoding is the optional TaskPacket `transport` extension defined in `protocol.md`. New Codex packets include it, the bundled `task-packet.codex.template.json` carries it, and `codex` packets without it remain valid.

## Dispatch routing

For every task authorized with runtime `codex`, dispatch the target-state mutation or repository diagnosis to Codex exactly as authorized. The parent plans, approves, validates, integrates, reviews, and synthesizes, and may execute bounded work itself under the SKILL.md Parent execution rules; it never swaps a codex-authorized task onto a native subagent (or the reverse). Before the first Codex dispatch of a run, locate the newest installed official plugin under `~/.claude/plugins/cache/openai-codex/codex/`, run its companion `setup --json` check, and record `codex_plugin_version` and `codex_dispatch_interface` in the manifest. If Codex cannot be invoked, the codex-authorized tasks stop with an exact blocker report.

## Execution mode

Foreground (`execution_mode: "foreground"`) is for exactly one small bounded task whose result the parent needs before anything else can proceed. Background (`execution_mode: "background"`) is for multi-step, long-running, parallel, or substantial write work. When in doubt, background: it preserves the sparse-parent posture and keeps the session responsive.

## Model and effort ladder

- Light and routine work, including routine verification: `codex-default` with default effort.
- Complex implementation and difficult diagnosis: `codex-default` with high effort.
- xhigh effort or a named Codex model: only after a failed high-effort attempt, for unusually consequential work, or on an explicit user request.

Every rung is approved in the RunManifest task authorization (`model` and `effort`). There is no silent escalation and no silent substitution.

## Fresh versus resume

The default dispatch is fresh: `dispatch_mode: "fresh"` with `resume_lineage: null`. Resume at most once per task, and only for the same trustworthy but incomplete task: the prior job ran cleanly, its partial work is trusted, and it stopped short only because of time, turns, or task size. A resume binds to the prior companion job and thread through `resume_lineage.prior_job_id` and `resume_lineage.prior_thread_id`, with `scope_requirement: "same_or_narrower"`: the continuation instruction stays within the same task authorization scope or a narrower part of it, never wider. Verify tasks always run fresh and are never resumed.

Cancellation, attestation conflict, transport corruption, scope violation, or otherwise untrusted state requires a fresh job. Never resume that state. Permit at most one fresh retry per task after such a failure, then stop and report honestly, always inside the existing task attempt limits and the run launch cap. `attempt_policy` records both bounds: `max_resume_continuations` and `max_fresh_retries`, each at most 1.

## Context boundary

Send bounded packet context and named reference paths only, exactly as the TaskPacket `context` object declares. Never send the full parent transcript or hidden reasoning to Codex, on any dispatch, resume, retry, or review.

## Monitoring and collection

Check background jobs on the packet cadence, `monitoring.cadence_seconds`, default 300 seconds, and never poll more often. Status checks are job-ID-specific: `status <job-id> --json` for the dispatched job only, never broad sweeps. Collect once at a terminal status with `result <job-id> --json`, write the job record from that payload, and validate the ReturnPacket. The sparse-parent posture holds throughout: the parent never supervises individual Codex tool actions.

## Transfer boundary

`/codex:transfer` stays outside normal runs. It is an emergency diagnostic handoff only, for a live-session diagnosis the parent cannot express as a bounded TaskPacket, and it requires explicit user approval recorded in the run log before use. It is never a routine dispatch path. `transport.transfer_policy` is always `explicit_emergency_diagnostic_only`.

## Review boundary

Use `/codex:review` for meaningful code changes and `/codex:adversarial-review` only for consequential design risk. Both produce fresh, read-only, advisory evidence, encoded in `review_policy` as `instance: "fresh"`, `write_enabled: false`, `authority: "advisory"`, and `acceptance: "parent"`. Review output never grants acceptance. Fable alone accepts, in the parent ReviewPacket, and the parent alone issues the final answer and terminal verdict.

## Evidence retention

Preserve compact durable evidence for every job: the spawn record, the job record with the raw companion result payload, the ReturnPacket, command evidence, review evidence, status-change notes in the run log, and the terminal state. Never delete run evidence.

## Attestation

Partial model attestation (`partially-verified` with a recorded reason) is acceptable only for `codex-default` requests when no contradiction is observed. An explicit model or effort contradiction between the request and the observed job fails closed and quarantines the affected work. The optional job-record key `observed_effort` carries the observed effort when the companion reports one; when it contradicts an explicit requested effort, validation fails exactly as it does for an observed model contradiction.
