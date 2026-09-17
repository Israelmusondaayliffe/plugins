---
name: midjourney-prompt-batching
description: Run bounded Midjourney jobs from new prompts, selected Explore items or existing creations. Use for Void Style Hunter, style-code exploration, prompt reuse, queue monitoring, selected HD variations or explicitly requested cleanup.
---

# Midjourney prompt batching

Carry a requested batch through its actual milestones in the authenticated Midjourney session. Read [web operations](references/current-web-operations.md). For Void Style Hunter, read [the preserved recipe](references/void-style-hunter.md). For prompt construction, use the relevant creation/edit guidance only when the task needs it; existing prompts can be reused directly.

## Set the operation

Record the requested source items or new prompts, submission count, folder, selected model, desired output stage, reference/profile/style settings, speed and budget. Use known context; ask only for a missing choice that changes scope or prevents submission. Read-only discovery does not authorize generation. A request to run or submit a named batch authorizes that scope. Assistant discovery/curation is optional when requested; The user owns final creative selection.

Default requested work to Relax unless the user says otherwise. Inspect the live mode before submitting. Prefer a supported per-job Relax control or an already-Relax session. If a persistent mode change would affect the user's simultaneous work and no per-job control is available, obtain the missing decision. Never purchase Fast time or silently fall back to a spending mode. Personalization training and Trash require separately named scope.

## Observe, submit and follow through

1. Use the host's available browser surface (an in-app browser, a browser extension bound to the user's existing session, or Computer Use) after verifying it permits the needed browser actions. Inspect the current page and account context. Resolve controls from fresh observed state rather than assumed labels. If authenticated access or a needed tool is unavailable, report that limit and deliver any requested prompts without claiming jobs ran.
2. Inspect the live selected model, exposed controls, current folder, active/queued jobs, capacity and notices. Read the Midjourney entry in `../../references/model-profiles.md` for compatibility. The old local queue count and Draft restrictions are dated snapshots, not action limits.
3. Select one source. For Explore, inspect the image and full source prompt before reusing it. For an own creation, preserve its job identity and settings. For new work, prepare the complete requested prompt. Use the exact current profile ID or historical code intended by the task; preserve multiple tags where supplied. Never substitute a current profile for a historical code silently.
4. Re-observe the composer before writing. If the user has changed it, preserve their work and use a separate safe context or wait. Do not overwrite their active input. Fill only the intended prompt/reference fields and verify the exact loaded text, codes, folder and mode before submission.
5. Submit one intended job, then re-observe for acceptance and a job ID or equivalent stable evidence. Record it in the operation receipt. If submission state is uncertain, inspect history/queue before any retry. A copied prompt, spinner or changed total alone does not establish acceptance.
6. Stop sending new work at the requested count or live capacity. A full queue pauses submission; it does not cancel accepted work. Monitor at sensible intervals, account for Relax speed, and report progress while waiting. Do not resubmit queued or slow-running jobs.
7. Inspect actual results when the requested stage includes rendering. Keep requested, accepted, queued/running, rendered, curated and HD-variation counts separate. A submission-only request can finish after verified acceptance; a render or curation request cannot finish there.
8. Preserve selected-image identity through curation and HD actions. Submit HD variations only for the selected image IDs within the requested scope. Inspect the resulting HD jobs separately. Saving a preferred reusable recipe needs the user's explicit selection; a UI selection or operational receipt is not that approval.
9. For explicitly requested cleanup, identify exact targets, use recoverable Trash narrowly and verify each result. Report skipped or unresolved targets. Do not imply Trash deletes account data permanently.

## Completion and stops

Finish when every requested item reaches the requested milestone or is explicitly unresolved with a reason. Keep one compact receipt containing item/source identity, exact prompt/settings, acceptance evidence, job/status, output links or files when available, user selections, HD lineage and any remaining work. Operational tracking is permitted for duplicate prevention; it does not approve a recipe.

Pause dependent actions on a mismatched prompt, changed user input, ambiguous source, uncertain acceptance, unsupported requested model/control, account warning or exhausted budget. Respect normal queue waiting. Continue already-authorized work when the issue clears; never compensate with extra submissions or purchases. Describe incomplete milestones plainly.
