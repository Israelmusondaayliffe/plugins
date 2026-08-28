# Bundled Unslop Workflow

# Bundled runtime copy

This workflow is self-contained inside Writing Enforcer. All resource paths below resolve inside this skill. Harness Engineering is not required.


Remove AI patterns, preserve voice, recover the writer's existing character, and enforce plain language. This is the canonical merged editor for Unslop, Humanizer, Stop Slop, and No AI Slop behavior.

---

## Plain-language law (Rule Zero)

**Simple words win. Always.**

If you can say it plainly, say it plainly. Prefer ordinary, precise verbs to inflated ones. "Start" beats "commence." "Important" beats "pivotal." "Show" beats "showcase." Not trying to sound smart. Trying to sound human.

This rule overrides every other stylistic judgment. When a word exists on the replacement table AND a simpler word conveys the same meaning, the simpler word wins without exception. If the complex word is the only precise option, keep it and note why.

Apply this rule to everything you write, not just to the content under review.

---

## Core Philosophy

Three things make writing sound like AI:
1. **AI patterns present.** The 47 documented patterns that signal generic LLM prose.
2. **Human personality absent or erased.** Sterile, voiceless writing that passes every technical check but has no pulse. Clean-but-soulless is itself an AI tell.
3. **Overly complex vocabulary.** Big words where small words work. Sounds like the writer is performing intelligence, not communicating.

This skill addresses all three. Pattern removal is the floor. Preserving the writer's real texture is the ceiling. Plain language is the law throughout.

Never manufacture personality. Do not add opinions, anecdotes, emotions, profanity, first-person claims, identity claims, examples, numbers, or certainty that the writer did not supply. When the source or an explicit user instruction supplies a viewpoint, feeling, first-person stance, or recognizable rhythm, preserve it and make it clearer when the draft has buried it. When the draft has little personal texture, make a restrained clarity edit instead of performing a synthetic human voice.

---

## Modes

**REWRITE**: Use the full four-phase pipeline only when the user asks for or approves prose changes. Return the edited text and a short What changed section. Keep diagnostic scores internal unless the user asks for them.

**DETECT**: This is the required audit mode before approval. Flag patterns only. Do not rewrite. Return categorized issues by severity (P0/P1/P2).

Trigger DETECT when the user says: "detect," "flag only," "audit only," "just flag," "scan," "what AI patterns are in this," or similar.

---

## Context Profiles

Auto-detect from content cues. User can override by naming a profile.

| Profile | Auto-detect signals | Notes |
|---|---|---|
| `linkedin` | Under 300 words + hashtags/mentions | Short-form social. Fragments OK, 1-2 emoji at end of line OK |
| `blog` | Default | All rules at full strength |
| `technical-blog` | Code blocks, API references, architecture | Technical terms get a pass; tone rules still apply |
| `investor-email` | Salutation + fundraising language | Extra strict on promotional language; zero significance inflation |
| `docs` | Step-by-step instructions, README structure | Clarity over personality; lists OK |
| `casual` | Slack, DMs, quick notes | P0 only; don't over-police |

Load `references/unslop-engine/context-profiles.md` for the full tolerance matrix per profile.

---

## Four-Phase Workflow

### Phase 1: Intent and Voice

**Before changing anything:**

1. Determine stakes (high/medium/low) and content purpose:
   - Who reads this? What should they do after?
   - High-stakes = full pipeline. Low-stakes = light touch.

2. Extract voice markers from the input:
   - Characteristic phrases and terms (keep these)
   - Tone indicators (formal/casual, punchy/flowing)
   - Task-supplied voice samples or explicit user preferences

   Do not infer voice from general memory, identity history, or unrelated prior work. A reusable profile is valid only when the user supplies or explicitly selects its source material for this task.

3. State assumed intent if not explicit. Flag if intent is unclear before proceeding.

4. Identify the core point and 3-5 voice signals to preserve. Leave strong human sentences alone. If the core point is unclear, ask instead of guessing.

Run `scripts/unslop-engine/voice_profiler.py` on input for automated voice extraction.
Load `references/unslop-engine/voice-extraction-guide.md` for detailed methodology.

**Output of Phase 1:** Intent statement, stakes level, voice profile with preservation list.

---

### Phase 2: Pattern Scan

Load `references/unslop-engine/ai-pattern-taxonomy.md` (24 original patterns) and `references/unslop-engine/extended-patterns.md` (23 additional patterns) for the full 47-pattern catalog.

