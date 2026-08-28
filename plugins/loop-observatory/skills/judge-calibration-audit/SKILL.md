---
name: judge-calibration-audit
description: Detect false passes, false failures, escalation clusters, and repeated disagreement between loop judges and later human labels. Use when evaluating judge quality or ground-truth problems. Do not repair judges or alter run records.
---

# Judge Calibration Audit

Run `python3 ../../scripts/loop_observatory.py audit`. A false pass requires a positive machine verdict and a negative human label. A false failure requires the reverse. Keep unlabeled runs outside disagreement rates. Prefer `loopkit:loop-doctor`, `operating-graph:graph-debug`, or Agent Ops for repair. If none is installed, run `python3 ../../scripts/loop_observatory.py repair-handoff RECORD_ID` and return the unresolved handoff. Do not claim a repair occurred.
