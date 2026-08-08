---
name: loop-designer
description: Design and initialize a bounded loop or goal contract (Codex Goals or Claude Code /goal) with observable completion, machine checks, authority boundaries, iteration limits, and named stop states. Use when a user asks to turn a recurring task into a loop, define a verifiable Goal, build a Plan-Act-Verify contract, or create durable loop state before execution. Do not use to run an existing contract.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Loop Designer

Create the finish line before execution. A valid loop needs fresh feedback that can change the next action. If the work finishes in one pass and no later observation matters, recommend a one-shot workflow instead.

## Workflow

1. Define the outcome in terms a stranger can verify from artifacts and checks.
2. Identify at least one deterministic machine check. Keep judgment criteria separate.
3. Record allowed paths, forbidden paths, and external actions that require approval.
4. Use user-supplied iteration limits. When none exist, ask because the contract schema requires explicit positive limits.
5. Define success, failure, blocked, and exhausted stops.
6. Copy `assets/contract-template.json` to a task-owned working path and replace every `__REPLACE_ME__` marker.
7. From the LoopKit plugin root, validate it:

```bash
python3 scripts/validate_contract.py /absolute/path/to/contract.json
```

8. Initialize durable state only after validation:

```bash
python3 scripts/init_run.py /absolute/path/to/contract.json --workspace /absolute/workspace/path
```

9. Return the run directory and summarize the authority boundary. Do not start execution unless the user requested an end-to-end run.

## Reliability

The model defines the contract. The validator enforces its structure, explicit caps, machine checks, and stops. Initialization creates a workspace-scoped run with atomic state files and an initial checkpoint.

## Error handling

- If no observable completion condition exists, stop and reshape the task.
- If a command depends on an unavailable tool, do not include it as a machine check.
- If the user wants recurrence but no clean no-op behavior exists, note that schedule readiness is blocked.

Load `references/contract-fields.md` when a field is ambiguous.
