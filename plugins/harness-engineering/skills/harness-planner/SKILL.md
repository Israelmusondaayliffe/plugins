---
name: harness-planner
description: Turn a confirmed harness profile and read-only audit into a decision-complete architecture and reversible operation plan for Claude Code, Claude Cowork, or Codex. Use when a user asks for a harness plan, implementation plan, workspace blueprint, capability plan, migration plan, or wants to see exact proposed changes and checks before any global, folder, or project files are edited.
---

# Harness Planner

Plan the outcome, scopes, operations, approvals, evidence, and rollback. Leave no implementation decisions unresolved.

## Workflow

1. Require a confirmed profile and current audit, or record why one is not applicable. The profile names the platform; plan only surfaces that exist there per its platform file.
2. Design the information, execution, and feedback layers.
3. Put each requirement in the narrowest durable scope. On Cowork, durable means a connected folder, app-level instructions, or an external system, never the session sandbox.
4. Reuse installed capabilities before proposing a new skill or plugin.
5. Prefer scripts, rules, hooks, sandbox settings, and templates when behavior must be exact, within what the platform supports.
6. Define separate approval groups using `../../references/safety-and-approvals.md`.
7. Generate file previews, operations, expected hashes, checks, failure stops, and rollback actions.
8. For prompt work, define a frozen baseline, fixed evaluation conditions, delta-only overlays, front-door route gates, reversible waves, and post-install acceptance.
9. Treat word or token ceilings as soft diagnostics. Behavioral acceptance wins.
10. Present the human plan and machine operations together.
11. Do not begin implementation until the user accepts the plan or explicitly requests end-to-end execution.

Start from `../../assets/harness-plan.template.json`. Validate it with `python3 ../../scripts/harnessctl.py validate-operations PLAN.json`.
Follow `../../references/frontier-first-prompt-governance.md` for subtraction, invocation-policy, or skill-compaction plans.
