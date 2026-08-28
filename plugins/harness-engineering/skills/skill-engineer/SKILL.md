---
name: skill-engineer
description: Create or upgrade a missing skill identified during harness design for Claude Code, Claude Cowork, or Codex, with evidence that the skill fixes a repeated failure. Use when the harness plan requires a new reusable workflow, validator, script, reference set, or asset bundle that is not already supplied by an installed skill or plugin.
---

# Skill Engineer

Reuse an existing capability when it already owns the task. Create a skill only for a repeated, named failure or workflow.

Author to `../../references/claude5-context-doctrine.md`. A skill is a lightweight guide that encodes opinions particular to this user, not a constraint cage. Depth moves into linked files that load on demand, and enumerated prohibitions collapse into one statement of the wanted shape.

## Workflow

1. Define concrete trigger examples and the failure the skill prevents.
2. Search installed namespaced and loose skills for an existing owner.
3. When `capability-operator:skill-creator-pro` is installed, use it as an optional quality companion for invocation load, leading words, progressive disclosure, completion criteria, split decisions, pruning, and behavior cases. When it is absent, apply those criteria locally and continue without reducing the acceptance standard.
4. Author to the shared format: a directory with `SKILL.md`, YAML frontmatter carrying `name` and a third-person `description` with specific trigger phrases, and depth moved into linked `references/`.
5. On Codex, load the system `skill-creator` skill, initialize with its `init_skill.py`, and generate matching `agents/openai.yaml` metadata. On Claude Code and Cowork, use an installed skill-creation skill when present; otherwise author the directory directly.
6. When the skill belongs to a plugin, use the active host's official plugin workflow for manifests, versioning, installation, source/cache parity, and fresh discovery.
7. Add deterministic scripts only when exact behavior warrants them.
8. Validate: the Codex quick validator on Codex, `claude plugin validate` when the skill ships inside a Claude Code plugin, structural checks on Cowork, plus realistic positive and near-miss tests.
9. Place it where the platform discovers it, per the platform file: personal or project skills directory, or inside a plugin.
10. Before compacting an existing skill, freeze its source fingerprint, launcher contract, scripts, positive and negative triggers, functional cases, and external rubric. Stop before editing when the current version fails its acceptance gate.
11. Add the skill to the harness plan and discovery checks.

When upgrading an existing skill, run `context-doctor` first and treat its findings as the starting removal set.

Do not create a broad everything-skill or load an entire library by default.
Word ceilings are soft diagnostics. The complete behavior suite decides acceptance. See `../../references/frontier-first-prompt-governance.md`.
