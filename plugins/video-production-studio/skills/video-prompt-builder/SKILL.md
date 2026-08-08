---
name: video-prompt-builder
description: "Build cinematic, shot-by-shot video prompts with effects breakdowns for Seedance 2.5, Kling 3, Veo 3, and Sora 2. BUILD turns a brief into staged scripts or prompts with effects timelines, density, and energy arcs. ANIMATE handles image-to-video, keyframes, multi-reference roles, character bibles, storyboards, extensions, edits, and clip joins. DECONSTRUCT converts a described video into the effects format. REMIX transfers an effects architecture to a new subject. Use for video prompts, one-takes, shot lists, animation, keyframes, extensions, edits, storyboards, reference pipelines, or full video workflows."
---

# Video Prompt Builder

Build cinematic, shot-by-shot video prompts from creative briefs, uploaded reference images, deconstructed references, or remixed architectures. Every output follows a structured effects breakdown format designed to give AI video generators maximum detail on camera work, effects, transitions, pacing, and energy arc.

**Seedance 2.5 takes precedence.** It is the current best-in-class video model and the default target for every prompt unless the user names another model. Platform facts, limits, and fixes: `references/seedance-25-playbook.md`. Prompt scaffolds: `assets/seedance-25-templates.md`. Also optimized for Kling 3, Veo 3, Sora 2 when the user targets them.

## Output Mandate

**All shot prompts go in a single triple-backtick code block by default.** Shots are separated by `---` dividers inside that block, except Seedance-native staged scripts, which are already one continuous prompt. This is the format accepted directly by Seedance and other generators, so the full sequence must be one pasteable unit.

Only break shots into individual code blocks if the user explicitly asks for it.

Supporting sections (effects inventory, density map, energy arc) are presented as structured text outside the code block. They frame the full picture. The single code-blocked shot sequence is the deliverable.

## Tone

Direct, technical. Director's shot notes, not a marketing brief. No hype language, no "stunning" or "breathtaking." Describe what happens and let the visuals speak.

Replace every em-dash with a period (new sentence) or comma (continue thought).

---

## Router Logic

Assess the user's request and route to the appropriate agent.

### BUILD mode → Load `agents/agent-build.md`

**Triggers**: User provides a creative brief, concept, idea, or description and wants video prompts generated from it. No uploaded images, no existing breakdown to work from. Pure text-to-video.

Examples:
- "Write me a video prompt for a trail running shoe ad"
- "I need a 30-second one-take for a coffee brand"
- "Shot list for a dramatic product reveal"
- "Seedance prompt for a dancer in an empty warehouse"
- "Plan a video sequence for this concept"
- "Three-minute ultra-long video about [concept]"

### ANIMATE mode → Load `agents/agent-animate.md`

**Triggers**: User uploads one or more images alongside a video generation request, or wants to extend, edit, continue, or join existing video generations. Sub-modes detected by the agent based on input type.

**Image-to-Video**: One image uploaded + motion intent.
**Keyframe / First & Last Frame**: Two images uploaded as start and end states. Maps to Seedance 2.5's First & Last Frame mode.
**Multi-Reference Shot Prompt (Seedance native)**: Multiple images uploaded. Each reference is bound to a role with `@Image N` tags (up to 30 images on 2.5; sweet spot 1-8 subjects). One prompt, full sequence up to 30 seconds.
**Role-Based Multi-Reference (model-agnostic)**: 2+ images with assigned roles (subject, style, environment, structural-guide). For Kling, Veo, Sora.
**Video Extension / Continuation**: Extend a prior generation by 4-30s per pass (60s ceiling) or chain with `@Video 1`.
**Edit (Smart Edit)**: User has a video and wants something changed in it: swap a subject, recolor, remove a watermark, replace background, strip BGM.
**Join**: Seamlessly connect two finished clips with a described bridge.
**Character Bible Pipeline (Seedance native multi-sheet)**: End-to-end workflow. Character hero shot, multi-sheet character bible, storyboard composite, and Seedance prompt with role-aware `@`-tags (`@Image 1` as persistent character anchor that renders across every shot, additional tags as consistency references and structural guide that never render). For Donotopia / Bobo / Lighthouse pattern.

Examples:
- "Animate this image" (single upload)
- "Transition from this to this" (two uploads, keyframe)
- "Seedance prompt from these 6 images" (multi-upload, native syntax)
- "Use this as the subject and this as the style reference" (role-based)
- "Extend this video, now the UFO appears" (extension)
- "Remove the background music from this clip" (edit)
- "Connect these two clips seamlessly" (join)
- "Run the character bible pipeline. Here's the character, the turnaround, the wardrobe sheet, the emotion sheet, and the storyboard." (Character Bible Pipeline)
- "Donotopia workflow for this concept" (Character Bible Pipeline, brief only)
- "Stage A through D for [character/concept]" (Character Bible Pipeline)

The agent loads prompt templates from `assets/animate-templates.md` and `assets/seedance-25-templates.md`.

When the user uploads a storyboard composite alongside character or style references, do not treat the storyboard as a shot to render. Assign it the structural-guide role and include the do-not-render directive. See `agents/agent-animate.md` for full detection and routing logic. The canonical Stage-2 storyboard-to-video pipeline lives in `previs-to-sequence`. Cross-reference there when the request goes beyond a single Stage-2 prompt and needs the full Stage-1 plus Stage-2 chain.

For end-to-end pipelines where the user wants character generation, character bible composite, storyboard composite, AND the Seedance video prompt, route to the Character Bible Pipeline sub-mode of ANIMATE. This sub-mode runs an asset inventory, ships prompts for any missing stages (Stage A character, Stage B bible, Stage C storyboard) as separate code blocks targeting GPT Image 2 / Nano Banana / etc, and ships the Stage D Seedance prompt with role-aware `@`-tags. The full doctrine lives in `references/character-bible-pipeline.md`.

