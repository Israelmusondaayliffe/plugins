---
name: harness-meta-audit
description: Run deep meta-audits against the user's AI harness and work system. Three routed modes. HARNESS audits goal alignment, Bitter Lesson over-engineering, self-model staleness, memory compounding, eval design, and the autonomy ladder. SECURITY maps prompt-injection exposure per input avenue and maintains a living attack-surface inventory. LIFE runs the ikigai big-picture, steelman-my-biggest-bet, 10x-or-dies, decisions-into-policy, binding-constraint, and bus-factor audits. Use whenever the user says audit my harness, self-model audit, bitter lesson check, is my memory compounding, autonomy ladder, attack surface, prompt injection review, where am I most wrong, find my bottleneck, bus factor, or asks for any deep review of their setup, priorities, or system design. Rerun after every major model intelligence jump.
license: MIT
metadata:
  author: Community Maintainers
  version: 1.1.0
  source: Daniel Miessler, 10 Prompts to Run Before Fable Goes Away
---

# Harness Meta-Audit

A Tier 3 router for maximum-intelligence audits pointed at the user's own harness and life
system. Based on Daniel Miessler's meta-prompt library. These audits benefit from the
strongest available model, so treat each run as high-effort work: research first, challenge
assumptions, verify findings against files, state confidence.

## Why this exists

Harnesses drift. The system prompt models a stale version of the user, skills accumulate
that fight the actual goal, memory captures but never resurfaces, and nobody defines what
better means. These audits catch the drift. Rerun them after every major model intelligence
jump, because a smarter model finds problems the previous one could not see.

## Router

Assess the request, load exactly one agent file, and follow it. Do not load the other
agents or the full prompt library for a single-audit request.

| Request signals | Load |
|---|---|
| Goal alignment, over-engineering, Bitter Lesson, self-model, memory, evals, what does better mean, autonomy, trust boundary, approval friction | `agents/harness-auditor.md` |
| Prompt injection, input avenues, attack surface, deployed systems, exposure, security posture | `agents/security-auditor.md` |
| Priorities, focus, ikigai, biggest bet, what to stop doing, 10x or dies, repeated decisions, bottleneck, bus factor, if I vanished | `agents/life-auditor.md` |

If the request spans modes ("full audit", "run everything"), run one mode at a time and
deliver each mode's findings before starting the next. A combined mega-report buries the
actionable items. If the request is genuinely ambiguous between modes, ask one focused
question with the mode options. Business stop-doings with an executable roadmap belong to
frontier-extraction's AUDIT move when that skill is mounted; LIFE here owns life and
priority stop-doings.

## Shared execution rules (all agents inherit these)

1. Ground every finding in the actual harness files. Read the contract files (CLAUDE.md and
   whatever it imports), the skills mount, and memory artifacts before claiming anything.
   A finding without a file path and a quoted line is an opinion, not a finding.
2. If the harness has no discoverable goal, stop and interview the user before auditing
   against an assumed one. Auditing toward the wrong goal is worse than not auditing.
3. Every audit ends with specific proposed edits: the file, the current text, the
   replacement. General advice is a failure mode.
4. Findings that require the user's judgment get presented as options with a recommendation
   first, not silently decided.
5. State confidence per finding (high, medium, low) and what evidence would change it.
6. Keep a last-run ledger (audit name, date, headline finding) at the top of each audit's
   output file, so rerun-after-model-jump is checkable. To automate the rerun trigger,
   hand off to a scheduling or loop skill when one is mounted.

## Output shape

Per audit: what was examined (files and evidence), findings ranked by impact, proposed
edits with exact locations, confidence statement. Plain prose. No scores without a stated
rubric.

## Resources

- `agents/harness-auditor.md` - runs the six HARNESS audits
- `agents/security-auditor.md` - runs the two SECURITY audits, owns attacksurface.md
- `agents/life-auditor.md` - runs the six LIFE audits
- `references/prompts.md` - the adapted Miessler prompt library, sectioned per audit
