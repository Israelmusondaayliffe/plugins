# Failure Recovery Procedures

Extended documentation for handling failure modes. Ensures graceful degradation and clear recovery paths.

## Failure Mode Taxonomy

### Critical Failures (Halt Workflow)

| Failure | Signal | Impact | Recovery |
|---------|--------|--------|----------|
| Intent unknown | Cannot state purpose | Wrong improvements applied | Phase 1 discovery |
| Voice profile empty | No markers detected | Generic output overwrites user | Light touch only |
| Fabrication detected | Claims without source | User credibility damaged | Remove or flag |
| Authored em dashes remain in editable prose | Authored count > 0 | User's critical rule violated | Repair the approved prose-only span |

### Quality Failures (Revise and Retry)

| Failure | Signal | Impact | Recovery |
|---------|--------|--------|----------|
| Voice score < 8 | Profile comparison fails | Sounds unlike user | Rollback, lighter touch |
| Technical score < 8 | Multiple AI tells remain | Sounds like AI | Re-apply techniques |
| Composite < 8 | Overall quality insufficient | Not ready to ship | Identify lowest dimension |

### Soft Failures (Flag and Proceed)

| Failure | Signal | Impact | Recovery |
|---------|--------|--------|----------|
| Voice profile low confidence | Limited sample | May not match user | Flag uncertainty |
| Edge case punctuation | Ambiguous em-dash context | Minor formatting | Default to period |
| Domain vocabulary conflict | Technical term triggers AI-tell | False positive | Preserve term |

## Detailed Recovery Procedures

### FM-1: Intent Unknown

**Symptoms:**
- Cannot answer "What decision does this enable?"
- Cannot identify audience
- "So what?" unclear

**Root Causes:**
- Content lacks context
- User provided text without explanation
- Multiple possible purposes

**Recovery Steps:**

1. **Attempt inference (low confidence):**
   - Look for audience signals (technical language = expert audience)
   - Look for action signals (CTA = persuasive intent)
   - Look for format signals (bullets = reference doc)

2. **Ask clarifying questions (preferred):**
   ```
   Before improving, I need to understand:
   - Who will read this?
   - What should they do after reading?
   - What's the one thing you want them to remember?
   ```

3. **If user wants quick output:**
   - State assumed intent explicitly
   - Apply medium-intensity techniques
   - Flag: "I've assumed this is [X] for [Y]. Let me know if I should adjust."

4. **Fallback:**
   - Apply minimal changes
   - Focus only on obvious AI tells
   - Don't restructure or reframe

**Prevention:** Build intent extraction into conversation flow. Ask early.

### FM-2: Voice Profile Empty

**Symptoms:**
- No characteristic phrases detected
- Tone unclear
- Style markers absent
- Confidence level: Low

**Root Causes:**
- Content too short (< 100 words)
- Content already generic
- Content heavily edited by others

**Recovery Steps:**

1. **Check current task sources:**
   - Look for writing samples the user supplied or explicitly selected
   - Look for explicit voice instructions in the current request
   - Apply only markers that are traceable to those sources

2. **Request sample:**
   ```
   I can't detect a strong voice pattern in this content. 
   Could you share something you've written that represents your style?
   Or should I apply minimal polish and preserve this voice as-is?
   ```

3. **Apply generic professional profile:**
   - Neutral, competent tone
   - Complete sentences
   - Clear structure
   - Light touch editing only

4. **Fallback:**
   - Remove only obvious AI tells
   - Don't change sentence structure
   - Don't adjust tone
   - Flag: "I've made minimal changes to preserve your style."

**Prevention:** Ask for a representative sample when voice matters. Reuse a prior profile only when the user explicitly selects it and its source remains available.

### FM-3: Fabrication Detected

**Symptoms:**
- Claim in output not traceable to user input
- Numbers, metrics, or outcomes appear that weren't provided
- Tools or methods mentioned that user didn't specify

**Root Causes:**
- LLM hallucinated plausible details
- Improvement technique "strengthened" claims
- Pattern-matching added typical examples

