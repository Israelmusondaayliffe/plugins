# AI Film Studio

Public plugin, version 0.2.0. The Codex manifest is [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json); it declares skills only, with no MCP server, hooks, or app surface. The Claude manifest is [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

AI Film Studio is an explicit-only planning system for a film project. It takes a filmmaker from a film-specific concept through records, production design, assets, performance, geography, shots, model routing, iteration, post-production planning, delivery preparation, and learning capture.

It does not automatically activate for filmmaking language. Use `$ai-film-studio:ai-film-studio`, `Use AI Film Studio`, `$ai-film-studio:film-advisor`, or `Use Film Advisor` to start an owned front door. Quoted, negated, conditional, incidental, or ordinary mentions do not activate it.

The plugin neither publishes work nor performs live generation, sign-in, uploads, purchases, destructive replacement, or external delivery without separate explicit approval. Its Film Advisor protocol is independent from Agent Ops Sol Advisor.

## Boundaries

- The bundled film-specific grill and decision record cover the full local concept workflow. Strategy Room is an optional companion for a broader decision interview.
- The bundled film records cover the local brief and evidence workflow. Outcome Engine is an optional companion for general outcome contracts.
- The plugin includes its own bundle validator. Harness Engineering is an optional companion for broader plugin lifecycle work.
- Installation and catalog governance stay outside this package. Capability Operator may handle them when available.
- This plugin always returns a complete model-neutral shot packet. `video-production-studio:video-prompt-builder` is an optional formatter for model-specific surface syntax.
- Model profiles are decision contracts, not live capability claims. Confirm a selected surface before execution.

## Local validation

```bash
python3 scripts/validate_bundle.py .
python3 -m unittest discover -s tests -v
```

The plugin contains only generalized, original production doctrine. See [source attribution](references/source-attribution.md) for its limits.
