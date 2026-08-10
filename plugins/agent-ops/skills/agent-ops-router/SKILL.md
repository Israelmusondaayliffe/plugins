---
name: agent-ops-router
description: Route reusable agent-system requests among agent design and agent-system audit. Use when a user asks to build a reusable agent, define an agent tool contract, choose an agent architecture, or audit an agent system's authority and stops. Generic Goals, bounded loops, resume, verification, and schedules, on Claude Code, Claude Cowork, or Codex, route to LoopKit.
---

# Agent Ops Router

## Overview

Select the operational object before choosing a skill. Reusable agent systems need explicit authority, tools, stops, evidence, and failure behavior.

## Workflow

1. Determine whether the user is designing or auditing a reusable agent system.
2. Choose one primary route with references/routing.md.
3. Complete assets/route-template.json and run scripts/validate_route.py.
4. Load only the route owner:
   - agent-design: agent-builder
   - audit: agent-system-audit
5. Route generic Goal or loop work, on any host (Claude Code, Claude Cowork, or Codex), to `loopkit:loopkit`.
6. Preserve the user's outcome contract across every route. Explicit Agent Ops selection chooses the operating method, not the definition of done.
7. Use Outcome Engine only when the request is a general idea-to-result workflow rather than an agent operating system.
8. Verify the chosen route names a target-state delta, unresolved count, evidence surface, total run budget, boundaries, and stop condition.

## Error Handling

- If two agent routes apply, choose a primary route and list the secondary handoff.
- If the request is about a run, resume, recurring task, or scheduled task rather than an agent definition, hand off to LoopKit.
- If authority or stop conditions are absent, do not start an autonomous loop.
- Choose the smallest finite worker set. Available topology slots are not mandatory launches.

## Reliability Notes

The model classifies the operating object. The validator enforces an allowed Agent Ops route or an explicit LoopKit handoff plus the four required control fields.

## Resources

- scripts/validate_route.py validates routing records.
- references/routing.md defines boundaries.
- assets/route-template.json provides the record.
