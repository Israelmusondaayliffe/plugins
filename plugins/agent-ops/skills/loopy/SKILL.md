---
name: loopy
description: Explicit-only compatibility shim for the historical Loopy name. Use only when the user explicitly says Loopy or asks for the Loop Library workflow. Redirect generic loop design, run, verification, resume, and diagnosis, on Claude Code, Claude Cowork, or Codex, to LoopKit. Retain the bundled legacy references only for an explicitly requested Loop Library discovery or publication task.
metadata:
  author: Community Maintainers
  version: 1.1.0-compat
---

# Loopy compatibility shim

This historical name remains available through Agent Ops 0.3.x. LoopKit owns generic loop work on Claude Code, Claude Cowork, and Codex.

For an explicit Loopy request, route generic work as follows:

- Craft or adapt a local loop: `loopkit:loop-designer`.
- Run it: `loopkit:loop-runner`.
- Audit it: `loopkit:loop-doctor` or `loopkit:loop-verifier` according to whether the target is design or completion.
- Resume it: `loopkit:loop-resumer`.

If the user explicitly requests Loop Library discovery, debrief, save, or publication, the existing files under this skill's `references/` remain the compatibility source. Publication still requires a live catalog check, an exact preview, and explicit approval for the external submission.

Do not create parallel local state. Use LoopKit receipts and checkpoints for any executed run.

This shim is scheduled for removal in Agent Ops 0.4.0 after LoopKit reaches 0.2.0.
