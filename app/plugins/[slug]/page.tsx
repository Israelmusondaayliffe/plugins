import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyCommand } from "../../components/CopyCommand";
import { marketplaceName, plugins } from "../../catalog.generated";

type PluginPageProps = {
  params: Promise<{ slug: string }>;
};

const repositoryUrl =
  "https://github.com/Israelmusondaayliffe/plugins";

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

  return (
    <>
      <header className="site-header shell detail-header">
        <Link className="wordmark" href="/" aria-label="Back to plugin catalog">
          <span className="wordmark-mark">IA</span>
          <span>PLUGIN REGISTRY</span>
        </Link>
        <Link className="back-link" href="/#plugins">
          Back to catalog
        </Link>
      </header>

      <main className="plugin-detail shell">
        <section className="detail-hero">
          <div className="detail-heading">
            <p className="kicker">{plugin.category} plugin</p>
            <h1>{plugin.name}</h1>
            <p>{plugin.longDescription}</p>
          </div>
          <dl className="detail-stats">
            <div>
              <dt>Version</dt>
              <dd>{plugin.version}</dd>
            </div>
            <div>
              <dt>Skills</dt>
              <dd>{plugin.counts.skills}</dd>
            </div>
            <div>
              <dt>Files</dt>
              <dd>{plugin.counts.files}</dd>
            </div>
            <div>
              <dt>Platforms</dt>
              <dd>{plugin.platforms.length}</dd>
            </div>
            <div>
              <dt>License</dt>
              <dd>{plugin.license ?? "See legal"}</dd>
            </div>
          </dl>
        </section>

        <section className="detail-install" aria-labelledby="install-title">
          <div>
            <h2 id="install-title">Install it on your surface.</h2>
            <p className="install-note">
              The same package is available in Codex, Claude Code, and Claude
              Cowork.
            </p>
          </div>
          <div className="detail-platform-installs">
            <article>
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
            <article>
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
            <article>
              <p className="platform-eyebrow">Claude Cowork</p>
              <CopyCommand
                command={repositoryUrl}
                label="marketplace URL"
              />
              <p className="install-note">
                In Customize → Plugins, add this marketplace and select {plugin.name}.
              </p>
            </article>
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
          <p className="footer-name">Israel&apos;s Plugin Registry</p>
          <Link href="/#plugins">Browse all plugins</Link>
        </div>
      </footer>
    </>
  );
}
