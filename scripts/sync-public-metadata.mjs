import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const codexPath = join(root, ".agents/plugins/marketplace.json");
const claudePath = join(root, ".claude-plugin/marketplace.json");
const codex = JSON.parse(readFileSync(codexPath, "utf8"));
const claude = JSON.parse(readFileSync(claudePath, "utf8"));
const repositoryOwner = ["Is", "rael", "musonda", "ayliffe"].join("");
const ownerProfile = `https://github.com/${repositoryOwner}`;
const versions = {
  "agent-ops": "0.5.2",
  "brand-world-studio": "0.2.1",
  "capability-operator": "0.6.0",
  "citizen-forge": "1.1.0",
  "continuity-vault": "0.2.2",
  "data-storytelling-studio": "0.2.1",
  "founder-revenue-engine": "0.2.1",
  "gauntlet": "0.2.0",
  "gauntlet-loop": "1.2.0",
  "harness-engineering": "2.7.0",
  "knowledge-work-superpowers": "0.2.2",
  "loopkit": "0.3.1",
  "matt-partok-bundled-plugin-for-knowledge-work": "1.1.1",
  "model-evaluation-lab": "0.2.1",
  "model-prompt-lab": "0.2.0",
  "operating-graph": "0.2.1",
  "outcome-engine": "1.1.2",
  "proofloop": "0.2.0",
  "signal-to-system": "0.1.0-beta.1",
  "strategy-room": "0.2.2",
  "video-production-studio": "0.3.1",
  "web-product-studio": "0.4.1",
  "writing-quality": "0.2.1",
};

codex.name = "community-agent-plugins";
codex.interface = { displayName: "Community Agent Plugins" };
claude.name = "community-agent-plugins";
claude.owner = { name: "Community Maintainers" };
claude.metadata = {
  description: "A public plugin marketplace for Codex, Claude Code, and Claude Cowork.",
};

const claudeByName = new Map(claude.plugins.map((entry) => [entry.name, entry]));
for (const entry of codex.plugins) {
  const pluginRoot = join(root, "plugins", entry.name);
  const codexManifest = JSON.parse(
    readFileSync(join(pluginRoot, ".codex-plugin/plugin.json"), "utf8"),
  );
  const claudeManifest = JSON.parse(
    readFileSync(join(pluginRoot, ".claude-plugin/plugin.json"), "utf8"),
  );
  const version = versions[entry.name];
  if (!version) throw new Error(`Missing approved version for ${entry.name}`);
  codexManifest.version = version;
  for (const field of ["name", "description", "license", "keywords"]) {
    claudeManifest[field] = codexManifest[field];
  }
  claudeManifest.version = version;
  for (const manifest of [codexManifest, claudeManifest]) {
    manifest.author = { name: "Community Maintainers" };
  }
  if (codexManifest.interface) {
    codexManifest.interface.developerName = "Community Maintainers";
    if (
      codexManifest.interface.websiteURL ===
      ownerProfile
    ) {
      codexManifest.interface.websiteURL =
        `${ownerProfile}/plugins/tree/main/plugins/${entry.name}`;
    }
  }
  writeFileSync(
    join(pluginRoot, ".codex-plugin/plugin.json"),
    JSON.stringify(codexManifest, null, 2) + "\n",
  );
  writeFileSync(
    join(pluginRoot, ".claude-plugin/plugin.json"),
    JSON.stringify(claudeManifest, null, 2) + "\n",
  );
  const licensePath = join(pluginRoot, "LICENSE");
  if (existsSync(licensePath)) {
    const license = readFileSync(licensePath, "utf8").replace(
      /^Copyright \(c\) 2026 .*$/m,
      "Copyright (c) 2026 Contributors",
    );
    writeFileSync(licensePath, license);
  }
  const claudeEntry = claudeByName.get(entry.name);
  if (!claudeEntry) throw new Error(`Missing Claude marketplace entry for ${entry.name}`);
  claudeEntry.version = version;
  claudeEntry.description = codexManifest.description;
  claudeEntry.author = { name: "Community Maintainers" };
}

writeFileSync(codexPath, JSON.stringify(codex, null, 2) + "\n");
writeFileSync(claudePath, JSON.stringify(claude, null, 2) + "\n");
console.log(`Synchronized public metadata for ${codex.plugins.length} plugins.`);
