# Bundled Unslop Engine Contract

## Ownership and independence

`unslop-harness-repair` owns Unslop work for the selected platform's harness and explicitly approved plugins. It contains the complete local Unslop engine used by this workflow. Removing or disabling the Writing Quality plugin must not remove detection, voice preservation, plain-language editing, pattern references, protected-material checks, or quality validation from this skill.

Writing Quality remains the owner for ordinary documents, emails, posts, and other writing outside harness or plugin maintenance. It is not a runtime dependency, required companion, or qualification authority for this skill.

The bundled engine is a dated snapshot of the canonical merged Writing Enforcer capability. Its source provenance remains in [source-provenance.md](unslop-engine/source-provenance.md). The local [engine manifest](unslop-engine-manifest.json) pins every bundled file by SHA-256.

Load [workflow.md](unslop-engine/workflow.md) before either `DETECT` or `REWRITE`. It is the mandatory runtime method. The remaining references supply the rules and evidence used inside that method.

## Modes

Use `DETECT` during audit. Report raw findings without changing source files.

Use `REWRITE` only after the user approves an exact repair group. The parent task or session makes the minimum effective edit inside approved human-facing prose. Deterministic scripts detect and verify. They do not receive broad mutation authority.

## Full local capability

The bundled engine provides:

- the full four-phase runtime method, rewrite threshold, voice-recovery techniques, scoring, failure modes, and output contracts in [workflow.md](unslop-engine/workflow.md);
- the original 24-pattern catalog in [ai-pattern-taxonomy.md](unslop-engine/ai-pattern-taxonomy.md);
- the additional 23-pattern catalog in [extended-patterns.md](unslop-engine/extended-patterns.md);
- the plain-language replacement table in [word-replacement-table.md](unslop-engine/word-replacement-table.md);
- context tolerances in [context-profiles.md](unslop-engine/context-profiles.md);
- voice extraction and preservation in [voice-extraction-guide.md](unslop-engine/voice-extraction-guide.md);
- source-backed voice and protected-material rules in [unslop-policy.md](unslop-engine/unslop-policy.md);
- negative patterns, clichés, and equivocation checks in [negative-style-guide.md](unslop-engine/negative-style-guide.md), [cliche-inventory.md](unslop-engine/cliche-inventory.md), and [divergence-patterns.md](unslop-engine/divergence-patterns.md);
- high-stakes criticism and repair recovery in [critique-frameworks.md](unslop-engine/critique-frameworks.md) and [failure-recovery.md](unslop-engine/failure-recovery.md);
- the full scoring model in [validation-criteria.md](unslop-engine/validation-criteria.md);
- local quality scanning, voice profiling, protected-material comparison, and punctuation utilities under `scripts/unslop-engine/`.

## Harness and plugin adaptation

Treat harness and plugin prose as technical documentation unless a closer profile is supported. Preserve precise domain terms. `harness`, plugin names, skill names, commands, paths, schema keys, frontmatter, routing triggers, identifiers, prompt tokens, tests, and quotations are not decorative language.

The raw scanner is evidence, not the final decision. It can flag valid technical terms and command flags. Classify each residual with source and context evidence. Do not lower the quality standard to excuse ordinary slop.

Protected exact material never changes inside this repair workflow. The repair verifier covers more harness forms than the bundled generic protected-material script, including quoted prose, tables, frontmatter, paths, identifiers, variable-length fences, and structured files. Use the generic script as additional evidence only.

## Required workflow

1. Run the local engine integrity check.
2. Load and follow the bundled four-phase workflow.
3. Extract intent, stakes, and source-backed voice signals from the approved text.
4. Run the local pattern scan in `DETECT` mode.
5. Separate raw findings from accepted findings and protected residuals.
6. Freeze source and protected-material hashes.
7. Present exact repair groups and wait for approval.
8. Apply the minimum effective edit using the local policy and references.
9. Re-scan with the local engine.
10. Reconcile all accepted findings and raw residuals.
11. Run repair verification and one fresh integrated review.

## Local commands

Verify that every pinned engine file is present and unchanged:

```bash
python3 scripts/unslop_repair.py engine-check
```

Create raw Unslop scan evidence without changing the input:

```bash
python3 scripts/unslop_repair.py scan \
  --input /absolute/path/to/file.md \
  --output /absolute/path/to/scan.json
```

Extract a voice profile when the source contains meaningful voice signals:

```bash
python3 scripts/unslop-engine/voice_profiler.py \
  /absolute/path/to/source.md \
  --output /absolute/path/to/voice-profile.json
```

Do not run `emdash_replacer.py` in place on a harness or plugin tree. It can rewrite protected syntax. If needed, use it on a scratch prose-only copy, review the diff, then apply the approved edit through the bounded repair workflow.

## Independence gate

Qualification fails when:

- a bundled engine file is missing or does not match its pinned hash;
- the workflow calls a script or reference from the Writing Quality plugin;
- the skill cannot scan and profile text from an isolated copy of its own directory;
- a worker treats Writing Quality as an approval, repair, or completion authority.
