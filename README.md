# Community Agent Plugins

A public marketplace of reusable capabilities for research, planning, creation,
operations, evaluation, and software work across Codex, Claude Code, and Claude Cowork.

Repository: https://github.com/Israelmusondaayliffe/plugins

## Install

Add the marketplace once:

    codex plugin marketplace add Israelmusondaayliffe/plugins --ref main

Install a plugin supported on Codex:

    codex plugin add <plugin-name>@community-agent-plugins

Example:

    codex plugin add knowledge-work-superpowers@community-agent-plugins

Start a new Codex task after installation so the new skills are loaded into the
task capability inventory.

## Install (Claude Code)

Add the marketplace once, then install a plugin supported on Claude Code:

    /plugin marketplace add Israelmusondaayliffe/plugins
    /plugin install loopkit@community-agent-plugins

Every plugin carries both a .codex-plugin and a .claude-plugin manifest, so the same
repository serves Codex and Claude package discovery. Runtime support varies by
plugin and is declared in `docs/host-support.json`; a manifest alone is not a
runtime-parity claim. Plugin skills load namespaced (loopkit:loop-runner).

## Install (Claude Cowork)

Open Customize, select Plugins, then Add marketplace. Paste the repository URL:

    https://github.com/Israelmusondaayliffe/plugins

The plugins in this repository will appear in Cowork's marketplace. Select a
Cowork-supported plugin and install it from the catalog.

## Included plugins

| Plugin | Purpose |
| --- | --- |
| agent-ops | Design, route, and audit reusable agent systems on Claude Code, Claude Cowork, and Codex, with explicit authority, evidence, stops, and failure behavior. |
| brand-world-studio | Brand briefs, visual systems, image-model routing, production prompt packs, and consistency verification. |
| capability-operator | Capability routing, read-only inventories, overlap audits, portfolio governance, skill creation, and fresh-task discovery proof on Claude Code, Claude Cowork, or Codex. |
| citizen-forge | Governed internal application creation for non-technical owners, with deterministic policy and lifecycle controls. |
| continuity-vault | Source-preserving extraction, knowledge promotion, graph routing, recall, and staleness auditing across Claude Code, Claude Cowork, and Codex sessions. |
| data-storytelling-studio | Routes checked analysis into decision-facing visual stories, executive readouts, reports, decks, dashboards, and publishable sites. |
| founder-revenue-engine | Signal research, ICP definition, commercial narrative, bounded outreach drafts, and founder-led content on Claude Code, Claude Cowork, or Codex. |
| gauntlet | Claude Code and Cowork edition of the gauntlet method: explicit-only mega-project loop with blind critics, fresh-context verification, evidence reports, and multi-session handoff. Loads only when the user names the gauntlet. |
| gauntlet-loop | Codex edition of the gauntlet method: explicitly invoked mega-projects through approved plans, bounded agent workstreams, fresh critics, durable handoffs, and independent verification. |
| harness-engineering | Design, build, verify, and maintain a personalized AI operating harness on Claude Code, Claude Cowork, or Codex through a source-first interview and reversible guided workflow. |
| knowledge-work-superpowers | A disciplined workflow system for research, analysis, writing, review, and evidence-backed delivery. |
| loopkit | Design, run, verify, resume, schedule, and diagnose bounded loops on Claude Code, Claude Cowork, and Codex with durable host-scoped state and evidence-gated completion. |
| matt-partok-bundled-plugin-for-knowledge-work | A Codex-native adaptation of Matt Pocock's complete promoted workflow, extended for coding and general knowledge work. |
| model-evaluation-lab | Plans reproducible model evaluations, normalizes benchmark runs, and produces measured model-selection decisions. |
| model-prompt-lab | Verified model routing, production prompt architecture, migration audits, and benchmark design on Claude Code, Claude Cowork, and Codex. |
| outcome-engine | Turn unclear goals into verified outcomes across research, writing, operations, creative work, personal planning, and software. |
| operating-graph | Design, run, inspect, and safely reorganize adaptive agent operating graphs. |
| proofloop | Governed agent learning ledger and evaluation wrapper with bounded refinement, verification, quarantined memory, and read-only audit. |
| strategy-room | Pre-commitment interviews, assumption challenge, option generation, decision synthesis, and uncertainty tracking. |
| video-production-studio | End-to-end routing, prompting, production, captions, graphics, runtime implementation, and delivery checks for video. |
| web-product-studio | Route, build, redesign, implement from images, and verify web products with one visual authority on Claude Code, Claude Cowork, or Codex. |
| writing-quality | Intent-aware drafting, rewriting, detect-only review, claim boundaries, and final prose validation. |

The marketplace currently contains 22 plugins and 179 skills. The packages also
include their supporting scripts, references, assets, and agent definitions.
LoopKit includes local lifecycle hooks. The marketplace does not currently
bundle MCP servers or app connectors.

## Update

Refresh the marketplace:

    codex plugin marketplace upgrade community-agent-plugins

Reinstall the plugin you want to update:

    codex plugin add <plugin-name>@community-agent-plugins

Then start a new Codex task.

## Repository structure

- .agents/plugins/marketplace.json is the Codex marketplace catalog.
- plugins/ contains the distributable plugin packages.
- app/ contains the public catalog website.
- scripts/generate-catalog.mjs builds the website catalog from plugin manifests.
- scripts/package-plugin.py creates deterministic Cowork-compatible `.plugin` archives.
- scripts/verify-public-safety.mjs enforces the public identity and path boundary.
- INSTALL.md contains installation and troubleshooting details.
- LEGAL.md records package-specific licensing and exclusions.
- PRIVACY.md describes repository and plugin data handling.
- TERMS.md states the terms for using these packages.
- SECURITY.md explains secret handling and issue reporting.

## Development

Requirements: Node.js 22.13.0 or newer.

    npm install
    npm run dev
    npm test

The website catalog is generated directly from the marketplace and plugin
manifests before local development and production builds.
