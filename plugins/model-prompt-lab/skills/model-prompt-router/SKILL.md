---
name: model-prompt-router
description: Route production prompting, migration, diagnosis and benchmark design for GPT 6 Astra, Fable 5.1 and older model compatibility. Use when the model, prompt surface, effort or operation is unclear. Verify current model guidance before handoff.
---

# Model Prompt Router

## Overview

Choose the model and operation before loading a large model-specific prompt skill. Current model facts come from the owning documentation, not from an older prompt template.

## Workflow

1. Extract the user job, target model, prompt surface, available tools, output contract, latency or cost constraints, and any source prompt.
2. Check current documentation when model availability, parameters, tool behavior, or limits affect the result.
3. Choose one primary route with references/workflow.md.
4. Fill assets/output-template.json and run scripts/validate_output.py.
5. Hand off generation or diagnosis to the selected model-specific prompter. Use prompt-benchmark-designer for eval design and prompt-migration-audit for migrations.
6. Return the prompt in its own code block when the prompt itself is the deliverable.

## Error Handling

- If the requested model cannot be verified, label the route provisional and do not invent parameters.
- If the user names an unsupported model or surface, preserve the job and recommend the nearest verified route.
- If two routes apply, choose a primary route and name the second as a follow-up.

## Reliability Notes

The model interprets the prompt job and chooses the route. The validator enforces an allowed route, an explicit target model, and a source-check decision.

## Resources

- scripts/validate_output.py validates the structured artifact.
- references/workflow.md defines routing and decision rules.
- assets/output-template.json is the reusable output template.
- assets/output-schema.json is the deterministic validation contract.

## Current model routes

For GPT-6 Astra, load `../gpt-6-astra-production-prompter/SKILL.md`. For Claude Fable 5.1, load `../fable-5-1-production-prompter/SKILL.md`. Keep GPT-5.6, GPT-5.4 and Fable 5 routes for explicitly selected compatibility work. Confirm runtime availability in the selected host; do not silently substitute a different model.
