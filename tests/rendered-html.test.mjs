import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);

function generatedExport(name) {
  const catalog = readFileSync(
    new URL("app/catalog.generated.ts", root),
    "utf8",
  );
  const prefix = "export const " + name + " = ";
  const start = catalog.indexOf(prefix);
  assert.notEqual(start, -1, "Missing generated export: " + name);
  const afterPrefix = catalog.slice(start + prefix.length);
  const end = afterPrefix.indexOf(" as const;");
  assert.notEqual(end, -1, "Generated export is incomplete: " + name);
  return JSON.parse(afterPrefix.slice(0, end).trim());
}

const marketplaceName = generatedExport("marketplaceName");
const visiblePlugins = generatedExport("plugins");
const totals = generatedExport("totals");
const collections = generatedExport("collections");
const hostSupport = JSON.parse(
  readFileSync(new URL("docs/host-support.json", root), "utf8"),
);
const owner = ["Israel", "musonda", "ayliffe"].join("");

function withoutReactMarkers(html) {
  return html.replace(/<!--[\s\S]*?-->/g, "");
}

function escapeRegex(value) {
  return value.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}

async function render(pathname = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", process.pid + "-" + Date.now());
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost" + pathname, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the depersonalized registry identity and exact public discovery", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  const text = withoutReactMarkers(html);
  assert.match(text, /Community Agent Plugins/);
  assert.match(text, /\bAP\b/);
  assert.match(text, /21 public plugins and 160 bundled skills/);
  assert.match(text, /21<\/strong><span>Public plugins/);
  assert.match(text, /160<\/strong><span>Bundled skills/);
  assert.match(text, /04<\/strong><span>Outcome groups/);
  assert.match(text, /03<\/strong><span>Verified hosts/);
  assert.match(text, /Current edition/);
  assert.match(text, /Gauntlet and Gauntlet Loop/);
  assert.match(text, /Capability Operator, Agent Ops, and\s+Harness Engineering/);

  assert.equal(collections.length, 4);
  for (const collection of [
    "Build and create",
    "Plan and run",
    "Verify and govern",
    "Think, communicate, and preserve",
  ]) {
    assert.match(text, new RegExp(collection));
  }
  for (const host of ["Codex", "Claude Code", "Claude Cowork"]) {
    assert.match(text, new RegExp(host));
  }
  assert.match(html, /data-testid="collection-filter"/);
  assert.match(html, /data-testid="host-filter"/);
  assert.match(html, /aria-keyshortcuts="\/"/);
  assert.match(html, /data-testid="theme-toggle"/);
  assert.match(html, /aria-label="Switch to Sumi theme"/);
  assert.doesNotMatch(html, /plugin-constellation/);
  assert.doesNotMatch(html, /data-testid="plugin-preview"/);
  assert.match(html, /aria-live="polite"/);
  for (const plugin of visiblePlugins) {
    assert.ok(
      html.includes('data-testid="plugin-row-' + plugin.slug + '"') &&
        html.includes('href="/plugins/' + plugin.slug + '"'),
      plugin.slug + " must render as a direct detail-page link",
    );
    assert.match(text, new RegExp(escapeRegex(plugin.description)));
  }
});

