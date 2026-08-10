# Platform: Claude Code

Facts below were verified against official Claude Code documentation in July 2026. Re-verify after major releases; the maintainer skill owns that cadence.

## Instruction chain

Precedence from broadest to most specific, later files refine earlier ones:

1. Managed policy: `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux), `C:\Program Files\ClaudeCode\CLAUDE.md` (Windows).
2. User: `~/.claude/CLAUDE.md`.
3. Project: `./CLAUDE.md` or `./.claude/CLAUDE.md`.
4. Local: `./CLAUDE.local.md`, gitignored, still supported.
5. Nested `CLAUDE.md` in subdirectories loads on demand when files there are read.

`@path/to/file` imports expand at launch, maximum recursion depth 4. Use imports to keep the root contract short, the same way this plugin's templates do.

## Config home and settings

- Home is `~/.claude/`, overridable with `CLAUDE_CONFIG_DIR`.
- `~/.claude/settings.json` (user), `.claude/settings.json` (project, shared), `.claude/settings.local.json` (local, gitignored).
- Settings control `permissions` allow and deny rules, `hooks`, `env`, `model`, and related keys. Precedence: managed, then CLI arguments, then local, then project, then user.

## Capability surfaces

- Skills: `~/.claude/skills/<name>/SKILL.md` (personal), `.claude/skills/<name>/SKILL.md` (project), plus plugin skills. Skills and slash commands are unified; both create `/name` invocations. Legacy single-file commands in `commands/` still work.
- Subagents: `~/.claude/agents/*.md` and `.claude/agents/*.md`, markdown with YAML frontmatter (`name`, `description`, `tools`, `model`, and related fields).
- Hooks: configured under `hooks` in settings or a plugin's `hooks/hooks.json`. Events include SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, and Stop. Types include command, prompt, and agent. Exit code 2 blocks.
- MCP: `.mcp.json` at project root, `claude mcp add`, user and project and plugin scopes.

## Plugins

- Manifest at `.claude-plugin/plugin.json` in the plugin root.
- Install through the `/plugin` UI or `claude plugin install` with `--scope user|project|local`. Test with `--plugin-dir ./path`.
- A plugin may ship skills, agents, commands, hooks, MCP servers, and settings defaults.
- Marketplace installs cache under `~/.claude/plugins/cache/`.
- Validate with `claude plugin validate <path>`; `--strict` treats warnings as errors.

## Verification

- `claude doctor` (CLI) and `/doctor` (in session) check installation health.
- `claude plugin validate` checks manifests, hook configs, and frontmatter.
- Prove installed listing and exact source-cache parity with `scripts/verify_install.py --platform claude`; it reads `installed_plugins.json` and the enabled-plugins map.
- Prove discovery from a fresh session: the skill or plugin front door must appear in the capability inventory of a new task, not just on disk.

## Harness placement guidance

- Personal policy goes in `~/.claude/CLAUDE.md`, kept short, with imports for depth.
- Repeated exact behavior goes into hooks or permission rules before more prose.
- Project truth (commands, layout, verification) goes in the project `CLAUDE.md`.
- Reusable workflows become skills; distributable sets become plugins.
