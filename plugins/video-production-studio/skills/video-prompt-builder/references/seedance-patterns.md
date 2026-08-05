# Seedance Technical Patterns

Production patterns for Seedance prompts, updated for Seedance 2.5 as the primary target. Use these to harden BUILD and ANIMATE output. Full 2.5 platform facts, limits, and troubleshooting live in `references/seedance-25-playbook.md`. Full prompt scaffolds live in `assets/seedance-25-templates.md`.

## Timeline Brackets

Native multi-shot syntax. More structured than plain Shot 1 / Shot 2 labels, and 2.5's timestamp control makes the brackets land where written.

```
[0-8s] Shot 1: [description]. End state: [where things are when the stage closes].
[8-16s] Shot 2: [description]. End state: [...].
[16-24s] Shot 3: [description]. End state: [...].
[24-30s] Shot 4: [description]. End state: [...].
```

Rules: one primary change per stage, an explicit end state per stage. Time ranges are budgets, not frame-exact cuts, so size each stage to its action. Default 30s rhythm when the story has no natural beats: 0-6 setup, 6-14 build, 14-24 turn, 24-30 resolution.

## Reference Tags

2.5 tag forms, bound by role:

- `@Image 1`, `@Image 2`... image references, numbered by upload order. Group form: `@Images 6-10`.
- `@Video 1`... video references: motion, camera behavior, pacing, or a clip to extend, edit, or join.
- `@Audio 1`... audio references: beat sync, ambience, voice, or BGM.
- `@clay render 1`. untextured 3D blockout that locks camera movement and blocking while image references carry the look.

Ceilings: 30 images, 10 videos (30s combined), 10 audio (30s combined). Sweet spots that actually hold: 1-8 image subjects, 1-5 video/audio subjects, reference clips 5-10s.

**Every tag gets a role line and an exclusion line:**

```
@Image 1 defines <Bride>'s face, hairstyle, and dress. Do not use the background.
@Video 1 defines only the slow-dance motion. Do not use the person's identity, clothing, or scene from the video.
```

The exclusion line is what stops reference details leaking into shots they were never meant to touch. Seedance 2.0's lowercase `@image1` style still parses; stay consistent within one prompt.

## Positive Constraints Clause

Standard closing clause for photorealistic or character-driven prompts:

```
Consistent faces and clothing, no deformation, realistic physics, stable proportions, no artifacts.
```

Variants by context:
- Character: "consistent faces, clothing, hairstyles throughout without deformation, drift, or artifacts"
- Long video anti-drift (verbatim, it works): "same face, same hairstyle, same outfit, same body type for the entire video"
- Physics-heavy: "consistent gravity, realistic material response, accurate collision"
- Portrait: "clear undeformed face, normal human body structure, rich details"
- Crowds: "background people differ in clothing color, hairstyle, and facial features; their movement is not perfectly synchronized"

2.5 obeys negatives, so close with a forbidden list: "No subtitles, no background music, no morphing, no extra characters."

## Audio Cues

2.5 generates audio in the same pass as video. Native syntax: `(music)`, `<sound effects>`, `{dialogue}`, `【subtitles】`. Name language and accent before dialogue lines for authentic delivery and lip sync.

Every Seedance prompt closes with an audio line. Format for ambient-only work: `[ambient sound], [foreground sound], [music or score], [dialogue cue if any].`

Examples:
- "Rustling leaves, blade ring, distant birds."
- "Warm jazz piano, ambient kitchen clatter, soft laughter."

When music must stay out, a plain "no music" can lose. The kill switch: `[SOUND] Strictly only naturally occurring sound and foley, no music allowed.`

## Lens and Format Specs

Filmic markers that materially improve output quality:
- **24fps**. cinematic default
- **35mm anamorphic**. widescreen filmic grain
- **2.35:1**. cinematic widescreen ratio
- **8K sharp** or **4K resolution**. detail target
- **Shallow DOF / creamy bokeh**. subject isolation
- **Warm film grain**. analog texture

Drop 2-3 of these into the Style line of any prompt.

## Subject-Action-Environment-Camera-Style Order

Harvested prompts consistently follow this clause order within a shot:

1. **Subject** (who/what, with identity anchors)
2. **Action** (what happens)
3. **Environment** (where)
4. **Camera** (movement, angle, lens)
5. **Style** (aesthetic, film format, grade)
6. **Constraints** (consistency clause + forbidden list)
7. **Audio** (native syntax cues)

This order is not mandatory but matches the pattern in the highest-engagement prompts.

## Word Count Sweet Spot

60-150 words per prompt for single-shot. 200-500 words for a full 30s staged script. Viral 30s oners run 400-600 words when the world detail carries the realism. Ultra-long (30-180s) prompts scale with per-window beats but restate consistency at start and end. Below 60 words loses detail. Padding without concrete detail introduces contradictions.

## Never Stretch, Always Stage

The classic 2.5 failure: taking a 15-second-era prompt and asking for 30 seconds without staging it. The model tries anyway, and you get actions that make no sense, props from nowhere, and characters that stop looking like themselves. A longer video means the same detail per beat as before, written four times over, not one paragraph stretched thin.
