---
name: harness-maintainer
description: Audit and update an existing harness after model changes, platform releases of Claude Code, Cowork, or Codex, plugin updates, repeated corrections, stale instructions, failed automations, or capability drift. Use for weekly, monthly, or quarterly harness reviews, model-jump audits, obsolete-skill removal, routing parity checks, maintenance planning, safe in-place upgrades, and conservative cleanup of stale Claude Code cache, archived session logs, temporary data, shell snapshots, and inactive plugin cache versions via the bundled guarded cleanup script.
---

# Harness Maintainer

Treat maintenance as a new audit and plan. Do not assume the previous harness state is current, and do not assume the platform still behaves the way the platform reference file describes; those files carry a verification date and go stale.

## Cadence

- Weekly: review outputs, run stops, automation and scheduled-task results, failed checks, and repeated corrections.
- Monthly: review instruction chains, memory staleness, plugin and skill use, hooks or validators, and output hygiene.
- Quarterly or after major platform changes: re-verify official platform behavior against the platform reference files, model-specific prompt blocks, connectors, optional capability bundles, discovery, and security boundaries. Update the platform files when reality has moved.

## Workflow

1. Run the harness's deterministic check script if one exists; its failures are the first work items. Then run `harness-audit` against fresh state.
2. Compare current behavior with the last verified receipt.
3. Classify drift as user change, product change, broken dependency, stale policy, or missing enforcement.
4. Remove dead weight before adding new instructions. After a model generation change, run `context-doctor` across the whole chain and treat instructions written for the previous generation as removable until a regression proves otherwise.
5. Promote any correction or finding class seen twice into the harness's deterministic check script rather than into more instructions, when it is deterministically checkable.
6. Produce a reversible update plan and approval groups.
7. Run the standard build and verification phases.

Follow `../../references/model-change-policy.md` after every major model change.

## Stale-data cleanup

This skill owns conservative cleanup of stale Claude Code data through the bundled
script `../../scripts/harness_cleanup.py`. The script is the only sanctioned deletion
path; never delete harness storage by hand or with ad-hoc shell commands.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/harness_cleanup.py"           # dry-run (default)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/harness_cleanup.py" --apply   # guarded deletion
```

Contract, enforced by the script and its tests:

- Fail-closed allowlist. Only four categories are ever candidates: archived session
  transcripts older than 90 days, disposable cache files older than 14 days, shell
  snapshots older than 30 days, and inactive plugin cache versions older than 30 days.
- Dry-run is the default; mutation requires an explicit `--apply`.
- The Claude home is discovered (`$CLAUDE_CONFIG_DIR`, else `~/.claude`), never assumed
  from a username, and broad roots, repo roots, symlinked or unmarked directories are
  refused.
- A single-run lock, symlink rejection, open-file (`lsof`) and process-ownership checks,
  protection of installed plugin versions and memory-referenced paths, and hard ceilings
  (10,000 candidates / 2 GiB) all run before any deletion. Retention thresholds can only
  be raised from the CLI and ceilings only lowered; the conservative defaults are floor
  and cap.
- Every run writes an atomic JSON receipt (default `<home>/cleanup-receipts/`) with
  candidates, deletions, skips, safety checks, warnings, stop reasons, thresholds,
  timestamps, and tool version. Any safety failure or incomplete receipt exits nonzero.

Interpret results for the user: exit 0 with zero candidates is a healthy no-op; exit 2
is a deliberate safety stop that needs human review, not a retry with loosened limits.
