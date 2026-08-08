---
name: frontier-extraction
description: Extract a frontier model's judgment into durable artifacts before access ends, pricing changes, or a model window closes. Applies the irreversibility test (can a cheaper model redo this tomorrow, if yes skip it) then routes across five moves. WORKSPACE rewrites CLAUDE.md and skills as an operating manual a weaker model can execute. AUDIT runs a consultant-grade business audit into an executable roadmap. VAULT atomizes deep research into one-insight linked notes. GOALS fires capped, evidence-gated goal runs on the highest-value backlog. RECORDER installs an extract-approach habit that writes a learnings note per solved problem. Use when the user says extract before it is gone, last day with this model, bank this model's judgment, distill the model, write the standard down, make this survive the model change, or wants session learnings captured automatically.
license: MIT
metadata:
  author: Community Maintainers
  version: 1.1.0
  source: Machina, Do this on your last day with Fable
---

# Frontier Extraction

A Tier 3 router for banking a frontier model's judgment into artifacts that keep their full
value after the model behind them is out of reach. The pattern is old: distill the teacher
while you have it, and everything trained on it still runs after the teacher is gone.

## The gate: the irreversibility test

Before doing anything under this skill, ask of the proposed work: **can a cheaper model
redo this tomorrow?** Websites, demo apps, content batches all fail the test, a mid-tier
model rebuilds them next week for nothing. What passes: a standard written down, a roadmap
already reasoned through, a knowledge vault already distilled, a skill that fires on its
own. Judgment-heavy to create, ordinary intelligence to use. If the user's request fails
the test, say so and redirect to what passes it. Mechanically: answer the question. Yes,
a cheaper model can redo it tomorrow: decline and redirect. No: proceed.

## Router

Load exactly one agent per move. Priority order when time is short: RECORDER first (it
converts all remaining time into assets automatically), then GOALS (it runs alone), then
WORKSPACE, AUDIT, VAULT.

| Request signals | Move | Load |
|---|---|---|
| Rewrite CLAUDE.md, write the standard, operating manual, quality bars, conventions, escalation rules | WORKSPACE | `agents/workspace-distiller.md` |
| Audit my business, consultant, roadmap, what should I stop doing, pricing, where my time goes | AUDIT | `agents/consultant-auditor.md` |
| Second brain, research vault, atomize, one insight per note, Obsidian, distill my research | VAULT | `agents/vault-miner.md` |
| Fire goals, unattended runs, highest-value backlog, spend the hours, long autonomous work | GOALS | `agents/goal-firer.md` |
| Capture how you solved that, learnings notes, record your approach, extraction habit | RECORDER | `agents/approach-recorder.md` |

"Run the full playbook" means executing moves in the priority order above, confirming scope
with the user once before starting (which projects, which backlog items), then proceeding
without further permission-asking.

## Shared rules

1. Every artifact this skill produces is written for a *less capable* reader. Checkable
   criteria, not adjectives. Named failure modes with the rule that prevents each. Exact
   escalation triggers. A cheaper model cannot invent a quality bar, but it applies a
   written one fine.
2. Write reasoning down in full at creation time: rationale, evidence, and tradeoffs in
   the document, never a replay of internal deliberation (reasoning-replay triggers
   refusal classifiers on Claude 5 models). The document, not the conversation, is the
   deliverable.
3. Atomize rather than summarize. A hundred linked one-insight notes get retrieved and
   reused; a 40-page report gets stored and forgotten.
4. Compose with the harness: route goal execution to goal-runner or loop-goal-engineer if
   mounted rather than reinventing loop mechanics here.

## Resources

- `agents/workspace-distiller.md`, `agents/consultant-auditor.md`, `agents/vault-miner.md`,
  `agents/goal-firer.md`, `agents/approach-recorder.md` - one per move
- `references/source-prompts.md` - the adapted original prompts from the article
- `assets/learnings-note-template.md` - the atomized note format used by VAULT and RECORDER
