# Advanced execution

Single-agent execution is the default. Parallel work is an optional mode, not
a quality signal.

## Eligible skills

Only these beta skills define an optional multi-agent path:

- signal-scout for independent source lanes
- research-to-decision-map for evidence analysis and adversarial review
- capability-matcher-and-brief-builder for independent candidate research
- workshop-workbench for a fresh package review

## Escalation test

Use multiple agents only when all of these are true:

1. The work has independent lanes or benefits from a genuinely independent
   review.
2. Each worker has a concrete, bounded deliverable.
3. The expected gain justifies the additional time and tokens.
4. The host supports the required coordination.

Set a finite cap before launching. Use two to four workers, avoid nested
delegation, and reserve one context to integrate the result. Do not launch
workers merely to repeat the same search or generate more options.

If the host lacks multi-agent support, perform the same lanes sequentially.
The completion contract and artifact must remain equivalent.

## Integration

The primary skill owns the final result. It must reconcile contradictions,
remove duplication, show unresolved disagreements, and return one artifact.
Worker output is evidence, not an automatic conclusion.

A skill becomes Tier 3 only when phase-specific agents, routing, or multi-stage
handoffs are required for its core workflow. A bounded optional parallel step
does not by itself create a Tier 3 architecture.
