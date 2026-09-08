# Model prompt routing

generate: create a new production prompt for a verified target model.
migrate: preserve the task while adapting model-specific structure, effort, tools, and constraints.
diagnose: find why an existing prompt underperforms before rewriting it.
benchmark: define representative cases, assertions, metrics, and stops.
working-mode: use fable-mode when the job is a reusable reasoning process rather than a single prompt.

Use gpt-5-6-production-prompter for verified GPT-5.6 work. Keep gpt-5-4-production-prompter as a legacy and migration route. Use fable-5-production-prompter for Fable or Mythos prompt work. Current platform behavior must be checked with the owning documentation.

GPT-6 Astra: gpt-6-astra-production-prompter.
Claude Fable 5.1: fable-5-1-production-prompter.
Older model skills remain explicit compatibility routes, not the current model default.
