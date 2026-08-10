---
name: harness-audit
description: Inspect a current Claude Code home, Cowork workspace, Codex home, project, or imported agent setup without changing it. Use for harness audits, setup inventories, CLAUDE.md or AGENTS.md chain checks, Cowork contract-file reviews, installed skill or plugin reviews, connector and MCP inventories, rules or hook inspection, drift detection, secret-exposure checks, and gap analysis before a harness plan or upgrade.
---

# Harness Audit

Read current state before proposing changes. Do not record credential values or private connector content.

## Workflow

1. Resolve the platform per `../../references/platform-matrix.md`, then read its platform file for the surfaces that exist there.
2. Run the harness's own deterministic check script first, if one exists (a smoke or validation script under the home scripts directory, or one the workspace contract names). Each failure enters the findings as a verified fact with the script's output as evidence. Skip re-deriving by hand anything the script already proves.
3. Identify the instruction chain for that platform: the CLAUDE.md chain on Claude Code, app instructions plus connected-folder contract files on Cowork, the AGENTS.md chain on Codex.
4. Inventory only the surfaces needed to answer the request. Use a full config, rules, hooks, skills, plugins, MCP, connector, templates, projects, memory, automation, and optional-capability inventory only when scope or risk justifies it.
5. Check for conflicts, placeholders, stale paths, duplicated ownership, missing validators, untrusted hooks, unsupported settings, cross-platform assumptions ported on similarity, and absent evidence.
6. Run the over-constraint pass with `context-doctor`. Reasoning-echo instructions rank first because they cause refusals rather than quality drag; verification instructions rank second.
7. Classify findings across information, execution, and feedback layers.
8. Separate verified facts, inferred risks, and user decisions.
9. Produce the smallest decision-useful audit. `audit.json` is optional unless a downstream machine operation needs it. Make no changes.

An audit is support work. It does not count as progress on an implementation request. Stop when the next safe target action is known.

## Promote repeat findings to the deterministic layer

A finding class that has surfaced in two or more audits belongs in the harness's check script, not in a longer checklist. When the audit report proposes fixes, include the script addition as a fix whenever the finding is deterministically checkable (registry parity, scope drift, version drift, dead file references, stale registries, output hygiene). If the harness has no such script, creating one is the first proposed fix. This keeps the auditor's prose focused on judgment calls the script cannot make.

Run:

```text
python3 ../../scripts/harnessctl.py audit --output AUDIT.json --platform auto [--home PATH] [--workspace PATH]
```

On Cowork, pass the connected folder as `--workspace`; the sandbox home is not the harness. Use `../../references/verification-standard.md` to distinguish file presence from operational proof.
