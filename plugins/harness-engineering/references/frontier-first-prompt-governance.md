# Frontier-First Prompt Governance

Use this reference when a harness is being shortened, adapted to a stronger model, or reorganized around progressive disclosure. The target is not the shortest prompt. The target is the smallest default context that preserves measured behavior.

## Governing thesis

Treat a large reported prompt reduction as directional evidence, never as a quota. Newer models may need less universal coaching, but user policy, authority boundaries, source precedence, and completion criteria remain load-bearing until a controlled subtraction test proves otherwise.

Build the harness as five layers:

1. A compact context kernel containing stable cross-task invariants.
2. Workspace and project delta-only overlays containing only true local rules.
3. Personal plugin front doors in default context, with specialists loaded through a front door or explicit selection.
4. Examples, references, scripts, and tests beside the task that needs them.
5. A prompt-subtraction loop that rejects reductions causing behavioral regressions.

## Placement rules

| Requirement | Smallest correct owner |
| --- | --- |
| Stable identity, voice, fabrication boundary, authority, source precedence, ask/proceed behavior, verification, interrupt behavior | Global context kernel |
| Writable zones, project loading, output paths, workspace verification entry points | Workspace overlay |
| Project ownership, inputs, workflow, acceptance, exclusions | Project overlay |
| Conditional workflow or recovery detail | Task-owned skill or reference |
| Good behavior demonstration | Task-owned example or evaluation fixture |
| Exact path, format, policy, or validation | Script, validator, rule, hook, sandbox control, or template |
| Model-specific compensation | Model Prompt Lab, loaded only for a reproduced failure |

State an invariant once. A closer layer refines scope but does not repeat the broader rule. Do not put capability inventories, connector manuals, CLI catalogs, or failure histories in universal context.

## Evidence freeze before subtraction

Create one dated run directory before editing. Freeze:

- applicable instruction files and their hashes;
- complete prompt input and word or token measurements by section;
- selected model, reasoning effort, run count, tool inventory, and effective task conditions;
- installed plugin listing, capability inventory, source and cache fingerprints, and routing results;
- evaluation suite, output schema, scorer version, raw model outputs, and normalized baseline;
- source fingerprints, launcher help, and script hashes for any skill pilot;
- operation plan, previews, approval groups, backups, receipts, and rollback order.

Do not compare runs whose model, effort, tools, scorer, or task conditions differ. When the scorer changes, rescore frozen raw outputs and record the calibration change. Never treat a scorer repair as a model improvement.

## Behavior evaluation contract

A useful permanent suite samples the decisions universal context is meant to protect:

- authority and safety;
- capability and source-owner routing;
- file layers, output paths, and verification;
- ask/proceed, confirmation, monitoring, and stopping;
- voice, templates, and completion evidence.

Run every case more than once at fixed settings. Freeze short examples for read-only diagnosis, scoped implementation, high-stakes confirmation, source-owner routing, UI verification, and evidence-backed completion.

Accept a subtraction batch only when:

1. every critical run passes;
2. no category falls below the accepted baseline;
3. overall pass rate meets or exceeds the accepted baseline;
4. prompt input is smaller for the intended reason;
5. duplicated guidance declines;
6. the installed environment passes the same suite after all context-affecting changes.

Word ceilings are diagnostics. They never override behavior acceptance. A noncritical miss already present in the frozen baseline does not justify new universal prose unless the behavior is repeated, harmful, and owned by the default context.

## Measure more than entry count

Track at least:

- combined instruction words;
- total prompt words or tokens;
- skill metadata words or tokens;
- implicit skill entries;
- duplicate display names;
- front doors present;
- hidden specialists absent;
- hidden specialists reachable;
- explicit hidden-skill invocation;
- source/cache parity.

One measured case reduced the instruction chain from 3,807 to 1,379 words, total prompt input from 5,724 to 4,492 words, implicit skill entries from 263 to 155, and duplicate names from 36 to 24. At the same time, the skill metadata block grew from 1,232 to 2,032 words because fewer but richer front doors remained. This proves that entry count is not prompt size. Measure the whole prompt and each section.

A fresh explicit-invocation smoke also warned that skill descriptions were shortened to fit a 2 percent skills-context budget. Put the owner, trigger boundary, and distinguishing route near the start of each front-door description. Capture the actual prompt after runtime truncation. Do not assume a complete source description reached the model.

## Compact instruction-chain workflow

1. Preserve the stable context kernel.
2. Remove repeated workflow inventories and point to the closest owner.
3. Reduce workspace and project files to deltas.
4. Move detailed examples and conditional instructions to task-owned files.
5. Move exact checks to deterministic mechanisms.
6. Subtract one coherent instruction group at a time.
7. Run the frozen suite twice.
8. Restore a failed batch, then add only the smallest missing routing or policy cue demonstrated by the failure.

