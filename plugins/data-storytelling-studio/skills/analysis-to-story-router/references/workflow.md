# Routing workflow

## Decision sequence

1. Confirm the analysis is checked, partial, or disputed.
2. Identify the decision and the smallest audience that must act.
3. Select one primary delivery format.
4. Declare the evidence limits and production companions.
5. Hand the route to visual audit or readout production.

## Format table

| Need | Primary format | Typical companion |
| --- | --- | --- |
| Inspect calculations or reproduce methods | notebook | Data Analytics when installed |
| Explain one relationship | chart | Spreadsheets or Visualize |
| Monitor changing measures | dashboard | Spreadsheets, Data Analytics, or Sites |
| Preserve full analysis and methods | report | Documents or Writing Quality |
| Lead a live decision discussion | deck | Presentations |
| Enable a fast decision | executive-readout | Writing Quality |
| Publish an interactive external artifact | site | Sites |

Select one primary delivery format. Add a secondary export only when another audience or access need requires it.

## Readiness rules

- `checked`: production may continue with stated caveats.
- `partial`: continue only if the decision can tolerate the named gaps.
- `disputed`: stop production and return the disagreement to the analysis owner.

The router owns format and handoff decisions. Analytical companions own calculations and domain methods.

## Zero-companion fallback

All companions are optional. The required_companions field records the capabilities a later production step needs. It does not report installation and does not block creation of the route artifact.

When no selected companion is available, create a self-contained local Markdown or JSON story brief. Include the source artifact paths and evidence limits from the route artifact. Record the selected format, missing production capabilities, risks, and exact next skill. Mark unsupported production or publication incomplete. Do not claim that the final artifact was delivered.
