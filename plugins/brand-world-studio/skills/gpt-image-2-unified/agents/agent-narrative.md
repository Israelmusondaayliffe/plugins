# Agent: NARRATIVE

Manga, comics, storyboards, panel sequences. Sequential art with characters, story beats, and narrative progression rendered as a single multi-panel image (or as a storyboard series via SERIES).

**Inheritance**: ADAPT from `nano-banana-unified/agents/agent-create.md` (Sequential Art / Comics sub-template). Panel structure, art-style specification, and dialogue-in-quotes discipline are model-agnostic. Adapted to use GPT Image 2's 8-output consistency (Spud & Garlic 4-page vintage comic demo, OpenAI Seinen manga demo). For multi-page narratives, recommend routing to SERIES; for single-page multi-panel, handle here.

## Scope

NARRATIVE is for sequential storytelling rendered as imagery:

- Manga pages (Seinen, Shonen, Shojo, Seinen gritty)
- Western comic strips and pages (superhero, indie, gag strip, graphic novel)
- Storyboards for film or animation (keyframes with action descriptions)
- Gag panels and meme-style sequential art
- Children's book page layouts (illustration + narrative text)
- Instructional panels (how-to with sequential steps)

For adjacent workflows, route back:
- Single image, no narrative sequence → CREATE
- Full multi-page comic book → SERIES (each prompt a full page)
- Text-first layout → TYPOGRAPHY or EDITORIAL
- Infographic with flow → INFOGRAPHIC

## Known strengths

- Specific manga sub-genres (Seinen, Shonen, Shojo) with appropriate line work and shading
- Multi-panel consistency on a single page (characters, props, setting repeat cleanly)
- Dialogue rendering in speech bubbles at legible scale
- Sound effects and onomatopoeia rendered as part of the composition
- Cross-cultural comic traditions (bande dessinée, manhwa, Western superhero, indie)

## Known weaknesses (flag)

- Character consistency can drift after 8+ panels in a single image
- Face identity may shift slightly between panels, especially for minor characters
- Complex action choreography may collapse into generic poses
- Very small dialogue text in dense panels may degrade

## Format escalation

**Default for NARRATIVE: system prompt operating contract** when the request involves character continuity across multiple panels or pages. The character bible lives in `<visual_dna>` at the top of one batch prompt, every per-panel spec inside `<images>` inherits it, and the model holds identity across the whole batch from one submission.

Auto-detection rules:

- **System prompt format (default)**: multi-panel narrative with named recurring characters, comic-page work, storyboard sequences, manga across multiple panels. Produces 1 batch prompt with the character bible in `<visual_dna>` and per-panel specs in `<images>`. The model returns the entire panel set from one submission.
- **JSON envelope format**: single-panel concept work with strict art-style preservation, dense typography panels with non-Latin scripts, gag strips with strict layout constraints.
- **NL format (fallback)**: single-panel concepts, exploratory narrative beats, "show me 7 different art traditions on the same scene" requests where the panel structure is the variation axis.

State the format chosen in the preamble. Read `references/system-prompt-template.md` Variant B for NARRATIVE-specific framing.

## Workflow

### Step 1: Declare the narrative brief

```
NARRATIVE BRIEF:
Format: [single-page multi-panel, storyboard strip, 2-page spread, 4-page sequence via SERIES]
Art tradition: [Seinen manga, Shonen manga, Shojo manga, indie graphic novel, superhero mainstream, bande dessinée, manhwa, Pixar storyboard, animation keyframe]
Protagonist(s): [name and identity description for each recurring character]
Story or action: [the narrative beat or full arc being rendered]
Panel count: [3, 4, 6, 9 panels on a single page]
Dialogue: [exact text in quotes, or "none," or "sound effects only"]
```

### Step 2: Detect the variation axis

Common NARRATIVE axes:

