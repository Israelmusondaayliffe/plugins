import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const versions = {
  "agent-ops": "0.5.1",
  "brand-world-studio": "0.2.0",
  "capability-operator": "0.5.0",
  "citizen-forge": "1.1.0",
  "continuity-vault": "0.2.1",
  "data-storytelling-studio": "0.2.0",
  "founder-revenue-engine": "0.2.0",
  "gauntlet": "0.2.0",
  "gauntlet-loop": "1.2.0",
  "harness-engineering": "2.7.0",
  "knowledge-work-superpowers": "0.2.1",
  "loopkit": "0.3.0",
  "matt-partok-bundled-plugin-for-knowledge-work": "1.1.1",
  "model-evaluation-lab": "0.2.0",
  "model-prompt-lab": "0.2.0",
  "operating-graph": "0.2.0",
  "outcome-engine": "1.1.1",
  "proofloop": "0.2.0",
  "signal-to-system": "0.1.0-beta.1",
  "strategy-room": "0.2.1",
  "video-production-studio": "0.3.0",
  "web-product-studio": "0.4.0",
  "writing-quality": "0.2.0",
};
const codexMarketplace = JSON.parse(
  readFileSync(join(root, ".agents/plugins/marketplace.json"), "utf8"),
);
const claudeMarketplace = JSON.parse(
  readFileSync(join(root, ".claude-plugin/marketplace.json"), "utf8"),
);
if (codexMarketplace.name !== "community-agent-plugins") {
  throw new Error("Codex marketplace identifier is not community-agent-plugins");
}
if (claudeMarketplace.name !== "community-agent-plugins") {
  throw new Error("Claude marketplace identifier is not community-agent-plugins");
}
const codexNames = codexMarketplace.plugins.map((entry) => entry.name).sort();
const claudeNames = claudeMarketplace.plugins.map((entry) => entry.name).sort();
if (JSON.stringify(codexNames) !== JSON.stringify(Object.keys(versions).sort())) {
  throw new Error("Codex marketplace inventory differs from the approved 23-plugin set");
}
if (JSON.stringify(claudeNames) !== JSON.stringify(codexNames)) {
  throw new Error("Claude marketplace inventory differs from Codex");
}
for (const [name, expected] of Object.entries(versions)) {
  const pluginRoot = join(root, "plugins", name);
  const codex = JSON.parse(
    readFileSync(join(pluginRoot, ".codex-plugin/plugin.json"), "utf8"),
  );
  const claude = JSON.parse(
    readFileSync(join(pluginRoot, ".claude-plugin/plugin.json"), "utf8"),
  );
  if (codex.version !== expected || claude.version !== expected) {
    throw new Error(`${name} version mismatch: expected ${expected}`);
  }
  for (const field of ["name", "version", "description", "license", "keywords"]) {
    if (JSON.stringify(codex[field] ?? null) !== JSON.stringify(claude[field] ?? null)) {
      throw new Error(`${name} manifest ${field} mismatch`);
    }
  }
  if (codex.author?.name !== "Community Maintainers" || claude.author?.name !== "Community Maintainers") {
    throw new Error(`${name} publisher is not depersonalized`);
  }
  if (/\+codex\./.test(expected)) throw new Error(`${name} contains a cachebuster`);
}
console.log(JSON.stringify({ status: "PASS", plugins: Object.keys(versions).length }, null, 2));
