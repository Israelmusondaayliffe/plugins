# Strategy Room routing

interview: use grill-me when the brief is vague, incomplete, or held in the user's head.
wayfind: use decision-wayfinder when the destination is meaningful but the route is obscured by several dependent decisions. Map the fog and choose one blocking edge; do not turn it into a generic project plan.
challenge: use assumption-challenger when hidden beliefs or external facts could reverse the choice.
explore: use multi-direction-explorer when the option set is narrow or repetitive.
synthesize: use decision-synthesizer when options and evidence are ready for a recommendation.
register: use assumption-register when uncertainty must remain visible after the decision.

Strategy Room owns pre-commitment reasoning and stops before execution. Outcome Engine and any other execution capability are optional companions.

When an execution companion is available and explicitly selected, hand it the accepted decision record after separate execution authorization. Otherwise emit a self-contained execution brief or decision handoff with the accepted decision, rationale, assumptions, evidence, risks, conditions, acceptance checks, next actions, and owner. Stop before execution.

Continuity Vault is optional. When it is absent, write durable decision state to `<approved-output-root>/strategy-room/decision-map.md` using Decision Wayfinder's template. Write any execution handoff to `<approved-output-root>/strategy-room/execution-handoff.md`. If no output root is authorized, ask for one before writing.
