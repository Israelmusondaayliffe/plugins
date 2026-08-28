---
name: founder-revenue-router
description: Routes founder-led revenue work across recent signal research, ideal-customer profiling, market narrative, outreach sequence, and LinkedIn content. Use when a founder needs evidence-backed early customers, design partners, a commercial message, or bounded outreach drafts. Enforces source traceability and never sends, writes CRM data, or changes accounts without separate action-time authorization.
---

# Founder Revenue Router

## Overview

Choose the commercial stage before researching or drafting. The plugin moves evidence toward a usable customer and message hypothesis while keeping external actions off by default.

## Workflow

1. Define the offer, stage, market, evidence already available, desired commercial outcome, and prohibited actions.
2. Choose one primary route using references/workflow.md.
3. Run the plugin companion preflight before using Sales, Creative Production, Gmail, Google Calendar, Canva, Writing Quality, Brand World Studio, or Strategy Room. Every companion is optional.
4. Fill assets/output-template.json and run scripts/validate_output.py.
5. Use last30days for recent signals, signal-to-icp and first-customer-finder for customer definition, market-narrative-builder for message, outreach-sequence-builder for drafts, and linkedin-viral-content-creator for founder-led content.
6. When Writing Quality is absent, apply the plugin-owned commercial-copy checks in references/commercial-copy-checks.md.
7. Return drafts and handoff instructions. Keep sending and account changes unauthorized.

## Error Handling

- If no evidence set exists, route to signal research before claiming an ICP.
- If the offer or positioning is unresolved and Strategy Room is installed, route the decision there.
- If the offer or positioning is unresolved and Strategy Room is absent, write a local commercial-decision gap. Include the evidence, assumptions, open questions, prohibited claims, and exact next decision. Stop before drafting from an invented answer.
- If the user requests sending, finish the draft and stop at the action boundary.

## Reliability Notes

The model selects the commercial route. The validator enforces one route, a named offer and outcome, rationale, and a false send-authorization flag.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- references/commercial-copy-checks.md defines the plugin-owned copy fallback.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.
