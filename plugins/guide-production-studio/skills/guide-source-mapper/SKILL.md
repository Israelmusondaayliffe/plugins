---
name: guide-source-mapper
description: Map sources, evidence status, rights, public provenance, and private exclusions before guide design. Use when deciding what can be taught or named publicly, whether an example was actually run, and whether enough evidence exists to write without invention. Do not use for final prose or publication.
metadata:
  author: Community Maintainers
  version: 0.1.1
---

# Guide Source Mapper

Recover the best available truth before simplifying it. A safe public guide can hide private machinery without hiding legitimate public provenance.

## Inputs

- The user's supplied sources and methods
- Original public sources and official documentation
- Private source material permitted for transformation
- Rights-safe examples, images, prompts, and results
- The guide contract or its blank template

Load `../guide-production-router/references/provenance-policy.md` before classifying sources.

## Workflow

1. **Read originals first.** When a generalized plugin, summary, or extracted workflow points to an available original source, inspect the original before deciding what the public guide may say.
2. **Classify every source.** Record public attribution, public reference, private transform-only, user-owned, or forbidden status.
3. **Separate three questions.** Decide what may inform the guide, what may appear in it, and what must be attributed.
4. **Record evidence status.** Mark methods and examples as verified, user-supplied, observed, unrun, or unknown.
5. **Preserve public lineage.** Keep permitted source names, finished works, released documentation, and production history when they help the reader judge the method.
6. **Protect private machinery.** Remove plugin names, private paths, identifiers, internal prompts, source-only notes, and implementation details unless explicitly approved for publication.
7. **Identify evidence gaps.** Stop if a result claim lacks evidence or a necessary example would have to be invented.
8. **Update the contract.** Populate sources, evidence, examples, boundaries, and required attribution.

## Handoff

Return the validated guide contract to the router. Do not design pages, write the guide, or publish.

## Failure stops

- Public provenance and private implementation cannot be separated safely.
- Rights are unclear for a required example or visual.
- The only available example is fictional while real proof is known to exist but has not been inspected.
- Current platform behavior lacks an official or otherwise approved current source.
- A claimed result is unrun, unknown, or unsupported.
