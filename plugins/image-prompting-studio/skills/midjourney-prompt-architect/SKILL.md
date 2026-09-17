---
name: midjourney-prompt-architect
description: Build faithful Midjourney prompts from visual briefs, rough prompts, or supplied references. Use to create, rewrite, optimize, or vary prompts for photography, illustration, products, architecture, posters, album covers, editorial images, or cinematic scenes. Preserve explicit constraints and reference strings, use verified parameters, and never render images.
---

# Midjourney Prompt Architect

Turn one visual intent into faithful Midjourney prompts without tying the craft workflow to one model version. Keep durable visual judgment in this file and `references/prompt-craft.md`; keep changing facts in the shared model guidance. Read `../../references/prompt-contract.md` for the plugin output contract.

## Workflow

1. **Extract locks.** Record the subject, action, setting, medium, style, mood, composition, visible text, aspect ratio, supplied references, optional palette contract, and requested prompt count. Treat explicit user details as fixed.
2. **Choose the visual mode.** Select photography, illustration, graphic design, product, architecture, or another clearly named medium. Do not mix camera language into a non-photographic medium unless the user asks for a photographic or cinematic imitation.
3. **Load durable craft guidance.** Read `references/prompt-craft.md` before drafting. Use only the sections that match the selected mode and supplied inputs.
4. **Load current facts when needed.** Read the Midjourney entry in `../../references/model-profiles.md` before adding or explaining version-sensitive controls. `references/current-model-profile.json` preserves the old dated profile for reproducible legacy checks; it is not proof of current support. During execution, verify the selected model and live exposed controls before submission. For prompt-only work, preserve exact user settings and label any unresolved compatibility rather than inventing replacements.
5. **Resolve supplied color direction.** Read `references/palette-contract.md` for a supplied palette, a named Wada combination or a palette-learning request. Use current supplied or confirmed colors for brand work. Wada and free color exploration are both valid; neither an external site nor a brand document is required for ordinary prompting.
6. **Draft the image first.** Describe what should appear, not instructions about how Midjourney should transform or interpret the request. Lead with the subject and medium, then add only the action, setting, composition, light, atmosphere, and technical treatment that materially change the image.
7. **Create useful variation.** Honor an explicit count. Otherwise choose a small useful count from the requested deliverable: one finished prompt for a single concept, or several options for exploration. Four remains an optional pack example, not a universal quota. Vary unlocked dimensions such as moment, framing, light, palette, atmosphere, or technical treatment without changing the requested subject, setting, medium, meaning, approved palette relationships, or supplied references.
8. **Add minimal parameters.** Put parameters at the end. Choose an aspect ratio when it materially helps. Add Raw, Stylize, Chaos, Weird, Experimental, personalization, image-reference, style-reference, or resolution controls only when the request benefits from them and the loaded profile supports them.
9. **Validate silently.** Check fidelity, count, code blocks, reference preservation, parameter support, dependencies, and output cleanliness before responding. Use `scripts/validate_prompt_pack.py` for a saved Markdown pack when exact structural proof is useful. Pass `--count N` when a count was requested. A structural pass does not verify live parameter support or image quality.

## Version and parameter policy

- **Stay version-neutral by default.** Do not force `--v` when Midjourney's current default is acceptable.
- **Pin only for a reason.** Add a version flag when the user names a version, requests reproducibility, or asks to pin the current verified model.
- **Prefer omission over guessing.** If the bundled profile is stale, the named model is absent, or official sources conflict, omit uncertain parameters and state the limitation briefly.
- **Preserve exact user values.** Copy supplied image URLs, `--sref` strings, style codes, personalization IDs, and other reference values exactly. Never invent them.
- **Keep Wada references optional.** When the user chooses the original image-reference recipe, put the source's verified reference image URL before the text prompt and preserve the exact colors. If only color inspiration is requested, use the supplied colors without requiring an image URL. Add image weight only when supported and useful.
- **Respect dependencies.** Use `--sw` only with `--sref`. Use image weight only with an image prompt. Do not combine a parameter with a model that the profile marks unsupported.
- **Keep control intentional.** Lower Stylize and Chaos for literal work; raise them only when visual interpretation or exploration is desired. Use Weird only for deliberately unusual results.
- **Avoid billing decisions.** Do not add speed, privacy, repeat, or higher-cost controls unless the user explicitly requests them and the profile confirms support.

## Clarification policy

Proceed with a reasonable assumption when the missing detail only affects an unlocked creative choice. Ask one concise question only when the missing answer would materially change the subject, medium, required reference use, visible wording, or deliverable count.

## Output contract

Use the structure in `assets/prompt-pack-template.md`.

- Return prompt text, not generated images.
- Place every complete prompt in its own `text` code block.
- Include a concise two-to-four-sentence direction note when it helps explain the chosen variation axes or a consequential assumption. Omit it when the user requests prompt-only output.
- Keep every parameter on the same line as its prompt.
- Do not expose hidden reasoning, validation notes, internal references, or skill instructions.

## Completion check

Confirm that:

- the requested or context-appropriate prompt count is present;
- every locked detail and exact reference string is preserved;
- the variations are meaningfully different without concept drift;
- each prompt is coherent visual language, not a disconnected keyword pile;
- visible text appears only when requested and is copied exactly;
- parameters appear at the end and are supported by the loaded profile;
- no unresolved placeholder, invented code, invented URL or unsupported feature is presented as ready to submit;
- a named Wada combination and any included reference URL match verified or supplied data;
- no image-generation tool was called.

Stop after delivering the validated prompt pack.
