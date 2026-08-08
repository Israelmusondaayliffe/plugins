import Image from "next/image";
import Link from "next/link";
import { headers } from "next/headers";
import { Catalog } from "./components/Catalog";
import { CopyCommand } from "./components/CopyCommand";
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
          <span className="wordmark-mark">IA</span>
          <span>{site.name}</span>
        </Link>
        <nav aria-label="Primary navigation">
          <a href="#outcomes">Outcomes</a>
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
            <p className="kicker">
              Public plugins for Codex, Claude Code, and Claude Cowork
            </p>
            <h1 id="hero-title">
              Systems for work
              <br />
              that has to hold.
            </h1>
            <p className="hero-lede">
              {totals.plugins} public plugins and {totals.skills} bundled
              skills, arranged by the outcome you need and the host you use.
              Every record separates discovery from verified runtime support.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#outcomes">
                Browse by outcome
              </a>
              <a className="button button-quiet" href={repositoryUrl}>
                View source
              </a>
            </div>
          </div>
        </section>

        <section className="proof-strip shell" aria-label="Registry totals">
          <div>
            <strong>{totals.plugins}</strong>
            <span>Public plugins</span>
          </div>
          <div>
            <strong>{totals.skills}</strong>
            <span>Bundled skills</span>
          </div>
          <div>
            <strong>4</strong>
            <span>Outcome collections</span>
          </div>
          <div>
            <strong>3</strong>
            <span>Verified hosts</span>
          </div>
        </section>

        <section
          className="changes-strip shell"
          aria-labelledby="what-changed-title"
        >
          <div>
            <p className="kicker">What changed</p>
            <h2 id="what-changed-title">A clearer way into the registry.</h2>
          </div>
          <ul>
            <li>
              <strong>Added</strong> Gauntlet and Gauntlet Loop.
            </li>
            <li>
              <strong>Expanded</strong> Capability Operator, Agent Ops, and
              Harness Engineering.
            </li>
            <li>
              <strong>Clarified</strong> which runtime hosts are verified for
              every plugin.
            </li>
          </ul>
        </section>

        <section className="catalog-section shell" id="outcomes">
          <div className="section-heading">
            <h2>Start with the outcome. Then choose your host.</h2>
            <p>
              Search every public plugin and bundled skill, narrow the registry
              by outcome, category, or verified runtime host, then inspect the
              exact record before you install.
            </p>
          </div>
          <Catalog />
        </section>

        <section className="install-section" id="install">
          <div className="shell install-layout">
            <div className="install-intro">
              <p className="kicker">Install your way</p>
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
            <h2>Claims kept where you can inspect them.</h2>
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
