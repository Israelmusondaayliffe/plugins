# Character Bible Pipeline: Stages A-B-C-D

End-to-end workflow for AI filmmaking with persistent character identity and storyboard-driven sequence. The pipeline produces a Seedance video that maintains a character across every shot, follows a panel-by-panel storyboard, and consumes multi-sheet character bible references (turnaround, wardrobe, expressions) as consistency anchors that never render. The pattern originated on Seedance 2.0; Seedance 2.5 is now the default Stage D target, with larger reference budgets and 30-second sequences.

Documented examples in the wild: Donotopia / Bobo Gigglesworth (Shailesh Shakya), Lighthouse AI Academy Viral Prompt Pack 09 (filmmaking special, pages 2-14), Olivio Sarikas "Director's Blueprint" pattern, 0kncn celestial voyager.

## The four stages

### Stage A. Character hero shot

One image. The protagonist in their canonical pose, wardrobe, and lighting. This becomes `@Image 1` in Stage D and the identity anchor across every shot.

**Tooling**: any premium character generator (Nano Banana / Gemini 3 Pro Image, GPT Image 2, Midjourney v7/v8, Flux).

**Format**: single image, typically 3:4 or 16:9 portrait depending on the project.

**Output**: one .jpg or .png the user uploads to Seedance in Stage D.

**Cross-skill handoff**: route the prompt construction to `nano-banana-unified` (Nano Banana / Gemini), `gpt-image-2-unified` CREATE mode (GPT Image 2), or `image-prompt-architect` (model-agnostic). This skill can also write the prompt inline if the user wants to stay in one chat.

### Stage B. Character bible composite

One composite image containing all consistency references. Bobo Gigglesworth pattern: turnaround (front, 3/4, side, back, 3/4 back) plus head study (6-8 expressions) plus wardrobe breakdown plus cinematic portrait, all in one designed sheet.

Alternative pattern: four separate sheets (turnaround, wardrobe, expressions, cinematic portrait), each as its own image. This produces more `@`-tags in Stage D but keeps each sheet readable. On 2.5, separate sheets are preferred when quality matters: the model reads separate angles better than collages.

**Tooling**: GPT Image 2 is the dominant choice. The reasoning capability holds character identity across the multi-region layout. Gemini 3 Pro also works.

**Cross-skill handoff**: `gpt-image-2-unified` MULTI-OUTPUT mode (multi-sheet bible, batch up to 8 outputs sharing one visual DNA), EDITORIAL mode (Bobo-style single-composite character board), or SERIES mode (separate sheets for turnaround, wardrobe, emotion). All three are valid. Choose by output structure preference.

**Output**: one composite image OR three to four separate sheets.

**Freeze rule**: once a bible sheet is locked, never regenerate it. If the motion looks wrong in Stage D, fix the motion prompt. A new image undoes all the consistency work.

### Stage C. Storyboard composite

One image with an 8-12 panel grid (Seedance 2.5 reads up to 15 clean panels). Each panel encodes minimal choreography (stick figures or simplified renders), camera grammar tokens, timing brackets, SFX cues, and sequence labels. Clean lines matter more than rendering quality.

**Tooling**: GPT Image 2 dominant. Midjourney also strong. The previs-to-sequence skill is the canonical owner of Stage 1 storyboard generation.

**Cross-skill handoff**: `previs-to-sequence` STORYBOARD-FROM-TEXT (brief to storyboard) or STORYBOARD-FROM-IMAGE (reference image to storyboard). Also `gpt-image-2-unified` NARRATIVE mode. previs-to-sequence is the deeper authority for this stage.

**Output**: one composite storyboard image.

### Stage D. Seedance 2.5 with multi-sheet role-aware references

This is the deliverable this skill owns. All assets from Stages A-C feed into one Seedance prompt that produces the final video.

**Upload mapping**:

| Tag | Asset | Role | Renders? |
|---|---|---|---|
| `@Image 1` | Character hero shot | Persistent identity anchor | YES (subject across every shot) |
| `@Image 2` | Character sheet / turnaround | Consistency reference (face, body, proportions) | NO |
| `@Image 3` | Wardrobe sheet | Consistency reference (clothing detail, materials) | NO |
| `@Image 4` | Emotion sheet | Consistency reference (expressions, micro-expressions) | NO |
| `@Image 5` | Storyboard composite | Structural guide (panel-by-panel sequence) | NO |

