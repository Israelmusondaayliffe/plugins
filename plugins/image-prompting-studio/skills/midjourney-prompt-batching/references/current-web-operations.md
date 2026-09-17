# Current Midjourney web operations

Baseline observed: September 1, 2026. Scope rules updated September 13, 2026 from the approved shared understanding; product facts below remain dated until checked against the live interface.

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
- Preserve exact supplied profile strings, including intended multiple tags. Replace only the conflicting profile component the user intends to change; do not normalize a historical code to a current ID.
- An explicit supplied code owns its requested job even if account defaults differ. Ask only when the intended profile is unresolved; do not silently change persistent preferences.

Official source: https://docs.midjourney.com/hc/en-us/articles/32433330574221-Personalization

## Explore and Create reuse

- Explore cards can be opened and reused through prompt-editing controls.
- Existing Create jobs can populate a new prompt through `Use`.
- Verify the composer contents before submission because UI state, selected styles, and parameters can carry over.
- A visible Create count is a state clue, not proof that each requested job was accepted.

Official source: https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web

## Queue capacity

Read live queue state and current account capacity before submitting. A September 1 note recorded a 10-job documented queue maximum, while the September 13 inspection showed 13 queued jobs. Neither number is a universal limit. A full-queue warning pauses additional submissions; continue tracking already accepted work.

Official source: https://docs.midjourney.com/hc/en-us/articles/27870484040333-Comparing-Midjourney-Plans

## Speed and Fast time

- Speed settings synchronize between the website and Discord.
- Relax availability depends on the user's plan and current product rules.
- A `No Fast hours left` state does not authorize a speed change or purchase.
- This workflow defaults to Relax under the approved user preference. Verify availability and prefer a supported per-job control or already-Relax context. A persistent setting change that could disturb concurrent user work needs a specific decision when no safe per-job option exists.
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
