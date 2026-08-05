# Acceptance profiles

## Global loose skill

Use for a directly installed skill that is not owned by a plugin.

Required proof:

1. The complete source package inventory is known.
2. The intended global destination is explicit.
3. The installed package validates.
4. Source and installed destination have exact inventory and content parity.
5. A clean Codex task prompt contains the expected skill name.

## Personal plugin

Use for local plugins distributed through the personal marketplace.

Required proof:

1. Source bundle validation passes.
2. The personal marketplace entry points to the intended local source.
3. `codex plugin list` shows the plugin installed and enabled.
4. Source and installed cache have exact inventory and content parity.
5. The routing registry selects the intended front door or focused skill.
6. A clean Codex task prompt contains every expected implicit namespaced skill. Explicit-only specialists must remain absent from the prompt and be reachable through deterministic front-door route cases.

## Public cross-platform release

Use only when publication is explicitly authorized.

Required proof:

1. A stable semantic version is consistent across release-owned manifests.
2. Codex and Claude manifests contain the same release version and owned skill inventory.
3. Validation passes before the commit.
4. The exact validated commit is present on the GitHub default branch.
5. A fresh anonymous clone installs successfully in isolation.
6. Catalog or Sites surfaces are synchronized to that exact commit when they are part of the release.
7. A user-facing installer or share link resolves to the released capability.
8. Fresh-task discovery succeeds from the isolated installation.

Never substitute a local cachebuster for the public semantic version.
