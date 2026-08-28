# Handoff phase

## Scope

Create an owner-specific handoff record for an approved proposal. Do not apply the change.

## Workflow

1. Confirm `decisions.jsonl` contains an approval for the proposal.
2. Read the routing map in `references/ownership-and-routing.md`.
3. Use the generated handoff JSON as the input brief for the owning plugin or skill.
4. Preserve the evidence references and approval decision.

## Output

Return the handoff path and owner. The receiving capability performs its own checks and approvals.
