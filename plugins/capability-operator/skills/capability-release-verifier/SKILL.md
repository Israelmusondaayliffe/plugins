---
name: capability-release-verifier
description: Verifies a loose skill, personal plugin, or public cross-platform capability release against a profile-specific proof chain. Use after creating, upgrading, installing, or publishing a capability when completion requires source inventory, validation, installed state, source-cache parity, routing, clean-task discovery, remote release, anonymous installation, or catalog and Sites synchronization evidence.
---

# Capability Release Verifier

Select one acceptance profile and produce one evidence receipt. A release passes only when every required check for that profile has current evidence.

## Profiles

Read [acceptance profiles](references/acceptance-profiles.md), then choose exactly one:

- `global-loose-skill`: package inventory, destination, validation, and clean-task visibility.
- `personal-plugin`: installed and enabled state, bundle validation, source-cache parity, routing, and clean-task discovery.
- `public-cross-platform-release`: version and Codex/Claude manifest parity, GitHub default-branch proof, anonymous install, catalog or Sites synchronization, and a shareable installer.

## Workflow

1. Resolve the source owner and exact release target.
2. Copy [evidence receipt template](assets/evidence-receipt-template.json).
3. Run the profile’s required checks using the source-owning tools:
   - Plugin Creator for local scaffold, validation, cachebuster, and reinstall.
   - Plugin Portfolio Manager for ownership and lifecycle records.
   - Fresh Task Discovery Verifier for clean-process prompt visibility.
   - Harness Engineering for plugin engineering or harness verification.
   - GitHub for remote state and anonymous clone proof.
   - Sites only when the approved release includes a hosted catalog or artifact.
4. Record structured evidence for every check in a separate `CapabilityReleaseEvidence` JSON record. Bind the receipt to each record with the record's SHA-256, and bind every record to the receipt's exact checked-out Git commit. The receipt may contain only the record reference, not caller-supplied `verified`, `exit_code`, `value`, command, or result fields. Command records must also hash their recorded stdout and stderr files. A statement without hash-bound evidence is not a pass.
5. Validate the receipt:

```bash
python3 scripts/validate_release_evidence.py \
  --profiles assets/acceptance-profiles.json \
  --receipt /absolute/path/to/evidence-receipt.json
```

6. Return the validator result and the exact receipt path.

## Guardrails

- Treat installation, enabled state, routing, and clean-task discovery as separate checks.
- Compare full source and cache inventories, including hidden files.
- Use the exact pushed commit for remote and anonymous-install proof.
- Do not publish, upload, or change access without explicit authority.
- Mark missing evidence `blocked` or `failed`. Do not soften it into a pass.
- Keep local cachebuster versions distinct from stable public semantic versions.
