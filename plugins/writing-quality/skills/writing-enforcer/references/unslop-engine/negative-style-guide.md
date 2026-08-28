# Negative Style Guide

Comprehensive inventory of patterns to eliminate. Use `scripts/unslop-engine/quality_validator.py` for automated signals and this inventory for contextual review.

<!-- harness-quality-gate: literal-list-start -->
## Core Principle

Negative style guides are more effective than positive guides because they're concrete and testable. "Don't use delve" is actionable. "Write clearly" is not.

## Category 1: High-Priority AI Tells

**These immediately signal AI authorship. Remove on sight.**

### Overused Verbs
- delve / delving / delved
- leverage (as verb) → use "use," "apply," "employ"
- unlock / unlocking → use "enable," "reveal," "allow"
- harness → use "use," "apply"
- streamline → be specific about what's simplified
- optimize → be specific about what's improved
- elevate → use "improve," "raise," "enhance"

### Overused Nouns
- journey (metaphorical) → use "process," "experience," "path"
- tapestry → almost never appropriate
- landscape (metaphorical) → use "field," "area," "domain"
- realm → use "area," "domain," "field"
- testament → use "evidence," "proof," "demonstration"
- beacon → almost never appropriate
- cornerstone → use "foundation," "basis," "core"

### Overused Adjectives
- myriad → use "many," "numerous," "various"
- plethora → use "many," "abundance," "wealth"
- nuanced → often filler, remove or be specific
- robust → be specific about what's strong
- seamless → be specific about what integrates well
- holistic → often meaningless, remove or explain
- pivotal → use "important," "key," "critical"
- unparalleled → almost always hyperbole, remove

### Overused Phrases
- "It's worth noting that" → just state it
- "It's important to note" → just state it
- "At the end of the day" → remove or rephrase
- "When all is said and done" → remove
- "In today's fast-paced world" → remove (cliché)
- "Now more than ever" → remove or be specific
- "This begs the question" → usually wrong usage anyway
- "The fact of the matter is" → just state the fact
- "In terms of" → often filler, rephrase
- "In order to" → usually just "to" suffices

## Category 2: Structural Anti-Patterns

### Title Patterns to Avoid
- "The [X] of [Y]" formula → varies structure
- Colon titles ("Mastering X: A Guide to Y") → often unnecessary
- "How to [X]: [Subtitle]" → fine occasionally, overused by AI
- Numbered titles ("7 Ways to...") → fine for listicles only

### Transition Anti-Patterns
- Starting sentences with:
  - "However," (occasionally fine, usually overused)
  - "Moreover,"
  - "Furthermore,"
  - "Additionally,"
  - "In conclusion,"
  - "To summarize,"
  - "That being said,"

**Alternatives:**
- Use logical flow that doesn't need transitions
- Use "But" instead of "However"
- Use "And" instead of "Additionally"
- Just start the next point without transition

### Formatting Anti-Patterns
- Excessive bolding (more than 5% of text)
- Bullet points for everything
- Headers every 50 words
- Numbered lists for non-sequential items
- Italics for emphasis (use sparingly)

### Paragraph Anti-Patterns
- Every paragraph same length (~3 sentences)
- Topic sentence + support + conclusion formula (too rigid)
- Paragraph starting with "This" referring to previous paragraph

## Category 3: Hedge Language

**Remove from conclusions. Acceptable in exploration.**

### Strong Hedges (Always Flag)
- "It depends on..."
- "On one hand... on the other hand..."
- "Could potentially..."
- "Might possibly..."
- "It could be argued that..."
- "Some might say..."
- "There are those who believe..."

### Medium Hedges (Flag in Conclusions)
- "Perhaps"
- "Maybe"
- "Possibly"
- "Probably"
- "Likely"
- "Kind of"
- "Sort of"
- "In some ways"

### Weak Hedges (Allow in Moderation)
- "Generally"
- "Usually"
- "Often"
- "Typically"
- "Tends to"

## Category 4: Business Jargon

**Remove unless industry-standard and necessary.**

### High Priority (Almost Never Appropriate)
- synergy / synergize
- paradigm shift
- game-changer
- disruptive / disruption (outside tech context)
- low-hanging fruit
- move the needle
- circle back
- touch base
- deep dive (as noun)
- bandwidth (for human capacity)
- leverage (as verb)
- actionable insights
- value-add
- best-in-class
- world-class
- cutting-edge
- state-of-the-art
- next-generation

### Medium Priority (Use Sparingly)
- stakeholder (sometimes necessary)
- deliverables (sometimes necessary)
- KPIs (use "metrics" when possible)
- scalable (be specific instead)
- ecosystem (often overused)
- alignment (sometimes necessary)
- visibility (be specific)

### Context-Dependent (Judge Case by Case)
- pivot (legitimate in startup context)
- runway (legitimate in finance context)
- deck (legitimate shorthand for presentation)
- ship (legitimate in product context)

## Category 5: Punctuation Anti-Patterns

