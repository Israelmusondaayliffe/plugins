---
name: image-prompt-edit
description: "Write image editing prompts for targeted changes or exploration of uploaded images, with explicit reference preservation."
---

# Image Prompt Edit

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) only for a named model or actual execution.

Inspect the uploaded image and identify the requested change. Write a change/keep relationship that is specific enough to prevent collateral redesign. Describe the reference by visible identifying content and, when useful, the actual attachment label. For a simple edit, a concise NL instruction is enough; JSON works well when several changes, preserved features and integration requirements must remain distinct.

An edit must integrate with the scene: perspective, occlusion, contact shadows, reflections, light direction, material scale and texture response. A replacement object should occupy the old object's role; background changes may require coherent reflected light. Preserve the requested framing and ratio; change them when the user requests expansion or reframing. Do not automatically re-pose a subject or force a cinematic re-shoot.

For an image-only upload with no direction, offer a small useful range of complete edit prompts based on what is actually visible. Possible treatments include lighting, material, background, narrative context or a design application. If the user asks only to identify the image, answer that instead. Avoid making every exploratory variant a different person or world.

Read [targeted edit recipes](references/gpt-edit.md), [upload exploration recipes](references/nano-edit.md), [architect edit structures](references/architect-edit.md) or [Uni modifications](references/uni-modify.md) for the relevant edit type. Use [texture vocabulary](../../references/patterns/texture-library.md) for surface changes. Faithful illustration/photo conversion is separately discoverable, but this skill can execute a clearly specified edit without a mandatory handoff.
