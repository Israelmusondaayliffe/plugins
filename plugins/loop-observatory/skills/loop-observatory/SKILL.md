---
name: loop-observatory
description: Route read-only cross-loop telemetry work. Use when the user asks to ingest LoopKit or registered Operating Graph runs, compare loop performance across versions or time, calculate acceptance metrics, identify limit exhaustion, or audit judge calibration. Do not use to design, execute, schedule, or directly repair one loop.
---

# Loop Observatory

Use this Tier 3 front door for multi-stage observability work.

1. Read `../../references/ownership-and-sources.md`.
2. For ingestion, read `../loop-run-ingestor/SKILL.md` and `agents/agent-ingest.md`.
3. For comparisons, read `../loop-portfolio-report/SKILL.md` and `agents/agent-report.md`.
4. For verdict analysis, read `../judge-calibration-audit/SKILL.md` and `agents/agent-audit.md`.
5. Keep source runs read-only and preserve missing evidence as unknown.
6. Prefer the capability that owns an individual repair. If no named companion is installed, return the local generic repair handoff and keep the result unresolved.

Use `python3 ../../scripts/loop_observatory.py --help` for the local deterministic interface.
