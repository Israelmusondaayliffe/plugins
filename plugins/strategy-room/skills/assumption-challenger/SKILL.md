---
name: assumption-challenger
description: Tier 3 research-first assumption challenger. It researches current sources, builds a challenge plan, examines the subject through several lenses, checks findings against the research, and returns a recommendations report. Use when user says "challenge assumptions," "analyze blind spots," "what am I missing," "critique this," "find contradictions," "stress test this," "what could go wrong," "tear this apart," or asks for rigorous adversarial review of plans, prompts, strategies, ideas, business cases, technical decisions, or AI prompts. Five-agent pipeline (researcher, planner, challenger, verifier, synthesizer). Three effort modes (light, standard, deep). Mandatory web search before challenge so the critique is grounded in current facts and expert disagreement, not training-data instinct.
license: MIT
metadata:
  author: Community Maintainers
  version: 2.0.0
  tier: 3
---

# Assumption Challenger

Research-grounded adversarial review. The skill becomes a domain expert through web search before challenging anything, then runs a five-phase pipeline that ends in a verified, actionable report.

## Why This Skill Exists

A challenge that isn't grounded in current facts is just confident speculation. Stale training data, generic critique patterns, and unchecked LLM instinct produce reviews that sound rigorous but miss the actual weak points. This skill enforces a research-first workflow so every assumption flagged, every contradiction surfaced, and every recommendation made is anchored in evidence the user can verify.

## How It Works

SKILL.md is the orchestrator. It does not produce the final report itself. It assesses the request, picks the effort mode, and routes through five sub-agents in sequence. Each sub-agent has a focused scope, a defined output, and a handoff protocol. A deterministic script gates the transition from research to challenge so the pipeline cannot proceed on a thin dossier.

The five phases:

1. **Research** (`agents/researcher.md`). Deep web search to become an expert in the subject. Outputs a research dossier.
2. **Plan** (`agents/planner.md`). Reads the dossier and the user's content, builds a targeted challenge plan. Outputs an analysis plan.
3. **Challenge** (`agents/challenger.md`). Runs the five lenses against the plan. Outputs raw challenge findings.
4. **Verify** (`agents/verifier.md`). Triple-verifies every finding against the research dossier and the plan. Outputs verified findings.
5. **Synthesize** (`agents/synthesizer.md`). Assembles the user-facing report with TL;DR, recommendations, and "if overwhelmed, start here" priorities. Outputs the final deliverable.

## Router Logic

Default route: full pipeline. Run all five phases in sequence on the user's input.

The orchestrator should also handle these explicit requests:

**"Just research X" / "Get me up to speed on Y"**
Route to `agents/researcher.md` only. Return the dossier as the deliverable.

**"I already have research, just challenge this" / "Skip the research"**
Route to `agents/planner.md` with the user's research as input. Continue through challenger, verifier, synthesizer.

**"Re-verify this report" / "Stress test these findings"**
Route to `agents/verifier.md` with the prior findings as input. Then `agents/synthesizer.md`.

**"Give me a quick gut check" / "Light pass"**
Set effort mode to `light`. Run the full pipeline at reduced depth.

**"Go deep on this" / "Maximum rigor" / "Stakes are high"**
Set effort mode to `deep`. Run the full pipeline at maximum depth.

If the request is ambiguous, ask one focused question. Do not run the pipeline blind.

## Effort Modes

The effort mode shapes how each agent operates. Set it once at the orchestrator level. Pass it to every agent.

**Light** (~5 min, low context cost)
- Researcher: 3 to 5 web searches. No web_fetch unless a single source is critical.
- Planner: 3 lenses prioritized (skip alternate viewpoints and meta-analysis unless directly relevant).
- Challenger: focused execution on prioritized lenses. 3 to 5 findings per lens.
- Verifier: spot-check critical findings, not every finding.
- Synthesizer: ~600 word report. TL;DR, top 3 priorities, top 3 questions, top 3 recommendations.

**Standard** (default, ~10 min)
- Researcher: 8 to 12 web searches across multiple subtopics. web_fetch on 2 to 3 highest-value sources.
- Planner: all 5 lenses, prioritized by relevance to the input.
- Challenger: full execution. 5 to 8 findings per lens.
- Verifier: every finding verified against dossier. Confidence calibrated.
- Synthesizer: ~1200 word report. Full 7 sections.

**Deep** (~20 min, high context cost)
- Researcher: 15+ web searches. web_fetch on 5+ sources. Cross-reference expert disagreement explicitly. Track recency for every claim.
- Planner: all 5 lenses with explicit hypotheses to test under each.
- Challenger: full execution. 8+ findings per lens. Includes improbable scenarios and second-order effects.
- Verifier: triple-verification. Every claim traced to a dossier entry. Every confidence score justified.
- Synthesizer: ~2500 word report. Full 7 sections plus appendix with research dossier excerpts and verification log.

