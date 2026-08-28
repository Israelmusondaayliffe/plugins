# Continuity Routing Workflow

Use one primary route per handoff.

| Route | Use when | Primary skill or companion | Required evidence |
| --- | --- | --- | --- |
| `handoff` | A fresh task or delegated slice must continue without conversation history | `continuity-router` plus `task-handoff.md` | Source paths, current state, decisions, proof, open risks, next action |
| `extract` | A task or source contains reusable decisions, procedures, or evidence | `frontier-extraction` | Source path or stable identifier |
| `promote` | Extracted knowledge needs a durable destination decision | `knowledge-promotion-policy` | Source, authority, reuse case, owner |
| `graph` | Relationships across sources are more important than linear notes | `graphify` | Named nodes and source-backed relationships |
| `search` | Prior context may exist but its location is unknown | Memory or Chronicle when available; bounded `continuity-router` local fallback otherwise | Query, exact authorized roots, authority checks, matches, and later source verification |
| `audit` | Claims, instructions, or references may be stale or conflicting | `staleness-and-conflict-audit` | Compared sources and review date |
| `digest` | A bounded set of sources needs a concise continuity summary | `frontier-extraction` plus an optional writing companion; direct local digest otherwise | Closed source set, source hashes, evidence excerpts, and audience |

Authority order is the active instruction chain (the `CLAUDE.md` chain on Claude Code / Cowork, the `AGENTS.md` chain on Codex), then project and workspace source files, then derived artifacts. Memory and Chronicle are recall surfaces and cannot settle a load-bearing conflict by themselves.

## Local fallback boundary

- Search only exact workspace roots the user authorized in the current task. Filesystem access does not grant search authority.
- Record every root searched, the literal query, authority statement, authority checks, and each match.
- Return `no-evidence` when a bounded search finishes or a closed digest source set produces no evidence. Return `search-incomplete` when a search bound is reached before completion.
- Keep Notion and Google Drive optional and source-owned. Do not treat a local fallback as permission to read or copy either source.
- A direct digest may use exact local source excerpts without a writing companion. Bind every claim to a source path and keep gaps explicit.
- Never promote, overwrite, delete, or resolve conflicting material without separate authority.
