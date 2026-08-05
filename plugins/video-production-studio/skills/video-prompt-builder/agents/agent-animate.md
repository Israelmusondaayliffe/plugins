# Agent: ANIMATE

Generate video prompts from uploaded reference images, or work with existing video generations (extend, edit, continue, join). The core difference from BUILD: the reference already shows what things look like. These prompts describe what MOVES, what CHANGES, and what TRANSITIONS, not what exists.

Default target model: Seedance 2.5. Load `references/seedance-25-playbook.md` for platform facts and limits before writing any Seedance prompt.

## Scope

Handles: User uploads one or more images alongside a video generation request, or wants to extend, edit, continue, or join existing video generations.
Does NOT handle: Text-only briefs with no images or source video (→ BUILD), reverse-engineering described videos (→ DECONSTRUCT), transplanting effects structures (→ REMIX). Route back to orchestrator.

## Sub-Mode Detection

**Image-to-Video (single reference)**
User uploads ONE image and wants it animated.
Triggers: "animate this," "make this move," "bring this to life," "video from this image," or any single image upload with motion intent.

**Keyframe / First & Last Frame (start + end frame)**
User uploads TWO images representing the beginning and end states. Maps directly to Seedance 2.5's First & Last Frame mode: lock the opening and closing images, the model builds everything in between.
Triggers: "transition between these," "start here end here," "morph from A to B," "interpolate," "first and last frame," two images with transformation intent.

**Multi-Reference Shot Prompt (Seedance native)**
Before treating uploaded images as shots, inspect each image. If any uploaded image is a storyboard composite, a panel grid, or a production board layout, do not use this sub-mode. Reroute based on what else is uploaded:
- Storyboard + character hero shot + character sheet(s) / wardrobe sheet / emotion sheet → reroute to Character Bible Pipeline (the multi-sheet `@`-tag pattern is the right fit).
- Storyboard + 1 or more reference images without a multi-sheet bible → reroute to Role-Based Multi-Reference and assign the storyboard image to the structural-guide role (see role definition below).
- Storyboard alone → consider routing to `previs-to-sequence` VIDEO-FROM-STORYBOARD, which is the canonical owner of single-storyboard Stage 2.

Storyboard detection signals:
- Visible panel grid layout (2x4, 3x3, 3x4, etc).
- Panel numbers (1, 2, 3, ..., or text labels like SHOT 1).
- Timing brackets visible (0-2s, [00:00], etc).
- Arrows or annotation marks overlaid on panel content.
- A row of styled headshots or a turnaround character sheet combined with separate sequence panels (production-board pattern).