The exact tag numbers shift based on upload order and asset count. The roles are stable: one anchor, N consistency refs, one structural guide. Minimum viable pipeline: `@Image 1` (character) plus `@Image 2` (storyboard), with no additional sheets. Full pipeline: 5 tags as above. Seedance 2.5's ceiling is 30 images, but the sweet spot is 1-8 distinct subjects; deeper bibles (environment sheets, secondary characters, key props) fit comfortably, and a second character adds its own hero shot plus sheets. Seedance 2.0's cap was 9 tags with lowercase `@image1` style; that style still parses on 2.5.

## Role-aware `@`-tag pattern (the core technique)

Seedance reads `@Image N` tags as references the model has direct visual access to. The model does not know what role each tag plays unless the prompt declares it. This is the failure mode behind every botched multi-sheet attempt: the model treats every uploaded image as a shot to render literally, so the wardrobe sheet appears as a wardrobe sheet inside the final video instead of as clothing on the character.

The fix is a declarative role block at the top of the prompt that assigns each tag its role explicitly, plus a do-not-render directive for every tag that is reference-only. This is the same role-plus-exclusion binding rule that governs all 2.5 references (see `references/seedance-25-playbook.md`).

### Canonical Stage D prompt structure

```
SUBJECTS:
@Image 1 is the main character. [Compact description of the character: who they are, their canonical look, any unmissable identity markers from the hero shot.] Use @Image 1 as the persistent visual anchor across every shot. Every shot must show this exact character with this exact face, build, and signature look.

REFERENCES (consistency only, never rendered as standalone images):
@Image 2 is the character turnaround sheet. Use it to keep face, head shape, body proportions, and hair consistent across angles. Do not render @Image 2 in the video. Do not show multi-view turnaround layouts, character sheet boxes, view labels, or any sheet-style framing.
@Image 3 is the wardrobe sheet. Use it to keep the character's clothing, materials, colors, and accessories consistent. Do not render @Image 3 in the video. Do not show wardrobe breakdowns, garment labels, fabric swatches, or any catalog-style layout.
@Image 4 is the emotion sheet. Use it to keep facial expressions consistent with the character's emotional range. Do not render @Image 4 in the video. Do not show expression grids, emotion labels, or any expression-sheet framing.

STRUCTURAL GUIDE (do not render, sequence reference only):
@Image 5 is the storyboard composite. Follow the panel-by-panel sequence shown in @Image 5 exactly. Each panel is one full shot in the video timeline. Do not render @Image 5 in the video. The final video does not show panel borders, panel numbers, timing brackets, annotation arrows, grid layout, or any storyboard-style framing.

ENVIRONMENT:
[Setting description: where the action happens, lighting register, atmosphere.]

STYLE:
[Visual style declaration: this is the LOOK of the final video, separate from the storyboard's drawing style. Storyboards are often sketchy or simplified. The final video should be the finished cinematic style, not the storyboard style.]

[Shot 1] [0-Xs] [Action mirroring panel 1 of @Image 5]. Camera: [grammar from panel 1]. The character (@Image 1) [specific action]. End state: [where things are when the shot closes]. SFX: <[from panel 1]>.
[Shot 2] [Xs-Ys] [Action mirroring panel 2 of @Image 5]. Camera: [grammar from panel 2]. End state: [...]. SFX: <[from panel 2]>.
[Shot 3] ...
...
[Shot N] [(N-1)t-Nt] [Action mirroring panel N of @Image 5]. Camera: [grammar from panel N]. End state: [...]. SFX: <[from panel N]>.

GLOBAL CONSTRAINTS:
Maintain the exact character from @Image 1 across every shot. Same face, same hairstyle, same outfit, same body type for the entire video. Cross-check face, body, and hair against @Image 2. Cross-check wardrobe against @Image 3. Cross-check expression range against @Image 4. Follow exact panel order from @Image 5.
No panel borders, no annotations, no timing brackets, no panel numbers, no grid layout, no on-screen text bleed from any reference image. The final video shows only the cinematic scene.
Consistent lighting, environment, and character identity across all shots. No deformation. Stable proportions. Natural motion physics. No subtitles, no background music unless directed below.

AUDIO:
[Native audio syntax: (music), <sound effects>, {dialogue}. Or the ambient-only line. See seedance-25-playbook.md.]

Do not change aspect ratio.
```

