# Build notes, 2026-07-29

Spec section 17 items, verified against the live harness before building:

1. **Effort ladder.** Current Claude Code effort values are `low`, `medium`, `high`,
   `xhigh`, `max`. `ultracode` is still the multi-agent opt-in token (confirmed live in the
   build session). Prompt template references these values.
2. **/loop versus gauntlet-run.** The built-in `/loop` skill exists for interval-paced
   recurring prompts. `gauntlet-run` owns gauntlet iteration: the round loop is a
   deterministic state machine driven from disk state, not an interval poll. `/loop` may be
   used to re-invoke `gauntlet-run` across long unattended stretches, but never replaces it.
3. **Cowork clean-context parity.** Not testable from the build surface. Degraded mode is
   wired in: `precheck.py` detects capabilities at runtime, `run.json` records
   `context_isolation`, and handoff plus evidence outputs carry the banner.
4. **Connectors.** Notion connector reachable from the build surface. The Notion mirror is an
   optional adapter that degrades silently to files-only. Notion is never source of truth.
5. **plugin.json schema.** Verified against `claude plugin validate` and installed plugins on
   2026-07-29: components are auto-discovered from `skills/` and `agents/` directories. The
   spec's original instruction to add explicit `skills` and `agents` manifest fields is stale
   and was not followed; unrecognized fields fail `--strict` validation. Manifest carries
   name, version, description, author, license, keywords only.

Structural decisions:

- Shared scripts live at plugin root `scripts/`, invoked via
  `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`. Skills do not carry duplicate script copies.
- Shared agent instruction sets live at plugin root `agents/` with standard
  name/description frontmatter.
- Domain adapters live at plugin root `references/domains/`.
- Unit tests live at plugin root `tests/`, one `test_<script>.py` per script,
  run with `python3 -m unittest discover -s tests`.
