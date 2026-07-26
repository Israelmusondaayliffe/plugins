# Verification Standard

Completion requires fresh evidence from the installed environment.

## Structural checks

- Required files exist at the approved paths.
- JSON, TOML, YAML, and Markdown parse or validate where a validator exists.
- The instruction chain (CLAUDE.md, contract files, or AGENTS.md per platform) resolves in the intended order.
- Plugin and skill manifests contain no placeholders.
- Generated files contain no secrets or user-specific sample data.

## Behavioral checks

- A new task discovers installed skills and plugin front doors.
- Fresh prompt input contains intended front doors, omits hidden specialists and exact mirrors, and records total plus section-level prompt size.
- Every hidden specialist has a deterministic front-door route and at least one actual explicit-invocation smoke.
- Command policy allows safe examples and blocks forbidden examples.
- Hooks run only after review and trust.
- Connectors return an authenticated profile or a precise setup requirement.
- Optional capability bundles (browser, computer use, device bridge) are tested only when the harness depends on them.

## Completion receipt

List every required check once. Include the command or inspection, fresh result, evidence path, and pass or fail status. A missing or stale check is a failure, not a clean no-op.

For prompt subtraction, include the frozen baseline, raw outputs, scorer version, normalized category comparison, and post-install rerun. For local plugin updates, accept the documented base version plus `+codex.<cachebuster>`, then require installed listing, exact source/cache parity, and fresh discovery.
