# Gauntlet Loop for Codex

Gauntlet Loop is an explicit-only execution system for unusually large, consequential, or compute-intensive Codex projects. It supports software engineering, product work, research, strategy, long-form writing, curriculum, operations, creative systems, and mixed projects.

Invoke it deliberately:

```text
$gauntlet-loop:gauntlet Plan and run this project.
```

The plugin never activates merely because a task is difficult, long, or likely to use subagents. All six skills disable implicit invocation.

## Method

1. Grill the goal until dangerous ambiguity is removed.
2. Write a project constitution and obtain approval.
3. Compile independent workstreams, concrete quality bars, evidence rules, authority boundaries, integration waves, and a finite resource envelope.
4. Assign builders and fresh-context critics.
5. Improve the largest meaningful gap without treating round count as proof of quality.
6. Maintain durable project and handoff files after material changes.
7. Integrate the complete project.
8. Use fresh verifiers to inspect the real artifacts and evidence.

Builders may test and inspect their work, but they cannot issue the authoritative verdict. Every authoritative critic, handoff reader, integrator, and verifier must use a new agent with no inherited conversation turns when the host exposes that control.

## Models, Max, and Ultra

The plugin does not select or silently change the parent model, reasoning effort, host mode, or cost profile. Choose the model and effort in Codex before invocation.

- Max gives one selected model more time to reason.
- Ultra is a host mode that coordinates subagents.
- The Gauntlet compiler records `highest_available` only as an internal preference. The runner resolves it against the live host and approved compute envelope.

If isolated agents are unavailable, Gauntlet may continue non-authoritative building work sequentially, but it must return `unable_to_evaluate` or `unable_to_verify` for claims that require fresh independent judgment.

## Skills

- `$gauntlet-loop:gauntlet`: initialize, route, resume, and close a project.
- `$gauntlet-loop:gauntlet-plan`: discover requirements and write the proposed project constitution.
- `$gauntlet-loop:gauntlet-compile`: turn an approved plan into the executable program.
- `$gauntlet-loop:gauntlet-run`: execute bounded workstreams and integration waves.
- `$gauntlet-loop:gauntlet-handoff`: create and validate durable transfers.
- `$gauntlet-loop:gauntlet-verify`: run independent verification and create repair packets.

## Project state

Gauntlet writes a `.gauntlet/` directory inside the selected project. The canonical entry points are:

```text
.gauntlet/project.md
.gauntlet/plan.md
.gauntlet/gauntlet.yaml
.gauntlet/state.json
.gauntlet/handoff.md
```

`gauntlet.yaml` uses JSON-compatible YAML so the bundled validator can parse it with Python's standard library.

Run deterministic checks:

```bash
python3 scripts/gauntletctl.py init --project-root /path/to/project --name "Project name"
python3 scripts/gauntletctl.py validate --project-root /path/to/project
python3 scripts/verify_bundle.py .
```

## Authority and cost

Invocation does not authorize publication, deployment, purchases, messages, permission changes, access to new sensitive systems, Goal creation, destructive actions, separate user-owned tasks, or silent model escalation. Those actions retain their normal approval requirements.

Every compiled program must set finite ceilings for elapsed time, total agent launches, concurrency, and critic rounds. Reaching a ceiling produces a checkpoint or partial closeout, never a success verdict.

## Pause, resume, and revise

Before pausing, run the handoff stage and validate the result. Resume in a new task with:

```text
$gauntlet-loop:gauntlet Resume the Gauntlet project in this workspace.
```

Material changes to purpose, deliverables, authority, quality bars, or resource ceilings create a new approved plan version. A user may accept a result below the original bar, but the override and remaining gap must be recorded.

## Verdicts

- `verified`: all critical criteria pass with inspectable evidence.
- `verified_with_caveats`: required criteria pass and remaining findings are non-blocking.
- `failed_verification`: a major criterion, quality bar, integration requirement, or material claim fails.
- `unable_to_verify`: required evidence, access, isolation, or inspection capability is missing.

## Known limitations

- A plugin skill cannot guarantee that a future task starts itself. Resume requires explicit invocation.
- New user-owned Codex tasks require explicit approval and a callable task-management surface.
- Fresh-context isolation depends on the host exposing a no-inherited-turns agent option.
- The plugin does not provide external telemetry or a hosted dashboard.
- Qualitative judgment remains judgment, even when anchored to concrete references and rubrics.
- No verifier can prove objective perfection.

## Attribution

This plugin adapts and extends Matt Shumer's Gauntlet Loop and the Claude of Duty methodology for broad Codex mega-project execution. It uses the core idea of builders working against a quality bar and fresh critics judging the real artifact. The implementation, schemas, scripts, and cross-domain extensions in this repository are original.

## License

MIT. See [LICENSE](LICENSE).
