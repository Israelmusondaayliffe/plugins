---
name: writing-quality-router
description: Routes writing requests to intent architecture, rewriting, detect-only review, or validation. Use when a user asks to draft, rewrite, tighten, humanize, review, or quality-check prose and the correct degree of intervention is unclear. Preserves source claims, separates diagnosis from mutation, and validates the route before execution.
---

# Writing Quality Router

## Overview

Writing Quality owns ordinary prose work. Choose the smallest writing workflow that can satisfy the request. Do not rewrite text when the user asked only for findings.

## Workflow

1. Identify the requested operation, audience, medium, decision, and constraints.
2. Select exactly one primary route using references/routing.md.
3. Record the route in assets/route-template.json and run scripts/validate_route.py.
4. Execute the selected skill:
   - intent-architecture: business-writing-intent-enforcer
   - rewrite: business-writing-intent-enforcer, then writing-enforcer with its source-backed 47-pattern method
   - detect-only: writing-enforcer in `DETECT` report-only mode
   - validation: writing-enforcer against the supplied draft, protected-material boundary, and constraints
5. Use claim-boundary-checker when factual claims exceed the supplied evidence or are unstable.
6. Recheck that the final response matches the requested operation and did not silently expand the factual scope.

## Error Handling

- If the operation is ambiguous but low-risk, choose the least mutating route and state the assumption.
- If the route JSON fails validation, fix the invalid route or missing rationale before writing.
- If sources conflict, preserve the conflict and route factual review to claim-boundary-checker.
- If the user asks for output only, keep routing notes internal.

## Reliability Notes

The model interprets intent and performs the prose work. The validator enforces one allowed route and a recorded rationale. Claim support is checked separately so style edits do not fabricate evidence. Raw Writing Enforcer scores are report-only; the contextual floor is 8.0 and the target is 10.0 with all hard gates clear.

## Ownership boundary

Writing Quality owns ordinary documents, emails, posts, and other prose. Harness Engineering's separate Unslop specialist owns harness and plugin maintenance. Neither capability imports or requires the other at runtime.

## Resources

- scripts/validate_route.py validates routing records.
- references/routing.md defines selection rules and boundaries.
- assets/route-template.json is the reusable route record.
