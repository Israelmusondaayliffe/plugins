# Three example tasks

These prompts are adapted from real work patterns. They are reusable demonstrations, not claims that this public version produced the original work. Provide the stated inputs before running each example.

## 1. Review workshop prose without editing it

Inputs: Provide the draft pages you want reviewed.

```text
Use writing-quality:writing-enforcer in DETECT mode on these workshop drafts. Find generic phrasing, filler and shifts away from my supplied voice. Quote each problem and suggest a specific repair. Keep code blocks, quotations and exact prompts protected. Return findings only; do not edit the drafts.
```

Expected result: A short findings list tied to the supplied passages; the source drafts remain unchanged.

## 2. Rewrite a guide in its author's voice

Inputs: Provide the draft plus a paragraph you wrote that represents your voice.

```text
Use writing-quality:writing-quality-router to revise this guide in my first-person voice. Use my sample paragraph for tone. Preserve the explanations and sequence. Do not invent experiences, opinions or results. Leave quoted prompts and code blocks unchanged. Return the revised guide.
```

Expected result: A coherent first-person revision that preserves the supplied meaning and protected blocks.

## 3. Write a concise team announcement

Inputs: Provide the workshop and companion-site links.

```text
Use writing-quality:business-writing-intent-enforcer to write a concise WhatsApp message asking my team to review the updated workshop and companion site. Include both links with clear labels. Do not list every change or invent a deadline. Give me only the message in a code block.
```

Expected result: A brief message ready to copy, with both supplied links intact.
