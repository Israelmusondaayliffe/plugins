---
name: gauntlet-evidence
description: Loads only when a gauntlet verification consensus exists on disk and the user explicitly asks for the gauntlet report, the gauntlet evidence report, or the receipts for a gauntlet run. Assembles EVIDENCE.md and EVIDENCE.json entirely from state files via script, with every number, path, command, and hash read from disk and never computed by the model. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Community Maintainers
  version: 0.2.0
---

# Gauntlet evidence

Report with receipts. This skill runs only after `gauntlet-verify` has written a consensus, and only when that consensus is `verified` or `verified-with-dissent`. If no consensus exists, route to `gauntlet-verify`; if the consensus is `failed` or `unverifiable`, route back to `gauntlet-run`. There is no path from an unverified run to a report.

## The hard constraint

Every number, path, command, and hash in the report is read from a file in `.gauntlet/`. This skill may not compute, estimate, recall, or infer any of them. Not a round count, not an exit code, not a hash, not a wall-clock figure. Assembly happens through the scripts:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hash_artifacts.py --run-dir <path to .gauntlet/runs/<run-id>>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_report.py --run-dir <path to .gauntlet/runs/<run-id>>
```

`hash_artifacts.py` produces the SHA-256 of every artifact file at report time. `build_report.py` assembles `EVIDENCE.md` and `EVIDENCE.json` from state and fails loudly on missing values. If a value is genuinely absent from state, the report prints `not recorded` in its place, and every `not recorded` printed anywhere in the report is itself listed in section 7. Unknown is never estimated (INV-5, and the `cost.json` rule: `unknown` is written as `unknown`).

The model's only jobs here are to run the scripts, surface the result, and refuse to decorate it.

## Fixed section order

Nine sections, this order, no additions, no omissions. The structure is `assets/evidence-report-template.md` in this skill.

1. **Verdict.** One line, the consensus value verbatim from `consensus.json`. No softening, no upgrading. `verified-with-dissent` is not shortened to "verified". `capped` is never presented as done (INV-7). If the run recorded degraded mode, the degraded-mode banner appears here.
2. **Goal and bar.** What was asked, what it was measured against, why that bar is fair. Plan hash and whether it matched.
3. **Per-piece table.** Piece, rounds, final blind result, quality votes, integrity votes, consensus, artifact path.
4. **Re-run the checks.** Every inspection command with its exit code, copy-pasteable.
5. **Claim audit summary.** Claim count, unsupported count, citation ratio, unreachable sources, per knowledge-work piece.
6. **Artifact integrity.** SHA-256 of every artifact file at report time, from `hash_artifacts.py`.
7. **What was not verified.** Mandatory, never omitted, never empty by silence. Every `cannot-verify`, every capped piece, every skipped inspection, every part of the goal that never became a piece, and every `not recorded` value printed anywhere in this report.
8. **Known remaining gaps.** The last `gap.md` of every non-converged piece, verbatim.
9. **Budget spent.** Rounds, subagents, sessions, wall clock, cost ledger, target changes, support artifacts, stop reason.

## EVIDENCE.json parity

`EVIDENCE.json` carries the same content as `EVIDENCE.md`, machine-readably. Both are written by `build_report.py` in the same pass. They may never disagree; if one is regenerated, both are.

## Verdict fidelity

The verdict line is the consensus value, verbatim. Dissent recorded in `consensus.json` is preserved verbatim, not summarized into agreement. A report that upgrades `verified-with-dissent`, hides a `cannot-verify`, or narrates a capped run as complete is the exact failure this plugin exists to prevent: a confident completion report from an unverified run is worse than no report at all.

## Degraded-mode banner rule

If `run.json` records `"context_isolation": "degraded"` or `"execution": "degraded"`, the report opens with a banner in section 1 naming the degradation and what it weakened. The banner is not optional, not removable when the results look good, and appears on every report the run ever produces.
