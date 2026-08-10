import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { extname } from "node:path";

const textExtensions = new Set(["", ".cjs", ".css", ".html", ".js", ".json", ".jsx", ".md", ".mjs", ".py", ".sh", ".toml", ".ts", ".tsx", ".txt", ".yaml", ".yml"]);
const files = execFileSync("git", ["ls-files", "-z"]).toString().split("\0").filter(Boolean);
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
const locator = new RegExp(`(?:https://github\\.com/|marketplace add\\s+)${personalAccount}(?:/|$)`);
const problems = [];

for (const file of files) {
  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const text = readFileSync(file, "utf8");
  for (const [label, pattern] of forbidden) {
    for (const [index, line] of text.split("\n").entries()) {
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
