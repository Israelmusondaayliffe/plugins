# Extended AI Pattern Catalog

23 additional patterns not covered in the core 24-pattern taxonomy. These supplement `references/unslop-engine/ai-pattern-taxonomy.md`. Load both when doing a full Phase 2 scan.

Sources: avoid-ai-writing (conorbronsdon, MIT) and no-ai-slop (Peter Yang, MIT, reviewed at commit `61c21c351da4dcb40946a11fead978f2078a2c65`). Synthesized and paraphrased.

<!-- harness-quality-gate: literal-list-start -->
---

## Pattern 25: Novelty Inflation

**Problem:** AI treats existing concepts as if the speaker invented or discovered them. "He introduced a term I hadn't heard before: context poisoning." In reality, most concepts in a conversation already exist somewhere.

**Two problems:** Factually risky if the concept has a Wikipedia page. Flatters the subject promotionally.

**Fix:** Describe what the person *did with* the concept, not that they discovered it. "Michel walked through how context poisoning works in practice" instead of "Michel introduced a term nobody's naming."

**Related patterns to flag:** "the failure mode nobody's naming," "a problem nobody talks about," "the insight everyone's missing," "what nobody tells you about." These are engagement-bait framings claiming scarcity of knowledge where none exists.

**Severity:** P1

---

## Pattern 26: Emotional Flatline

**Problem:** AI claims emotions structurally without conveying them through writing. "What surprised me most," "I was fascinated to discover," "What struck me was."

Two problems: It's tell-don't-show. If something is genuinely surprising, the reader should feel that from the content. Also, these are massively overused as list transitions. They're filler wearing emotion as a costume.

**Fix:** If you claim an emotion, the writing around it should earn it. Otherwise cut the claim and present the thing directly.

**Related:** "hit differently" / "hits different": trendy colloquialism used as shortcut to sound relatable without earning the emotional beat.

**Severity:** P1

---

## Pattern 27: False Concession Structure

**Problem:** "While X is impressive, Y remains a challenge." AI uses this to sound balanced without actually weighing anything. Both halves are vague.

