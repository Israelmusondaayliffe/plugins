import Link from "next/link";
import { headers } from "next/headers";
import { Catalog } from "./components/Catalog";
import { CopyCommand } from "./components/CopyCommand";
import { ThemeToggle } from "./components/ThemeToggle";
import { marketplaceName, plugins, site, totals } from "./catalog.generated";

const repositoryUrl =
  "https://github.com/Israelmusondaayliffe/plugins";

export default async function Home() {
  const incoming = await headers();
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host");
  const protocol = incoming.get("x-forwarded-proto") ?? "https";
  const origin = host ? protocol + "://" + host : "http://localhost:3000";
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: site.name,
    numberOfItems: plugins.length,
    itemListElement: plugins.map((plugin, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: origin + "/plugins/" + plugin.slug,
      name: plugin.name,
    })),
  };

  return (
    <>
      <header className="site-header shell">
        <Link className="wordmark" href="/" aria-label={site.name}>
          <span className="wordmark-mark">AP</span>
          <span>{site.name}</span>
        </Link>
        <div className="header-actions">
          <nav aria-label="Primary navigation">
            <a href="#outcomes">Catalog</a>
            <a href="#install">Install</a>
            <a href={repositoryUrl}>GitHub</a>
          </nav>
          <ThemeToggle />
        </div>
      </header>

      <main>
        <section className="registry-intro shell" aria-labelledby="hero-title">
          <div className="registry-intro-copy">
            <p className="kicker">
              Community Agent Plugins · Public registry
            </p>
            <h1 id="hero-title">Choose the work. Check the host. Install the plugin.</h1>
            <p className="hero-lede">
              A practical index of {totals.plugins} public plugins and {totals.skills} bundled
              skills for Codex, Claude Code, and Claude Cowork. Search by the
              outcome you need, then use only the install action documented for your host.
            </p>
          </div>
          <div className="registry-totals" aria-label="Registry totals">
            <div><strong>{totals.plugins}</strong><span>Public plugins</span></div>
            <div><strong>{totals.skills}</strong><span>Bundled skills</span></div>
            <div><strong>04</strong><span>Outcome groups</span></div>
            <div><strong>03</strong><span>Supported hosts</span></div>
          </div>
        </section>

        <section className="catalog-section shell" id="outcomes">
          <div className="section-heading">
            <p className="kicker">Registry index</p>
            <h2>Start with the outcome. Then choose the host.</h2>
            <p>
              Search every public plugin and bundled skill, narrow the registry
              by outcome, category, or host, then inspect the
              exact record before you install.
            </p>
          </div>
          <Catalog />
        </section>

        <section className="changes-strip shell" aria-labelledby="what-changed-title">
          <div>
            <p className="kicker">Current edition</p>
            <h2 id="what-changed-title">A maintained registry, not a marketing list.</h2>
          </div>
          <ul>
            <li><strong>Added</strong> Signal to System with ten public skill guides.</li>
            <li><strong>Introduced</strong> a chooser that starts from the job in front of you.</li>
            <li><strong>Clarified</strong> host support and evidence status on every public record.</li>
          </ul>
        </section>

        <section className="install-section" id="install">
          <div className="shell install-layout">
            <div className="install-intro">
              <p className="kicker">Install by host</p>
              <h2>Choose your host. Check the record.</h2>
              <p>
                Add the public source once, then use the command shown only for
                a host verified on that plugin’s record.
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
                <p>Add the marketplace, then install a Codex-supported plugin.</p>
                <CopyCommand command="codex plugin marketplace add Israelmusondaayliffe/plugins --ref main" />
                <CopyCommand
                  command={"codex plugin add loopkit@" + marketplaceName}
                />
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
                <CopyCommand
                  command={"/plugin install loopkit@" + marketplaceName}
                />
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
                  choose a Cowork-supported plugin from its record.
                </p>
                <CopyCommand
                  command={repositoryUrl}
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
            <h2>Inspect each claim.</h2>
            <p>
              A plugin can be available in a marketplace and still not be
              verified on every host. The registry keeps those facts separate,
              so the host filter and install actions only reflect documented
              runtime support.
            </p>
            <Link className="text-link" href="/plugins/capability-operator">
              Inspect a complete plugin record
            </Link>
          </div>
          <dl className="inventory-facts">
            <div>
              <dt>Registry</dt>
              <dd>{site.name}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>Public on GitHub</dd>
            </div>
            <div>
              <dt>Discovery</dt>
              <dd>Outcome, category, and host</dd>
            </div>
            <div>
              <dt>Install surface</dt>
              <dd>Host-specific records</dd>
            </div>
          </dl>
        </section>
      </main>

      <footer>
        <div className="shell footer-grid">
          <div>
            <p className="footer-name">{site.name}</p>
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
