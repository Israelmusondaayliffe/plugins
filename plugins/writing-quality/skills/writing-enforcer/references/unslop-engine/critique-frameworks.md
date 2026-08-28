# Critique Frameworks: Audience-Specific Review Lenses

This reference provides structured approaches for red-teaming output through different audience perspectives.

## Core Concept

Self-critique requires adopting an external perspective. The lens chosen determines what weaknesses get surfaced. Match critique lens to intended audience.

## Framework Selection

Choose critique lens based on who will consume/evaluate the output:

- **Undergraduate lens** → Educational content, tutorials, onboarding docs
- **Executive lens** → Strategy memos, board decks, business proposals  
- **Technical expert lens** → Architecture docs, research papers, API design
- **Skeptical peer lens** → Arguments, pitches, claims requiring proof
- **General public lens** → Marketing content, blog posts, social media
- **Internal team lens** → Project plans, process docs, retrospectives

## Undergraduate Lens

**Use for:** Educational content, explanations, how-to guides, onboarding materials

### Critique Questions

**Tone & Approach:**
- Is it condescending? ("This is simple," "just do X," "obviously")
- Does it assume too much prior knowledge?
- Is jargon explained or does it pile up?
- Are examples relevant to someone learning?

**Clarity:**
- Could a complete beginner follow this?
- Are steps missing that seem "obvious" to expert?
- Is there a clear progression from simple to complex?
- Are there sudden jumps in difficulty?

**Engagement:**
- Is it boring? (Too much theory before payoff)
- Does it respect learner's intelligence?
- Are there hands-on elements?
- Is the "why" clear before the "how"?

**Common Weaknesses:**
- Explaining things the learner doesn't need yet
- Not explaining things the expert takes for granted
- Writing for the professor, not the student
- No clear takeaway or action items

### Red Team Process

1. **Find assumptions:** What prior knowledge is assumed?
2. **Identify jargon:** Which terms aren't defined?
3. **Check scaffolding:** Does each concept build on previous?
4. **Test clarity:** Could you follow this without asking questions?
5. **Rate engagement:** Would a learner stay focused?

### Rewrite Priorities

- Add concrete examples before abstract concepts
- Define technical terms on first use
- Break complex ideas into smaller pieces
- Add "why this matters" context
- Remove condescending language

## Executive Lens

**Use for:** Strategy docs, business proposals, board presentations, leadership updates

### Critique Questions

**Respect for Time:**
- Is the bottom line up front?
- Can busy executive grasp it in 30 seconds?
- Is there unnecessary detail that should be appendix?
- Does it answer "so what?" immediately?

**Decision Focus:**
- What decision is this asking for?
- Are recommendations clear and specific?
- Is the ask explicit?
- Are next steps concrete?

**Business Impact:**
- Is there quantified impact? (Revenue, cost, time, risk)
- Are tradeoffs explicit?
- Is ROI clear?
- Is timeline realistic?

**Strategic Alignment:**
- How does this connect to company priorities?
- What's the competitive angle?
- Why now? (Timing rationale)
- What happens if we don't do this?

**Common Weaknesses:**
- Burying the lede
- Too much process, not enough outcome
- Vague recommendations ("we should consider")
- Missing the "why this matters to business" connection

### Red Team Process

1. **Time test:** Can key message be extracted in 30 sec?
2. **Decision clarity:** What exactly is being asked?
3. **Impact quantification:** Are claims backed by numbers?
4. **Risk assessment:** What's not being said?
5. **Action clarity:** What happens next?

### Rewrite Priorities

- Move conclusion to top (BLUF: Bottom Line Up Front)
- Cut background that doesn't support decision
- Quantify everything possible
- Make recommendation explicit and bold
- Add executive summary if >2 pages

## Technical Expert Lens

**Use for:** Architecture docs, technical proposals, research, API design

### Critique Questions

**Technical Rigor:**
- Are there logical gaps or hand-waves?
- Is the technical depth appropriate?
- Are edge cases considered?
- Would this actually work in production?

