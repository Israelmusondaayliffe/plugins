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
  assert.match(html, /<title>Community Agent Plugins<\/title>/i);
  assert.match(html, /A working system/);
  assert.match(html, /22(?:<!--.*?-->)? field-tested plugins/);
  assert.match(html, /179(?:<!--.*?-->)?\s*<\/strong>\s*<span>Bundled skills/);
  assert.match(html, /Codex, Claude Code, and(?:<!--.*?-->)?\s*Claude Cowork/);
  const owner = ["Israel", "musonda", "ayliffe"].join("");
  assert.match(html, new RegExp(`codex plugin marketplace add ${owner}`));
  assert.match(html, new RegExp(`/plugin marketplace add ${owner}`));
  assert.match(
    html,
    new RegExp(`https://github.com/${owner}/plugins`),
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
    /codex plugin add capability-operator@community-agent-plugins/,
  );
  assert.match(
    html,
    /\/plugin install capability-operator@community-agent-plugins/,
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
    /codex plugin add harness-engineering@community-agent-plugins/,
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
    /codex plugin add loopkit@community-agent-plugins/,
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
    /codex plugin add citizen-forge@community-agent-plugins/,
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
    /codex plugin add operating-graph@community-agent-plugins/,
  );
  assert.match(
    html,
    /\/plugin install operating-graph@community-agent-plugins/,
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
    /codex plugin add gauntlet-loop@community-agent-plugins/,
  );
});

test("publishes every plugin with exact manifest and runtime-host claims", async () => {
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
  const hostSupport = JSON.parse(
    readFileSync(
      new URL("../docs/host-support.json", import.meta.url),
      "utf8",
    ),
  );

  assert.equal(codexNames.length, 22);
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
    const runtimePlatforms = hostSupport[name].platforms;
    assert.equal(
      html.includes(`codex plugin add ${name}@community-agent-plugins`),
      runtimePlatforms.includes("Codex"),
      `${name} Codex install visibility must match verified runtime support`,
    );
    assert.equal(
      html.includes(`/plugin install ${name}@community-agent-plugins`),
      runtimePlatforms.includes("Claude Code"),
      `${name} Claude Code install visibility must match verified runtime support`,
    );
    assert.equal(
      html.includes('platform-eyebrow">Claude Cowork'),
      runtimePlatforms.includes("Claude Cowork"),
      `${name} Cowork install visibility must match verified runtime support`,
    );
  }
});
