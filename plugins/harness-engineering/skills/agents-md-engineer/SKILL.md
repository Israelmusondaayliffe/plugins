---
name: agents-md-engineer
description: Design, rewrite, split, or verify agent instruction files across scopes on any supported platform, a CLAUDE.md chain for Claude Code, contract files at connected-folder roots for Claude Cowork, or an AGENTS.md chain for Codex. Use when users ask what belongs in CLAUDE.md or AGENTS.md, want instructions modeled on an existing harness, need shorter or clearer agent guidance, have conflicting instruction files, or need templates that encode role, boundaries, routing, workflow, and verification.
---

# Instruction File Engineer

Keep instruction files short, accurate, durable, and scoped to the directories that need them. The engineering discipline is identical across platforms; the file names, load order, and import mechanics are not. Read the platform file first.

## Workflow

1. Resolve the platform and its chain: CLAUDE.md precedence and `@` imports on Claude Code, app instructions plus folder contract files on Cowork, AGENTS.md scopes on Codex.
2. Inspect the applicable chain and any override files.
3. Identify repeated behavior that truly belongs in persistent instructions.
4. Move detailed workflows into skills or references and exact checks into scripts, rules, hooks, or templates.
5. Separate global personal policy from workspace layout and project commands.
6. Preserve existing load-bearing rules and show a diff for updates.
7. Verify that closer files refine rather than silently contradict broader guidance. On Cowork, also verify the global instructions actually direct Claude to read the folder contract, since folder files do not load themselves.

Use the templates under `../../assets/`: `global-claude`, `project-claude`, and `cowork-contract` for Claude platforms, the three `agents` templates for Codex. Replace every bracketed placeholder. Do not copy the advanced case study as a default.

Use a compact context kernel for stable cross-task policy and delta-only workspace or project overlays. Keep front-door ownership cues only when they are load-bearing for routing. Treat size ceilings as diagnostics and accept subtraction only against a frozen behavior suite.

For measured context reduction, follow `../../references/frontier-first-prompt-governance.md`.
