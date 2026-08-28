import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const versions = {
  "agent-ops": "0.5.2",
  "brand-world-studio": "0.2.2",
  "capability-operator": "0.6.0",
  "citizen-forge": "1.1.0",
  "continuity-vault": "0.2.2",
  "data-storytelling-studio": "0.2.1",
  "founder-revenue-engine": "0.2.2",
  "gauntlet": "0.2.2",
  "gauntlet-loop": "1.2.0",
  "guide-production-studio": "0.1.1",
  "harness-engineering": "2.7.0",
  "knowledge-work-superpowers": "0.2.2",
  "last30days": "3.16.1",
  "loop-observatory": "0.1.0",
  "loopkit": "0.3.1",
  "matt-partok-bundled-plugin-for-knowledge-work": "1.1.1",
  "model-evaluation-lab": "0.2.1",
  "model-prompt-lab": "0.2.0",
  "operating-graph": "0.2.1",
  "outcome-engine": "1.1.2",
  "practice-compiler": "0.2.0",
  "proofloop": "0.2.0",
  "signal-to-system": "0.1.0-beta.1",
  "skill-eval-loop": "0.1.0",
  "strategy-room": "0.2.3",
  "video-production-studio": "0.3.1",
  "web-product-studio": "0.4.2",
  "writing-quality": "0.2.1",
  "ai-film-studio": "0.2.0",
};
const preservedAuthors = new Map([["last30days", "mvanhorn"]]);
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
  throw new Error("Codex marketplace inventory differs from the approved 29-plugin set");
}
if (JSON.stringify(claudeNames) !== JSON.stringify(codexNames)) {
  throw new Error("Claude marketplace inventory differs from Codex");
}
for (const [name, expected] of Object.entries(versions)) {
  const pluginRoot = join(root, "plugins", name);
  const marketplaceEntry = claudeMarketplace.plugins.find(
    (entry) => entry.name === name,
  );
  if (marketplaceEntry?.version !== expected) {
    throw new Error(`${name} marketplace version mismatch: expected ${expected}`);
  }
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
  const expectedAuthor = preservedAuthors.get(name) ?? "Community Maintainers";
  if (codex.author?.name !== expectedAuthor || claude.author?.name !== expectedAuthor) {
    throw new Error(`${name} publisher mismatch: expected ${expectedAuthor}`);
  }
  if (/\+codex\./.test(expected)) throw new Error(`${name} contains a cachebuster`);
}
console.log(JSON.stringify({ status: "PASS", plugins: Object.keys(versions).length }, null, 2));