test("server-renders a guided public record with source and related navigation", async () => {
  const response = await render("/plugins/capability-operator");
  assert.equal(response.status, 200);

  const html = await response.text();
  const text = withoutReactMarkers(html);
  assert.match(text, /Capability Operator/);
  assert.match(text, /Purpose/);
  assert.match(text, /Verified hosts/);
  assert.match(text, /Version/);
  assert.match(text, /Bundled skills/);
  assert.match(html, /aria-label="On this page"/);
  for (const id of ["install", "start", "workflow", "skill-guide", "all-skills"]) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }
  assert.match(text, /Begin with the front door/);
  assert.match(text, /What this plugin is best for/);
  assert.match(text, /A practical way to use it/);
  assert.match(text, /Start from the job in front of you/);
  assert.match(text, /Worked example/);
  assert.match(text, /Boundaries/);
  assert.match(text, /Success signals/);
  assert.ok(
    (html.match(/Copy [^"]+ prompt:/g) ?? []).length >= 3,
    "guide must render three prompt copy controls",
  );
  assert.match(text, /Source you can inspect/);
  assert.match(
    html,
    new RegExp(
      "https://github.com/" +
        owner +
        "/plugins/tree/main/plugins/capability-operator",
    ),
  );
  assert.match(text, /Related plugins/);
  const relatedCount = (html.match(/data-testid="related-plugin"/g) ?? []).length;
  assert.ok(relatedCount > 0 && relatedCount <= 3);
  assert.match(html, /aria-live="polite"/);
});

test("only renders install actions for each verified host", async () => {
  const codexOnlyResponse = await render("/plugins/gauntlet-loop");
  assert.equal(codexOnlyResponse.status, 200);
  const codexOnlyHtml = await codexOnlyResponse.text();
  assert.match(codexOnlyHtml, /data-install-host="Codex"/);
  assert.doesNotMatch(codexOnlyHtml, /data-install-host="Claude Code"/);
  assert.doesNotMatch(codexOnlyHtml, /data-install-host="Claude Cowork"/);
  assert.match(
    codexOnlyHtml,
    new RegExp(
      "codex plugin add gauntlet-loop@" + marketplaceName,
    ),
  );
  assert.doesNotMatch(
    codexOnlyHtml,
    new RegExp("/plugin install gauntlet-loop@" + marketplaceName),
  );

  const claudeOnlyResponse = await render("/plugins/gauntlet");
  assert.equal(claudeOnlyResponse.status, 200);
  const claudeOnlyHtml = await claudeOnlyResponse.text();
  assert.doesNotMatch(claudeOnlyHtml, /data-install-host="Codex"/);
  assert.match(claudeOnlyHtml, /data-install-host="Claude Code"/);
  assert.match(claudeOnlyHtml, /data-install-host="Claude Cowork"/);
  assert.doesNotMatch(
    claudeOnlyHtml,
    new RegExp("codex plugin add gauntlet@" + marketplaceName),
  );
  assert.match(
    claudeOnlyHtml,
    new RegExp("/plugin install gauntlet@" + marketplaceName),
  );
});

test("renders all and only the public static plugin routes", async () => {
  assert.equal(totals.plugins, 21);
  assert.equal(totals.skills, 160);
  assert.equal(visiblePlugins.length, 21);

  for (const plugin of visiblePlugins) {
    const response = await render("/plugins/" + plugin.slug);
    assert.equal(response.status, 200, plugin.slug + " detail page must render");
    const html = await response.text();
    const platforms = hostSupport[plugin.slug].platforms;

    assert.match(html, /id="start"/, plugin.slug + " start section must render");
    assert.match(html, /id="workflow"/, plugin.slug + " workflow must render");
    assert.match(html, /id="skill-guide"/, plugin.slug + " skill guide must render");
    assert.match(html, /id="all-skills"/, plugin.slug + " complete skill list must render");
    for (const quickStart of plugin.guide.quickStarts) {
      assert.ok(
        html.includes(quickStart.prompt.replaceAll("&", "&amp;")),
        plugin.slug + " quick-start prompt must render",
      );
    }
    assert.equal(
      html.includes("codex plugin add " + plugin.slug + "@" + marketplaceName),
      platforms.includes("Codex"),
      plugin.slug + " Codex install visibility must match runtime support",
    );
    assert.equal(
      html.includes("/plugin install " + plugin.slug + "@" + marketplaceName),
      platforms.includes("Claude Code"),
      plugin.slug + " Claude Code install visibility must match runtime support",
    );
    assert.equal(
      html.includes('data-install-host="Claude Cowork"'),
      platforms.includes("Claude Cowork"),
      plugin.slug + " Cowork install visibility must match runtime support",
    );
  }

  const unknownResponse = await render("/plugins/not-a-public-plugin");
  assert.equal(unknownResponse.status, 404);

  const excludedResponse = await render(
    "/plugins/matt-partok-bundled-plugin-for-knowledge-work",
  );
  assert.equal(excludedResponse.status, 404);
});

test("serves public discovery exports from the visible catalog", async () => {
  const pluginsResponse = await render("/plugins.json");
  assert.equal(pluginsResponse.status, 200);
  assert.equal(pluginsResponse.headers.get("cache-control"), "no-store");
  const publicCatalog = await pluginsResponse.json();
  assert.deepEqual(publicCatalog.counts, totals);
  assert.equal(publicCatalog.plugins.length, 21);
  assert.equal(publicCatalog.collections.length, 4);
  for (const plugin of publicCatalog.plugins) {
    assert.ok(plugin.guide, plugin.slug + " guide must be public");
    assert.equal(plugin.guide.quickStarts.length, 3);
    assert.ok(plugin.guide.workflow.length >= 3);
  }

  const llmsResponse = await render("/llms.txt");
  assert.equal(llmsResponse.status, 200);
  assert.equal(llmsResponse.headers.get("cache-control"), "no-store");
  const llms = await llmsResponse.text();
  assert.match(llms, /Inventory: 21 plugins and 160 skills/);
  assert.match(llms, /Install on Codex:/);
  assert.match(llms, /Install on Claude Code:/);
  assert.match(llms, /Install in Claude Cowork:/);
  assert.match(llms, /Best for:/);
  assert.match(llms, /Try asking:/);
  assert.match(llms, /Recommended workflow:/);

  for (const value of [JSON.stringify(publicCatalog), llms]) {
    assert.doesNotMatch(value, /matt-partok-bundled-plugin-for-knowledge-work/i);
    assert.doesNotMatch(value, /Matt Partok Bundled Plugin For Knowledge Work/i);
  }
});
