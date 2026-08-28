---
name: loop-portfolio-report
description: Use when normalized loop outcomes must be compared across engines, versions, models, or time periods, including acceptance, exhaustion, duration, stop reasons, and evidenced cost. Requires ingested runs and keeps missing data unknown.
---

# Loop Portfolio Report

Run `python3 ../../scripts/loop_observatory.py report`. Produce both JSON and Markdown. Calculate acceptance rate only from known human labels. Calculate cost per accepted result only when accepted runs have known cost evidence. For scheduled use, return no-op when there are no newly ingested terminal runs.
