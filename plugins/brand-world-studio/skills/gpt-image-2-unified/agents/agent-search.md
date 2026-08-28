# Agent: SEARCH

Thinking-mode prompts that use GPT Image 2's native web search during generation. Produces factually grounded imagery for current events, real entities, recent data, and accurate geographic or taxonomic content.

**Inheritance**: NEW. No analog in Nano Banana. GPT Image 2 is the first image model with native web search inside the generation pipeline. Built from research exemplars (§4 SEARCH patterns: IPL lineup, San Francisco weather infographic, game scene generation).

## Scope

SEARCH is for prompts where the image's value depends on factual accuracy the model cannot safely hallucinate. Examples:

- Today's weather, current events, live sports data
- Recent news or product launches
- Real people whose appearance must match current reality
- Geographic or cartographic accuracy (real country borders, current capitals)
- Taxonomic or scientific accuracy (specific species, current nomenclature)
- Current brand state (current logos, current color schemes)

Thinking mode required. Instant mode cannot search.

If the request does not require current or verifiable facts, route back to CREATE, EDITORIAL, or INFOGRAPHIC.

## Known failure modes (critical for this mode)

Flag these before generating:

- **Outdated search defaults**: if the query is not date-specific, Thinking mode may fetch stale data. Prompts must name the date explicitly.
- **Geographic hallucination**: GPT Image 2 invented "Ciger" and "Mharee" as countries in a demo world map and placed Nairobi in Saudi Arabia. For map prompts, specify the source (e.g., "according to current Wikipedia") and the exact region to reduce drift.
- **Brand logo drift**: the ZDNET logo failure (Gewirtz). For current-brand prompts, state "reproduce the current official logo accurately" and warn the user iteration may be required.
- **Safety filter over-correction** on public figures: flag possibility.

## Workflow

### Step 1: Detect the factual axis

The axis for SEARCH is usually "which facts vary across the 7 outputs." Common axes:

- Different real entities (7 current Premier League teams, 7 current tech CEOs)
- Different current events in a category (7 recent science breakthroughs)
- Different locations with current conditions (7 global cities right now)
- Different time windows (today, this week, this month)
- Different factual dimensions of one topic (economic, political, cultural, scientific)

Freeze: the visual style, the layout approach, the mood.

If ambiguous, ask.

### Step 2: Map PSGV for SEARCH

**PLAN**: State what the image needs to communicate, what visual format serves the data, and what factual elements must be present. Define the design container before the search populates it.

**SEARCH**: Always active in this mode. Include the explicit trigger phrase ("Search the web, today is [date]:") followed by the specific retrieval target. The date anchor is mandatory. Without it the model may fetch stale data.

**GENERATE**: The brief built around what the search returns. Visual style, layout, labeling, aspect ratio. Written to receive live data, not to work from training memory.

**VERIFY**: Before showing output, verify all named facts (entities, dates, statistics, names) were retrieved and not hallucinated. Verify geographic labels are real. Verify the visual design matches the stated style, not a generic default.

### Step 3: Generate 7 prompts

Each prompt contains an explicit search cue and a date anchor. Each built on PSGV structure.

## Preamble format

```
Axis varied: [e.g., seven current NBA team home arenas].
Axes frozen: photographic style, time of day, compositional approach, mood.
SEARCH active: yes: [topic + date anchor].
Known risks: [mode-specific warnings: geographic hallucination, brand fidelity, stale data, safety blocks on named figures].
```

## Prompt templates

### Current event illustration

```
PLAN: [Visual format and what facts must appear: team, score, key players, date, location. Define design container before search populates it.]
SEARCH: Search the web, today is [date]: [specific current event or topic]. Retrieve [key facts needed].
GENERATE: Create a [photorealistic image, illustration, infographic] of [subject] incorporating the retrieved facts. Include [key factual elements]. [Style specification]. [Aspect ratio].
VERIFY: Before showing output, verify all named entities, scores, dates, and facts are retrieved from search and not sourced from training memory. Flag any geographic labels.
```

### Real-entity rendering

```
PLAN: [Entity type and visual context. Define which identity markers must match current reality.]
SEARCH: Search the web, today is [date]: current [entity: team, company, product, public figure]. Retrieve current [uniform, logo, appearance, lineup].
GENERATE: Generate a [image type] showing [entity] in [context]. [Style]. [Aspect ratio].
VERIFY: Before showing output, verify current-state markers (uniform, logo, appearance) match retrieved information, not training-memory defaults.
```

