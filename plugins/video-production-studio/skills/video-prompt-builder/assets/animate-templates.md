# Prompt Templates

Structural templates for each mode's prompt output. These are scaffolds, not fill-in-the-blanks. Adapt phrasing to the specific brief. The structure ensures consistency. The language adapts to the concept.

Seedance 2.5 scaffolds (one-take, timed beats, staged script, reference binding, edit, extension, ultra-long, join, audio direction) live in `assets/seedance-25-templates.md`. The templates below cover the image-driven sub-modes and the Character Bible Pipeline.

## Image-to-Video Prompt Template

Single reference image animated. Focus on motion, not description.

### Short Clip (single shot, 3-8 seconds)

```
Using the uploaded [explicit description of subject, pose, setting, lighting, and notable details], [describe the primary motion: what moves, in which direction, at what speed]. Camera [camera behavior: push-in, orbit, static, tracking]. [Secondary motion: environmental elements, atmospheric effects, fabric, hair]. [Speed/timing: normal speed, slow-motion percentage, speed ramp]. [Lighting shifts if any]. Maintain [identity anchors: specific features, outfit, expression foundation that must not change]. [Duration]. Do not change aspect ratio.
```

### Multi-Shot Sequence (4+ shots)

Each shot follows this structure:

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects]
Using the uploaded [explicit description], [what moves in this shot]. Camera [behavior]. [Speed/timing]. [Subject identity anchors repeated]. [Transition to next shot]. Do not change aspect ratio.
```

## Keyframe / First & Last Frame Prompt Template

Two reference images: start state and end state. Prompt describes the transformation between them. On Seedance 2.5, this maps to the First & Last Frame mode: the model locks both frames and builds everything in between.

### Variation Format (3-5 variations exploring different interpolation styles)

```
Starting from the uploaded [explicit description of start frame: subject, pose, environment, lighting, mood], transition toward the state shown in the uploaded [explicit description of end frame: what changed, new pose, new environment, new lighting, new mood]. [Transformation style: smooth morph / dramatic shift / physics-based / time-lapse]. [What changes first, what changes last. sequencing the transformation]. [Midpoint description: what the halfway state looks like]. Camera [behavior during transformation]. [Speed/pacing: constant, accelerating, decelerating]. [Duration]. Maintain [persistent elements: what stays constant across both states]. Do not change aspect ratio.
```

### Shot-by-Shot Format (for complex transformations)

```
SHOT 1 ([timestamp]). Anchor Start State
EFFECT: [Subtle motion establishing the start frame is alive]
Starting from the uploaded [explicit start frame description], [minimal motion: breathing, wind, ambient movement]. Camera [static or very subtle]. Maintain [all start-state anchors]. Do not change aspect ratio.

SHOT 2 ([timestamp]). Transformation Begins
EFFECT: [First transformation effect]
[What element begins changing first]. [Direction and speed of change]. Camera [reacts to or reveals the change]. [Start frame anchors still mostly intact]. Do not change aspect ratio.

SHOT N ([timestamp]). Arrive at End State
EFFECT: [Resolution effect]
[Final elements settle into the end state shown in the uploaded end frame description]. Camera [final position]. [All end-state anchors now established]. Do not change aspect ratio.
```

## Multi-Reference Shot Prompt Template (Seedance 2.5 Native)

Seedance 2.5 reads a full staged script natively: one prompt binds up to 30 image references, 10 video references, and 10 audio references (`@Image N`, `@Video N`, `@Audio N`) and generates up to 30 seconds in one pass. The working sweet spot is 1-8 image subjects and 1-5 video/audio subjects; stay inside it.

### Structure

```
[Reference-binding block: one role line plus one exclusion line per tag.]
@Image 1 defines <CharacterName>'s face, hairstyle, and [garment]. Do not use the background.
@Image 2 defines [element]. Do not use [what it must not contribute].
@Video 1 defines only the [motion type] motion. Do not use the person's identity, clothing, or scene from the video.
@Audio 1 is the background music.

[Style and world preamble: visual style, era, setting, lighting register, filmic markers.]

[0-6s] [Stage 1: one primary change, referencing tags as they appear.] End state: [where things are].
[6-14s] [Stage 2.] End state: [...].
[14-24s] [Stage 3, the turn.] End state: [...].
[24-30s] [Stage 4, resolution.] End state: [...].

