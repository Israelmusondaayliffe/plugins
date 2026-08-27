# Unslop Harness Repair Contract

## Ownership

This skill owns the complete Unslop method for harness and plugin repair. Its bundled engine supplies the policy, 47-pattern catalog, voice-preservation rules, word table, context profiles, scanner, and validation tools. Harness Engineering owns the repair run, including scope, freeze, approvals, worker boundaries, mutation, reconciliation, integrated review, release, and completion.

Writing Quality owns ordinary prose work only. It is not a runtime dependency or qualification authority here. Classify legitimate technical language in context. Do not remove a precise term merely because a raw scanner dislikes it.

## Phase 1: read-only audit

Inspect the current source owner, installed state, routing owner, and exact approved roots. The normal default is:

- the active platform instruction-file chain;
- the Harness Engineering source plugin;
- the closest current harness contracts for the selected platform.

Other plugins are outside scope until named or approved. Inventory only text surfaces relevant to the requested repair. Run the bundled engine integrity check, voice profiler when the source carries meaningful voice, and local scan. Record raw matches separately from accepted findings.

The audit must leave every source hash unchanged. Use:

```bash
python3 scripts/unslop_repair.py audit \
  --run-id RUN_ID \
  --root /absolute/approved/root \
  --output /absolute/output/audit.json
```

## Phase 2: freeze

Freeze only after the audit inventory is stable. The freeze stores the approved roots, exact file hashes, protected-material fingerprints, full inventory digest, and bundled Unslop engine digest.

```bash
python3 scripts/unslop_repair.py freeze \
  --audit /absolute/output/audit.json \
  --output /absolute/output/freeze.json
```

If a source hash changes between audit and freeze, stop. Do not silently refresh the baseline.

## Phase 3: approval

Present:

- accepted finding clusters and their evidence;
- raw matches classified as protected or legitimate technical language;
- exact allowed roots and target paths;
- repair groups and worker assignments;
- the 8.0 score floor and 10.0 target;
- hard gates, failure stops, rollback path, and release boundary.

Do not repair before explicit approval. Candidate approval does not authorize installation, routing promotion, publication, or private repository synchronization.

## Phase 4: bounded repair

Back up each existing target before mutation. Apply small, reversible edits only inside the approved paths. Use the bundled Unslop engine in `REWRITE` mode: preserve source-backed voice, remove accepted patterns, prefer plain precise language, and make the minimum effective edit. Preserve meaning, commands, code, prompts, quotations, links, identifiers, paths, tables, frontmatter, and other structured material.

Protected material does not change inside an Unslop repair. If an accepted finding sits inside protected metadata or another protected form, classify it `protected`. A separate operation with its own approval and task-owned verifier may change that material, but it is outside this repair run.

Excessive Markdown bold is editable formatting. The verifier allows bold delimiters to be removed while requiring the exact emphasized words to survive. Changing those words remains protected-material drift.

The repair process may use zero to three direct worker agents through the host's native agent surface under the worker contract. The parent integrates the result and rejects out-of-scope changes.

Do not use global replacement or automatic prose rewriting on raw harness trees. In particular, a punctuation or wording script cannot decide whether a token is prose, code, a quotation, a path, an identifier, or source-owned language.

## Phase 5: reconciliation

Every accepted finding must end in one terminal state:

- `repaired`: the approved candidate resolves the finding and records evidence;
- `protected`: the text must remain, with category, reason, source owner, and evidence.

`Needs review`, deferred, audit-only, unclassified, and unresolved are not terminal. The final unresolved count must be zero.

Raw residuals remain separate from accepted findings. Each residual needs one of these contextual classifications:

- `legitimate-technical`;
- `protected-source`.

The literal term `harness` is not a defect when it precisely names the system under maintenance.

## Phase 6: qualification

The contextual score covers only editable, assistant-authored prose after protected and legitimate technical material is classified.

