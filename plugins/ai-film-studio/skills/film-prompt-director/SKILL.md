---
name: film-prompt-director
description: "Explicit-only model-neutral prompt packet direction governed by declared adapter contracts."
---

# Film Prompt Director

Activation: explicit-only, either by direct request for `film-prompt-director` or a routed Film Advisor packet.

## Contract-first routing

Read [the model adapter contract](../../references/model-adapter-contract.md) before selecting an adapter. Select only a declared status:

- `planning-only`: can transform records and identify missing decisions.
- `delegated`: returns a complete normalized packet and may pass it to the named optional format owner.
- `unverified`: may not claim a surface capability or emit its syntax.

Never infer availability, duration, cost, reference limits, beta access, or an interface from a model name.

## Complete local packet

Always assemble a complete model-neutral shot packet. Copy the approved asset references and their positive and negative controls, geography lock, first-frame occupancy, timed action beats, performance, camera, lens, light, physics, dialogue, sound, constraints, source hashes, target model, and external-action policy. Validate the packet against the local record contracts.

If `video-production-studio:video-prompt-builder` is available, it may format the unchanged normalized packet for Seedance 2.5, Kling, or Veo. If it is absent, return the full normalized packet and a formatter handoff that names the requested model, the missing optional formatter, the selected surface questions, and the validation still required. Leave `compiled_prompt` and `prompt_sha256` empty, mark the local validator `unrun`, and do not claim model-specific syntax.

## External stop

Before live use, ask for or verify the selected surface, current controls, costs, and required approval. This skill cannot sign in, upload, purchase, start a generation, or publish.

## Handoff

Create a `PromptPacket` and attach it to the `ShotRecord`. Use `schemas/PromptPacket.schema.json`, `scripts/film_advisor.py`, and the adapter contract for deterministic validation. The packet remains a complete planning result even when its optional surface formatter is unavailable.
