---
name: image-typography
description: "Write prompts where lettering, exact text or multilingual typography is the main visual subject or critical constraint."
---

# Image Typography

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) only for a named model or actual execution.

Make an exact text inventory before designing. Keep spelling, capitalization, punctuation, diacritics and script intact. Distinguish literal copy from instructions: font names, color codes and layout labels should not appear as text unless requested. If translation is needed, treat the translation as content to verify rather than letting the image model improvise it.

Describe hierarchy, scale relationships, alignment, spacing, line breaks, reading direction, letterform character and material. A non-Latin script needs its own typographic conventions, not a Latin style mechanically imposed. Specify what must read first and how decorative lettering relates to legible supporting copy. Use fewer text zones when density would defeat the intended format.

Choose NL for expressive lettering or JSON when exact strings, placement and exclusions benefit from separation. Supplied text has authority; proposed copy must be identifiable as proposed. Do not promise error-free lettering or exact reproduction of a named font. A generated layout can be a reference for later typesetting when precise production text is needed.

Use [typography recipes](references/gpt-typography.md) for display words, mixed scripts, wordmarks, dense editorial and environmental lettering. Review the written inventory against the prompt; if a rendered image exists, read its actual text rather than assuming the instruction worked.
