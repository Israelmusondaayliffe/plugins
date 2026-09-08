---
name: midjourney-prompt-batching
description: Reuse selected Midjourney Explore or Create prompts as a controlled web batch, apply the intended Personalization profile, monitor queue capacity, and clean up explicitly named creations. Use when a user asks to batch Midjourney prompts, move Explore ideas into Create, reuse existing jobs with a profile code, manage a Create queue, or Trash selected results. Do not use to invent ordinary prompts or architect V8.2 image edits.
---

# Midjourney Prompt Batching

Run a bounded Explore-to-Create or Create-to-Create batch in the user's authenticated Midjourney web session. Preserve prompt intent, make profile changes exact, observe after every mutation, and stop before cost, speed, or cleanup decisions exceed the user's authority.

## Route first

- Route new or substantially rewritten text-to-image prompts to `brand-world-studio:midjourney-prompt-architect`.
- Route image replacement, inpainting, outpainting, reference composition, or failed V8.2 edits to `brand-world-studio:midjourney-v8-2-edit-architect`.
- Keep this skill on prompt reuse, profile edits, submission pacing, queue observation, and authorized cleanup.

## Authority gate

Interpret `run`, `submit`, `generate`, or `batch these` as authority to submit only the named sources and requested count. Treat `clean the queue`, `trash these`, or an equally specific instruction as separate authority for Trash actions.

Inspecting prompts, profiles, settings, and queue state is read-only. Do not change speed mode, buy Fast time, alter account settings, or Trash anything unless the current request clearly authorizes that exact action.

## Workflow

1. **Confirm the batch contract.** Record the source surface, selected prompts or jobs, target count, exact profile choice, cleanup scope, and whether the request authorizes submission. Ask one concise question only when a missing answer could change what is submitted, billed, or removed from Create.
2. **Load current web rules.** Read `references/current-web-operations.md` before changing a profile, interpreting queue capacity, changing speed, or using Trash. Refresh the affected fact from official Midjourney documentation when the reference is stale or the live interface disagrees.
3. **Open the authenticated surface.** Use the host's available browser or computer-control tool with the user's selected authenticated Midjourney session. If no suitable tool is available, return the prepared batch and manual steps without claiming submission. Observe the page before acting. Stop if authentication is missing, the intended account is unclear, or a fresh login or account change would be required.
4. **Inspect live capacity.** Read current active and queued work, the visible speed mode, Fast-time state, and any platform warning. Do not hardcode queue capacity. Set a submission ceiling equal to the smaller of the authorized count and currently available capacity.
5. **Reuse one source at a time.** On Explore, open `Edit prompt`; on Create, use `Use`. Verify that the expected prompt loaded before editing it. Do not silently rewrite the visual concept.
6. **Apply Personalization exactly.** Preserve a valid existing profile parameter when it already matches the batch contract. Use plain `--p` only when the user's currently selected Personalization state is the intended state. Use the exact supplied profile code when the user names one. Remove a conflicting profile parameter before adding the intended one, and never invent or normalize a code.
7. **Submit and re-observe.** Submit only after the prompt, parameters, profile, and remaining batch count match the contract. Re-observe the Create count, queue state, warnings, and loaded prompt after each submission. Stop at the target, at live capacity, or on the first unexpected state.
8. **Clean only the named scope.** If cleanup is authorized, identify each target from stable visible context such as its selected card, prompt snippet, or creation detail. Use Trash one item at a time, then re-observe. Do not describe Trash as permanent deletion, privacy protection, or account cleanup.
9. **Return a batch receipt.** Report requested count, submitted count, source surface, profile applied, current queue state, Trash actions, skipped items, and the exact reason for any early stop.

## Stop conditions

Stop without guessing when:

- the source card, prompt, profile, or cleanup target is ambiguous;
- the loaded prompt does not match the selected source;
- the queue is full or the live limit cannot be confirmed;
- Midjourney reports no Fast time and continuing would require a speed change or purchase not already authorized;
- a submission, profile change, speed change, purchase, or Trash action exceeds the current request;
- the interface changes enough that the next action cannot be verified from fresh observation.

## Completion

Finish only when every authorized item is submitted, explicitly skipped, or stopped with a reason, and every cleanup target has a terminal result. A prompt copied into the composer is not submitted work. A Trash click is not verified until the surface is re-observed.

Do not restart Codex, change Midjourney account settings, or claim the generated images are good without inspecting their rendered results.
