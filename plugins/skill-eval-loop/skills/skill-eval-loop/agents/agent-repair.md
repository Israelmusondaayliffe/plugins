# Repair phase

## Scope

Create and evaluate isolated candidates. Source promotion is a separate approved step.

## Workflow

1. Stage the current target with `stage` and record its source fingerprint.
2. Apply the smallest fix to the staged copy through Skill Creator Pro or the appropriate plugin owner.
3. Run the full suite against the staged candidate.
4. If the candidate passes without regression, request explicit approval.
5. Promote only with the required approval token and expected source fingerprint.

## Output

Return the staged path, passing run ID, source fingerprint, and promotion status. Hand generic scheduling or loop diagnosis to LoopKit.
