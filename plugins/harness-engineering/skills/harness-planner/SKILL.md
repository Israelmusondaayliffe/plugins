---
name: harness-planner
description: Turn a confirmed harness profile and read-only audit into a decision-complete architecture and reversible operation plan for Claude Code, Claude Cowork, or Codex. Use when a user asks for a harness plan, implementation plan, workspace blueprint, capability plan, migration plan, or wants to see exact proposed changes and checks before any global, folder, or project files are edited.
---

# Harness Planner

Plan the outcome, scopes, operations, approvals, evidence, and rollback. Leave no implementation decisions unresolved.

## Workflow

1. Require a confirmed profile and current audit, or record why one is not applicable. The profile names the platform; plan only surfaces that exist there per its platform file.
2. Name the primary outcome metric, the before state, the target state, and the unresolved required-work count. State the expected primary outputs, a support-artifact cap, a total launch cap, and a one-low-yield-wave stop: one wave of work that produces no target-state delta ends the run for re-planning. Execution against the target is the primary work; audits, tests, receipts, and critics are support.
3. Design the information, execution, and feedback layers.
4. Put each requirement in the narrowest durable scope. On Cowork, durable means a connected folder, app-level instructions, or an external system, never the session sandbox.
5. Plan removals before additions. Instructions the audit marked as model compensation come out in their own approval group, each with a stated reason.
6. Reuse installed capabilities before proposing a new skill or plugin.
7. Prefer scripts, rules, hooks, sandbox settings, and templates when behavior must be exact, within what the platform supports.
8. Define separate approval groups using `../../references/safety-and-approvals.md`.
9. Generate file previews, operations, expected hashes, the smallest proportional checks, failure stops, and rollback actions.
10. Use the smallest sufficient topology. A launch cap above six requires a usage warning, a finite expected output per worker, and explicit approval.
11. Present the human plan and machine operations together.
12. Do not begin implementation until the user accepts the plan or explicitly requests end-to-end execution.

Start from `../../assets/harness-plan.template.json`. Validate it with `python3 ../../scripts/harnessctl.py validate-operations PLAN.json`.
