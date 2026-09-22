---
name: image-research-prompts
description: "Research facts and visual references for image prompts about real entities, current events, data, geography or scientific subjects."
---

# Image Research Prompts

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) when adapting a prompt for a named model.

Identify the facts the image actually needs: entities, appearance, date, event, labels, units, geography or structure. Use the authoritative owner where possible and record the date relevant to the subject, not only the date of browsing. Separate verified facts, unknowns and deliberately speculative content.

Research before writing when the host can browse. Place the resulting fact inventory directly into the prompt so it remains usable in a generation surface with no search. If the requested workflow intentionally searches at generation time, include a specific retrieval target and date anchor, plus what to do when a fact is unavailable. Do not assert that OpenAI uniquely supports search or that a SEARCH label guarantees retrieval.

Define the visual container around the facts: hierarchy, region, map extent, chart encoding, required labels and source line. Preserve values and units across prompt alternatives. For scientific imagery, distinguish appearance from verified structural/anatomical relationships. For proposed future scenes, identify them as speculative rather than inventing confirmation.

Deliver prompts plus concise source links supporting the facts used. Use [research recipes](references/gpt-search.md) for current events, entities, weather/data, geography, brands and taxonomy. Their search instructions are templates to adapt to actual host capabilities. Check facts and text inventory before delivery; inspect rendered labels only when a result exists.
