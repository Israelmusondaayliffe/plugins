# Matt Partok Bundled Plugin For Knowledge Work

> Deprecated compatibility release. The bundle remains installable for this release so existing users can migrate. New work should use the destination plugins below. Removal requires a later, separately approved release.

This plugin adapts Matt Pocock's promoted skills workflow for Codex, software
delivery, and general knowledge work. It preserves the original sequence of
clarifying an idea, recording decisions, researching or prototyping unknowns,
writing a specification, splitting large work into bounded slices, executing,
handing off, and reviewing against evidence.

The requested plugin title uses "Partok." The upstream author and attribution
use Matt Pocock's correct name.

## Install

    codex plugin add matt-partok-bundled-plugin-for-knowledge-work@community-agent-plugins

Start a new Codex task after installation so the skills enter the task
capability inventory.

## Migration table

| Legacy skills | Replacement | Replacement prompt |
|---|---|---|
| `matt-grilling`, `matt-grill-me`, `matt-grill-with-docs`, `matt-domain-modeling` | Strategy Room, Outcome Engine, or Harness Engineering | `Grill me on this decision`, `Run Outcome Engine and clarify this brief`, or `Grill me about my harness setup` |
| `matt-wayfinder` | `strategy-room:decision-wayfinder` | `Wayfind this large uncertain effort` |
| `matt-to-spec`, `matt-to-tickets`, `matt-prototype`, `matt-triage`, `matt-implement` | Outcome Engine | `Turn this settled conversation into an outcome brief`, `Break this approved brief into action slices`, or `Prototype the riskiest assumption with a bounded test` |
| `matt-research` | `knowledge-work-superpowers:systematic-research` | `Run bounded research for this decision` |
| `matt-handoff` | `continuity-vault:continuity-router` | `Create a durable handoff for a fresh task` |
| `matt-writing-great-skills` | `capability-operator:skill-creator-pro` | `Improve this skill writing and validate its behavior cases` |
| `matt-code-review`, `matt-codebase-design`, `matt-diagnosing-bugs`, `matt-improve-codebase-architecture`, `matt-tdd`, `matt-resolving-merge-conflicts` | `web-product-studio:code-production-agent` | `Use TDD for this change`, `Diagnose this hard bug`, `Review this code against the spec`, or `Resolve these merge conflicts` |
| `matt-teach` | No public successor in this migration | Keep this compatibility skill or install a teaching skill separately |
| `matt-ask-matt`, `matt-setup-matt-pocock-skills` | Retired routing and setup | Invoke the destination plugin directly |

No replacement preserves a `$matt-*` alias. Migrate prompts now while this compatibility release remains available.

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
