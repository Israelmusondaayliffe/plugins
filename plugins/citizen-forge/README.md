# Citizen Forge

Citizen Forge turns a plain-language internal-tool idea into a governed application lifecycle. It is designed for non-technical owners while keeping risk classification, policy decisions, state transitions, checks, change gates, and release decisions in deterministic Python code.

## Main workflow

1. Capture and confirm the application idea.
2. Register ownership and check for overlapping tools.
3. Score risk and choose a deterministic route.
4. Select one of four approved Python paved roads.
5. Provision only the adapters that are actually available.
6. Build and check the application against 35 named controls.
7. Block release when required evidence is missing, invalid, or unavailable.
8. Govern later changes, operation, transfer, archive, and retirement.

The `citizen-forge` front door routes an end-to-end request through the focused lifecycle skills.

## Install

Add the public marketplace once, then install Citizen Forge:

```bash
codex plugin marketplace add Israelmusondaayliffe/plugins --ref main
codex plugin add citizen-forge@community-agent-plugins
```

Start a new Claude Code, Claude Cowork, or Codex task after installation so the plugin skills appear in the task capability inventory.

## Included skills

- `citizen-forge`
- `citizen-idea`
- `citizen-register`
- `citizen-triage`
- `citizen-provision`
- `citizen-build`
- `citizen-release`
- `citizen-change`
- `citizen-operate`
- `citizen-explain`

## Safety model

- Deterministic code owns governance decisions.
- Missing or unverified controls never count as passed.
- Consequential changes always require a separate human gate.
- Filesystem checks reject project-root escapes and external symlinks.
- Unsupported cloud, identity, database, secret, monitoring, backup, and CI integrations remain `UNAVAILABLE`.
- The four included paved roads use the Python standard library and local files by default.

## Verification

The package includes unit, integration, adversarial, golden, usability, mutation, installation-parity, fresh-discovery, and lifecycle smoke tests.

Python 3.9 or newer is required for the deterministic runtime and verification suite.
