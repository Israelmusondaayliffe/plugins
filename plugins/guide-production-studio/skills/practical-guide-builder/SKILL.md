---
name: practical-guide-builder
description: Write or rebuild an approved practical guide from a validated contract. Use when the guide needs plain-language context, exact actions, real examples, reusable prompts or templates, troubleshooting, and visual evidence. Do not invent unsupported material or publish.
metadata:
  author: Community Maintainers
  version: 0.1.1
---

# Practical Guide Builder

Write for an intelligent person who wants to do the work. Explain enough to make the action meaningful, then give them something real to try.

## Prerequisite

Require a validated guide contract with accepted architecture. Load the provenance, architecture, and visual references named by that contract.

## Build order

1. **Open with the reader's job.** Say what the guide helps them do, when it is useful, and what they need before starting.
2. **Define the idea.** Explain unfamiliar terms the first time they appear. Use plain language without making the subject shallow.
3. **Show the whole shape.** Give a short mental model before detailed steps so the reader knows where they are going.
4. **Give one action per step.** State the input, action, expected result, and why the step matters when the reason changes judgment.
5. **Use real evidence.** Prefer rights-safe, tested examples and actual outputs. Preserve permitted public provenance beside the teaching it supports.
6. **Label limits where they occur.** Mark planning-only, unrun, version-sensitive, practitioner, or user-supplied material near the relevant instruction.
7. **Make prompts usable.** Explain when to use a prompt, what to provide, what it returns, what it cannot decide, and how to judge the result.
8. **Show before offering blanks.** Place a completed example before a template. Omit the template when copying is not genuinely useful.
9. **Teach failure recognition.** Connect visible symptoms to likely causes, protected elements, smallest next action, and stop conditions.
10. **Teach visually when the judgment is visual.** Use comparisons, crops, frames, diagrams, or annotated examples that the reader can inspect.
11. **Serve returning experts.** Make exact prompts, settings, decision rules, sources, and reference tables easy to find without weakening the beginner path.
12. **Remove internal language.** Public copy contains no model instructions outside copy-ready prompts, plugin names, paths, ledgers, validators, receipts, routing notes, or publication commentary.

## Writing standard

- Use ELI5 clarity for an intelligent adult.
- Keep context, intent, value, quality, and voice visible.
- Write short, direct sentences without reducing the depth.
- Avoid course, lesson, assignment, instructor, and module framing unless the user explicitly asks for education packaging.
- Avoid biography and self-promotion unless the source subject genuinely requires it.
- Avoid fake first-person experience.
- Prefer an opinionated craft recommendation only when evidence or tested practice supports it.

## Checks before handoff

Run the public-output scanner:

```text
python3 ../guide-production-router/scripts/validate_public_guide.py GUIDE.md
```

Then return the candidate to the router for independent review. Do not call it approved, publish it, or launch sibling guides.