### DECONSTRUCT mode → Load `agents/agent-deconstruct.md`

**Triggers**: User wants to analyze, reverse-engineer, or break down an existing video into the effects breakdown format. The input is a description of something that already exists, not a brief for something new.

Examples:
- "Deconstruct the Apple Watch ad"
- "Break down this video into shots and effects"
- "Analyze the effects in this Nike commercial"
- "What's the shot structure of this reference?"
- "Reverse-engineer this video's editing style"

### REMIX mode → Load `agents/agent-remix.md`

**Triggers**: User has (or wants to use) an existing effects breakdown and wants to apply that structure to a new subject, brand, or concept. Requires both a source structure and a new context.

Examples:
- "Take the Hoka breakdown and apply it to a skateboarding brand"
- "Use that effects structure but for a perfume ad"
- "Remix the deconstruction we just did for a tech product"
- "Same energy arc but for a completely different subject"

### Ambiguous Requests

If the request could fit multiple modes, use this priority:
1. If user uploads image(s) with video intent, or wants to extend/edit/join existing generations → ANIMATE
2. If user references an existing video to analyze → DECONSTRUCT
3. If user has an existing breakdown AND a new context → REMIX
4. If user provides a concept, brief, or idea with no images → BUILD
5. If unclear, ask: "Are you building from a concept, animating or extending reference material, deconstructing a reference, or remixing an existing structure?"

---

## Shared Resources

All agents reference:
- `references/seedance-25-playbook.md`. Seedance 2.5 platform facts: capabilities, modes, reference budgets and sweet spots, audio syntax, languages, extension and edit workflows, pro tools, reference bible workflow, troubleshooting, pre-flight checklist.
- `references/seedance-patterns.md`. Seedance technical patterns: timeline brackets, reference tags with role binding, constraint clauses, audio cues, lens specs, clause order, word counts.
- `references/effects-breakdown-reference.md`. The Hoka athletic brand film example. Gold standard for detail level and structure.
- `references/effects-vocabulary.md`. Named effects catalog with precise descriptions.
- `references/creative-principles.md`. Five creative principles, duration calibration, anti-patterns.
- `references/ai-video-failure-modes.md`. What AI video generators struggle with and how to write around it, including what Seedance 2.5 changed.
- `references/style-families.md`. Six style families (cinematic narrative, action/VFX, product/commercial, character portrait, environment/landscape, UGC/meme) with signature language patterns.
- `references/consistency-constraints.md`. Character, physics, anatomy, and quality constraint language for reliable output.

BUILD agent also references:
- `assets/seedance-25-templates.md`. Nine Seedance 2.5 templates (one-take, timed beats, staged script, reference binding, edit, extension, ultra-long, join, audio direction) plus five format recipes (KPOP MV, vlog, product 3D, realistic lighting, animation).
- `assets/build-templates.md`. Five text-to-video template scaffolds (T1 Cinematic Narrative, T2 Product, T3 Portrait, T4 Landscape, T5 Action/VFX).

ANIMATE agent also references:
- `assets/seedance-25-templates.md`. As above; T4-T8 (reference binding, edit, extension, ultra-long, join) are ANIMATE's core scaffolds.
- `assets/animate-templates.md`. Image-to-video, keyframe, Seedance native multi-reference, video continuation, JSON variant, role-based multi-reference templates, and Character Bible Pipeline Template (Stage D plus Stage A/B/C handoff prompts).
- `references/character-bible-pipeline.md`. Full A-B-C-D doctrine for the Character Bible Pipeline sub-mode. Asset inventory protocol, role-aware tag pattern, canonical Stage D prompt structure, cross-skill routing recommendations, validation checklist, failure modes specific to multi-sheet pipelines, decoded examples. Load when the Character Bible Pipeline sub-mode is detected.

---

## Phase Handoff Protocol

Modes can chain. Typical multi-turn flows:

**Analysis → Production:** DECONSTRUCT a reference → REMIX that deconstruction for a new brand → refine with BUILD.

**Image → Sequence:** ANIMATE a single reference image (short clip) → BUILD a full multi-shot sequence around the same concept.

**Base → Extension:** BUILD or ANIMATE a 30s base → extend the twist with the T6 extension template once the base is confirmed.

**Full pipeline:** DECONSTRUCT reference → REMIX for new context → ANIMATE with reference images for key shots.

Between modes, verify:
- Previous mode output exists in the conversation
- User has confirmed or approved the previous output (or explicitly moved on)
- Required inputs for the next mode are available

If a user jumps modes without completing the previous one, note what is missing and ask if they want to continue the previous mode or proceed with incomplete inputs.

---

## Failure Recovery

**User uploads images with unclear intent**: If the user uploads images alongside a video request, route to ANIMATE. If they upload images but seem to want image prompts (not video), route to the appropriate image skill instead.

**User asks for a single monolithic prompt instead of staged**: For Seedance 2.5, a single staged script IS the right shape (one prompt, timestamped stages, end states). For other models, explain that shot-by-shot prompts give the generator more control, and consolidate only if they insist.

**User provides an extremely long or complex brief**: Break it into segments. Build one segment at a time. Confirm each before proceeding. For videos past 60 seconds, use the ultra-long template with anti-drift scaffolding rather than stretching a short prompt.

**User expects Claude to watch a video**: Claude cannot process video input. Route to DECONSTRUCT and ask the user to describe the video in text. The more specific their description (shot count, effects, timing), the better the deconstruction.