**Precision:**
- Is terminology used correctly?
- Are specifications precise enough to implement?
- Are performance claims backed by benchmarks?
- Are failure modes addressed?

**Completeness:**
- What questions would expert immediately ask?
- Are tradeoffs analyzed honestly?
- Is the solution actually solving the root problem?
- What about backwards compatibility / migration?

**Credibility:**
- Does author understand the domain?
- Are there obvious mistakes an expert would catch?
- Are claims too bold for evidence provided?
- Is complexity justified or is there simpler approach?

**Common Weaknesses:**
- Marketing language in technical context
- Oversimplification of hard problems
- Ignoring known challenges in the space
- Solutions that reveal shallow understanding
- Buzzword compliance over engineering sense

### Red Team Process

1. **Sanity check:** Would this actually work?
2. **Edge case analysis:** What breaks this?
3. **Implementation reality:** How hard is this really?
4. **Alternative scan:** Is there simpler/better approach?
5. **Domain knowledge test:** Does author get the fundamentals?

### Rewrite Priorities

- Remove marketing language
- Add technical specificity
- Address known failure modes
- Include benchmarks/measurements
- Acknowledge tradeoffs honestly

## Skeptical Peer Lens

**Use for:** Arguments, persuasive writing, pitches, claims requiring proof

### Critique Questions

**Logical Soundness:**
- Where are the weak points in reasoning?
- Are there hidden assumptions?
- Does evidence actually support conclusions?
- Are there alternative explanations?

**Evidence Quality:**
- Is data cherry-picked?
- Are sources credible?
- Are claims falsifiable?
- Is correlation being treated as causation?

**Counterarguments:**
- What would critic say?
- Are obvious objections addressed?
- Is steel-manning of alternatives present?
- Why should skeptic be convinced?

**Rhetorical Moves:**
- Is there circular reasoning?
- Are there appeals to emotion over logic?
- Is argument relying on authority vs. evidence?
- Are there false dichotomies?

**Common Weaknesses:**
- Ignoring strongest counterarguments
- Straw-manning opposition
- Overconfidence in weak evidence
- Logical fallacies (slippery slope, ad hominem, etc.)
- Confusing consensus with truth

### Red Team Process

1. **Devil's advocate:** Make strongest case against position
2. **Evidence review:** Is proof actually proving the claim?
3. **Assumption hunt:** What's being taken for granted?
4. **Alternative hypothesis:** What else could explain this?
5. **Burden of proof:** Is claim extraordinary enough to require extraordinary evidence?

### Rewrite Priorities

- Address strongest counterarguments directly
- Strengthen weakest evidence or remove claim
- Make assumptions explicit
- Acknowledge limits of conclusion
- Add qualifiers where confidence is low

## General Public Lens

**Use for:** Blog posts, marketing content, public communications

### Critique Questions

**Accessibility:**
- Is this understandable without domain expertise?
- Are analogies helpful or confusing?
- Is length appropriate for casual reading?
- Does it lose momentum midway?

**Engagement:**
- Does opening hook attention?
- Is there a clear narrative?
- Are examples relatable?
- Is tone appropriate for broad audience?

**Clarity:**
- Is main point obvious?
- Are there too many concepts for one piece?
- Is structure easy to follow?
- Can reader act on this?

**Authenticity:**
- Does it sound like real person wrote it?
- Is it trying too hard to sound smart?
- Are there generic platitudes?
- Does personality come through?

**Common Weaknesses:**
- Inside baseball / unexplained jargon
- Assuming everyone cares about this topic
- Generic advice that applies to nothing specifically
- No clear takeaway or "so what"
- Corporate-speak that distances reader

### Red Team Process

1. **Jargon check:** What would confuse non-expert?
2. **Interest test:** Why should casual reader care?
3. **Skim test:** Does structure guide eye to key points?
4. **Voice test:** Does this sound human?
5. **Value test:** What does reader gain?

### Rewrite Priorities

