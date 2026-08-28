---
name: iteration-supervisor
description: "Explicit-only evidence and iteration supervision for AI film generations without initiating live jobs."
---

# Iteration Supervisor

Activation: explicit-only, either by direct request for `iteration-supervisor` or a routed Film Advisor packet.

This skill plans and diagnoses generations. It never starts a paid or live job itself.

## Loop

1. State the narrow test hypothesis and the visible acceptance conditions.
2. Choose a baseline whose known quality isolates the variable under test.
3. Capture the exact record versions, assets, adapter decision, and expected result before testing.
4. Review the output against named evidence. Classify the earliest failure as source asset, geography, performance, direction, adapter uncertainty, or inconclusive.
5. Change one causal variable, not a cloud of adjectives. Preserve the rest of the input and log the change.
6. If repeated attempts fail, simplify the shot or reopen the earlier decision. Do not stack uncontrolled repairs.

## Stop rules

Do not ask a user to spend credits, authenticate, upload media, or generate without the approval required by [approval gates](../../references/approval-gates.md). A test plan can recommend the smallest useful experiment, but execution remains a separately approved action.

## Handoff

Store each comparison as a `GenerationAttempt` using `schemas/GenerationAttempt.schema.json`. Route an approved evidence package to `post-delivery-director`; route a diagnosed source problem to the earliest relevant skill. Use `VerificationPacket` for evidence checks.
