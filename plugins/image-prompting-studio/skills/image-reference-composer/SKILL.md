---
name: image-reference-composer
description: "Compose subjects, objects, environments, style or layout from multiple image references with clear roles and priority."
---

# Image Reference Composer

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) only for a named model or actual execution.

Read every supplied reference. Identify what each contributes: identity, object geometry, wardrobe, environment, composition, pose, material, lighting or style. Use a short reference map and an explicit priority when references conflict. Do not transfer a style reference's face or a wardrobe reference's identity unless requested.

Build one coherent scene. Resolve scale, perspective, eye lines, body/object contacts, occlusion and lighting so the result feels constructed in one space. State who holds what and where each subject sits. Multiple references do not require blending every feature. For a subject placed in a location, preserve the subject's recognition anchors while adapting illumination and contact to the setting.

JSON can separate roles and integration constraints; NL suits a simple blend; a shared system-style prompt suits several compositions under one reference map. Do not impose an inherited four-reference limit or claim an unsupported high-fidelity headcount. Consult the named model profile only when it changes the requested operation.

Use [composition recipes](references/gpt-compose.md), [Uni fusion recipes](references/uni-fuse.md) and [fusion methods](references/fusion-methods.md). A separate prompt should remain understandable when copied with its intended attachments. Check for cross-reference leakage in the written prompt and, if rendered outputs exist, inspect actual integration.
