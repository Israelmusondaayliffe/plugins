import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const readJson = (path) => JSON.parse(readFileSync(join(root, path), "utf8"));
const readText = (path) => readFileSync(join(root, path), "utf8");
const codexMarketplace = readJson(".agents/plugins/marketplace.json");
const claudeMarketplace = readJson(".claude-plugin/marketplace.json");
const hostSupport = readJson("docs/host-support.json");
const curation = readJson("docs/site-redesign/site-curation.json");
const errors = [];
const pluginNames = readdirSync(join(root, "plugins"), { withFileTypes: true })
  .filter(
    (entry) =>
      entry.isDirectory() &&
      existsSync(join(root, "plugins", entry.name, ".codex-plugin", "plugin.json")) &&
      existsSync(join(root, "plugins", entry.name, ".claude-plugin", "plugin.json")),
  )
  .map((entry) => entry.name)
  .sort();
const codexPluginNames = codexMarketplace.plugins.map((entry) => entry.name).sort();
const claudePluginNames = claudeMarketplace.plugins.map((entry) => entry.name).sort();
const claudeByName = new Map(
  claudeMarketplace.plugins.map((entry) => [entry.name, entry]),
);
let skillCount = 0;
const descriptions = new Map();

if (JSON.stringify(codexPluginNames) !== JSON.stringify(pluginNames)) {
  errors.push("Codex marketplace inventory differs from the plugin directories");
}
if (JSON.stringify(claudePluginNames) !== JSON.stringify(pluginNames)) {
  errors.push("Claude marketplace inventory differs from the plugin directories");
}
if (JSON.stringify(Object.keys(hostSupport).sort()) !== JSON.stringify(pluginNames)) {
  errors.push("Host-support inventory differs from the plugin directories");
}

for (const name of pluginNames) {
  const pluginRoot = join(root, "plugins", name);
  const codexManifest = readJson(`plugins/${name}/.codex-plugin/plugin.json`);
  const claudeManifest = readJson(`plugins/${name}/.claude-plugin/plugin.json`);
  const claudeEntry = claudeByName.get(name);
  const support = hostSupport[name];
  const skillsRoot = join(pluginRoot, "skills");
  const skills = readdirSync(skillsRoot, { withFileTypes: true }).filter(
    (entry) =>
      entry.isDirectory() &&
      existsSync(join(skillsRoot, entry.name, "SKILL.md")),
  );
  skillCount += skills.length;
  descriptions.set(name, codexManifest.description);
  if (claudeManifest.description !== codexManifest.description) {
    errors.push(`${name}: Codex and Claude manifest descriptions differ`);
  }
  if (claudeEntry?.description !== codexManifest.description) {
    errors.push(`${name}: Claude marketplace description differs from the manifest`);
  }
  if (!Array.isArray(support?.platforms) || support.platforms.length === 0) {
    errors.push(`${name}: verified runtime platforms are missing`);
    continue;
  }
  const interfaceClaims = [
    codexManifest.description,
    codexManifest.interface?.displayName,
    codexManifest.interface?.shortDescription,
    codexManifest.interface?.longDescription,
  ].join(" ");
  for (const platform of ["Codex", "Claude Code", "Claude Cowork"]) {
    if (interfaceClaims.includes(platform) && !support.platforms.includes(platform)) {
      errors.push(`${name}: public interface claims unsupported runtime ${platform}`);
    }
  }
  if (support.platforms.length < 3 && !support.note) {
    errors.push(`${name}: limited runtime support requires a public note`);
  }
}

const pluginCount = pluginNames.length;
const expectedCountText = `${pluginCount} plugins and ${skillCount} skills`;
const readme = readText("README.md");
const countClaims = [...readme.matchAll(/\b(\d+) plugins and (\d+) skills\b/g)];
if (countClaims.length !== 1) {
  errors.push("README must contain exactly one plugin and skill count claim");
} else if (countClaims[0][0] !== expectedCountText) {
  errors.push(`README count is stale: expected ${expectedCountText}`);
}

const tableRows = new Map(
  [...readme.matchAll(/^\| ([a-z0-9-]+) \| (.+) \|$/gm)]
    .filter((match) => pluginNames.includes(match[1]))
    .map((match) => [match[1], match[2]]),
);
for (const name of pluginNames) {
  if (tableRows.get(name) !== descriptions.get(name)) {
    errors.push(`${name}: README purpose differs from the manifest description`);
  }
}
if (tableRows.size !== pluginCount) {
  errors.push(`README table must contain exactly ${pluginCount} plugin rows`);
}
if (
  !readme.includes("Runtime support varies by") ||
  !readme.includes("docs/host-support.json")
) {
  errors.push("README must distinguish package manifests from runtime support");
}
if (readme.includes("Install any plugin")) {
  errors.push("README must not claim every plugin runs on every host");
}

