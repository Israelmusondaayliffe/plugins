---
name: model-prompt-engineer
description: Create, migrate, or test prompts used by a harness while adapting to the selected current model and prompt surface, Anthropic models for Claude Code and Cowork harnesses, OpenAI models for Codex harnesses. Use for global instruction prompts, autonomous-run prompts, verification prompts, API system prompts, model migrations, prompt regressions, or requests to support the latest model without freezing the harness to one model generation.
---

# Model Prompt Engineer

Keep stable user policy separate from temporary model compensation.

## Workflow

1. Classify the prompt surface: thread, instruction file (CLAUDE.md, contract file, or AGENTS.md), skill, autonomous run (Goal, scheduled task, or headless run), API system prompt, or builder surface.
2. Preserve an explicitly named target model.
3. If the user requests latest, current, or default, verify current guidance from the vendor's official documentation for the resolved platform's model family before selecting or rewriting.
4. Load an installed model-specific prompting skill when one exists and is visible; prefer the namespaced plugin copy.
5. State the outcome, necessary context, constraints, authority, output contract, and completion evidence once each.
6. Remove duplicate reminders and obsolete workarounds.
7. Test representative success, ambiguity, approval, tool-routing, formatting, and stop cases.
8. Run each case more than once at fixed model, effort, tool, and scorer conditions.
9. Subtract one coherent prompt group at a time. Restore any critical, category, or overall regression.
10. Record model-specific blocks as provisional.

Follow `../../references/model-change-policy.md`. Never invent a model name, parameter, price, or availability claim.
For universal context changes, also follow `../../references/frontier-first-prompt-governance.md`.
