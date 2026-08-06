---
name: strategy-room-router
description: Routes pre-commitment decision work to rigorous interview, uncertain-effort wayfinding, assumption challenge, broad option generation, decision synthesis, or assumption tracking. Use when a product, business, creative, technical, or personal choice needs pressure-testing before resources are committed, or when a large uncertain effort needs its next blocking decision mapped. Enforces a decision-only boundary and hands execution to Outcome Engine only after the recommendation is accepted.
---

# Strategy Room Router

## Overview

Choose the decision operation before loading several broad thinking skills. Strategy Room ends with a decision record and an explicit handoff, not silent execution.

## Workflow

1. Identify the decision, decision owner, deadline, stakes, reversibility, evidence already available, and what commitment would follow.
2. Select one primary route using references/workflow.md.
3. Fill assets/output-template.json and run scripts/validate_output.py.
4. Use grill-me for source-first interview, decision-wayfinder for a large uncertain effort whose blocking decisions are unclear, assumption-challenger for researched scrutiny, multi-direction-explorer for distinct options, decision-synthesizer for the recommendation, and assumption-register for durable uncertainty tracking.
5. Deliver the decision record and name the next owner. Do not execute the selected option unless a separate task authorizes it.

## Error Handling

- If no real decision exists, return the missing decision statement rather than running a generic brainstorm.
- If evidence is insufficient for an irreversible choice, route to challenge or register before synthesis.
- If the user asks for execution, complete the decision phase first and hand off explicitly.

## Reliability Notes

The model identifies the decision stage. The validator enforces one route, a named decision, a rationale, and a false execution-authorization flag.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
