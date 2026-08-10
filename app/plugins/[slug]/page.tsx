import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyCommand } from "../../components/CopyCommand";
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

  return (
    <>
      <header className="site-header shell detail-header">
        <Link className="wordmark" href="/" aria-label={site.name}>
          <span className="wordmark-mark">AP</span>
          <span>{site.name}</span>
        </Link>
        <Link className="back-link" href="/#outcomes">
          Back to registry
        </Link>
      </header>

      <main className="plugin-detail shell">
        <section className="detail-hero">
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
              <dt>Verified hosts</dt>
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

        <section className="detail-install" aria-labelledby="install-title">
          <div>
            <p className="kicker">Verified installation</p>
            <h2 id="install-title">Install on a verified host.</h2>
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

        <section className="skill-list-section">
          <div className="section-heading detail-section-heading">
            <p className="kicker">Bundled capabilities</p>
            <h2>Every skill in this plugin.</h2>
          </div>
          <div className="skill-list">
            {plugin.skills.map((skill, index) => (
              <article key={skill.name}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <h3>{skill.name}</h3>
                  <p>{skill.description}</p>
                </div>
              </article>
            ))}
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
