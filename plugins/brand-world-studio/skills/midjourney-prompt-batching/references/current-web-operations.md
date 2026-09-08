# Current Midjourney web operations

Last verified: September 1, 2026.

Use this reference only for browser batching, Personalization, queue pacing, speed-state handling, and Trash behavior. Follow the live authenticated interface when labels or limits change, then verify changed product facts against official Midjourney documentation.

## Recorded operating pattern

The reusable workflow observed in the user's Midjourney session was:

1. Open an Explore card, choose `Edit prompt`, inspect the loaded prompt, and submit selected remixes.
2. Open Create, choose `Use` on an existing job, add or replace the intended `--p` profile parameter, and submit the reused prompt.
3. Open Styles and Personalize to inspect selected profiles or copy an exact profile code, then return to the batch.
4. Watch the Create count and job status between submissions instead of filling the queue blindly.
5. When Fast time is unavailable, inspect Settings and the visible speed state before deciding whether work can continue.
6. Use Trash only for selected cleanup targets and verify the result after each action.

This pattern is evidence of the user's workflow, not authority to submit or Trash in a future task.

## Personalization

- Plain `--p` applies the user's selected Personalization state.
- `--p PROFILE_CODE` applies an exact profile when the code is supplied.
- The web interface can expose Personalize choices and a `Copy Profile Code` action.
- Do not add a second conflicting profile parameter. Preserve the exact code and replace only the profile parameter that the user intends to change.
- If the selected profile and a supplied code disagree, stop and confirm which one owns the batch.

Official source: https://docs.midjourney.com/hc/en-us/articles/32433330574221-Personalization

## Explore and Create reuse

- Explore cards can be opened and reused through prompt-editing controls.
- Existing Create jobs can populate a new prompt through `Use`.
- Verify the composer contents before submission because UI state, selected styles, and parameters can carry over.
- A visible Create count is a state clue, not proof that each requested job was accepted.

Official source: https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web

## Queue capacity

At the last check, Midjourney's plan comparison documented a maximum of 10 queued jobs. Treat that number as dated. Read the live queue and current plan documentation before relying on capacity, and stop on any queue-full message.

Official source: https://docs.midjourney.com/hc/en-us/articles/27870484040333-Comparing-Midjourney-Plans

## Speed and Fast time

- Speed settings synchronize between the website and Discord.
- Relax availability depends on the user's plan and current product rules.
- A `No Fast hours left` state does not authorize a speed change or purchase.
- Changing Standard, Relax, Fast, or Turbo is a persistent account-level production choice. Require explicit authority when the request did not already name the intended mode.
- Buying more Fast time is a purchase and always needs separate confirmation.

Official source: https://docs.midjourney.com/hc/en-us/articles/32016412137741-GPU-Speed-Fast-Relax-Turbo

## Trash

- Trash removes a creation from the visible Create workflow but is recoverable through Organize under current documented behavior.
- Trash is not permanent deletion and does not prove privacy or data erasure.
- Use it only for explicitly selected targets. Re-observe after every Trash action.

Official sources:

- https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web
- https://docs.midjourney.com/hc/en-us/articles/33329462451469-Organizing-Your-Creations

## Refresh rule

Recheck official sources when:

- the default model, Personalization syntax, profile selector, queue limit, speed modes, plan limits, Create controls, or Trash behavior changes;
- the live interface conflicts with this reference;
- more than 30 days have passed and one of these facts controls an action.
