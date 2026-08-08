---
name: writing-enforcer
description: "Unified writing enforcer that removes AI patterns, preserves voice, injects soul, and ensures plain human-sounding prose. Combines humanizer, output-quality-enforcer, and anti-AI style detection into one workflow. Use when asked to humanize this, remove AI feel, make this sound like me, clean this up, too robotic, too generic, sound more human, or to improve any text that reads as AI-generated or over-polished. Two modes: DETECT (flag patterns only) and REWRITE (full pipeline, default). Applies the plain-language rule: simpler words always beat complex words. Enforces voice, soul, intent, and the 36-pattern AI-tell taxonomy. Runs deterministic scripts for em-dash removal and quality scoring."
license: MIT
metadata:
  author: Community Maintainers
  version: 1.0.0
  combines: humanizer, output-quality-enforcer-v3, avoid-ai-writing
---

# Writing Enforcer

Remove AI patterns, preserve voice, inject soul, enforce plain language. The single skill that replaces humanizer and output-quality-enforcer-v3.

---

## Plain-Language Rule (Rule Zero)

**Simple words win. Always.**

If you can say it plainly, say it plainly. "Use" beats "leverage." "Start" beats "commence." "Important" beats "pivotal." "Show" beats "showcase." Not trying to sound smart. Trying to sound human.

This rule overrides every other stylistic judgment. When a word exists on the replacement table AND a simpler word conveys the same meaning, the simpler word wins without exception. If the complex word is the only precise option, keep it and note why.

Apply this rule to everything you write, not just to the content under review.

---

## Core Philosophy

Three things make writing sound like AI:
1. **AI patterns present.** The 36 documented patterns that statistically signal LLM authorship.
2. **Human personality absent.** Sterile, voiceless writing that passes every technical check but has no pulse. Clean-but-soulless is itself an AI tell.
3. **Overly complex vocabulary.** Big words where small words work. Sounds like the writer is performing intelligence, not communicating.

This skill addresses all three. Pattern removal is the floor. Soul injection is the ceiling. Plain language is the law throughout.

---

## Modes

**REWRITE** (default): Full 4-phase pipeline. Returns clean text, diff summary, and quality score.

**DETECT**: Flag patterns only. No rewriting. Returns categorized issues by severity (P0/P1/P2). Use when the user wants to see problems before deciding what to fix, or when auditing content they don't want altered.

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

Load `references/context-profiles.md` for the full tolerance matrix per profile.

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
   - Known user preferences from memory

3. State assumed intent if not explicit. Flag if intent is unclear before proceeding.

Run `scripts/voice_profiler.py` on input for automated voice extraction.
Load `references/voice-extraction-guide.md` for detailed methodology.

**Output of Phase 1:** Intent statement, stakes level, voice profile with preservation list.

---

### Phase 2: Pattern Scan

Load `references/ai-pattern-taxonomy.md` (24 original patterns) and `references/extended-patterns.md` (12 additional patterns from avoid-ai-writing) for the full 36-pattern catalog.

Run `scripts/quality_validator.py` on the input for automated detection.

**Scan priority order:**

**P0 — Fix immediately (credibility killers):**
- Chatbot artifacts: "Certainly!," "I hope this helps!," "Great question!"
- Cutoff disclaimers: "As of my last update," "based on available information"
- Vague attributions: "Experts believe," "Industry reports suggest" (without names)
- Significance inflation: "marking a pivotal moment," "a watershed moment"

**P1 — Fix before publishing (obvious AI smell):**
- Tier 1 word violations (see `references/word-replacement-table.md`): delve, leverage, tapestry, realm, paradigm, robust, seamless, utilize, embark, testament to, pivotal, underscores, cutting-edge, nestled, vibrant, showcase, game-changer, watershed, intricate, holistic, actionable, synergy, serves as, boasts, features (as verb), empower
- Copula avoidance: "serves as" → "is," "boasts" → "has," "features" → "has/includes"
- -ing analyses: trailing clauses that add zero information ("symbolizing...," "reflecting...," "showcasing...")
- Promotional language: "vibrant," "renowned," "breathtaking," "nestled in the heart of"
- Template phrases: "a [adj] step toward [adj] infrastructure," "Whether you're X or Y"
- Formulaic openings: "In the rapidly evolving world of..."
- "Let's" transition openers: "Let's explore," "Let's dive in"
- Bold overuse
- Em dashes (handled by script; listed here for awareness)

