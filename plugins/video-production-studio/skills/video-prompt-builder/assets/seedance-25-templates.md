# Seedance 2.5 Templates

Nine templates extracted from the highest-engagement Seedance 2.5 prompts in the wild (PJ Ace's one-take cheat sheet, Knightama's forgotten-footage oners, TechHalla's frozen-time sequences, ByteDance's official formulas), each with a note on why it works. Shared by BUILD and ANIMATE. Every template ships as one paste-ready code block. Platform facts and limits live in `references/seedance-25-playbook.md`.

## T1. One-Take (Oner)

The format behind the viral 30-second single-shot films. Seven labeled blocks, no cuts anywhere.

```
Main subject: [identity in dense concrete detail: age, features, clothing with specific garments, hair, texture notes like "realistic skin texture, minimal makeup"]. Keep identity, clothing, hairstyle, and appearance consistent throughout.

Location: [primary space in lived-in detail], transitions through [the physical path the take travels: doorways, stairs, exteriors]. Everyone [period/world]-accurate and natural.

Visual Style: [realism register: e.g. ultra-realistic documentary realism, candid behavior, busy lived-in environment full of background activity].

Camera Style: [camera identity: e.g. 1980s VHS camcorder / smartphone selfie / steadicam], single continuous unbroken take, no cuts. [Who or what carries the camera and how it moves with the subject.] [Artifact vocabulary matched to the camera identity: handheld shake, autofocus hunting, exposure pumping, motion blur, grain, lens flares, bodies briefly blocking the lens.] No stabilization. No cinematic moves. No edits. One take start to finish.

Action (continuous, single take): [A chain of small physical beats with cause and effect. The camera picks up the subject mid-action. Each beat is one concrete physical interaction: a shoulder bump, a grabbed flyer, a door pushed open, a ball trapped underfoot. Route the chain along the location path. End on a deliberate closing beat, e.g. a look into the lens, then the recording cuts to black mid-motion.]

Audio: Natural ambient sound only: [layered ambience matched to each space along the path]. No music. No sound design. No narration.

Goal: [One sentence stating the intent: a single continuous unbroken take following X through Y. Candid, imperfect, believable.]
```

Why it works: dense concrete detail per block gives the model an unambiguous world; the identity-lock line and "one take start to finish" are explicit continuity contracts; artifact vocabulary sells realism harder than any quality adjective; and action written as chained micro-beats with cause and effect is what keeps 30 seconds coherent instead of mushy.

## T2. Timed-Beats Cinematic

The frozen-time / rewind / spectacle structure. Global style, timestamped stages with shot-type tags, closing constraint paragraph.

```
[Global style paragraph: photorealistic cinematic + era + location + lighting + texture notes like "subtle handheld texture, heavy natural film grain".]

0-[X]s: [Shot type: Medium Wide / Dynamic Tracking / Slow 360° Orbital / Extreme Close-Up] [One primary event. Who is in frame, what they do, what begins.]

[X]-[Y]s: [Shot type] [The next primary event. If time manipulation is the gimmick, state it mechanically: "Time locks completely at the peak of the spill. Every face freezes. Only she keeps moving."]

[Y]-[Z]s: [Shot type] [The showcase stage. Physics language earns its keep here: suspended droplets with surface tension, floating debris, weightless fabric.]

[Z]-30s: [Shot type] [Resolution beat, then a final punctuation shot: hard cut to a close-up, a knowing look, a held expression.]

[Closing paragraph: photorealistic, ultra-detailed fluid physics, motion blur only on moving elements, stable characters, cinematic lighting, heavy natural film grain, no artifacts, movie-level temporal coherence.]
```

Why it works: 2.5's timestamp control is real, so the stages land where written; shot-type tags steer framing per stage; physics vocabulary plays directly to the model's simulation strength; and the closing paragraph locks temporal coherence across the whole run.

## T3. Staged Script with End States

ByteDance's official formula for any multi-beat 30s video. The most reliable general-purpose structure.

```
[0-8s] [One primary action.] End state: [exactly where things are when the stage closes].
[8-16s] [One primary action.] End state: [...].
[16-24s] [One primary action.] End state: [...].
[24-30s] [Closing action.] End state: [...].
Keep [subject]'s identity, clothing, and [key environment element] consistent throughout. No subtitles, no background music.
```

Rules: one primary change per stage; an explicit end state for every stage; a consistency line and a forbidden list at the end. Time ranges are budgets, not frame-exact cuts, so give each beat enough room or the model rushes it.

Why it works: end states convert vague motion into checkable targets, which is what stops actions half-completing; one change per stage prevents the prop-teleporting that killed stretched 15s prompts.