- Simplify language without dumbing down ideas
- Add relatable examples
- Cut insider references
- Strengthen opening hook
- Make takeaway explicit

## Internal Team Lens

**Use for:** Project docs, process guides, team communications

### Critique Questions

**Practicality:**
- Can teammates actually use this?
- Is it too idealistic vs. real constraints?
- Does it acknowledge messy reality?
- Are edge cases covered?

**Clarity of Expectations:**
- Who does what?
- When are things due?
- What defines success?
- How do we handle exceptions?

**Team Context:**
- Does it account for team's skill levels?
- Is it consistent with existing processes?
- Does it respect team's time/bandwidth?
- Is it maintainable long-term?

**Communication:**
- Is tone appropriate for team culture?
- Is it clear why we're doing this?
- Are concerns/objections addressed?
- Is feedback invited?

**Common Weaknesses:**
- Top-down tone that ignores team input
- Processes that look good on paper but won't work in practice
- Unclear ownership
- No acknowledgment of added workload
- Missing the "why" that motivates adoption

### Red Team Process

1. **Reality check:** Will this survive contact with actual work?
2. **Ownership clarity:** Who's responsible for what?
3. **Adoption friction:** What makes this hard to follow?
4. **Team buy-in:** Why would team embrace vs. resist this?
5. **Maintenance burden:** Who keeps this up to date?

### Rewrite Priorities

- Add specific ownership assignments
- Acknowledge constraints and tradeoffs
- Explain rationale, not just rules
- Include feedback mechanism
- Make it easy to follow

## Multi-Lens Critique

For important work, apply multiple lenses sequentially:

### Sequence for Strategy Doc

1. **Executive lens** (Is the ask clear?)
2. **Skeptical peer lens** (Is reasoning sound?)
3. **Technical expert lens** (if applicable - Is it feasible?)

### Sequence for Educational Content

1. **Undergraduate lens** (Is it learnable?)
2. **General public lens** (Is it engaging?)
3. **Technical expert lens** (Is it accurate?)

### Sequence for Product Pitch

1. **Skeptical peer lens** (Are claims defensible?)
2. **Executive lens** (Is business case clear?)
3. **General public lens** (Is story compelling?)

## Applying Critique Results

### Step 1: Prioritize Weaknesses

Not all critique findings are equal. Prioritize:

1. **Critical flaws** that undermine core message
2. **Credibility issues** that lose audience trust
3. **Clarity problems** that confuse main point
4. **Polish issues** that distract but don't derail

### Step 2: Rewrite with Focus

Address top 5 issues, not everything:
- Critical flaws → Must fix
- Credibility issues → Must fix
- Clarity problems → Fix if major
- Polish issues → Fix if easy

### Step 3: Validate Improvements

After rewrite, quick re-check:
- Did fixes address the weaknesses?
- Did fixes introduce new problems?
- Is output now audience-appropriate?
- What's the remaining risk?

## Common Critique Mistakes

**Mistake: Wrong lens for audience**
- Using technical expert lens on general public content
- Using undergraduate lens on expert documentation
- Mixing lenses (executive expectations on creative writing)

**Mistake: Critique paralysis**
- Finding so many issues nothing survives
- Losing sight of what's already working
- Perfectionism that prevents shipping

**Mistake: Surface-level critique**
- Focusing on grammar/typos vs. substance
- Missing logical gaps while fixing word choice
- Polishing turds instead of rebuilding foundations

**Mistake: Ignoring domain norms**
- Applying rules that don't match domain expectations
- Judging by wrong standards (academic rigor for blog post)
- Missing what makes domain-specific work good

## Output Format

After critique, present:

```
## Top 5 Weaknesses (from [Lens Name] perspective)

1. **[Weakness category]:** [Specific issue]
   - **Impact:** [Why this matters]
   - **Fix:** [How to address]

2. [...]

## Recommended Revisions

[Explain which changes have highest ROI]

## Remaining Risks

[What's still not perfect and why that's ok/not ok]
```
