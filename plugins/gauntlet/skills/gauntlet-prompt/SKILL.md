---
name: gauntlet-prompt
description: Loads only when a gauntlet brief exists and the user explicitly asks for the gauntlet prompt or the gauntlet loop prompt to paste into Claude Code. Turns a completed gauntlet brief into a short lead-agent prompt, lints it with the plugin's prompt linter, writes it to prompt.md, and surfaces it in a single fenced code block. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Gauntlet prompt

Turn a completed brief into the prompt the lead agent runs on. Precondition: a run directory exists with status `briefed`. If there is no brief, route back to `gauntlet-brief`; never draft a gauntlet prompt from conversation alone.

## The design rule that decides whether this plugin works

**The output prompt is short.** Prescribing architecture replaces the model's judgment with yours. The brief holds the detail; the prompt holds the contract. Everything the lead agent needs beyond the contract lives in the run directory, and the prompt points there instead of restating it. Enforce shortness with the linter, not with taste.

Start from `assets/prompt-template.md` in this skill. Fill its placeholders from `run.json`, `PLAN.md`, and `bar/bar.md`. Do not add sections the template does not have. For the common ways prompts go wrong, with before and after pairs, read `references/prompt-antipatterns.md` before drafting.

## Required clauses

Every gauntlet prompt contains all nine. No substitutes, no omissions.

```
the goal
the bar, with real paths
split into the smallest independently judgeable pieces
builder plus separate critic with fresh context
blind comparison where possible
loop until it wins or the user stops
maintain the live progress page
write state to the named run directory
use subagents and the highest effort setting
```

For knowledge-work domains (`prose`, `research`, `strategy`, `deck`, `prompt-system`), the prompt must also require the reader-proxy inspection against the frozen question sets and the claim ledger validated by `claim_audit.py`.

## Lint before surfacing

Run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_prompt.py --run-dir <path to .gauntlet/runs/<run-id>>
```

`lint_prompt.py` fails the prompt when it:

- exceeds 600 words, warns above 400
- prescribes architecture, file layout, module lists, or a tech stack the user did not specify
- fixes a round count
- omits any required clause above
- omits the effort and subagent instruction
- for knowledge-work domains, omits the reader-proxy and claim-ledger requirements

A failed lint blocks the stage. Fix the prompt and re-lint; never surface a prompt the linter rejected, and never argue with the linter. The script decides, not the model.

## Output

Write the linted prompt to `prompt.md` in the run directory and set `status` to `prompted`. Surface it to the user in one fenced code block containing nothing but the prompt: no preamble inside the block, no commentary inside the block, no second block.

## Platform facts

Verified 2026-07-29 per `docs/BUILD-NOTES.md`: the Claude Code effort ladder is `low / medium / high / xhigh / max`, and `ultracode` is the current multi-agent opt-in token, so the effort clause fills from the top of that ladder and uses `ultracode` where multi-agent mode needs opting in. The built-in `/loop` surface exists for interval pacing, but `gauntlet-run` owns gauntlet iteration because the round loop is a deterministic state machine driven from disk state, not an interval poll. `/loop` may optionally re-invoke `gauntlet-run` across long unattended stretches; it never replaces it, and the prompt must not delegate the round loop to it.
