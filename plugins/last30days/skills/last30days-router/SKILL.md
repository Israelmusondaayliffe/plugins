---
name: last30days-router
description: Route multi-stage recent-signal work across last30days research, comparisons, trend discovery, source diagnostics, watchlists, and briefings. Use when a request spans more than one last30days workflow, asks what the plugin can do, or does not clearly identify the right focused workflow.
---

# Last30days Router

## Route the request

Choose the smallest workflow that completes the request:

- Fresh topic research, recommendations, community sentiment, competitor comparisons, trend discovery, saved-library search, HTML briefs, or freshness verification: read `../last30days/SKILL.md` completely and follow its contract.
- Setup, permissions, missing sources, runtime problems, or a post-run failure: read `../last30days-health/SKILL.md` and follow it.
- Add, inspect, run, or remove monitored topics: read `../last30days-watchlist/SKILL.md` and follow it.
- Generate or retrieve a daily or weekly summary from monitored findings: read `../last30days-briefing/SKILL.md` and follow it.

For a compound request, use this order when applicable: health check, research, watchlist update, briefing. Do not run a broad health check when the requested research can proceed normally.

## Safety boundary

The bundled engine can call external services, read browser cookies after consent, install optional command-line tools during setup, write local research data, publish public HTML, and send watchlist output to configured webhooks.

- You may run `--preflight`, `--diagnose`, and read-only list/show commands without extra confirmation.
- Get explicit user approval before reading browser cookies, saving credentials, publishing HTML, configuring or sending to a webhook, or installing optional setup tools.
- Never print secrets, cookie values, API keys, or unmasked credentials.
- Explain the destination before creating local watchlist, briefing, library, or report files.

## Completion standard

Report the query window, sources that actually returned evidence, partial or failed source coverage, saved artifact paths, and any user action still required. Do not describe a source as quiet when it failed, timed out, or was not configured.
