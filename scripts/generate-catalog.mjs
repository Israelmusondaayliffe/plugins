import {
  existsSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const marketplacePath = join(root, ".agents/plugins/marketplace.json");
const marketplace = JSON.parse(readFileSync(marketplacePath, "utf8"));
const claudeMarketplacePath = join(root, ".claude-plugin/marketplace.json");
const claudeMarketplace = JSON.parse(
  readFileSync(claudeMarketplacePath, "utf8"),
);
const hostSupport = JSON.parse(
  readFileSync(join(root, "docs/host-support.json"), "utf8"),
);
const claudePluginNames = new Set(
  claudeMarketplace.plugins.map((plugin) => plugin.name),
);
const claudePluginsByName = new Map(
  claudeMarketplace.plugins.map((plugin) => [plugin.name, plugin]),
);
const codexPluginNames = new Set(marketplace.plugins.map((plugin) => plugin.name));
const missingFromClaude = [...codexPluginNames].filter(
  (name) => !claudePluginNames.has(name),
);
const missingFromCodex = [...claudePluginNames].filter(
  (name) => !codexPluginNames.has(name),
);
const missingHostSupport = [...codexPluginNames].filter(
  (name) => !hostSupport[name],
);
const unknownHostSupport = Object.keys(hostSupport).filter(
  (name) => !codexPluginNames.has(name),
);

if (
  missingFromClaude.length ||
  missingFromCodex.length ||
  missingHostSupport.length ||
  unknownHostSupport.length
) {
  throw new Error(
    [
      missingFromClaude.length
        ? `Missing from Claude marketplace: ${missingFromClaude.join(", ")}`
        : "",
      missingFromCodex.length
        ? `Missing from Codex marketplace: ${missingFromCodex.join(", ")}`
        : "",
      missingHostSupport.length
        ? `Missing host-support records: ${missingHostSupport.join(", ")}`
        : "",
      unknownHostSupport.length
        ? `Unknown host-support records: ${unknownHostSupport.join(", ")}`
        : "",
    ]
      .filter(Boolean)
      .join("\n"),
  );
}

function walk(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (
      entry.name === "__pycache__" ||
      entry.name === ".plugin-eval" ||
      entry.name === "CyberpunkReplica.ttf"
    ) {
      return [];
    }
    return entry.isDirectory() ? walk(path) : [path];
  });
}

function cleanText(value) {
  return String(value ?? "").replace(/[\u2014\u2013]/g, "-");
}

function unquoteFrontmatterValue(value) {
  const trimmed = value.trim();
  const first = trimmed.at(0);
  const last = trimmed.at(-1);
  return trimmed.length >= 2 &&
    ((first === '"' && last === '"') || (first === "'" && last === "'"))
    ? trimmed.slice(1, -1)
    : trimmed;
}

function frontmatterValue(source, key) {
  const match = source.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
  return match ? cleanText(unquoteFrontmatterValue(match[1])) : "";
}