**P2 — Stylistic polish (fix when time allows):**
- Generic conclusions: "The future looks bright," "Only time will tell"
- Tier 2 word clusters (flag when 2+ in same paragraph): harness, navigate, foster, elevate, streamline, empower, bolster, resonate, facilitate, ecosystem, burgeoning, cornerstone, transformative
- Compulsive rule of three
- Uniform paragraph length
- Transition phrases: "Moreover," "Furthermore," "In today's X"
- Title case headings
- Synonym cycling
- Rhetorical question openers used as stalls

**Rewrite-vs-patch threshold:** If text has 5+ P1 hits across 3+ categories, the structure itself is AI-generated. Advise full rewrite from the core point outward rather than patching.

---

### Phase 3: Rewrite and Soul Injection

**These happen together.** Removing patterns without adding soul produces sterile text. Adding soul without removing patterns produces decorated AI slop.

#### 3.1 Rewrite principles

- Replace every word on the Tier 1 list with its plain alternative. No exceptions unless the complex word is the only precise option.
- "Serves as" → "is." Always. Not "functions as." Just "is."
- Trailing -ing clauses: delete if the information is redundant. If it matters, make it its own sentence.
- Significance claims: delete entirely. If something is significant, the facts show it.
- Generic conclusions: replace with a specific thought or cut.
- Vague attributions: name the source or remove the claim.
- Don't just swap synonyms. Reconceive the sentence. Ask: what is this actually trying to say?

Load `references/word-replacement-table.md` for the full 3-tier replacement table.

#### 3.2 Soul injection

After pattern removal, check for the "clean but lifeless" failure. If 3+ of these symptoms are present, inject soul:

- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person when it would fit
- No humor, no edge, no personality
- Reads like a press release or Wikipedia article

**Six soul techniques:**

1. **Have opinions.** Don't just report facts. React to them.
2. **Vary rhythm.** Short punchy sentences. Then longer ones that take their time. Mix it up.
3. **Acknowledge complexity.** "This is impressive but also unsettling" beats "This is impressive."
4. **Use "I" when it fits.** First person isn't unprofessional. It's honest.
5. **Let some mess in.** Perfect structure feels algorithmic. Tangents and asides are human.
6. **Be specific about feelings.** Not "this is concerning" but "there's something unsettling about agents running at 3am while nobody's watching."

**Soul calibration by content type:**

| Type | Soul intensity | Notes |
|---|---|---|
| Blog/essay/social | High | Full personality, rhythm play, opinions |
| Business/professional | Medium | Conviction yes, informality varies |
| Technical docs | Low | Clarity over personality |
| Email/casual | Medium | Natural, not performative |
| Academic | Low | Precision first |

#### 3.3 Divergence enforcement

If rewrite still contains hedge language in conclusions or recommendations:
- Load `references/divergence-patterns.md`
- Nuance belongs in reasoning. Conclusions must be decisive.
- "Perhaps we should consider" → "Do X. Here's why."

#### 3.4 Em-dash enforcement

Run `scripts/emdash_replacer.py` on ALL output. Zero em-dashes. No exceptions.

| Context | Replace with | Capitalization |
|---|---|---|
| New sentence follows | Period | Capitalize next word |
| Continuation/addition | Comma | Keep lowercase |

---

### Phase 4: Validation

#### 4.1 Second-pass audit

Re-read the rewritten text. Flag any patterns that survived the first pass: recycled transitions, lingering significance inflation, copula swaps that snuck through, Tier 1 words that were missed. Fix them in-line.

#### 4.2 Manual checklist

- [ ] Voice profile preserved (characteristic phrases intact, tone matches)
- [ ] Soul present (appropriate personality for content type, not sterile)
- [ ] No fabricated details (everything traces to original input — violation = automatic failure)
- [ ] Zero em-dashes
- [ ] Zero P0 patterns
- [ ] Zero Tier 1 word violations
- [ ] Simple words used throughout (Rule Zero honored)
- [ ] Quality score ≥ 7/10

#### 4.3 Score and deliver

For high-stakes content, run self-critique before final delivery:
Load `references/critique-frameworks.md`. Red-team with audience lens. List top 3 weaknesses. Rewrite addressing each.

