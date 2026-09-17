---
name: image-prompt-review
description: Review image prompts and supplied results against a brief or reference. Find structural errors, contradictions, continuity drift and task-specific visual defects, then suggest focused repairs.
---

# Image prompt review

Review the requested material independently. A supplied prompt, set of prompts, shot plan or image result is enough; no prior generation workflow is required. Distinguish defects in the written request from defects actually observed in images.

Read the [prompt contract](../../references/prompt-contract.md) for counts, formats, reference handling and delivery. When a model is named, consult only its relevant [model profile](../../references/model-profiles.md).

Read the brief and references used by the work. Establish the intended count, output form, model if specified, fixed elements and allowed changes. Use [review methods](references/review-methods.md) for structure, coverage, continuity, physical/material behavior and targeted repair. Do not impose the old ten-shot photoshoot rules on unrelated imagery.

For JSON, use [the structural checker](scripts/validate_prompt_payload.py) when a deterministic check helps. It accepts JSON objects, arrays or fenced JSON and reports malformed input rather than skipping it. Count and required/equal paths are optional checks derived from the actual brief. It does not measure visual fidelity or artistic merit.

Review the prompt semantically: conflicting change/keep instructions, ambiguous reference roles, wrong aspect ratio or file form, missing exact text, unsupported controls, and constraints that erase the source's character. In a set, inspect relevant subject/world continuity and deliberate variation. Read [material and realism review](references/material-review.md) only when physical behavior matters to the intended medium.

When outputs are supplied, inspect them against the actual source and prompt. Report visible drift, not inferred hidden defects. Without output images, label conclusions as prompt review only. Do not declare images accepted or save a preferred recipe for the user.

Deliver concise findings tied to specific prompts or visible regions, with suggested repairs. If the user requested revisions, return corrected complete prompts while preserving their useful wording, exact text, formats and unaffected choices. Avoid silently rewriting protected prompt examples to satisfy prose rules. A repeated structural problem merits one shared fix, not a rewrite of the creative set.
