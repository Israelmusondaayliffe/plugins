---
name: practice-proposal-review
description: Reviews, ranks, approves, rejects, or defers Practice Compiler proposals using their redacted evidence and occurrence counts. Use when deciding which repeated session patterns deserve a skill, AGENTS.md rule, hook, tool fix, config change, durable note, or content idea. Records decisions without applying changes.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Practice Proposal Review

1. Run `python3 scripts/practice_compiler.py report`.
2. Inspect evidence references for each staged proposal.
3. Reject one-offs, generic advice, and signals based only on mentions.
4. Prefer updating an existing skill over creating another skill when ownership already exists.
5. Record each decision:

```bash
python3 scripts/practice_compiler.py decide PROPOSAL_ID approve --note "reason"
python3 scripts/practice_compiler.py decide PROPOSAL_ID reject --note "reason"
```

Approval produces a handoff record. It does not grant authority to edit the destination.
