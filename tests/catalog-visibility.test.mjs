import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);
const readJson = (path) =>
  JSON.parse(readFileSync(new URL(path, root), "utf8"));
const readText = (path) => readFileSync(new URL(path, root), "utf8");
const mattSlug = "matt-partok-bundled-plugin-for-knowledge-work";
const mattDisplayName = "Matt Partok Bundled Plugin For Knowledge Work";

function generatedExport(name) {
  const catalog = readText("app/catalog.generated.ts");
  const match = catalog.match(
    new RegExp(`export const ${name} = ([\\s\\S]*?) as const;\\n`),
  );
  assert.ok(match, `Generated catalog export is missing: ${name}`);
  return JSON.parse(match[1]);
}

const curation = readJson("docs/site-redesign/site-curation.json");
const codexMarketplace = readJson(".agents/plugins/marketplace.json");
const claudeMarketplace = readJson(".claude-plugin/marketplace.json");
const catalog = generatedExport("plugins");
const totals = generatedExport("totals");
const collections = generatedExport("collections");
const repositorySkills = codexMarketplace.plugins.reduce(
  (total, plugin) =>
    total +
    readdirSync(new URL(`plugins/${plugin.name}/skills/`, root), {
      withFileTypes: true,
    }).filter((entry) => entry.isDirectory()).length,
  0,
);

test("keeps the complete repository inventory separate from the Site inventory", () => {
  assert.equal(codexMarketplace.plugins.length, 22);
  assert.equal(claudeMarketplace.plugins.length, 22);
  assert.equal(repositorySkills, 180);
  assert.equal(curation.visibility.visible_plugins.length, 21);
  assert.equal(curation.visibility.excluded_plugins.length, 1);
  assert.equal(curation.expected_totals.plugins, 21);
  assert.equal(curation.expected_totals.skills, 158);
  assert.equal(totals.plugins, 21);
  assert.equal(totals.skills, 158);
});

test("excludes the Matt bundle from every generated Site surface", () => {
  const catalogText = readText("app/catalog.generated.ts");
  assert.deepEqual(curation.visibility.excluded_plugins, [mattSlug]);
  assert.equal(catalog.some((plugin) => plugin.slug === mattSlug), false);
  assert.doesNotMatch(catalogText, new RegExp(mattSlug));
  assert.doesNotMatch(catalogText, new RegExp(mattDisplayName));
  for (const routePath of ["app/plugins.json/route.ts", "app/llms.txt/route.ts"]) {
    assert.equal(existsSync(new URL(routePath, root)), true);
    const route = readText(routePath);
    assert.doesNotMatch(route, new RegExp(mattSlug));
    assert.doesNotMatch(route, new RegExp(mattDisplayName));
  }
  for (const collection of collections) {
    assert.equal(collection.plugins.includes(mattSlug), false);
  }
});

test("assigns every visible plugin to one approved outcome collection", () => {
  assert.deepEqual(
    collections.map((collection) => ({
      name: collection.name,
      plugins: [...collection.plugins],
    })),
    [
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
    ],
  );
  assert.deepEqual(
    collections.flatMap((collection) => collection.plugins).sort(),
    [...curation.visibility.visible_plugins].sort(),
  );
});

test("binds both machine-readable exports to the generated visible catalog", () => {
  const pluginsRoute = readText("app/plugins.json/route.ts");
  const llmsRoute = readText("app/llms.txt/route.ts");
  for (const source of [pluginsRoute, llmsRoute]) {
    assert.match(source, /catalog\.generated/);
    assert.match(source, /plugins/);
    assert.match(source, /totals/);
  }
});
