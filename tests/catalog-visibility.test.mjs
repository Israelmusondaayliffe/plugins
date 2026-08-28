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

test("keeps the approved Site copy exact", () => {
  const shellCopy = [
    ["app/page.tsx", "Install by host"],
    ["app/page.tsx", "Inspect each claim."],
    [
      "app/components/SignalSkillChooser.tsx",
      "Each choice selects one independently usable skill. Your recommendation appears here.",
    ],
    ["app/plugins/[slug]/page.tsx", "Use this workflow."],
    ["app/plugins/[slug]/page.tsx", "Inspect the source."],
    [
      "app/plugins/signal-to-system/skills/[skill]/page.tsx",
      "Use this skill when",
    ],
    [
      "app/plugins/signal-to-system/skills/[skill]/page.tsx",
      "Use another skill for these jobs",
    ],
    [
      "app/plugins/signal-to-system/skills/[skill]/page.tsx",
      "How this skill works",
    ],
    [
      "app/plugins/signal-to-system/skills/[skill]/page.tsx",
      "A result you can use, with clear limits.",
    ],
  ];
  for (const [path, copy] of shellCopy) {
    const compactSource = readText(path).replace(/\s+/g, " ");
    assert.ok(compactSource.includes(copy), `${path} is missing: ${copy}`);
  }

  const workedResults = {
    "knowledge-work-superpowers": "The finished decision brief traces its sources, states uncertainty clearly, and ties the recommendation to the evidence.",
    "outcome-engine": "The finished workshop test has an approved brief, practical work units, and clear readiness evidence.",
    proofloop: "The briefing is verified, and its learning record remains reviewable without replacing the source instructions.",
    "writing-quality": "The launch copy is clear and intentional, preserves the source meaning, and makes only supportable claims.",
    "capability-operator": "The selected primary capability has a clear fit, backed by evidence for every installation or discovery claim.",
    "citizen-forge": "The internal app is owned and registered, with clear allowed actions, blocked actions, and operating responsibilities.",
    "agent-ops": "The reusable agent contract says what to inspect, when to report, when to do nothing, and when to stop.",
    "video-production-studio": "The delivery-ready video matches the approved brief in story, media, captions, and technical properties.",
    "web-product-studio": "The working redesign keeps the product's identity, shortens the main path, and passes the agreed browser flows.",
    "model-prompt-lab": "The target prompt has an explicit contract and measured evidence that supports or rejects the migration.",
    "strategy-room": "The decision states its tradeoffs, testable assumptions, and the next evidence needed before a larger commitment.",
    "brand-world-studio": "The brand system and prompt pack are inspectable and produce related images without making every image identical.",
    "founder-revenue-engine": "The customer hypothesis is testable, the narrative is credible, and the bounded outreach draft is tied to observed signals.",
    "continuity-vault": "The knowledge records are traceable, scoped, and useful to later work without replacing the original project evidence.",
    "data-storytelling-studio": "The concise readout helps leaders decide what to test while keeping evidence and caveats visible.",
    "model-evaluation-lab": "The evidence package is reproducible, and the model choice is tied to the real production constraints.",
    loopkit: "The resumable loop reports real changes, records clean no-op runs, and stops or escalates under defined conditions.",
    "harness-engineering": "The host-native harness supports the user's real work, with its rules, capabilities, and proof chain verified in a fresh task.",
    "operating-graph": "The graph is inspectable: every transition has a reason, evidence is preserved, and publication remains behind explicit approval.",
    "gauntlet-loop": "The public release is complete, with compact evidence that every required workstream reached a terminal state.",
    gauntlet: "The documentation system makes its artifacts, source fidelity, checks, and unresolved items independently inspectable.",
    "signal-to-system": "The illustrative route ends with a traceable chain from cited public signals to a bounded test, a right-sized workshop package, and permission-aware follow-up outputs. This is not a claimed outcome.",
  };
  for (const [slug, result] of Object.entries(workedResults)) {
    assert.equal(guideSource.guides[slug].workedExample.result, result);
    assert.equal(catalog.find((plugin) => plugin.slug === slug)?.guide.workedExample.result, result);
  }

  assert.equal(guideSource.guides["outcome-engine"].tips[0], "Describe the intended change as well as the artifact you want produced.");
  assert.equal(guideSource.guides["capability-operator"].tips[2], "Describe the outcome instead of relying on the tool name you remember.");
  assert.equal(guideSource.guides["citizen-forge"].tips[3], "Describe normal operation and support after the first release.");
  assert.equal(guideSource.guides["video-production-studio"].tips[3], "Review the rendered file as well as the timeline or source code.");
  assert.equal(guideSource.guides["brand-world-studio"].successSignals[2], "Finished assets are checked together and individually.");
  assert.equal(guideSource.guides["continuity-vault"].tips[0], "Provide the original source instead of a remembered summary.");
  assert.equal(guideSource.guides["data-storytelling-studio"].tips[0], "Bring checked analysis rather than raw data alone.");
  assert.equal(guideSource.guides["model-evaluation-lab"].tips[0], "Use production-like cases, including hard examples.");
  assert.equal(guideSource.guides["harness-engineering"].skillPaths[4].why, "It checks the installed capability, fresh-task behavior, and the files.");
});

