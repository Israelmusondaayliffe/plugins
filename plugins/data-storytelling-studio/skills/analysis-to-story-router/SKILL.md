---
name: analysis-to-story-router
description: Routes checked analysis to the right notebook, chart, dashboard, report, deck, executive readout, or publishable site. Use when the user has data findings or an analysis artifact and needs to choose a decision-facing format, audience, companion tools, evidence limits, and handoff path before production.
---

# Analysis to Story Router

## Overview

Choose the smallest delivery format that can support the audience's decision. Preserve the analytical source of truth and record uncertainty before production begins.

## Workflow

1. Inventory the source artifacts, decision question, audience, time horizon, and analysis state.
2. Load `references/workflow.md` and apply its routing table.
3. Select one primary format and name any secondary export only when it serves a distinct consumer.
4. Declare the companion capabilities needed for production. The required_companions field records production needs. It does not prove installation or create a hard runtime dependency.
5. Record evidence limits, risks, and the next coordinator skill.
6. When a selected companion is unavailable, write a self-contained local Markdown or JSON story brief. Include the decision question, audience, source artifact paths, analysis state, chosen format, evidence limits, production needs, risks, and next skill.
7. Mark unsupported production or publication incomplete in the local brief. Stop before claiming that the requested deck, dashboard, site, or other unsupported deliverable was produced or published.
8. Fill `assets/output-template.json` and run `scripts/validate_output.py` before a structured handoff.

## Boundaries

- Do not recalculate metrics or alter source data.
- Do not select a deck because the output is executive-facing when a one-page readout is sufficient.
- Do not promise interactive behavior without an installed publishing surface and a test plan.
- Do not treat a populated required_companions field as proof that any companion is installed.
- Do not claim production, publication, or delivery when the needed companion is absent.

## Error recovery

Set `handoff_ready` to false when the decision question is unclear, the analysis is disputed, or a required source is missing. Return the exact missing input and the safest interim format. When only a production companion is missing, return the complete local story brief and mark the unsupported production or publication step incomplete.

## Reliability

Format selection is judgment. The output contract, readiness state, evidence limits, and named handoff are deterministic and validated.
