# Harness Engineering

Harness Engineering is a local-first plugin that turns a rough operating brief into a personalized, installed, and verified AI operating harness on Claude Code, Claude Cowork, or Codex.

It does not copy one person's setup. It resolves the target platform, interviews the user, inspects the current environment, proposes the smallest useful architecture, and applies only approved changes after creating backups. The principles are shared across platforms; the surfaces are not, and the plugin never ports a path, command, or capability between platforms on similarity alone. See `references/platform-matrix.md`.

## Main workflow

1. Resolve the platform (Claude Code, Claude Cowork, or Codex).
2. Run `harness-interview` to establish needs, constraints, and success criteria.
3. Run `harness-audit` to inspect the current environment without changing it.
4. Run `harness-planner` to produce a decision-complete operations plan.
5. Review and approve operation groups.
6. Run `harness-builder` or `harness-runner` to apply the plan with durable state.
7. Run `harness-verifier` against fresh files and live discovery evidence.

The `harness-engineering` front door routes an end-to-end request through those phases.

## Context doctrine

On Claude 5 generation models the common defect in an inherited harness is over-constraint rather than absence. Anthropic removed over 80 percent of Claude Code's system prompt for Opus 5 and Fable 5 with no measurable loss on their coding evaluations. `references/claude5-context-doctrine.md` carries the rules that follow from that, and `context-doctor` applies them as a read-only audit with a deterministic scanner at `skills/context-doctor/scripts/context_scan.py`. The doctrine separates model compensation, which is removable, from user policy and taste, which is not.

## Install

Claude Cowork: install the delivered `harness-engineering.plugin` file from chat with one press, or install from your marketplace in the app.

Claude Code:

```bash
claude plugin install harness-engineering@israel-codex-plugins
```

or test a local checkout with `claude --plugin-dir ./plugins/harness-engineering`.

Codex:

```bash
codex plugin marketplace add Israelmusondaayliffe/plugins --ref main
codex plugin add harness-engineering@israel-codex-plugins
```

Start a new task after installation so the plugin's skills appear in the task capability inventory.

## Safety model

- Audit and planning are read-only.
- Dry-run is the default for file operations.
- Every update requires an expected file hash and a backup.
- New files and updates are written atomically.
- Hooks, authentication, external publication, and third-party installs require separate approval.
- Reports record configuration keys and capability state, never secret values.

## Frontier-first maintenance

Harness Engineering treats model-visible instructions as a compact context kernel with delta-only overlays. It keeps personal plugin front doors in default context, loads specialists only when relevant, and moves examples plus exact checks beside the task that owns them. Prompt reductions are accepted only against frozen behavior, routing, installed-state, and rollback evidence.

See `references/frontier-first-prompt-governance.md` for the complete subtraction, invocation-policy, skill-pilot, and post-model-update contract.

## Included skills

- `harness-engineering` (front door)
- `harness-interview`
- `harness-audit`
- `harness-planner`
- `agents-md-engineer` (instruction files: CLAUDE.md, Cowork contract files, AGENTS.md)
- `context-doctor` (read-only over-constraint audit against the Claude 5 context doctrine)
- `harness-builder`
- `skill-engineer`
- `plugin-engineer`
- `model-prompt-engineer`
- `harness-runner`
- `harness-verifier`
- `harness-maintainer`

## Local tooling

`scripts/harnessctl.py` uses only the Python standard library. It provides platform-aware environment audit (`--platform auto|claude-code|cowork|codex`), schema validation, dry-run, approved apply, backup manifests, verification, and rollback.

Python 3.9 or newer is required for deterministic apply and rollback. Interview, reasoning, and plan generation can still run when Python is unavailable, but the plugin must stop before changing files.

## Data handling

The plugin has no telemetry or hosted service. It stores run state locally under the user's selected run directory. On Cowork, run state must live in a connected folder to survive the session. See `PRIVACY.md` and `SECURITY.md`.
