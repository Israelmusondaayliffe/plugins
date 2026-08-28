# Validation Criteria

Objective scoring rubrics for consistent quality assessment. Use with `scripts/unslop-engine/quality_validator.py` for deterministic checks.

<!-- harness-quality-gate: literal-list-start -->
## Three-Tier Validation Model

### Tier 1: Structural Integrity (Gate Pass/Fail)

These must ALL pass before proceeding:

| Criterion | Pass | Fail |
|-----------|------|------|
| Intent clarity | Purpose evident in first paragraph | Reader confused about why they're reading |
| Decision enablement | Clear what action to take | "So what?" unanswered |
| Information completeness | All claims supported | Gaps require user clarification |
| Fabrication check | All facts trace to user input | Any invented details present |

**If ANY Tier 1 criterion fails:** Return to Phase 1 (Intent Extraction). Do not apply quality techniques to content with unclear purpose.

### Tier 2: Voice Consistency (Score 0-10)

| Score | Description |
|-------|-------------|
| 10 | Indistinguishable from user's natural writing |
| 9 | Minor deviations, clearly same voice |
| 8 | Voice preserved, slight polish visible |
| 7 | Voice recognizable, some generic elements |
| 6 | Mix of user voice and generic quality |
| 5 | Generic with traces of user voice |
| 4 | Mostly generic, few user markers |
| 3 | Generic quality writing |
| 2 | AI-sounding with forced improvements |
| 1 | Completely overwrote user's voice |
| 0 | Not attempted |

**Calculation:**
- Start at 10
- Subtract 1 for each characteristic phrase lost
- Subtract 1 for tone shift (formal→casual or reverse)
- Subtract 2 for sentence rhythm change
- Subtract 1 for structure preference violation
- Minimum 0

**Threshold:** Score at least 8 required. Target 10. Below 8 means revise with voice profile focus.

### Tier 3: Technical Quality (Score 0-10)

| Component | Weight | Scoring |
|-----------|--------|---------|
| Authored em-dash elimination | 1.5 points | 1.5 = zero in editable prose, 0 = any; protected exact material is excluded |
| AI-tell elimination | 2 points | 2 = zero, 1.5 = 1-2, 0.5 = 3-5, 0 = 6+ |
| Cliche elimination | 1 point | 1 = zero, 0.5 = 1-2, 0 = 3+ |
| Hedge elimination | 1 point | 1 = zero in conclusions, 0.5 = 1-2, 0 = 3+ |
| Copula avoidance (V3) | 1 point | 1 = zero, 0.5 = 1-2, 0 = 3+ |
| -ing constructions (V3) | 1 point | 1 = zero, 0.5 = 1-2, 0 = 3+ |
| Significance inflation (V3) | 1 point | 1 = zero, 0.5 = 1-2, 0 = 3+ |
| Sycophancy/chatbot (V3) | 0.5 points | 0.5 = zero, 0 = any found |
| Base | 1 point | Always awarded |

**Maximum:** 10 points

**Additional flags (not scored but reported):**
- Curly quotation marks (ChatGPT artifact)
- Negative parallelisms (overuse indicator)
- Rule of three (forced triplets)
- Generic positive conclusions

**Structural-slop deduction (V5):**
- Subtract 0.5 per explicit structural-slop hit, up to 2 points.

**Threshold:** Score at least 8 required. Target 10. Below 8 means revise specific failing components.

## Composite Quality Score

**Formula (V5):**
```
Overall = (Voice x 0.35) + (Technical x 0.35) + (Texture x 0.1) + (Intent x 0.2)

Where:
  Intent = 10 if Tier 1 passes, 0 if fails
  Texture = 10 if source-backed voice texture remains, 0 if the edit erased it or invented personality
```

**Interpretation:**
| Score | Quality Level | Action |
|-------|---------------|--------|
| 9-10 | Excellent | Ship confidently |
| 8-8.9 | Good | Ship, note minor improvements possible |
| 7-7.9 | Below threshold | Revise before shipping |
| 6-6.9 | Below threshold | Revise before shipping |
| 5-5.9 | Poor | Major revision needed |
| <5 | Failed | Return to Phase 1 |

## Detailed Rubrics

### Em-Dash Detection

**What counts as em-dash:**
- Standard em-dash: `U+2014`
- Double hyphen used as em-dash: --
- En-dash used as em-dash: `U+2013`

**Severity levels:**
- Zero authored em dashes in editable prose: Pass
- 1+ em-dashes in authored prose: Critical failure
- Em-dashes inside protected exact material: Preserve and exclude from the authored-prose count

**Note:** Script detection is deterministic. If needed, run `scripts/unslop-engine/emdash_replacer.py` only on a scratch prose-only copy. Preserve protected exact material.

### AI-Tell Detection

