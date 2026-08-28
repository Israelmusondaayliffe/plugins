# Writing Quality

Writing Quality owns ordinary prose work: drafting, authorized rewriting, report-only review, claim boundaries, and final validation.

## Owned skills

- writing-quality-router
- claim-boundary-checker
- business-writing-intent-enforcer
- writing-enforcer

Writing Enforcer contains the complete local 47-pattern Unslop engine. Its full method, catalogs, plain-language table, context profiles, source-backed voice policy, criticism method, failure recovery, scoring model, provenance, and third-party notices ship inside the plugin. Local scripts provide scanning, voice profiling, protected-material checks, and scratch-only punctuation support.

## Companion capabilities

- Knowledge Work Superpowers for evidence-led analysis and deliverables
- Documents or Google Docs for file and collaborative document work

Companions are optional and remain source-owned.

## Boundaries

- `DETECT` requests do not authorize rewriting.
- `REWRITE` requires an explicit request or approval to change prose.
- Style work does not authorize new facts, examples, certainty, identity, experience, results, opinions, emotions, or first-person claims.
- Source-backed voice means preserving what the selected source supplies. Neutral text stays neutral.
- Code, commands, logs, quotations, citations, prompts, links, paths, identifiers, tables, frontmatter, structured data, and exact templates remain unchanged.
- Punctuation helpers operate only on a separate scratch prose copy. They never rewrite all output, a source document, or a file tree.
- Raw scanner scores are report-only evidence. The contextual floor is 8.0 out of 10, the target is 10.0, and every hard gate must clear.

## Ownership

Writing Quality owns ordinary documents, emails, posts, and other prose. Harness Engineering's Unslop specialist separately owns harness and plugin maintenance. Writing Quality remains complete when Harness Engineering is absent, and Harness Unslop remains complete when Writing Quality is absent. Neither capability has a runtime dependency on the other.

## Verification

Run `python3 skills/writing-enforcer/scripts/engine_check.py` to verify the pinned 19-file engine. Run `python3 scripts/verify_bundle.py` from any directory before release. Installation is trusted only after plugin validation, source-to-cache parity, live listing, and clean-task discovery all pass.