### Em-Dashes (Critical)
**NEVER USE. Always replace.**

| Original | Replace With |
|----------|--------------|
| "This works [em dash] it saves time" | "This works. It saves time" |
| "This works [em dash] really well" | "This works, really well" |

**Rule:** If what follows could be a sentence → period + capitalize. Otherwise → comma + lowercase.

### Other Punctuation Issues
- Semicolons overuse (AI uses more than humans)
- Ellipsis for drama... (usually remove)
- Exclamation points in professional writing!
- Parentheses overuse (often just aside that should be removed)

## Category 6: Meta-Commentary

**Remove unless serving clear purpose.**

### To Remove
- "Let me explain..."
- "Allow me to..."
- "I'll now discuss..."
- "As mentioned earlier..."
- "As we discussed..."
- "To put it simply..."
- "In other words..."
- "Simply put..."
- "To be clear..."
- "To be fair..."

### Acceptable
- "Here's the key point:" (if genuinely key)
- Questions that advance the argument
- Brief signposting in long documents

## Category 7: Filler Words

**Remove unless serving rhythm purpose.**

### Always Remove
- "Basically"
- "Actually" (usually)
- "Literally" (unless literal)
- "Really" (usually)
- "Very" (usually)
- "Quite"
- "Rather"
- "Somewhat"
- "Just" (usually)
- "Simply" (usually)

### Usually Remove
- "In fact"
- "Indeed"
- "Certainly"
- "Definitely"
- "Absolutely"

## Detection Script Usage

```bash
python3 scripts/unslop-engine/quality_validator.py content.txt --verbose
```

**Output:**
```
AI TELL DETECTION REPORT
========================
High Priority (remove immediately):
- Line 3: "delve into" → suggest: "explore"
- Line 7: "leverage" → suggest: "use"

Medium Priority (review):
- Line 12: "However," (sentence start)

Hedge Language:
- Line 15: "perhaps" (in conclusion)

Total issues: 4
Severity: Medium
```

## Replacement Strategies

### For AI Tells
Don't just swap synonyms. Reconceive the sentence.

**Bad:** "We need to leverage our expertise" → "We need to utilize our expertise"
**Good:** "We need to leverage our expertise" → "Our expertise in X gives us an advantage"

### For Hedge Language
Make a choice and state it. Move nuance to supporting text.

**Bad:** "Perhaps we should consider option A"
**Good:** "Choose option A. Here's why, despite B's appeal..."

### For Jargon
Be specific about what you mean.

**Bad:** "We need to move the needle on engagement"
**Good:** "We need to increase comment rate from 2% to 5%"

### For Filler
Delete and see if meaning changes. Usually doesn't.

**Bad:** "It's basically just a simple process"
**Good:** "It's a straightforward process"

## Domain-Specific Exceptions

### Technical Writing
- "Robust" acceptable when describing systems
- "Optimize" acceptable with specific metrics
- "Scalable" acceptable with clear meaning

### Academic Writing
- "Nuanced" acceptable when genuinely nuanced
- "Framework" acceptable for theoretical models
- Formal transitions more acceptable

### Marketing Writing
- Some enthusiasm acceptable
- Superlatives used strategically
- Still avoid clichés

## Category 8: Copula Avoidance (V3 Addition)

**LLMs substitute elaborate constructions for simple "is"/"are"/"has."**

| AI Pattern | Human Version |
|------------|---------------|
| "serves as" | "is" |
| "stands as" | "is" |
| "functions as" | "is" |
| "boasts" | "has" |
| "features" | "has" or "includes" |
| "offers a" | "has a" |
| "represents a" | "is a" |

**Detection:** Search for "serves as," "stands as," "boasts," "features [a/an/the]."

**Fix:** Replace with "is," "are," or "has." Almost always shorter and clearer.

## Category 9: Superficial -ing Constructions (V3 Addition)

**LLMs tack present participle phrases onto sentences for fake depth.**

**Watch for sentence-ending patterns:**
- ", highlighting [abstract concept]"
- ", showcasing [quality]"
- ", ensuring [positive outcome]"
- ", reflecting [deeper meaning]"
- ", symbolizing [significance]"
- ", contributing to [broader thing]"
- ", fostering [positive quality]"
- ", encompassing [range]"

**Fix:** Delete the -ing clause. If the information matters, make it its own sentence with a concrete subject.

**Before:** "The policy was announced Tuesday, highlighting the administration's commitment to reform."
**After:** "The policy was announced Tuesday."

## Category 10: Significance Inflation (V3 Addition)

**LLMs add empty claims about importance, legacy, and broader meaning.**

**Watch-words:**
- "marking a pivotal moment"
- "setting the stage for"
- "a testament to"
- "reflects broader trends"
- "contributing to the [field]"
- "indelible mark"
- "deeply rooted"
- "enduring legacy"
- "key turning point"

**Fix:** Delete the significance claim entirely. If something is actually important, the facts will show it.