**High severity (deduct 1 point each):**
- delve, delving
- leverage (as verb)
- unlock, unlocking
- journey (metaphorical)
- tapestry
- testament
- landscape (metaphorical)
- myriad
- plethora
- nuanced (overused)
- vibrant, breathtaking, stunning, nestled, renowned (V3: promotional language)
- showcasing, fostering, garner, underscore (V3: AI vocabulary)
- interplay, intricacies, enduring (V3: AI vocabulary)

**Medium severity (deduct 0.5 points each):**
- however (sentence start)
- moreover
- furthermore
- in conclusion
- it's worth noting
- it's important to note
- firstly, secondly, thirdly

**Low severity (flag but don't deduct):**
- robust
- scalable
- comprehensive
- streamline
- optimize

**See `references/unslop-engine/negative-style-guide.md` and `references/unslop-engine/ai-pattern-taxonomy.md` for complete inventories.**

### Cliché Detection

**Business domain (deduct 1 point each):**
- game-changer
- paradigm shift
- low-hanging fruit
- move the needle
- circle back
- synergy
- disruptive

**Creative domain (deduct 1 point each):**
- at the end of the day
- when all is said and done
- in today's fast-paced world
- now more than ever
- the [X] of [Y] (formulaic titles)

**Technical domain (deduct 0.5 points each):**
- cutting-edge
- state-of-the-art
- best-in-class
- world-class
- next-generation

**See `references/unslop-engine/cliche-inventory.md` for complete inventory by domain.**

### Hedge Language Detection

**Strong hedges (deduct in conclusions):**
- "It depends"
- "On one hand... on the other"
- "Could be" / "might be"
- "Perhaps" / "maybe"
- "Kind of" / "sort of"

**Acceptable hedges (don't deduct):**
- In exploration/analysis sections
- When uncertainty is genuine and stated
- In research context with confidence levels

**Note:** Hedge language in reasoning = acceptable. Hedge language in conclusions = deduct.

## Validation Workflow

### Pre-Edit Validation

1. **Tier 1 gate check:**
   - Can I state the intent in one sentence?
   - Do I know the audience?
   - Is the action clear?
   - If ANY no → clarify before proceeding

2. **Voice profile extraction:**
   - Create profile per `references/unslop-engine/voice-extraction-guide.md`
   - Confidence level: High/Medium/Low
   - If Low → use light-touch editing

### Post-Edit Validation

1. **Run technical validation:**
   ```bash
   python3 scripts/unslop-engine/quality_validator.py output.txt --verbose
   ```

2. **Score voice consistency:**
   - Compare to profile
   - Check protected phrases
   - Assess tone preservation

3. **Calculate composite:**
   - Apply formula
   - If below 8, identify the lowest component and revise only inside the approved group

4. **Final checks:**
   - [ ] Authored editable-prose em-dash count = 0; protected exact material is unchanged
   - [ ] Fabrication count = 0
   - [ ] Voice profile checklist passes
   - [ ] Portability, mechanism, distance, and reader-backtracking checks pass
   - [ ] Supplied opinions, emotions, and first-person voice remain clear
   - [ ] Protected exact material is unchanged
   - [ ] Contextual quality score is at least 8; target 10

### When Scores Conflict

**Voice high, technical low:**
- Accept. Voice preservation matters more.
- Note: "Technical polish light to preserve your voice."

**Technical high, voice low:**
- Revise. Technical excellence without voice = failure.
- Rollback changes that broke voice.

**Both low:**
- Return to Phase 2 (voice extraction)
- Something fundamental went wrong

## Quick Reference Thresholds

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Authored em dashes in editable prose | 0 | 0 | 0 |
| AI tells | <3 | 0 | 0 |
| Clichés | <3 | <1 | 0 |
| Hedges (conclusions) | <2 | 0 | 0 |
| Voice score | 8 | 10 | 10 |
| Technical score | 8 | 10 | 10 |
| Composite | 8 | 10 | 10 |

## Validation Script Usage

**Basic:**
```bash
python3 scripts/unslop-engine/quality_validator.py content.txt
```

**Create a voice profile, then run the quality scan:**
```bash
python3 scripts/unslop-engine/voice_profiler.py source.txt --output source_voice_profile.json
python3 scripts/unslop-engine/quality_validator.py content.txt
```

**Verbose output:**
```bash
python3 scripts/unslop-engine/quality_validator.py content.txt --verbose
```

**Output format:**
```
QUALITY VALIDATION REPORT
=========================
Technical Score: 8/10
- Em-dashes: 0 ✓
- AI tells: 1 (found: "leverage")
- Clichés: 0 ✓
- Hedges: 0 ✓

Voice Score: [Manual assessment required]

Recommendations:
- Replace "leverage" with "use" or "apply"

Overall: PASS (pending voice assessment)
```

## Remember

**Validation is not bureaucracy.** It's the mechanism that ensures quality means something specific and measurable.

**Objective scores enable objective improvement.** "Make it better" becomes "increase technical score from 6 to 8 by removing these 3 AI tells."

**But voice is subjective.** That's why it gets 40% weight and human judgment. Scripts handle technical. Judgment handles voice.
<!-- harness-quality-gate: literal-list-end -->
