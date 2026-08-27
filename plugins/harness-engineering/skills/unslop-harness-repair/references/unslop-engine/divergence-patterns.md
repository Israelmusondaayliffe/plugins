# Divergence Patterns: Anti-Equivocation Strategies

This reference provides systematic approaches for forcing decisive thinking instead of hedging across different domains.

## Core Problem

LLMs default to presenting multiple options without choosing because:
1. Risk aversion (user might disagree with the choice)
2. Training on balanced, "fair" presentation of alternatives
3. Inability to assess context-specific tradeoffs
4. Optimization for consensus rather than conviction

**Result:** Output that hedges, equivocates, and avoids taking a stand.

## Detection Patterns

### Hedge Language Red Flags

**Explicit hedging:**
- "It depends on..."
- "Both X and Y are valid..."
- "Consider these options..."
- "You could do either..."
- "There are pros and cons to each..."

**Implicit hedging:**
- "If you value X, choose A; if you value Y, choose B"
- Listing options without recommendation
- Equal weight given to contradictory approaches
- "On one hand... on the other hand..." structures
- Conditional recommendations based on unstated assumptions

**Structural hedging:**
- Three-column comparison tables with no winner
- "Option A vs. Option B" sections with no conclusion
- Bullet lists of alternatives with equal billing
- Sections that end with "choose based on your needs"

## Divergence Enforcement Framework

### Step 1: Identify Decision Points

Scan output for moments requiring choice:
- Strategic direction (approach A vs. B)
- Prioritization (feature X vs. Y first)
- Positioning (messaging angle 1 vs. 2)
- Resource allocation (invest here vs. there)
- Tactical execution (method A vs. B)

### Step 2: Steel-Man All Options

Before choosing, genuinely argue each option's strongest case:
- What's the best-case scenario for this choice?
- What evidence supports it?
- Who would advocate for this and why?
- What unstated assumptions make this optimal?

**Critical:** Don't straw-man the alternatives. Make each case as strong as possible.

### Step 3: Force the Choice

Pick ONE option and argue vigorously for it. Framework:

**Structure:**
1. **State the choice clearly:** "Do X."
2. **Lead with the strongest argument:** Why X is superior
3. **Acknowledge Y's appeal:** "While Y offers [benefit]..."
4. **Explain why that doesn't change the recommendation:** "...X is still better because..."
5. **Add supporting arguments:** Secondary reasons for X
6. **Close with confidence:** Reinforce the choice

**Example transformation:**
- **Before:** "You could focus on enterprise customers for higher revenue, or consumers for faster growth. It depends on your goals."
- **After:** "Focus on enterprise first. Despite consumer's appeal for faster user acquisition, enterprise provides the cash runway you need to survive long enough to scale. Consumer can wait until you have sustainable economics."

### Step 4: Preserve Nuance in Reasoning, Not in Conclusion

**Acceptable nuance:**
- Explaining tradeoffs within the chosen path
- Identifying risks and mitigation strategies
- Noting conditions under which recommendation changes
- Acknowledging what you're sacrificing

**Unacceptable equivocation:**
- Undermining the recommendation with "but you could also..."
- Ending with "ultimately it's up to you" (no kidding)
- Reopening alternatives after arguing for one
- Hedging with "this is just one perspective"

## Domain-Specific Divergence Strategies

### Strategy Documents

**Typical hedge:**
"Your go-to-market could be bottom-up (faster initial traction) or top-down (higher deal values). Consider your resources and market dynamics."

**Divergence enforcement:**
"Go bottom-up. Top-down enterprise sales will burn through runway before you have product-market fit. Start with individual users who can adopt without procurement cycles, build proof points, then expand up-market once you've proven value. You'll sacrifice early revenue but gain speed-to-learning, which matters more at this stage."

**Key elements:**
- Clear choice: "Go bottom-up"
- Acknowledges alternative appeal: "Top-down has higher deal values"
- Explains why it doesn't matter: "Will burn runway before PMF"
- States decisive reasoning: "Speed-to-learning matters more"

### Creative/Design Decisions

**Typical hedge:**
"The design could use minimalist style (clean, modern) or maximalist (bold, memorable). Depends on brand positioning."

**Divergence enforcement:**
"Go maximalist. Your market is saturated with sterile SaaS minimalism. You need to be remembered, not just seen. Maximalism risks alienating some users but creates passionate advocates—exactly what you need as an unknown brand. Safe design won't cut through."

**Key elements:**
- Definitive choice: "Go maximalist"
- Names the tradeoff: "Risks alienating some"
- Argues why it's worth it: "Need passionate advocates"
- Explains context: "Market saturated with minimalism"

### Technical Architecture

**Typical hedge:**
"You could use microservices (scalable, flexible) or monolith (simpler, faster to start). Evaluate based on team size and growth plans."

