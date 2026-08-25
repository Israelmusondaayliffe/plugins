---
name: workflow-clinic
description: "Diagnose a recurring workflow and design a better future state with explicit human, AI, automation, controls, and handoffs. Use for repeated work that is slow, fragile, confusing, or wasteful. Do not use for general project planning or silently implement integrations."
---

# Workflow Clinic

Treat the workflow before prescribing tools.

## Shared rules

Use [source and tool policy](../../references/source-and-tool-policy.md) when
current tool capabilities or connected systems matter. Follow
[evidence and artifact policy](../../references/evidence-and-artifact-policy.md)
for assumptions and output.

## Diagnose

1. Define the recurring trigger, desired result, people affected, frequency,
   volume, and acceptable failure.
2. Map the current path from trigger to completion. Include inputs, decisions,
   transformations, handoffs, waits, rework, approvals, and evidence.
3. Identify the actual failure modes. Distinguish a process problem from a
   training, authority, data, incentive, or tooling problem.
4. Establish a baseline using supplied observations or clearly labeled
   estimates. Do not invent time or cost savings.

## Design

For each step, choose deliberately:

- Human ownership for judgment, relationships, accountability, or ambiguity.
- AI assistance for bounded interpretation, drafting, classification, or
  synthesis with review.
- Automation for stable, deterministic, permissioned repetition.
- Removal when a step has no defensible value.

Design the smallest coherent future-state workflow. Include inputs, owners,
handoffs, controls, exceptions, failure recovery, and evidence of completion.
Recommend tools only after the job and constraints are clear. Search the web
when current product capabilities affect the design.

## Pilot outline

Define the pilot boundary, owner, baseline, high-level success signal, stop
condition, rollback path, and review date. This is an operational outline, not
an evidence-grade experiment design. Route falsifiable predictions, sampling,
confounders, result classification, and a reusable ledger to Experiment
Designer and Ledger.

Do not implement integrations or change live systems unless the user explicitly
requests and authorizes that work.

Use [the Workflow Clinic template](assets/workflow-clinic-template.md). The
result is complete when another person can run the pilot and understand why
each step belongs to a human, AI, automation, or nowhere.
