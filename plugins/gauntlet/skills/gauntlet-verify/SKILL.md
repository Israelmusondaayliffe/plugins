---
name: gauntlet-verify
description: Loads only when the user explicitly asks to verify the gauntlet, asks whether a gauntlet run is actually done, or when a gauntlet run has reached a stopped or converged state with no consensus on disk. Spawns independent quality and integrity verifiers that never saw the build, collects their verdicts to disk, and computes consensus by script. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.
metadata:
  author: Israel Ayliffe
  version: 0.1.0
---

# Gauntlet verify

Independent verification of a stopped or converged run. Convergence is a critic outcome, not a verdict. This skill answers "is it actually done" with agents that never saw the build, and it is the only path to the evidence report. A doneness question always comes here first, never to the report.

## Rules

- **Two verifier types, always both.** Quality verifiers judge the artifact against the bar and the acceptance criterion. Integrity verifiers judge whether the artifact is honest and functional (INV-4). A piece verified by only one type has not been verified.
- **N per type, default 3, minimum 2.** Odd numbers preferred, so a majority exists. The per-piece counts come from the `verifiers` field in `pieces.json`, set at brief time.
- **Exact inputs, nothing else.** Each verifier receives: the goal from `CONTEXT.md`, the success criteria from `PLAN.md`, the bar, the acceptance criterion for the piece, the artifact, and the inspection output. Nothing else. No round history, no critic verdicts, no builder notes, no other verifier's result, no path into `.gauntlet/sealed/`. Success criteria come from `PLAN.md`, never from later state.
- **Parallel but never shared.** Verifiers may run in parallel, but they must not share context. Each is its own clean-context spawn seeded only from the input list above.
- **`cannot-verify` is a first-class outcome.** It must survive into consensus and into the report. Missing inspection output, an unreachable source, an absent artifact, a moved rubric, or a plan hash mismatch all produce it. Absence of evidence is never a pass (INV-5).
- **Plan hash first.** Every verifier checks `plan_hash_matched` before anything else. A mismatch is reported and the result is `cannot-verify` regardless of what the artifact looks like. Success criteria or a rubric edited mid-run is an integrity failure, not a refinement.

## Integrity verifier mandate

Claims traced to reachable sources that say what is claimed. Commands ran and tests executed. Stated constraints hold. Rubric and success criteria unmoved. No stubs, no dead paths, no placeholder assets. Existence of files is not evidence of work. A plausible summary is not evidence of anything.

## Procedure per piece

1. Confirm the piece is eligible: run status is `stopped` or `converged` (or the user asked whether it is done), and no `consensus.json` exists yet for the piece.
2. For knowledge-work pieces with a claim ledger, refresh the audit first so verifiers judge current reachability:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/claim_audit.py --run-dir <path to .gauntlet/runs/<run-id>> --piece <piece-id>
   ```

3. Spawn N quality verifiers from `${CLAUDE_PLUGIN_ROOT}/agents/quality-verifier.md` and N integrity verifiers from `${CLAUDE_PLUGIN_ROOT}/agents/integrity-verifier.md`, each in fresh context, each given the exact input list above and nothing else. See `references/verification-independence.md` in this skill for what the spawning layer must enforce versus what is instructional, and for degraded-mode semantics.
4. Write each verdict per the SPEC 8.6 shape into `verification/<piece>/` under the run directory: `quality-1.json` through `quality-N.json` and `integrity-1.json` through `integrity-N.json`. Fields: `piece_id`, `verifier_type` (`quality` or `integrity`), `verifier_index`, `result` (`pass`, `fail`, or `cannot-verify`), `criterion_applied`, `evidence_inspected`, `reason`, `plan_hash_matched`. No other result values exist.
5. Compute consensus. Only the script does this, never a model:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/consensus.py --run-dir <path to .gauntlet/runs/<run-id>> --piece <piece-id>
   ```

   It writes `verification/<piece>/consensus.json`. Do not paraphrase, recount, or override its output.

## Consensus table

Applied by `consensus.py`, first matching condition wins:

| Condition | Consensus |
|---|---|
| Any integrity fail | `failed`, regardless of quality votes |
| Any `cannot-verify`, either type | `unverifiable` |
| All pass, both types | `verified` |
| Majority quality pass with dissent, no integrity fail, no cannot-verify | `verified-with-dissent`, dissent preserved verbatim |
| Majority quality fail | `failed`, gaps unioned |

## Routing after consensus

- `verified` or `verified-with-dissent`: the run may proceed to `gauntlet-evidence`. Dissent travels with it, verbatim.
- `failed` or `unverifiable`: route back to `gauntlet-run` with the verifier reasons as new work. Never forward to the report. There is no wording of a failed or unverifiable consensus that reaches `gauntlet-evidence`.
