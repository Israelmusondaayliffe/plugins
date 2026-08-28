---
name: approved-practice-handoff
description: Use when an explicitly approved Practice Compiler proposal needs a skill-eval, skill-creation, harness, continuity, or content-workflow handoff. Routes to the existing owner, produces a handoff file only, and never applies the change.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Approved Practice Handoff

1. Require an approval entry for the proposal ID.
2. Read the generated handoff under the Practice Compiler state root.
3. Treat the destination owner in `references/ownership-and-routing.md` as preferred, not required.
4. Select a preferred owner only when the caller confirms that owner is available.
5. Otherwise keep the owner unassigned and return the complete generic handoff.
6. Include proposal ID, redacted evidence references, occurrence count, decision note, requested outcome, destination class, authority boundary, and required next proof.
7. Let the receiving capability perform current-file checks, backups, validation, and any further approval.

Do not convert approval of a proposal into approval for publication, external messages, hooks, configuration changes, or source edits.