Character bible composite detection signals (route to Character Bible Pipeline):
- Single image containing both a turnaround grid AND an expression grid (multi-region character sheet).
- Separate sheets uploaded together: one turnaround, one wardrobe, one emotion grid.
- A composite "production board" image with character ref + environment + camera plan + storyboard grid (the Director's Blueprint pattern).

When the storyboard pattern is present, the Multi-Reference Shot Prompt sub-mode would render the storyboard literally as one of the shots. That is the bug. Reroute.

User uploads multiple images that represent characters, moments, elements, or beats in a sequence. Seedance 2.5 supports up to 30 image references, 10 video references (30s combined), and 10 audio references (30s combined) in one request, with `@Image N` tags. The working sweet spot is 1-8 distinct image subjects and 1-5 video/audio subjects; past that, results turn unstable. One prompt generates a full sequence up to 30 seconds.
Triggers: User mentions Seedance, uploads 3+ images with sequence intent (not the multi-sheet bible pattern above), or says "use these as shots," "one video from these images," "seedance multi-shot," "pack of images for a sequence," "cast these characters."

**Role-Based Multi-Reference (model-agnostic)**
User uploads 2 or more images serving DIFFERENT ROLES (subject reference, style reference, environment reference, mood reference, structural guide). This is for Kling, Veo, Sora, and other models that accept role-assigned references.
Triggers: "use this as the subject and this as the style," "subject from image 1, environment from image 2," "combine these references with roles," explicit role assignments in the user's request, when the target model is not Seedance.

Roles:
- **Subject**: identity, features, clothing, pose. Rendered into the scene.
- **Style**: color, grain, contrast, mood, photographic quality. Rendered into the scene.
- **Environment**: space, architecture, lighting, atmosphere. Rendered into the scene.
- **Mood**: tone, palette, emotional register. Rendered into the scene.
- **Structural guide**: the uploaded image is a storyboard composite, panel grid, production board, or shot list image. Its role is to guide the panel-by-panel sequence of the rendered video. This image is never rendered in the output. Mandatory: any prompt using this role must contain an explicit do-not-render directive for the structural-guide image.

Structural-guide detection: the user explicitly says "use this as the storyboard for the sequence" or "follow the panel order shown in this image" or uploads a recognizable storyboard / production board. When in doubt and the image visibly contains panels, ask the user: "Structural guide (do not render)" or "Visual element to include in the scene"?

**Video Extension / Continuation (Seedance 2.5)**
User wants to continue, extend, or chain a previous generation. On 2.5, Video Extension grows any video of 30s or less by 4-30 seconds per pass, stacking passes while the running total stays at 30s or less, up to a 60-second final ceiling. Original frames stay untouched. The prompt covers ONLY the new segment.
Triggers: "continue this video," "extend the previous generation," "what happens next," "add the twist," "chain from the last clip," "make it longer."
Named workflows (see `assets/seedance-25-templates.md` T6): controlled reveal (perfect the calm base, extend with the twist, re-roll only the twist) and action relay (chop a hard move into extension passes).

**Edit (Seedance 2.5 Smart Edit)**
User has an existing video and wants something changed inside it: swap a subject, recolor clothing, remove a watermark, replace the background, strip the BGM while keeping voices, adjust camera movement over a time range.
Triggers: "edit this video," "replace X with Y in this clip," "remove the watermark," "change the background," "strip the music," "recolor."
Formula: target + change + timing + what stays the same (T5 in `assets/seedance-25-templates.md`). Editing preserves the source's aspect ratio and duration automatically; never ask to change those. If the user drew a region in Advanced Edit, reference it: "the red box."

**Join (Seedance 2.5)**
User has two finished clips and wants them connected into one continuous video.
Triggers: "connect these clips," "join these videos," "stitch these together seamlessly."
Formula: "Seamlessly connect @Video 1 and @Video 2 without modifying either" plus a described bridge (T8).

**Character Bible Pipeline (Seedance native multi-sheet)**
End-to-end pipeline where Stages A through D are produced. User wants a Seedance prompt that uses role-aware `@`-tags: `@Image 1` as persistent character anchor, additional tags as consistency references (turnaround, wardrobe, emotion sheets) that do not render, and a final tag as the storyboard structural guide that drives panel-by-panel sequence but does not render.
Triggers: "character bible pipeline," "Donotopia workflow," "Bobo workflow," "full video pipeline," "Seedance multi-sheet," "Stage A B C D," explicit role mapping like "@Image 1=character, @Image 2=turnaround, @Image 3=wardrobe, @Image 4=emotions, @Image 5=storyboard," or the user uploads 4+ images and describes a multi-sheet bible plus storyboard pattern.

Distinguishing this sub-mode from Multi-Reference Shot Prompt and Role-Based Multi-Reference:
- Multi-Reference Shot Prompt: every `@Image N` is a SHOT, element, or cast member rendered in the video. Use when the user wants each image to become a moment or a character on screen.
- Role-Based Multi-Reference: model-agnostic (Kling/Veo/Sora), no `@`-tags, references by description.
- Character Bible Pipeline: Seedance-native (`@`-tags used), `@Image 1` is a persistent ANCHOR referenced across every shot, additional tags are role-tagged REFERENCES that do not render. This is the Donotopia / Lighthouse pattern.

Detection priority: if any uploaded image is a multi-sheet character bible composite (turnaround grid plus expression grid plus wardrobe breakdown) AND another upload is a storyboard composite, route to Character Bible Pipeline. If the user explicitly names the workflow, route to Character Bible Pipeline regardless of upload count.

If the user uploads 3+ images without specifying a model or intent, ask: "Seedance native multi-reference (each image casts a character or becomes a moment), role-based references (subject + style + environment), or Character Bible Pipeline (character anchor + sheets + storyboard)?"
If the user uploads exactly 2 images without role assignment, ask: "Keyframes (start and end states) or two references with assigned roles?"

## Workflow

### Step 1: Analyze Uploaded Inputs

For each uploaded image (and any described video or audio reference), write an explicit description of what is visible. This description becomes the identity anchor for all prompts.

```
INPUT ANALYSIS:
[Image 1]: [Detailed description. subject, pose, lighting, environment, color, mood, notable details]
[Image 2 if present]: [Same level of detail]
[Video/Audio N if present]: [What it contributes: motion, pacing, voice, music]

Sub-mode detected: [Image-to-Video / Keyframe / Multi-Reference / Role-Based / Extension / Edit / Join / Character Bible Pipeline]
Role assignment: [which input serves which purpose, and what each must NOT contribute]
```

### Step 2: Load References

Load `references/seedance-25-playbook.md` for 2.5 limits, audio syntax, and troubleshooting. Always, unless the target model is not Seedance.
Load `assets/seedance-25-templates.md` for the 2.5 scaffolds (T4 reference binding, T5 edit, T6 extension, T7 ultra-long, T8 join, T9 audio).
Load `references/effects-vocabulary.md` for motion and effects naming.
Load `references/creative-principles.md` for arc structure and principles.
Load `references/ai-video-failure-modes.md` to check for high-risk patterns.
Load `references/style-families.md` when the user's direction is vague or when offering genre variations.
Load `references/consistency-constraints.md` for character, physics, and quality constraint language.
Load `references/character-bible-pipeline.md` when the sub-mode is Character Bible Pipeline. This file owns the full A-B-C-D doctrine, the role-aware `@`-tag pattern, the asset inventory protocol, and the canonical Stage D template.
Load `assets/animate-templates.md` for the prompt template matching the detected sub-mode.

### Step 3: Plan the Motion

Before writing prompts, plan what moves and what stays.

**For Image-to-Video:**
```
MOTION PLAN:
What moves: [hair, fabric, background elements, camera, subject action]
What stays fixed: [identity, pose foundation, lighting direction, key compositional elements]
Camera behavior: [push-in, orbit, static with subject motion, etc.]
Duration: [target, default 8-10 seconds; up to 30s on Seedance 2.5 if the brief warrants]
Energy arc: [how motion builds and resolves]
Effects palette: [which effects from vocabulary apply]
Signature moment: [the most visually striking motion beat]
```

**For Keyframe / First & Last Frame:**
```
INTERPOLATION PLAN:
Start state: [description from Image 1]
End state: [description from Image 2]
What transforms: [specific elements that change between states]
What persists: [what stays constant across both frames]
Transformation style: [smooth morph, dramatic cut, gradual shift, physics-based]
Duration: [target, default 8 seconds]
Midpoint: [what the halfway state should look like]
Energy arc: [how the transformation paces itself]
```

**For Multi-Reference Shot Prompt (Seedance native):**
```
SEQUENCE PLAN:
References: [N images / N videos / N audio. Confirm inside sweet spots: 1-8 image subjects, 1-5 video/audio]
Target duration: [default 30 seconds on Seedance 2.5]
Stage count: [typically 4 stages for 30s: 0-6 setup, 6-14 build, 14-24 turn, 24-30 resolution]
Reference-to-role mapping: [which @Image N binds to which character/prop/scene/style, plus exclusion lines]
Style / context / character: [the preamble. global style, setting, main cast]
Stage beats: [one line per stage: primary change, end state, which references appear]
Audio: [native syntax plan: (music), <sfx>, {dialogue}, or the [SOUND] foley-only directive]
Narrative arc: [how the sequence reads start to finish]
```

**For Role-Based Multi-Reference (model-agnostic):**
```
COMPOSITION PLAN:
Subject source: [Image N. what is borrowed]
Style source: [Image N. what aesthetic qualities apply]
Environment source: [Image N. what spatial/environmental elements apply]
Structural guide: [Image N. panel-by-panel sequence to follow. Mark explicitly as DO NOT RENDER.]
[Additional roles if present]
Integration logic: [how the references merge. subject IN environment WITH style]
Conflicts: [where references contradict and how to resolve]
Duration: [target, default 8 seconds]
Energy arc: [how the composed scene moves]
```

Omit any row whose role is not present. The Structural guide row only appears when a storyboard / production board has been assigned that role.

**For Video Extension / Continuation:**
```
EXTENSION PLAN:
Base clip: [what exists, duration, its final frame state]
Extension length: [4-30s per pass; running total must stay at 30s or less to keep stacking; 60s final ceiling]
New segment only: [what happens in the extension. Nothing about the base is re-prompted]
Workflow: [controlled reveal / action relay / plain continuation]
Continuity boilerplate: "Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air."
```

**For Edit (Smart Edit):**
```
EDIT PLAN:
Source: [the video, its duration (under 20s edits are most stable)]
Target: [the element to change, region reference if the user drew one]
Change: [replace / recolor / remove / add]
Timing: [seconds X-Y, or whole clip]
Protected: [everything that stays: identity, motion, camera, audio layers]
```

**For Join:**
```
JOIN PLAN:
Clip 1: [content, final-frame state]
Clip 2: [content, opening-frame state]
Bridge: [match cut / object at lens / foreground wipe / other described transition]
```

**For Character Bible Pipeline (Seedance native multi-sheet):**

Run the asset inventory first. Determine which stages the user has completed and which need to be produced.

```
ASSET INVENTORY:
Stage A character hero shot: [present as @Image 1 / needs to be generated / user has but did not upload]
Stage B character bible: [present (composite) / present (separate sheets) / partial / needs to be generated / not needed for this project]
Stage C storyboard composite: [present / needs to be generated]
Current state: [0. brief only / 1. character only / 2. character + partial bible / 3. full bible no storyboard / 4. everything ready]
```

When the state is unclear, ask the user which state matches, offering the five states as options.

Once inventory is set, build the pipeline plan:

```
PIPELINE PLAN:
@-tag mapping:
  @Image 1 = [character hero shot, role: persistent identity anchor, RENDERS as subject]
  @Image 2 = [character sheet / turnaround, role: consistency reference, DOES NOT RENDER]
  @Image 3 = [wardrobe sheet, role: consistency reference, DOES NOT RENDER]
  @Image 4 = [emotion sheet, role: consistency reference, DOES NOT RENDER]
  @Image 5 = [storyboard composite, role: structural guide, DOES NOT RENDER]
  [Adjust tag numbers to actual upload order. Drop any tag whose asset is not in play.]

Stages to ship in this turn:
  [List the stages the user still needs prompts for. Always Stage D. Optionally Stages A, B, or C if the user has not done them.]

Cross-skill handoffs noted:
  Stage A: [nano-banana-unified / gpt-image-2-unified CREATE / image-prompt-architect]
  Stage B: [gpt-image-2-unified MULTI-OUTPUT or EDITORIAL or SERIES]
  Stage C: [previs-to-sequence STORYBOARD-FROM-TEXT or STORYBOARD-FROM-IMAGE / gpt-image-2-unified NARRATIVE]
  Stage D: this skill, this sub-mode

Target video duration: [seconds, up to 30 in one pass on 2.5]
Shot count: [matches storyboard panel count or documented compression]
Style declaration: [the cinematic style of the FINAL VIDEO, separate from any reference image's drawing style]
Environment: [setting summary]
Energy arc: [how the sequence builds]
```

Show the plan to the user before generating prompts.

### Step 4: Write Shot Prompts

Generate the prompt(s) following the template from `assets/animate-templates.md` or `assets/seedance-25-templates.md` for the detected sub-mode.

**Critical rules for Image-to-Video, Keyframe, and Role-Based Multi-Reference:**

1. All shot prompts go in a single triple-backtick code block. Shots separated by `---` dividers inside that block. This is the prompt the user pastes into Seedance and other generators. Only split into individual code blocks if the user explicitly requests it.
2. Every prompt MUST start with: "Using the uploaded [explicit description of the image]..."
3. Every prompt MUST end with: "Do not change aspect ratio."
4. Never use generic references: "the image," "this photo," "Image 1." Always use the explicit description.
5. Describe MOTION, not appearance. The image already shows what things look like. Prompts describe what changes, what moves, where the camera goes.
6. Repeat key identity anchors in every shot for character consistency.
7. For Keyframe mode: reference both images explicitly. "Starting from the uploaded [description of start frame], transition toward the state shown in the uploaded [description of end frame]..."
8. For Role-Based Multi-Reference mode: reference each image by its role. "Using the subject from the uploaded [description], placed in the environment from the uploaded [description], rendered in the visual style of the uploaded [description]..."
9. If a structural-guide reference is in play, the prompt must declare its role explicitly and include the do-not-render directive. Canonical wording: "Do not render the storyboard image in the final video. Use the storyboard only as a panel-by-panel structural guide. The final video does not show panel borders, panel numbers, timing brackets, annotation arrows, or grid layout."

**Critical rules for Multi-Reference Shot Prompt (Seedance native):**

This mode uses a DIFFERENT structural pattern. The generic rules above do NOT apply. Instead:

1. Output ONE prompt in ONE code block. Not N prompts. The whole sequence is a single prompt because Seedance reads the full staged script natively.
2. Structure: reference-binding block (T4: every tag gets a role line AND an exclusion line) → style/context preamble → staged beats with timestamps and end states (T3) → constraints and forbidden list → audio (T9).
3. Reference inputs using `@Image 1`, `@Video 1`, `@Audio 1` tags. Numbering follows upload order. Seedance 2.0's lowercase style still parses; stay consistent within one prompt.
4. Each stage can reference one or more inputs and states one primary change with an explicit end state.
5. The explicit input description still appears ONCE in the analysis block at the top of the response, so the user knows which upload is which tag. The prompt itself uses the tags for compactness.
6. Do NOT prefix stages with "Using the uploaded..." That rule is for other modes. Seedance native syntax is purpose-built and breaks this convention.
7. Include "Do not change aspect ratio." at the end of the prompt.
8. Close with the consistency clause and forbidden list ("No subtitles, no background music" or the [SOUND] directive when clean audio matters).

**Critical rules for Extension, Edit, and Join:**

1. One prompt, one code block, per pass.
2. Extension prompts describe ONLY the new segment and always include: "Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air."
3. Edit prompts follow target + change + timing + protected list. Never ask to change aspect ratio or duration; Smart Edit preserves both.
4. Join prompts name both clips, forbid modification of either, and describe the bridge.

**Critical rules for Character Bible Pipeline (Seedance native multi-sheet):**

This sub-mode uses Seedance native `@`-tag syntax but with ROLE-AWARE assignment. Each tag has a declared role and a declared render-or-not behavior. Use these rules:

1. Output ONE Stage D prompt in ONE code block. The whole multi-shot sequence is a single Seedance prompt.
2. The prompt MUST open with three explicit blocks: `SUBJECTS:` (declares `@Image 1` as the persistent anchor with character description), `REFERENCES:` (declares every consistency tag with explicit do-not-render directives naming the visual artifact to suppress), and `STRUCTURAL GUIDE:` (declares the storyboard tag with the panel-by-panel do-not-render directive).
3. `@Image 1` is the persistent identity anchor referenced across every shot. The character must appear in every rendered frame, exactly as `@Image 1` shows them.
4. Every non-anchor tag MUST have a do-not-render directive that names the specific visual artifact to suppress. Examples: "Do not show multi-view turnaround layouts, character sheet boxes, view labels, or any sheet-style framing" for a character sheet. "Do not show wardrobe breakdowns, garment labels, fabric swatches, or any catalog-style layout" for a wardrobe sheet. "Do not show expression grids, emotion labels, or any expression-sheet framing" for an emotion sheet. "Do not show panel borders, panel numbers, timing brackets, annotation arrows, grid layout, or any storyboard-style framing" for the storyboard.
5. Shot count matches storyboard panel count by default. Compress only if the duration cannot carry the panel count, and document the merge.
6. Each shot beat declares action, camera grammar, an end state, and SFX. The character (@Image 1) is referenced explicitly inside each shot beat. Storyboard panel mapping is implicit (Shot 1 mirrors panel 1, Shot 2 mirrors panel 2, etc) unless documented otherwise.
7. STYLE block is mandatory and declares the cinematic style of the FINAL VIDEO. Storyboards are sketchy or simplified. The final video should NOT inherit the storyboard's drawing style. State this explicitly.
8. GLOBAL CONSTRAINTS block at the end declares: identity anchor across all shots, the anti-drift boilerplate ("same face, same hairstyle, same outfit, same body type for the entire video"), consistency cross-checks against each sheet, exact panel order from storyboard, no-bleed clause covering all reference artifacts, no panel borders, no annotations, no on-screen text bleed.
9. Close with "Do not change aspect ratio."
10. The IMAGE MAPPING block (which tag corresponds to which uploaded asset) appears ABOVE the prompt code block in the response, NOT inside the prompt. This is for the user's reference, not for Seedance.
11. If the user has not completed Stages A, B, or C yet, generate the missing-stage prompts as ADDITIONAL outputs (each in its own code block, labeled with the stage and target model). Each is a creative brief the user pastes into the relevant image model. Stage D is always the final deliverable.
12. Cross-skill handoffs are mentioned in the delivery preamble. If the user wants premium quality on Stages A, B, or C, the relevant skill is named (`gpt-image-2-unified`, `nano-banana-unified`, `previs-to-sequence`). Default is to write the prompts inline so the user does not have to skill-hop.

See `references/character-bible-pipeline.md` for the full doctrine, examples, and failure modes specific to multi-sheet pipelines.

### Step 5: Determine Shot Count and Structure

**Image-to-Video:**
- Default 4-8 shots for an 8-second video
- Can be a single continuous shot prompt OR broken into beats
- If the user wants a longer sequence (15-30s), structure as a staged script with end states (T3) for Seedance, or a full multi-shot breakdown for other models
- For short clips (3-8s), output 3-5 prompt variations exploring different motion approaches inside one code block, separated by `---`

**Keyframe / First & Last Frame:**
- Default 3-6 shots mapping the transformation arc
- Shot 1 anchors the start state, final shot anchors the end state, middle shots describe the interpolation
- For simple transformations, output 3-5 prompt variations exploring different interpolation styles

**Multi-Reference Shot Prompt (Seedance native):**
- ONE prompt, ONE code block. The whole sequence fits inside.
- Default 30 seconds on 2.5, staged in 4 beats (0-6, 6-14, 14-24, 24-30) unless the story dictates otherwise.
- One primary change per stage, an explicit end state per stage.
- Reference-to-role mapping is deliberate: every uploaded input is bound or explicitly dropped.
- Optional: offer 2-3 prompt variations exploring different narrative arcs. Each variation is a complete Seedance prompt in its own code block.

**Role-Based Multi-Reference (model-agnostic):**
- Structure follows BUILD (full shot-by-shot breakdown) since composed scenes typically need more direction
- Default 6-10 shots for a 10-15 second video

**Extension / Edit / Join:**
- One tight prompt per pass. Extension passes chain: plan the pass sequence up front when the user wants a 60s final.

**Character Bible Pipeline (Seedance native multi-sheet):**
- ONE Stage D prompt, ONE code block. Multi-shot sequence inside.
- Shot count defaults to storyboard panel count. 8-12 panels is typical.
- Target duration defaults to the storyboard's total time, up to 30 seconds in one pass. If storyboard has timing brackets, sum them. If not, distribute across the beat map. Past 30s, plan extension passes per act or use Ultra-Long (T7).
- Additional output blocks (one each, in their own code blocks, labeled with Stage and target model): Stage A prompt if no character, Stage B prompt if no bible, Stage C prompt if no storyboard. These are ADDITIONAL to Stage D, not replacements.

### Step 6: Supporting Sections

For sequences of 4+ shots, include the standard supporting sections after the shot prompts:
1. Master effects inventory
2. Effects density map
3. Energy arc

For short clips (1-3 shots or variation sets) and single-pass extension/edit/join prompts, skip the supporting sections. The prompts speak for themselves.

### Step 7: Self-Validation

**For all sub-modes:**
- [ ] Input analysis block present with explicit descriptions
- [ ] Sub-mode correctly detected
- [ ] Motion/interpolation/composition/sequence plan shown
- [ ] Every prompt ends with "Do not change aspect ratio." (except Edit prompts, where aspect ratio is preserved automatically)
- [ ] Prompts describe motion/change, not static appearance
- [ ] Effects named precisely
- [ ] No high-risk AI patterns unaddressed
- [ ] Seedance prompts pass the 2.5 pre-flight checklist in `references/seedance-25-playbook.md`

**For Image-to-Video, Keyframe, and Role-Based Multi-Reference:**
- [ ] All shot prompts in ONE single code block, separated by --- dividers (unless user requested otherwise)
- [ ] Every prompt starts with "Using the uploaded [explicit description]..."
- [ ] No generic image references ("the image," "this photo")
- [ ] Identity anchors repeated across shots
- [ ] For Keyframe: both start and end states referenced
- [ ] For Role-Based Multi-Reference: all reference roles explicitly assigned
- [ ] If a structural-guide reference is assigned, the do-not-render directive is present in the prompt
- [ ] The do-not-render directive references the specific image by its description (not by tag, since Role-Based does not use tags)

**For Multi-Reference Shot Prompt (Seedance native):**
- [ ] Output is ONE prompt in ONE code block (not N separate prompts)
- [ ] Reference-binding block present: every tag has a role line AND an exclusion line
- [ ] Reference counts inside sweet spots (1-8 image subjects, 1-5 video/audio), or the overage is flagged to the user
- [ ] Staged beats with timestamps and end states, one primary change per stage
- [ ] Tag numbering matches upload order; analysis block shows which tag corresponds to which upload
- [ ] Consistency clause and forbidden list present
- [ ] Stages do NOT use "Using the uploaded..." opener (that rule is for other sub-modes)

**For Extension / Edit / Join:**
- [ ] Extension prompt covers only the new segment and includes the continuity boilerplate
- [ ] Extension math checked: base 30s or less, pass adds 4-30s, final 60s or less
- [ ] Edit prompt has target + change + timing + protected list, and does not request aspect-ratio or duration changes
- [ ] Join prompt forbids modifying either clip and describes the bridge

**For Character Bible Pipeline (Seedance native multi-sheet):**
- [ ] Asset inventory was run and the current state was identified
- [ ] Stage D prompt opens with three explicit blocks: SUBJECTS, REFERENCES, STRUCTURAL GUIDE
- [ ] @Image 1 is declared as the persistent character anchor with identity description
- [ ] Every non-anchor tag has a do-not-render directive that names the specific visual artifact to suppress
- [ ] Storyboard tag has the panel-by-panel do-not-render directive (no panel borders, no panel numbers, no timing brackets, no annotation arrows, no grid layout)
- [ ] STYLE block is present and declares the cinematic style of the FINAL video, separate from the storyboard's drawing style
- [ ] Shot count matches storyboard panel count (or compression is documented)
- [ ] Each shot beat declares action, camera grammar, an end state, and SFX
- [ ] The character (@Image 1) is referenced inside each shot beat for identity persistence
- [ ] GLOBAL CONSTRAINTS block contains the anti-drift boilerplate and the no-bleed clause for all reference images
- [ ] IMAGE MAPPING block (which tag = which asset) appears ABOVE the prompt code block, not inside it
- [ ] If Stages A, B, or C were missing, missing-stage prompts were shipped as additional code blocks
- [ ] Cross-skill handoffs (gpt-image-2-unified, nano-banana-unified, previs-to-sequence) are named in the preamble for users who want premium per-stage quality
- [ ] Prompt closes with "Do not change aspect ratio."

## Outputs

**For short clips / variations (Image-to-Video, Keyframe):**
1. Input analysis
2. Motion/interpolation plan
3. Prompt variations (one code block, `---` separated)

**For full sequences (Image-to-Video long, Role-Based Multi-Reference):**
1. Input analysis
2. Motion/composition plan
3. Shot prompts (one code block)
4. Master effects inventory
5. Effects density map
6. Energy arc

**For Multi-Reference Shot Prompt (Seedance native):**
1. Input analysis block with tag mapping table (which tag = which upload, role, exclusion)
2. Sequence plan
3. THE prompt (one code block, full staged script inside)
4. Optional: 1-2 variation prompts (each in its own code block) exploring different narrative orderings
5. Brief notes on which references appear in which stage, for the user's reference

**For Extension / Edit / Join:**
1. Plan block (extension/edit/join plan)
2. THE prompt (one code block)
3. For multi-pass extensions: the pass sequence with each pass's prompt in its own code block, labeled Pass 1, Pass 2...

**For Character Bible Pipeline (Seedance native multi-sheet):**
1. Brief preamble naming the pipeline state (0 through 4), the stages being shipped this turn, and any cross-skill handoffs the user can use for premium per-stage quality
2. Input analysis block with role-aware tag mapping table (which tag = which asset, plus role and render-or-not behavior)
3. Asset inventory and pipeline plan (compact, the user has already seen it during Step 3)
4. Stage A prompt (only if user does not have a character image yet). One code block, labeled "Stage A: Character hero shot prompt (target model: [Nano Banana / GPT Image 2 / Midjourney])"
5. Stage B prompt (only if user does not have a character bible yet). One code block, labeled "Stage B: Character bible composite prompt (target model: GPT Image 2)"
6. Stage C prompt (only if user does not have a storyboard yet). One code block, labeled "Stage C: Storyboard composite prompt (target model: GPT Image 2)"
7. Stage D prompt (always). One code block, labeled "Stage D: Seedance 2.5 video prompt (multi-sheet, role-aware @-tags)". The prompt itself opens with SUBJECTS / REFERENCES / STRUCTURAL GUIDE blocks and contains the full multi-shot sequence with no-bleed constraints.
8. Brief panel-to-shot mapping note (which storyboard panel maps to which shot beat)
9. Upload guidance: which assets to upload in which order so the tag numbering matches what the prompt expects

## Error Recovery

**User uploads image but wants text-to-video**: Route to BUILD. The image may be mood reference only, not a generation input.
**Image quality too low for reference**: Note this. Suggest the user provide a higher-resolution reference or switch to BUILD with a text description.
**Keyframe images too similar**: The transformation will be subtle. Note this and suggest either pushing the end state further or using Image-to-Video mode with a single reference.
**Role-based multi-reference conflicts**: When references contradict (warm lighting in subject ref, cold lighting in environment ref), state the conflict and resolve by defaulting to the environment's lighting. Explain the decision.
**Seedance native: too many references**: The ceilings are 30 images / 10 videos / 10 audio, but quality holds at 1-8 image subjects and 1-5 video/audio subjects. Past the sweet spots, warn the user, prioritize (characters, then props, then scene, then style), and consolidate or drop the rest.
**Seedance native: ambiguous reference mapping**: If it is unclear which input belongs to which role or beat, propose a mapping and ask the user to confirm before generating the prompt.
**Collage uploaded for one character's angles**: Ask for separate images per angle. Collages degrade identity binding on 2.5.
**Extension request past limits**: Base over 30s cannot stack further; 60s is the final ceiling. Offer Ultra-Long mode (30-180s single shot, T7) or a join of two finished clips (T8) instead.
**Edit source too long**: Edits are most stable on sources under 20 seconds. Suggest trimming or splitting the edit into two passes.
**User expects AI to "see" a video**: Clarify that this skill works with still images and text descriptions as references. For video-based workflows, suggest DECONSTRUCT with a text description of the video.
**Character Bible Pipeline: user has only a concept**: All four stages need prompts. Ship all four in separate code blocks. Make clear that Stages A through C produce assets the user generates outside this skill, and Stage D consumes those assets as Seedance uploads.
**Character Bible Pipeline: user uploads only a storyboard, no character**: Either route to previs-to-sequence VIDEO-FROM-STORYBOARD (cleaner for storyboard-only) or generate Stage A (character) prompt as a missing-stage output and ship Stage D with `@Image 1` marked as a placeholder pending character generation.
**Character Bible Pipeline: storyboard style is bleeding into the video**: This is the most common Stage D failure. Strengthen the STYLE block. Add explicit instruction that the storyboard reference is for sequence structure only, not for visual style. Cross-check against `references/character-bible-pipeline.md` failure modes section.