Run `scripts/unslop-engine/quality_validator.py` on the input for automated detection.

**Scan priority order:**

<!-- harness-quality-gate: literal-list-start -->
**P0: Fix immediately (credibility killers):**
- Chatbot artifacts: "Certainly!," "I hope this helps!," "Great question!"
- Cutoff disclaimers: "As of my last update," "based on available information"
- Vague attributions: "Experts believe," "Industry reports suggest" (without names)
- Significance inflation: "marking a pivotal moment," "a watershed moment"

**P1: Fix before publishing (obvious AI smell):**
- Tier 1 word violations (see `references/unslop-engine/word-replacement-table.md`): delve, leverage, tapestry, realm, paradigm, robust, seamless, utilize, embark, testament to, pivotal, underscores, cutting-edge, nestled, vibrant, showcase, game-changer, watershed, intricate, holistic, actionable, synergy, serves as, boasts, features (as verb), empower
- Copula avoidance: "serves as" → "is," "boasts" → "has," "features" → "has/includes"
- -ing analyses: trailing clauses that add zero information ("symbolizing...," "reflecting...," "showcasing...")
- Promotional language: "vibrant," "renowned," "breathtaking," "nestled in the heart of"
- Template phrases: "a [adj] step toward [adj] infrastructure," "Whether you're X or Y"
- Formulaic openings: "In the rapidly evolving world of..."
- "Let's" transition openers: "Let's explore," "Let's dive in"
- Bold overuse
- Authored em dashes (handled only in editable prose; protected exact material stays unchanged)

**P2: Stylistic polish (fix when time allows):**
- Generic conclusions: "The future looks bright," "Only time will tell"
- Tier 2 word clusters (flag when 2+ in same paragraph): harness, navigate, foster, elevate, streamline, empower, bolster, resonate, facilitate, ecosystem, burgeoning, cornerstone, transformative
- Compulsive rule of three
- Uniform paragraph length
- Transition phrases: "Moreover," "Furthermore," "In today's X"
- Title case headings
- Synonym cycling
- Rhetorical question openers used as stalls
- Throat-clearing and faux-insight openers
- Colon reveals used for fake drama
- Dramatic fragmentation and self-answered question setups
- Fake-profound kicker lines
- Summary-recap endings
<!-- harness-quality-gate: literal-list-end -->

**Rewrite-vs-patch threshold:** If text has 5+ P1 hits across 3+ categories, the structure itself is AI-generated. Advise full rewrite from the core point outward rather than patching.

---

### Phase 3: Rewrite and Voice Recovery

**These happen together.** Removing patterns without protecting voice produces sterile text. Adding synthetic personality produces decorated AI slop.

#### 3.1 Rewrite principles

- Make the minimum effective edit. Fix the actual slop, errors, repetition, and confusion. Do not rewrite strong sentences for consistency or make every paragraph equally tidy.
- Preserve the writer's structure, detours, uncertainty, rough edges, and level of polish unless they block the piece's job.
- Lead with the point only when setup adds nothing. Keep a personal aside, story, or admission when it supplies context, tension, or character.
- Protect specific facts. Do not smooth names, dates, numbers, mechanisms, or useful detail into generic claims of importance.
- Prefer active voice and direct verbs when they are clearer. Keep passive voice when the actor is unknown, irrelevant, or deliberately backgrounded.
- Replace every word on the Tier 1 list with its plain alternative. No exceptions unless the complex word is the only precise option.
- "Serves as" → "is." Always. Not "functions as." Just "is."
- Trailing -ing clauses: delete if the information is redundant. If it matters, make it its own sentence.
- Significance claims: delete entirely. If something is significant, the facts show it.
- Generic conclusions: replace with a specific thought or cut.
- Vague attributions: name the source or remove the claim.
- Don't just swap synonyms. Reconceive the sentence. Ask: what is this actually trying to say?

Load `references/unslop-engine/word-replacement-table.md` for the full 3-tier replacement table.

#### 3.2 Voice recovery

After pattern removal, check for the "clean but lifeless" failure. If 3+ of these symptoms appeared because of the edit, restore voice from the source:

- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person when it would fit
- No humor, no edge, no personality
- Reads like a press release or Wikipedia article

**Six voice-recovery techniques:**

