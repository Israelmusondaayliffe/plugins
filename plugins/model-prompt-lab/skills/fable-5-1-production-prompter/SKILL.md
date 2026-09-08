---
name: fable-5-1-production-prompter
description: Prepare, migrate and diagnose Claude Fable 5.1 prompts using current owner documentation, the task’s evidence and a bounded validation. Use when Fable 5.1 is the selected model; keep older Fable 5 guidance as explicit compatibility.
---

# Fable 5.1 Production Prompter

Confirm the target host exposes `claude-fable-5-1` before executing. Read [Anthropic’s Fable 5.1 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) and [model overview](https://platform.claude.com/docs/en/models/fable-5-1/overview) for API controls and current availability.

Preserve the user’s job, output contract, sources and authority. Start from an existing prompt when supplied. Diagnose the observed failure before adding instructions. Test effort against the task; do not impose the publisher’s preferred model settings on other users.

For long tool runs, make useful progress updates visible and batch independent calls. Keep API history append-only. Ask for targeted file edits, readable prose and source-attributed quotations when those are the observed gaps. Keep changes and tests inside the requested scope.

Return the complete prompt in its own code block, with only material assumptions and verification limits outside it. Do not copy private histories, benchmark receipts, voice guides or account configuration. A source guide is documentation, not proof that a prompt succeeds on the user’s task.
