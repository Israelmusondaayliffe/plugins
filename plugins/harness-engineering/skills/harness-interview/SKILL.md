---
name: harness-interview
description: Conduct a persistent, source-first interview that converts a user's incomplete harness idea into a confirmed profile for Claude Code, Claude Cowork, or Codex. Use when the user says grill me, interview me, design my harness, set up Claude Code or Cowork or Codex for me, ask what I need, or gives a thin brief whose answers could change global instructions, contract files, workspace structure, permissions, skills, plugins, connectors, verification, or maintenance.
---

# Harness Interview

Treat the interview and confirmed profile as the deliverable. Do not build during this phase.

## Workflow

1. Resolve the target platform first using `../../references/platform-matrix.md`. If the user runs several, interview for one primary platform and record the others as separate scopes.
2. Inspect authorized existing files and capability state before asking discoverable facts.
3. Establish the root outcome, users, work types, constraints, and largest unresolved dependency.
4. Follow the decision tree in `../../references/interview-tree.md` one branch at a time, interpreting each branch through the platform file for the resolved platform.
5. Ask one to three linked questions. Offer a recommended default and its main tradeoff when evidence supports one.
6. Define important harness terms before dependent choices use them. Record each answer as fact, constraint, preference, assumption, or decision, keeping only records that change the profile.
7. Pressure-test authority, failure modes, maintenance, portability, and proof.
8. Run a convergence check: all material branches are resolved, discoverable from a named source, explicitly excluded, or deferred with an owner or revisit trigger. Present the complete working model and request correction.
9. Save a schema-versioned profile only after confirmation. Record the platform in the profile scope.

## Profile requirements

Include user context, target platform, intended scope, workspace choice, project pattern, data sources, capability needs, authority boundaries, verification expectations, maintenance ownership, exclusions, accepted assumptions, and deferred decisions.

Validate saved profiles with `python3 ../../scripts/harnessctl.py validate-profile PROFILE.json`.

When a confirmed profile must continue in a fresh task, route the durable handoff to Continuity Vault. The handoff does not authorize a build.
