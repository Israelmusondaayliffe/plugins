---
name: strategy-room-router
description: Routes pre-commitment decision work to rigorous interview, uncertain-effort wayfinding, assumption challenge, broad option generation, decision synthesis, or assumption tracking. Use when a product, business, creative, technical, or personal choice needs pressure-testing before resources are committed, or when a large uncertain effort needs its next blocking decision mapped. Enforces a decision-only boundary and produces a self-contained handoff when no optional execution companion is available.
---

# Strategy Room Router

## Overview

Choose the decision operation before loading several broad thinking skills. Strategy Room ends with a decision record and an explicit handoff, not silent execution.

## Workflow

1. Identify the decision, decision owner, deadline, stakes, reversibility, evidence already available, and what commitment would follow.
2. Select one primary route using references/workflow.md.
3. Fill assets/output-template.json and run scripts/validate_output.py.
4. Use grill-me for source-first interview, decision-wayfinder for a large uncertain effort whose blocking decisions are unclear, assumption-challenger for researched scrutiny, multi-direction-explorer for distinct options, decision-synthesizer for the recommendation, and assumption-register for durable uncertainty tracking.
5. Deliver the decision record and name the next owner. Use an execution companion only when it is available, explicitly selected, and separately authorized. Otherwise produce the local execution handoff and stop before execution.

## Local fallback contract

- The execution handoff contains the accepted decision, rationale, assumptions, evidence, risks, conditions, acceptance checks, next actions, and owner.
- When file output is authorized, write it to `<approved-output-root>/strategy-room/execution-handoff.md`.
- When Continuity Vault is absent, write durable decision state to `<approved-output-root>/strategy-room/decision-map.md` through Decision Wayfinder's template.
- If no output root is authorized, ask for one before writing. Keep the complete handoff in the current task until the root is approved.
- Stop before execution. A handoff records what another authorized task can do; it does not grant that authority.

## Error Handling

- If no real decision exists, return the missing decision statement rather than running a generic brainstorm.
- If evidence is insufficient for an irreversible choice, route to challenge or register before synthesis.
- If the user asks for execution, complete the decision phase first. Use an available, explicitly selected execution companion or return the self-contained local handoff.

## Reliability Notes

The model identifies the decision stage. The validator enforces one route, a named decision, a rationale, and a false execution-authorization flag.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
