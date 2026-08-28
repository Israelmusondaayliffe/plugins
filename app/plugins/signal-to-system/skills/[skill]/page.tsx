import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyCommand } from "../../../../components/CopyCommand";
import { ThemeToggle } from "../../../../components/ThemeToggle";
import {
  signalToSystemGuides,
  signalToSystemStages,
  site,
} from "../../../../catalog.generated";

type SignalSkill = keyof typeof signalToSystemGuides;
type SignalSkillPageProps = {
  params: Promise<{ skill: string }>;
};

const repositoryUrl = "https://github.com/Israelmusondaayliffe/plugins";

function skillName(slug: string) {
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function isSignalSkill(skill: string): skill is SignalSkill {
  return Object.prototype.hasOwnProperty.call(signalToSystemGuides, skill);
}

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.keys(signalToSystemGuides).map((skill) => ({ skill }));
}

export async function generateMetadata({
  params,
}: SignalSkillPageProps): Promise<Metadata> {
  const { skill } = await params;
  if (!isSignalSkill(skill)) return {};
  return {
    title: skillName(skill),
    description: signalToSystemGuides[skill].summary,
    openGraph: { images: [] },
    twitter: { images: [] },
  };
}

export default async function SignalSkillPage({ params }: SignalSkillPageProps) {
  const { skill } = await params;
  if (!isSignalSkill(skill)) notFound();

  const guide = signalToSystemGuides[skill];
  const stage = signalToSystemStages.find((item) => item.slug === guide.stage);
  if (!stage) notFound();
  const stageIndex = signalToSystemStages.findIndex(
    (item) => item.slug === guide.stage,
  );
  const skillIndex = Object.keys(signalToSystemGuides).indexOf(skill);

  return (
    <>
      <header className="site-header shell detail-header">
        <Link className="wordmark" href="/" aria-label={site.name}>
          <span className="wordmark-mark">AP</span>
          <span>{site.name}</span>
        </Link>
        <div className="header-actions">
          <Link className="back-link" href="/plugins/signal-to-system#choose">
            Back to skill chooser
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="signal-skill-page shell">
        <section className="signal-skill-hero outcome-think-communicate-and-preserve">
          <div>
            <p className="kicker">
              Signal to System · {stage.name} · Skill {String(skillIndex + 1).padStart(2, "0")}
            </p>
            <h1>{skillName(skill)}</h1>
            <p>{guide.summary}</p>
          </div>
          <dl className="signal-skill-position">
            <div>
              <dt>Stage</dt>
              <dd>{String(stageIndex + 1).padStart(2, "0")} · {stage.name}</dd>
            </div>
            <div>
              <dt>Use</dt>
              <dd>Independently</dd>
            </div>
            <div>
              <dt>Evidence</dt>
              <dd>Visible</dd>
            </div>
          </dl>
        </section>

        <nav className="detail-nav" aria-label="On this page">
          <span>On this page</span>
          <a href="#fit">Fit</a>
          <a href="#request">Request</a>
          <a href="#method">Method</a>
          <a href="#result">Result</a>
          <a href="#source">Source</a>
        </nav>

        <section className="signal-fit-grid" id="fit" aria-label="Skill fit">
          <article>
            <p className="kicker">Use when</p>
            <h2>Use this skill when</h2>
            <ul>
              {guide.useWhen.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </article>
          <article>
            <p className="kicker">Choose another skill when</p>
            <h2>Use another skill for these jobs</h2>
            <ul>
              {guide.notFor.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </article>
        </section>

        <section className="signal-request" id="request" aria-labelledby="request-title">
          <div>
            <p className="kicker">Illustrative request</p>
            <h2 id="request-title">Copy it, then replace the brackets.</h2>
            <p>
              This is a starting request, not a claimed test result or real-world
              case study.
            </p>
          </div>
          <CopyCommand
            command={guide.illustrativePrompt}
            label={skillName(skill) + " illustrative request"}
          />
        </section>

        <section className="guide-section workflow-section" id="method" aria-labelledby="method-title">
          <div className="section-heading detail-section-heading">
            <p className="kicker">Working method</p>
            <h2 id="method-title">How this skill works</h2>
          </div>
          <ol className="workflow-list">
            {guide.method.map((step, index) => (
              <li key={step}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><p>{step}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section className="signal-result" id="result" aria-labelledby="result-title">
          <div>
            <p className="kicker">What a useful result includes</p>
            <h2 id="result-title">A result you can use, with clear limits.</h2>
            <p>{guide.usefulResult}</p>
          </div>
          <aside>
            <p className="guide-eyebrow">Evidence boundary</p>
            <p>{guide.evidenceBoundary}</p>
          </aside>
        </section>

        <section className="signal-source" id="source">
          <div>
            <p className="kicker">Inspect the instructions</p>
            <h2>The source is public.</h2>
            <p>
              Read the complete skill instructions, templates, and shared
              evidence policies in the repository.
            </p>
          </div>
          <a
            className="signal-guide-link"
            href={repositoryUrl + "/blob/main/plugins/signal-to-system/skills/" + skill + "/SKILL.md"}
          >
            Open {skillName(skill)} on GitHub
            <span aria-hidden="true">↗</span>
          </a>
        </section>

        <nav className="signal-skill-directory" aria-label="All Signal to System skills">
          <p>All ten skills</p>
          <div>
            {signalToSystemStages.map((item) =>
              item.skills.map((itemSkill) => (
                <Link
                  aria-current={itemSkill === skill ? "page" : undefined}
                  href={"/plugins/signal-to-system/skills/" + itemSkill}
                  key={itemSkill}
                >
                  {skillName(itemSkill)}
                </Link>
              )),
            )}
          </div>
        </nav>
      </main>

      <footer>
        <div className="shell footer-grid">
          <p className="footer-name">Signal to System</p>
          <Link href="/plugins/signal-to-system#choose">Choose another skill</Link>
        </div>
      </footer>
    </>
  );
}
