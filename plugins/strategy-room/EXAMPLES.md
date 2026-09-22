# Three example tasks

These prompts are adapted from real work patterns. They are reusable demonstrations, not claims that this public version produced the original work. Provide the stated inputs before running each example.

## 1. Agree on a second phase before building

Inputs: Provide the first-phase result and second-phase proposal.

```text
Use strategy-room:grill-me before we start phase two. Read the completed work and proposed changes. Ask only questions whose answers could change the scope, order, acceptance checks or rollback. Finish with a shared-understanding summary for my approval. Do not implement the plan.
```

Expected result: A focused interview and a decision record; no implementation begins.

## 2. Choose which capabilities to develop next

Inputs: Provide candidate capabilities, available evidence and your time constraint.

```text
Use strategy-room:decision-synthesizer to select the next five capabilities to develop from this list. Compare readiness, distinct usefulness, dependencies and maintenance effort. Show the alternatives, supporting evidence and reasons to defer each unselected candidate. State what would change your recommendation. Stop at the decision.
```

Expected result: A ranked selection with alternatives, explicit trade-offs and conditions.

## 3. Update a workshop after a product release

Inputs: Provide the workshop and official release information.

```text
Use strategy-room:assumption-register to assess this workshop update. Separate confirmed product facts from my preferences and assumptions about attendee access. Identify what still needs checking, who should check it and how it could change the plan. Recommend where the new material fits without disrupting the current flow. Do not edit or publish yet.
```

Expected result: An assumption register and a scoped recommendation grounded in the supplied sources.
