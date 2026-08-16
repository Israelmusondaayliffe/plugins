# Verification Standard

Completion requires fresh evidence from the installed environment. Verification is required by risk, not universally: verify changed or task-relevant surfaces, and do not re-prove unchanged state. Progress is an observable target-state delta plus a falling unresolved-work count. A passing validator never outweighs required items still marked needs-review, deferred, audit-only, backfill-only, or otherwise unfinished; unresolved required work blocks completion.

When the requested outcome depends on visual, editorial, strategic, experiential, or other human judgment, the task owner must supply a named qualitative acceptance artifact with an owner, threshold, and evidence surface. Report `functional_result` and `qualitative_result` separately. Runtime, structural, or telemetry proof cannot substitute for a missing, failed, blocked, stale, or below-threshold qualitative result.

## Structural checks

- Required files exist at the approved paths.
- JSON, TOML, YAML, and Markdown parse or validate where a validator exists.
- The instruction chain (CLAUDE.md, contract files, or AGENTS.md per platform) resolves in the intended order.
- Plugin and skill manifests contain no placeholders.
- Generated files contain no secrets or user-specific sample data.
- Support artifacts stay within the approved cap.

## Behavioral checks

- A new task discovers installed skills and plugin front doors.
- Fresh prompt input contains intended front doors, omits hidden specialists and exact mirrors, and records total plus section-level prompt size.
- Every hidden specialist has a deterministic front-door route and at least one actual explicit-invocation smoke.
- Command policy allows safe examples and blocks forbidden examples.
- Hooks run only after review and trust.
- Changed or task-relevant connectors return an authenticated profile or a precise setup requirement.
- Browser, Computer Use, and Artifacts are tested when changed, used, or required by acceptance. They remain preferred for rendered web work, native UI work, and polished structured deliverables.
- Required items have terminal states. `Needs review`, deferred, audit-only, and backfill-only remain incomplete unless approved as final.
- A required task-owned qualitative result has current evidence, meets its declared threshold, and is not replaced by functional proof.

## Completion receipt

List every required check once in one compact receipt. Include the command or inspection, fresh result, evidence path, and pass or fail status. A required missing or stale check is a failure, not a clean no-op. Do not create checks for unchanged surfaces.

Evidence is risk-tiered. Summarize ordinary low-risk commands inline: command, exit code, one-line result. Reserve separate evidence files for destructive, security, release, installation, or similarly high-risk operations. Do not require repeated unchanged-state proofs, duplicated receipts, or runtime-generated verifier scripts per worker or surface family.

For prompt subtraction, include the frozen baseline, raw outputs, scorer version, normalized category comparison, and post-install rerun. For local plugin updates, use the platform's supported flow: on Claude Code, a version bump plus marketplace refresh and plugin update; on Codex, the documented base version plus `+codex.<cachebuster>`. Then require installed listing, exact source/cache parity, and fresh discovery.

The completion receipt must keep `functional_result` and `qualitative_result` as separate fields when judgment is load-bearing. Harness Engineering verifies that the task owner supplied and passed the qualitative gate; it does not replace or reinterpret that owner's rubric.