test("preserves the approved skill routing descriptions", () => {
  const skillDescriptions = {
    "web-product-studio/full-output-enforcement": "Guides long code-generation tasks through continuation rules, placeholder checks, and clean token-limit splits. Use for exhaustive, unabridged output.",
    "web-product-studio/redesign-existing-projects": "Audits existing websites and apps, identifies generic AI patterns, applies the skill's design standards, and checks that existing functionality still works. Supports any CSS framework or vanilla CSS.",
    "strategy-room/assumption-challenger": "Tier 3 research-first assumption challenger. It researches current sources, builds a challenge plan, examines the subject through several lenses, checks findings against the research, and returns a recommendations report. Use when user says \"challenge assumptions,\" \"analyze blind spots,\" \"what am I missing,\" \"critique this,\" \"find contradictions,\" \"stress test this,\" \"what could go wrong,\" \"tear this apart,\" or asks for rigorous adversarial review of plans, prompts, strategies, ideas, business cases, technical decisions, or AI prompts. Five-agent pipeline (researcher, planner, challenger, verifier, synthesizer). Three effort modes (light, standard, deep). Mandatory web search before challenge so the critique is grounded in current facts and expert disagreement, not training-data instinct.",
    "brand-world-studio/brandkit": "Creates brand-guidelines boards, logo systems, identity decks, and visual-world presentations across minimalist, cinematic, editorial, dark-tech, luxury, cultural, security, gaming, developer-tool, and consumer-app styles. It directs logo concepts, composition, sparse typography, symbols, mockups, imagery, and grid layouts.",
    "founder-revenue-engine/linkedin-viral-content-creator": "Create LinkedIn posts using a probability-driven consensus-breaking method and 69 included templates. Use when writing LinkedIn posts, creating hooks, improving drafts, or generating contrarian content. Enforces no-fabrication rule and a configurable voice profile. Six-phase workflow maps consensus, generates hooks via dual method (tail sampling plus templates), applies PRISM humanization, writes body, enforces quality, and delivers multiple options with rationale.",
    "gauntlet/gauntlet": "Loads only when the user explicitly invokes the gauntlet by name with one of these trigger phrases: gauntlet, run the gauntlet, gauntlet loop, gauntlet mode, gauntlet run, the big one, mega project mode, max run, ultracode run, beat this bar, blind critic loop, Claude of Duty method, resume the gauntlet, gauntlet handoff. It is the front door and router for the gauntlet mega-project method. It prechecks the surface and routes to the brief, prompt, run, verify, evidence, and handoff stages. Do not load for ordinary tasks, quick edits, single-shot drafts, routine reviews, or any request that does not name the gauntlet.",
    "web-product-studio/code-production-agent": "Coding agent for non-coders that turns plain-English requirements into software through required research, planning, approval, and validated execution. Handles building new apps/features/components/APIs, debugging and refactoring existing code, system design, performance optimization, and clean architecture restructuring. Five subagents (Planner, Builder, Fixer, Designer, Reviewer) coordinate through strict phase workflow. Includes deterministic code validation scripts for linting, error scanning, complexity analysis, structure checks. Use when user says \"build me\", \"create an app\", \"make a website\", \"fix this code\", \"debug this\", \"refactor\", \"optimize performance\", \"design a system\", \"clean up this codebase\", \"build an API\", \"create a component\", or describes any software idea or code problem in plain language. Also triggers on \"help me code\", \"I need software\", \"what's wrong with this code\", \"make this faster\", \"restructure this\", or any coding request from a non-technical user.",
    "web-product-studio/image-to-code": "Image-to-code workflow for Claude Code, Claude Cowork, and Codex. For visually important web tasks, it must first generate the design images, analyze them, and implement the website to match them as closely as possible. On any of these hosts, it must prefer large, readable, section-specific images instead of tiny compressed boards, generate fresh standalone images for sections or detail views instead of cropping old ones, avoid lazy under-generation, avoid cards-inside-cards-inside-cards UI, and keep the hero clean, spacious, readable, and visible on a small laptop.",
    "web-product-studio/imagegen-frontend-web": "Generates website design references for landing pages, marketing sites, and product comps. It creates one separate horizontal image for every section; an eight-section landing page produces eight images. Never compress multiple sections into one image. It requires varied composition, background treatment, calls to action, hero scale, a shared narrative concept, second-read details, and one consistent palette so developers or coding models can recreate the design.",
  };

  for (const [key, expected] of Object.entries(skillDescriptions)) {
    const [pluginSlug, skillName] = key.split("/");
    const plugin = catalog.find((entry) => entry.slug === pluginSlug);
    const skill = plugin?.skills.find((entry) => entry.name === skillName);
    assert.equal(skill?.description, expected, key + " routing description changed");
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