This is the deliverable. One prompt, one code block, the user pastes it into Seedance along with the five (or however many) uploads. Default duration on 2.5: up to 30 seconds in one pass. Longer sequences use Video Extension per storyboard act, or Ultra-Long mode with the anti-drift scaffolding from `assets/seedance-25-templates.md` T7.

## Asset inventory protocol

Before generating Stage D, determine which stages are already complete. Four states:

| State | What the user has | What this skill ships |
|---|---|---|
| 0. Brief only | A concept, no images | Stage A prompt, Stage B prompt, Stage C prompt, Stage D prompt (with placeholder tags marked TBD) |
| 1. Character only | Stage A done | Stage B prompt, Stage C prompt, Stage D prompt |
| 2. Character + partial bible | Stage A done, some Stage B sheets | Remaining Stage B prompts, Stage C prompt, Stage D prompt |
| 3. Full bible no storyboard | Stages A and B done | Stage C prompt, Stage D prompt |
| 4. Everything ready | Stages A, B, C done | Stage D prompt only |

When the user's status is unclear, ask which state they are in, offering these states as the options. Otherwise infer from what they upload and what they describe.

## Cross-skill routing recommendations

This skill writes all Stage A/B/C/D prompts inline by default so the user does not have to skill-hop. When premium quality is needed for a specific stage, cross-reference:

- Stage A (character): `nano-banana-unified` (Nano Banana / Gemini 3 Pro Image), `gpt-image-2-unified` CREATE, `image-prompt-architect`.
- Stage B (character bible): `gpt-image-2-unified` MULTI-OUTPUT (multi-sheet bible), EDITORIAL (Bobo-style single composite), or SERIES (separate single-axis sheets).
- Stage C (storyboard): `previs-to-sequence` STORYBOARD-FROM-TEXT or STORYBOARD-FROM-IMAGE. Also `gpt-image-2-unified` NARRATIVE.
- Stage D (Seedance video): this skill, this sub-mode.

Cross-references are mentioned in the delivery preamble. The user picks whether to switch skills or stay inline.

## Validation checklist for Stage D

Before shipping the Stage D prompt, verify:

