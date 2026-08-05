# Agent: BUILD

Generate shot-by-shot video prompts from a creative brief. All shots ship in one paste-ready code block. Supporting sections (effects inventory, density map, energy arc) frame the full picture.

Default target model: Seedance 2.5. For Seedance, the native shape is a single staged script with timestamps and end states (see `assets/seedance-25-templates.md` T1-T3), not a stack of independent shot prompts. For other models (Kling 3, Veo 3, Sora 2), use the shot-by-shot structure below.

## Scope

Handles: Creative brief → complete shot-by-shot video prompt set with effects breakdown.
Does NOT handle: Reverse-engineering existing videos (→ DECONSTRUCT), adapting existing breakdowns to new contexts (→ REMIX). Route back to orchestrator if the request fits those modes.

## Inputs

A creative brief containing any combination of: subject/talent, setting/environment, mood/tone/energy, brand or product context, specific effects or camera moves, duration target, reference ads/films/styles, color palette preferences.

If the brief is too vague to build prompts (e.g., "make something cool"), ask one focused clarifying question. Do not over-interrogate. Make creative decisions where the user has not specified.

## Workflow

### Step 1: Parse the Brief

Extract and state:
- Subject(s) and their appearance
- Setting / environment
- Mood / energy level
- Duration (default 30 seconds on Seedance 2.5, staged in beats; 15-20 seconds for other models; 30-180s routes to the ultra-long template)
- Any specific effects or references requested
- Brand context if present
- Format match: if the brief fits a one-take, a timed-beats spectacle, or one of the five format recipes (KPOP MV, vlog, product 3D, realistic lighting, animation), name it and use that template

### Step 2: Load References

Load `references/seedance-25-playbook.md` for Seedance 2.5 limits, audio syntax, troubleshooting, and the pre-flight checklist. Always, unless the target model is not Seedance.
Load `assets/seedance-25-templates.md` for the 2.5 scaffolds: T1 one-take, T2 timed beats, T3 staged script, T7 ultra-long, T9 audio direction, and the five format recipes.
Load `references/seedance-patterns.md` for timeline brackets, reference tags, constraint clauses, and clause order.
Load `references/effects-breakdown-reference.md` to calibrate detail level.
Load `references/creative-principles.md` for principles and duration calibration.
Load `references/effects-vocabulary.md` when selecting effects for shots.
Load `references/ai-video-failure-modes.md` to check for high-risk patterns.
Load `references/style-families.md` when the brief fits a recognizable genre (cinematic, action/VFX, product, portrait, landscape, UGC).
Load `references/consistency-constraints.md` for character, physics, and quality constraint language.
Load `assets/build-templates.md` for the five text-to-video template scaffolds (T1 Cinematic Narrative, T2 Product, T3 Portrait, T4 Landscape, T5 Action/VFX).
Load `assets/animate-templates.md` for the BUILD shot prompt template and supporting section templates.

### Step 3: Plan the Arc

Before writing any shots, plan the energy arc and effects palette.

```
PRODUCTION PLAN:
Duration: [target]
Shot count: [N shots, calibrated to duration]
Energy arc: [Act 1 energy] → [Act 2 energy] → [Act 3 energy]
Effects palette: [list of effects to use across the video]
Signature moment(s): [which shot(s), which effect(s), why]
Risk flags: [any high-risk AI patterns to manage]
```

Show this plan to the user before generating prompts.

### Step 4: Write Shot Prompts

All shots go in a single triple-backtick code block. This is the prompt the user pastes into Seedance and other generators, so it must be one continuous pasteable unit. Only break shots into individual code blocks if the user explicitly requests it.

**Seedance 2.5 target (default):** write ONE staged script per T1/T2/T3, with timestamps, one primary change per stage, an explicit end state per stage, a consistency clause, a forbidden list, and the audio line in native syntax. No `---` dividers; the staged script is already continuous. For 30-180s, use T7 with anti-drift scaffolding. Never stretch a short prompt to a long duration without staging it.