[Consistency clause: same face, same hairstyle, same outfit, same body type for the entire video.] No subtitles, no background music[, adjust when music is directed via @Audio or (music)].
[Audio line: native syntax (music), <sound effects>, {dialogue}, or ambient-only list.]
Do not change aspect ratio.
```

### Reference Example (Seedance 2.5 idiomatic)

```
@Image 1 defines <Chef>, a small husky in a white chef hat. Do not use the background.
@Image 2 defines the copper-pot kitchen set. Do not use any characters from it.
@Audio 1 is the warm jazz piano score.

Cinematic 3D render, warm golden-hour restaurant kitchen, shallow depth of field, 24fps.

[0-6s] <Chef> stirs a copper pot on the stove, steam rising. End state: he lifts the spoon to taste.
[6-14s] He tastes, eyes widen, and barks one command toward the pass. End state: three plates lined up on the counter.
[14-24s] A waiter sweeps past collecting the plates; the camera tracks the plates through the kitchen bustle. End state: the last plate lands on the pass under warm light.
[24-30s] <Chef> leans into frame, looks straight into the lens, and gives one approving nod. End state: hold on his face, steam drifting.

Same face, same fur pattern, same chef hat for the entire video. No subtitles.
(music: @Audio 1 warm jazz piano) <kitchen clatter, sizzling, soft laughter>
Do not change aspect ratio.
```

### Rules

- One prompt in one code block. Not N prompts.
- Every tag gets a role line AND an exclusion line. The exclusion line stops reference leaks.
- Tag numbering follows upload order. Seedance 2.0's lowercase `@image1` style still parses; stay consistent within one prompt.
- One primary change per stage, an explicit end state per stage. Time ranges are budgets.
- Preamble carries style, world, and filmic markers.
- Audio uses the native syntax: `(music)`, `<sound effects>`, `{dialogue}`. For clean footage: `[SOUND] Strictly only naturally occurring sound and foley, no music allowed.`
- Always close with "Do not change aspect ratio."
- Do NOT use the "Using the uploaded [description]..." prefix. That convention is for other sub-modes.

### Reference Mapping Block (shown in the response, NOT in the prompt)

Above the prompt code block, present a mapping so the user knows which upload corresponds to which tag:

```
REFERENCE MAPPING:
@Image 1 = [description of first uploaded image] (role: ..., excludes: ...)
@Image 2 = [description of second uploaded image] (role: ..., excludes: ...)
@Video 1 = [uploaded video description] (role: motion reference)
@Audio 1 = [uploaded audio description] (role: score / beat sync)
```

This mapping is for the user's reference. It is not part of the Seedance prompt itself.

## Extended Reference Tags

Beyond `@Image N`, Seedance 2.5 prompts use:

**`@Video N`**: video reference. Motion, camera behavior, pacing to inherit; a clip to extend, edit, or join. "Camera motion follows @Video 1. Do not use the people or scene from the video."

**`@Audio N`**: audio reference. Beat sync, ambience, voice, or BGM. "The rhythm of @Audio 1 drives the cut points."

**`@Images 6-10`**: group tag for a batch sharing one role (e.g. crowd extras, product angles).

**`@clay render 1`**: untextured 3D blockout from Maya/Blender that locks camera movement and blocking while image references carry the look. "Replace the white humanoid model with @Image 1's knight." Coarse blockouts work better than fine ones; avoid limbed figures unless the full limb motion is spelled out.

Reference all of these in the REFERENCE MAPPING block using the same pattern.

## Video Extension Template (Seedance 2.5)

Extension grows a clip of 30s or less by 4-30 seconds per pass (60s final ceiling). The prompt covers ONLY the new segment; original frames stay untouched. Full workflow guidance (controlled reveal, action relay) is T6 in `assets/seedance-25-templates.md`.

```
[What happens in the new segment only, written as a continuation of the final frame.] Camera: [movement]. Style: [maintain established style]. Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air. Audio: [diegetic continuation]. Do not change aspect ratio.
```

Example: "The phone reforms back into its shape and lands softly on the ground. Camera: slow push-in following the reformation. Style: maintain cinematic realism. Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air. Audio: subtle reverse-shatter crystalline tones settling into a gentle impact thud. Do not change aspect ratio."

For chained continuation of a prior generation referenced as a tag, the same shape applies with `Continue from @Video 1.` opening the prompt.

## JSON-Formatted Seedance Prompt (Optional)

Some users prefer structured JSON for Seedance prompts. Offer this variant only when the user explicitly requests JSON format or API-style structure.

```json
{
  "references": [
    {"tag": "@Image 1", "role": "Chef husky identity", "exclude": "background"},
    {"tag": "@Audio 1", "role": "jazz score"}
  ],
  "style": "cinematic 3D render, warm golden hour kitchen",
  "stages": [
    {"time": "0-6s", "action": "stirs a copper pot", "end_state": "lifts spoon to taste"},
    {"time": "6-14s", "action": "tastes and barks a command", "end_state": "three plates on the counter"},
    {"time": "14-24s", "action": "waiter sweeps the plates to the pass", "end_state": "last plate lands"},
    {"time": "24-30s", "action": "chef nods into the lens", "end_state": "hold on face"}
  ],
  "constraints": "same face, same fur, same hat for the entire video; no subtitles",
  "audio": "(music: @Audio 1) <kitchen clatter, sizzling>",
  "duration": "30s",
  "aspect_ratio": "preserve"
}
```

The natural-language template remains the default. JSON is only for users who ask for it.

## Role-Based Multi-Reference Prompt Template (Model-Agnostic)

For Kling, Veo, Sora, and other models that accept role-assigned reference images (subject reference, style reference, environment reference, mood reference, and structural-guide for storyboards that direct the sequence without being rendered).

### Shot Prompt Structure

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects]
Using the subject from the uploaded [explicit description of subject reference: identity, features, clothing, pose], placed in the environment from the uploaded [explicit description of environment reference: space, architecture, lighting, atmosphere], rendered in the visual style of the uploaded [explicit description of style reference: color palette, grain, contrast, mood, photographic quality]. [What moves in this shot]. Camera [behavior]. [Speed/timing]. [How the references integrate: which dominates, where they blend]. Maintain [identity anchors from subject reference]. [Transition to next shot]. Do not change aspect ratio.
```

