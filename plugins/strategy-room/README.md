# Strategy Room

Strategy Room packages source-first interviews, uncertain-effort wayfinding, assumption challenge, broad option generation, decision synthesis, and durable uncertainty tracking for consequential choices.

## Owned skills

- strategy-room-router
- decision-synthesizer
- decision-wayfinder (explicit specialist routed by Strategy Room)
- assumption-register
- grill-me
- assumption-challenger
- multi-direction-explorer

## Optional companion capabilities

- Knowledge Work Superpowers for additional evidence-led research
- Outcome Engine for execution after an accepted decision
- ProofLoop for extended verification
- Writing Quality for optional final prose review
- Continuity Vault for optional cross-task continuity

Run `scripts/check_companions.py` to see which optional companions are installed. Missing optional companions do not block owned workflows.

## Local fallbacks

- Without an execution companion, Strategy Room emits a self-contained execution brief or decision handoff. It includes the accepted decision, rationale, assumptions, evidence, risks, conditions, acceptance checks, next actions, and owner. Strategy Room then stops before execution.
- Without Continuity Vault, Strategy Room writes the decision map to `<approved-output-root>/strategy-room/decision-map.md` from `skills/decision-wayfinder/assets/decision-map-template.md`. It writes an execution handoff, when needed, to `<approved-output-root>/strategy-room/execution-handoff.md`.
- The approved output root comes from the active host or the user's explicit file authorization. If neither supplies one, ask the user to approve a local root before writing. Do not substitute conversation history for the durable file.

## Boundaries

- Strategy Room ends at a decision record and named handoff.
- A recommendation does not authorize execution.
- Wayfinding maps one blocking decision at a time and does not become a generic project plan.
- Facts, assumptions, and judgment remain visibly separate.

## Verification

Run `scripts/verify_bundle.py` from any directory. Installation is trusted only after plugin validation, skill validation, source-to-cache parity, live listing, real-artifact validation, and clean-task discovery all pass.