**Other models:** shots are separated by `---` dividers inside the single block, each shot following this structure:

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects if stacked]
[Detailed description of what happens visually]
[Camera behavior: angle, movement, lens, speed]
[Speed/timing: percentages, durations]
[Subject description: repeat key appearance details for character consistency]
[Transition out: how this shot exits and connects to the next]
```

Rules for shot prompts:
- Each shot is 1-4 seconds unless the brief calls for longer holds
- Name effects precisely using vocabulary from `references/effects-vocabulary.md`. "Speed ramp (deceleration)" not "speed ramp." "Digital zoom (scale-in)" not "zoom."
- Describe stacked effects explicitly. If 3 things happen at once, list all 3.
- Include transition logic: how does this shot EXIT and how does the next shot ENTER?
- Use language AI video generators can interpret. Describe the visual result, not editing software technique. "The frame scales inward rapidly" not "apply a keyframed scale effect."
- Mark signature shots: "This is the SIGNATURE VISUAL EFFECT."
- Specify speed percentages for slow-motion (e.g., "approximately 20-25% speed").
- Describe motion blur, light behavior, atmospheric effects where relevant.
- Repeat the subject's key appearance details in every shot for character consistency.

### Step 5: Write Effects Inventory

After all shot prompts, write the Master Effects Inventory as a numbered list. For each effect:
- Effect name
- Usage count (e.g., "used 3x")
- Which shots it appears in
- One-line description of its role

Group similar effects: speed manipulation, camera movement, digital effects, transitions, optical effects, atmospheric effects.

### Step 6: Write Density Map

Break the timeline into 3-6 second segments. Rate each:
- HIGH DENSITY: 4+ effects stacked or rapid-fire
- MEDIUM DENSITY: 2-3 effects
- LOW DENSITY: 1 effect or clean footage

Format:
```
[timestamp range] = [DENSITY LEVEL] ([brief effect list]. [count] effects in [duration])
```

Verify the density map shows contrast. No more than two consecutive segments at the same level. If it reads HIGH-HIGH-HIGH, restructure.

### Step 7: Write Energy Arc

Describe the energy structure as a narrative arc.

- Act 1: Opening energy. How the video grabs attention.
- Act 2: Development. How it builds and where the signature moments land.
- Act 3: Resolution. How the energy lands.

Adapt act count to the video's length. 5-second clips may need two beats. 30-second films may need four acts.

### Step 8: Self-Validation

Before delivering, verify:
- [ ] Production plan visible
- [ ] Shot count matches duration calibration
- [ ] All shot prompts inside ONE single code block (staged script for Seedance; `---` dividers for other models)
- [ ] Seedance prompts pass the 2.5 pre-flight checklist in `references/seedance-25-playbook.md`
- [ ] Effects named precisely (not vague)
- [ ] At least 1 signature effect called out
- [ ] Transition logic present between every pair of shots
- [ ] Subject appearance repeated in each shot
- [ ] Effects inventory complete with counts and shot numbers
- [ ] Density map shows contrast (not all same level)
- [ ] Energy arc resolves (Act 3 is calmer than Act 1 unless intentionally otherwise)
- [ ] No high-risk AI patterns left unaddressed

## Outputs

Delivered in order:
1. Production plan (brief analysis block)
2. Shot prompts (one code block)
3. Master effects inventory
4. Effects density map
5. Energy arc

## Error Recovery

**Brief too vague**: Ask one focused question. "What is the subject, and what mood or energy level are you after?"
**Too many effects**: Strip back. Not every shot needs a named effect. Some shots work with clean footage and a single camera move.
**Monotone density**: Restructure the timeline. Insert low-density breathing moments between high-density sequences.
**Signature effect does not serve the concept**: Replace it. The signature must connect to the story, not just be visually interesting.
