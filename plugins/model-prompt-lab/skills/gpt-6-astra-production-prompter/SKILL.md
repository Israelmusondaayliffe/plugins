---
name: gpt-6-astra-production-prompter
description: Prepare, migrate, and diagnose prompts for GPT-6 Astra using explicitly accepted field evidence before or after local model availability. Use for Astra prompts, Astra migration, Astra prompt audit, overcomplicated Astra interfaces, landing-page bias, extra controls or labels, Astra writing, Astra computer use, or effort and cost restraint. Treat host support, exact model strings, API parameters, pricing, and rollout status as unverified until the owning surface proves them.
---

# GPT-6 Astra Production Prompter

Build an Astra-ready prompt overlay without turning early reports into permanent harness policy. Astra does not need to be installed locally to prepare or audit the overlay. Local availability is required only for runtime acceptance.

## Evidence boundary

Load `references/field-evidence.md` first. It records the user-accepted field observations that justify this overlay and separates them from facts that still need host or owner verification.

Never invent an Astra model slug, API parameter, effort enum, price, availability date, or rollout state. In a prompt delivery, write the target as `GPT-6 Astra` in prose and mark configuration as `verify on the target host` until the owning surface exposes exact values.

## Routes

- New prompt: load `agents/agent-generate.md`.
- Existing prompt moving to Astra: load `agents/agent-migrate.md`.
- Existing Astra prompt with a specific failure: load `agents/agent-diagnose.md`.

If the request is ambiguous, infer the route from the supplied artifact and symptom. Ask only when the missing choice would materially change the result.

## Stable rules

Preserve user authority, safety, privacy, approval boundaries, plugin ownership, explicit-only activation, source accuracy, and worker-verifier separation. Do not remove stable policy merely because Astra may follow instructions more strongly.

## Astra overlay

1. State the job, intent, success criteria, hard boundaries, and output contract once.
2. Remove repeated emphasis, legacy anti-laziness pressure, forced checklists, generic tool pressure, default subagent fan-out, and stale model names unless a measured failure still requires them.
3. For interfaces, state the requested product type. Do not turn a simple interface into a landing page. Do not add labels, buttons, sections, features, dashboards, or explanatory furniture that the task does not require.
4. Use computer control when it materially completes the job and the host provides it. Observe, act narrowly, re-observe, and verify the result. Do not add tool rituals to tasks that do not need them.
5. Match effort to task difficulty and cost. High effort is not the default. If higher effort increases overbuilding, step down before adding prompt scaffolding.
6. For writing, preserve voice and intent. Do not add generic polish when the draft is already clear.
7. Stop once the acceptance criteria are met. One focused retry is enough unless new evidence changes the diagnosis.

## Delivery

Use `assets/delivery-template.md`. Put the finished prompt in its own code block. Run `scripts/validate_prompt.py` on the delivered prompt. For a Codex target whose current catalog exposes `gpt-6-astra`, add `--target-host codex`; this permits that exact host-qualified ID, not API aliases or invented variants. Without a verified target, keep the default prose-only model name.

Runtime acceptance requires current host availability and a bounded check against the requested outcome. Use `references/migration-overlay.md` when new evidence is needed; do not run a broad benchmark without a concrete decision it will inform.