const route = readJson("docs/site-redesign/route.json");
if (!route.objective.includes(`${pluginCount}-package repository`)) {
  errors.push("Site redesign route has a stale repository plugin count");
}
const acceptance = readJson("docs/site-redesign/acceptance-flow.json");
const marketplaceExpectation = acceptance.flows?.[0]?.steps?.[0]?.expected ?? "";
if (
  !marketplaceExpectation.includes(`${curation.expected_totals.plugins} public plugins`) ||
  !marketplaceExpectation.includes(`${curation.expected_totals.skills} bundled skills`)
) {
  errors.push("Site redesign acceptance flow has stale public Site totals");
}

const repositoryMetadata = readJson(".github/repository-metadata.json");
const expectedDescription =
  `A public multi-harness marketplace with ${pluginCount} plugins and ${skillCount} skills for Claude Code, Claude Cowork, and Codex.`;
if (repositoryMetadata.description !== expectedDescription) {
  errors.push("Repository About description does not match the live inventory");
}
if (repositoryMetadata.homepage !== null) {
  errors.push("Repository homepage must stay empty until a hosted catalog is approved");
}

const catalog = readText("app/catalog.generated.ts");
function generatedExport(name) {
  const match = catalog.match(
    new RegExp(`export const ${name} = ([\\s\\S]*?) as const;\\n`),
  );
  if (!match) throw new Error(`Generated catalog export is missing: ${name}`);
  return JSON.parse(match[1]);
}

let sitePlugins;
let siteTotals;
try {
  sitePlugins = generatedExport("plugins");
  siteTotals = generatedExport("totals");
} catch (error) {
  errors.push(error.message);
}

const visibleNames = curation.visibility?.visible_plugins ?? [];
const excludedNames = curation.visibility?.excluded_plugins ?? [];
if (
  siteTotals?.plugins !== curation.expected_totals?.plugins ||
  siteTotals?.skills !== curation.expected_totals?.skills
) {
  errors.push("Generated Site totals do not match the Site curation policy");
}
if (
  JSON.stringify(sitePlugins?.map((plugin) => plugin.slug)) !==
  JSON.stringify(visibleNames)
) {
  errors.push("Generated Site plugin order differs from the Site curation allowlist");
}
for (const excludedName of excludedNames) {
  if (catalog.includes(`"slug": ${JSON.stringify(excludedName)}`)) {
    errors.push(`${excludedName}: excluded plugin appears in the generated Site catalog`);
  }
}
for (const [name, description] of descriptions) {
  if (!visibleNames.includes(name)) continue;
  const recordStart = catalog.indexOf(`"slug": ${JSON.stringify(name)}`);
  const nextRecord = catalog.indexOf('\n  {\n    "slug":', recordStart + 1);
  const record = catalog.slice(
    recordStart,
    nextRecord === -1 ? catalog.length : nextRecord,
  );
  if (!record.includes(`"description": ${JSON.stringify(description)}`)) {
    errors.push(`${name}: generated catalog description is stale`);
  }
  for (const platform of hostSupport[name].platforms) {
    if (!record.includes(JSON.stringify(platform))) {
      errors.push(`${name}: generated catalog omits verified runtime ${platform}`);
    }
  }
  if (!record.includes(`"runtimeNote": ${JSON.stringify(
    hostSupport[name].note ??
      `Verified runtime support: ${hostSupport[name].platforms.join(", ")}.`,
  )}`)) {
    errors.push(`${name}: generated runtime-support note is stale`);
  }
}

const homepage = readText("app/page.tsx");
const detailPage = readText("app/plugins/[slug]/page.tsx");
for (const staleClaim of [
  "One source, packaged for all three.",
  "The same package is available in Codex, Claude Code, and Claude Cowork.",
]) {
  if (homepage.includes(staleClaim) || detailPage.includes(staleClaim)) {
    errors.push(`Public catalog contains an unqualified runtime claim: ${staleClaim}`);
  }
}

if (errors.length) {
  throw new Error(errors.join("\n"));
}

console.log(
  JSON.stringify(
    {
      status: "PASS",
      plugins: pluginCount,
      skills: skillCount,
      descriptions: descriptions.size,
      repositoryDescription: repositoryMetadata.description,
    },
    null,
    2,
  ),
);