Default to standard. Only escalate to deep when the user signals high stakes, asks for maximum rigor, or the subject involves consequential decisions (financial, medical, legal, strategic).

## Phase Handoff Protocol

Between phases, the orchestrator must verify:

1. **Researcher → Planner**: Run `scripts/dossier_check.py` against the research dossier. The script validates source count, source diversity, recency, and dimensional coverage. If it fails, send the dossier back to the researcher with the failure reasons. Do not proceed to planning until the script passes.

2. **Planner → Challenger**: Confirm the plan covers all required lenses for the effort mode. Confirm each lens has at least one specific hypothesis to test.

3. **Challenger → Verifier**: Confirm every finding has a claim, a reasoning chain, and a confidence draft. Findings without these are incomplete and must be returned.

4. **Verifier → Synthesizer**: Confirm every finding is now annotated with a verification status (confirmed, partially confirmed, not confirmed by research, speculative). Findings marked "not confirmed by research" must be either downgraded to speculative or removed before synthesis.

5. **Synthesizer → User**: Confirm the report includes TL;DR, all required sections for the effort mode, calibrated confidence, and an "if overwhelmed, start here" section.

## Shared Resources

All phases draw from these references. The orchestrator does not load them itself. Each agent loads only what it needs.

- `references/analysis_frameworks.md`. The five lenses with detailed sub-frameworks. Used by planner and challenger.
- `references/research_protocol.md`. Source tiering, recency rules, expert disagreement detection. Used by researcher.
- `references/verification_protocol.md`. Triple-verification methodology, confidence calibration, evidence chains. Used by verifier.
- `references/cognitive_biases.md`. Bias taxonomy and detection patterns. Used by challenger and verifier.
- `references/example_reports.md`. Sample outputs for different input types. Used by synthesizer.

## Templates

Each phase produces a structured artifact using a template from `assets/`. Templates exist so the handoff between agents is unambiguous and the script can validate structure deterministically.

- `assets/research_dossier_template.md`. Researcher output.
- `assets/analysis_plan_template.md`. Planner output.
- `assets/challenge_findings_template.md`. Challenger output.
- `assets/verified_findings_template.md`. Verifier output.
- `assets/final_report_template.md`. Synthesizer output. The user-facing deliverable.

## Script

`scripts/dossier_check.py` is the deterministic gate between research and challenge. It validates the dossier on:

- Minimum source count (varies by effort mode)
- Source diversity (no more than 50% from one domain)
- Recency (at least 30% of sources from the last 12 months for fast-moving subjects)
- Dimensional coverage (the dossier must touch at least 4 of: technical, market, user, regulatory, ethical, historical)

Run it after every researcher output. Do not proceed past research until it passes.

## Error Recovery

If any phase fails or produces unusable output, do not paper over it. Surface the failure to the user with three options: retry the phase, downgrade the effort mode, or abandon the analysis. Do not silently continue with broken intermediate output. A bad dossier produces a bad challenge. A bad challenge produces a bad recommendation. The pipeline is only as strong as its weakest phase.

## Output

By default, the user sees only the final report from the synthesizer. The intermediate artifacts (dossier, plan, raw findings, verified findings) are kept by the orchestrator and surfaced only on request. If the user asks "show me your research" or "how did you verify this", the orchestrator can surface the relevant intermediate artifact.

## Special Considerations for AI Prompt Analysis

When the input is an AI prompt (for Claude, GPT, Gemini, or any model), the planner should additionally check:

- Is the task clearly defined?
- Are examples provided (few-shot learning)?
- Is output format specified?
- Are constraints and guardrails explicit?
- Is chain-of-thought or reasoning encouraged?
- Are edge cases handled?
- Does the prompt use model-specific capabilities?
- Are model limitations being overlooked?
- Is the prompt structured for token efficiency?

The researcher should research the specific model's current capabilities (training cutoff, context window, known weaknesses, recent updates). Prompt analysis without current model knowledge produces stale advice.

## When Not to Use This Skill

- Quick yes/no questions where one search beats a five-phase pipeline.
- Pure creative brainstorming where critique would kill the divergent thinking.
- Emotional support requests dressed as critique requests. If the user wants validation, this skill is the wrong tool.
- Subjects where research is impossible (private internal data only the user has access to). In that case, run the pipeline without the research phase and explicitly flag the gap in the final report.

## Version History

- 2.0.0 (Apr 2026): Tier 3 upgrade. Five-agent pipeline. Mandatory research phase. Deterministic dossier gate. Triple-verification protocol. Three effort modes.
- 1.0.0 (Oct 2025): Initial Tier 1 release. Single SKILL.md with five lenses.
