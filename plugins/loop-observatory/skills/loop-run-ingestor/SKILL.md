---
name: loop-run-ingestor
description: Use when terminal LoopKit or registered Operating Graph runs need idempotent normalization, source registration, corrupt-run handling, or duplicate checks. Read only. Does not execute or repair loops.
---

# Loop Run Ingestor

1. Read `../../references/normalized-schema.md`.
2. Register every Operating Graph root explicitly before ingestion.
3. Run `python3 ../../scripts/loop_observatory.py ingest`.
4. Treat corrupt and incomplete sources as errors, not terminal successes.
5. Confirm the source fingerprint before and after ingestion when proving read-only behavior.
6. Return counts for ingested, unchanged, incomplete, and corrupt sources.
