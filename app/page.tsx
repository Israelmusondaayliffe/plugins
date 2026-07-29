import Image from "next/image";
import Link from "next/link";
import { Catalog } from "./components/Catalog";
import { CopyCommand } from "./components/CopyCommand";
import { plugins, totals } from "./catalog.generated";

const repositoryUrl =
  "https://github.com/Israelmusondaayliffe/plugins";

export default function Home() {
  const resourceTotal = totals.assets + totals.references + totals.scripts;
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Israel's Plugin Registry",
    numberOfItems: plugins.length,
    itemListElement: plugins.map((plugin, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: repositoryUrl + "/tree/main/plugins/" + plugin.slug,
      name: plugin.name,
    })),
  };

  return (
    <>
      <header className="site-header shell">
        <Link className="wordmark" href="/" aria-label="Israel's Plugin Registry">
          <span className="wordmark-mark">IA</span>
          <span>PLUGIN REGISTRY</span>
        </Link>
        <nav aria-label="Primary navigation">
          <a href="#plugins">Plugins</a>
          <a href="#install">Install</a>
          <a href={repositoryUrl}>GitHub</a>
        </nav>
      </header>

      <main>
        <section className="hero shell" aria-labelledby="hero-title">
          <figure className="hero-art" aria-hidden="true">
            <Image
              alt=""
              fill
              priority
              sizes="(max-width: 800px) 100vw, 62vw"
              src="/plugin-constellation.png"
              unoptimized
            />
          </figure>
          <div className="hero-copy">
            <p className="kicker">One marketplace. Three agent surfaces.</p>
            <h1 id="hero-title">
              A working system,
              <br />
              packaged.
            </h1>
            <p className="hero-lede">
              {totals.plugins} field-tested plugins for Codex, Claude Code, and
              Claude Cowork. One source, packaged for all three.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#plugins">
                Browse the registry
              </a>
              <a className="button button-quiet" href={repositoryUrl}>
                View source
              </a>
            </div>
          </div>
        </section>

        <section className="proof-strip shell" aria-label="Marketplace totals">
          <div>
            <strong>{totals.plugins}</strong>
            <span>Public plugins</span>
          </div>
          <div>
            <strong>{totals.skills}</strong>
            <span>Bundled skills</span>
          </div>
          <div>
            <strong>{resourceTotal.toLocaleString("en-US")}</strong>
            <span>Support files</span>
          </div>
          <div>
            <strong>3</strong>
            <span>Supported agent surfaces</span>
          </div>
        </section>

        <section className="catalog-section shell" id="plugins">
          <div className="section-heading">
            <h2>Find the capability. Inspect the package. Choose your surface.</h2>
            <p>
              Search every plugin and skill, select a record, then install only
              what belongs in your agent setup.
            </p>
          </div>
          <Catalog />
        </section>

        <section className="install-section" id="install">
          <div className="shell install-layout">
            <div className="install-intro">
              <p className="kicker">Install your way</p>
              <h2>Choose your surface. Keep the same plugin.</h2>
              <p>
                The repository carries native manifests for Codex and Claude.
                Add the public source once, then install only what you need.
              </p>
            </div>
            <div className="platform-install-grid">
              <article className="platform-install-card">
                <div className="platform-card-heading">
                  <span>01</span>
                  <div>
                    <p className="platform-eyebrow">Terminal</p>
                    <h3>Codex</h3>
                  </div>
                </div>
                <p>Add the marketplace, then install any plugin by name.</p>
                <CopyCommand command="codex plugin marketplace add Israelmusondaayliffe/plugins --ref main" />
                <CopyCommand command="codex plugin add loopkit@israel-plugins" />
                <p className="platform-note">
                  Start a fresh Codex task after installation.
                </p>
              </article>

              <article className="platform-install-card">
                <div className="platform-card-heading">
                  <span>02</span>
                  <div>
                    <p className="platform-eyebrow">Slash commands</p>
                    <h3>Claude Code</h3>
                  </div>
                </div>
                <p>Run both commands inside Claude Code.</p>
                <CopyCommand command="/plugin marketplace add Israelmusondaayliffe/plugins" />
                <CopyCommand command="/plugin install loopkit@israel-plugins" />
                <p className="platform-note">
                  Skills load under their plugin namespace.
                </p>
              </article>

              <article className="platform-install-card">
                <div className="platform-card-heading">
                  <span>03</span>
                  <div>
                    <p className="platform-eyebrow">Customize → Plugins</p>
                    <h3>Claude Cowork</h3>
                  </div>
                </div>
                <p>
                  Select Add marketplace, paste the GitHub repository, then
                  choose any plugin from the catalog.
                </p>
                <CopyCommand
                  command="https://github.com/Israelmusondaayliffe/plugins"
                  label="marketplace URL"
                />
                <a
                  className="platform-doc-link"
                  href="https://claude.com/docs/cowork/guide/plugins"
                >
                  Official Cowork install guide
                </a>
              </article>
            </div>
          </div>
        </section>

        <section className="inventory-section shell">
          <div className="inventory-statement">
            <h2>Skills first. Claims kept exact.</h2>
            <p>
              Every plugin carries both Codex and Claude manifests. This release
              includes skills, scripts, references, assets, and agent
              definitions. It does not currently bundle MCP servers or app
              connectors.
            </p>
            <Link className="text-link" href="/plugins/capability-operator">
              Inspect a complete plugin record
            </Link>
          </div>
          <dl className="inventory-facts">
            <div>
              <dt>Repository</dt>
              <dd>Public on GitHub</dd>
            </div>
            <div>
              <dt>Marketplace</dt>
              <dd>One GitHub source</dd>
            </div>
            <div>
              <dt>Install surface</dt>
              <dd>Codex + Claude</dd>
            </div>
            <div>
              <dt>Discovery</dt>
              <dd>Platform-native</dd>
            </div>
          </dl>
        </section>
      </main>

      <footer>
        <div className="shell footer-grid">
          <div>
            <p className="footer-name">Israel&apos;s Plugin Registry</p>
            <p>Public packages for Codex, Claude Code, and Claude Cowork.</p>
          </div>
          <div className="footer-links">
            <a href={repositoryUrl}>Source</a>
            <a href={repositoryUrl + "/blob/main/SECURITY.md"}>Security</a>
            <a href={repositoryUrl + "/blob/main/LEGAL.md"}>Legal</a>
          </div>
        </div>
      </footer>

      <script
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        type="application/ld+json"
      />
    </>
  );
}
