---
name: image-infographic
description: "Write image prompts for factual diagrams, maps, charts, process explanations and information graphics with explicit labels and relationships."
---

# Image Infographic

Read the shared [prompt contract](../../references/prompt-contract.md). Use [model profiles](../../references/model-profiles.md) only for a named model or actual execution.

Start with the information, not a decorative style. Identify the audience's question and the relationship that answers it: sequence, comparison, hierarchy, geography, causality, proportion or anatomy. Choose a visual form that represents that relationship faithfully.

Create an exact inventory of title, labels, values, units, connections, legend and source line. State the required relationships and positions, not only the noun names. Distinguish a process arrow from correlation or causation. Preserve data across stylistic alternatives. If information is missing, use supplied placeholders or research it; do not invent credible-looking figures.

Specify composition, reading order, visual hierarchy, density, color meanings and medium. Labels must remain associated with the correct object or series. A map needs a defined region and source; scientific structure needs a verified reference. Use JSON for a dense label inventory or NL when a simpler visual explanation reads better.

Use [infographic recipes](references/gpt-infographic.md) for diagrams, charts, maps, anatomy, educational posters and flowcharts. Check the prompt against its data source. Rendered accuracy is a separate check: inspect labels, numbers and spatial relationships when an output is available.
