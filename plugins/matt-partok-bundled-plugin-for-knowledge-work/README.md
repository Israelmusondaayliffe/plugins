# Matt Partok Bundled Plugin For Knowledge Work

This plugin adapts Matt Pocock's promoted skills workflow for Codex, software
delivery, and general knowledge work. It preserves the original sequence of
clarifying an idea, recording decisions, researching or prototyping unknowns,
writing a specification, splitting large work into bounded slices, executing,
handing off, and reviewing against evidence.

The requested plugin title uses "Partok." The upstream author and attribution
use Matt Pocock's correct name.

## Install

    codex plugin add matt-partok-bundled-plugin-for-knowledge-work@israel-plugins

Start a new Codex task after installation so the skills enter the task
capability inventory.

## Main flow

1. Use `matt-ask-matt` to choose the smallest useful workflow.
2. Use `matt-grill-me` or `matt-grill-with-docs` to settle open decisions.
3. Use `matt-research` or `matt-prototype` only when discussion cannot answer a
   question reliably.
4. For one bounded session, proceed to `matt-implement` and verification.
5. For multi-session work, use `matt-to-spec`, then `matt-to-tickets`.
6. Use `matt-handoff` when a fresh thread needs durable state.
7. Finish with `matt-code-review` for software or the relevant evidence checks
   for knowledge work.

## Included skills

- `matt-ask-matt`
- `matt-code-review`
- `matt-codebase-design`
- `matt-diagnosing-bugs`
- `matt-domain-modeling`
- `matt-grill-me`
- `matt-grill-with-docs`
- `matt-grilling`
- `matt-handoff`
- `matt-implement`
- `matt-improve-codebase-architecture`
- `matt-prototype`
- `matt-research`
- `matt-resolving-merge-conflicts`
- `matt-setup-matt-pocock-skills`
- `matt-tdd`
- `matt-teach`
- `matt-to-spec`
- `matt-to-tickets`
- `matt-triage`
- `matt-wayfinder`
- `matt-writing-great-skills`

## Verification

Run the package checks from this directory:

```bash
python3 scripts/verify_bundle.py
python3 -m unittest tests/test_verify_bundle.py
```

See `NOTICE.md` and `LICENSE` for upstream attribution and licensing.
