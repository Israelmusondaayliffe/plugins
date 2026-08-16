---
name: harness-verifier
description: Verify a generated or upgraded harness against its approved profile, operations plan, current files, live capability state, and fresh discovery evidence, on Claude Code, Claude Cowork, or Codex. Use when a user asks whether the harness is complete, installed, global, visible, safe, restart-ready, or actually operational rather than merely present on disk.
---

# Harness Verifier

Verify without repairing during the verification pass. Use the platform file to know which proof surfaces exist; never mark a check passed on a surface the platform does not have.

Verification is outcome-first and required by risk, not universally. Start from the observable target-state delta and the unresolved required-work count, and limit checks to changed or task-relevant surfaces. Passing validators never outweigh required items still marked needs-review, deferred, or otherwise unfinished; unresolved required work means the harness is not complete.

## Workflow

1. Read the profile and plan without relying on the builder's summary.
2. Inspect current files, hashes, manifests, permissions, and backup evidence.
3. Verify the requested target-state delta and unresolved count before checking support machinery. A passing validator cannot override unresolved required work.
4. When judgment is load-bearing, inspect the task-owned qualitative acceptance artifact and report `functional_result` and `qualitative_result` separately. A missing, failed, blocked, stale, or below-threshold qualitative result prevents a complete verdict even when tests pass.
5. Run the smallest safe deterministic check set approved for the changed surfaces.
6. Verify only changed skills and plugins with the platform's validator: `claude plugin validate` and `claude doctor` on Claude Code, structural checks plus the live plugin list on Cowork, the official skill validators and `codex plugin list` on Codex. Then prove installed listing, source-cache parity where a cache exists, and fresh-task discovery.
7. On Cowork, additionally prove that changed files were committed to the connected folder on the user's device, not only staged in the sandbox.
8. For context changes, compare only the prompt and routing surfaces affected by the change, followed by one final behavior run when the global chain changed.
9. When independent criticism is required, use one fresh critic on the integrated result. Inspect intermediate pieces only when risk or a finding requires it.
10. Test connectors, Browser, Computer Use, Artifacts, hooks, rules, or optional capability bundles only when they changed, supplied evidence, or are required by acceptance.
11. Evaluate each judgment criterion with file, line, command, or live-surface evidence.
12. Emit one compact receipt with one result per required check.

Use `../../references/verification-standard.md`. A required missing, skipped, stale, stubbed, or renamed check fails verification. Unrequired checks should not be invented.
Use `../../references/frontier-first-prompt-governance.md` for prompt-subtraction and skill-pilot acceptance.
