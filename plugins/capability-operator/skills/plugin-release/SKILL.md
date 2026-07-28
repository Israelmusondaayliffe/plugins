---
name: plugin-release
description: Ship plugin content changes from the source-of-truth repo to installed copies. Detects drift between repo and installed versions, bumps every required manifest together, commits and pushes, refreshes the marketplace install, and verifies parity. Use for a plugin release, version bump, repo-to-install sync, checking whether the repo updated too, or when installed plugin content has drifted from its source repo.
---

# Plugin Release

One release choreography, always the same order, ending in parity evidence. The failure mode this skill exists for: a content change that never reaches installed copies because a version was not bumped, or a push that happened while the installed cache stayed stale.

## Workflow

1. Locate the source-of-truth repo and read its release rules first (usually the repo's own CLAUDE.md or AGENTS.md). Those rules win over this skill's defaults.
2. Detect drift: diff repo plugin content against the installed cache copies and list every plugin whose content changed, whether or not its version moved.
3. Treat changed content with an unmoved version as a failing state. Bump each changed plugin's version in every manifest the repo requires (typically the plugin manifest, any second-host manifest, and the root marketplace manifest) in the same commit.
4. Run each changed plugin's own verification scripts and tests before committing. A failing bundle check blocks the release.
5. Commit and push, then refresh the local install: update the marketplace, then update each changed installed plugin. Note that live sessions pick up the update only after a restart.
6. Verify parity: for every changed plugin, the installed version must equal the repo version. If the harness has a deterministic smoke script, run it as the final gate. Produce a short receipt listing plugins, old and new versions, commit hash, and verification results.

## Error handling

- Downstream copies that update by re-upload (for example a Cowork bundle) are part of the release only when the user asks; say explicitly whether they were refreshed.
- If the marketplace update pulls nothing, confirm the push actually landed on the branch the marketplace tracks before debugging the installer.
- Never edit installed cache copies directly; the repo is the only writable surface.
