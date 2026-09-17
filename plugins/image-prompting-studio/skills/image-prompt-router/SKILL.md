---
name: image-prompt-router
description: "Route image prompting and requested Midjourney operations to one task specialist. Covers creation, edits, references, conversion, series and layout without requiring branding work."
---

# Image Prompting Studio

Prompts are the default deliverable on every host, including Claude Code, Claude Cowork, and Codex. Follow the [prompt contract](../../references/prompt-contract.md). Choose one primary specialist by the requested deliverable; an explicit specialist invocation wins. Supporting references can help without creating a chain of mandatory skill calls. Do not activate Brand Studio merely because an image includes a brand.

When no model is named, write a broadly compatible non-Midjourney prompt. A named model selects its [dated profile](../../references/model-profiles.md), not a different generic workflow. Ask only when the missing answer would materially change the result; useful alternatives can cover ordinary creative ambiguity.

| Requested work | Primary skill |
|---|---|
| General scene, subject or concept | [image-prompt-create](../image-prompt-create/SKILL.md) |
| Targeted change or image-only exploration | [image-prompt-edit](../image-prompt-edit/SKILL.md) |
| Viewpoint, lens or framing alternatives | [image-camera-directions](../image-camera-directions/SKILL.md) |
| Coverage or frame blueprint before prompting | [image-shot-planner](../image-shot-planner/SKILL.md) |
| Combine references with roles and priority | [image-reference-composer](../image-reference-composer/SKILL.md) |
| Facts and current references are the main missing ingredient | [image-research-prompts](../image-research-prompts/SKILL.md) |
| Continuity across related images | [image-series](../image-series/SKILL.md) |
| One prompt must request multiple separate image files | [image-multi-output](../image-multi-output/SKILL.md) |
| Lettering or exact multilingual text is central | [image-typography](../image-typography/SKILL.md) |
| Factual relationships, labels, data or process | [image-infographic](../image-infographic/SKILL.md) |
| Poster, cover, spread or image/text page composition | [image-editorial](../image-editorial/SKILL.md) |
| Ordered narrative or instructional beats | [image-storyboard](../image-storyboard/SKILL.md) |
| One composite grid with multiple cells | [image-campaign-grid](../image-campaign-grid/SKILL.md) |
| Apply brand visual language to a creative image concept | [image-brand-interpretation](../image-brand-interpretation/SKILL.md) |
| Faithful illustration to photo or photo to illustration | [image-illustration-photo-translator](../image-illustration-photo-translator/SKILL.md) |
| Creative medium/style transformation | [image-style-translator](../image-style-translator/SKILL.md) |
| Age, season, historical change, decay or restoration | [image-time-variation](../image-time-variation/SKILL.md) |
| Spatial arrangement is the main design problem | [image-layout-architect](../image-layout-architect/SKILL.md) |
| Assess or repair supplied prompts | [image-prompt-review](../image-prompt-review/SKILL.md) |
| Midjourney creation prompt syntax | [midjourney-prompt-architect](../midjourney-prompt-architect/SKILL.md) |
| Midjourney editor, edits or retexture prompts | [midjourney-edit-architect](../midjourney-edit-architect/SKILL.md) |
| Operate Midjourney submissions, exploration, curation or HD workflow | [midjourney-prompt-batching](../midjourney-prompt-batching/SKILL.md) |

## Resolve overlap by the deliverable

A poster usually belongs to editorial; lettering as the subject belongs to typography; factual relationships belong to infographic; spatial arrangement as the main problem belongs to layout. Research can supply facts inside any of them without becoming a compulsory second workflow.

A coherent set belongs to series. Ordered storytelling belongs to storyboard. When the central request is one submission yielding separate files, use multi-output, even for related variants. A grid is one composite and belongs to campaign-grid. A brand name alone does not turn an ordinary image prompt into a brand strategy task.

Faithful photo/illustration translation keeps the reference's recognizable character, object or world. Broader reinterpretation of medium/style belongs to style-translator. Camera directions can be controlled studies or naturally evolving shots; the reference and wording decide, not a rigid global freeze/diversity rule.

For an operation, use the available surface and verify actual model, mode, attachments and accepted submissions. If tools are unavailable, deliver the complete prompt and state what remains unexecuted. Save preferred recipes only after explicit user selection. Never claim rendered or creative success from prompt validation alone.
