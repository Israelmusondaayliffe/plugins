# gauntlet

Explicit-only mega-project loop for Claude Code (primary) and Claude Cowork (packaged
secondary). Implements the gauntlet method: split a goal into the smallest independently
judgeable pieces, give each piece a builder and a blind critic with fresh context, judge
against an external bar, name one gap per round, loop until the work wins or the run stops,
verify with agents that never saw the build, and report with receipts.

Method source: Matt Shumer, "How to Run a Gauntlet Loop" (somethingbig.ai, 2026-07-27) and
github.com/mshumer/Claude-of-Duty.

## Editions

This is the Claude Code and Cowork edition, built from the v3.0 spec in `docs/SPEC.md`. The
sibling `gauntlet-loop` plugin in this marketplace is the Codex edition of the same method,
built independently with a Codex-native invocation policy and dual-format manifests. Install
the edition that matches your surface; they share the method, not their state layouts.

## Invocation contract

This plugin never loads on its own. It responds only to explicit triggers: gauntlet, run the
gauntlet, gauntlet loop, gauntlet mode, gauntlet run, the big one, mega project mode, max
run, ultracode run, beat this bar, blind critic loop, Claude of Duty method, resume the
gauntlet, gauntlet handoff. "Make this really good" does not load it. It is for projects
that justify real cost: days of work, hundreds of subagents, top-effort model settings.

## Skills

| Skill | Job |
|---|---|
| `gauntlet` | Front door and router. Surface precheck, stage routing, hard rules: never reports completion, never skips verification |
| `gauntlet-brief` | Interview, bar setting, sizing, decomposition. Gated by `validate_bar.py` and `brief_complete.py` |
| `gauntlet-prompt` | Writes the short lead-agent prompt. Linted by `lint_prompt.py`: under 600 words, no prescribed architecture |
| `gauntlet-run` | The loop. Builder and blind critic per piece, inspection before judgment, one gap per round, stop conditions by script |
| `gauntlet-verify` | Independent fresh-context verification, separate quality and integrity verifiers, consensus by `consensus.py` |
| `gauntlet-evidence` | Evidence report with paths, commands, exit codes, hashes. Every value read from state, never narrated |
| `gauntlet-handoff` | Script-generated session handoff, portable across sessions, threads, and surfaces |

## Layout

- `skills/`: the seven skills, each with its own references and assets
- `agents/`: builder, critic, reader-proxy, quality-verifier, integrity-verifier, smoother
- `scripts/`: 17 Python 3 stdlib scripts; exactness lives here, judgment lives in the model
- `references/domains/`: eight domain adapters: code, visual, prose, research, deck,
  strategy, prompt-system, brand
- `tests/`: unit tests, `python3 -m unittest discover -s tests`
- `docs/SPEC.md`: the binding spec; `docs/BUILD-NOTES.md`: platform facts verified at build

## State

Runs live in `.gauntlet/runs/<run-id>/` in the target project, resumable from disk by an
agent that never saw the conversation. Blind label maps are sealed outside the run directory.
`workbench.html` is a script-generated live progress page.

## Invariants

1. The bar is external and inspectable.
2. The builder never grades itself.
3. Judgment inspects the real thing.
4. Quality and integrity are judged separately.
5. Nothing is done without re-runnable evidence.
6. Continuity is written from state, not narrated.
7. Caps pause, they do not certify.
