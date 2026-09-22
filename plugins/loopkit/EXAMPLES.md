# Three example tasks

These prompts are adapted from real work patterns. They are reusable demonstrations, not claims that this public version produced the original work. Provide the stated inputs before running each example.

## 1. Design a weekly local activity scout

Inputs: Provide your town, travel limit, interests and preferred reporting time.

```text
Use loopkit:loopkit to design a weekly research loop for local activities over the next seven days. Return a best plan, backup, shortlist and source check. Include current dates, travel estimates and costs or unknowns. No bookings, purchases or messages. Complete and verify one manual run before proposing the schedule. If scheduling is unavailable, return the schedule specification and say it is inactive.
```

Expected result: A bounded contract, a sourced report and verification receipt; an active schedule only when supported and explicitly authorized.

## 2. Carry a workshop revision through review

Inputs: Provide the approved revision scope, draft pages, output folder and any existing verification command.

```text
Use loopkit:loop-designer to make a contract for this approved workshop revision. Name the permitted files, required editorial and beginner reviews, completion checks and stop conditions. Allow at most three iterations and stop after one iteration with no progress. Then use loopkit:loop-runner to carry out the local revision. Do not publish until I explicitly approve the final pages and destinations.
```

Expected result: A saved contract, bounded iterations and a completion receipt supported by actual checks.

## 3. Check two repository copies before synchronizing

Inputs: Provide the two repository paths and the files that should match.

```text
Use loopkit:loopkit to compare the approved files in these two repositories. Record the expected relationship, actual differences and permitted repairs in a contract. Begin read-only and show the proposed synchronization. After approval, apply only those repairs, verify the result and save a checkpoint for resuming if interrupted. Do not push, merge, install or change credentials.
```

Expected result: A reproducible comparison and proposed repair scope, followed by approved local changes and a verified receipt.
