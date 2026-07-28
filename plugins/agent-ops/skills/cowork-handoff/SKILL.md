---
name: cowork-handoff
description: Package a task as a self-contained prompt that Claude Cowork, or another agentic harness, runs on its own. Use when the user says give me the prompt for Cowork, wants work handed to Cowork or a second harness instead of executed here, or asks for a copy-paste brief another agent can complete without this session's context. Produces the handoff prompt, not the work itself.
---

# Cowork Handoff

The receiving harness is an agent, not a text editor. It has its own tools, files, and judgment, and it has none of this session's context. The handoff prompt must stand alone: everything the receiver needs is in the prompt or in files the prompt names.

## Workflow

1. Confirm the split: what the receiving harness will do, and what stays here. Say which side owns verification.
2. Gather what the receiver cannot discover on its own: goal, background decisions already made, exact file paths or uploads it will have, and any constraints from the user's standing rules that apply to the task.
3. Write the handoff prompt with these parts, in order:
   - Objective: one sentence, outcome-shaped.
   - Context: the decisions and facts the receiver would otherwise have to guess. No session narrative.
   - Inputs: exact files, paths, or uploads it will have, and what each is.
   - Task: the work, stated as end state rather than steps, with steps only where order genuinely matters.
   - Constraints: authority boundaries, things it must not touch, and output location and naming rules.
   - Success criteria and verification: what done looks like and how the receiver proves it before claiming completion.
   - Report format: what it should write back, so the human can relay results without interpretation.
4. Deliver the prompt in a single copyable block. Nothing outside the block should be required.
5. If the handoff depends on an updated upload or plugin on the receiver, say so above the block, including that a fresh session is needed after an upload swap.

## Error handling

- If the task needs data only this session has, embed it in the prompt or write it to a file the receiver will have; never assume shared memory.
- If success criteria cannot be stated, the task is not ready to hand off; resolve the unknowns first.
- When results come back, verify them here before integrating; the handoff prompt should have made that verification cheap.