**Recovery Steps:**

1. **Identify fabrication:**
   - List all claims in output
   - Trace each to user input
   - Flag any without source

2. **Remove or mark:**
   - Delete fabricated claims entirely, OR
   - Mark as assumption: "[Assumption: X. Please verify.]"

3. **If critical to content:**
   - Ask user: "I don't have data for [X]. Can you provide it?"
   - Offer placeholder: "[INSERT: specific metric]"

4. **Re-validate:**
   - Run full fabrication check again
   - Zero tolerance policy

**Fallback:** Remove rather than guess. Incomplete > incorrect.

**Prevention:** Fabrication check is Tier 1 gate. Never skip.

### FM-4: Authored em dashes remain

**Symptoms:**
- `scripts/unslop-engine/quality_validator.py` reports authored dash punctuation in editable prose
- Manual review finds an authored em dash outside protected exact material

**Root Causes:**
- Script not run
- Edge case not handled
- New content added after script

**Recovery Steps:**

1. **Use a scratch prose-only copy:**
   ```bash
   python3 scripts/unslop-engine/emdash_replacer.py scratch-input.txt scratch-output.txt
   ```
   Review the diff and apply only the approved prose edit. Never run the replacer across a raw harness or plugin file.

2. **Manual verification:**
   - Search for "—" character
   - Search for "--" double hyphen
   - Search for "–" en-dash

3. **If script fails:**
   - Manual replacement
   - Rule: Could be sentence? → period + capitalize. Otherwise → comma.

4. **Final check:**
   - Authored editable-prose count must equal zero
   - Protected exact material must remain byte-for-byte unchanged

**Fallback:** Period + capitalize is the safer default when ambiguous.

**Prevention:** Run script as LAST step before output.

### FM-5: Voice Score Below Threshold

**Symptoms:**
- Characteristic phrases missing
- Tone shifted significantly
- Output "sounds generic"
- Voice score < 8/10

**Root Causes:**
- Techniques too aggressive
- Voice profile not used
- Technical fixes broke voice

**Recovery Steps:**

1. **Compare to profile:**
   - Which phrases were lost?
   - Where did tone shift?
   - What structure changed?

2. **Rollback specific changes:**
   - Restore characteristic phrases
   - Revert tone-shifting edits
   - Keep technical fixes that don't affect voice

3. **Re-apply with voice priority:**
   - Load voice profile explicitly
   - Mark protected phrases
   - Apply techniques only outside protected zones

4. **Accept lower technical score if needed:**
   - Voice > Technical when in conflict
   - Note tradeoff in output

**Fallback:** "I've preserved your voice at the cost of some technical polish."

**Prevention:** Extract voice profile before applying any techniques.

### FM-6: Technical Score Below Threshold

**Symptoms:**
- AI tells remaining in output
- Clichés not eliminated
- Hedge language in conclusions
- Technical score < 8/10

**Root Causes:**
- Techniques applied too lightly
- Edge cases missed
- Script not run

**Recovery Steps:**

1. **Identify failing components:**
   - Run `scripts/unslop-engine/quality_validator.py content.txt --verbose`
   - List specific issues

2. **Target specific issues:**
   - AI tells: Check against negative style guide
   - Clichés: Check against cliché inventory
   - Hedges: Check conclusion sections specifically

3. **Re-apply targeted technique:**
   - Don't re-run entire pipeline
   - Focus on specific failing area
   - Verify voice not broken

4. **Re-score:**
   - Run validator again
   - Iterate until ≥7

**Fallback:** "Technical polish limited to preserve your voice. Here are remaining items you may want to address: [list]"

**Prevention:** Run scripts before manual review.

### FM-7: Voice vs. Technical Conflict

**Symptoms:**
- Fixing AI tells breaks user's characteristic phrase
- Technical improvement makes content stiff
- User's natural hedging flagged as problem

**Root Causes:**
- User's voice includes patterns that read as AI tells
- Domain vocabulary overlaps with cliché list
- User naturally hedges (curious voice type)

**Recovery Steps:**

