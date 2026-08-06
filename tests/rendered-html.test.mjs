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

test("server-renders the IA registry identity and exact public discovery", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  const text = withoutReactMarkers(html);
  assert.match(text, /Israel(?:&#x27;|')s Plugin Registry/);
  assert.match(text, /\bIA\b/);
  assert.match(text, /21 public plugins and 157 bundled skills/);
  assert.match(text, /21<\/strong><span>Public plugins/);
  assert.match(text, /157<\/strong><span>Bundled skills/);
  assert.match(text, /4<\/strong><span>Outcome collections/);
  assert.match(text, /3<\/strong><span>Verified hosts/);
  assert.match(text, /What changed/);
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
  assert.match(html, /data-testid="plugin-preview"/);
  assert.match(html, /aria-live="polite"/);
  assert.match(text, /Copy only the action shown for a verified host/);
});

test("server-renders complete public records with source and related navigation", async () => {
  const response = await render("/plugins/capability-operator");
  assert.equal(response.status, 200);

  const html = await response.text();
  const text = withoutReactMarkers(html);
  assert.match(text, /Capability Operator/);
  assert.match(text, /Purpose/);
  assert.match(text, /Verified hosts/);
  assert.match(text, /Version/);
  assert.match(text, /Bundled skills/);
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
  assert.equal(totals.skills, 157);
  assert.equal(visiblePlugins.length, 21);

  for (const plugin of visiblePlugins) {
    const response = await render("/plugins/" + plugin.slug);
    assert.equal(response.status, 200, plugin.slug + " detail page must render");
    const html = await response.text();
    const platforms = hostSupport[plugin.slug].platforms;

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
  const publicCatalog = await pluginsResponse.json();
  assert.deepEqual(publicCatalog.counts, totals);
  assert.equal(publicCatalog.plugins.length, 21);
  assert.equal(publicCatalog.collections.length, 4);

  const llmsResponse = await render("/llms.txt");
  assert.equal(llmsResponse.status, 200);
  const llms = await llmsResponse.text();
  assert.match(llms, /Inventory: 21 plugins and 157 skills/);
  assert.match(llms, /Install on Codex:/);
  assert.match(llms, /Install on Claude Code:/);
  assert.match(llms, /Install in Claude Cowork:/);

  for (const value of [JSON.stringify(publicCatalog), llms]) {
    assert.doesNotMatch(value, /matt-partok-bundled-plugin-for-knowledge-work/i);
    assert.doesNotMatch(value, /Matt Partok Bundled Plugin For Knowledge Work/i);
  }
});