### With Structural Guide Reference

When one of the uploaded references is a storyboard composite, panel grid, or production board (structural-guide role), use this variant. The structural-guide image is read for sequence structure only and is never rendered in the output.

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects]
Using the subject from the uploaded [explicit subject description], placed in the environment from the uploaded [explicit environment description], rendered in the visual style of the uploaded [explicit style description], following the panel-by-panel sequence shown in the uploaded [explicit storyboard description].

CRITICAL: Do not render the storyboard image in the final video. Use the storyboard only as a panel-by-panel structural guide. The final video does not show panel borders, panel numbers, timing brackets, annotation arrows, or grid layout.

[Per-shot beat blocks describing what happens. Each mirrors one panel from the storyboard.]

Maintain identity, style, and environment as referenced. Do not change aspect ratio.
```

If only two roles plus structural guide are present (no environment reference, for example), adapt the opening sentence accordingly. The structural guide and do-not-render directive remain mandatory.

If only two references (e.g., subject + style, no separate environment):

```
Using the subject from the uploaded [explicit subject description], rendered in the visual style of the uploaded [explicit style description]. [Environment described in text since no environment reference]. [Motion, camera, effects]. Maintain [identity anchors]. Do not change aspect ratio.
```

## Character Bible Pipeline Template (Stage D, Seedance 2.5 native multi-sheet)

Use this template for the Character Bible Pipeline sub-mode of ANIMATE. The full A-B-C-D doctrine lives in `references/character-bible-pipeline.md`. This template covers the Stage D Seedance prompt only.

The prompt uses role-aware `@`-tags. `@Image 1` is the persistent identity anchor that renders as the subject across every shot. Additional tags are consistency references (character sheet, wardrobe sheet, emotion sheet) or the structural guide (storyboard). Reference tags do not render. The do-not-render directive is mandatory and must name the specific visual artifact to suppress.

### Stage D Prompt Structure

```
SUBJECTS:
@Image 1 is the main character. [Compact character description: who they are, canonical look, identity markers from the hero shot, build, hair, signature wardrobe.] Use @Image 1 as the persistent visual anchor across every shot. Every shot must show this exact character with this exact face, build, and signature look.

