# Durable task handoff

Use this route when a fresh task or delegated slice must continue without relying on hidden conversation state.

1. Read the actual source files and current evidence. Do not reconstruct state from memory alone.
2. State the objective and exact boundary of work already authorized.
3. Separate completed, current, blocked, and not-started work.
4. Record decisions that constrain the next task, with reasons and source paths.
5. Link the latest proof and state what it does and does not establish.
6. Name user-owned or external actions that remain unapproved.
7. Provide one first action that can be taken from the handoff itself.
8. Run a cold-read check: a fresh context should identify source, state, next action, stop condition, and verification without the prior chat.

Use `assets/task-handoff-template.md`. A complete handoff grants no new authority.