Default beat rhythm when the story has no natural structure (ByteDance's own map): 0-6 set the scene, 6-14 build, 14-24 the turn, 24-30 how it ends. Write the same six details for every beat: subject, action, setting, camera, style, rules.

## T4. Reference-Binding Casting Block

Prepend to any prompt that uses references. The single biggest quality lever in 2.5.

```
@Image 1 defines <CharacterName>'s face, hairstyle, and [garment]. Do not use the background.
@Image 2 defines <SecondCharacter>'s face and [garment].
@Video 1 defines only the [motion type] motion. Do not use the person's identity, clothing, or scene from the video.
@Audio 1 is the background music.
```

Why it works: the model has no idea what role an upload plays unless told; the exclusion line ("do not use...") is what stops one reference's details leaking into shots it was never meant to touch. Every tag gets both lines. Priority when trimming: characters, then props, then scene, then style.

## T5. Edit Prompt (Smart Edit)

Target + change + timing + what stays the same.

```
Edit @Video 1. From seconds [X-Y], [the change: replace / recolor / remove / add]. Keep [identity, motion, the camera movement, and everything else in the scene] unchanged.
```

Region-pinned variant (after drawing a box in Advanced Edit): "Replace the [subject] inside the red box with [replacement], matching the original motion path, only during seconds [X-Y]." Audio-only variant: "Remove only the background music. Keep the dialogue, lip sync, ambience, and all visuals exactly as they are." Editing preserves the source's aspect ratio and duration; do not ask to change them.

Why it works: the four-part formula scopes the diff. Anything not named in the change clause is protected by the keep clause, so the model stops "helpfully" regenerating the rest of the frame.

## T6. Extension (Nesting Doll)

Prompt only the new segment. The original frames are never touched.

```
[What happens in the new segment only, written as a continuation of the final frame.] Extend the video naturally, smooth motion continuity, no hard cuts, nothing appears out of thin air.
```

Two proven workflows:
- **Controlled reveal.** Generate the calm base, confirm it is perfect, extend with the twist. Re-roll only the twist.
- **Action relay.** Chop a hard move into passes: "draws the sword," extend "lunges forward," extend "turns and sheathes."

Limits: +4-30s per pass, stack while the running total is 30s or less, 60s final ceiling.

Why it works: each pass is a small, cheap, independently re-rollable bet, and the boilerplate line suppresses the two classic extension artifacts (hard cuts and pop-in).

## T7. Ultra-Long (30-180s)

Everything from T3, scaled up, with anti-drift scaffolding.

```
Full video [N] seconds, [aspect ratio], [global style and world]. [Consistency requirements stated here at the top: same face, same hairstyle, same outfit, same body type for the entire video. Reference bindings per T4 if references are in play.]

[0-[X]s] Camera: [...]. Action: [...]. Dialogue: {[...]}. Sound: <[...]>.
[[X]-[Y]s] Camera: [...]. Action: [...]. [Re-mention @references as they appear.]
[... one block per time window through [N]s ...]

[Global style paragraph restated.] Same face, same hairstyle, same outfit, same body type for the entire video. No subtitles, no background music, no morphing, no extra characters.
```

Why it works: long generations drift, so the consistency requirements appear at the start AND the end, global parameters are restated at the top, and references are re-mentioned throughout. Per-window blocks carry camera, action, dialogue, and sound so no stretch of the timeline is unsupervised.

## T8. Join Two Clips

```
Seamlessly connect @Video 1 and @Video 2 without modifying either. Bridge: [describe the connective tissue: a match cut on shape, an object flying at the lens, a lens-filling foreground wipe]. Smooth motion continuity, nothing appears out of thin air.
```

Why it works: "without modifying either" scopes generation to the bridge alone, and naming the transition device gives the model a concrete mechanism instead of a vague "blend."

## T9. Audio Direction Block

Seedance 2.5 generates audio in the same pass. Direct it with the native bracket syntax.

```
(music: [style, instrumentation, when it enters])
<sound effects: [foley list, tied to on-screen events]>
{[Language, accent] dialogue: "[line]"}
【subtitles: [only if wanted; otherwise omit and forbid]】
```

For clean footage, replace the block with the kill switch: `[SOUND] Strictly only naturally occurring sound and foley, no music allowed.` A plain "no music" sometimes loses the fight; the dedicated sound directive holds.

Why it works: the bracket types are the model's native channel separation, and naming language plus accent before a dialogue line is what produces authentic delivery and correct lip sync.

---

# Format Recipes

Condensed direction for five formats with proven viral results. Use with T1-T3 as the structural base.

**KPOP / music video.** Hard cuts landing exactly on the snare or the drop, never soft crossfades. Symmetrical center-weighted framing, recurring archways or portals to dolly through at performer eye level. One bold saturated palette locked across every scene, skin tones neutral-to-warm. Lip sync holds best on medium close-ups with crisp diction, open vowels, staccato phrasing written into the prompt. One dance move per cut, not a continuous take.

**Vlog realism.** Skip tripod language; describe the shake: handheld micro-jitter, arm's-length selfie framing, natural body sway. Light with whatever is already there and let it change per location. Cut on movement (a turn, a step off a curb, a hand on a door), with quick b-roll cutaways. Warm soft grade outdoors, cooler and flatter interiors. The giveaway details sell it: a visible mic cable, hair across the face, a direct look at the lens like talking to a friend.

**Product with 3D elements.** Describe materials by physical property, not name: "glossy polycarbonate with internal light scatter," "matte PBT-style plastic with high diffuse roughness." One camera move per shot: a slow 360-degree orbit for material read, a straight pull-back for an exploded-parts reveal, never both blended. Large diffused softbox light, thin rim light on translucent edges, gradient specular sweep as the camera moves. Infinite studio backdrop, soft pastel gradient, gentle ambient occlusion under floating parts. Grade pastel with lifted blacks, nothing blown out.

**Realistic lighting.** Name the light's direction and color temperature separately: a warm key against a cool sky-fill reads as real, a single flat light never does. Hard directional light close up (crisp speculars, sharp shadow edges), atmospheric haze softening with distance. Weight on edges: rim light in flyaway hair, a flare blooming exactly when the camera tilts sunward, highlights that roll off instead of clipping. Shadows imperfect, picking up bounced color from nearby surfaces. Background layers lose contrast and saturation with distance; skipping atmospheric perspective is the fastest way back to synthetic.

**Animation.** Pick one reference era and commit; never blend three styles. Name the exact register: cel-shaded, painterly-over-3D, or classic 2D. Mix frame rates on purpose: character on twos for the hand-drawn feel, camera and vehicles in smooth continuous motion. Camera language deliberate: extreme close-ups on hands and mechanisms, smooth tracking on action, dramatic low angles for the biggest moment. Painterly shading with visible brushstroke texture over the geometry. One palette family across every scene.
