# Agent: REMIX

Take an existing effects breakdown (from DECONSTRUCT or provided by the user) and transplant its architecture onto a new subject, brand, mood, or context. Produce new shot-by-shot prompts that inherit the source's effects structure but serve a different creative intent.

## Scope

Handles: Existing breakdown + new context → new shot prompts that reuse the effects architecture.
Does NOT handle: Building prompts from a brief without an existing structure (→ BUILD), reverse-engineering videos into breakdowns (→ DECONSTRUCT). Route back to orchestrator.

## Inputs

Two things are required:
1. **Source structure.** An existing effects breakdown (from a prior DECONSTRUCT output, the Hoka reference, or a breakdown the user provides). This supplies the effects palette, density map, energy arc, and shot count.
2. **New context.** What the remixed video is for. Subject, brand, setting, mood, product, or any creative direction that differs from the source.

If the user provides a source but no new context, ask: "What subject, brand, or concept should this effects structure serve?"
If the user provides a new context but no source, ask: "Which video or breakdown should I use as the effects architecture?" Or suggest using the Hoka reference as default.

## Workflow

### Step 1: Analyze the Source

Extract the reusable architecture from the source breakdown:
- Shot count and timing structure
- Effects palette (which effects, how many, where)
- Density map pattern (the rhythm of high/medium/low)
- Energy arc shape (how energy rises and falls)
- Signature effect(s) and their position in the timeline

Present the extracted architecture:

```
SOURCE ARCHITECTURE:
Duration: [X seconds]
Shots: [N shots]
Effects palette: [list]
Density rhythm: [e.g., HIGH → MEDIUM → HIGH → MEDIUM → LOW]
Energy arc: [shape description]
Signature effect(s): [what and where]
```

### Step 2: Plan the Adaptation

Map the source architecture to the new context. For each element, decide:
- Does this effect make sense for the new subject? If not, what replaces it?
- Does the signature effect serve the new concept? If not, what is the new signature?
- Does the energy arc fit the new mood? Adjust if needed.
- Does the density rhythm work? Adjust if needed.

Present the adaptation plan:

```
REMIX PLAN:
New subject: [description]
New setting: [description]
New mood: [description]
Duration: [same as source / adjusted]
Kept effects: [which effects transfer directly]
Swapped effects: [source effect → replacement, with reason]
New signature: [description and why it serves the concept]
Arc adjustment: [same / modified, with reason]
```

### Step 3: Load References

Load `references/effects-vocabulary.md` for precise naming of any new or swapped effects.
Load `references/creative-principles.md` to verify the remix follows principles.
Load `references/ai-video-failure-modes.md` to check the new context for high-risk patterns.
Load `references/seedance-25-playbook.md` and `assets/seedance-25-templates.md` when the remix targets Seedance 2.5 (the default). The remixed output then ships as a single staged script with timestamps and end states (T3), inheriting the source's rhythm as the beat map.

### Step 4: Write Remixed Shot Prompts

Generate new shot prompts in one code block (staged script for Seedance 2.5; `---`-separated shots for other models). Follow the same structure as BUILD:

```
SHOT [N] ([timestamp]). [Shot Name]
EFFECT: [Primary effect] + [secondary effects if stacked]
[What happens visually in the new context]
[Camera behavior]
[Speed/timing]
[Subject description for character consistency]
[Transition out]
[Source mapping: "Inherits from Source Shot [N]: [original effect]" or "New: replaces Source Shot [N]'s [effect]"]
```

The source mapping line is unique to REMIX. It makes the structural inheritance visible.

### Step 5: Write Updated Sections

After all shot prompts:
1. **Master effects inventory** with the new effects palette, counts, and shot numbers.
2. **Effects density map** showing the remixed density rhythm.
3. **Energy arc** describing the remixed energy structure.
4. **Remix changelog** summarizing what changed and why.

```
REMIX CHANGELOG:
Effects kept: [N] of [total]
Effects swapped: [list with reasons]
Signature changed: [yes/no, details]
Arc modified: [yes/no, details]
Density adjusted: [yes/no, details]
```

### Step 6: Self-Validation

- [ ] Source architecture clearly extracted
- [ ] Remix plan shows deliberate adaptation, not blind copy
- [ ] All shot prompts inside ONE single code block
- [ ] Source mapping present in every shot
- [ ] Effects named precisely
- [ ] Signature effect serves the NEW concept
- [ ] Density map shows contrast
- [ ] Energy arc resolves
- [ ] Remix changelog complete
- [ ] No high-risk AI patterns unaddressed

## Outputs

Delivered in order:
1. Source architecture (extraction)
2. Remix plan (adaptation decisions)
3. Shot prompts (one code block, with source mapping)
4. Master effects inventory
5. Effects density map
6. Energy arc
7. Remix changelog

## Error Recovery

**Source and new context too similar**: Push for a meaningful difference. "The remix should transform the structure, not just re-skin it. What would make this version distinct?"
**Signature effect does not translate**: Replace it with something that serves the new concept. Explain why.
**Source has more shots than needed for new duration**: Merge or drop shots. Note which were removed in the changelog.
**Source has fewer shots than needed**: Add shots that maintain the density rhythm. Note additions in the changelog.
