# Capability Operator

Capability Operator routes, inventories, maintains, and governs local capabilities on Claude Code, Claude Cowork, and Codex.

## Owned skills

- capability-router
- capability-inventory
- skill-overlap-audit
- fresh-task-discovery-verifier
- plugin-portfolio-manager
- harness-meta-audit
- skill-creator-pro

## Optional companion examples

- system plugin-creator and skill-creator when canonical scaffolding is available
- Plugin Eval when analysis or benchmarks are requested
- ProofLoop when its bounded verification protocol is explicitly requested
- Claude Mem when recall is requested, never as a source of truth

Capability Operator remains useful when none of these companions are installed.

## Host surfaces

- Claude Code and Claude Cowork: `~/.claude/` is the config home. Installed plugins are recorded in `enabledPlugins` inside `~/.claude/settings.json`, `~/.claude/plugins/installed_plugins.json`, and the cached marketplaces under `~/.claude/plugins/marketplaces/`. Loose skills live in `~/.claude/skills/` and agents in `~/.claude/agents/`. Live listing comes from `claude plugin list` or the `/plugin` command. Fresh-task discovery evidence is the skill inventory of a fresh `claude -p` session.
- Codex: `~/.codex/` (or `CODEX_HOME`) is the config home, holding `config.toml` and `~/.codex/skills/`. Live listing comes from `codex plugin list`. Fresh-task discovery evidence is a clean-task prompt from `codex debug prompt-input`.

## Boundaries

- One request gets one primary route. Companions load only at documented handoffs.
- Explicit user selections win, and focused actions route to the narrow owned skill.
- Inventory and audit operations are read-only by default.
- Global writes require explicit task authority and a recent backup.
- Filesystem presence is not accepted as installation or discovery proof.

## Verification

The bundled registry is a small public example, not a maintainer portfolio. Create a local registry from source plugins, installed plugins, or both:

```bash
python3 skills/capability-inventory/scripts/collect_inventory.py \
  --plugins /path/to/plugins \
  --output /tmp/capability-inventory.json

python3 skills/capability-router/scripts/generate_local_registry.py \
  --inventory /tmp/capability-inventory.json \
  --output /tmp/routing-registry.json
```

Add `--skip-installed` when only source manifests should be inventoried. For installed entries, the collector records skills from each readable local plugin source. The generator prefers a source entry when the same plugin also appears as installed, then uses installed entries for names absent from source inventory.

Repeat `--plugin plugin-name` to select one or more inventory entries. Without `--plugin`, the generator includes every source or installed plugin with inventoried skills. The output is deterministic for the same inventory and snapshot date. It is a valid starting point with `needs_semantic_review: true`; review purpose, front doors, triggers, companions, handoffs, exclusions, lifecycle, and collision rules, then set that field to `false` before relying on implicit routing. Removing the field does not bypass review. Explicit plugin and skill selection remain available during review.

Validate and use the reviewed registry:

```bash
python3 skills/capability-router/scripts/validate_routes.py \
  --registry /tmp/routing-registry.json

python3 skills/capability-router/scripts/route_request.py \
  --registry /tmp/routing-registry.json \
  --plugin plugin-name \
  --task "the request"
```

Add `--inventory-root /path/to/plugins` when every selected plugin comes from that source root and source-tree parity must be checked. Omit it for an installed-only registry.

Render optional human and portfolio views:

```bash
python3 skills/capability-router/scripts/render_routing_reference.py \
  /tmp/routing-registry.json /tmp/routing-reference.md

python3 skills/capability-router/scripts/render_portfolio_ledger.py \
  /tmp/routing-registry.json /path/to/plugins /tmp/portfolio-ledger.json
```

The human routing reference works for source or installed inventory. The portfolio ledger requires a matching source plugin root because it reads plugin manifests.

Run `scripts/verify_bundle.py`, the routing cases, the plugin validator, and the skill validators. After installation, compare source with the installed cache and run `fresh-task-discovery-verifier`.
