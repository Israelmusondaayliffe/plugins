---
name: harness-runner
description: Execute an approved Harness Engineering plan as a bounded autonomous run with durable state, iteration receipts, approval stops, resume behavior, and a verifier handoff, on Claude Code, Claude Cowork, or Codex. Use when a user says run the harness build, keep going until verified, resume the build, or carry an approved multi-stage harness implementation to a named terminal state.
---

# Harness Runner

Map a sustained loop onto the platform's autonomy surface only when the user explicitly requests that mode. Use durable state only when the run must cross sessions or resume. Ordinary approved builds stay in the current task or session with one compact run ledger.

## Workflow

1. Require the approved profile, audit, plan, allowed paths, caps, and stop rules.
2. Confirm the primary outcome metric, before and target states, unresolved count, total launch cap, and support-artifact cap.
3. Create durable state only when the approved run needs it. On Cowork, durable state belongs in a connected folder because sandbox-only state does not survive.
4. Observe fresh state and choose one bounded target action.
5. Apply only an approved operation group.
6. Record progress only when the requested target state changes. Tests, receipts, and reports are support work.
7. Stop and re-plan after one wave with no unresolved-work reduction, or when support artifacts outgrow primary outputs.
8. Continue only while target-state progress is measurable and the single run budget has capacity.
9. Stop as waiting input, blocked, exhausted, failed, cancelled, or completed. Do not rename a failure as success.
10. Send the integrated completion candidate to `harness-verifier` once.

The run never grants broader filesystem, authentication, publication, or external-action authority.
