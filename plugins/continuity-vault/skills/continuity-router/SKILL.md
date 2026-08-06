---
name: continuity-router
description: Routes continuity work across durable task handoffs, extraction, durable-file promotion, knowledge graphs, memory search, staleness audits, and digests. Use when work from tasks, delegated slices, projects, or research must remain usable and trustworthy across future Claude Code, Claude Cowork, or Codex sessions. Keeps workspace files as authority, treats memory and Chronicle as recall only, and does not overwrite or delete source material.
---

# Continuity Router

## Overview

Choose the continuity operation before moving information. Preserve provenance and keep the source closest to the work as the authority.

## Workflow

1. Identify the source, project, authority layer, intended future use, and allowed write boundary.
2. Select one primary route using `references/workflow.md`.
3. Use `references/task-handoff.md` and `assets/task-handoff-template.md` for a fresh-task or delegated-slice handoff, `frontier-extraction` for durable extraction, `knowledge-promotion-policy` for destination decisions, `graphify` for relationship mapping, and `staleness-and-conflict-audit` for trust checks.
4. Use memory or Chronicle only to find likely context. Recheck load-bearing facts against authoritative files.
5. Fill `assets/output-template.json` and run `scripts/validate_output.py`.
6. Return a bounded handoff. A handoff records authority and evidence but grants no new authority. Do not move, overwrite, delete, or promote material without the task's existing write authority.

## Error Handling

- If the source cannot be named, stop before promotion.
- If two instruction layers conflict, route to a conflict audit and preserve both sources.
- If a destination is outside the approved boundary, recommend it without writing.

## Reliability Notes

The model selects a route and explains why. The validator enforces a named source, authority layer, route, rationale, and false destructive-action flag.
