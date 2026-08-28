---
name: capability-repair-cycle
description: Use when a failed skill or plugin eval needs the smallest candidate repair tested against the full suite. Edits an isolated copy and promotes only after a passing receipt and explicit approval.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Capability Repair Cycle

1. Require a failed or needs-review receipt with specific evidence.
2. Stage the source with `python3 scripts/skill_eval_loop.py stage TARGET`.
3. Use the target's own instructions for the smallest candidate change. Skill Creator Pro or another target owner may advise when available.
4. Change only the smallest surface connected to the failure.
5. Re-run the full suite against the staged path.
6. Stop if the failure signature repeats, limits are exhausted, or another case regresses.
7. Ask for explicit approval only after the candidate receipt passes.
8. Pin the passing candidate run, then promote with the exact staged path, passing run ID, approval token, and expected source fingerprint.

Promotion creates a state-root backup before replacing source contents. It refuses stale fingerprints.
