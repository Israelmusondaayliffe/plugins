# Capability Routing Policy

## Purpose

Use this policy only when ownership is unclear or a request spans more than one personal plugin. A focused request should load the owned skill directly.

Explicit selection chooses the operating method, not the definition of done. The parent retains the user's requested target state, unresolved-work accounting, resource cap, and final completion decision across every route and handoff.

## Collision decisions

| Collision | Primary route | Later handoff or exclusion |
| --- | --- | --- |
| Writing versus research | Knowledge Work Superpowers | Hand final prose to Writing Quality after evidence work is complete. |
| Strategy versus execution | Strategy Room | Hand an accepted decision to Outcome Engine. |
| Agent operations versus ProofLoop | Agent Ops | Exclude ProofLoop unless the user explicitly requests its learning protocol. |
| Prompt design versus evaluation | Model Prompt Lab while designing the benchmark | Hand a completed benchmark specification and real comparative runs to Model Evaluation Lab. |
| Brand system versus image prompting | Brand World Studio | Keep brand ownership primary. Use its model and prompt skills, then hand implementation to Web Product Studio or Video Production Studio. |
| Data storytelling versus analysis | Data Storytelling Studio when analysis is already checked | Exclude exploratory analysis. Hand production to the selected artifact capability. |
| Capability maintenance versus continuity | Capability Operator | Hand durable knowledge decisions to Continuity Vault after the maintenance decision is verified. |
| Web versus video | Video Production Studio when the requested deliverable is video | Use website capture as an input, not as a web product build. |
| Visual-quality gate inside a web product | Web Product Studio | Keep `web-product-router` primary; hand a load-bearing hero to hidden `web-product-studio:visual-fidelity-gate` before secondary features. Ordinary CRUD and cosmetic fixes stay ungated. |

## Required handoffs

- Strategy Room to Outcome Engine after the decision is accepted.
- Knowledge Work Superpowers to Writing Quality for final human-facing prose.
- Model Prompt Lab to Model Evaluation Lab when comparative runs or a deployment choice are needed.
- Brand World Studio to Web Product Studio or Video Production Studio for implementation.
- Data Storytelling Studio to Spreadsheets, Presentations, Visualize, Sites, or Writing Quality for production.
- Agent Ops to ProofLoop only when learning and quarantined memory are explicitly requested.
- Capability Operator to Continuity Vault for a verified durable knowledge decision.

## Connector order

Select the connector that owns the data first. Then select the workflow plugin that operates on the retrieved material. Connector choice does not decide workflow ownership.

Browser, Computer Use, and Artifacts are first-class execution surfaces. Prefer them when they best fit rendered web state, native interfaces, or polished structured deliverables. Verify only surfaces used by the task or changed by the work.

## Fallbacks

Prefer the namespaced plugin skill. Use an identical loose skill only when the user explicitly selected it or the plugin is missing from the fresh task. Record the fallback and require discovery verification.
