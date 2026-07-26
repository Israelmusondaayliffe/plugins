---
name: context-doctor
description: Audit persistent context against the Claude 5 context doctrine and return a deprune ledger. Use when a user asks to rightsize a CLAUDE.md, AGENTS.md, Cowork contract file, skill, or plugin bundle, says a skill is over-constrained or too prescriptive, asks what to cut after a model upgrade, wants a context audit, doctrine audit, over-constraint check, reasoning-echo check, or asks why an inherited harness degrades output on Claude 5 models. Read-only. It produces findings and a proposed removal set, and does not rewrite the source.
---

# Context Doctor

Over-constraint is the default failure mode of context written for 4.x models. Find it,
prove it, and propose removals with reasons. Removal without a stated reason gets reverted.

Read `../../references/claude5-context-doctrine.md` before judging anything.

The doctrine is platform independent; the chain it applies to is not. Audit the CLAUDE.md
chain on Claude Code, the app instructions plus connected-folder contract files on Claude
Cowork, and the AGENTS.md chain on Codex. Skills and plugin bundles are audited the same
way on all three.

## Workflow

1. Resolve the scope: one file, one skill directory, a plugin bundle, or an instruction
   chain. Name every file that will be judged.
2. Run the scanner for the deterministic findings:

```text
python3 scripts/context_scan.py PATH [--json OUT.json]
```

3. Apply the doctrine's audit test to what the scanner cannot see: judgement calls,
   examples that could be interface design, upfront detail that could load on demand, and
   content that only restates what the file system already shows.
4. Separate two classes and keep them separate in the output. Model compensation is
   removable. User policy, taste, gotchas, authority boundaries, and data routing are not,
   even when they read as rules.
5. Rank findings. Reasoning-echo hits come first because they cause refusals rather than
   drag. Verification instructions come second. Everything else follows by token weight.
6. Report the proposed removal set with a reason per line, and the keep set with its
   justification. Hand the ledger to whoever will apply it.

## Output

One row per finding: file, line, category, severity, the text, the reason, and the proposed
action. A file with no findings gets a row saying so. Silence is not a result.

Do not edit the audited source. Application belongs to `agents-md-engineer` for instruction
files, `skill-engineer` for skills, and `plugin-engineer` for bundles.
