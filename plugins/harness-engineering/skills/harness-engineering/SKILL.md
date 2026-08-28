---
name: harness-engineering
description: Design, build, verify, or maintain a personalized AI operating harness on Claude Code, Claude Cowork, or Codex from a vague brief or an existing setup. Use when a user asks for an operating system for their AI, a harness, a CLAUDE.md or AGENTS.md chain, Cowork contract files, workspace architecture, capability stack, guided setup, harness upgrade, or an end-to-end workflow combining interview, audit, planning, reversible implementation, and verification. Route focused requests to the owned skill that matches the current phase.
---

# Harness Engineering

Build the smallest harness that satisfies the user's real work. Treat the user's existing files and live environment as implementation truth.

On Claude 5 generation models the common defect in an inherited harness is over-constraint, not absence. Read `../../references/claude5-context-doctrine.md` before writing or judging any persistent context, and prefer removing an instruction to adding one.

## Platform first

Resolve the target platform (Claude Code, Claude Cowork, or Codex) using `../../references/platform-matrix.md` before any phase. The principles are shared; the surfaces are not. Name the platform in every profile, plan, and receipt. A user running more than one platform gets one harness scope per platform, never a copy-paste between them.

## Route

1. Vague or incomplete brief: load `harness-interview`.
2. Existing setup or upgrade request: load `harness-audit` before planning.
3. Confirmed profile plus audit: load `harness-planner`.
4. Instruction-file work only (CLAUDE.md, AGENTS.md, Cowork contract files): load `agents-md-engineer`.
5. Approved file operations: load `harness-builder`.
6. Missing reusable skill: load `skill-engineer`.
7. Missing distributable bundle: load `plugin-engineer`.
8. Model-specific prompt work: load `model-prompt-engineer`.
9. Sustained approved build: load `harness-runner`.
10. Completion claim: load `harness-verifier`.
11. Affirmative Unslop repair of a harness or approved plugins: load `unslop-harness-repair`.
12. Drift or update work: load `harness-maintainer`. When that maintenance may change human-facing harness prose, the maintainer also loads `unslop-harness-repair` as its bounded repair specialist.
13. Over-constrained or inherited context: load `context-doctor` before rewriting anything.

For an end-to-end request, use this order: interview, audit, plan, approve, run, verify, hand off.

## Contract

- Investigate before asking factual questions.
- For build, change, cleanup, and implementation requests, execution against the target is the primary work; exploration, plans, tests, receipts, critics, and reports are support and count as progress only when they directly enable or verify a requested target-state change. Unresolved required work blocks completion.
- Keep audit and planning read-only.
- Present the complete plan and operation groups before changing files.
- Back up every existing file before an approved update.
- Do not install third-party code, trust hooks, authenticate accounts, or publish externally without separate approval.
- Require fresh evidence before completion.

Read `../../references/harness-architecture.md` for scope placement, `../../references/frontier-first-prompt-governance.md` for context reduction or capability-catalog work, and `../../references/safety-and-approvals.md` before any mutation.
