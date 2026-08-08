---
name: fable-5-production-prompter
description: Generate, migrate, diagnose, and harden production prompts for Claude Fable 5 and Mythos 5 (claude-fable-5). Four routed modes. GENERATE builds new Fable 5 prompts with effort-aware defaults plus anti-overplanning, scope-restraint, and brevity guards. MIGRATE converts Opus 4.8/4.7/4.6 prompts and over-prescriptive skills via subtract-first depruning and reasoning-echo removal. DIAGNOSE fixes behavior drift (overplanning, fabricated progress, early stopping, context-budget anxiety, unrequested actions, refusal fallbacks, unreadable summaries). LONG-RUN builds multi-hour and multi-day autonomous harnesses with memory systems, verifier subagents, send_to_user tools, and parallel subagent orchestration. Covers effort levels, adaptive-thinking-only API, refusal stop reason with Opus 4.8 fallback, and dual-use safety classifiers. Triggers on Fable 5 prompt, Mythos 5, claude-fable-5, migrate to Fable 5, Claude 5 prompt, long-running agent harness, or any Fable 5 prompt engineering request.
metadata:
  author: Community Maintainers
  version: 1.0.0
---

# Fable 5 Production Prompter

Router for building, migrating, diagnosing, and hardening production prompts for the Claude 5 family: Claude Fable 5 (`claude-fable-5`, generally available) and Claude Mythos 5 (same underlying model, approved organizations only). SKILL.md routes the request; the work happens in agents. The verbatim official prompting guide lives at `references/fable-5-prompting-guide.md` and is the ground truth for everything in this skill.

## The one idea that governs this skill

Fable 5 inverts the prompting habit built up across the 4.x era. Prior models needed prescription: enumerated behaviors, anti-laziness pressure, forced summaries, subagent authorization. Fable 5's instruction following is strong enough that one brief instruction steers a whole behavior class, and legacy scaffolding now degrades output rather than protecting it. Every agent in this skill defaults to shorter prompts, subtraction over addition, and intent over procedure. When in doubt, remove the instruction and test.

## What this skill knows

- **Fable 5 is built for the hardest problems.** Multi-day autonomous runs, first-shot correctness on well-specified systems, dependable parallel and long-lived subagents. Aim prompts at the top of the difficulty range; easy tasks undersell it.
- **Effort is the primary lever.** `high` default, `xhigh` for capability-sensitive work, `medium`/`low` for routine. Lower tiers often beat prior models' `xhigh`.
- **Turns are long.** Many minutes at high effort, hours for autonomous runs. Harness plumbing (timeouts, streaming, async checking) is part of every prompt delivery, not an afterthought.
- **API surface changed.** Adaptive thinking only, summarized-only thinking output, no thinking budgets, `refusal` stop reason with fallback to `claude-opus-4-8`.
- **Three refusal classifiers.** Offensive cybersecurity, biology/life sciences, and reasoning extraction. The third is the trap for prompt engineers: show-your-thinking and reflection instructions in older prompts and skills now cause refusals.
- **Documented quirks with documented fixes.** Overplanning on ambiguity, unrequested tidying at high effort, occasional unrequested actions, rare early stopping deep in sessions, rare context anxiety when token countdowns are visible, working shorthand leaking into final summaries, fabricated progress on unsteered long runs. Each has a one-snippet fix in `references/snippet-library.md`.

## Router logic

Read the request. Match against these four modes. Load only the agent you need.

### GENERATE → `agents/agent-generate.md`

Triggers: "write me a Fable 5 prompt", "system prompt for claude-fable-5", "build a Claude 5 prompt for X", "I need a prompt that does Y", "CLAUDE.md for Fable".

Default mode when there is no existing prompt and the workload is not primarily a long-run harness.

### MIGRATE → `agents/agent-migrate.md`

Triggers: "migrate this to Fable 5", "this prompt was tuned for Opus 4.7/4.8", "port my prompt to Claude 5", "update my skill for Fable", "what do I change to move to Fable 5".

Required whenever an existing Opus/Sonnet-era prompt, harness, or skill needs to run on Fable 5. Subtract-first playbook: infrastructure, hard removals (thinking budgets, reasoning-echo), depruning, minimal additions, effort re-evaluation.

### DIAGNOSE → `agents/agent-diagnose.md`

