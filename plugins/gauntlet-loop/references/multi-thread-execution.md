# Multi-Thread Execution

Distinguish three surfaces:

- subagent threads inside the current task;
- user-owned Codex tasks or chats;
- resumed or forked sessions.

Default parallelism uses bounded subagent threads. Creating separate user-owned tasks requires explicit user approval, a named thread plan, and a callable task-management surface.

For every parallel unit:

- declare purpose, inputs, outputs, quality bar, dependencies, evidence, and integration owner;
- assign disjoint write targets or a separate worktree;
- preserve parent sandbox and approval limits;
- cap concurrency at the live host limit;
- batch verifier panels when slots are limited.

The lead remains responsible for integration and cannot treat subagent summaries as substitutes for real artifacts.
