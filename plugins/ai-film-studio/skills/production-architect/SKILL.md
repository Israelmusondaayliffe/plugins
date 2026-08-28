---
name: production-architect
description: "Explicit-only planning for a durable film-production system, dependencies, and handoffs."
---

# Production Architect

Activation: explicit-only, either by direct request for `production-architect` or a routed Film Advisor packet.

## Outcome

Produce a production architecture plan, not an unscoped file operation. The plan identifies a project root, authoritative records, naming and ontology, sequence and scene graph, dependencies, owners, schedule, cost envelope, evidence gates, external actions, and completion criteria.

## Method

1. Choose one project identifier and a stable asset-name convention such as `@type_project_descriptor`.
2. Define authoritative records for project, assets, performance, geography, shots, iterations, and delivery.
3. Map the dependency chain: concept and brief before assets; assets and geography before shots; verified records before any paid test; tests before post-production decisions.
4. Separate approved states from candidates. A file is not reusable production input until its record says why it passed.
5. Name the owner, input, output, and acceptance evidence for every handoff.
6. Build the eleven production stages from `references/production-workflow.md`, with editing, sound, continuity review, and generation represented as connected streams.
7. Record cost ceilings and a configured failed-attempt budget. Default to 12 attempts only when the user has not chosen another limit.

Do not create projects, folders, accounts, remote destinations, or live jobs without direct authorization. Use a `ProductionPlan` and project-owned templates only.

## Handoff

Use `FilmBrief`, `ProductionPlan`, and the schema set in `schemas/`. Send identity and state work to `asset-bible-director`, visual continuity work to `visual-development-director`, and shot planning to `shot-continuity-director`.
