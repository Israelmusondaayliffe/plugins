# Optional Agent Ops compatibility window

LoopKit owns generic goal and loop design (Codex Goals or Claude Code `/goal`), execution, verification, resume, scheduling, and diagnosis on Claude Code, Claude Cowork, and Codex.

Some installations include Agent Ops compatibility shims named `goal-runner`, `loop-goal-engineer`, and `loopy`. When present, those explicit-only shims may hand generic host-platform work to the matching LoopKit skill while retaining their historical names. LoopKit does not require Agent Ops or those shims.

Fresh generic requests route directly to LoopKit. An explicit request for an installed legacy shim may still load that shim. Agent Ops owns the lifecycle of its optional compatibility identities.
