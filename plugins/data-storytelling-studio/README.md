# Data Storytelling Studio

Data Storytelling Studio turns checked analysis into a decision-facing artifact without quietly recalculating or overstating the source evidence.

## Owned workflow

1. `analysis-to-story-router` selects the delivery format and records the companion capabilities needed for production. The required_companions field records production needs. It does not prove installation or create a hard runtime dependency.
2. `chart-message-audit` tests each visual claim against its stated evidence and records revisions.
3. `executive-readout-builder` creates an answer-first narrative with decisions, risks, caveats, and next actions.

## Companion boundary

Spreadsheets, Data Analytics, Documents, Presentations, Visualize, Sites, Writing Quality, and Knowledge Work Superpowers are optional companions. Their absence does not block the plugin's owned routing, visual audit, or executive-readout work.

When a selected production companion is absent, write a self-contained local Markdown or JSON story brief. Preserve the source artifact paths and evidence limits. Mark the unsupported production or publication step incomplete and stop before claiming delivery.

Run `python3 scripts/check_companions.py` before a workflow whose output depends on a companion. Run `python3 scripts/verify_bundle.py` before installation or release.

## Maintenance

Edit the source under `plugins/data-storytelling-studio`, increment the version in both JSON contracts, validate every coordinator template, then reinstall through this marketplace. Do not edit the installed cache.
