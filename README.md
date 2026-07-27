# Israel's Plugin Registry

A public marketplace for the personal plugins I use to research, plan, create,
operate, evaluate, and ship work in Codex, Claude Code, and Claude Cowork.

Website: https://israel-codex-plugins.israelayliffe.chatgpt.site

Repository: https://github.com/Israelmusondaayliffe/plugins

## Install

Add the marketplace once:

    codex plugin marketplace add Israelmusondaayliffe/plugins --ref main

Install any plugin:

    codex plugin add <plugin-name>@israel-codex-plugins

Example:

    codex plugin add knowledge-work-superpowers@israel-codex-plugins

Start a new Codex task after installation so the new skills are loaded into the
task capability inventory.

## Install (Claude Code)

Add the marketplace once, then install any plugin:

    /plugin marketplace add Israelmusondaayliffe/plugins
    /plugin install loopkit@israel-codex-plugins

Every plugin carries both a .codex-plugin and a .claude-plugin manifest, so the same
repository serves Codex and Claude. Plugin skills load namespaced (loopkit:loop-runner).

## Install (Claude Cowork)

Open Customize, select Plugins, then Add marketplace. Paste either repository form:

    Israelmusondaayliffe/plugins
    https://github.com/Israelmusondaayliffe/plugins

The plugins in this repository will appear in Cowork's marketplace. Select any plugin
and install it from the catalog.

## Included plugins

| Plugin | Purpose |
| --- | --- |
| agent-ops | Design, route, and audit durable agent systems |
| brand-world-studio | Build brand systems, briefs, visuals, and consistency checks |
| capability-operator | Route, inventory, govern, and verify Codex capabilities |
| citizen-forge | Turn internal-tool ideas into governed, verified application lifecycles |
| continuity-vault | Extract, structure, and govern durable working knowledge |
| data-storytelling-studio | Turn analysis into clear executive stories |
| founder-revenue-engine | Find customers, build outreach, and shape market narratives |
| harness-engineering | Interview, design, build, verify, and maintain a personalized Codex harness |
| knowledge-work-superpowers | Research, analyze, draft, review, and verify evidence-backed work |
| loopkit | Design, run, verify, resume, schedule, and diagnose bounded Codex loops |
| matt-partok-bundled-plugin-for-knowledge-work | Apply Matt Pocock's promoted workflow to coding and general knowledge work |
| model-evaluation-lab | Plan, run, and interpret model evaluations |
| model-prompt-lab | Design, migrate, and benchmark production prompts |
| outcome-engine | Turn unclear goals into verified outcomes |
| operating-graph | Design, run, inspect, and safely reorganize adaptive agent operating graphs |
| proofloop | Run governed, evidence-gated learning loops |
| strategy-room | Frame decisions, pressure-test strategy, and produce action-ready direction |
| video-production-studio | Plan and produce video systems, captions, and motion assets |
| web-product-studio | Design, build, test, and ship web products |
| writing-quality | Route, improve, and verify serious writing work |

The marketplace currently contains 20 plugins and 160 skills. The packages also
include their supporting scripts, references, assets, and agent definitions.
LoopKit includes local lifecycle hooks. The marketplace does not currently
bundle MCP servers or app connectors.

## Update

Refresh the marketplace:

    codex plugin marketplace upgrade israel-codex-plugins

Reinstall the plugin you want to update:

    codex plugin add <plugin-name>@israel-codex-plugins

Then start a new Codex task.

## Repository structure

- .agents/plugins/marketplace.json is the Codex marketplace catalog.
- plugins/ contains the distributable plugin packages.
- app/ contains the public catalog website.
- scripts/generate-catalog.mjs builds the website catalog from plugin manifests.
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
