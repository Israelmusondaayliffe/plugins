---
name: market-narrative-builder
description: Builds a source-traceable commercial narrative that connects a specific audience problem, market language, offer, proof, objections, and call to action. Use when a defined ICP must become outreach, sales copy, founder content, or campaign assets. Validates that claims come from the allowed evidence set and keeps unsupported proof out of the message.
---

# Market Narrative Builder

## Overview

Turn evidence and positioning into one commercial story. The narrative should make the problem and offer legible without inflating proof.

## Workflow

1. Load the validated ICP, offer definition, approved positioning, source ledger, and known objections.
2. Extract the audience's language and separate observed pain from the founder's interpretation.
3. Draft the problem, offer, proof, objections, and call to action using references/workflow.md.
4. Fill assets/output-template.json and run scripts/validate_output.py.
5. Use Writing Quality for optional final prose validation when installed. When it is absent, apply the plugin-owned commercial-copy checks in ../founder-revenue-router/references/commercial-copy-checks.md.
6. Use Brand World Studio for visual expression only when installed. Its absence does not block the owned narrative.
7. Route any unsupported claim back to research or remove it.

## Error Handling

- If proof is absent, use an honest pilot or learning claim rather than invented results.
- If the audience and buyer differ, name both and adapt the call to action.
- If the offer or positioning is unresolved and Strategy Room is installed, route the decision there.
- If Strategy Room is absent, write a local commercial-decision gap as Markdown or JSON in the user-approved output root. Include the evidence, assumptions, open questions, prohibited claims, and exact next decision. Stop before drafting the unresolved answer. If no output root is approved, ask for one before writing the gap.

## Reliability Notes

The model shapes the narrative. The validator requires the audience, problem, evidence, offer, proof, objections, and call to action.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
