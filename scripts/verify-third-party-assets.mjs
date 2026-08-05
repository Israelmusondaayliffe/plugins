import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const pluginsRoot = join(root, "plugins");
const binaryExtensions = new Set([
  ".aac",
  ".gif",
  ".jpeg",
  ".jpg",
  ".m4a",
  ".mov",
  ".mp3",
  ".mp4",
  ".otf",
  ".png",
  ".svg",
  ".ttf",
  ".wav",
  ".webp",
  ".woff",
  ".woff2",
]);
const failures = [];

function walk(directory) {
  const files = [];
  for (const name of readdirSync(directory)) {
    const path = join(directory, name);
    if (statSync(path).isDirectory()) files.push(...walk(path));
    else files.push(path);
  }
  return files;
}

function requireFile(path, reason) {
  if (!existsSync(join(root, path))) failures.push(`${reason}: missing ${path}`);
}

function covered(path) {
  const fontPrefix =
    "plugins/video-production-studio/skills/embedded-captions/modes/standard/fonts/files/";
  if (path.startsWith(fontPrefix)) {
    const name = path.slice(fontPrefix.length);
    const match = name.match(/^(.+)-latin-\d+-(?:normal|italic)\.woff2$/);
    if (!match) return false;
    requireFile(
      `plugins/video-production-studio/third-party-licenses/fontsource/${match[1]}.txt`,
      `Font license for ${path}`,
    );
    return true;
  }
  if (
    path ===
    "plugins/video-production-studio/skills/music-to-video/references/templates/logo-split-lockup-pulse/assets/fredoka-700.woff2"
  ) {
    requireFile(
      "plugins/video-production-studio/third-party-licenses/fontsource/fredoka.txt",
      `Font license for ${path}`,
    );
    return true;
  }
  if (
    path.startsWith(
      "plugins/video-production-studio/skills/music-to-video/references/templates/held-text-strobe-burst/assets/texture-mask-text/masks/",
    )
  ) {
    requireFile(
      "plugins/video-production-studio/third-party-licenses/hyperframes-apache-2.0.txt",
      `Hyperframes license for ${path}`,
    );
    return true;
  }
  if (
    path.startsWith(
      "plugins/video-production-studio/skills/graphic-overlays/assets/fonts/",
    )
  ) {
    requireFile(
      "plugins/video-production-studio/skills/graphic-overlays/NOTICE.md",
      `MIT notice for ${path}`,
    );
    return true;
  }
  if (
    path.startsWith(
      "plugins/video-production-studio/skills/website-to-video/assets/sfx/",
    )
  ) {
    requireFile(
      "plugins/video-production-studio/skills/website-to-video/assets/sfx/CREDITS.md",
      `SFX credits for ${path}`,
    );
    return true;
  }
  if (
    path.startsWith(
      "plugins/video-production-studio/skills/embedded-captions/assets/strokefonts/",
    )
  ) {
    const text = readFileSync(join(root, path), "utf8");
    return (
      text.includes("USE RESTRICTION:") &&
      text.includes("The Hershey Fonts were originally created by Dr.") &&
      text.includes("The format of the Font data in this distribution")
    );
  }
  if (path.startsWith("plugins/web-product-studio/skills/playwright/assets/")) {
    requireFile(
      "plugins/web-product-studio/skills/playwright/LICENSE.txt",
      `Playwright license for ${path}`,
    );
    requireFile(
      "plugins/web-product-studio/skills/playwright/NOTICE.txt",
      `Playwright notice for ${path}`,
    );
    return true;
  }
  return false;
}

for (const absolutePath of walk(pluginsRoot)) {
  const path = relative(root, absolutePath);
  if (!binaryExtensions.has(extname(path).toLowerCase())) continue;
  if (!covered(path)) failures.push(`Unlicensed or unclassified asset: ${path}`);
}

for (const forbidden of [
  "CyberpunkReplica.ttf",
  "CyberpunkReplica.woff",
  "CyberpunkReplica.woff2",
]) {
  if (walk(pluginsRoot).some((path) => path.endsWith(forbidden))) {
    failures.push(`Proprietary font must not be distributed: ${forbidden}`);
  }
}

if (failures.length) {
  for (const failure of failures) console.error(`FAIL: ${failure}`);
  process.exit(1);
}
console.log(JSON.stringify({ status: "PASS", assetPolicy: "licensed-only" }, null, 2));
