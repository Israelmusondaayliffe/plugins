---
name: loopy
description: Explicit-only compatibility shim for the historical Loopy name. Use only when the user explicitly says Loopy or asks for the Loop Library workflow. Use LoopKit as an optional companion when available; otherwise use the bundled local design, run, verification, resume, diagnosis, and Loop Library workflows. Generic requests do not activate this historical name.
metadata:
  author: Community Maintainers
  version: 1.1.0-compat
---

# Loopy compatibility shim

LoopKit is the preferred optional companion for generic loop work on Claude Code, Claude Cowork, and Codex.

When LoopKit is available, route the explicit Loopy request as follows:

- Craft or adapt a local loop: `loopkit:loop-designer`.
- Run it: `loopkit:loop-runner`.
- Audit it: `loopkit:loop-doctor` or `loopkit:loop-verifier` according to whether the target is design or completion.
- Resume it: `loopkit:loop-resumer`.

When LoopKit is absent, complete the explicit request with the bundled local fallback:

- Use `references/run.md` for a bounded run or resume from the exact loop definition and latest available receipt.
- Use `references/audit.md` for design diagnosis and verification, `references/debrief.md` for runtime evidence, and `references/discover.md` for recurring-work discovery.
- For craft or adaptation work, require a feedback cycle that observes fresh state, chooses one bounded action, verifies it with reproducible evidence, records the result, and enters a named terminal state. Return a one-shot workflow when fresh feedback cannot change the next action.
- Before delivery, confirm scope, approval boundaries, reproducible verification, and success, blocked, approval-required, and no-progress stops where relevant. Do not invent tools, schedules, limits, metrics, owners, or permissions.
- Use `references/publish.md` for Loop Library work. Publication still requires a live catalog check, an exact preview, and explicit approval for the external submission.

Do not create parallel local state. In local fallback mode, resume from existing authorized state or return the compact receipt described in `references/run.md`. Keep historical state read-only as migration evidence. The fallback keeps the same safety and verification standard.

This historical compatibility identity remains explicit-only while Agent Ops bundles it.
