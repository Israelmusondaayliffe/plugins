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

## Bounded local fallback

Use this fallback only when the selected recall or writing companion is unavailable.

For local recall:

1. Ask for or reuse only the exact workspace roots the user authorized in the current task. Do not infer authority from filesystem access, the home directory, sibling projects, or prior tasks.
2. Run `scripts/local_fallback.py search` with each authorized root, the query, and the current authority statement. The helper rejects the filesystem root, the home directory, symlink roots, missing roots, and implicit searches.
3. Return the helper record with the query, roots searched, authority checks, and matches. Treat `no-evidence` as the result only when the bounded search finishes with no match. If a bound stops the search, return `search-incomplete`. Do not invent recall or widen the search.

For a direct digest:

1. Close the source set to exact files inside the authorized roots. Notion and Google Drive remain optional and source-owned. Read them only through their own authorized surfaces, then include a local exported file only when the task permits it.
2. Run `scripts/local_fallback.py digest` with the closed source set and audience. The helper records source hashes and exact excerpts without using a writing companion.
3. Build the concise digest only from that evidence. Cite the source path for each claim, distinguish evidence from gaps, and return `no-evidence` when the closed source set contains no usable text.

The fallback is read-only. It never promotes, overwrites, deletes, writes a companion, or resolves conflicts without separate authority.

## Error Handling

- If the source cannot be named, stop before promotion.
- If two instruction layers conflict, route to a conflict audit and preserve both sources.
- If a destination is outside the approved boundary, recommend it without writing.
- If a requested local root was not explicitly authorized in the current task, stop before search.

## Reliability Notes

The model selects a route and explains why. The validator enforces a named source, authority layer, route, rationale, and false destructive-action flag.