1. **Preserve or sharpen supplied opinions.** Keep the writer's reactions, conviction, and uncertainty. If editing has buried a supplied position, make it clear without adding your own.
2. **Restore the source rhythm.** Keep its mix of short, long, fragmentary, or flowing sentences when clear.
3. **Preserve supplied complexity.** Do not flatten mixed feelings or qualified claims into false certainty.
4. **Keep first person when the writer used it.** Do not create first-person experience for them.
5. **Let useful mess remain.** Keep tangents and asides that carry voice or context.
6. **Protect or clarify concrete feeling language already present.** Do not invent emotional reactions to make the prose seem human.

**Soul calibration by content type:**

| Type | Soul intensity | Notes |
|---|---|---|
| Blog/essay/social | High | Preserve supplied personality, rhythm, and opinions |
| Business/professional | Medium | Conviction yes, informality varies |
| Technical docs | Low | Clarity over personality |
| Email/casual | Medium | Natural, not performative |
| Academic | Low | Precision first |

#### 3.3 Divergence enforcement

If rewrite still contains hedge language in conclusions or recommendations:
- Load `references/unslop-engine/divergence-patterns.md`
- Nuance belongs in reasoning. Conclusions must be decisive.
- "Perhaps we should consider" → "Do X. Here's why."

#### 3.4 Em-dash enforcement

Remove em dashes from assistant-authored editable prose. Never run the replacer across all output, a source document, or a file tree. If needed, run `scripts/unslop-engine/emdash_replacer.py` with a separate scratch prose input and scratch output, review the diff, and apply only authorized edits. Preserve code, commands, quotations, citations, and other protected exact material even when it contains an em dash.

| Context | Replace with | Capitalization |
|---|---|---|
| New sentence follows | Period | Capitalize next word |
| Continuation/addition | Comma | Keep lowercase |

#### 3.5 Always-on Unslop pass

Load `references/unslop-engine/unslop-policy.md` before delivery. Apply its quick pass to assistant-authored human-facing prose. Preserve protected exact material unchanged. In DETECT mode, the report receives the pass but quoted source evidence does not.

---

### Phase 4: Validation

#### 4.1 Second-pass audit

Re-read the rewritten text. Flag any patterns that survived the first pass: recycled transitions, lingering significance inflation, copula swaps that snuck through, Tier 1 words that were missed. Fix them in-line.

#### 4.2 Manual checklist

- [ ] Voice profile preserved (characteristic phrases intact, tone matches)
- [ ] Existing voice remains present without synthetic personality
- [ ] Supplied opinions, emotions, first-person voice, and useful roughness remain clear
- [ ] Minimum-effective-edit check passed
- [ ] No fabricated details or personality (everything traces to original input or explicit direction; violation = automatic failure)
- [ ] Protected exact material remains byte-for-byte unchanged
- [ ] Always-on Unslop pass completed
- [ ] Zero authored em dashes; protected exact material is unchanged
- [ ] Zero P0 patterns
- [ ] Zero Tier 1 word violations
- [ ] Simple words used throughout (Rule Zero honored)
- [ ] Contextual quality score is at least 8/10; target 10/10

#### 4.3 Score and deliver

For high-stakes content, run self-critique before final delivery:
Load `references/unslop-engine/critique-frameworks.md`. Red-team with the audience lens. Repair only weaknesses inside the user's rewrite authority and factual boundary. Report any weakness that needs broader authority instead of expanding the task.

**Composite quality score:**
- Voice consistency: 35%
- Technical quality (pattern removal): 35%
- Intent alignment: 20%
- Preserved voice texture: 10%

Threshold: 8/10 minimum. Target 10/10. Below 8 means revise inside the approved group or stop for a new approval.

Keep this score and checklist internal by default. A visible score often adds more process than the reader needs. Show it only when the user asks for validation, scoring, or audit evidence.

---

## Output Format

### REWRITE mode (approved repair only)

```
[Edited text here]

What changed:
- [Major edits, briefly]
```

Validation mode, only when requested:
```
Score: [X/10] | [Pass / Needs work]
[Failed checks and evidence]
```

### DETECT mode

```
P0: Fix immediately:
- "[quoted text]" → [pattern name]

P1: Fix before publishing:
- "[quoted text]" → [pattern name]

P2: Polish when time allows:
- "[quoted text]" → [pattern name]

ASSESSMENT:
[Which flags are clear problems vs. judgment calls]
[Rewrite-vs-patch recommendation if 5+ P1 hits]
```

---

## Failure Modes

**FM-1: Voice destroyed during rewrite.** Roll back aggressive rewrites. Restore characteristic phrases. Accept lower technical score if needed. Voice preservation wins over pattern removal.