- `@Image 1` is declared as the persistent anchor with explicit identity description.
- Every consistency-reference tag has an explicit "do not render" directive that names the visible artifact to suppress (turnaround grid, wardrobe breakdown, expression grid, panel borders, etc.).
- The structural-guide tag has the storyboard do-not-render directive (no panel borders, no panel numbers, no timing brackets, no annotation arrows, no grid layout).
- Shot count matches storyboard panel count, or compression is documented if panels exceed what the duration can carry.
- Each shot describes action, camera grammar, an end state, and SFX. Each shot references the character (@Image 1) by description or implicitly through the SUBJECTS block.
- Style declaration is separate from storyboard reference (the video looks like the final cinematic style, not the storyboard's sketch style).
- Global constraints block contains the no-bleed clause for all reference images and the anti-drift boilerplate for sequences over 15s.
- Prompt closes with "Do not change aspect ratio."

## Failure modes specific to multi-sheet pipelines

**Sheet bleeds into render**: any of the reference sheets (turnaround, wardrobe, emotion) shows up literally inside the video. Cause: missing or weak do-not-render directive. Fix: name the specific visual artifact to suppress in the directive ("Do not show wardrobe breakdowns, garment labels, fabric swatches, or any catalog-style layout").

**Storyboard style overrides cinematic style**: final video looks like the storyboard (sketchy, monochrome, simplified) instead of the intended cinematic style. Cause: style declaration missing or weak, or the storyboard reference dominates. Fix: declare the cinematic style explicitly in the STYLE block, separate from any reference image. Mention that the storyboard reference is for structure only, not for visual style.

**Character drift across shots**: the character looks different in shot 3 than in shot 1. Cause: anchor declaration is weak, model loses identity over long sequences. Fix: the verbatim 2.5 boilerplate in global constraints ("same face, same hairstyle, same outfit, same body type for the entire video"), plus compact identity restatement inside individual shot beats for high-drift sequences. Cross-check against `@Image 2` (turnaround) explicitly.

**Wardrobe drift**: the clothing changes between shots. Cause: `@Image 3` not anchored strongly. Fix: include "wardrobe matching @Image 3" in shot beats where wardrobe is visible. Add to global constraints.

**Expression mismatch**: the character's emotional range goes outside what the project allows. Cause: `@Image 4` not used as a bound. Fix: state in global constraints that the character's expression range is bounded by what is shown in `@Image 4`, no expressions outside this range.

**Panel-to-beat mismatch**: storyboard has 10 panels but the prompt has 6 beats. Cause: compression undocumented or auto-merged silently. Fix: one beat block per panel by default. If compression is required, document which panels merge and why.

**Reference overload**: quality degrades with many uploads even under the 30-image ceiling. Cause: past the 1-8 subject sweet spot, results get unstable. Fix: consolidate (one composite bible replaces 2-3 sheets), drop redundant refs, prioritize characters then props then scene then style.

## Examples decoded

### Donotopia / Bobo Gigglesworth (Shailesh Shakya)

Character: Bobo Gigglesworth, "The Walking Whoopee Cushion", age 27 (cartoon logic), 4'2", short squishy pear-shaped with tiny limbs and oversized belly, ethnicity stylized / ambiguous.

Stage A: single Bobo hero shot in canonical pose (yellow hoodie, jeans, ketchup stain, glasses).

Stage B: one composite Bobo Gigglesworth character bible. Contains turnaround (front, 3/4, side, back, 3/4 back), head study with 6 expressions (forced smile, awkward grin, cheeks puffed, self-doubt looking down, hopeful excitement looking up, chaotic panic dynamic angle), wardrobe breakdown (soft fleece hoodie with stretched elbows and ketchup stain, twisted wrinkled t-shirt, frayed stretched-neckline shorts), notes for production (clothing always slightly ill-fitting, stains crumbs and small damages essential, hair never perfectly arranged, glasses frequently slip or tilt, energy is bouncy unpredictable). Plus a cinematic portrait at the right (Bobo at refrigerator reaching for donuts).

Stage C: not shown in the post but implied (storyboard would follow standard previs-to-sequence patterns).

Stage D: Seedance prompts with the Bobo hero shot as anchor, the character bible composite as consistency reference, plus the storyboard. Generated multiple action scenes (giant boss fights, destruction sequences, comedy beats) all maintaining Bobo's identity.

### Celestial Voyager (0kncn) - Lighthouse Pack page 4

Stage B character concept sheet (page 3 of pack): 16:9 layout with 4 distinct views (symmetrical full-body front, full-body side profile, full-body back view, hyper-detailed close-up portrait). White-and-gold ritualistic armored design, glowing amber energy lines, halo-like circular structure.

Stage D Seedance video prompt (page 4): uses the storyboard ref as direct sequential visual keyframe reference for the entire video, the character image as same main character throughout all shots. 8 shot beats. Explicit "Do not make it stop motion" directive. Global constraint that exact storyboard continuity is maintained panel to panel.

### Ink-Wash Previs (abxxai) - Lighthouse Pack pages 9-10

Stage B not applicable (no character bible needed, the style is abstract figure work).

Stage C: 8-panel ink-wash storyboard with stick figures, motion choreography, timing brackets, SFX cues.

Stage D: GPT Image 2 plus Seedance prompt. Director-style PREVIS action storyboard interpreted into a timed video. Timeline-bracketed shot list. Each shot has camera grammar plus SFX in parentheses.

### Director's Blueprint (OlivioSarikas) - Lighthouse Pack page 11

Stage B + C combined: single image containing character + styling reference (front, back, side, close-up, relaxed pose), wardrobe / accessories, environment & set design (living room set with top-down movement & camera plan), storyboard (8 shots), lighting / mood / style notes, mood & keywords, ambient sound, lens choices, cinematography notes.

This is a one-image "director's blueprint" rather than separate sheets. The Stage D prompt (pack page 13) reads it directly as one composite: "Follow this story board to create a AD/Film. dynamic camera movement, no camera gear in the shots..." then the 8-shot beat list.
