---
name: brand-review
description: Inspect brand strategy, identity systems or visual assets against supplied requirements and references. Use for brand consistency, release readiness, deliberate variation versus drift, or specific repair recommendations.
---

# Brand review

Read [brand context](../../references/brand-context.md). Review the requested set against the current supplied or confirmed authority. A review can assess a proposed direction without pretending it is approved.

1. Identify the brief, reference assets, decisions and exact artifact set. Inspect available images and documents directly. For missing artifacts, state which checks remain untested.
2. Apply [review controls](references/workflow.md) to each relevant artifact: message, composition, hierarchy, spacing, color roles, typography, imagery, logo treatment, text and requested exclusions. Distinguish allowed variation from drift against the governing principle.
3. Report material findings with artifact, visible evidence, affected requirement and smallest useful repair. State when a conclusion is an aesthetic recommendation rather than a requirement failure.
4. Use pass, fail or blocked only for assistant assessment against the stated scope. Pass requires all mandatory checks tested with no material issue remaining. If authority is missing, offer explicitly provisional feedback where useful and leave conformance blocked.
5. For structured output, use [the template](assets/output-template.json) and `../../scripts/validate_artifact.py ARTIFACT.json --schema assets/output-schema.json` with paths resolved from this skill. A valid file is not visual proof.

Deliver the review without silently modifying the assets. The user owns final creative acceptance. Record acceptance only when their explicit decision is present; leave it pending otherwise. Do not infer approval from a pass, download, favorite or selected UI card.
