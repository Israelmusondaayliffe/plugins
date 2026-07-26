# Claude 5 Context Doctrine

<!-- context-scan: catalogue -->

Verified 2026-07-25 against two Anthropic sources: "The new rules of context engineering
for Claude 5 models" and "A field guide to Claude Fable 5: Finding your unknowns", both by
Thariq Shihipar. Re-verify on the maintainer cadence in `model-change-policy.md`.

Anchor fact: Anthropic removed over 80 percent of Claude Code's system prompt for Opus 5
and Fable 5 with no measurable loss on their coding evaluations. Over-constraint is now the
default failure mode of an inherited harness, not under-specification.

## The seven reversals

Each was correct for 4.x. Each is now a liability.

1. Rules to judgement. Hard rules written to prevent worst cases now conflict with each
   other, and the model spends reasoning resolving the clash. Describe the wanted shape
   instead. Anthropic replaced "default to writing no comments, never write multi-paragraph
   docstrings" with "Write code that reads like the surrounding code: match its comment
   density, naming, and idiom."
2. Examples to interface design. Worked examples constrain the model to the example's
   exploration space. Spend the effort on parameter names, enums, and expressive contracts.
3. Upfront to progressive disclosure. Build a tree that loads at the right time, not a
   central repository of everything. Applies to instruction files, skills, and tools.
4. Repetition to single placement. Tool guidance belongs in the tool description, once.
5. Instruction-file memory to auto-memory. The model saves relevant memories itself.
6. Simple specs to rich references. A spec can be an HTML artifact, a test suite, a rubric,
   or a function in another codebase. Source code is the highest fidelity reference there
   is. Code beats a screenshot, which beats a description.
7. Per surface. System prompt carries product context and deserves the most attention when
   building a harness. Instruction files stay light on what the repo is and spend their
   tokens on gotchas, never on what is visible from the file system. Skills are lightweight
   guides encoding opinions particular to the user, split into files when long.

## The unknowns loop

The map is the prompt, skills, and context. The territory is the codebase and the real
constraints. Unknowns are the gap, and on Claude 5 models quality is bottlenecked by the
user's ability to clarify them rather than by the model.

Four quadrants: known knowns, known unknowns, unknown knowns (obvious, never written down,
recognised on sight), unknown unknowns.

Patterns by stage. Before: blind spot pass, brainstorm and prototype, interview one
question at a time prioritised by architectural impact, references, an implementation plan
that leads with the decisions most likely to change. During: an implementation notes file
with a Deviations section, taking the conservative option and continuing rather than
stopping. After: pitches and explainers for buy-in, and a quiz the user must pass.

Both failure directions are real. Too specific and the model follows instructions past the
point where a pivot was right. Too vague and it defaults to industry practice that does not
fit.

## Model supplements

From the Fable 5 and Opus 5 prompting skills, generalised only where they govern persistent
context rather than a single prompt.

- Subtract first. Every legacy behavioural instruction is presumed removable and earns its
  place back only by measured regression. Report every subtraction, or users add it back.
- Reasoning echo is banned. Any instruction to show thinking, explain reasoning in the
  response, reflect, or transcribe a thought process risks the reasoning extraction refusal
  classifier and drives fallbacks. Older skills hide these in reflection blocks. Reasoning
  visibility goes through structured thinking blocks or a send-to-user tool.
- Verification instructions come out on Opus 5. Explicit verification, double-check, and
  re-verify instructions cause over-verification and cost tokens with no quality gain.
- Calibrate rather than prescribe. Response length, narration cadence, document length,
  scope, and delegation each get one short positive statement of the wanted shape.
- Deprune on sight: enumerated behaviour lists, anti-laziness language, forced interim
  summaries, aggressive subagent authorisation, capitalised emphasis, tool-triggering
  pressure, vision workarounds, code review recall workarounds.
- Fix order when behaviour is wrong: change effort or infrastructure, then remove
  something, then add one targeted line, then restructure. Restructure last.

## Known conflict

Fable 5 long-horizon guidance recommends fresh-context verifier subagents. Opus 5 guidance
forbids subagent verification outright. Position taken here: keep verification by
fresh-context subagent only for long-horizon autonomous runs where no human sees the
intermediate work, name it explicitly there, and remove it from interactive skills and
general instruction files. Confidence medium. Revisit when the two guides reconcile.

## What must not be cut

The argument is that instructions compensating for model weakness should go. It is not an
argument that user policy should go. Keep, and where possible move down the reliability
ladder into scripts:

- Voice, tone, and banned-pattern rules.
- Brand and visual constraints.
- Output path, naming, and versioning discipline.
- Fabrication bans covering numbers, metrics, sources, templates, tool parameters, and
  skill behaviour.
- Data routing rules, such as which connector owns which question.
- Authority boundaries and approval gates.

An instruction encoding genuine product policy rather than model compensation stays, and
the audit says so explicitly rather than deleting it silently.

## The audit test

For any line in any persistent file, in order:

1. Would a Claude 5 model do this correctly without the line? Cut it.
2. Does it exist only to compensate for a 4.x weakness? Cut it.
3. Does it ask for reasoning to be echoed? Cut it, no exceptions.
4. Is it a verification or double-check instruction outside a long-horizon autonomous run?
   Cut it.
5. Is it a prohibition that could be a positive description of the wanted shape? Rewrite it.
6. Is it detail only some tasks need? Move it behind progressive disclosure.
7. Is it visible from the file system or obvious from the repo? Cut it.
8. Does it encode user policy, taste, or a real gotcha? Keep it, and consider a script.
