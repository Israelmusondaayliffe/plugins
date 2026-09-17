---
name: image-camera-directions
description: Write controlled viewpoint studies or natural new shots from a reference. Cover camera angle, framing, shot distance, turnarounds and still endpoints while preserving the intended character, object or world.
---

# Image camera directions

Create useful new views of the supplied subject or world. Judge from the request whether the user wants a controlled camera study or a natural continuation of a shoot.

Read the [prompt contract](../../references/prompt-contract.md) for counts, formats, reference handling and delivery. When a model is named, consult only its relevant [model profile](../../references/model-profiles.md).

## Choose the right kind of change

For camera-only studies, retain subject state, style, environment and physical lighting; the new viewpoint changes what is visible and how the same light is seen. For a new shot in a shoot, pose, gaze, expression, action and lighting can develop naturally while retaining continuity. Do not force either every axis to freeze or a secondary pose change. Follow combined instructions such as a new angle at night without a needless mode-choice question.

Inspect the reference before describing it. Record the few identity, design, world, palette and style anchors that distinguish it. Unknown back surfaces or off-frame space require plausible inference; they are not facts recovered from the reference.

## Write the directions

Use [camera methods](references/camera-methods.md) for distance, perspective, lighting continuity, objects/worlds, turnarounds and the still/video boundary. Read [camera and light vocabulary](references/camera-light-vocabulary.md) when optical or lighting detail changes the prompt.

Choose a format the user requested or that suits the job. Read only relevant templates:

- [Controlled-angle NL/JSON forms](references/controlled-angle-templates.md): preservation-heavy viewpoint studies and the panoramic candidate.
- [Nano camera forms](references/source-nano-camera-templates.md): concise directions or a four-view character sheet.
- [Twelve-shot recipes](references/angle-recipes.md): a curated shoot with detailed composition, portrait, wardrobe and accessory examples.

Each prompt names the reference, camera position, distance/crop, what becomes visible and the changes allowed. The source's ten/twelve-shot banks are choices; explicit requested counts win. Preserve the exact target style and aspect ratio unless the brief permits a change.

## Complete the request

Check meaningful viewpoint differences, reference continuity and whether each still is coherent from that camera. Distinguish separate image prompts, one composite turnaround and an actual camera move. A still can depict an endpoint or an implied-motion moment; continuous motion needs a video deliverable. Explain that boundary without requiring another plugin.

Deliver complete prompts. When images are available, compare them to the reference and identify observed drift rather than claiming preservation from the wording alone. The user chooses preferred results.
