# Migrate a prompt to Astra

Use when a source prompt already exists.

1. Freeze the source job and acceptance criteria.
2. Apply the classification in `references/migration-overlay.md`.
3. Preserve stable policy and exact output requirements.
4. Remove one coherent group of duplicate or prior-model compensation instructions.
5. Add at most one task-specific Astra restraint for a demonstrated or field-reported risk.
6. Keep the source prompt as rollback evidence.
7. If Astra is unavailable, finish the prompt migration and mark runtime acceptance pending. Do not invent configuration.
