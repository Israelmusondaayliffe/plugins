import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { extname } from "node:path";

const textExtensions = new Set(["", ".cjs", ".css", ".html", ".js", ".json", ".jsx", ".md", ".mjs", ".py", ".sh", ".toml", ".ts", ".tsx", ".txt", ".yaml", ".yml"]);
const files = execFileSync("git", [
  "ls-files",
  "--cached",
  "--others",
  "--exclude-standard",
  "-z",
]).toString().split("\0").filter(Boolean);
const personalFirstName = ["Is", "rael"].join("");
const personalSurname = ["Ay", "liffe"].join("");
const personalAccount = [personalFirstName, "musonda", personalSurname.toLowerCase()].join("");
const localUser = [personalFirstName.toLowerCase(), personalSurname.toLowerCase()].join("");
const forbidden = [
  ["personal name", new RegExp(`${personalFirstName}(?: A\\.| ${personalSurname}|'s)`, "i")],
  ["personal home path", new RegExp(`/(?:Users|home)/${localUser}`, "i")],
  ["old marketplace identity", new RegExp(`${personalFirstName.toLowerCase()}-(?:codex-)?plugins`, "i")],
  ["personal hosted site", new RegExp(`${personalSurname.toLowerCase()}\\.chatgpt\\.site`, "i")],
];
const canonicalPublicSite = [
  "https://",
  personalFirstName.toLowerCase(),
  "-codex-plugins.",
  localUser,
  ".chatgpt.site",
].join("");
const unslopSkillPrefix = "plugins/harness-engineering/skills/unslop-harness-repair/";
const unslopManifest = JSON.parse(
  readFileSync(`${unslopSkillPrefix}references/unslop-engine-manifest.json`, "utf8"),
);
const pinnedUnslopFiles = new Set(
  Object.keys(unslopManifest.files).map((relative) => `${unslopSkillPrefix}${relative}`),
);
const pinnedPersonalNameLines = new Map([
  [
    `${unslopSkillPrefix}references/unslop-engine/unslop-policy.md`,
    new Set([`- Use no em dashes in authored prose under ${personalFirstName}'s global rule.`]),
  ],
  [
    `${unslopSkillPrefix}references/unslop-engine/word-replacement-table.md`,
    new Set([
      `${personalFirstName}'s Law applies throughout: if a simpler word conveys the same meaning, that is always the right choice.`,
      `Tier system adapted from avoid-ai-writing (conorbronsdon, MIT license) and humanizer/blader. Table extended with ${personalFirstName}'s Rule Zero (simple words always preferred) and OQE-v3 patterns.`,
    ]),
  ],
  [
    `${unslopSkillPrefix}references/unslop-engine/workflow.md`,
    new Set([`## ${personalFirstName}'s Law (Rule Zero)`]),
  ],
]);
const allowedPinnedEnginePersonalName = (file, line, label) =>
  label === "personal name" &&
  pinnedUnslopFiles.has(file) &&
  pinnedPersonalNameLines.get(file)?.has(line.trim());
const allowedPublicLocator = (file, line) =>
  file === "docs/site-redesign/release-evidence.json" &&
  line.includes(`\"deployed_url\": \"${canonicalPublicSite}\"`);
const locator = new RegExp(`(?:https://github\\.com/|marketplace add\\s+)${personalAccount}(?:/|$)`);
const problems = [];

for (const file of files) {
  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const text = readFileSync(file, "utf8");
  for (const [label, pattern] of forbidden) {
    for (const [index, line] of text.split("\n").entries()) {
      if (
        allowedPublicLocator(file, line) &&
        (label === "old marketplace identity" || label === "personal hosted site")
      ) {
        continue;
      }
      if (allowedPinnedEnginePersonalName(file, line, label)) continue;
      if (pattern.test(line)) problems.push(`${label}: ${file}:${index + 1}`);
    }
  }
  for (const [index, line] of text.split("\n").entries()) {
    if (line.includes(personalAccount) && !locator.test(line)) {
      problems.push(`owner slug outside locator: ${file}:${index + 1}`);
    }
  }
}

if (problems.length) {
  for (const problem of [...new Set(problems)].sort()) console.error(`FAIL: ${problem}`);
  process.exit(1);
}
console.log(JSON.stringify({ status: "PASS", filesChecked: files.length }, null, 2));
