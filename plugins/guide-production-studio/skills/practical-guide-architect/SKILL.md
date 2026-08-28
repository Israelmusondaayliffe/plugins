---
name: practical-guide-architect
description: Design a practical guide after its sources are mapped. Use when choosing one page, layered sections, or child pages; defining beginner and expert paths; removing repetition; and making each component solve a reader problem. Do not use before evidence status is known.
metadata:
  author: Community Maintainers
  version: 0.1.1
---

# Practical Guide Architect

Choose structure from the reader's job. A page exists because it helps someone understand, try, compare, troubleshoot, or return for reference.

## Prerequisite

Require a validated guide contract with mapped sources, evidence, examples, and boundaries. Load `../guide-production-router/references/guide-architecture.md`.

For visual or spatial subjects, also load `../guide-production-router/references/visual-evidence.md`.

## Workflow

1. **Name the reader's job.** Write the action they came to complete, not the subject label.
2. **Name the starting point.** State what a new reader probably knows and what an experienced reader still needs.
3. **Choose the smallest useful shape.** Select a single page, layered page, or parent with child pages using the architecture reference.
4. **Design the start path.** Let a first-time reader understand the purpose and attempt one useful action without reading the entire system.
5. **Design the return path.** Let an experienced reader find prompts, parameters, decision rules, examples, or troubleshooting quickly.
6. **Make components earn their place.** For every page, prompt, template, image, or download, record the reader problem it solves and the evidence that supports it.
7. **Remove default packaging.** Reject components included only because another guide had them.
8. **Place examples before blanks.** A reader sees the method applied before receiving a reusable template.
9. **Limit duplication.** Parent pages orient and route. Child pages teach. Downloads support reuse without becoming the only useful content.
10. **Update and validate the contract.** Record the final mode, pages, components, visual requirements, and scale gate.

## Handoff

Return the validated architecture to the router. Writing may start only after the architecture is accepted for the benchmark.

## Failure stops

- A proposed component has no named reader problem.
- The structure is copied from another guide without topic-specific justification.
- A child page repeats its parent instead of teaching a distinct job.
- A blank form or template is the main teaching experience.
- A visual subject has no plan for visual evidence.
