import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);
const readJson = (path) =>
  JSON.parse(readFileSync(new URL(path, root), "utf8"));
const readText = (path) => readFileSync(new URL(path, root), "utf8");
const mattSlug = "matt-partok-bundled-plugin-for-knowledge-work";
const mattDisplayName = "Matt Partok Bundled Plugin For Knowledge Work";
const signalSlug = "signal-to-system";

function generatedExport(name) {
  const catalog = readText("app/catalog.generated.ts");
  const match = catalog.match(
    new RegExp(`export const ${name} = ([\\s\\S]*?) as const;\\n`),
  );
  assert.ok(match, `Generated catalog export is missing: ${name}`);
  return JSON.parse(match[1]);
}

const curation = readJson("docs/site-redesign/site-curation.json");
const guideSource = readJson("docs/site-redesign/plugin-guides.json");
const codexMarketplace = readJson(".agents/plugins/marketplace.json");
const claudeMarketplace = readJson(".claude-plugin/marketplace.json");
const catalog = generatedExport("plugins");
const totals = generatedExport("totals");
const collections = generatedExport("collections");
const signalToSystemStages = generatedExport("signalToSystemStages");
const signalToSystemGuides = generatedExport("signalToSystemGuides");
const repositorySkills = codexMarketplace.plugins.reduce(
  (total, plugin) =>
    total +
    readdirSync(new URL(`plugins/${plugin.name}/skills/`, root), {
      withFileTypes: true,
    }).filter((entry) => entry.isDirectory()).length,
  0,
);

test("keeps the complete repository inventory separate from the Site inventory", () => {
  assert.equal(codexMarketplace.plugins.length, 23);
  assert.equal(claudeMarketplace.plugins.length, 23);
  assert.equal(repositorySkills, 193);
  assert.equal(curation.visibility.visible_plugins.length, 22);
  assert.equal(curation.visibility.excluded_plugins.length, 1);
  assert.equal(curation.expected_totals.plugins, 22);
  assert.equal(curation.expected_totals.skills, 171);
  assert.equal(totals.plugins, 22);
  assert.equal(totals.skills, 171);
});

test("excludes only the repository-only compatibility plugin", () => {
  const catalogText = readText("app/catalog.generated.ts");
  assert.deepEqual(curation.visibility.excluded_plugins, [mattSlug]);
  for (const [slug, displayName] of [[mattSlug, mattDisplayName]]) {
    assert.equal(catalog.some((plugin) => plugin.slug === slug), false);
    assert.doesNotMatch(catalogText, new RegExp(slug));
    assert.doesNotMatch(catalogText, new RegExp(displayName));
  }
  for (const routePath of ["app/plugins.json/route.ts", "app/llms.txt/route.ts"]) {
    assert.equal(existsSync(new URL(routePath, root)), true);
    const route = readText(routePath);
    for (const [slug, displayName] of [[mattSlug, mattDisplayName]]) {
      assert.doesNotMatch(route, new RegExp(slug));
      assert.doesNotMatch(route, new RegExp(displayName));
    }
  }
  for (const collection of collections) {
    assert.equal(collection.plugins.includes(mattSlug), false);
  }
  assert.equal(catalog.some((plugin) => plugin.slug === signalSlug), true);
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
          "signal-to-system",
        ],
      },
    ],
  );
  assert.deepEqual(
    collections.flatMap((collection) => collection.plugins).sort(),
    [...curation.visibility.visible_plugins].sort(),
  );
});

test("binds all ten Signal to System skills to one stage and one guide", () => {
  const signalPlugin = catalog.find((plugin) => plugin.slug === signalSlug);
  assert.ok(signalPlugin);
  const skillNames = signalPlugin.skills.map((skill) => skill.name).sort();
  assert.equal(signalToSystemStages.length, 4);
  assert.deepEqual(
    signalToSystemStages.flatMap((stage) => stage.skills).sort(),
    skillNames,
  );
  assert.deepEqual(Object.keys(signalToSystemGuides).sort(), skillNames);
  for (const [skill, guide] of Object.entries(signalToSystemGuides)) {
    assert.ok(guide.illustrativePrompt.includes("["), skill + " needs an adaptable request");
    assert.ok(guide.method.length >= 3, skill + " needs a working method");
    assert.ok(guide.useWhen.length >= 2, skill + " needs fit guidance");
    assert.ok(guide.notFor.length >= 2, skill + " needs boundary guidance");
    const stage = signalToSystemStages.find((item) => item.slug === guide.stage);
    assert.ok(stage?.skills.includes(skill), skill + " must match its declared stage");
  }
});

test("gives every public plugin one complete, source-safe guide", () => {
  const guideNames = Object.keys(guideSource.guides);
  assert.deepEqual(guideNames.sort(), [...curation.visibility.visible_plugins].sort());
  assert.equal(
    guideNames.some((name) => curation.visibility.excluded_plugins.includes(name)),
    false,
  );

  for (const plugin of catalog) {
    const guide = guideSource.guides[plugin.slug];
    const skills = new Set(plugin.skills.map((skill) => skill.name));
    assert.ok(guide.bestFor.length >= 3, plugin.slug + " needs best-for guidance");
    assert.equal(guide.quickStarts.length, 3, plugin.slug + " needs three prompts");
    assert.ok(
      guide.workflow.length >= 3 && guide.workflow.length <= 6,
      plugin.slug + " needs a bounded workflow",
    );
    assert.ok(guide.skillPaths.length > 0, plugin.slug + " needs task-to-skill paths");
    assert.ok(
      guide.workedExample.steps.length >= 3,
      plugin.slug + " needs a worked example",
    );
    assert.ok(guide.tips.length >= 2, plugin.slug + " needs tips");
    assert.ok(guide.boundaries.length >= 2, plugin.slug + " needs boundaries");
    assert.ok(
      guide.successSignals.length >= 2,
      plugin.slug + " needs success signals",
    );

    const referencedSkills = [
      guide.startHere.skill,
      ...guide.workflow.flatMap((step) => step.skills),
      ...guide.skillPaths.map((path) => path.skill),
    ];
    for (const skill of referencedSkills) {
      assert.ok(
        skills.has(skill),
        plugin.slug + " references unknown skill " + skill,
      );
    }
    assert.equal(
      new Set(guide.quickStarts.map((item) => item.prompt.toLowerCase())).size,
      3,
      plugin.slug + " prompts must be unique",
    );
    const text = JSON.stringify(guide);
    for (const forbidden of [
      "/Users/",
      "~/.codex",
      "~/.claude",
      "@personal",
      "personal-plugins-private",
    ]) {
      assert.equal(
        text.toLowerCase().includes(forbidden.toLowerCase()),
        false,
        plugin.slug + " guide contains forbidden private text",
      );
    }
    assert.deepEqual(plugin.guide, guide);
  }
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
