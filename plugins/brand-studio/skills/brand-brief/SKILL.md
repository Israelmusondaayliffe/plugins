---
name: brand-brief
description: Translate supplied or confirmed brand decisions into a practical production brief. Use when the user needs audience, visual principles, assets, deliverables and constraints organized for identity, campaign or design work.
---

# Brand brief

Read [brand context](../../references/brand-context.md). Use the evidence already supplied. A separate strategy file is optional; current conversation decisions can be the source.

1. Identify the brand, audience, intended response, positioning, deliverables, existing assets and constraints.
2. Translate each relevant attribute into visible choices using [brief controls](references/workflow.md). For example, precision can affect spacing, typography, grid and image selection.
3. State visual principles, color and type boundaries, permitted variation, likely drift to avoid, source references and the authority of each decision. Split genuinely different audiences or formats into named tracks when needed.
4. Deliver a model-neutral brief that another person or tool can use independently. Leave unsettled positioning labeled as proposed or unknown; do not manufacture approval to fill a field.
5. If JSON is requested, use [the template](assets/output-template.json) and run `../../scripts/validate_artifact.py ARTIFACT.json --schema assets/output-schema.json` with paths resolved from this skill. Validation checks structure, not approval or taste.

Finish when the requested deliverables and constraints are clear, their source is traceable and consequential gaps are visible. A production issue that changes positioning becomes a decision for the user. Transfer the brief to another studio only when requested.
