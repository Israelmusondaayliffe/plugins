---
name: harness-maintainer
description: Audit and update an existing harness after model changes, platform releases of Claude Code, Cowork, or Codex, plugin updates, repeated corrections, stale instructions, failed automations, or capability drift. Use for weekly, monthly, or quarterly harness reviews, model-jump audits, obsolete-skill removal, routing parity checks, maintenance planning, and safe in-place upgrades.
---

# Harness Maintainer

Treat maintenance as a new audit and plan. Do not assume the previous harness state is current, and do not assume the platform still behaves the way the platform reference file describes; those files carry a verification date and go stale.

## Cadence

- Weekly: review outputs, run stops, automation and scheduled-task results, failed checks, and repeated corrections.
- Monthly: review instruction chains, memory staleness, plugin and skill use, hooks or validators, and output hygiene.
- Quarterly or after major platform changes: re-verify official platform behavior against the platform reference files, model-specific prompt blocks, connectors, optional capability bundles, discovery, and security boundaries. Update the platform files when reality has moved.

## Workflow

1. Run `harness-audit` against fresh state.
2. Compare current behavior with the last verified receipt.
3. Classify drift as user change, product change, broken dependency, stale policy, or missing enforcement.
4. Remove dead weight before adding new instructions. After a model generation change, run `context-doctor` across the whole chain and treat instructions written for the previous generation as removable until a regression proves otherwise.
5. Produce a reversible update plan and approval groups.
6. Run the standard build and verification phases.

Follow `../../references/model-change-policy.md` after every major model change.
