---
name: writing-enforcer
description: Applies the complete local 47-pattern Unslop method to ordinary prose while preserving source-backed voice and exact protected material. Use when the user asks to humanize, tighten, clean up, remove AI patterns, make prose sound like them, audit writing without rewriting, or validate a draft. Supports DETECT for report-only review and REWRITE only when the user authorizes prose changes.
license: MIT
metadata:
  author: Community Maintainers
  version: 1.1.0
  combines: humanizer, output-quality-enforcer-v3, avoid-ai-writing, stop-slop, no-ai-slop
---

# Writing Enforcer

Writing Enforcer owns the complete Unslop method for ordinary prose. It contains its own 47-pattern catalogs, plain-language rules, source-backed voice method, context profiles, criticism and recovery guides, scoring model, scanner, voice profiler, protected-material checks, and scratch-only punctuation helper.

## Modes

- `DETECT`: report patterns and their locations. Do not change the supplied text or write a replacement draft.
- `REWRITE`: use only when the user asks for or approves prose changes. Make the minimum effective edit and return the requested result.

If the request is ambiguous, choose `DETECT` or ask before changing prose.

## Required method

1. Load [workflow.md](references/unslop-engine/workflow.md). It is the full four-phase method and required runtime policy.
2. Identify the audience, purpose, stakes, requested mode, and factual boundary.
3. Extract voice only from the selected source or an explicit user-supplied sample. Never infer voice from memory, identity history, or unrelated work.
4. Run `scripts/unslop-engine/quality_validator.py` for raw pattern evidence. Treat its score as report-only evidence.
5. For `DETECT`, classify the findings and stop without mutation.
6. For `REWRITE`, preserve the source's meaning and useful texture, then make the smallest authorized change.
7. Run `scripts/protected_scope_validator.py BEFORE AFTER` when supplied Markdown or structured material contains protected forms.
8. Re-scan the candidate, reconcile raw residuals in context, and apply the contextual gate before delivery.

## Voice boundary

Preserve or clarify opinions, emotions, first person, rhythm, uncertainty, humor, bluntness, and useful roughness only when the selected source supplies them. Neutral source text stays neutral.

Never invent personality, facts, examples, certainty, identity claims, experience, results, opinions, emotions, or first-person claims.

## Protected boundary

Keep code, commands, logs, quotations, citations, prompts, links, paths, identifiers, tables, frontmatter, structured data, and exact templates unchanged. Strong emphasis delimiters may be removed only when every occurrence of the emphasized words survives exactly, including duplicate and multiline text.

Do not run a punctuation helper across all output, a source document, or a file tree. `scripts/unslop-engine/emdash_replacer.py` accepts only a separate scratch input and scratch output. Review its diff, then apply an authorized prose edit manually.

## Qualification gate

The contextual score must be at least 8.0 out of 10. Target 10.0. Raw script scores do not decide the result.

Fail when any hard gate is not clear:

- fabricated content or invented voice;
- protected-material drift;
- mutation without rewrite authority;
- unresolved accepted findings;
- P0 credibility failures;
- authored em dashes in editable prose;
- incomplete or externally dependent local engine.

## Ownership

Writing Quality owns ordinary documents, emails, posts, and other prose work. Harness Engineering's separate Unslop specialist owns harness and plugin maintenance. Each capability remains complete without a runtime dependency on the other.

## Local resources

- `references/unslop-engine-manifest.json` pins the complete local engine inventory.
- `references/unslop-engine/` contains the full method, catalogs, policy, provenance, scoring, notices, and recovery material.
- `scripts/unslop-engine/` contains the scanner, voice profiler, generic protected-material validator, and scratch-only punctuation helper.
- `scripts/engine_check.py` verifies the pinned local engine.
- `scripts/protected_scope_validator.py` enforces the expanded protected-material boundary.
