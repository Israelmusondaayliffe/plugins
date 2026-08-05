# AI Video Generation Failure Modes

What current AI video models (Seedance, Kling, Veo, Sora, Runway) struggle with. These failure modes should inform how prompts are constructed.

## What Seedance 2.5 Changed

Several classic failure modes below are substantially fixed on Seedance 2.5 and should not be over-hedged when it is the target:

- **Precise timing works.** Timestamped stages land where written. Time ranges are budgets, not frame-exact cuts, so size stages to their action.
- **Long takes hold.** 30 seconds in one pass, 60s via extension stacking, 30-180s in Ultra-Long mode with anti-drift scaffolding.
- **Multi-person casting fixed.** Characters in one frame no longer swap faces or merge. Crowds work when variety is demanded explicitly.
- **Negatives obey.** "No subtitles, no background music" sticks (use the `[SOUND]` directive when music still fights back).
- **Texture and complex motion hold.** Real skin, separated fur, martial arts, dance, subtle facial acting.
- **On-screen text works when the language is stated explicitly** ("All on-screen text must be in Korean. No garbled characters.").

What still fails on 2.5:

- **Reference overload.** Ceilings are 30 images / 10 videos / 10 audio, but quality holds at 1-8 image subjects and 1-5 video/audio subjects. Past the sweet spots, results get unstable and re-rolls pile up.
- **Stretched prompts.** A 15-second-era prompt asked to fill 30s without staging produces nonsense actions, pop-in props, and identity drift. Stage everything.
- **Collages.** One image with multiple angles degrades identity binding. Separate images per angle.
- **Unbound references.** Tags without a role line and an exclusion line leak details across shots.
- **Limbed blockouts.** Clay-render figures with limbs move wrong unless the full limb motion is spelled out. Coarse primitives work better.
- **Emotion labels.** "She is sad" reads flat. Only visible physical cues land.

The sections below describe the general case across models. Apply them fully to Kling, Veo, Sora, and Runway; apply them with the exceptions above to Seedance 2.5.

## High-Risk Patterns

**Crowds doing varied actions.** Multiple people performing different independent actions almost always degrades. Bodies merge, limbs multiply, faces distort. Keep the subject count low. One or two subjects max for quality work.

**Multi-speaker dialogue.** Lip-sync breaks down with more than one speaker. If dialogue is needed, frame one speaker at a time.

**Complex physics interactions.** Liquids pouring into containers, balls bouncing with accurate trajectories, cloth draping over complex shapes. The physics will be approximate at best, broken at worst.

**Text and signage.** Any text visible in frame will likely corrupt. Letters scramble, words morph. Avoid prompts that depend on readable text.

**Hands and fingers in close-up.** Extra fingers, fused fingers, impossible grips. If hands are not the focus, they are usually fine. If they are the focus, expect problems.

**Character consistency across cuts.** A subject in Shot 1 may not look the same in Shot 5 unless the prompt heavily anchors their appearance. Image-to-video helps here. Describe the subject consistently across every shot.

**Long continuous takes.** Most models handle 3-8 seconds well. Beyond that, quality degrades. Break long sequences into shorter shots with transitions.

## Medium-Risk Patterns

**Rapid camera movement.** Whip pans and fast orbits can cause warping or tearing. The prompt should describe the motion clearly but keep the most aggressive movements to 1-2 seconds.

**Stacked digital effects.** Models handle one or two effects per shot well. Three or more stacked effects (zoom + shake + rotation + speed ramp) increase the chance of visual chaos. Stack sparingly, save it for signature moments.

**Precise timing.** "At exactly 2.3 seconds the hand reaches the object." Models do not have frame-accurate timing control. Use approximate ranges, not exact timestamps.

**Reflections and mirrors.** Reflective surfaces often produce inconsistent reflections. The reflection may not match the subject.

**Fine detail at distance.** Intricate patterns, small facial features, or detailed textures far from camera will likely simplify or smear.

## Low-Risk Patterns (Safe Bets)

**Single subject, simple action.** One person walking, running, turning, looking. This is the sweet spot.

**Atmospheric effects.** Fog, rain, dust, snow, god rays. Models handle these well.

**Camera movements at moderate speed.** Slow push-ins, gentle orbits, smooth tracking. These are reliable.

**Lighting changes.** Golden hour warmth, dramatic shadows, light shifts. Models understand lighting well.

**Slow-motion on a single subject.** Reducing speed on a clear action is well-handled.

**Static or near-static compositions with subtle motion.** A portrait with wind in the hair. A product on a turntable. These work consistently.

## Prompt Construction Implications

When writing shot-by-shot prompts, use this knowledge to:

1. Keep subject count to 1-2 per shot.
2. Avoid text, signage, or readable content in frame.
3. Limit effect stacking to 2 per shot for reliability, reserving 3+ stacks for the designated signature moment.
4. Describe the subject's appearance in every shot for character consistency.
5. Use image-to-video as the primary workflow whenever possible. Generate a reference image first, then animate.
6. Keep individual shot durations between 1-4 seconds.
7. Use approximate ranges for timing ("approximately 2-3 seconds") rather than exact values.
8. When a prompt involves a high-risk pattern, flag it in the shot description and note the risk.
