import {
  existsSync,
  readFileSync,
  readdirSync,
  statSync,
} from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const readJson = (path) => JSON.parse(readFileSync(join(root, path), "utf8"));
const readText = (path) => readFileSync(join(root, path), "utf8");
const errors = [];
const expected = {
  repositoryPlugins: 22,
  repositorySkills: 181,
  sitePlugins: 21,
  siteSkills: 159,
};
const mattSlug = "matt-partok-bundled-plugin-for-knowledge-work";
const mattDisplayName = "Matt Partok Bundled Plugin For Knowledge Work";

const codexMarketplace = readJson(".agents/plugins/marketplace.json");
const claudeMarketplace = readJson(".claude-plugin/marketplace.json");
const hostSupport = readJson("docs/host-support.json");
const curation = readJson("docs/site-redesign/site-curation.json");

function sorted(values) {
  return [...values].sort();
}

function duplicates(values) {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

function pluginDirectories() {
  return readdirSync(join(root, "plugins"), { withFileTypes: true })
    .filter(
      (entry) =>
        entry.isDirectory() &&
        existsSync(join(root, "plugins", entry.name, ".codex-plugin/plugin.json")) &&
        existsSync(join(root, "plugins", entry.name, ".claude-plugin/plugin.json")),
    )
    .map((entry) => entry.name);
}

function skillCount(name) {
  const skillsRoot = join(root, "plugins", name, "skills");
  return readdirSync(skillsRoot, { withFileTypes: true }).filter(
    (entry) =>
      entry.isDirectory() &&
      existsSync(join(skillsRoot, entry.name, "SKILL.md")),
  ).length;
}

const repositoryNames = codexMarketplace.plugins.map((plugin) => plugin.name);
const claudeNames = claudeMarketplace.plugins.map((plugin) => plugin.name);
const packageNames = pluginDirectories();
const repositorySkillTotal = packageNames.reduce(
  (total, name) => total + skillCount(name),
  0,
);

if (repositoryNames.length !== expected.repositoryPlugins) {
  errors.push(`Repository Codex marketplace has ${repositoryNames.length} plugins, expected ${expected.repositoryPlugins}`);
}
if (claudeNames.length !== expected.repositoryPlugins) {
  errors.push(`Repository Claude marketplace has ${claudeNames.length} plugins, expected ${expected.repositoryPlugins}`);
}
if (JSON.stringify(sorted(repositoryNames)) !== JSON.stringify(sorted(claudeNames))) {
  errors.push("Repository Codex and Claude marketplace inventories differ");
}
if (JSON.stringify(sorted(repositoryNames)) !== JSON.stringify(sorted(packageNames))) {
  errors.push("Repository marketplace inventory differs from plugin packages");
}
if (repositorySkillTotal !== expected.repositorySkills) {
  errors.push(`Repository packages contain ${repositorySkillTotal} skills, expected ${expected.repositorySkills}`);
}
if (!repositoryNames.includes(mattSlug)) {
  errors.push("Matt bundle is missing from the repository marketplace");
}
if (!existsSync(join(root, "plugins", mattSlug))) {
  errors.push("Matt bundle package is missing from the repository");
}
if (!hostSupport[mattSlug]) {
  errors.push("Matt bundle runtime-support record is missing from the repository");
}

const visibleNames = curation.visibility?.visible_plugins ?? [];
const excludedNames = curation.visibility?.excluded_plugins ?? [];
const curatedNames = [...visibleNames, ...excludedNames];
if (curation.visibility?.mode !== "explicit-allowlist") {
  errors.push("Site visibility policy is not explicit-allowlist");
}
if (duplicates(curatedNames).length) {
  errors.push(`Site curation contains duplicate plugin names: ${duplicates(curatedNames).join(", ")}`);
}
if (JSON.stringify(sorted(curatedNames)) !== JSON.stringify(sorted(repositoryNames))) {
  errors.push("Site curation does not account for every repository plugin exactly once");
}
if (JSON.stringify(excludedNames) !== JSON.stringify([mattSlug])) {
  errors.push("Site curation must exclude exactly the Matt bundle");
}
if (visibleNames.length !== expected.sitePlugins) {
  errors.push(`Site curation exposes ${visibleNames.length} plugins, expected ${expected.sitePlugins}`);
}
if (curation.expected_totals?.plugins !== expected.sitePlugins || curation.expected_totals?.skills !== expected.siteSkills) {
  errors.push("Site curation expected totals are incorrect");
}

const collectionNames = curation.collections?.map((collection) => collection.name) ?? [];
const collectionPlugins = curation.collections?.flatMap((collection) => collection.plugins ?? []) ?? [];
const expectedCollections = [
  {
    name: "Build and create",
    plugins: [
      "citizen-forge",
      "web-product-studio",
      "brand-world-studio",
      "video-production-studio",
      "founder-revenue-engine",
    ],
  },
  {
    name: "Plan and run",
    plugins: [
      "outcome-engine",
      "loopkit",
      "operating-graph",
      "gauntlet-loop",
      "gauntlet",
      "agent-ops",
    ],
  },
  {
    name: "Verify and govern",
    plugins: [
      "capability-operator",
      "harness-engineering",
      "model-evaluation-lab",
      "proofloop",
    ],
  },
  {
    name: "Think, communicate, and preserve",
    plugins: [
      "knowledge-work-superpowers",
      "writing-quality",
      "strategy-room",
      "data-storytelling-studio",
      "continuity-vault",
      "model-prompt-lab",
    ],
  },
];
const actualCollections = (curation.collections ?? []).map((collection) => ({
  name: collection.name,
  plugins: collection.plugins,
}));
if (JSON.stringify(actualCollections) !== JSON.stringify(expectedCollections)) {
  errors.push("Site curation collections do not match the approved four-collection spine");
}
if (duplicates(collectionPlugins).length) {
  errors.push(`Site collections repeat plugins: ${duplicates(collectionPlugins).join(", ")}`);
}
if (JSON.stringify(sorted(collectionPlugins)) !== JSON.stringify(sorted(visibleNames))) {
  errors.push("Site collections do not assign every visible plugin exactly once");
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
let generatedCollections;
try {
  sitePlugins = generatedExport("plugins");
  siteTotals = generatedExport("totals");
  generatedCollections = generatedExport("collections");
} catch (error) {
  errors.push(error.message);
}

if (siteTotals?.plugins !== expected.sitePlugins || siteTotals?.skills !== expected.siteSkills) {
  errors.push("Generated Site totals do not match the approved Site inventory");
}
if (JSON.stringify(sitePlugins?.map((plugin) => plugin.slug)) !== JSON.stringify(visibleNames)) {
  errors.push("Generated catalog does not match the Site curation allowlist");
}
if (JSON.stringify(generatedCollections) !== JSON.stringify(curation.collections)) {
  errors.push("Generated collections differ from the Site curation record");
}
if (catalog.includes(mattSlug) || catalog.includes(mattDisplayName)) {
  errors.push("Matt bundle appears in the generated client catalog");
}

const routePaths = ["app/plugins.json/route.ts", "app/llms.txt/route.ts"];
for (const routePath of routePaths) {
  if (!existsSync(join(root, routePath))) {
    errors.push(`Missing public export route: ${routePath}`);
    continue;
  }
  const routeSource = readText(routePath);
  if (!routeSource.includes("plugins") || !routeSource.includes("totals")) {
    errors.push(`${routePath} is not bound to the generated visible catalog`);
  }
  if (routeSource.includes(mattSlug) || routeSource.includes(mattDisplayName)) {
    errors.push(`${routePath} contains the Matt bundle`);
  }
}

function walk(directory) {
  if (!existsSync(directory) || !statSync(directory).isDirectory()) return [];
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  });
}

for (const directory of ["app", "public", "build", "worker", "dist"]) {
  for (const path of walk(join(root, directory))) {
    let source;
    try {
      source = readFileSync(path, "utf8");
    } catch {
      continue;
    }
    if (source.includes(mattSlug) || source.includes(mattDisplayName)) {
      errors.push(`Public Site surface contains the Matt bundle: ${path.slice(root.length)}`);
    }
  }
}

if (errors.length) {
  throw new Error(errors.join("\n"));
}

console.log(JSON.stringify({
  status: "PASS",
  repository: {
    plugins: expected.repositoryPlugins,
    skills: expected.repositorySkills,
  },
  site: {
    plugins: expected.sitePlugins,
    skills: expected.siteSkills,
  },
  excluded: excludedNames,
  collections: collectionNames,
}, null, 2));
