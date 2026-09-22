---
name: midjourney-edit-architect
description: Write or repair Midjourney image-edit prompts for replacement, removal, additions, restyling, viewpoint changes, reference composition, inpainting and outpainting. Use for precise edit instructions, staged edits or diagnosis of a supplied Midjourney result.
---

# Midjourney edit architect

Turn the source image, references and requested change into complete paste-ready prompts. Read `../../references/prompt-contract.md` and the Midjourney entry in `../../references/model-profiles.md`. This public skill returns edit prompts; the user renders them separately in Midjourney.

1. Inspect the supplied image and references. Identify the visual anchor, requested change, protected features and the light, perspective or material cues needed to integrate the result. Ask only when a missing reference or material ambiguity prevents a faithful result.
2. Read [edit methods](references/edit-methods.md). Use its reference-role, risk and Editor guidance for the actual task. Preserve requested identity and world properties with artistic judgment. A change of viewpoint can reveal new surfaces; a naturally developed shot can alter pose and light when the context calls for it.
3. Load [edit patterns](references/edit-patterns.md) for the relevant recipe. Keep the exact source examples as craft references, adapting parameters only against the selected current model. Load [failure recovery](references/failure-recovery.md) when an output or stated failure needs diagnosis.
4. Choose one pass or a useful staged sequence. Honor explicit count and format. Use the retained precision, anchor-rich, cohesion and fallback approaches when alternatives help; do not require four responses for every edit.
5. State attachment roles where needed. Default to web prompt format when the surface is unstated. Consult [the dated boundary reference](references/current-model-boundaries.md) for web/Discord differences, then check the current model guidance before asserting supported controls. Keep parameters after the visual instructions.
6. Deliver each complete prompt in its own code block. For a sequence, say which result becomes the next base and what must be inspected before continuing. For diagnosis, give the observed failure, likely cause, smallest correction and revised prompt.

Finish prompt work when the change, references, preserved features and format are clear and no invented detail or unsupported control is presented as certain. A prompt does not prove the edit succeeded. Inspect actual output when provided or generated; The user selects accepted creative results and reusable recipes.

The MIT license and imported source attribution remain in `LICENSE` and [source provenance](references/source-provenance.json).
