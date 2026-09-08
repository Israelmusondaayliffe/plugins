---
name: practice-compiler
description: Mines an exact Codex session window for repeated tasks, recurring feedback, follow-up instructions, failed commands, and reusable workflows, then stages semantically grouped, redacted proposals with session-and-line evidence. Use when a user asks what their sessions reveal, what should become a skill or workflow, what feedback keeps recurring, or what follow-up instructions they repeatedly add. Supports read-only stdout preview and source classification. Does not change the harness, publish content, or replace Codex Mem.
---

# Practice Compiler

Route the request to one phase. The safe compounding loop is scan, review, decide, then hand off. The scanner never performs the destination change.

## Router

- Scan recent sessions or find repeated friction: read `../session-signal-scan/SKILL.md` and `agents/agent-scan.md`.
- Group, rank, explain, approve, or reject proposals: read `../practice-proposal-review/SKILL.md` and `agents/agent-review.md`.
- Prepare an approved destination handoff: read `../approved-practice-handoff/SKILL.md` and `agents/agent-handoff.md`.
- End-to-end request: read-only scan, proposal review, explicit decision, then handoff record.

## Gates

- Select exact source roots and a bounded time window. Automation, subagent, and synthetic traces require explicit selection.
- Persist only redacted snippets and source references.
- Require repeated evidence before staging by default.
- Use an exact `--since` and `--until` window for time-bounded reviews.
- Prefer `--stdout` for an approval-stage review that must not change scanner state.
- Approval authorizes a handoff record, not the destination mutation.
- A schedule may run the scan and staging phases only.

Load `references/ownership-and-routing.md` when the destination owner is unclear.

## Selected-source learning

For cross-host learning or neutral Design exports, load `../active-practice-learning/SKILL.md`. A scan requires an exact `--sessions-root`, explicit `--adapter codex` or `--adapter claude`, and `--since`/`--until`. Use `--stdout` for a read-only scan. Never select a user's entire host history implicitly.

For a question about learning ownership or a single supplied lesson, answer from the supplied material. Do not inspect sessions, write a proposal, save memory or change a destination unless that action was requested. A handoff approval authorizes the handoff record only.