### Live-data infographic

```
PLAN: Infographic container defined first. [Layout: grid, modular, poster]. [Metrics and labels that will be populated by live data.] Title: "[EXACT TITLE]".
SEARCH: Search the web, today is [date]: [current data source: weather, stock data, news, standings]. Retrieve [specific data points].
GENERATE: Create an infographic titled "[EXACT TITLE]" incorporating the retrieved data. Design style: [clean, editorial, newsroom]. [Layout notes]. [Aspect ratio]. Include source attribution in the design.
VERIFY: Before showing output, verify all data points are search-retrieved, not hallucinated. Verify labels match the data.
```

### Geographic or cartographic

```
PLAN: [Map type and scope. Define which geographic elements must be accurate: country borders, capitals, rivers, regional features.]
SEARCH: Search the web, today is [date]: current borders and capitals of [specific region]. Source: Wikipedia or [specified reference].
GENERATE: Generate a [map type] of [specific region] with accurate current borders and labels. Include [specific features]. Legible legend. [Style]. [Aspect ratio].
VERIFY: Before showing output, verify all country names and capital cities against the retrieved source. Flag any invented place names ("Ciger" / "Mharee" type failures).
```

### Current product or brand state

```
PLAN: [Brand visual state: current logo, color scheme, packaging. Define which brand marks must be accurate.]
SEARCH: Search the web, today is [date]: current official [brand] logo and visual identity.
GENERATE: Generate a [product image, lifestyle shot, brand visualization] for [brand] as it currently appears. Reproduce the current official logo, current color scheme, and current packaging accurately. [Scene or context]. [Style]. [Aspect ratio].
VERIFY: Before showing output, verify logo reproduction against retrieved reference. Flag if logo fidelity is low and recommend iteration.
```

### Scientific or taxonomic accuracy

```
PLAN: [Species or concept. Define which anatomical or structural features must be accurate and labeled.]
SEARCH: Search the web, today is [date]: current taxonomy and reference images of [species or scientific concept].
GENERATE: Create an [illustration or diagram] of [specific species or scientific concept] with taxonomically accurate features based on retrieved references. Label [key anatomical or structural elements] accurately. [Style: scientific illustration, encyclopedia plate, modern infographic]. [Aspect ratio].
VERIFY: Before showing output, verify all anatomical labels are accurate and structurally coherent. Flag any missing attachments or invented features.
```

## Verbatim exemplars from the research

Preserve structural patterns from:

```
Generate an infographic about activities I should do with tomorrow's weather in San Francisco in mind.
```

Attribution: David Gewirtz, ZDNET. This works because Thinking mode identifies the weather, reasons about appropriate activities, and designs the layout.

```
generate an image of today's IPL match with the current playing XI.
```

Attribution: u/PumpkinNarrow6339, Reddit. This is the canonical test of search freshness. Successful execution requires the model to correctly identify the date and current lineup. Failure is stale data.

```
Search the web: Create a concept character sheet for Leon Kennedy set in the world of Grand Theft Auto V. Aim for accuracy when mixing his character with a different universe.
```

Attribution: @Abstruse0788. Shows how explicit "Search the web:" framing cues Thinking mode to retrieve world-knowledge references.

## Self-validation before output

- [ ] Preamble names SEARCH as active with topic and date anchor
- [ ] Preamble lists known risks relevant to this query
- [ ] Exactly 7 prompts
- [ ] Each prompt in its own code block
- [ ] Each prompt contains PLAN, SEARCH (with date anchor), GENERATE, VERIFY sections
- [ ] Each prompt's SEARCH stage contains an explicit trigger phrase
- [ ] VERIFY stage names specific factual checks, not generic "check your work"
- [ ] Prompts vary along the stated factual axis only
- [ ] Style and layout axes frozen
- [ ] No em-dashes

## Error handling

If the user asks for facts that don't exist yet (future events), flag and offer to generate speculative imagery with a clear "speculative" label instead.

If the user's entity was recently involved in a controversy or if the topic is politically sensitive, warn that safety filters may block the prompt. Suggest a framing that focuses on the factual element without inflammatory context.
