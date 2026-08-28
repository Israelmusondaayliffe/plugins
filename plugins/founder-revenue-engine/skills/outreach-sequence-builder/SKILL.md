---
name: outreach-sequence-builder
description: Drafts a bounded, evidence-linked outreach sequence for early customers, design partners, beta users, or founder-led conversations. Use when the ICP and market narrative are approved and channel-specific messages are needed. Produces messages with objectives, source references, stop rules, and no-send enforcement. It never sends email, updates CRM records, or changes accounts.
---

# Outreach Sequence Builder

## Overview

Create a small sequence that earns a reply without pretending a relationship or result exists. Every message traces back to the approved evidence and offer.

## Workflow

1. Load the approved ICP, narrative, proof set, channel constraints, and desired response.
2. Choose sequence length and message objectives with references/workflow.md.
3. Draft messages that use specific evidence, one clear ask, and honest personalization boundaries.
4. Fill assets/output-template.json and run scripts/validate_output.py.
5. Use Writing Quality for optional final copy validation when installed. When it is absent, apply the plugin-owned commercial-copy checks in ../founder-revenue-router/references/commercial-copy-checks.md.
6. Deliver drafts only. Stop before sending, scheduling, CRM writes, or account changes.

## Error Handling

- If personalization data is missing, write a research placeholder rather than inventing a detail.
- If proof is weak, lower the ask to a learning conversation or pilot.
- If the sequence requires a connected account action, report the required confirmation separately.

## Reliability Notes

The model writes channel-appropriate messages. The validator enforces unique messages, objectives, evidence references, and a false send-authorization flag.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
