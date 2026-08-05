---
name: agent-builder
description: Build agents and agentic workflows for Claude Code, Claude Cowork, and Codex from a plain task description. ARCHITECT selects the simplest suitable pattern. WORKFLOW builds concrete workflow artifacts. AGENT creates autonomous agents with ground-truth verification, stop conditions, pause points, and host-specific definitions. ACI designs safer tool interfaces and parameters. REVIEW critiques an existing agent setup. Built agents inherit the active host instruction chain and output discipline. Use for agent architecture, subagents, multi-agent systems, orchestrator-worker designs, prompt chains, evaluator-optimizer loops, agent review, or tool-interface design.
metadata:
  author: Community Maintainers
  version: 1.1.0
---

# Agent Builder

Turn "I want an agent that does X" into a working agent design and its concrete artifacts for Claude Code, Claude Cowork, or Codex.

The framework this skill encodes, from Anthropic's Building Effective Agents: the most successful implementations use simple, composable patterns, not complex frameworks. Every design starts at the bottom of the simplicity ladder and climbs only when the step demonstrably improves outcomes. Agentic systems trade latency and cost for task performance, and that trade is made consciously, never by default.

## Router Logic

Assess the request and route. Load only the agent you route to.

**ARCHITECT** -> Load `agents/agent-architect.md`
Triggers: any fresh "build me an agent for X" where the pattern is not yet chosen. This is the default entry point. Every new build passes through ARCHITECT first, even when the user names a pattern, because the doc's core finding is that people over-build. ARCHITECT ends with a chosen pattern and hands off.

**WORKFLOW** -> Load `agents/agent-workflow.md`
Triggers: pattern already chosen (by ARCHITECT or explicitly by the user) and it is one of the five workflow patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.

**AGENT** -> Load `agents/agent-autonomous.md`
Triggers: pattern chosen is a true autonomous agent (open-ended, unpredictable step count), or the user asks for a subagent definition (a Claude Code or Cowork agents/*.md file, a Codex config.toml agent block), a persistent agent definition, or "an agent that runs on its own."

**ACI** -> Load `agents/agent-aci.md`
Triggers: "design the tools", "write tool definitions", "my agent keeps misusing the tool", MCP tool surface design, parameter naming, or any request focused on the agent-computer interface rather than the agent itself.

**REVIEW** -> Load `agents/agent-review.md`
Triggers: user pastes or points at an existing agent setup (subagent files, orchestration prompts, CLAUDE.md, AGENTS.md, tool definitions) and wants critique, debugging of agent behavior, or "why is my agent flaky."

## The Simplicity Ladder (governs every route)

1. Single optimized LLM call with retrieval and in-context examples. Usually enough. Always the first candidate.
2. Workflow pattern (predefined code paths, predictable): chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.
3. Autonomous agent (model directs its own process): only for open-ended problems where steps cannot be predicted or hardcoded, and trust in model decisions is justified.

Never deliver a rung-3 design when rung 1 or 2 solves the task. Say so plainly when the user asks for an agent they do not need.

## Target Tool Handling

Default target is Claude Code. Claude Cowork uses the same Claude artifact shapes, delivered through plugins, with the platform caveats in target-formats.md. If the user says Codex, target the Codex app and CLI. Artifact formats per host live in `references/target-formats.md`, load it before emitting any final artifact. Two per-target rules that always apply: Codex-bound prompts (GPT-5.5 targets) are outcome-first (outcome, criteria, constraints, never step-by-step procedure), a rule that does not apply to Claude-bound prompts, and every built agent inherits the user's operating harness when one exists (contract chain layers, single dated write destination, validators, four-phase workflow), duplicating none of it. When the built system needs a /goal or /loop to run (schedules, autonomous sessions, orchestrator kickoff messages), compose with the loop-goal-engineer skill if it is available rather than hand-writing those prompts.

## Shared Output Contract

Every route delivers:

1. One line naming the mode, chosen pattern, and target tool.
2. Short reasoning: why this pattern and not the simpler rung below it, what the ground truth is, where the humans pause it.
3. The artifacts, each in its own triple backtick code block, each labeled with its destination path (e.g. `.claude/agents/reviewer.md`, `AGENTS.md` section, system prompt).
4. A one-line test note: how to sandbox-test before trusting it, because errors compound in agentic systems.

Formatting rules baked into every artifact: no em-dashes (period or comma instead), no emojis, plain language, concrete paths, explicit numbers for caps and retries.

## Validation Gate

Before delivering any autonomous agent or orchestration design, run:

```bash
python scripts/validate_agent.py <file-with-design> --kind agent|workflow|subagent
```

It checks the non-negotiables: stopping conditions (max iterations or budget), ground-truth verification (tool results or code execution, never self-report), success criteria, and human pause points for agent kind; frontmatter shape for subagent kind; gate presence for workflow kind. Fix failures and re-run before delivering.

## Shared Resources

- `references/patterns.md` Workflows vs agents, the augmented LLM building block, all five workflow patterns with use-when tests and examples. Load in ARCHITECT, WORKFLOW, REVIEW.
- `references/autonomous-agents.md` Agent mechanics, the ground truth rule, stopping conditions, pause points, proven domains, the three core principles. Load in AGENT, REVIEW.
- `references/aci-design.md` Tool prompt engineering, format rules of thumb, the tool design checklist, poka-yoke. Load in ACI, and in AGENT when the agent gets custom tools.
- `references/target-formats.md` Claude Code and Cowork subagent file format and Agent-tool dispatch, CLAUDE.md chain and skills placement, Codex AGENTS.md chain and config.toml agent blocks, and the CLI translation table (chaining = phase gates, parallelization = worktrees, evaluator-optimizer = grader loops). Load before emitting artifacts in any mode.
- `assets/agent-spec-template.md` The design spec every build fills before artifacts are written.
- `assets/subagent-template.md` Claude Code and Cowork subagent file skeleton.

## Error Recovery

If the task has no clear success criteria and no feedback loop, agents add little value there (the doc is explicit: agents shine where success is checkable and feedback exists). Say so, and offer the strongest rung-1 or rung-2 alternative instead. If required information about the user's environment is genuinely missing (repo layout, available tools, which CLI), ask one focused question, not three.
