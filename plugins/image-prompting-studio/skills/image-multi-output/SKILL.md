---
name: image-multi-output
description: "Write one prompt requesting multiple separate image outputs, including eight-image sets and coordinated pages with shared visual DNA."
---

# Image Multi Output

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) when adapting a prompt for a named model.

Deliver one complete prompt for the requested set unless the user explicitly asks for alternative batch prompts. This skill covers both repeated subject variants and distinct deliverables when the central requirement is one submission producing separate images. Preserve the distinction between one prompt, one composite/contact sheet, and several separate submissions.

Build a shared visual DNA block: subject/world, recognition anchors, palette roles, material/treatment, graphic language and the constraints that belong across the set. Then enumerate every output with its own purpose, content, exact text, layout, ratio and distinguishing direction. Allow deliberate per-image exceptions instead of forcing every page into an identical composition.

For an eight-image request, explicitly request eight separate image outputs, one per specification, with no grid, collage or contact sheet. Preserve the user's system-style prompt method using `<visual_dna>`, `<images>` and `<verify>` or the requested JSON/NL equivalent. On an ordinary chat surface this is an operating prompt, not a real elevated system role.

Use [multi-output recipes](references/gpt-multi-output.md) for event packages, product systems, editorial pages and world/character bibles. Read [page inventories](references/page-inventories.md) for useful starting contents. They are options, not a seven-page quota or a dependency on Brand Studio.

Write the requested prompts without submitting generation requests. If reviewing user-supplied results, count the actual separate images and report any shortfall. Never label a grid as eight files or crop it to manufacture the claim. Prompt preparation does not prove an output count.
