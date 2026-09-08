# Agent Ops

Agent Ops packages reusable agent design, agent-system routing, and agent-system audit for Claude Code, Claude Cowork, and Codex. The design principles are shared across hosts; the subagent surfaces are not. On Claude Code and Cowork, subagents are `agents/*.md` files dispatched via the Agent tool. On Codex, subagents are named `[agents.<name>]` blocks in `config.toml` driven by lifecycle verbs.

## Owned skills

- agent-ops-router
- astra-advisor (explicit-only; GPT 6 Astra parent, workers and review)
- fable-advisor (explicit-only; Fable 5.1 parent, native workers and review, with an explicitly selected Codex worker option)
- sol-advisor (legacy public packet compatibility)
- agent-system-audit
- agent-builder
- goal-runner (explicit-only historical compatibility shim with an optional LoopKit handoff)
- loop-goal-engineer (explicit-only historical compatibility shim with an optional LoopKit handoff)
- loopy (explicit-only historical compatibility shim with an optional LoopKit handoff)

Generic Goals and loops normally route to LoopKit when that optional companion is available. If it is absent, an explicit Agent Ops request uses the bundled local fallback. The three historical names keep their explicit-only activation boundary.

## Optional companion capabilities

Agent Ops does not require a sibling plugin for reusable agent design, audit, or its local compatibility fallback.

- Outcome Engine can handle general idea-to-result delivery when installed.
- LoopKit can handle generic Goals, bounded loops, verification, resume, scheduling, and runtime diagnosis on any host when installed.
- ProofLoop can add bounded evidence and learning checks when installed.
- Superpowers can add composable development workflows when installed.
- Plugin Eval can add trigger and bundle evaluation when installed.

## Boundaries

- Agent Ops owns reusable agent-system design and audit. Optional companions keep their own domains when installed, but their absence does not narrow Agent Ops capability.
- Missing authority, evidence, or stop conditions blocks autonomous execution.
- Audits remain read-only unless a repair is separately requested.

## Verification

Run scripts/verify_bundle.py and validate each skill. Scenario tests must cover agent design, audit, the optional LoopKit handoff, and the local fallback.

## Advisor isolation

Start Astra Advisor or Fable Advisor only when explicitly requested. Fable Advisor and Gauntlet are mutually exclusive. Native Fable workers use `fa-worker`; independent reviews use `fa-verifier`. Keep Codex lifecycle tooling and Claude agent files separate. Model configuration and protocol tests do not prove runtime availability on another installation.