## Category 11: Negative Parallelisms (V3 Addition)

**"Not only...but..." and "It's not just...it's..." are overused 10x by LLMs.**

**Patterns to flag:**
- "Not only...but also..."
- "It's not just about..., it's..."
- "It's not merely..., it's..."
- "More than just a..."

**Fix:** State the point directly. Remove the rhetorical contrast structure.

**Before:** "It's not just a tool, it's a platform for innovation."
**After:** "It's a platform for building custom workflows."

## Category 12: Rule of Three Overuse (V3 Addition)

**LLMs force everything into groups of three: three adjectives, three examples, three benefits.**

**Detection:** Multiple triplet structures in same paragraph. Especially adjective triplets ("seamless, intuitive, and powerful") and noun triplets ("innovation, inspiration, and insights").

**Fix:** Use the number of items that actually exist. Two is fine. Four is fine. Don't force three.

## Category 13: Synonym Cycling (V3 Addition)

**LLM repetition-penalty code causes excessive synonym substitution for the same entity.**

**Before:** "The protagonist faces challenges. The main character overcomes obstacles. The central figure triumphs."
**After:** "The protagonist faces challenges but triumphs."

**Detection:** Same entity referred to by 3+ different names in close proximity.

**Fix:** Pick one term and stick with it. Repetition of the right word is clearer than forced variation.

## Category 14: False Ranges (V3 Addition)

**LLMs use "from X to Y" constructions where X and Y aren't on a meaningful scale.**

**Before:** "From the singularity of the Big Bang to the grand cosmic web, from the birth of stars to the dance of dark matter."
**After:** "The book covers the Big Bang, star formation, and dark matter theories."

**Detection:** "From [X] to [Y]" with poetic/abstract endpoints. Often paired with parallel "from...to..." structures.

## Category 15: Sycophantic Tone (V3 Addition)

**Chatbot praise language that survives into final content.**

**Always remove:**
- "Great question!"
- "You're absolutely right"
- "That's an excellent point"
- "Certainly!" / "Of course!"
- "I hope this helps"
- "Let me know if you'd like me to"

**These should never appear in published text.**

## Category 16: Generic Positive Conclusions (V3 Addition)

**Vague upbeat endings with zero specific information.**

**Watch-words:** "The future looks bright," "exciting times lie ahead," "continue their journey toward excellence," "a major step in the right direction," "poised to"

**Fix:** Replace with a specific fact about what happens next, or delete the conclusion entirely.

## Category 17: Curly Quotation Marks (V3 Addition)

**ChatGPT-specific artifact. Uses Unicode curly quotes instead of straight quotes.**

**Detection:** Characters U+201C, U+201D (double), U+2018, U+2019 (single). Script detects automatically.

**Fix:** Replace with straight quotes: " and '

## Category 18: Context-Sensitive Abstraction and Specificity

Treat abstract metaphor nouns as warnings, not automatic failures. Replace decorative terms such as substrate, wedge, vector, locus, vantage, nexus, bedrock, scaffolding, modality, gold-plating, ratchet, endgame, north star, and flywheel with the real component or mechanism. Keep legitimate technical vocabulary.

Use three manual tests:

- **Portability:** Could the sentence appear unchanged in another project's copy?
- **Mechanism:** Does the sentence name what happens, who acts, or what the reader should do?
- **Distance:** Does it name the actual reader, team, system, or event instead of vague people or abstractions?

If a sentence fails a test and the source supplies no specific replacement, cut or qualify it. Do not invent details.

## Pre-Output Checklist

Before shipping any content:

- [ ] Zero authored em dashes in editable prose; protected exact material is unchanged
- [ ] Zero high-priority AI tells
- [ ] <3 medium-priority issues
- [ ] Zero hedge language in conclusions
- [ ] Zero business jargon (unless necessary)
- [ ] Zero filler words (unless rhythm)
- [ ] Zero copula avoidance patterns (serves as, stands as, boasts)
- [ ] Zero trailing -ing constructions adding fake depth
- [ ] Zero significance inflation claims
- [ ] Zero sycophantic/chatbot language artifacts
- [ ] Zero curly quotation marks
- [ ] Generic claims pass portability, mechanism, and distance checks
- [ ] Supplied opinions, emotions, and first-person voice remain clear
- [ ] No personality or experience invented

If any fail, revise before shipping.

## Remember

**The goal is not robotic perfection.** It's removing patterns that scream "AI wrote this."

**Some patterns are fine in moderation.** The issue is overuse, not existence.

**Context matters.** "Leverage" is fine in finance. "Delve" is rarely fine anywhere.

**When in doubt, be specific.** Most AI tells are vague abstractions. Specificity is the cure.

**Clean is not enough.** Sterile writing that passes every check but erases the writer's personality is itself a failure. See Phase 3 (Voice Recovery) in SKILL.md. Recover only traits present in the source; never invent opinions or experience.
<!-- harness-quality-gate: literal-list-end -->