const plugins = marketplace.plugins.map((entry) => {
  const pluginRoot = join(root, "plugins", entry.name);
  const manifest = JSON.parse(
    readFileSync(join(pluginRoot, ".codex-plugin/plugin.json"), "utf8"),
  );
  const claudeManifestPath = join(pluginRoot, ".claude-plugin/plugin.json");
  const claudeMarketplaceEntry = claudePluginsByName.get(entry.name);
  const supportsClaude =
    existsSync(claudeManifestPath) && claudePluginNames.has(entry.name);
  if (!supportsClaude) {
    throw new Error(`Missing Claude manifest for ${entry.name}`);
  }
  const claudeManifest = JSON.parse(readFileSync(claudeManifestPath, "utf8"));
  const support = hostSupport[entry.name];
  const allowedPlatforms = new Set(["Codex", "Claude Code", "Claude Cowork"]);
  if (
    !Array.isArray(support.platforms) ||
    support.platforms.length === 0 ||
    support.platforms.some((platform) => !allowedPlatforms.has(platform))
  ) {
    throw new Error(`Invalid host-support record for ${entry.name}`);
  }
  const expectedSource = `./plugins/${entry.name}`;
  if (
    entry.source?.path !== expectedSource ||
    claudeMarketplaceEntry?.source !== expectedSource
  ) {
    throw new Error(`Marketplace source mismatch for ${entry.name}`);
  }
  for (const field of ["name", "version", "description", "license", "keywords"]) {
    if (
      JSON.stringify(manifest[field] ?? null) !==
      JSON.stringify(claudeManifest[field] ?? null)
    ) {
      throw new Error(`Manifest ${field} mismatch for ${entry.name}`);
    }
  }
  for (const keyword of ["codex", "claude-code", "cowork"]) {
    if (!manifest.keywords?.includes(keyword)) {
      throw new Error(`Missing ${keyword} platform keyword for ${entry.name}`);
    }
  }
  const files = walk(pluginRoot);
  const skillRoot = join(pluginRoot, "skills");
  const skills = statSync(skillRoot).isDirectory()
    ? readdirSync(skillRoot, { withFileTypes: true })
        .filter((item) => item.isDirectory())
        .map((item) => {
          const skillFile = join(skillRoot, item.name, "SKILL.md");
          const source = readFileSync(skillFile, "utf8");
          return {
            name: item.name,
            description: frontmatterValue(source, "description"),
          };
        })
        .sort((a, b) => a.name.localeCompare(b.name))
    : [];

  const hasSegment = (file, segment) =>
    relative(pluginRoot, file).split("/").includes(segment);
  const counts = {
    skills: skills.length,
    assets: files.filter((file) => hasSegment(file, "assets")).length,
    references: files.filter((file) => hasSegment(file, "references")).length,
    scripts: files.filter((file) => hasSegment(file, "scripts")).length,
    files: files.length,
  };

  return {
    slug: entry.name,
    name: cleanText(manifest.interface?.displayName ?? entry.name),
    shortDescription: cleanText(
      manifest.interface?.shortDescription ?? manifest.description,
    ),
    longDescription: cleanText(
      manifest.interface?.longDescription ?? manifest.description,
    ),
    description: cleanText(manifest.description),
    version: manifest.version,
    category: entry.category,
    license: manifest.license ?? null,
    capabilities: manifest.interface?.capabilities ?? [],
    defaultPrompts: (manifest.interface?.defaultPrompt ?? []).map(cleanText),
    platforms: support.platforms,
    runtimeNote: cleanText(
      support.note ?? `Verified runtime support: ${support.platforms.join(", ")}.`,
    ),
    skills,
    counts,
    bundlesMcp: Boolean(manifest.mcpServers),
    bundlesApp: Boolean(manifest.apps),
  };
});

const totals = plugins.reduce(
  (acc, plugin) => ({
    plugins: acc.plugins + 1,
    skills: acc.skills + plugin.counts.skills,
    assets: acc.assets + plugin.counts.assets,
    references: acc.references + plugin.counts.references,
    scripts: acc.scripts + plugin.counts.scripts,
    files: acc.files + plugin.counts.files,
  }),
  { plugins: 0, skills: 0, assets: 0, references: 0, scripts: 0, files: 0 },
);

const output = `// Generated by scripts/generate-catalog.mjs. Do not edit directly.\n` +
  `export const marketplaceName = ${JSON.stringify(marketplace.name)} as const;\n` +
  `export const plugins = ${JSON.stringify(plugins, null, 2)} as const;\n` +
  `export const totals = ${JSON.stringify(totals, null, 2)} as const;\n` +
  `export type Plugin = (typeof plugins)[number];\n`;

writeFileSync(join(root, "app/catalog.generated.ts"), output);
console.log(`Generated catalog for ${plugins.length} plugins and ${totals.skills} skills.`);
