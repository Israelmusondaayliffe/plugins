import {
  collections,
  marketplaceName,
  plugins,
  site,
  totals,
} from "../catalog.generated";

export const dynamic = "force-dynamic";

function renderCatalog() {
  const lines = [
    `# ${site.name}`,
    "",
    site.description,
    "",
    `Inventory: ${totals.plugins} plugins and ${totals.skills} skills.`,
    `Marketplace: ${marketplaceName}.`,
    "",
    "## Collections",
  ];

  for (const collection of collections) {
    lines.push(`### ${collection.name}`);
    lines.push(collection.description);
    lines.push(`Plugins: ${collection.plugins.join(", ")}.`);
    lines.push("");
  }

  lines.push("## Plugins");
  for (const plugin of plugins) {
    lines.push(`### ${plugin.name} (${plugin.slug})`);
    lines.push(plugin.longDescription);
    lines.push(`Category: ${plugin.category}.`);
    lines.push(`Version: ${plugin.version}.`);
    lines.push(`Runtime support: ${plugin.platforms.join(", ")}.`);
    lines.push(`Runtime note: ${plugin.runtimeNote}`);
    lines.push(`Skills: ${plugin.counts.skills}.`);
    if (plugin.platforms.includes("Codex")) {
      lines.push(`Install on Codex: codex plugin add ${plugin.slug}@${marketplaceName}`);
    }
    if (plugin.platforms.includes("Claude Code")) {
      lines.push(`Install on Claude Code: /plugin install ${plugin.slug}@${marketplaceName}`);
    }
    if (plugin.platforms.includes("Claude Cowork")) {
      lines.push("Install in Claude Cowork: https://github.com/Israelmusondaayliffe/plugins");
    }
    lines.push("Best for:");
    for (const item of plugin.guide.bestFor) {
      lines.push(`- ${item}`);
    }
    lines.push("Try asking:");
    for (const item of plugin.guide.quickStarts) {
      lines.push(`- ${item.prompt}`);
    }
    lines.push("Recommended workflow:");
    plugin.guide.workflow.forEach((step, index) => {
      lines.push(
        `${index + 1}. ${step.title}: ${step.instruction} Skills: ${step.skills.join(", ")}.`,
      );
    });
    lines.push(`Bundled skills: ${plugin.skills.map((skill) => skill.name).join(", ")}.`);
    lines.push("");
  }

  return lines.join("\n");
}

export function GET() {
  return new Response(renderCatalog() + "\n", {
    headers: {
      "cache-control": "no-store",
      "content-type": "text/plain; charset=utf-8",
    },
  });
}