**Divergence enforcement:**
"Build a monolith. Microservices are premature optimization for your 3-person team. You'll waste months on inter-service communication and distributed tracing instead of shipping features. Start simple, stay focused, split later if you actually scale—most startups never need to. Architectural flexibility isn't your constraint; shipping speed is."

**Key elements:**
- Clear stance: "Build a monolith"
- Acknowledges microservices appeal: "Scalable, flexible"
- Context-specific reasoning: "3-person team"
- Priority clarity: "Shipping speed is the constraint"

### Writing/Communication Style

**Typical hedge:**
"The tone could be formal (professional) or casual (approachable). Consider your audience."

**Divergence enforcement:**
"Write casually. Your audience is developers who hate corporate BS. Formal tone makes you sound like every other vendor manual. Use contractions, second person, and occasional humor. You'll alienate suits who want 'enterprise-grade documentation,' but they're not your buyers—your buyers are tired developers who want clarity, not ceremony."

**Key elements:**
- Direct choice: "Write casually"
- Target audience clarity: "Developers who hate corporate BS"
- Tradeoff acknowledged: "Alienate suits"
- Reason it doesn't matter: "They're not your buyers"

## Advanced Techniques

### Multi-Factor Decisions

When choice depends on multiple variables:

**Don't:**
"If A and B, choose X. If A and not-B, choose Y. If not-A and B, choose Z..."

**Do:**
1. State the dominant factor: "The key variable is A, not B or C"
2. Make recommendation based on that: "So do X"
3. Explain why other factors are secondary: "B and C matter less because..."

### Conditional Recommendations

When recommendation truly varies by context:

**Don't:**
Leave user to decide which context applies

**Do:**
1. Define the contexts precisely
2. Tell user which context they're probably in
3. Make recommendation for that context
4. Provide decision rule for switching contexts

**Example:**
"You're likely in 'low-cash, high-uncertainty' mode since you're pre-revenue. In that mode, do X. If you raise $5M+ or hit $100K MRR, switch to Y—but not before."

### Steel-Man Then Destroy

For contentious choices:

**Pattern:**
1. Present the alternative position at its strongest
2. "Here's the best case for Y: [compelling argument]"
3. Acknowledge it has merit: "This isn't wrong..."
4. Introduce the decisive factor: "...but it misses X"
5. Explain why X dominates: "And X matters more because..."
6. Conclude with choice: "So do Z, not Y"

**Example:**
"The case for focusing on SEO is compelling: it's free, compounds over time, and builds a moat. This isn't wrong—SEO is valuable. But it takes 6-12 months to pay off, and you have 6 months of runway. You need revenue now, not next year. Do direct sales first. SEO can wait until you're not in survival mode."

## When Divergence Enforcement Doesn't Apply

**Legitimate cases for presenting options:**
- User explicitly asks for options to evaluate themselves
- Decision requires information only user has
- Truly equal alternatives where any choice is fine
- Exploratory/brainstorming mode before converging

**How to handle these:**
- Make it clear this is pre-decision exploration
- Set expectation you'll help decide after user provides context
- If user pushes for recommendation anyway, force a choice

## Common Mistakes

**Mistake 1: Fake decisiveness**
- Saying "do X" but then walking it back with hedges
- Making choice but not arguing for it
- Choosing without explaining why alternatives fail

**Mistake 2: Dictatorial tone**
- Being decisive doesn't mean being inflexible
- Acknowledge reasonable disagreement exists
- Explain your reasoning, don't just assert authority

**Mistake 3: Oversimplification**
- Ignoring real tradeoffs to force a clean story
- Pretending choice is obvious when it's genuinely hard
- Missing important context that changes recommendation

**Mistake 4: Premature convergence**
- Forcing a choice before understanding the problem
- Deciding without considering real constraints
- Picking based on generic principles vs. specific context

## Validation Checklist

After enforcing divergence, verify:
- [ ] Clear choice stated early and reinforced at end
- [ ] Alternative's appeal acknowledged (not straw-manned)
- [ ] Decisive reasoning explains why alternative doesn't win
- [ ] Tradeoffs are explicit and defended
- [ ] No reopening of alternatives after choice made
- [ ] No undermining hedges like "but it depends"
- [ ] Confidence in recommendation is clear

## Output Quality Indicators

**Good divergence enforcement:**
- Reader knows exactly what to do
- Reasoning is transparent and defensible
- Tradeoffs are clear, not hidden
- Alternative's merit is respected but overcome
- Recommendation feels earned, not arbitrary

**Poor enforcement:**
- Still feels like "it depends"
- Hedge language persists despite choosing
- Why this choice beats alternatives is unclear
- Reader left uncertain about recommendation
