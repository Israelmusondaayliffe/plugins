---
name: goal-runner
description: Explicit-only compatibility shim for the historical Goal Runner name. Use only when the user explicitly says goal-runner or Goal Runner. Use LoopKit as an optional companion when available; otherwise use this skill's bundled local contract, execution, verification, and resume tools. Generic requests do not activate this historical name.
metadata:
  author: Community Maintainers
  version: 1.2.0-compat
---

# Goal Runner compatibility shim

LoopKit is the preferred optional companion for generic Goal and loop execution on Claude Code, Claude Cowork, and Codex.

When LoopKit is available, route the explicit request as follows:

- Create or reshape a Goal contract: `loopkit:loop-designer`.
- Execute a ready Goal contract: `loopkit:loop-runner`.
- Check a completion claim: `loopkit:loop-verifier`.
- Continue interrupted work: `loopkit:loop-resumer`.
- Multi-stage or ambiguous work: `loopkit:loopkit`.

When LoopKit is absent, complete the explicit request with the bundled local fallback:

- Load `references/completion-doctrine.md` and `references/environments.md`.
- Create a new versioned contract and progress pair with `scripts/init_run.py` only when execution or resume needs durable state.
- Validate the contract with `scripts/verify_contract.py` before execution and at the completion check.
- Use the bundled agent roles for contract shaping, execution, fresh verification, and resume when the host supports them. Use the documented degraded check when it does not.

Do not lower the acceptance standard in fallback mode. Reuse an active compatible contract instead of creating duplicate state. Keep pre-existing historical contract and progress files read-only as migration evidence. The initializer refuses to overwrite an existing version.

This historical compatibility identity remains explicit-only while Agent Ops bundles it.
