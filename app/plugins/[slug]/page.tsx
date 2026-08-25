import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyCommand } from "../../components/CopyCommand";
import { SignalSkillChooser } from "../../components/SignalSkillChooser";
import { ThemeToggle } from "../../components/ThemeToggle";
import {
  collections,
  marketplaceName,
  plugins,
  site,
} from "../../catalog.generated";

type PluginPageProps = {
  params: Promise<{ slug: string }>;
};

const repositoryUrl =
  "https://github.com/Israelmusondaayliffe/plugins";

export const dynamicParams = false;

export function generateStaticParams() {
  return plugins.map((plugin) => ({ slug: plugin.slug }));
}

export async function generateMetadata({
  params,
}: PluginPageProps): Promise<Metadata> {
  const { slug } = await params;
  const plugin = plugins.find((item) => item.slug === slug);
  if (!plugin) return {};
  return {
    title: plugin.name,
    description: plugin.longDescription,
  };
}

export default async function PluginPage({ params }: PluginPageProps) {
  const { slug } = await params;
  const plugin = plugins.find((item) => item.slug === slug);
  if (!plugin) notFound();

  const collection = collections.find((item) =>
    item.plugins.some((pluginSlug) => pluginSlug === plugin.slug),
  );
  const relatedPlugins = collection
    ? plugins
        .filter(
          (item) =>
            item.slug !== plugin.slug &&
            collection.plugins.some((pluginSlug) => pluginSlug === item.slug),
        )
        .slice(0, 3)
    : [];
  const isSignalToSystem = plugin.slug === "signal-to-system";
  const isDeclaredBeta = plugin.supportStatus === "declared-beta";

  return (
    <>
      <header className="site-header shell detail-header">
        <Link className="wordmark" href="/" aria-label={site.name}>
          <span className="wordmark-mark">AP</span>
          <span>{site.name}</span>
        </Link>
        <div className="header-actions">
          <Link className="back-link" href="/#outcomes">Back to registry</Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="plugin-detail shell">
        <section className={"detail-hero outcome-" + (collection?.slug ?? "uncategorized")}>
          <div className="detail-heading">
            <p className="kicker">
              {collection?.name ?? plugin.category} collection
            </p>
            <p className="detail-purpose-label">Purpose</p>
            <h1>{plugin.name}</h1>
            <p>{plugin.description}</p>
          </div>
          <dl className="detail-stats">
            <div>
              <dt>Version</dt>
              <dd>{plugin.version}</dd>
            </div>
            <div>
              <dt>Bundled skills</dt>
              <dd>{plugin.counts.skills}</dd>
            </div>
            <div>
              <dt>{isDeclaredBeta ? "Declared beta hosts" : "Verified hosts"}</dt>
              <dd>
                <span className="host-badges">
                  {plugin.platforms.map((platform) => (
                    <span key={platform}>{platform}</span>
                  ))}
                </span>
              </dd>
            </div>
            <div>
              <dt>Files</dt>
              <dd>{plugin.counts.files}</dd>
            </div>
            <div>
              <dt>License</dt>
              <dd>{plugin.license ?? "See legal"}</dd>
            </div>
          </dl>
        </section>

        <nav className="detail-nav" aria-label="On this page">
          <span>On this page</span>
          <a href="#install">Install</a>
          {isSignalToSystem && <a href="#choose">Choose</a>}
          <a href="#start">Start</a>
          <a href="#workflow">Workflow</a>
          <a href="#skill-guide">Skill guide</a>
          <a href="#all-skills">All skills</a>
        </nav>

        <section
          className="detail-install"
          aria-labelledby="install-title"
          id="install"
        >
          <div>
            <p className="kicker">
              {isDeclaredBeta ? "Beta package installation" : "Verified installation"}
            </p>
            <h2 id="install-title">
              {isDeclaredBeta ? "Install on a declared beta host." : "Install on a verified host."}
            </h2>
            <p className="install-note">
              {plugin.runtimeNote} Package manifests and runtime verification
              are separate claims.
            </p>
          </div>
          <div className="detail-platform-installs">
            {plugin.platforms.includes("Codex") && (
              <article data-install-host="Codex">
                <p className="platform-eyebrow">Codex</p>
                <CopyCommand
                  command={
                    "codex plugin add " + plugin.slug + "@" + marketplaceName
                  }
                  label="Codex install command"
                />
                <p className="install-note">
                  Add the marketplace first if needed, then start a fresh task.
                </p>
              </article>
            )}
            {plugin.platforms.includes("Claude Code") && (
              <article data-install-host="Claude Code">
                <p className="platform-eyebrow">Claude Code</p>
                <CopyCommand
                  command={
                    "/plugin install " + plugin.slug + "@" + marketplaceName
                  }
                  label="Claude Code install command"
                />
                <p className="install-note">
                  Add this repository as a marketplace first if needed.
                </p>
              </article>
            )}
            {plugin.platforms.includes("Claude Cowork") && (
              <article data-install-host="Claude Cowork">
                <p className="platform-eyebrow">Claude Cowork</p>
                <CopyCommand
                  command={repositoryUrl}
                  label="Claude Cowork marketplace URL"
                />
                <p className="install-note">
                  In Customize → Plugins, add this marketplace and select{" "}
                  {plugin.name}.
                </p>
              </article>
            )}
          </div>
        </section>

        {isSignalToSystem && <SignalSkillChooser />}

        <section
          className="guide-section guide-start"
          aria-labelledby="start-title"
          id="start"
        >
          <div className="section-heading detail-section-heading">
            <p className="kicker">Start here</p>
            <h2 id="start-title">
              {isSignalToSystem
                ? "Start with the job, not a hidden router."
                : "Begin with the front door."}
            </h2>
            {isSignalToSystem ? (
              <p>
                Each skill works independently. Use the chooser when you want a
                recommendation, or name the exact skill when the job is clear.
              </p>
            ) : (
              <p>
                You do not need to memorize every skill. Start with{" "}
                <code>{plugin.guide.startHere.skill}</code> and describe the
                result you want.
              </p>
            )}
          </div>
          <div className="start-here-card">
            <div>
              <p className="guide-eyebrow">
                {isSignalToSystem
                  ? "Default when the direction is unclear"
                  : "Recommended first skill"}
              </p>
              <h3>{plugin.guide.startHere.skill}</h3>
              <p>{plugin.guide.startHere.why}</p>
            </div>
            <div className="quick-starts" aria-label="Copyable starting prompts">
              {plugin.guide.quickStarts.map((item) => (
                <article key={item.goal}>
                  <p className="guide-eyebrow">{item.goal}</p>
                  <CopyCommand
                    command={item.prompt}
                    label={item.goal + " prompt"}
                  />
                </article>
              ))}
            </div>
          </div>
        </section>

        <section
          className="guide-section best-for-section"
          aria-labelledby="best-for-title"
        >
          <div className="section-heading detail-section-heading">
            <p className="kicker">Good fit</p>
            <h2 id="best-for-title">What this plugin is best for.</h2>
          </div>
          <ul className="best-for-list">
            {plugin.guide.bestFor.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section
          className="guide-section workflow-section"
          aria-labelledby="workflow-title"
          id="workflow"
        >
          <div className="section-heading detail-section-heading">
            <p className="kicker">Recommended workflow</p>
            <h2 id="workflow-title">A practical way to use it.</h2>
            <p>
              Follow these steps in order for a complete job. For a smaller
              request, use only the step that fits.
            </p>
          </div>
          <ol className="workflow-list">
            {plugin.guide.workflow.map((step, index) => (
              <li key={step.title}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.instruction}</p>
                  <p className="skill-route">
                    Skills:{" "}
                    {step.skills.map((skill, skillIndex) => (
                      <span key={skill}>
                        {skillIndex > 0 ? ", " : ""}
                        <code>{skill}</code>
                      </span>
                    ))}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section
          className="guide-section skill-guide-section"
          aria-labelledby="skill-guide-title"
          id="skill-guide"
        >
          <div className="section-heading detail-section-heading">
            <p className="kicker">Choose the right skill</p>
            <h2 id="skill-guide-title">Start from the job in front of you.</h2>
            <p>
              Find the sentence closest to what you need, then name that skill
              in your request.
            </p>
          </div>
          <div className="skill-paths">
            {plugin.guide.skillPaths.map((path) => (
              <article key={path.need}>
                <p>{path.need}</p>
                <h3>{path.skill}</h3>
                <p>{path.why}</p>
              </article>
            ))}
          </div>
        </section>

        <section
          className="guide-section worked-example"
          aria-labelledby="example-title"
        >
          <div className="section-heading detail-section-heading">
            <p className="kicker">
              {isSignalToSystem ? "Illustrative route" : "Worked example"}
            </p>
            <h2 id="example-title">{plugin.guide.workedExample.title}</h2>
            <p>{plugin.guide.workedExample.situation}</p>
          </div>
          <div className="example-body">
            <ol>
              {plugin.guide.workedExample.steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <div>
              <p className="guide-eyebrow">What a useful result looks like</p>
              <p>{plugin.guide.workedExample.result}</p>
            </div>
          </div>
        </section>

        <section className="guidance-grid" aria-label="Practical guidance">
          <article>
            <p className="kicker">Better inputs</p>
            <h2>Tips.</h2>
            <ul>
              {plugin.guide.tips.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article>
            <p className="kicker">Know the limits</p>
            <h2>Boundaries.</h2>
            <ul>
              {plugin.guide.boundaries.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article>
            <p className="kicker">Completion check</p>
            <h2>Success signals.</h2>
            <ul>
              {plugin.guide.successSignals.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </section>

        <section className="skill-list-section" id="all-skills">
          <div className="section-heading detail-section-heading">
            <p className="kicker">Bundled capabilities</p>
            <h2>Every skill in this plugin.</h2>
          </div>
          <div className="skill-list">
            {plugin.skills.map((skill, index) => {
              const content = (
                <>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <h3>{skill.name}</h3>
                    <p>{skill.description}</p>
                  </div>
                  {isSignalToSystem && (
                    <span className="signal-row-arrow" aria-hidden="true">↗</span>
                  )}
                </>
              );
              return isSignalToSystem ? (
                <Link
                  className="signal-skill-row"
                  href={"/plugins/signal-to-system/skills/" + skill.name}
                  key={skill.name}
                >
                  {content}
                </Link>
              ) : (
                <article key={skill.name}>{content}</article>
              );
            })}
          </div>
        </section>

        {collection && relatedPlugins.length > 0 && (
          <section
            className="related-section"
            aria-labelledby="related-plugins-title"
          >
            <div className="section-heading related-heading">
              <p className="kicker">{collection.name}</p>
              <h2 id="related-plugins-title">Related plugins.</h2>
              <p>Continue with another package built for the same outcome.</p>
            </div>
            <div className="related-grid">
              {relatedPlugins.map((item) => (
                <Link
                  data-testid="related-plugin"
                  href={"/plugins/" + item.slug}
                  key={item.slug}
                >
                  <span>{item.counts.skills} skills</span>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <span aria-hidden="true">↗</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="package-section">
          <div>
            <h2>Source you can inspect.</h2>
            <a
              className="text-link"
              href={repositoryUrl + "/tree/main/plugins/" + plugin.slug}
            >
              Open this plugin on GitHub
            </a>
          </div>
          <dl className="package-facts">
            <div>
              <dt>Assets</dt>
              <dd>{plugin.counts.assets}</dd>
            </div>
            <div>
              <dt>References</dt>
              <dd>{plugin.counts.references}</dd>
            </div>
            <div>
              <dt>Scripts</dt>
              <dd>{plugin.counts.scripts}</dd>
            </div>
            <div>
              <dt>Total files</dt>
              <dd>{plugin.counts.files}</dd>
            </div>
          </dl>
        </section>
      </main>

      <footer>
        <div className="shell footer-grid">
          <p className="footer-name">{site.name}</p>
          <Link href="/#outcomes">Browse all plugins</Link>
        </div>
      </footer>
    </>
  );
}
