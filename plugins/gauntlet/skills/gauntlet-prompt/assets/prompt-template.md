# Lead-agent prompt skeleton

Fill the placeholders, keep the result under 400 words, and run `${CLAUDE_PLUGIN_ROOT}/scripts/lint_prompt.py` before surfacing it. Do not add architecture, file layouts, module lists, tech stacks, or round counts. Platform note per `docs/BUILD-NOTES.md`, verified 2026-07-29: the current effort ladder is low / medium / high / xhigh / max, and `ultracode` is the multi-agent opt-in token, so fill `{{effort_setting}}` from the top of that ladder and use `ultracode` where multi-agent mode needs opting in.

---

{{goal}}

The bar: {{bar_description}}. The reference artifacts and measurements are at {{bar_paths}}. Beat that bar. You may not argue with it, soften it, or replace it.

Split the goal into the smallest independently judgeable pieces. You own the decomposition and may re-split as you learn.

For each piece, loop in rounds: a builder improves the real artifact, then a separate critic with fresh context judges it against the bar. The critic never sees the builder's reasoning, history, or summaries.

Compare blind wherever possible: neutral labels, no provenance, judgment on the inspected output rather than on descriptions of it.

{{knowledge_work_clause}} <!-- include for prose, research, strategy, deck, and prompt-system domains: "Inspect every knowledge-work piece with a fresh reader-proxy agent against its frozen question set, and maintain a claim ledger validated by claim_audit.py." -->

Loop each piece until it beats the bar or the user stops the run. Caps pause work; they never certify it.

Write all state to {{run_dir}} after every round.

Keep the live progress page at {{run_dir}}/workbench.html regenerated from state after every round.

Use subagents freely and run at the highest effort setting ({{effort_setting}}, with ultracode where multi-agent work needs opting in).
