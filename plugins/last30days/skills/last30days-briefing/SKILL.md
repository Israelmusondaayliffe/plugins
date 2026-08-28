---
name: last30days-briefing
description: Generate or retrieve daily and weekly briefings from stored last30days watchlist findings. Use for morning research briefs, weekly recent-signal summaries, monitored-topic recaps, and concise updates from the local watchlist store.
---

# Last30days Briefing

Set `SKILL_DIR` to the directory containing this file. The briefing runner is at `$SKILL_DIR/../../scripts/run_briefing.sh`.

## Commands

```bash
bash "$SKILL_DIR/../../scripts/run_briefing.sh" generate
bash "$SKILL_DIR/../../scripts/run_briefing.sh" generate --since YYYY-MM-DD
bash "$SKILL_DIR/../../scripts/run_briefing.sh" generate --weekly
bash "$SKILL_DIR/../../scripts/run_briefing.sh" show
bash "$SKILL_DIR/../../scripts/run_briefing.sh" show --date YYYY-MM-DD
```

Generation reads the local watchlist database and saves structured briefing data under `~/.local/share/last30days/briefs/`. State that destination before generating a new briefing.

Present the result in this order:

1. Important new findings and notable engagement changes.
2. Topics with failed, stale, or partial collection.
3. Coverage and cost summary.
4. Topics with no meaningful change, compressed into one short line.

Do not claim a topic was quiet when its last run failed or its sources were unavailable. If no topics exist, route the user to `last30days-watchlist` instead of fabricating a briefing.
