---
name: harness-audit
description: Inspect a current Claude Code home, Cowork workspace, Codex home, project, or imported agent setup without changing it. Use for harness audits, setup inventories, CLAUDE.md or AGENTS.md chain checks, Cowork contract-file reviews, installed skill or plugin reviews, connector and MCP inventories, rules or hook inspection, drift detection, secret-exposure checks, and gap analysis before a harness plan or upgrade.
---

# Harness Audit

Read current state before proposing changes. Do not record credential values or private connector content.

## Workflow

1. Resolve the platform per `../../references/platform-matrix.md`, then read its platform file for the surfaces that exist there.
2. Identify the instruction chain for that platform: the CLAUDE.md chain on Claude Code, app instructions plus connected-folder contract files on Cowork, the AGENTS.md chain on Codex.
3. Inventory config key names, rules, hooks, skills, plugins, MCP and connector names, templates, projects, memory surfaces, automations or scheduled tasks, and optional capability bundles.
4. Check for conflicts, placeholders, stale paths, duplicated ownership, missing validators, untrusted hooks, unsupported settings, cross-platform assumptions ported on similarity, and absent evidence.
5. Run the over-constraint pass with `context-doctor`. Reasoning-echo instructions rank first because they cause refusals rather than quality drag; verification instructions rank second.
6. Classify findings across information, execution, and feedback layers.
7. Separate verified facts, inferred risks, and user decisions.
8. Produce `audit.json` plus a short gap summary. Make no changes.

Run:

```text
python3 ../../scripts/harnessctl.py audit --output AUDIT.json --platform auto [--home PATH] [--workspace PATH]
```

On Cowork, pass the connected folder as `--workspace`; the sandbox home is not the harness. Use `../../references/verification-standard.md` to distinguish file presence from operational proof.
