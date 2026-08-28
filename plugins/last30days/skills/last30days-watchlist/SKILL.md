---
name: last30days-watchlist
description: Manage recurring last30days topic monitoring, run stored topics, inspect deltas, set budgets, and configure optional delivery. Use for watchlists, ongoing social listening, change detection, scheduled topic research, or monitored competitor signals.
---

# Last30days Watchlist

Set `SKILL_DIR` to the directory containing this file. The watchlist runner is at `$SKILL_DIR/../../scripts/run_watchlist.sh`.

## Commands

```bash
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" list
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" add "TOPIC" --schedule daily
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" add "TOPIC" --weekly
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" delta "TOPIC"
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" run-one "TOPIC"
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" run-all
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" remove "TOPIC"
bash "$SKILL_DIR/../../scripts/run_watchlist.sh" config budget "VALUE"
```

Use `list` before changing an existing watchlist. Confirm the exact topic before remove. Explain that add, remove, run, and config commands update the local last30days SQLite store.

Delivery configuration can send results to an external HTTPS webhook. Treat webhook configuration and delivery as an external side effect. Show the destination host and get explicit approval before running `config delivery` or any command that sends data.

After a run, report new findings first, then changed engagement or source coverage, then unchanged status. Name failures and partial coverage separately from a true zero-result delta.
