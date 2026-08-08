# Predictable skill writing

Use this quality layer before adding files, agents, or rules. The goal is reliable behavior with the least default-context and maintenance cost.

## Invocation load

The frontmatter description is always-visible routing material. State the owned job, leading words users say, high-value near misses, and explicit-only boundaries. Do not claim a broad noun when the skill owns one operation. The description decides when to load; the body decides what to do after loading.

## Leading words

Lead instructions with the controlled action: `Inspect`, `Choose`, `Validate`, `Stop`, `Return`. A reader scanning the left edge should see the workflow. Keep a reason only where it changes judgment.

## Progressive disclosure

- Keep the entrypoint to routing, gates, happy path, failure stops, completion, and direct resource links.
- Put domain facts and long examples in references.
- Put output shapes in assets.
- Put deterministic transformations and validators in scripts.
- Use agents only for distinct behavioral roles with explicit handoffs.

Every resource needs a load condition. Remove orphan resources and duplicated guidance.

## Completion criteria

Define the artifact or state produced, the validator or review surface, the fresh result required, the remaining uncertainty to report, and the authority boundary completion does not cross. If the skill cannot say when to stop, it is not ready.

## Split and pruning tests

Split when branches differ in triggers, inputs, authority, evidence, failure stops, or owners. Keep them together when they share one contract and separation would create a fragile dependency.

For each instruction, ask which acceptance case fails without it, whether another layer already supplies it, whether this is the closest owner, and whether a validator or template can express it more exactly. Delete content with no failing behavior case. Do not preserve obsolete aliases, setup commands, or copied source structure for familiarity.
