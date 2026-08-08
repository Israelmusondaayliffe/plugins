---
name: goal-runner
description: Explicit-only compatibility shim for the historical Goal Runner name. Use only when the user explicitly says goal-runner or Goal Runner. Redirect Goal contract, execution, verification, and resume work, on Claude Code, Claude Cowork, or Codex, to the matching LoopKit skill. Generic goal or completion requests should trigger LoopKit directly.
metadata:
  author: Community Maintainers
  version: 1.2.0-compat
---

# Goal Runner compatibility shim

This historical name remains available through Agent Ops 0.3.x. LoopKit now owns generic Goal and loop execution on Claude Code, Claude Cowork, and Codex.

Route the explicit request as follows:

- Create or reshape a Goal contract: `loopkit:loop-designer`.
- Execute a ready Goal contract: `loopkit:loop-runner`.
- Check a completion claim: `loopkit:loop-verifier`.
- Continue interrupted work: `loopkit:loop-resumer`.
- Multi-stage or ambiguous work: `loopkit:loopkit`.

Use LoopKit's state root, receipt validator, checkpoint hooks, and terminal-state rules. Do not create a separate Goal Runner state format. Preserve any existing historical contract and progress files as read-only migration evidence, then initialize a LoopKit run only with the user's requested goal and boundaries.

This shim is scheduled for removal in Agent Ops 0.4.0 after LoopKit reaches 0.2.0.
