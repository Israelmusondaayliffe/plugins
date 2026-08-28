# Writing route rules

Writing Quality owns ordinary prose. Harness and plugin maintenance remain with Harness Engineering's separate Unslop specialist, which is not a runtime dependency of this router.

## intent-architecture

Use when the user needs a new draft, message strategy, audience adaptation, or structural rethink. Load business-writing-intent-enforcer first.

## rewrite

Use when the user authorizes changes to supplied prose. Preserve meaning, claims, source-backed voice, and protected exact material. Load business-writing-intent-enforcer, then writing-enforcer.

## detect-only

Use for audits, critique, issue spotting, and requests that prohibit rewriting. Run Writing Enforcer in `DETECT` mode. Report findings with locations and proposed remedies. Do not return replacement prose unless requested.

## validation

Use when the draft already exists and the user wants a pass or fail against named requirements. Report failed checks before optional refinements.

## Claim boundary

Invoke claim-boundary-checker when a material statement is unsupported by supplied sources, depends on current facts, or crosses from editing into factual invention.