**Composite quality score:**
- Voice consistency: 35%
- Technical quality (pattern removal): 35%
- Intent alignment: 20%
- Soul presence: 10%

Threshold: 7/10 minimum. Below 7 = revise, not ship with caveats.

---

## Output Format

### REWRITE mode (default)

```
[Cleaned text here]

---

SUMMARY:
Intent: [What this achieves for whom]
Voice: [Preserved / adjusted; key markers]
Soul: [Level applied]
Changes: [Major edits, briefly]
Score: [X/10] — [Pass / Needs work]
[If <8: "Want me to push this further?"]
```

Quick delivery for low-stakes:
```
[Cleaned text]
---
Score: [X/10] | [Top 2 changes made]
```

### DETECT mode

```
P0 — Fix immediately:
- "[quoted text]" → [pattern name]

P1 — Fix before publishing:
- "[quoted text]" → [pattern name]

P2 — Polish when time allows:
- "[quoted text]" → [pattern name]

ASSESSMENT:
[Which flags are clear problems vs. judgment calls]
[Rewrite-vs-patch recommendation if 5+ P1 hits]
```

---

## Failure Modes

**FM-1: Voice destroyed during rewrite.** Roll back aggressive rewrites. Restore characteristic phrases. Accept lower technical score if needed. Voice preservation wins over pattern removal.

**FM-2: Clean but lifeless.** Re-apply Phase 3.2 soul injection with higher intensity. Add opinions, rhythm variation, first-person.

**FM-3: Fabrication introduced.** Compare output to input line by line. Remove any added claims or numbers not in original. Incomplete > incorrect.

**FM-4: Over-correction.** Text sounds forced-casual or trying-too-hard-to-be-human. Dial back soul injection. Natural > decorated.

**FM-5: Domain vocabulary flagged.** Check voice profile's domain list. "Robust" is fine in systems engineering. "Robust" is an AI tell in marketing copy. Context determines the call.

**FM-6: Soul stripped during polish.** Compare pre- and post-polish versions. Restore personality at cost of one lower-priority technical flag. Soul > sterile perfection.

Load `references/failure-recovery.md` for extended recovery procedures.

---

## Pre-Output Checklist

Before EVERY output:
- [ ] Rule Zero applied (simpler words used throughout)
- [ ] Intent extracted and stated
- [ ] Voice profile created/loaded
- [ ] Pattern scan complete (scripts/quality_validator.py)
- [ ] Soul check passed (not sterile)
- [ ] Em-dashes replaced (scripts/emdash_replacer.py)
- [ ] Fabrication check passed
- [ ] Voice consistency verified
- [ ] Second-pass audit done
- [ ] Quality score ≥ 7/10

If ANY check fails: fix or flag explicitly. Do not ship broken output.

---

## Resources

### References (load as needed)

- `references/word-replacement-table.md` — 3-tier word/phrase replacement table (109+ entries). Load for Phase 3.1.
- `references/ai-pattern-taxonomy.md` — Original 24-pattern catalog with examples. Load for Phase 2.
- `references/extended-patterns.md` — 12 additional patterns from avoid-ai-writing (novelty inflation, emotional flatline, false concession, rhetorical openers, etc.). Load for Phase 2.
- `references/context-profiles.md` — Tolerance matrix per profile. Load when profile is ambiguous.
- `references/voice-extraction-guide.md` — Voice marker detection and profile creation.
- `references/negative-style-guide.md` — Broader banned patterns, hedge language, business jargon, filler words.
- `references/divergence-patterns.md` — Anti-equivocation strategies for conclusions.
- `references/cliche-inventory.md` — Domain-specific overused phrases.
- `references/critique-frameworks.md` — Audience-specific review lenses for high-stakes self-critique.
- `references/failure-recovery.md` — Extended recovery procedures for 9 failure modes.
- `references/validation-criteria.md` — Detailed scoring rubrics.

### Scripts (deterministic operations)

- `scripts/emdash_replacer.py` — Replaces all em-dashes, en-dashes, double-hyphens. Run on every output.
- `scripts/quality_validator.py` — Detects 12 pattern categories. Provides objective score.
- `scripts/voice_profiler.py` — Extracts voice markers from sample text.

---

**The rule that ties it all together:** Plain language is human language. If you can say it simply, say it simply. Remove what signals machine authorship. Inject what signals a real person with opinions. Validate it holds. That's the job.
