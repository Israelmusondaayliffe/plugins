---
name: unslop-harness-repair
description: Repair writing-quality drift in an AI operating harness or explicitly approved plugins through a read-only audit, hash freeze, user-approved bounded edits, protected-material checks, residual reconciliation, integrated review, and release proof. Use when the user affirmatively requests an Unslop harness repair or when Harness Maintainer loads this specialist for prose-changing maintenance. Do not use for ordinary document editing, explanation-only requests, cache cleanup, authentication, version-only changes, binaries, or code-only maintenance.
---

# Unslop Harness Repair

Turn a proven audit-to-freeze repair method into a controlled Harness Engineering operation. This platform-neutral edition supports Claude Code, Claude Cowork, and Codex. It contains its own complete Unslop engine and owns Unslop work for the selected platform's harness and approved plugins. It does not require the Writing Quality plugin. Harness Engineering owns scope, approvals, repair control, integration, installation, and completion.

## Activation

- Run after an affirmative user request for this specialist.
- Harness Maintainer may load it when approved maintenance can change human-facing prose in the platform's instruction-file chain, skills, plugins, prompts, metadata, or references.
- Keep ordinary prose Unslop with `writing-quality:writing-quality-router` when that plugin is available. Its presence or absence does not change this skill's harness and plugin capability.
- Do not activate from quoted, negated, hypothetical, future, or explanation-only wording.

## Default scope

Start with the active platform instruction-file chain, the Harness Engineering plugin, and the closest current harness contracts. Add another plugin only when the user names it or approves it in the repair plan.

## Required sequence

1. Load [repair-contract.md](references/repair-contract.md), [worker-contract.md](references/worker-contract.md), [unslop-engine-contract.md](references/unslop-engine-contract.md), and the bundled [four-phase workflow](references/unslop-engine/workflow.md). The workflow is mandatory runtime policy, not optional background material.
2. Run `scripts/unslop_repair.py engine-check`. Stop if any pinned local engine file is missing or changed.
3. Audit the approved text surfaces without changing them. Extract intent, stakes, and source-backed voice signals.
4. Run the bundled engine in `DETECT` mode with `scripts/unslop_repair.py scan`.
5. Freeze exact paths, hashes, routing state, protected material, and the bundled engine digest.
6. Separate raw scanner matches from accepted findings. Preserve exact platform and domain terms when context requires them.
7. Present the audit, repair groups, score gate, exclusions, resource cap, and stop conditions. Wait for explicit approval.
8. Apply only the approved repair group. Follow the bundled four-phase workflow with its policy, 47-pattern catalog, word table, context profiles, and voice rules. Use zero to three direct worker agents through the host's native agent surface only when their scopes are disjoint.
9. Re-scan locally. Reconcile every accepted finding to `repaired` or `protected`. A protected finding needs a category, reason, source owner, and evidence.
10. Apply the contextual qualification gate. A raw scanner exit code or raw score is never the verdict.
11. Run one fresh read-only integrated review over the whole candidate, including the independence gate.
12. Show the exact candidate diff and qualification result. Wait for separate promotion approval before installation.
13. After promotion approval, verify changed bundles, installed listing, source-cache parity, explicit invocation, front-door routing, isolated engine operation, and fresh discovery.

## Hard gates

- Contextual score must be at least 8.0 out of 10. Target 10.0.
- Zero fabricated facts, opinions, emotions, identity claims, experience, numbers, examples, or outcomes.
- Zero protected-material drift, unapproved scope changes, unresolved accepted findings, P0 credibility failures, routing corruption, placeholder corruption, or authored em dashes.
- The bundled Unslop engine must be complete and usable from an isolated copy of this skill without Writing Quality.
- Hard-gate failures cannot be offset by a higher score.
- One repair wave where unresolved work does not fall stops the run and requires a new plan.

## Authority

The parent task or session owns the freeze, approvals, integrated diff, installation, and terminal verdict. Workers return evidence only. Deterministic scripts never rewrite raw harness or plugin trees. The parent applies approved minimum-effective edits and never expands its own scope.
