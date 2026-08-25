---
name: experiment-designer-and-ledger
description: "Turn one important assumption into the cheapest useful experiment with a prediction, measure, stop rule, evidence plan, and portable result ledger. Use to test a product, workflow, workshop, service, community, or creative hypothesis. Do not manage a large experiment program or call an untested result proof."
---

# Experiment Designer And Ledger

Design the smallest test that can change a real decision.

## Shared rules

Use [source and tool policy](../../references/source-and-tool-policy.md) when a
baseline or method depends on current external facts. Follow
[evidence and artifact policy](../../references/evidence-and-artifact-policy.md)
when classifying results.

## Design

1. State the decision the experiment should inform.
2. Write one falsifiable assumption and explain why it matters.
3. Record the current evidence strength: unsupported, suggestive, promising, or
   repeated.
4. Define the smallest test that could meaningfully increase or reduce
   confidence. Prefer reversible, low-cost tests over elaborate pilots.
5. Set the prediction, participants or sample, method, success measure, failure
   signal, stop rule, timebox, and ethical or permission constraints before the
   result exists.
6. Identify confounders and what the test cannot prove.

## Ledger

Create a Markdown experiment record using
[the experiment template](assets/experiment-design-template.md). Use
[the CSV ledger](assets/experiment-ledger.csv) when the user wants multiple
runs, comparison, or later automation.

Treat the ledger as append-only evidence. Give each experiment a stable ID and
each correction or interpretation a new version with its own timestamp. Never
replace the original prediction, method, raw observation, or result after the
outcome is known. Link corrections to the prior record.

When results are supplied:

- preserve raw observations separately from interpretation
- compare the outcome with the precommitted prediction
- classify the result as supports, weakens, inconclusive, or invalid
- if invalid, record the exact invalidation reason
- record the actual sample, deviations, confounders, and raw evidence location
- update confidence without pretending one test proves a broad claim
- recommend stop, repeat, revise, or scale

Do not run a live experiment, recruit people, send messages, or change a
service without explicit authorization.
