---
name: guide-acceptance-review
description: Independently review a practical guide as a cold reader against its contract, sources, evidence, structure, visual teaching, and usefulness. Use when a guide is awaiting human approval, publication, baseline pinning, or scale. The reviewer must differ from the producer and cannot self-approve.
metadata:
  author: Community Maintainers
  version: 0.1.1
---

# Guide Acceptance Review

Judge whether the guide helps a person do the work. Passing files and honest disclaimers are supporting evidence, not the teaching verdict.

## Independence gate

Require distinct producer and reviewer identities. If they are the same, stop. The reviewer may inspect prior feedback but must perform a fresh read of the candidate and sources.

Load `../guide-production-router/references/human-acceptance-rubric.md`. Load the visual evidence reference when the subject is visual, motion-led, spatial, or interface-based.

## Review sequence

1. **Read cold.** Inspect the candidate before reading its internal rationale. Record the first point where purpose, vocabulary, or next action becomes unclear.
2. **Try the path.** Follow the quick start or first useful action using only what the guide provides.
3. **Trace claims.** Check factual behavior, examples, provenance, run status, and limitations against the contract and sources.
4. **Inspect structure.** Identify pages, templates, prompts, or downloads that do not earn their place or repeat another component.
5. **Inspect visual teaching.** Confirm the reader can see the comparison or evidence needed for visual judgment.
6. **Separate problem classes.** Mark privacy and unsupported claims as critical; context, usefulness, examples, structure, and voice as qualitative gates.
7. **Refuse false resolution.** A limitation is not resolved merely because it is disclosed. State what the disclosure protects and what teaching gap remains.
8. **Record the verdict.** Populate `guide-review.template.json` with evidence for every gate.

Validate the record:

```text
python3 ../guide-production-router/scripts/validate_guide_review.py GUIDE_REVIEW.json
```

## Allowed verdicts

- `blocked`: required source, rights, evidence, or independence is missing.
- `rejected`: the guide is reviewable but one or more acceptance gates fail.
- `ready_for_human_review`: every reviewer gate passes and remaining approval belongs to the named human owner.

Do not set `human_approved`. A model or worker cannot certify the human's decision.

## Scale gate

Bulk guide work remains blocked until the named human approves the benchmark and a cold reader has completed the intended first action without author-only context.
