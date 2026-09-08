# Palette contract intake

Use this adapter only when the user supplies a palette contract, a contract file, or a canonical pointer owned by the relevant project.

## Accepted input

Read JSON, YAML, Markdown, or structured text that identifies some or all of:

- palette or collection name;
- named colors and exact values;
- roles such as dominant, support, highlight, shadow, neutral, or accent;
- approved pairings, proportions, contrast rules, materials, or lighting behavior;
- forbidden substitutions or combinations;
- provenance and the contract's authority level.

Treat explicitly approved fields as locked. Preserve exact color names and values. If the contract has no role mapping, use the colors without inventing a hierarchy and state the assumption outside the prompt only when consequential.

## Prompt mapping

Translate the contract into observable color behavior:

- name the dominant field or material;
- assign supporting colors to surfaces, wardrobe, environment, or light;
- reserve accents at the stated scale;
- preserve approved contrast and temperature relationships;
- vary placement, balance, atmosphere, or material response without leaving the palette.

Prefer meaningful color language over dumping a sequence of hex codes. Include exact values only when the user or contract requires them.

## User-selected palette sources

Use a palette repository only when the user or project selects it. Obtain its exact palette data and reference image from that source; do not invent URLs or select a publisher-owned palette by default. Preserve the contract’s color names, values, roles and proportions. If both JSON and a reference image are supplied, verify they identify the same palette. When the source is unavailable, continue only from sufficient user-supplied palette data or report the missing input.
