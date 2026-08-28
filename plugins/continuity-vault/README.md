# Continuity Vault

Continuity Vault packages source-preserving extraction, governed knowledge promotion, relationship mapping, recall routing, and staleness audits for work that must survive future Claude Code, Claude Cowork, and Codex sessions.

## Owned skills

- continuity-router
- knowledge-promotion-policy
- staleness-and-conflict-audit
- frontier-extraction
- graphify

## Companion capabilities

- Claude Mem for recall and prior-context discovery
- Notion and Google Drive for source-owned internal material
- Knowledge Work Superpowers for evidence-led deliverables
- Writing Quality for final continuity report prose

Run `scripts/check_companions.py` to see which optional companions are installed. Missing optional companions do not block owned workflows.

When Claude Mem or another recall companion is absent, `continuity-router` can run a bounded local search across exact workspace roots the user authorized in the current task. The fallback records the query, roots searched, authority checks, and matches. It returns `no-evidence` when nothing supports the requested recall.

When no writing companion is available, the router can create a direct evidence digest from a closed set of files inside those authorized roots. The local helper records source hashes and exact excerpts without promoting or mutating any source. Notion and Google Drive remain optional source owners. Read from them only through their own authorized surfaces.

## Boundaries

- Workspace files and the active instruction chain remain authoritative.
- Memory and Chronicle are recall surfaces, not sources of truth.
- Extraction, audits, and promotion decisions do not authorize silent source mutation.
- A local fallback never promotes, overwrites, deletes, or resolves conflicts without existing authority.

## Verification

Run `scripts/verify_bundle.py` from any directory. Installation is trusted only after plugin validation, skill validation, source-to-cache parity, live listing, real-artifact validation, and clean-task discovery all pass.
