---
name: astra-advisor
description: Use only after the user explicitly says "use astra-advisor" or gives an equivalent imperative such as "run this as a multi-thread session." Runs a fixed, bounded Astra Advisor topology with exact model roles, packet validation, evidence checks, and no implicit activation.
---

# Astra Advisor

Astra Advisor is a hidden explicit-only fixed-topology workflow for bounded multi-task work. Do not select it from complexity, project size, high compute, incidental subagent language, or a request that merely has several tasks.

## Activation

Require an explicit request to use Astra Advisor, or an imperative equivalent such as "run this as a multi-thread session." A later same-request revocation such as "but do not activate it" or an immediate "No" after an activation question cancels that activation. If activation is absent or revoked, use the normal Agent Ops route or the relevant owner. Record activation as explicit in the RunManifest.

## Host and task-creation preflight

This protocol requires the Codex desktop task-creation surface. Activation alone does not authorize new sidebar tasks. Before dispatch, require an explicit user request to create the separate worker and reviewer tasks, and verify each model and effort on the selected host. If that authority or surface is absent, stop with a bounded handoff; do not call `create_thread`, substitute a subagent receipt, or claim runtime qualification. A CLI or another host may inspect packets but cannot satisfy this execution contract.

## Fixed standalone topology

| Slot | Exact mapping | Authority |
| --- | --- | --- |
| Parent | `gpt-6-astra` XHigh | plan, approve, integrate, and answer |
| Routine worker | `gpt-6-astra` XHigh | bounded routine implementation and test evidence |
| Complex worker | `gpt-6-astra` XHigh | bounded complex implementation and test evidence |
| Reviewer | fresh non-fork `gpt-6-astra` High | one integrated final criticism pass |

Topology slots are available roles, not required launches. Dispatch the smallest finite worker set needed for direct deliverables. Create each worker through a fresh `create_thread` call, and do not let workers spawn other workers.

The reviewer is one new task, never a fork. It reviews the integrated result and inspects intermediate work only when risk or a finding requires it. The reviewer cannot build, repair, write, approve, integrate, or issue a final verdict. Workers cannot accept work or issue a final verdict. Stop the affected run if the required model or effort is unavailable.

## Packet contract

Read references/protocol.md before execution. Use the four JSON templates in assets/ and validate every packet with:

    python3 scripts/validate_packets.py --root PROJECT_ROOT PACKET.json

The packet types are RunManifest, TaskPacket, ReturnPacket, and ReviewPacket. A ReturnPacket is evidence, not acceptance.

Each RunManifest names a root-relative approved plan and its SHA-256. Each TaskPacket names and hashes its RunManifest, binds the same plan through its inputs, matches the authorized task DAG, and includes canonical task-creation evidence. Expected and returned artifacts stay inside the TaskPacket write roots.

A ReviewPacket names and hashes the TaskPacket and ReturnPacket it reviewed. Its artifact set must equal the return. Evidence is valid only when the path exists under the supplied root and the SHA-256 matches. Command evidence records the task, command, exit code, and stdout and stderr hashes. Packet validation does not execute commands.

## Context policy

The 150K checkpoint is an observation checkpoint, not a configuration change, retry trigger, or automatic compaction boundary. Record either observed_above_without_crossing or telemetry-unavailable when those are the available facts. Do not invent numeric occupancy and do not alter the checkpoint configuration.

## Work-first budget

One top-level budget covers discovery, audit, implementation, review, repair, and final verification for the full user request. Defaults are six total worker or reviewer launches, four concurrent tasks, one integrated critic round, one repair round, and one final verification pass. A higher launch or concurrency cap must be finite, requires a usage warning and explicit approval, and must remain within the validator's absolute ceiling. "As many as needed" means choose the smallest sufficient finite number.

Every worker owns a direct deliverable or target-system mutation. Read-only workers require a named immediate decision and may not outnumber implementation workers in an implementation run.

## Authority and stop rules

- Use the single full-request budget and finite retry, critic-round, repair-round, and elapsed-time limits.
- Keep task write scopes disjoint or serialize them. Stop on overlap.
- Do not pass the full parent transcript or hidden reasoning to workers.
- Stop on an unsupported model or effort, stale plan, exhausted budget, missing approval, unsafe scope, forged evidence, or cycle.
- In a Gauntlet-composed run, Gauntlet owns state, budget, approval, integration, final answer, and terminal verdict. Astra Advisor supplies only bounded packets and workstream criticism.

## Completion

Return a ReturnPacket with status `succeeded`, `blocked`, `failed`, or `escalate`, plus the exact TaskPacket path and hash, artifact hashes, criterion-to-evidence mapping, actual scope, commands, evidence, uncertainties, risks, `observable_delta`, `primary_output_count`, `unresolved_before`, `unresolved_after`, `support_artifact_count`, and `next_target_action`. An implementation return cannot succeed with zero observable delta or, when unresolved work existed, no unresolved reduction. Do not label the work accepted.