| Category | Points | Pass condition |
| --- | ---: | --- |
| Meaning and factual fidelity | 2.0 | No invented or weakened claims |
| Protected material | 2.0 | Exact protected fingerprints remain intact |
| Scope and authority | 1.5 | Every change is approved and owned |
| Finding reconciliation | 1.5 | Every accepted finding is terminal |
| Language quality | 2.0 | Direct, specific prose with no authored em dashes |
| Verification evidence | 1.0 | Behavior checks and fresh integrated review pass |

The minimum is 8.0 out of 10. Target 10.0. These hard gates cannot be offset by points:

- fabrication or invented voice;
- protected-material drift;
- unapproved scope;
- unresolved accepted findings;
- P0 credibility, routing, or placeholder corruption;
- authored em dashes;
- missing, changed, or externally dependent bundled Unslop capability.

Use the bundled validator under `scripts/unslop-engine/` as report-only evidence through `scripts/unslop_repair.py scan`. Record its raw findings and explain contextual exclusions. Do not accept its exit code or unclassified raw score as the qualification verdict. Qualification fails if the bundled engine is incomplete or the workflow calls Writing Quality resources.

## Phase 7: integrated review

One fresh read-only reviewer compares the complete candidate with the freeze and checks:

- meaning and factual fidelity;
- quotations and quoted prose;
- inline code and fenced blocks;
- prompt tokens and delimiters;
- links, paths, identifiers, tables, and frontmatter;
- routing and activation boundaries;
- placeholder suffixes and malformed sentences;
- complete finding and residual ledgers;
- local engine integrity and isolated operation without Writing Quality.

Any finding blocks promotion. Repair inside the approved group, regenerate the candidate inventory digest, and rerun the one integrated review.

## Phase 8: candidate and release stops

Show the exact candidate diff, test results, score, hard-gate result, residual classes, and integrated review before installation. Stop for promotion approval.

After approval, validate only changed plugins and skills. Prove source validation, native tests, installed listing, exact source-cache parity, explicit specialist invocation, front-door routing, isolated local-engine operation, and fresh-task discovery. Report `functional_result` and `qualitative_result` separately.

## Verification ledger

The verification command consumes the freeze plus a JSON ledger:

```json
{
  "schema_version": 1,
  "run_id": "RUN_ID",
  "approval": {
    "status": "approved",
    "group": "bounded-repair",
    "authority": "user",
    "evidence": "user approval reference",
    "approved_paths": ["/absolute/root/file.md"],
    "created_paths": []
  },
  "workers": [],
  "findings": [],
  "residuals": [],
  "quality": {
    "score": 10.0,
    "floor": 8.0,
    "target": 10.0,
    "category_scores": {
      "meaning_factual_fidelity": {"score": 2.0, "max": 2.0, "evidence": "EVIDENCE"},
      "protected_material": {"score": 2.0, "max": 2.0, "evidence": "EVIDENCE"},
      "scope_authority": {"score": 1.5, "max": 1.5, "evidence": "EVIDENCE"},
      "finding_reconciliation": {"score": 1.5, "max": 1.5, "evidence": "EVIDENCE"},
      "language_quality": {"score": 2.0, "max": 2.0, "evidence": "EVIDENCE"},
      "verification_evidence": {"score": 1.0, "max": 1.0, "evidence": "EVIDENCE"}
    },
    "hard_gates": {
      "fabrication_free": true,
      "protected_material_intact": true,
      "scope_intact": true,
      "terminal_findings": true,
      "p0_clear": true,
      "authored_em_dash_free": true,
      "unslop_engine_complete": true
    }
  },
  "repair_waves": [],
  "integrated_review": {
    "status": "clear",
    "fresh": true,
    "reviewer": "fresh-reviewer-id",
    "inventory_sha256": "CURRENT_INVENTORY_SHA256"
  }
}
```

Run:

```bash
python3 scripts/unslop_repair.py verify \
  --freeze /absolute/output/freeze.json \
  --ledger /absolute/output/ledger.json \
  --output /absolute/output/qualification.json
```
