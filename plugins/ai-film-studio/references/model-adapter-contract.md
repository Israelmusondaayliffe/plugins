# Model adapter contract

Model adapters translate a complete `ShotRecord` into a safe, model-specific handoff. They are not evidence that a product feature exists or is currently available.

## Contract

Every `ModelProfile` must declare:

- the model and profile version checked plus the verification date;
- supported inputs, reference behavior, audio, duration, and editing modes;
- known constraints and recurring failure patterns;
- a prompt formatter, validator, and evidence record;
- the external-action approval policy.

`status` is one of `delegated`, `unverified`, or `template`. An unverified or template profile cannot claim a feature, emit surface syntax, or initiate an external action.

## Complete local packet

AI Film Studio always produces a complete model-neutral shot packet. The packet includes the approved references, reference limits, geography, first-frame intent, timed action, performance, camera, lens, light, physics, dialogue, sound, constraints, source hashes, target model, and approval policy.

The local packet is a complete planning result. It does not claim model-specific surface syntax or a passing surface validator result.

## Optional model-specific formatter

The Seedance 2.5, Kling, and Veo profiles name `video-production-studio:video-prompt-builder` as an optional formatter and validator. When that companion is available, pass it the unchanged normalized packet. When it is absent, return the full normalized packet plus a handoff naming the requested model, missing formatter, selected surface questions, and validation still required. Do not claim that final surface syntax was produced.

Before any live use, verify the selected surface, duration, aspect ratio, reference controls, availability, and cost. Do not infer a product mode from this contract.

## Versioned profile selection

Read `model-profiles/index.json` before resolving a model. Seedance 2.5 is the default profile only for a model-specific video prompt with no model named. Explicit Kling and Veo selections remain explicit. A future model begins from the unverified template and cannot emit surface syntax until current evidence is recorded.

## Planning-only adapters

`image-planning` and `video-planning` are model-neutral record transforms. They may identify missing constraints and produce a decision-ready handoff, but they do not call a service, upload media, or make a capability claim.
