import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";

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

test("server-renders the public marketplace homepage", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Israel&#x27;s Plugin Registry<\/title>/i);
  assert.match(html, /A working system/);
  assert.match(html, /21(?:<!--.*?-->)? field-tested plugins/);
  assert.match(html, /Codex, Claude Code, and(?:<!--.*?-->)?\s*Claude Cowork/);
  assert.match(html, /codex plugin marketplace add Israelmusondaayliffe/);
  assert.match(html, /\/plugin marketplace add Israelmusondaayliffe/);
  assert.match(
    html,
    /https:\/\/github.com\/Israelmusondaayliffe\/plugins/,
  );
  assert.match(html, /Official Cowork install guide/);
  assert.match(html, /knowledge-work-superpowers/);
  assert.match(html, /LoopKit/);
  assert.match(html, /Harness Engineering/);
  assert.match(html, /does not currently.*MCP servers/i);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/);
});

test("server-renders plugin detail pages", async () => {
  const response = await render("/plugins/capability-operator");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Capability Operator/);
  assert.match(html, /capability-router/);
  assert.match(
    html,
    /codex plugin add capability-operator@israel-plugins/,
  );
  assert.match(
    html,
    /\/plugin install capability-operator@israel-plugins/,
  );
  assert.match(html, /In Customize → Plugins/);
});

test("server-renders the Harness Engineering release", async () => {
  const response = await render("/plugins/harness-engineering");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Harness Engineering/);
  assert.match(html, /harness-interview/);
  assert.match(
    html,
    /codex plugin add harness-engineering@israel-plugins/,
  );
});

test("server-renders the LoopKit release", async () => {
  const response = await render("/plugins/loopkit");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /LoopKit/);
  assert.match(html, /loop-runner/);
  assert.match(
    html,
    /codex plugin add loopkit@israel-plugins/,
  );
});

test("server-renders the Citizen Forge release", async () => {
  const response = await render("/plugins/citizen-forge");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Citizen Forge/);
  assert.match(html, /citizen-release/);
  assert.match(html, /questions such as &quot;is this safe\?&quot;/);
  assert.match(
    html,
    /codex plugin add citizen-forge@israel-plugins/,
  );
});

test("server-renders the Operating Graph release", async () => {
  const response = await render("/plugins/operating-graph");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Operating Graph/);
  assert.match(html, /graph-verify/);
  assert.match(
    html,
    /codex plugin add operating-graph@israel-plugins/,
  );
  assert.match(
    html,
    /\/plugin install operating-graph@israel-plugins/,
  );
});

test("server-renders the Gauntlet Loop release", async () => {
  const response = await render("/plugins/gauntlet-loop");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Gauntlet Loop/);
  assert.match(html, /gauntlet-verify/);
  assert.match(
    html,
    /codex plugin add gauntlet-loop@israel-plugins/,
  );
});

test("publishes every plugin across both manifest formats and all install surfaces", async () => {
  const codexMarketplace = JSON.parse(
    readFileSync(
      new URL("../.agents/plugins/marketplace.json", import.meta.url),
      "utf8",
    ),
  );
  const claudeMarketplace = JSON.parse(
    readFileSync(
      new URL("../.claude-plugin/marketplace.json", import.meta.url),
      "utf8",
    ),
  );
  const codexNames = codexMarketplace.plugins.map((plugin) => plugin.name).sort();
  const claudeNames = claudeMarketplace.plugins
    .map((plugin) => plugin.name)
    .sort();

  assert.equal(codexNames.length, 21);
  assert.deepEqual(claudeNames, codexNames);

  for (const name of codexNames) {
    assert.equal(
      existsSync(
        new URL(`../plugins/${name}/.codex-plugin/plugin.json`, import.meta.url),
      ),
      true,
      `${name} must include a Codex manifest`,
    );
    assert.equal(
      existsSync(
        new URL(`../plugins/${name}/.claude-plugin/plugin.json`, import.meta.url),
      ),
      true,
      `${name} must include a Claude manifest`,
    );

    const response = await render(`/plugins/${name}`);
    assert.equal(response.status, 200, `${name} detail page must render`);
    const html = await response.text();
    assert.ok(
      html.includes(`codex plugin add ${name}@israel-plugins`),
      `${name} must expose its Codex install command`,
    );
    assert.ok(
      html.includes(`/plugin install ${name}@israel-plugins`),
      `${name} must expose its Claude Code install command`,
    );
    assert.ok(
      html.includes("Claude Cowork"),
      `${name} must expose its Claude Cowork install path`,
    );
  }
});
