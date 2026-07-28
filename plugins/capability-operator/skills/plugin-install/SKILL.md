---
name: plugin-install
description: Install a plugin from a marketplace reference or a pasted install command, at user scope by default, then prove the install with registry evidence and fresh-task discovery. Use when the user pastes a claude plugin install, marketplace add, or npx skills command, asks to install a plugin or skill globally, or an install needs to be completed and verified end to end instead of assumed.
---

# Plugin Install

Install once, then prove it. The recurring failure modes this skill exists for: an install that silently lands at project scope instead of user scope, a stale registry entry left behind by a retried install, and "the skill shows in my current session" mistaken for installation evidence.

## Workflow

1. Parse what the user gave you: a plugin@marketplace reference, a marketplace add plus install pair, or an npx installer line. If the marketplace is not yet registered on the host, register it first.
2. Install at user scope unless the user explicitly names another scope. If a prior attempt left an entry at the wrong scope, remove the stale entry rather than installing a second copy next to it.
3. Prove installation from the host registry, not from memory: on Claude Code read the installed-plugins registry and confirm exactly one entry for the plugin, the intended scope, and the expected version. Confirm no duplicate or legacy-marketplace entries remain.
4. Prove discovery with `fresh-task-discovery-verifier`: the plugin's skills must appear in a fresh host session, not merely the current one.
5. Record the result where the harness keeps runtime or capability registries, and report name, version, scope, and the discovery evidence in one line each.

## Error handling

- A repeated install command usually means the first attempt gave no visible confirmation. Check the registry before running it again.
- Installed and task-visible are separate evidence layers; passing one does not pass the other.
- If discovery fails after a clean install, compare source, installed cache, and enabled state before reinstalling.
