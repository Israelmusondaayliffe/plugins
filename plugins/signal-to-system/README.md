# Signal to System

Signal to System is an experimental community plugin for people who use AI to
turn knowledge, evidence, and repeated work into useful outcomes.

It contains ten independently invocable skills. Install the plugin once, then
invoke the skill that owns the job. The skills can consume one another's
artifacts, but users do not have to follow a fixed pipeline.

## Sense

- curiosity-compass ranks a messy field of ideas or opportunities.
- signal-scout performs an on-demand scan of current public signals.
- research-to-decision-map turns gathered evidence into a decision record.

## Decide

- workflow-clinic diagnoses and redesigns a recurring workflow.
- capability-matcher-and-brief-builder selects a person, agent, tool, or service.
- experiment-designer-and-ledger creates the smallest useful test and evidence record.

## Make

- workshop-workbench creates the workshop deliverables the user actually needs.
- creative-project-control-room creates a source-of-truth control pack for multi-asset work.

## Compound

- session-compounder turns a session into selected decisions, follow-ups, and reusable material.
- proof-to-product-mapper maps proven or promising work into an appropriate reusable form.

## Source policy

Text and ordinary files always work. Current public claims should be checked
with web search. Browser use is for rendered or dynamic verification. Computer
use is for UI-only work or an explicitly requested action. Notion, Drive,
GitHub, and other connected sources are read only when the user requests them.
External writes and messages always require explicit authorization.

## Advanced execution

Single-agent work is the default. Signal Scout, Research-to-Decision Map,
Capability Matcher and Brief Builder, and Workshop Workbench may use a small,
bounded team when parallel research or independent review materially improves
the result. Every advanced run must still return one integrated artifact and
work in a single-agent fallback.

## Beta status

Version 0.1.0-beta.1 is a living experimental release. All ten core workflows
are intended to function, while selected advanced modes may remain previews.
There is no support-time or maintenance promise.

Public examples are intentionally absent until real, permission-safe workflows
are approved and de-identified. Files under evals are synthetic routing and
behavior fixtures, not real-world proof or testimonials.

## Verification

Run:

    python3 scripts/verify_bundle.py

Validate each skill with the bundled Skill Creator validator, then validate the
plugin manifest and run the repository release checks.
