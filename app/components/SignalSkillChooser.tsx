"use client";

import Link from "next/link";
import { useState } from "react";
import {
  signalToSystemGuides,
  signalToSystemStages,
} from "../catalog.generated";
import { CopyCommand } from "./CopyCommand";

type SignalSkill = keyof typeof signalToSystemGuides;

function skillName(slug: string) {
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function SignalSkillChooser() {
  const [selected, setSelected] = useState<SignalSkill | null>(null);
  const guide = selected ? signalToSystemGuides[selected] : null;
  const stage = guide
    ? signalToSystemStages.find((item) => item.slug === guide.stage)
    : null;

  return (
    <section
      aria-labelledby="signal-chooser-title"
      className="signal-chooser guide-section"
      data-testid="signal-skill-chooser"
      id="choose"
    >
      <div className="section-heading detail-section-heading">
        <p className="kicker">Ten skills · one job at a time</p>
        <h2 id="signal-chooser-title">What is in front of you?</h2>
        <p>
          Choose the closest need. The Site will recommend one skill and give
          you a request you can adapt. You never have to run all ten.
        </p>
      </div>

      <div className="signal-chooser-layout">
        <div
          aria-label="Choose the job in front of you"
          className="signal-needs"
          role="group"
        >
          {signalToSystemStages.map((item) => (
            <section className="signal-stage" key={item.slug}>
              <div className="signal-stage-heading">
                <p>{item.name}</p>
                <span>{item.description}</span>
              </div>
              <div className="signal-stage-options">
                {item.skills.map((skill) => {
                  const signalSkill = skill as SignalSkill;
                  const itemGuide = signalToSystemGuides[signalSkill];
                  return (
                    <button
                      aria-pressed={selected === signalSkill}
                      data-testid={"signal-choice-" + signalSkill}
                      key={signalSkill}
                      onClick={() => setSelected(signalSkill)}
                      type="button"
                    >
                      <span>{itemGuide.chooserLabel}</span>
                      <small>{skillName(signalSkill)}</small>
                    </button>
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        <div
          aria-live="polite"
          className="signal-recommendation"
          data-testid="signal-recommendation"
        >
          {selected && guide && stage ? (
            <>
              <p className="guide-eyebrow">Recommended · {stage.name}</p>
              <h3>{skillName(selected)}</h3>
              <p>{guide.summary}</p>
              <div className="signal-prompt">
                <p>Illustrative request</p>
                <CopyCommand
                  command={guide.illustrativePrompt}
                  label={skillName(selected) + " illustrative request"}
                />
              </div>
              <Link
                className="signal-guide-link"
                href={"/plugins/signal-to-system/skills/" + selected}
              >
                Open the full skill guide
                <span aria-hidden="true">↗</span>
              </Link>
            </>
          ) : (
            <div className="signal-recommendation-empty">
              <p className="guide-eyebrow">Your recommendation</p>
              <h3>Choose one need to begin.</h3>
              <p>
                Each choice maps to one independently usable skill. The result
                will appear here without changing the page.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
