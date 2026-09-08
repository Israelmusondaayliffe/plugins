# Astra migration overlay

## Subtract first

Audit the source prompt for:

- duplicate constraints;
- repeated `must`, `always`, or `critical` emphasis;
- anti-laziness pressure;
- forced planning, progress reports, or checklists;
- generic tool or subagent pressure;
- stale hard-coded model names;
- instructions that turn every interface into a landing page;
- repeated UI labels, controls, features, or explanatory sections;
- high effort used by habit rather than evidence.

Classify each item as stable policy, current-model compensation, stale reference, duplicate constraint, or unrelated. Preserve stable policy. Remove one coherent compensation group, then evaluate that group.

## Prompt additions that may earn their place

Add only the task-specific guard that addresses the likely failure:

- Simple interface: `Build only the requested workflow. Do not add landing-page sections, extra controls, labels, or features unless they are required for the workflow.`
- Computer control: name the target app, allowed action boundary, completion condition, and proof surface.
- Writing: name the audience, intent, voice source, and non-negotiable facts. Do not add style adjectives without a concrete meaning.
- Cost: name the evidence threshold and stop condition. Use the least expensive effort that clears the task.

## Three focused runtime probes

Run these only when Astra is available on the target host:

1. A simple interface task that fails if it becomes a landing page or gains unnecessary controls.
2. A voice-preserving writing task that fails if facts, tone, or useful roughness are flattened.
3. A bounded computer-control task that fails if the model narrates instead of completing and verifying the action.

Compare each probe with the frozen GPT-5.6 Sol baseline under matched tools and task instructions. Record correctness, completion, restraint, cost, latency, and user-authority compliance. Stop after the decision is clear.
