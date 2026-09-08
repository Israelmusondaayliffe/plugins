---
name: claim-boundary-checker
description: Separates supported, unsupported, uncertain, and non-factual statements in prose. Use when editing or drafting could introduce factual claims beyond supplied sources, when a user asks for a claim audit, or when current and high-stakes facts need explicit boundaries. Produces a validated claim ledger without turning ordinary writing work into unnecessary research.
---

# Claim Boundary Checker

## Overview

Protect the factual boundary of a draft. Keep evidence status visible while allowing ordinary prose work to proceed.

## Workflow

1. Define the evidence set: supplied sources, verified tool results, or no evidence.
2. Extract material claims. Ignore pure opinion, obvious framing, and harmless stylistic language.
3. Classify each claim using references/classification.md.
4. Record findings with assets/claim-ledger-template.json.
5. Run scripts/validate_claim_ledger.py.
6. In diagnose or validation mode, report support gaps and suggested remedies without rewriting. In an authorized revision, remove, qualify, source, or explicitly mark unsupported claims unverified.
7. For current, medical, legal, financial, security, or platform-behavior claims, verify through the source of truth before treating them as supported.

## Error Handling

- If no evidence set is supplied, label material factual claims unsupported or uncertain rather than guessing. Missing support in the supplied material is not proof of falsehood or fabrication.
- If a source only partially supports a claim, narrow the claim to the supported scope.
- If live verification is required but unavailable, state the boundary and avoid a confirmed-current claim.
- If the ledger fails validation, fix missing claim text, status, or remedy before delivery.

## Reliability Notes

The model identifies and classifies claims. The validator checks allowed statuses, required fields, and unique identifiers. The skill never treats absence of contradiction as evidence.

## Resources

- scripts/validate_claim_ledger.py validates the ledger.
- references/classification.md defines evidence statuses and remedies.
- assets/claim-ledger-template.json provides the output schema.
