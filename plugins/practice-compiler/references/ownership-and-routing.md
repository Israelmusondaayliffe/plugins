# Ownership and routing

Practice Compiler owns read-only trace scanning, redacted signal records, deduplicated proposal staging, and human decisions about those proposals.

It does not own the destination change. These are preferred owners, not runtime requirements:

| Proposal destination | Preferred owner |
| --- | --- |
| Existing skill update | `skill-eval-loop:capability-repair-cycle` |
| New skill candidate | `capability-operator:skill-creator-pro` |
| `AGENTS.md`, hook, config, tool, or CLI | `harness-engineering:harness-engineering` |
| Durable knowledge | `continuity-vault:continuity-router` |
| Content idea | The user's content backlog, then the chosen writing workflow |
| Discard | No handoff |

Codex Mem may help locate prior work when healthy, but it is not required. The scanner reads local JSONL directly and treats current files as authority.

When a preferred owner is unavailable, write the generic handoff with an unassigned owner. The handoff still includes the proposal ID, redacted evidence references, occurrence count, decision note, requested outcome, destination class, authority boundary, and proof required before the receiving change.
