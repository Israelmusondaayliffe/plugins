import assert from "node:assert/strict";
import { readFileSync, statSync } from "node:fs";
import test from "node:test";

const root = new URL("../", import.meta.url);
const read = (path) => readFileSync(new URL(path, root), "utf8");

test("uses the exact Wada Paper and Sumi tokens", () => {
  const css = read("app/globals.css");
  for (const token of [
    "#F8F5EF", "#FCFBF8", "#EFEDE8", "#292729", "#6B6864", "#DEDAD3", "#B33C49",
    "#121214", "#1A1819", "#242122", "#F1EEE8", "#AAA5A0", "#403B3D", "#D45662",
  ]) {
    assert.ok(css.includes(token), `missing Wada token ${token}`);
  }
  assert.match(css, /:root\[data-theme="sumi"\]/);
  assert.doesNotMatch(css, /linear-gradient|radial-gradient|fractalNoise/);
});

test("maps Wada combination 284 to all four outcomes", () => {
  const css = read("app/globals.css");
  const expected = {
    "--outcome-build": "#FFDD00",
    "--outcome-plan": "#00B49B",
    "--outcome-verify": "#E2625E",
    "--outcome-think": "#004F46",
  };
  for (const [name, value] of Object.entries(expected)) {
    assert.ok(css.includes(`${name}: ${value}`), `${name} must be ${value}`);
  }
  for (const outcome of [
    "outcome-build-and-create",
    "outcome-plan-and-run",
    "outcome-verify-and-govern",
    "outcome-think-communicate-and-preserve",
  ]) {
    assert.ok(css.includes(outcome), `missing outcome marker ${outcome}`);
  }
});

test("defaults to Paper and persists only device-local Sumi state", () => {
  const layout = read("app/layout.tsx");
  const toggle = read("app/components/ThemeToggle.tsx");
  assert.match(toggle, /community-agent-plugins-theme/);
  assert.match(toggle, /localStorage\.setItem/);
  assert.match(toggle, /aria-pressed/);
  assert.match(toggle, /Switch to Sumi theme/);
  assert.match(layout, /localStorage\.getItem/);
  assert.doesNotMatch(layout, /data-theme="sumi"/);
});

test("removes the old image hero and creates a deterministic preview", () => {
  const homepage = read("app/page.tsx");
  const previewScript = read("scripts/generate-social-preview.mjs");
  assert.doesNotMatch(homepage, /plugin-constellation|hero-art|next\/image/);
  assert.match(homepage, /registry-intro/);
  assert.match(previewScript, /WADA COMBINATION #284/);
  assert.match(previewScript, /1200/);
  assert.match(previewScript, /630/);
  assert.ok(statSync(new URL("public/og.png", root)).size > 10_000);
});

test("records Wada as the sole authority and rejects 268 and 336", () => {
  const authority = JSON.parse(read("docs/site-redesign/visual-authority.json"));
  assert.equal(authority.design_constitution, null);
  assert.match(authority.selected_direction, /Wada Paper/);
  assert.deepEqual(
    authority.rejected_directions.map((direction) => direction.name),
    ["Wada combination #268", "Wada combination #336"],
  );
});
