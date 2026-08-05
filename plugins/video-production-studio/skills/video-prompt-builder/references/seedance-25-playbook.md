# Seedance 2.5 Playbook

Seedance 2.5 (ByteDance, released 2026-07-31 on CapCut / Dreamina / Jimeng, API via BytePlus ModelArk) is the current best-in-class video model and the default target for every prompt this skill produces. This file holds the platform facts, the working limits, and the fixes that are known to hold. Sources: ByteDance's own prompt guidance plus the highest-engagement community prompts (PJ Ace, Knightama, TechHalla, Jerrod Lew).

## Capability summary

- **30-second single-pass generation** with audio generated in the same pass. Double the 2.0 ceiling of 15s. Consumer app renders up to 4K; current API endpoints top out at 720p.
- **Video Extension.** Any video up to 30s can grow by 4-30 seconds per pass. Passes stack while the running total is 30s or less. Hard ceiling: 60-second final video. Original frames are never touched.
- **Ultra-Long mode.** One-shot generation of 30 to 180 seconds from a single prompt.
- **Timestamp control that holds.** "At second 5, she turns around" happens at second 5. Time ranges are budgets, not frame-exact cuts, so give each beat enough room or the model rushes it.
- **Reference ceilings:** 30 images, 10 video clips (30s combined), 10 audio clips (30s combined) per request. Audio-only generation is supported.
- **Reference sweet spots (ByteDance's own guidance, and the number that matters):** 1-8 distinct subjects from images, 1-5 from video or audio, reference clips 5-10 seconds each, edit sources under 20 seconds. Beyond these, results turn unstable and re-rolls pile up.
- **Real video editing.** Upload a video and change things in it: swap a subject, recolor clothing, remove a watermark, replace the background, strip the BGM while keeping voices. Editing preserves the source's aspect ratio and duration automatically. Do not ask to change those.
- **Negatives obey.** "No subtitles, no background music" sticks.
- **Multi-person casting fixed.** Characters in one frame no longer swap faces or merge.
- **De-AI-ed output.** Real skin texture, separated fur, natural speech, and complex motion (martial arts, dance, subtle facial acting) hold up.

## The four modes (CapCut / Dreamina panel)

1. **Omni Reference.** The default. Text plus any mix of image, video, and audio references.
2. **Smart Edit.** Upload a video, describe the change. Local uploads get an Advanced Edit toolbar: draw boxes, arrows, and markers on a frame to pin the edit to an exact region. Already-generated videos get the same through the Video Edit button.
3. **Ultra-Long Video.** 30 to 180 seconds via the clock icon.
4. **First & Last Frame.** Lock the opening and closing images; the model builds everything in between.

## Reference tags and binding

Tag forms: `@Image 1`, `@Video 1`, `@Audio 1`, group tags like `@Images 6-10`, and `@clay render 1` for untextured 3D blockouts. Seedance 2.0's lowercase `@image1` style still parses; stay consistent within one prompt.

The single biggest quality lever in 2.5: **bind every reference to a role, and state what it must NOT contribute.**

```
@Image 1 defines <Bride>'s face, hairstyle, and dress. Do not use the background.
@Image 2 defines <Groom>'s face and suit.
@Video 1 defines only the slow-dance motion. Do not use the people, clothing, or scene from the video.
@Audio 1 is the background music.
```

Rules:
- Every reference gets a role line AND an exclusion line. The exclusion line is what stops one reference's details leaking into shots it was never meant to touch.
- Priority order when trimming: core characters, then key props or products, then scene, then overall style.
- One character needing multiple angles gets separate images per angle, never a collage.
- Reuse the same references across shots and generations. Carried references are what keep a sequence consistent.

## Audio syntax

Four bracket types, worth memorizing:

- `(music)` in parentheses
- `<sound effects>` in angle brackets
- `{dialogue}` in braces
- `【subtitles】` in those brackets

Non-English dialogue: name the language and accent before the line for authentic delivery. The kill switch when music sneaks in anyway:

```
[SOUND] Strictly only naturally occurring sound and foley, no music allowed.
```

## Languages

Most heavily optimized: Chinese, English, Spanish, Indonesian, Malay. Fully supported: Thai, Arabic, Portuguese, Vietnamese, Japanese, Korean. Dialogue lip-syncs in all of them. For on-screen text, be explicit: "All on-screen text must be in Korean. No Chinese, English, or garbled characters." That covers signage, packaging, and captions, which makes one ad localizable across five markets.

## Extension workflows (the nesting doll)

Generate a clip (30s or less), extend by 4-30 seconds, prompt only the new part. Repeat while the result is 30s or less. Ceiling: 60s final.

- **Controlled reveal.** Generate the calm scene first, confirm it is perfect, then extend with the twist ("a UFO streaks past the window; the coffee cup shatters"). You re-roll only the twist, never the setup.
- **Action relay.** Hard moves land more reliably chopped into extension passes: generate "draws the sword," extend "lunges forward," extend "turns and sheathes."
- Every extension pass includes: "Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air."

## Editing formula

Target + change + timing + what stays the same:

```
Edit @Video 1. From seconds 1-8, replace the man's jeans with black tailored trousers. Keep his identity, motion, the camera movement, and everything else in the scene unchanged.
```

With Advanced Edit, draw a box first, then reference it: "Replace the sheep inside the red box with a brown horse, matching the original motion path, only during seconds 7-15."

Audio is editable separately: "Remove only the background music. Keep the dialogue, lip sync, ambience, and all visuals exactly as they are."

## Pro tools

- **Green screen, both directions.** "The white background becomes a green screen" for clean plates, or composite green-screen clips into scenes with automatic lighting and perspective matching.
- **Blockouts / clay renders.** Export a camera move or animatic from Maya or Blender, upload it, map each primitive to a reference image ("replace the white humanoid model with @Image 1's knight"). Coarse blockouts (simple shapes for motion and camera) work better than fine ones. Avoid limbed blockout figures unless the full limb motion is spelled out.
- **Storyboard grids.** A hand-drawn or stick-figure grid (15 panels or fewer, clean lines) plus "each panel is one full shot" and per-shot descriptions yields a coherent film that follows the boards.
- **Joining two clips.** "Seamlessly connect @Video 1 and @Video 2 without modifying either" plus a described bridge (a match cut, an object flying at the lens, a lens-filling foreground wipe). The model generates only the connective tissue.

## The reference bible workflow

The 30 image slots do not come from Seedance. They come from an image model, made and picked by hand, before the video prompt is written.

1. **Pick the image tool by what the shot needs.** Stylized or art-directed: Midjourney (route to `image-prompt-architect` or the user's preferred prompter). Realism, real faces, real materials and light: Nano Banana Pro (`nano-banana-unified`) or GPT Image 2 (`gpt-image-2-unified`).
2. **Lock one look for the whole project first.** One style code, one grade, one lighting register. Then generate by category under that locked style: wide establishing shot, environment, main character, key prop, closing shot.
3. **Build reference sheets for anything recurring.** Front, side, back, blank background. This is what lets the same character or product drop into new scenes without redrawing. The full pipeline for this lives in `references/character-bible-pipeline.md`.
4. **Freeze locked references.** If the motion looks wrong later, fix the motion prompt. Never regenerate a locked reference; a new image undoes the consistency work.

Keep one page per asset and an index in the project's files so a later session can reuse the set.

## Iteration economics

Generation is credit-hungry and a 180-second run costs serious credits. Perfect the cheap short base clip first, use Extension to iterate on the risky segment, and stay inside the reference sweet spots. Pushing past them is how you end up re-rolling.

## Troubleshooting (verbatim fixes that hold)

| Symptom | Fix |
|---|---|
| Music sneaks in despite "no music" | `[SOUND] Strictly only naturally occurring sound and foley, no music allowed.` |
| Something appears or vanishes at a transition | Add "no hard cuts, nothing appears out of thin air" at every transition point and describe the transition explicitly |
| Faces drift in long videos | `same face, same hairstyle, same outfit, same body type for the entire video` |
| Crowd looks like clones | "Background people differ in clothing color, hairstyle, and facial features; their movement is not perfectly synchronized." |
| Emotion reads flat | Never write "she is sad." Write the visible cues: breathing, brow, gaze, a swallowed sob. Pair every emotion word with something the camera can see |
| Blockout figure moves wrong | Use coarse primitives, or spell out the full limb motion |
| Reference details leak between shots | Add the exclusion line to every reference binding ("Do not use the background / identity / clothing / scene") |

## Pre-flight checklist

Before shipping any Seedance 2.5 prompt, verify:

- Subject and main action stated plainly.
- Every reference says what to use AND what to ignore.
- One primary change per stage, each with an explicit end state.
- Character count, clothing, and prop ownership consistent across stages.
- Forbidden list at the end (subtitles, BGM, morphing, extra characters).
- Reference counts inside the sweet spots (1-8 image subjects, 1-5 video/audio subjects).

Seedance 2.5 rewards writers who direct. Treat the prompt like a shooting script instead of a wish.

## Seedance 2.0 differences (legacy)

When the user explicitly targets 2.0 or a 2.0-era workflow: 15s ceiling, up to 9 image references (`@image1` lowercase style), 3 video and 3 audio references, no extension stacking, no ultra-long mode, no region-pinned editing, timestamp adherence approximate. The 2.0 patterns in `references/seedance-patterns.md` still apply there.
