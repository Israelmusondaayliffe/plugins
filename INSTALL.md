# Install and update

This repository supports Codex, Claude Code, and Claude Cowork from the same
public source.

## Add the marketplace

Run this once:

    codex plugin marketplace add Israelmusondaayliffe/plugins --ref main

The marketplace name is community-agent-plugins.

## Install a plugin

Use the plugin folder name shown in the catalog:

    codex plugin add <plugin-name>@community-agent-plugins

For example:

    codex plugin add model-prompt-lab@community-agent-plugins

Start a new Codex task after installation. An already open task may keep the
capability inventory it loaded before the plugin was installed.

LoopKit includes local `PreCompact` and `SessionStart` hooks. Review and trust
them through `/hooks` before relying on automatic checkpoint refresh or resume.
The plugin remains usable through its skills and scripts if the hooks are not
trusted.

## Update

Refresh the marketplace source:

    codex plugin marketplace upgrade community-agent-plugins

Install the desired plugin again:

    codex plugin add <plugin-name>@community-agent-plugins

Start a new task to verify that the updated skills are visible.

## Troubleshooting

List installed marketplaces and plugins:

    codex plugin marketplace list
    codex plugin list

If a plugin is present on disk but absent from a task, close that task and open
a completely new one. Task inventories can remain stale after installation.

Some skills call optional tools or external services. Read that skill's
instructions for required CLIs, environment variables, accounts, or connectors.
No secrets are included in this repository.

## Claude Code

Add the marketplace and install a plugin from inside Claude Code:

    /plugin marketplace add Israelmusondaayliffe/plugins
    /plugin install <plugin-name>@community-agent-plugins

## Claude Cowork

Open Customize, select Plugins, then Add marketplace. Paste the repository URL:

    https://github.com/Israelmusondaayliffe/plugins

Choose a plugin from the marketplace and select Install.