- Art tradition (7 comic traditions applied to the same story beat)
- Story beat (7 moments from a single arc, freeze characters and style)
- Panel layout (7 compositional arrangements of the same narrative)
- Character framing (7 different ways to frame the same climax: close-up, wide, dramatic low, POV, etc.)
- Mood register (7 tonal interpretations: comedic, tense, melancholic, heroic)
- Audience register (children's book, young adult, adult Seinen, all-ages indie)
- Era (golden-age superhero, 1990s manga, modern webtoon, silent film storyboard)

### Step 3: Map PSGV for NARRATIVE

**PLAN**: Protagonist identity anchor (the visual DNA that must hold across panels), art tradition, panel structure, and story arc. Define these before the brief so the model reasons about consistency upfront.

**SEARCH**: SKIP for most narrative work. Active when the subject requires current factual accuracy (real historical event, real public figure in a narrative context).

**GENERATE**: The narrative brief. Art tradition, protagonist, panel-by-panel beats, dialogue in quotes, line work, color.

**VERIFY**: Before showing output, verify protagonist identity is consistent across all panels. Verify dialogue text is spelled correctly. Verify each panel represents a distinct story beat.

### Step 4: Generate 7 prompts

## Preamble format

```
Format: [single-page panel count, storyboard strip, spread].
Protagonists: [identity anchor for each recurring character].
Story beat: [what happens in this sequence].
Axis varied: [e.g., art tradition across 7 comic styles].
Axes frozen: protagonist identities, story beat, dialogue, panel count.
Format chosen: [System prompt operating contract / JSON envelope / Natural language].
SEARCH active: [yes + topic] OR [no].
```

## Prompt templates: system prompt format (default for multi-panel work)

Each system prompt is a complete batch submission. The character bible sits at the top in `<visual_dna>`, the per-panel specs sit inline in `<images>`, and the user submits the prompt once to receive the full panel set in one coordinated batch.

### Multi-panel manga (system prompt)

```
Generate [N up to 8] separate [aspect ratio] panels as a coordinated sequential manga sequence. All [N] share one visual DNA. Story beat varies across the panels. Character identities, art tradition, line work, palette hold.

<visual_dna>
Protagonist: [exact identity: name, age, hair, signature feature, wardrobe].
Supporting characters: [each with locked features].
Art tradition: [Seinen / Shonen / Shojo].
Visual style: [line work treatment, ink contrast, screentone usage, color treatment if any].
Visual world: [setting, era, palette logic, mood register].
Aspect ratio: [W:H] for every panel.
</visual_dna>

<global_forbidden>
- protagonist feature drift between panels
- supporting character feature drift
- art tradition shift between panels
- ink treatment change between panels
- screentone style change
- color treatment shift
- panel-to-panel quality variance
- story beat repetition
- dialogue paraphrasing
</global_forbidden>

<images>
<image_1 subject="[story beat 1 label]">
[Which characters appear, the action, the panel composition, dialogue in quotes if any.]
</image_1>
<image_2 subject="[story beat 2 label]">
[Spec for beat 2.]
</image_2>
[continue through image_N within the 8-output ceiling]
</images>

<verify>
Before showing output, confirm for ALL [N] panels:
- Character identities consistent across every panel
- Visual style and ink treatment consistent across every panel
- Each panel renders a distinct story beat with no repeats
- Dialogue spelled correctly where present and matches the brief verbatim
- Aspect ratio [W:H] held across every panel
</verify>
```

### Western comic continuity (system prompt)

```
Generate [N up to 8] separate [aspect ratio] panels as a coordinated Western comic page. All [N] share one visual DNA. Story beat and panel composition vary across the panels. Character identities, house art style, color treatment hold.

<visual_dna>
Protagonist: [identity description].
Supporting characters: [each with locked features].
Art style anchor: [Moebius / Mignola / Kirby / Romero / specific contemporary].
Color treatment: [flat comic color / painterly / black and white with gray tones].
Visual world: [setting, era, mood register].
Aspect ratio: [W:H] for every panel.
</visual_dna>

<global_forbidden>
- character identity drift between panels
- art style reinterpretation between panels
- color treatment shift (flat to painterly or vice versa)
- panel layout chaos not requested
- dialogue paraphrasing
- speech bubble illegibility
</global_forbidden>

<images>
<image_1 subject="[story beat 1 label]">
[Which characters appear, the action, the panel composition, dialogue in quotes if any.]
</image_1>
<image_2 subject="[story beat 2 label]">
[Spec for beat 2.]
</image_2>
[continue through image_N within the 8-output ceiling]
</images>

<verify>
Before showing output, confirm for ALL [N] panels:
- Character identities consistent across every panel
- Art style anchor held across every panel
- Color treatment identical across every panel
- Dialogue spelled correctly and matches the brief verbatim
- Speech bubbles legible and well placed
- Aspect ratio [W:H] held across every panel
</verify>
```

### Storyboard sequence (system prompt)

```
Generate [N up to 8] separate [aspect ratio] frames as a coordinated film storyboard. All [N] share one visual DNA. Camera position and story moment vary across the frames. Protagonist identity, visual treatment, palette hold.

<visual_dna>
Protagonist: [identity description].
Supporting characters: [each with locked features].
Visual treatment: [rough pencil / clean keyframe / black-and-white shot list].
Visual world: [setting, era, palette].
Frame format: [aspect ratio, typically horizontal cinema ratio].
Aspect ratio: [W:H, typically 16:9 or 2.39:1] for every frame.
</visual_dna>

<global_forbidden>
- protagonist identity drift between frames
- visual treatment shift between frames
- camera position repetition where distinction was requested
- color creep into a black-and-white treatment
- finished-comic polish on a rough storyboard
- aspect ratio variation
</global_forbidden>

<images>
<image_1 subject="[camera position 1, e.g. wide establishing]">
[Camera direction, action in frame, characters present, treatment specifics.]
</image_1>
<image_2 subject="[camera position 2, e.g. medium two-shot]">
[Spec for frame 2.]
</image_2>
[continue through image_N within the 8-output ceiling]
</images>

<verify>
Before showing output, confirm for ALL [N] frames:
- Protagonist identity consistent across every frame
- Visual treatment identical across every frame
- Each frame represents a distinct camera position or story moment
- Color discipline held (no color in a black-and-white treatment)
- Aspect ratio [W:H] held across every frame
</verify>
```

## Prompt templates: NL fallback (single-panel concepts, exploratory work)

When the request is single-panel or art-tradition variation across the same beat, NL works fine.

### Multi-panel single-page manga (NL)

```
PLAN: Protagonist identity anchor: [name, age, hair, outfit, signature feature]. Art tradition: [Seinen, Shonen, Shojo]. Panel count: [N]. Story arc: [beat-by-beat].
SEARCH: SKIP.
GENERATE: Single-page [Seinen, Shonen, Shojo] manga, [N] panels. Protagonist: [identity details]. Story: [beat-by-beat description per panel]. Panel layout: [vertical scroll, traditional grid, irregular dynamic]. Dialogue: [panel 1: "EXACT TEXT", panel 2: "EXACT TEXT"] or no dialogue. Sound effects: [SFX in quotes] or none. Line work: [heavy ink contrast for Seinen, clean lines for Shojo, speed lines for action]. [Aspect ratio: 2:3 or 3:4].
VERIFY: Before showing output, verify protagonist identity is consistent across all panels. Verify all dialogue text is correctly spelled. Verify each panel shows a distinct narrative beat.
```

### Western comic page (NL)

```
PLAN: Protagonist identity anchor: [identity description]. Art style anchor: [Moebius, Mignola, Kirby, Romero]. Panel layout plan: [grid, splash, widescreen].
SEARCH: SKIP.
GENERATE: [Superhero, indie graphic novel, gag strip] comic page, [N] panels. Protagonist: [identity description]. Story: [panel-by-panel beats]. Layout: [type]. Dialogue in speech bubbles: [exact text per panel in quotes]. Art style: [specific reference]. Color treatment: [flat comic color, painterly, black and white with gray tones]. [Aspect ratio: 2:3 or 3:4].
VERIFY: Before showing output, verify protagonist identity holds across panels. Verify dialogue is legible and correctly placed.
```

### Storyboard strip (NL)

```
PLAN: Scene to be storyboarded. Camera directions per frame: [wide, medium, close-up]. Protagonist identity anchor.
SEARCH: SKIP.
GENERATE: [N]-frame film storyboard showing [action or scene]. Protagonist: [identity]. Each frame: [camera direction: wide, medium, close-up; action: what happens]. Consistent character across frames. Visual style: [rough pencil, clean keyframe, black-and-white shot list]. Action notes beneath each frame: [brief text]. [Aspect ratio: horizontal strip, 16:5 or similar].
VERIFY: Before showing output, verify protagonist identity is consistent. Verify each frame represents a distinct camera position or story moment.
```

### Gag strip (NL)

```
PLAN: Gag structure: setup, escalation, punchline. Style reference anchor.
SEARCH: SKIP.
GENERATE: [N]-panel gag strip in the style of [Calvin and Hobbes, Peanuts, The Far Side, xkcd]. Subject: [premise]. Beats: panel 1 setup, panel 2 escalation, panel 3 punchline. Dialogue: [exact text per panel in quotes]. Line work matching the reference strip. Palette: [black and white, or limited color]. [Aspect ratio: horizontal strip].
VERIFY: Before showing output, verify the punchline panel is structurally distinct from the setup. Verify dialogue is legible.
```

### Children's book page (NL)

```
PLAN: Illustration style anchor. Narrative text placement. Color palette appropriate for age range.
SEARCH: SKIP.
GENERATE: Single page of a children's book for ages [range]. Illustration style: [watercolor, digital painterly, crayon vernacular, Eric Carle collage, Beatrix Potter]. Scene: [what the illustration shows]. Accompanying narrative text: "[EXACT TEXT]" in [placement: top, bottom, integrated]. Color palette: [warm, cool, primary, pastel]. [Aspect ratio: landscape for spread, portrait for single page].
VERIFY: Before showing output, verify narrative text is legible at the stated placement. Verify illustration style matches the reference.
```

### Action sequence (NL)

```
PLAN: Action choreography mapped across panels: [beat 1, beat 2, beat 3, climax]. Protagonist identity anchor. Motion and impact cues defined.
SEARCH: SKIP.
GENERATE: Dynamic action storyboard in [manga, Western comic, animation] style showing [action sequence]. Protagonist: [identity]. Panels depict: [beat 1, beat 2, beat 3, climax]. Motion lines, impact frames, camera movement indicators. Dialogue: minimal or SFX only: "[SFX in quotes]". Art style and ink treatment: [specify]. [Aspect ratio: 2:3 or 1:1 for splash].
VERIFY: Before showing output, verify action escalates across panels. Verify protagonist identity is consistent despite motion and perspective changes.
```

### Silent narrative (NL)

```
PLAN: Full visual storytelling plan. No dialogue. Story carried through action, expression, and environment across panels.
SEARCH: SKIP.
GENERATE: [N]-panel silent comic in [art tradition]. Story: [what happens visually across panels]. Protagonist: [identity]. Each panel carries the narrative through action, expression, and environmental detail. Line work: [specify]. Color treatment: [specify]. [Aspect ratio].
VERIFY: Before showing output, verify the story is readable without any text. Verify protagonist identity holds across all panels.
```

## Verbatim exemplars from the research

OpenAI launch:

```
Japanese manga-style fantasy comic page and typography that celebrates global languages.
```

Pattern: art tradition + subject + typographic layer. Works because GPT Image 2 sustains all three across panels.

```
Manga-style fantasy comic page, Page 1 of 4, showing the protagonist discovering a hidden temple. Use Seinen style with high contrast ink work.
```

Pattern: explicit page count, plot beat, and style specification. "Page 1 of 4" cues the model to sustain visual DNA across sibling outputs via SERIES.

From @RainHuangapp (Chinese Expeditionary Force Storyboard):

```
Cute Chinese Expeditionary Force Storyboard.
```

Pattern: minimal prompt. Model fills in the historical reference and storyboard format. Works for well-known historical subjects; for custom narratives, be more specific.

## Self-validation before output

- [ ] Protagonist(s) described with specific identity markers
- [ ] Story beat or full arc specified
- [ ] Dialogue in quotes (if present) or noted as absent
- [ ] Panel count specified
- [ ] Preamble names axis, frozen axes, and format chosen
- [ ] Preamble states SEARCH as active or SKIP
- [ ] Exactly 7 prompts (in chosen format)
- [ ] Each prompt in its own code block (system prompts in plain ` ``` `, NL in plain ` ``` `)
- [ ] Each prompt encodes PSGV per format (XML blocks for system prompt, labels for NL)
- [ ] Each prompt's verification step checks protagonist consistency and dialogue accuracy
- [ ] Prompts vary along the stated axis only
- [ ] No em-dashes

## Error handling

If the user wants more than 9 panels on a single page, warn about density and consistency risks, and offer to split across SERIES (each prompt = one page of up to 9 panels).

If the protagonist description is vague, ask with `ask_user_input_v0` (options: give detailed description, upload reference image, let the skill generate a protagonist).

For dialogue in non-Latin scripts, confirm the script with the user and flag that typography rendering benefits from Thinking mode.
