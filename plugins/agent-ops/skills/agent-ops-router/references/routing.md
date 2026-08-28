# Agent operations routes

- agent-design: define a reusable agent, its contract, tools, authority, and verification.
- audit: assess an existing agent system without changing it.
- loopkit-handoff: route generic Goals, bounded loops, execution, verification, resume, schedules, and runtime diagnosis on Claude Code, Claude Cowork, or Codex. Use the optional `loopkit:loopkit` companion when available. When it is absent and Agent Ops was explicitly selected, use the bundled local fallback: goal-runner for contract, execution, verification, and resume; loop-goal-engineer for design, scheduling, and diagnosis; loopy for Loop Library and local-loop workflows.

Agent Ops owns reusable agent-system design, routing, and audit. LoopKit and Outcome Engine are optional companions that keep their own domains when installed. Their absence does not reduce Agent Ops design, audit, or explicit local fallback capability. The parent retains the user's outcome and work-first definition of done across every route.