**Fix:** Either make the concession specific (name what's impressive, name the actual challenge) or pick a side and argue it.

**Severity:** P1

---

## Pattern 28: Rhetorical Question Openers (as Stalls)

**Problem:** "But what does this mean for developers?" / "So why should you care?" / "What's next?" AI uses rhetorical questions to stall before the actual point.

**Fix:** If you know the answer, just say it. Rhetorical questions are earned by strong setup, not dropped as section transitions.

**Severity:** P1

---

## Pattern 29: Parenthetical Hedging

**Problem:** "(and, increasingly, Z)" / "(or, more precisely, Y)" / "(and perhaps more importantly, W)": AI inserts parenthetical asides to sound nuanced without committing.

**Fix:** If the aside matters, give it its own sentence. If it doesn't, cut it.

**Severity:** P2

---

## Pattern 30: Numbered List Inflation

**Problem:** "Three key takeaways" / "Five things to know" / "Here are the top seven": AI defaults to numbered lists because they're structurally safe. Often padding to hit a number.

**Fix:** Only use numbered lists when the content genuinely has that many discrete, parallel items. If you're padding to hit a number, the list shouldn't exist.

**Severity:** P2

---

## Pattern 31: Reasoning Chain Artifacts

**Problem:** "Let me think step by step," "Breaking this down," "To approach this systematically," "Step 1:," "Here's my thought process," "First, let's consider": artifacts of chain-of-thought reasoning leaking into published prose.

**Fix:** The reader doesn't need to see the scaffolding. State the conclusion, then the evidence.

Also watch for numbered reasoning steps that read like an internal monologue rather than an argument meant for an audience.

**Severity:** P1

---

## Pattern 32: Acknowledgment Loops

**Problem:** "You're asking about," "The question of whether," "To answer your question," "That's a great question. The...": AI restates the prompt before answering.

**Fix:** In writing, this is pure filler. The reader knows what they asked. Just answer. Also: opening a section by summarizing what the previous section said. If the structure is clear, the reader doesn't need a recap.

**Severity:** P0 (in published content)

---

## Pattern 33: Confidence Calibration Phrases

**Problem:** "It's worth noting that," "Interestingly," "Surprisingly," "Importantly," "Significantly," "Notably," "Certainly," "Undoubtedly": AI uses these to signal how the reader should feel about a fact instead of letting the fact speak for itself.

**Fix:** One "notably" in a 2,000-word piece is fine. Three in 500 words is emphasis stacking. Flag by density.

Also: "Here's what's interesting," "Here's the interesting part": reader-steering cue that pre-interprets importance. If you need a lead-in, make it specific: "The revenue number matters because..." not "Here's the interesting part."

**Severity:** P2 (by density)

---

## Pattern 34: Excessive Structure

**Problem:** Too many headers in short text (more than 3 headings under 300 words). Too many list items (8+ bullets under 200 words). Formulaic section headers: "Overview," "Key Points," "Summary," "Conclusion," "Introduction."

**Fix:** Merge sections or use prose transitions. Lists that should be paragraphs. Headers that tell the reader what follows, not placeholders.

**Severity:** P1

---

## Pattern 35: Rhythm and Uniformity (Structure as Primary Detection Signal)

**Problem:** AI text is metronomic. Uniform sentence length (most 15-25 words), uniform paragraph length (most 3-5 sentences same size), symmetrical phrasing. Structure is the #1 detection signal because it is harder to mask than vocabulary.

**Fix:**
- Mix short punchy sentences (3-8 words) with longer flowing ones (20+). Fragments work.
- Some paragraphs should be one sentence. Some longer.
- Human writers repeat the clearest word; they don't cycle synonyms or avoid repetition mechanically.
- If the piece sounds like it could be read by TTS without sounding weird, it's too uniform.
- Preserve the writer's supplied opinions and reactions. Do not add opinions to make neutral source material seem human.
- Don't over-polish: aggressively editing out every irregularity can push human writing toward AI statistical profiles. Natural disfluency and idiosyncratic word choices keep text human. Don't sand away all personality.

**Severity:** P1 (structure is harder to fix than vocabulary but more important)

---

## Pattern 36: Vague Endorsement

**Problem:** "Worth reading," "worth paying attention to," "worth a look," "worth your time": these substitute a generic thumbs-up for a specific reason.

**Fix:** Say *why* something matters instead. What specifically makes it worth the reader's attention?

**Severity:** P2

---

## Pattern 37: Throat-Clearing Openers

**Problem:** "Here's the thing," "Let me be clear," "I'll be honest," and "The uncomfortable truth is" delay a point while performing candor or authority.

**Fix:** Start with the claim. Keep an opener only when it is a recognizable voice marker and contributes real context rather than ceremony.

**Severity:** P1

---

## Pattern 38: Colon Reveals

**Problem:** A setup phrase followed by a lowercase dramatic reveal makes an ordinary fact sound staged: "The best part: it learns."

**Fix:** Write a plain sentence. Keep colons for lists, labels, quotations, and cases where the grammar needs one. Sentence case follows a colon unless a proper noun, title, quotation, or code requires otherwise.

**Severity:** P1

---

## Pattern 39: Dramatic Fragmentation

**Problem:** Stacked fragments such as "Not a tool. Not a workflow. A revolution." or "That's it. That's the whole thing." manufacture intensity through rhythm.

**Fix:** State the point in a complete sentence. Preserve a fragment only when it is characteristic of the writer and earns its emphasis.

**Severity:** P1

---

## Pattern 40: Self-Answered Rhetorical Setups

**Problem:** "What if I told you...", "Think about it:", "Plot twist:", and "The answer? Better evals." stage a reveal instead of making the claim.

**Fix:** Remove the setup and state the answer directly. This extends Pattern 28 beyond question openers used as transitions.

**Severity:** P1

---

## Pattern 41: Fake-Profound Kickers

**Problem:** A final aphorism, metaphor, or mic-drop line tries to make the piece sound deeper after the argument has ended.

**Fix:** Delete the kicker. End on the strongest concrete fact, takeaway, or next action already supported by the draft. Do not replace it with a prettier metaphor.

**Severity:** P1

---

## Pattern 42: Summary-Recap Endings

**Problem:** "In conclusion," "Ultimately," "Overall," or a final paragraph that repeats the piece makes the reader sit through the same point twice.

**Fix:** End on the last concrete point, decision, or action. Keep a summary only when the format or audience genuinely needs one.

**Severity:** P1

---

## Pattern 43: Decorative Abstract Metaphors

**Problem:** Technical-sounding metaphor nouns replace the actual mechanism. Common examples include substrate, wedge, vector, locus, vantage, nexus, bedrock, scaffolding, modality, gold-plating, ratchet, endgame, north star, and flywheel.

**Fix:** Name the concrete component, action, constraint, or mechanism. Keep a term when it is legitimate domain vocabulary.

**Severity:** P2 and context-sensitive

---

## Pattern 44: Portable Generic Claims

**Problem:** A sentence could appear unchanged in another project's copy because it names a feeling instead of a fact, mechanism, number, instruction, or decision.

**Fix:** Ask what the reader should know or do. Add supported specifics or cut the sentence.

**Severity:** P1

---

## Pattern 45: False Agency and Reader Distance

**Problem:** An abstraction appears to decide, believe, discover, or act, or the writing talks about vague people instead of the actual reader, team, or process.

**Fix:** Name the actor or mechanism when known. Keep passive voice when the actor genuinely does not matter.

**Severity:** P1

---

## Pattern 46: Weak-Verb Adverb Scaffolding

**Problem:** An empty adverb props up a weak verb or an unsupported intensity claim. Examples include "significantly improves" without a measured change and "runs quickly" without a number or stronger verb.

**Fix:** Use the supported number or a more exact verb. Keep an adverb when it carries real emphasis, uncertainty, contrast, or voice.

**Severity:** P2 and context-sensitive

---

## Pattern 47: Reader-Backtracking Sentences

**Problem:** A dense sentence makes the reader restart because it carries several ideas, nested clauses, or unclear references.

**Fix:** Split or shorten it without flattening a clear, characteristic cadence.

**Severity:** P2 and context-sensitive

---

## Quick-Reference: What These Patterns Have in Common

All 23 are structural, contextual, or meta-patterns rather than simple word bans. They survive a vocabulary-only edit. The only way to catch them is to read for meaning: does this sentence actually say something, or is it performing the act of saying something?

That question is the best single detector for AI writing at all levels.
<!-- harness-quality-gate: literal-list-end -->
