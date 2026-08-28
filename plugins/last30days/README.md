# Last30Days

Last30Days researches recent social, community, market, code, and web signals on Codex, Claude Code, and Claude Cowork. The package combines the pinned v3.16.0 research engine with local routing, diagnostics, watchlists, and briefings.

## Workflows

- `last30days-router`: choose research, health, watchlist, or briefing work
- `last30days`: run recent research, comparisons, discovery, and recommendations
- `last30days-health`: inspect runtime, permissions, credentials, and source coverage
- `last30days-watchlist`: manage recurring topics and deltas
- `last30days-briefing`: generate daily or weekly summaries from stored findings

The plugin does not require another catalog plugin. External sources, credentials, optional command-line tools, and browser-cookie access remain conditional on the selected workflow and its approval rules.

## Frozen engine boundary

The payload under `skills/last30days/**` is the pinned v3.16.0-derived engine recorded in `NOTICE.md`. The root launchers and four wrapper skills are the public adapter. Do not treat the older copy inside Founder Revenue Engine as the source for this package.

## Safety

Read-only preflight and diagnostics are safe starting points. Ask before browser-cookie access, credential writes, optional tool installation, webhook delivery, or public HTML publication. Standard research does not publish without an explicit publish option.

## Validate

```bash
python3 -m unittest discover -s tests -v
bash scripts/run_last30days.sh --help
bash scripts/run_last30days.sh --preflight --no-browser-cookies
```
