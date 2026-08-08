# Continuity Routing Workflow

Use one primary route per handoff.

| Route | Use when | Primary skill or companion | Required evidence |
| --- | --- | --- | --- |
| `handoff` | A fresh task or delegated slice must continue without conversation history | `continuity-router` plus `task-handoff.md` | Source paths, current state, decisions, proof, open risks, next action |
| `extract` | A task or source contains reusable decisions, procedures, or evidence | `frontier-extraction` | Source path or stable identifier |
| `promote` | Extracted knowledge needs a durable destination decision | `knowledge-promotion-policy` | Source, authority, reuse case, owner |
| `graph` | Relationships across sources are more important than linear notes | `graphify` | Named nodes and source-backed relationships |
| `search` | Prior context may exist but its location is unknown | Memory or Chronicle companion | Query plus later authority check |
| `audit` | Claims, instructions, or references may be stale or conflicting | `staleness-and-conflict-audit` | Compared sources and review date |
| `digest` | A bounded set of sources needs a concise continuity summary | `frontier-extraction` plus writing companion | Closed source set and audience |

Authority order is the active instruction chain (the `CLAUDE.md` chain on Claude Code / Cowork, the `AGENTS.md` chain on Codex), then project and workspace source files, then derived artifacts. Memory and Chronicle are recall surfaces and cannot settle a load-bearing conflict by themselves.
