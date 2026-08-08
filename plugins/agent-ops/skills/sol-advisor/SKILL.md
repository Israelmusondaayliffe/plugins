---
name: sol-advisor
description: Use only after the user explicitly says "use sol-advisor" or gives an equivalent imperative such as "run this as a multi-thread session." Runs a fixed, bounded Sol Advisor topology with exact model roles, packet validation, evidence checks, and no implicit activation.
---

# Sol Advisor

Sol Advisor is a hidden explicit-only fixed-topology workflow for bounded multi-task work. Do not select it from complexity, project size, high compute, incidental subagent language, or a request that merely has several tasks.

## Activation

Require an explicit request to use Sol Advisor, or an imperative equivalent such as "run this as a multi-thread session." A later same-request revocation such as "but do not activate it" or an immediate "No" after an activation question cancels that activation. If activation is absent or revoked, use the normal Agent Ops route or the relevant owner. Record activation as explicit in the RunManifest.

## Fixed standalone topology

| Slot | Exact mapping | Authority |
| --- | --- | --- |
| Parent | `gpt-5.6-sol` High | plan, approve, integrate, and answer |
| Routine worker | `gpt-5.6-luna` Max | bounded routine implementation and test evidence |
| Complex worker | `gpt-5.6-terra` Max | bounded complex implementation and test evidence |
| Reviewer | fresh non-fork `gpt-5.6-sol` XHigh | workstream criticism only |

Each worker must be created through a fresh `create_thread` call and may not spawn workers. The reviewer must be a new task, never a fork, and may not build, repair, write, approve, integrate, or issue a final verdict. Workers cannot issue an acceptance or final verdict. Missing model or effort support stops the affected run. Do not substitute a different model or effort.

## Packet contract

Read references/protocol.md before execution. Use the four JSON templates in assets/ and validate every packet with:

    python3 scripts/validate_packets.py --root PROJECT_ROOT PACKET.json

The packet types are RunManifest, TaskPacket, ReturnPacket, and ReviewPacket. A ReturnPacket is not acceptance. Every RunManifest plan names a root-relative approved-plan file and SHA-256. Every TaskPacket must name and hash its RunManifest, bind that same plan through its input records, match that manifest's task DAG and authorization, and be backed by canonical task-creation request and response evidence. Expected and returned artifacts must stay inside the TaskPacket write roots. A ReviewPacket names and hashes the exact TaskPacket and ReturnPacket it reviewed, with an artifact set equal to the return. Evidence is valid only when its path exists under the supplied root and its SHA-256 matches the packet. Command evidence is a JSON record that binds its task, command, exit code, and recorded stdout/stderr hashes; validation does not execute commands.

## Runtime profiles

Read `assets/runtime-profiles.json` before creating a run and validate it with:

    python3 scripts/validate_runtime_profiles.py assets/runtime-profiles.json

The profile is an evidence contract, not a capability claim. It defines Codex, Claude Code, and Cowork separately for fresh-task creation, exact model and effort selection, scheduling, durable state, hooks, and clean-task discovery. A required capability may proceed only after its profile-required evidence is present. If a capability is unsupported, unavailable, or lacks current evidence, stop that dispatch or requested operation. Do not replace a missing host capability with a different model, a forked task, a local loop, or an inferred discovery result.

## Context policy

The 150K checkpoint is an observation checkpoint, not a configuration change, retry trigger, or automatic compaction boundary. Record either observed_above_without_crossing or telemetry-unavailable when those are the available facts. Do not invent numeric occupancy and do not alter the checkpoint configuration.

## Authority and stop rules

- Use finite launch, concurrency, retry, critic-round, repair-round, and elapsed-time limits.
- Keep task write scopes disjoint or serialize them. Stop on overlap.
- Do not pass the full parent transcript or hidden reasoning to workers.
- Stop on an unsupported model or effort, stale plan, exhausted budget, missing approval, unsafe scope, forged evidence, or cycle.
- In a Gauntlet-composed run, Gauntlet owns state, budget, approval, integration, final answer, and terminal verdict. Sol Advisor supplies only bounded packets and workstream criticism.

## Completion

Return a ReturnPacket with status `succeeded`, `blocked`, `failed`, or `escalate`, plus the exact TaskPacket path and hash, artifact hashes, criterion-to-evidence mapping, actual scope, commands, evidence, uncertainties, risks, and the next action. Do not label the work accepted.