**FM-2: Clean but lifeless.** Re-apply Phase 3.2 using only voice signals present in the source. Restore rhythm, first-person, opinions, uncertainty, or asides that the edit removed. If the source has no strong voice signal, keep the edit restrained.

**FM-3: Fabrication introduced.** Compare output to input line by line. Remove any added claims or numbers not in original. Incomplete > incorrect.

**FM-4: Over-correction.** Text sounds forced-casual or trying-too-hard-to-be-human. Roll back changes that were not required for clarity or pattern removal. Natural > decorated.

<!-- harness-quality-gate: literal-list-start -->
**FM-5: Domain vocabulary flagged.** Check voice profile's domain list. "Robust" is fine in systems engineering. "Robust" is an AI tell in marketing copy. Context determines the call.
<!-- harness-quality-gate: literal-list-end -->

**FM-6: Voice stripped during polish.** Compare pre- and post-polish versions. Restore source-backed personality at the cost of one lower-priority technical flag. Recognizable voice beats sterile perfection.

Load `references/unslop-engine/failure-recovery.md` for extended recovery procedures.

---

## Pre-Output Checklist

Before EVERY output:
- [ ] Rule Zero applied (simpler words used throughout)
- [ ] Intent extracted and stated
- [ ] Voice profile created/loaded
- [ ] Pattern scan complete (scripts/unslop-engine/quality_validator.py)
- [ ] Minimum-effective-edit check passed
- [ ] Existing voice and useful roughness preserved
- [ ] Supplied opinions, emotions, and first-person voice preserved or clarified
- [ ] No opinions, emotions, identity claims, examples, or first-person experience invented
- [ ] Code, commands, logs, quotations, citations, structured data, and exact prompt blocks unchanged
- [ ] Always-on Unslop pass complete
- [ ] Authored em dashes removed from editable prose; protected exact material preserved
- [ ] Fabrication check passed
- [ ] Voice consistency verified
- [ ] Second-pass audit done
- [ ] Contextual quality score is at least 8/10; target 10/10

If ANY check fails: fix or flag explicitly. Do not ship broken output.

---

## Resources

### References (load as needed)

- `references/unslop-engine/word-replacement-table.md`: 3-tier word/phrase replacement table (109+ entries). Load for Phase 3.1.
- `references/unslop-engine/ai-pattern-taxonomy.md`: Original 24-pattern catalog with examples. Load for Phase 2.
- `references/unslop-engine/extended-patterns.md`: 23 additional patterns from Unslop, Stop Slop, avoid-ai-writing, and no-ai-slop. Load for Phase 2.
- `references/unslop-engine/unslop-policy.md`: Mandatory final pass, protected-material boundary, and source-backed voice rules. Load before every delivery.
- `references/unslop-engine/source-provenance.md`: Source ownership, credits, and retirement record for the merged capability. Load for maintenance or redistribution.
- `references/unslop-engine/context-profiles.md`: Tolerance matrix per profile. Load when profile is ambiguous.
- `references/unslop-engine/voice-extraction-guide.md`: Voice marker detection and profile creation.
- `references/unslop-engine/negative-style-guide.md`: Broader banned patterns, hedge language, business jargon, filler words.
- `references/unslop-engine/divergence-patterns.md`: Anti-equivocation strategies for conclusions.
- `references/unslop-engine/cliche-inventory.md`: Domain-specific overused phrases.
- `references/unslop-engine/critique-frameworks.md`: Audience-specific review lenses for high-stakes self-critique.
- `references/unslop-engine/failure-recovery.md`: Extended recovery procedures for 9 failure modes.
- `references/unslop-engine/validation-criteria.md`: Detailed scoring rubrics.

### Scripts (deterministic operations)

- `scripts/unslop-engine/emdash_replacer.py`: Replaces dash punctuation. Use only on a scratch prose-only copy, then review and apply the approved edit manually.
- `scripts/unslop-engine/quality_validator.py`: Detects surface and structural pattern categories. Provides an objective internal score.
- `scripts/unslop-engine/protected_material_validator.py`: Compares source and edited Markdown to verify fenced blocks, block quotations, inline code, and citations stayed unchanged.
- `scripts/unslop-engine/voice_profiler.py`: Extracts voice markers from sample text.

---

**The rule that ties it all together:** Plain language is human language. If you can say it simply, say it simply. Remove what signals machine authorship. Preserve what signals this writer. Validate that nothing new was invented. That's the job.
