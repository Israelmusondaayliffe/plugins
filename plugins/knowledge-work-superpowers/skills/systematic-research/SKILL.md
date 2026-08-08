---
name: systematic-research
description: Use when deep research, current or disputed facts, fact checking, literature review, or a multi-source investigation needs primary evidence.
---

# Systematic Research

## Purpose

Answer important questions through an explicit evidence process. Search results are discovery aids, not evidence by themselves.

## Research Gate

Do not draft conclusions before defining the decision question, research questions, evidence standard, and stop condition. State what decision or deliverable the research must change. For simple one-source lookups, use the fast path and cite the direct source.

Choose the research bound before searching: bounded research answers one decision question within named limits; broad research maps a field but still defines a saturation rule and excluded branches.

## Workflow

### Phase 1: Question Map

Break the brief into answerable questions. For each question, record:

- Why it matters.
- What evidence would answer it.
- Which source owns the fact.
- What date or freshness range applies.
- What would disconfirm the likely answer.

Also record the overall stop condition, such as a source-owner answer, a minimum independent evidence threshold, a time boundary, or saturation with named remaining gaps.

### Phase 2: Source Routing

Use this order:

1. The internal connector or file that owns the fact.
2. Primary public sources such as official documents, filings, datasets, laws, standards, papers, transcripts, and first-party records.
3. Strong secondary analysis for context or interpretation.
4. Discovery sources that lead to stronger evidence.

For technical or platform questions, prefer official documentation. For current facts, use live research rather than memory.

### Phase 3: Discovery Pass

Map terminology, key entities, likely primary sources, date ranges, and competing explanations. Use discovery sources to find authoritative material.

Do not fill the final source ledger with weak pages merely because they rank highly.

### Phase 4: Evidence Pass

Open and read the sources that can directly answer the questions. Record each useful source in `../../assets/source-ledger-template.md` or an equivalent ledger.

For every source, capture:

- Source ID.
- Title and location.
- Source type.
- Publication or update date.
- Access date.
- Relevant question or claim.
- Limits, conflicts, and useful details.

### Phase 5: Triangulation

For important claims, seek independent support when available. Independence matters more than repetition. Several pages repeating one original report count as one evidence chain.

When sources conflict:

1. Check dates, definitions, populations, methods, and incentives.
2. Identify whether the conflict is factual, methodological, or interpretive.
3. Prefer the source closest to the original fact.
4. Preserve the disagreement when it cannot be resolved.

### Phase 6: Gap And Counterevidence Pass

Search for:

- Evidence against the emerging conclusion.
- Missing populations or cases.
- More recent updates.
- Retractions, corrections, or changed definitions.
- Internal evidence that conflicts with public claims.

Do not treat the first coherent story as the final answer.

### Phase 7: Saturation Check

Stop when the predeclared condition is met: additional searching is no longer changing the decision-relevant answer, the remaining gaps are named, and the evidence standard is met. Do not stop merely because enough sources have been collected. If the bound expires first, return the strongest supported answer and the exact unresolved question rather than widening scope silently.

## Source Quality Questions

Ask:

- Is this the original source?
- Is it current enough for the claim?
- Does it measure or state what the draft will claim?
- Are definitions and populations aligned?
- Does the source have a reason to overstate the result?
- Can the reader inspect it?

## Citation Discipline

- Cite the page that supports the claim, not a search-results page.
- Place citations near the supported claim.
- Use quotations sparingly and within applicable limits.
- Do not cite a source for a broader claim than it supports.
- Label inaccessible or unverified sources.

## Handoff

When the source ledger is ready, load `knowledge-work-superpowers:evidence-first-analysis` to test the claims. For independent question groups and permitted multi-agent work, load `knowledge-work-superpowers:dispatching-parallel-research`. Route a durable fresh-task research handoff to Continuity Vault.