REFERENCES (consistency only, never rendered as standalone images):
@Image 2 is the character turnaround sheet. Use it to keep face, head shape, body proportions, and hair consistent across angles. Do not render @Image 2 in the video. Do not show multi-view turnaround layouts, character sheet boxes, view labels, or any sheet-style framing.
@Image 3 is the wardrobe sheet. Use it to keep clothing, materials, colors, and accessories consistent. Do not render @Image 3 in the video. Do not show wardrobe breakdowns, garment labels, fabric swatches, or any catalog-style layout.
@Image 4 is the emotion sheet. Use it to keep facial expressions within the character's emotional range. Do not render @Image 4 in the video. Do not show expression grids, emotion labels, or any expression-sheet framing.

STRUCTURAL GUIDE (do not render, sequence reference only):
@Image 5 is the storyboard composite. Follow the panel-by-panel sequence shown in @Image 5 exactly. Each panel is one full shot in the video timeline. Do not render @Image 5 in the video. The final video does not show panel borders, panel numbers, timing brackets, annotation arrows, grid layout, or any storyboard-style framing.

ENVIRONMENT:
[Setting description: where the action happens, lighting register, atmosphere.]

STYLE:
[Visual style of the FINAL VIDEO. This is the cinematic finish, separate from any reference image's drawing style. Storyboards are sketchy and simplified. The final video should NOT inherit that look. State the final style explicitly: e.g., "cinematic 3D animation in Pixar / Donotopia register, soft volumetric lighting, warm grade, shallow depth of field," or "live-action cinematic, 35mm anamorphic, film grain, naturalistic color."]

[Shot 1] [0-Xs] [Action mirroring panel 1 of @Image 5]. The character (@Image 1) [specific action]. Camera: [from panel 1: lens, angle, distance, move]. End state: [where things are]. SFX: <[from panel 1]>.
[Shot 2] [Xs-Ys] [Action mirroring panel 2 of @Image 5]. The character (@Image 1) [specific action]. Camera: [from panel 2]. End state: [...]. SFX: <[from panel 2]>.
[Shot 3] [...continued through each panel of the storyboard...]
[...]
[Shot N] [(N-1)t-Nt] [Final shot, mirroring panel N of @Image 5]. The character (@Image 1) [closing action]. Camera: [from panel N]. End state: [...]. SFX: <[from panel N]>.

GLOBAL CONSTRAINTS:
Maintain the exact character from @Image 1 across every shot. Same face, same hairstyle, same outfit, same body type for the entire video. Cross-check face, body, and hair against @Image 2. Cross-check wardrobe against @Image 3. Cross-check expression range against @Image 4. Follow exact panel order from @Image 5.
No panel borders, no annotations, no timing brackets, no panel numbers, no grid layout, no on-screen text bleed from any reference image. The final video shows only the cinematic scene.
Consistent lighting, environment, and character identity across all shots. No deformation. Stable proportions. Natural motion physics. No subtitles.

AUDIO:
[Native audio syntax: (music), <sound effects>, {dialogue}. Or ambient-only list, or the [SOUND] foley-only directive.]

Do not change aspect ratio.
```

### REFERENCE MAPPING Block (above the prompt, NOT inside it)

Present the mapping in the response above the prompt code block. This is for the user's reference, not part of the Seedance prompt itself.

```
REFERENCE MAPPING:
@Image 1 = [description of character hero shot, role: persistent identity anchor, RENDERS as subject]
@Image 2 = [description of character sheet / turnaround, role: consistency reference, DOES NOT RENDER]
@Image 3 = [description of wardrobe sheet, role: consistency reference, DOES NOT RENDER]
@Image 4 = [description of emotion sheet, role: consistency reference, DOES NOT RENDER]
@Image 5 = [description of storyboard composite, role: structural guide, DOES NOT RENDER]
```

Drop any tag row whose asset is not in play. Adjust tag numbers to match actual upload order.

### Minimum Viable Variant (character + storyboard only)

When the user has only a character image and a storyboard (no separate bible sheets), collapse to two tags:

```
SUBJECTS:
@Image 1 is the main character. [Compact character description.] Use @Image 1 as the persistent visual anchor across every shot.

STRUCTURAL GUIDE (do not render, sequence reference only):
@Image 2 is the storyboard composite. Follow the panel-by-panel sequence shown in @Image 2 exactly. Each panel is one full shot. Do not render @Image 2 in the video. Do not show panel borders, panel numbers, timing brackets, annotation arrows, grid layout, or any storyboard-style framing.

ENVIRONMENT: [...]
STYLE: [...]

[Shot 1] [0-Xs] [Action mirroring panel 1 of @Image 2]. The character (@Image 1) [action]. Camera: [...]. End state: [...]. SFX: <[...]>.
[...]

GLOBAL CONSTRAINTS:
Maintain the exact character from @Image 1 across every shot. Same face, same hairstyle, same outfit, same body type for the entire video. Follow exact panel order from @Image 2. No panel borders, no annotations, no on-screen text bleed.

AUDIO: [...]
Do not change aspect ratio.
```

### Stage A / B / C Companion Templates (handoff prompts)

When Stages A, B, or C are not yet complete, ship one prompt per missing stage as ADDITIONAL code blocks above the Stage D prompt. Each is a brief the user pastes into the relevant image model.

**Stage A: Character hero shot prompt (target model: Nano Banana / GPT Image 2 / Midjourney)**

```
Create a single character hero shot. [Character: who they are, age, build, ethnicity, key identity markers, wardrobe, accessories.] [Pose: canonical pose that establishes silhouette.] [Lighting: register.] [Background: neutral so the character is the focus, or specific setting if appropriate.] [Style: cinematic 3D / illustrative / photoreal / etc.] [Aspect ratio: 3:4 portrait or 16:9 cinematic.] Render high detail, professional character design. This image becomes the persistent identity anchor for downstream video generation.
```

**Stage B: Character bible composite prompt (target model: GPT Image 2)**

```
PLAN: Single composite character bible sheet for [character name]. Multi-region layout containing: full-body turnaround (front, 3/4, side, back, 3/4 back), expression study (6-8 core emotions: [list]), wardrobe breakdown (key garments with detail callouts), and cinematic portrait (hero pose). All regions share one visual DNA: same face, same build, same wardrobe baseline, same lighting register.

GENERATE: Design a single 16:9 production-board image presenting a complete character bible for [character description]. Layout: clean grid-based design, labeled sections. Include character + styling reference (full-body multiple angles, plus close-ups), wardrobe breakdown with material detail, expression study grid showing emotional range, and one cinematic portrait at hero scale. Style: [cinematic 3D / illustrative / photoreal]. Background: clean white or neutral gray so character work dominates. Professional pre-production aesthetic, like a Pixar / DreamWorks character bible.

VERIFY: Before showing output, verify identity (face, build, hair) is identical across every region. Verify wardrobe is consistent across turnaround views. Verify expressions are distinct and non-repetitive. Verify layout reads cleanly as a designed sheet, not a collage.
```

If the user wants four separate sheets instead of one composite, route to gpt-image-2-unified SERIES mode and skip this Stage B prompt. SERIES handles single-axis variation (turnaround alone, expressions alone, wardrobe alone) more cleanly. On Seedance 2.5, separate sheets are also the higher-fidelity choice: the model reads separate angles better than collages, and the reference budget accommodates them.

**Stage C: Storyboard composite prompt (target model: GPT Image 2)**

```
PLAN: Single storyboard composite sheet for [project name]. Grid layout, [N: typically 8-12, up to 15] panels in sequence. Each panel shows one beat of the action. Style: minimal stick-figure choreography OR simplified character renders OR ink-wash silhouette (pick one), clean lines. Panels include camera grammar tokens (lens, angle, distance, move), timing brackets, SFX cues, and brief action notes.

GENERATE: Design a single [16:9 or 4:3] storyboard sheet with [N] sequential panels showing the following beats: [beat 1 description, beat 2 description, ... beat N description]. Each panel labeled with number, timing bracket (e.g., 0-2s, 2-4s), camera grammar (e.g., WIDE / HANDHELD 28mm, ECU PUSH IN 85mm), and brief SFX note. Use [stick-figure / simplified render / ink-wash] style for the choreography drawings. Layout: clean grid, panels separated by clear borders. This is a pre-production tool, not the final video aesthetic.

VERIFY: Before showing output, verify panel count matches [N]. Verify each panel has visible timing bracket, camera grammar, and SFX cue. Verify the sequence reads as a coherent narrative arc. Verify panels are styled for legibility (not cluttered).
```

If the user wants the canonical Stage 1 storyboard with full previs grammar (colored motion arrows, distinct camera tokens, SFX cue layering), route to previs-to-sequence STORYBOARD-FROM-TEXT or STORYBOARD-FROM-IMAGE. That skill is the deeper authority for Stage 1.

## BUILD Shot Prompt Template

Text-only brief, no reference images. Full description of the visual.

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects if stacked]
[Detailed description of what is visible: subject, environment, lighting, composition]
[Camera behavior: angle, movement, lens, position]
[Speed/timing: percentages, durations, ramp directions]
[Subject appearance details repeated for character consistency]
[Atmospheric and environmental details]
[Transition out: how this shot exits and connects to the next]
```

## Supporting Section Templates

### Effects Inventory Entry

```
[N]. [EFFECT NAME] (used [count]x). Shots [list]. [One-line role description].
```

### Density Map Entry

```
[timestamp range] = [HIGH/MEDIUM/LOW] DENSITY ([brief effect list]. [count] effects in [duration])
```

### Energy Arc Structure

```
Act 1 ([time range]): [ENERGY LEVEL]. [What happens and why].
Act 2 ([time range]): [ENERGY LEVEL]. [What happens and why].
Act 3 ([time range]): [ENERGY LEVEL]. [What happens and why].
```

## Timeline Brackets Template (Seedance native structure)

Structured format for multi-shot prompts. Cleaner than "SHOT 1 / SHOT 2" labels. Matches the pattern in the highest-engagement Seedance prompts, and on 2.5 the brackets land where written.

```
Style: [STYLE_FAMILY + cinematic markers: 35mm anamorphic, 24fps, film grain]. Duration: [Ns].
[0-8s] Shot 1: [Shot name]. [Subject + action]. Camera: [movement]. Lighting: [description]. End state: [...]. [Dialogue cue if any].
[8-16s] Shot 2: [Shot name]. [Subject + action]. Camera: [movement]. Lighting: [description]. End state: [...].
[16-24s] Shot 3: [Shot name]. [Subject + action]. Camera: [movement]. Lighting: [description]. End state: [...].
[24-30s] Shot 4: [Shot name]. [Closing beat]. End state: [...].
Constraints: consistent faces and clothing, no deformation, realistic physics, stable proportions. Same face, same hairstyle, same outfit for the entire video. No subtitles, no background music.
Audio: [ambient], [foreground sound], [music or score, or the [SOUND] foley-only directive].
Do not change aspect ratio.
```

Use this when the user requests: precise timing, a single-prompt multi-shot output, Seedance native syntax, or a time-coded script. Scale the bracket count to the duration; the four-beat 30s map (0-6, 6-14, 14-24, 24-30) is the default rhythm when the story has no natural structure.

## Positive Constraints Library

Drop-in consistency clauses for any prompt. Pick the one matching the context.

**Character-driven:**
```
Consistent faces, clothing, and hairstyles throughout without deformation, drift, or artifacts.
```

**Long-video anti-drift (verbatim 2.5 boilerplate):**
```
Same face, same hairstyle, same outfit, same body type for the entire video.
```

**Physics-heavy:**
```
Consistent gravity, realistic material response, accurate collision, no floating objects.
```

**Portrait / subtle motion:**
```
Clear undeformed face, normal human body structure, stable proportions, rich skin and fabric detail.
```

**Multi-shot coherence:**
```
Consistent lighting, environment, and character identity across all shots.
```

**Crowd variety:**
```
Background people differ in clothing color, hairstyle, and facial features; their movement is not perfectly synchronized.
```

## Diegetic Audio Library

Standard audio outro lines by context. On Seedance 2.5, wrap in the native syntax where useful: `(music)`, `<sound effects>`, `{dialogue}`.

- **Action:** "Footsteps, fabric rustle, weapon impact, distant echo."
- **Nature:** "Wind through leaves, flowing water, ambient birdsong."
- **Urban:** "Distant traffic, neon hum, footfalls on wet pavement."
- **Interior / intimate:** "Soft breathing, room tone, faint score."
- **Commercial / product:** "Subtle impact, material chime, ambient hum."
- **Clean footage kill switch:** "[SOUND] Strictly only naturally occurring sound and foley, no music allowed."
