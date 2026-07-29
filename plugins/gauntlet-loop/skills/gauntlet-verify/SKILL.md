---
name: gauntlet-verify
description: Use when the user explicitly invokes $gauntlet-loop:gauntlet-verify to evaluate a project with fresh independent judges, acceptance-to-evidence traceability, adversarial checks, and a bounded final verdict. Never use implicitly.
---

# Gauntlet Verify

Issue the final project verdict from independent evidence, never from builder confidence.

## Invocation contract

This skill is explicit-only. Require state `ready_for_verification`, `verifying`, `failed_verification`, or `unable_to_verify`, plus a compiled program and indexed evidence.

## Load before acting

Read:

- `.gauntlet/project.md`
- `.gauntlet/plan.md`
- `.gauntlet/gauntlet.yaml`
- `.gauntlet/state.json`
- `.gauntlet/artifact-register.md`
- `.gauntlet/source-register.md`
- `.gauntlet/integration/synthesis-report.md`
- `.gauntlet/integration/contradiction-register.md`
- `.gauntlet/verification/acceptance-matrix.md`
- `../../references/verification-panel.md`
- `../../references/evidence-report.md`
- `../../references/quality-bars.md`
- `../../references/knowledge-work-bars.md`
- `../../references/state-machine.md`
- `../../assets/verifier-report.json`
- `../../schemas/verifier-report.schema.json`

## Preflight

Validate the workspace, then transition to `verifying`.

Map every acceptance criterion to:

- the responsible artifact;
- the observable check;
- the evidence path;
- known exclusions or caveats;
- the verifying perspective.

A criterion without inspectable evidence is not passed.
The matrix must cover every compiled material criterion exactly, and every artifact or evidence reference must resolve to an existing inspectable file. Verifier roles must match the compiled panel.

## Independent panel

Run at least three bounded verification perspectives:

1. acceptance and scope;
2. evidence and correctness;
3. integration and adversarial failure.

Start each judge with no inherited turns, equivalent to `fork_turns: "none"`. Provide only the approved plan, acceptance matrix, relevant artifacts, and evidence. Judges are read-only unless the user separately authorizes repair.

Builders and integration owners cannot issue the final verdict.

Each judge returns a schema-valid report containing criterion results, findings, severity, evidence paths, uncertainty, and recommended disposition.

## Synthesis

Reproduce important checks directly when possible. Resolve disagreements by examining evidence, not by majority vote.

Allowed verdicts:

- `verified`: every material criterion passes with sufficient evidence;
- `verified_with_caveats`: the requested outcome is met, with explicit non-material limitations;
- `failed_verification`: one or more material criteria fail;
- `unable_to_verify`: required evidence or access is unavailable.

Do not convert missing evidence into a pass.

## Output contract

Produce:

- `.gauntlet/verification/verifier-reports/<perspective>.json`
- `.gauntlet/verification/acceptance-matrix.md`
- `.gauntlet/verification/unresolved-findings.md`
- `.gauntlet/reports/evidence-report.md`
- updated risks, decisions, progress, and handoff.

Generate the report:

`python3 ../../scripts/gauntletctl.py evidence --project-root <root> --verdict <verdict>`

Transition state to the exact verdict and validate the final workspace.

## Repair loop

For `failed_verification` or `unable_to_verify`, identify the smallest repairable scope. Returning to execution requires an explicit Gauntlet invocation and remaining budget. Scope or budget expansion requires user approval.

## Completion

Complete only when the panel reports exist, evidence is traceable, disagreements and caveats are explicit, the final report is generated, and state matches the evidence-based verdict.
