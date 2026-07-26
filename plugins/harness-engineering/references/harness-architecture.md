# Harness Architecture

## Three operating layers

1. Information: instructions, context, skills, tools, connectors, project references, and memory.
2. Execution: workspace boundaries, plans, autonomous runs, scripts, rules, hooks, approvals, and recovery.
3. Feedback: checks, receipts, reviews, failure records, maintenance, and model-change audits.

A useful harness is balanced across all three. Do not compensate for missing verification by adding more instructions.

## Scope hierarchy

Platform file names differ (see `platform-matrix.md`); the hierarchy does not:

- Thread prompt: one task.
- Global instruction layer: personal defaults that apply everywhere. `~/.claude/CLAUDE.md` on Claude Code, app-level global instructions on Cowork, global `AGENTS.md` on Codex.
- Workspace layer: shared layout, routing, and output rules. Workspace `CLAUDE.md` or `AGENTS.md`, or the contract files at a Cowork connected-folder root.
- Project or nested layer: the closest project-specific commands, constraints, and verification rules.
- Skill: a repeatable workflow with optional references, scripts, or assets.
- Plugin: a distributable bundle of skills and optional tools or lifecycle components.
- MCP or connector: live external data or actions.
- Hook, rule, or script: deterministic enforcement, where the platform supports it.

Put a requirement in the narrowest scope that must always see it.

## Reliability order

Prefer the least-free mechanism that fits:

1. Script
2. Command rule
3. Hook
4. Sandbox or permission setting
5. Template
6. Prompt instruction
7. Instruction file
8. Inference

Repeated corrections should move toward deterministic enforcement. On platforms without hooks (Cowork), the ladder compresses: scripts run by contract become the top rung.

## Context architecture

Model-visible instructions are a compact context kernel plus delta-only overlays. Personal plugin front doors remain in default context. Specialists, detailed workflows, examples, and recovery guidance load from their task-owned files. Exact behavior belongs in deterministic mechanisms whenever possible.

Prompt size is a diagnostic, not an acceptance criterion. Freeze behavior before subtracting instructions and keep only reductions that preserve authority, routing, stopping, formatting, and verification. Use `frontier-first-prompt-governance.md` for the full evidence and rollout contract.
