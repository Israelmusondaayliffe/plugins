# Platform Matrix

Harness Engineering targets three platforms. The principles are shared. The surfaces are not. Resolve the platform before auditing, planning, or writing any file, and name it in every profile, plan, and receipt.

## Shared spine (all platforms)

- Phase order: interview, audit, plan, approve, apply with backups, verify with fresh evidence.
- Three layers: information, execution, feedback. Keep them balanced.
- Reliability ladder: prefer scripts, rules, and settings over prose instructions.
- Safety model: read-only audit, dry-run default, hash preconditions, backups, atomic writes, separate approval groups, rollback.
- `harnessctl.py` mechanics (validate, dry-run, apply, rollback) are platform-neutral. Only the audit target paths differ.

## Detection

Check in this order and confirm with the user when signals conflict:

1. Claude Cowork: session runs in a managed sandbox or Cowork VM, uploads appear under `/mnt/user-data/uploads/`, user folders arrive through connected-folder tools, plugins are cached under `~/.claude/plugins/synced/`, and there is no user-managed terminal home.
2. Claude Code: the `claude` CLI is on PATH, `~/.claude/` (or `CLAUDE_CONFIG_DIR`) holds `settings.json`, and instruction files are `CLAUDE.md`.
3. Codex: the `codex` CLI is on PATH, `CODEX_HOME` or `~/.codex/` holds `config.toml`, and instruction files are `AGENTS.md`.

A user can operate two or all three. In that case treat each platform as its own harness scope with its own audit, plan, and verification. Never assume parity between stacks.

## Divergence table

| Surface | Claude Code | Claude Cowork | Codex |
| --- | --- | --- | --- |
| Instruction chain | `CLAUDE.md` chain: managed policy, `~/.claude/CLAUDE.md`, project, `CLAUDE.local.md`, nested | Global instructions and preferences in app settings, plus contract files at the root of each connected folder | `AGENTS.md` chain: global, workspace, project, nested |
| Config home | `~/.claude/` with scoped `settings.json` | App-managed; no user-editable home inside the session | `~/.codex/` with `config.toml` |
| Skills | `~/.claude/skills/`, `.claude/skills/`, plugin skills | Plugin skills (namespaced `plugin:skill`) and app-level skills | `~/.codex/skills/`, plugin skills |
| Plugin install | `/plugin` UI, `claude plugin install`, marketplaces | Custom-plugin archive upload in **Customize** > **Plugins**, or a configured marketplace | `codex plugin marketplace add`, `codex plugin add` |
| Deterministic enforcement | Hooks in `settings.json`, permission rules | User-owned validator scripts run per contract; hooks rarely available | Rules, hooks, sandbox settings |
| Automation | Hooks, headless runs, background tasks | Scheduled tasks created in-session | Goals, Automations |
| State durability | Files in repo or `~/.claude/` persist | Session sandbox is ephemeral; durable state must live in a connected folder or an external system | Files in `CODEX_HOME` and workspace persist |
| Verification surface | `claude doctor`, `/doctor`, `claude plugin validate`, fresh session discovery | Fresh-task skill inventory, plugin list in app, contract files staged and read | `codex plugin list`, skill validators, fresh-task discovery |

## Platform files

Read exactly one before touching that platform's files:

- `platform-claude-code.md`
- `platform-cowork.md`
- `platform-codex.md`

If a fact is not in the platform file and not verifiable from the live environment or official documentation, treat it as unknown and say so. Never port a path, command, or capability from one platform to another on similarity alone.