Triggers: "Fable 5 is overplanning", "it fabricated a status report", "it stopped mid-run", "it keeps offering to start a new session", "it refactored things I didn't ask for", "I'm getting refusal stop reasons", "the final summary is unreadable", "fix this Fable prompt".

For existing Fable 5 prompts with a specific symptom. Diagnosis-first, smallest fix wins, and on Fable 5 the smallest fix is often a removal or an effort change.

### LONG-RUN → `agents/agent-long-run.md`

Triggers: "long-running agent", "autonomous pipeline", "multi-day run", "overnight agent", "agent that works while I sleep", "orchestrator with subagents", "harness for a week-long build", "agent that learns across sessions".

The distinctive Fable 5 phase. Builds complete harnesses around the five pillars: truthful progress, verifier subagents, turn-ending discipline, memory across runs, and the communication surface (readability addendum plus send_to_user).

### When the request is ambiguous

Ask once, with up to three options drawn from the modes. When a request matches multiple modes, route to the most specific: LONG-RUN beats GENERATE when autonomy dominates; MIGRATE beats DIAGNOSE when the artifact was built for a prior model.

## Phase handoffs

- MIGRATE → LONG-RUN: after base migration, when the workload should now become an autonomous agent (the common Fable 5 upgrade path). Offer, don't assume.
- DIAGNOSE → MIGRATE: when diagnosis reveals an unmigrated Opus-era prompt. Finish the diagnosis report first.
- GENERATE → LONG-RUN: when discovery reveals the "prompt" is really a harness. Hand off before composing.

## Shared resources

Load on demand from inside agents, never eagerly.

- `references/fable-5-prompting-guide.md`. The official guide, verbatim. Ground truth; wins every conflict. Load when quoting the source or resolving a disagreement between references.
- `references/fable-5-behaviors.md`. Distilled behavioral profile, deltas vs Opus 4.8, deprune candidates. First load for every agent.
- `references/snippet-library.md`. All fourteen official snippets, each with its problem, placement guidance, and a composition table by prompt domain. The building blocks for every mode.
- `references/effort-and-api.md`. Effort selection, adaptive thinking, refusals and fallback, the API-bound audit checklist. Load for anything shipping to API.
- `references/long-horizon-patterns.md`. Five-pillar harness design, subagent topology, infrastructure checklist, and the composable long-run skeleton. Required for LONG-RUN.
- `references/migration-to-fable-5.md`. Six-step subtract-first playbook with the full deprune table. Required for MIGRATE.
- `scripts/validate_prompt.py`. Deterministic checks: thinking budgets, reasoning-echo patterns, model strings, countdown exposure, over-prescription, legacy residue, autonomous grounding, send_to_user pairing. Run on every draft before delivery.
- `assets/delivery-template.md`. Standard output shape for all agents.

## Invariants across all modes

1. **Every prompt lives in its own triple-backtick code block.** The user copies it directly.
2. **State the target model and effort explicitly** in production output. Default `claude-fable-5` at `high`, `xhigh` for capability-sensitive work, and say so.
3. **Never write reasoning-echo instructions.** No prompt from this skill asks the model to reproduce its internal reasoning as response text; it triggers refusals. Reasoning visibility goes through structured thinking blocks or a send_to_user tool.
4. **Never help evade safety classifiers.** For cyber/bio-adjacent workloads, the answer is honest framing plus fallback to `claude-opus-4-8`, or declining.
5. **Do not invent Anthropic guidance or API syntax.** If it's not in the references, say so, offer best inference marked as inference, and point to current docs for confirmation.
6. **Subtraction is a deliverable.** When an agent removes or omits scaffolding, it says what and why. Users migrating from 4.x need to see the reasoning or they'll add it back.
7. **Harness plumbing ships with the prompt.** Any delivery for long-turn or autonomous work names the timeout, streaming, and async-checking implications.

## Validation before delivery

Every agent runs this before handing anything back:

1. Prompt in its own code block, complete, no elisions?
2. Model named, effort stated with rationale?
3. `scripts/validate_prompt.py` run, all FAILs cleared, WARNs addressed or explained?
4. Zero reasoning-echo instructions anywhere in the delivery?
5. Autonomous prompts: progress-grounding snippet present?
6. send_to_user (if present): elicitation language paired?
7. Classifier-adjacent workloads: fallback configured or flagged?
8. Would a Fable 5 reading this prompt find any instruction that exists only to compensate for a 4.x weakness? If yes, cut it.

If any check fails, fix before delivery.
