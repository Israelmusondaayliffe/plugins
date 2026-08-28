---
name: guide-production-router
description: Route source-grounded practical guides across source mapping, architecture, writing, and independent review. Use when building or rebuilding manuals, how-to pages, prompt guides, or reference libraries where context, evidence, examples, visual teaching, and human acceptance matter. Do not use for simple copyediting, workshops, or publication-only work.
metadata:
  author: Community Maintainers
  version: 0.1.1
---

# Guide Production Router

Own the teaching product, not merely its prose. A useful guide lets a reader understand the idea, try the work, recognize failure, and decide what to do next without hidden context.

## Route the request

- **Map sources or decide what can be taught:** load `../guide-source-mapper/SKILL.md`.
- **Choose one page, layered sections, or child pages:** load `../practical-guide-architect/SKILL.md`.
- **Write or rebuild an approved guide:** load `../practical-guide-builder/SKILL.md`.
- **Review a candidate as a reader:** load `../guide-acceptance-review/SKILL.md`.
- **Run the complete workflow:** source map, architecture, one benchmark, independent review, human gate, then scale.

Use the smallest route that completes the current request. Do not load later phases before their inputs exist.

## Required contract

Create one private guide contract from `assets/guide-contract.template.json`. Validate it with:

```text
python3 scripts/validate_guide_contract.py GUIDE_CONTRACT.json
```

The contract combines source lineage, audience, architecture, evidence, boundaries, and acceptance. Do not create separate ledgers unless the source volume truly requires one.

Load these references only when their decision is active:

- `references/provenance-policy.md` while classifying sources, examples, and attribution.
- `references/guide-architecture.md` while choosing structure and components.
- `references/visual-evidence.md` for visual, motion, image, interface, or spatial subjects.
- `references/human-acceptance-rubric.md` during independent and human review.

## Workflow gates

1. **Inspect the actual sources.** Summaries and generalized runtime material cannot replace an available original source when lineage matters.
2. **Separate privacy from provenance.** Protect private implementation details while retaining permitted public origin, proof, and attribution.
3. **Choose architecture from use.** Do not begin with a standard packet or predetermined page count.
4. **Build one benchmark.** Bulk production remains blocked until the benchmark passes human review.
5. **Require real evidence.** Use a real, rights-safe example or label the material as planning-only. Do not replace available real proof with fiction.
6. **Review independently.** The producer may revise but cannot approve the guide.
7. **Stop before publication.** Publication requires separate authority and a destination-owning capability.

## Companions

- Use Knowledge Work Superpowers when source collection or evidence synthesis is substantial.
- Use the relevant domain plugin or authoritative source for the subject method.
- Use Writing Quality only after the guide's teaching, evidence, and structure pass review.
- Use Notion or another destination owner only after explicit publication approval.
- Use ProofLoop only when the user explicitly requests its protocol.

## Completion

Guide production is ready for human review only when:

- the guide contract validates;
- every factual or behavioral claim has an approved source or a visible limitation;
- every component solves a named reader problem;
- examples and results carry accurate run status;
- visual subjects include usable visual evidence or are labeled reference-only;
- an independent review record validates with status `ready_for_human_review`;
- publication and bulk production remain blocked.

Human approval, cold-reader observation, publication, and scale are later states. Report them honestly.