In the measured case, the first compact candidate lost the named internal-wiki owner and later lost the Capability Operator route after skill-catalog changes. Generic phrases such as "internal wiki connector" were not equivalent to the source owner required by the contract. The repair was a compact owner mapping, not restoration of the old manual. Re-run behavior checks after every mutation to task-start context, including capability-policy waves and reinstallations.

## Front-door invocation policy

Apply invocation metadata only from a source-owned portfolio and routing registry:

- Personal plugin front door: implicit invocation enabled.
- Specialist owned by a front door: implicit invocation disabled only after a deterministic route proves reachability.
- Explicit-only plugin: every owned skill implicit invocation disabled.
- Exact loose mirror of a visible namespaced skill: implicit invocation disabled.
- Loose-only, curated, runtime, connector, and system skills: unchanged.

Preserve all unrelated interface and dependency fields. A renderer should produce staged `agents/openai.yaml` previews plus hash-guarded operations. It must not edit sources itself.

Roll out in reversible waves. Start with explicit-only plugins and exact mirrors, then move from smaller to larger plugin families. Stop a wave on the first route, parity, discovery, or behavior regression. Do not hide a specialist merely because its name resembles a front door. Route coverage must be deterministic.

After each accepted wave:

1. run the existing routing suite;
2. run one deterministic front-door case per hidden specialist;
3. validate each affected plugin;
4. refresh the supported local cachebuster and reinstall each affected plugin independently;
5. prove installed listing and exact source/cache parity;
6. capture fresh prompt input;
7. prove front doors remain visible and hidden specialists remain absent;
8. run an actual explicit invocation smoke for a hidden specialist;
9. rerun the universal behavior suite.

Metadata absence is not reachability proof. A fresh `codex exec` or equivalent new-task invocation is stronger evidence than file inspection alone.

## Skill compaction pilot

Treat a large skill as its own evaluation target. Freeze positive triggers, negative triggers, functional cases, an external rubric, source fingerprint, script hashes, launcher help, and CLI flags before editing.

Functional success alone is insufficient. In the measured pilot, all 32 trigger and functional cases passed while the rubric passed only 5 of 6 and the static evaluator scored 26 with grade F. The failures were broken relative links, excessive deferred token cost, excessive invoke token cost, and excessive skill size. The planned compaction correctly stopped before candidate staging.

If the frozen current version fails its acceptance contract:

1. do not pin it as a successful baseline;
2. do not edit or promote the compaction candidate;
3. record the pre-existing failures separately;
4. open a dedicated repair plan if authorized;
5. rerun the baseline gate before resuming compaction.

When the baseline passes, keep stable invariants, safety, core flow, mode selection, grounding, and completion in `SKILL.md`. Move conditional operations, setup, recovery, and annotated examples into directly linked references. Keep the canonical launcher and CLI contract unchanged unless the task explicitly authorizes engine changes.

## Rollback and stopping

Use hash preconditions, dry-run receipts, one approval group at a time, backups, and atomic writes. Keep separate rollback manifests for instruction layers, capability waves, plugin versions, and skill promotion.

Rollback in reverse apply order. After a capability rollback, restore prior plugin versions, reinstall, and prove parity plus fresh discovery. If no skill candidate was promoted, state that no promotion rollback is needed.

Stop immediately when:

- a hash precondition changes;
- evaluation conditions become incomparable;
- a critical or category regression appears;
- a front door cannot reach a specialist;
- an unexpected file enters a generated operation plan;
- the frozen skill baseline fails;
- source and installed cache diverge.

## Self-verification rule

Harness Engineering must accept its supported local development version shape. Validators and tests may require the stable base version, but they must also accept the documented `+codex.<cachebuster>` suffix. A validator that rejects the plugin's own supported update flow is stale even when installation succeeds.

Every Harness Engineering update ends with:

- source bundle verification;
- complete unit tests;
- text quality checks;
- plugin validation;
- cachebuster refresh through Plugin Creator;
- reinstall from the owning local marketplace;
- installed and enabled listing;
- exact source/cache parity;
- fresh front-door discovery;
- the relevant behavior and routing checks.

## Maintenance cadence

Run prompt subtraction monthly and after a major model or Codex update. Reproduce a failure before restoring model-specific compensation. Keep the last accepted prompt, evaluation inputs, raw outputs, normalized comparison, and rollback receipts so the next maintenance run starts from evidence instead of accumulated advice.