1. **Identify conflict:**
   - What voice marker triggers what technical flag?
   - Is this a genuine user pattern or coincidence?

2. **Prioritize voice:**
   - Voice wins in conflict
   - Preserve the user's pattern
   - Accept lower technical score

3. **Note the exception:**
   - Flag in output: "Preserved '[phrase]' as it matches your voice"
   - Add to user's protected phrases list

4. **Adjust detection:**
   - For this user, whitelist the pattern
   - Don't flag in future

**Fallback:** When in doubt, preserve what the user wrote.

**Prevention:** Build exception list per user. Learn over time.

### FM-8: Ambiguous Punctuation

**Symptoms:**
- Em-dash replacement unclear
- Not obvious if period or comma appropriate
- Reading aloud doesn't clarify

**Root Causes:**
- Grammatically ambiguous construction
- Could be either continuation or new thought
- User's original intent unclear

**Recovery Steps:**

1. **Apply reading test:**
   - Read aloud with pause
   - Could standalone? → period
   - Clearly continuation? → comma

2. **Check semantic content:**
   - New subject introduced? → period
   - Same subject, more detail? → comma

3. **Default rule:**
   - When genuinely ambiguous → period + capitalize
   - Rationale: Overcapitalization is less wrong than undercapitalization

4. **Flag if critical:**
   - For important documents, note: "Changed '—' to '.'. Verify this reads correctly."

**Fallback:** Period is the safer default.

**Prevention:** This is an expected edge case. Default to period.

### FM-9: Voice Stripped During Polish

**Symptoms:**
- Phase 3 preserved source-backed personality and rhythm
- Phase 4 technical polish removed it
- Output passes technical checks but reads flat
- "Clean but lifeless" despite high technical score

**Root Causes:**
- Aggressive cliche scrubbing removed personality-carrying phrases
- Divergence enforcement flattened mixed feelings into decisive statements
- AI-tell removal stripped conversational elements
- Voice consistency check did not account for the writer's useful roughness

**Recovery Steps:**

1. **Compare Phase 3 output to Phase 4 output:**
   - Where did personality disappear?
   - Which specific technical fix caused it?

2. **Identify source-backed voice elements:**
   - First-person perspective ("I keep thinking about...")
   - Rhythm variation (short/long sentence mix)
   - Specific feelings ("unsettling" vs. "concerning")
   - Tangents or asides that add humanity

3. **Restore source-backed voice, accept a lower technical score:**
   - Put back personality-carrying phrases
   - Accept medium-priority AI tells if they carry voice
   - Recognizable voice > sterile perfection

4. **Re-validate with the voice-texture gate:**
   - Does it still have a pulse?
   - Would a human recognize this as human-written?

**Fallback:** "I restored a source-backed voice marker at the cost of one remaining medium-priority pattern."

**Prevention:** Run the voice-texture preservation check immediately after technical polish. Never add opinions, feelings, anecdotes, or first-person experience that the source did not supply.

## Escalation Paths

### When to Ask User

- Intent completely unclear after inference attempt
- Voice profile empty and no memory data
- Fabrication would require significant content changes
- Voice vs. technical conflict on central element

### When to Flag and Ship

- Minor punctuation ambiguity
- Low-confidence voice profile (user notified)
- Single remaining medium-priority AI tell
- Technical score 6.5-6.9 (close to threshold)

### When to Refuse Output

- Cannot determine intent AND user won't clarify
- Fabrication cannot be removed without gutting content
- Voice score < 5 (complete voice loss)
- User explicitly requesting fabrication

## Recovery Metrics

Track these for quality improvement:

- Failure frequency by type
- Recovery success rate
- Time to recovery
- User satisfaction post-recovery

## Remember

**Graceful degradation > perfect execution.** Better to flag uncertainty than ship broken output.

**Recovery is expected.** These procedures exist because failures happen. Don't treat failure as unusual.

**User communication matters.** Clear explanation of what went wrong and what was done builds trust.

**Learn from patterns.** Repeated failures in the same area signal need for process improvement.
