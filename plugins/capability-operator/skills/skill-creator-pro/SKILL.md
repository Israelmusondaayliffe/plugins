---
name: skill-creator-pro
description: Professional-grade skill creation framework with 3-tier architecture (simple, complex, agentic), eval/iteration loop with grading agents and interactive review, reliability patterns, deep discovery, MCP integration guidance, and Anthropic-aligned best practices. Use when creating new skills or updating existing skills that need to work reliably, handle edge cases, use appropriate tools (scripts for deterministic accuracy, templates for consistency), validate outputs, anticipate failure modes, or coordinate across MCP servers. Includes tier selection framework, orchestrator/router patterns for agentic skills, structured eval loop with benchmark aggregation, description optimization pipeline, blind A/B comparison, and production-grade quality gates. Triggers on skill creation, skill update, build a skill, create a skill, improve skill, test a skill, run evals, benchmark skill, optimize description, or any request to package Claude workflows into reusable skills.
---

# Skill Creator Pro

Create professional, reliable skills through systematic discovery, tier-appropriate architecture, eval-driven iteration, and production-grade quality gates.

Your job is to figure out where the user is in the creation process and help them progress. Maybe they want to build from scratch. Maybe they already have a draft and want to test it. Maybe they want to skip evals and just vibe. Be flexible, but know the full process so you can guide them through it.

## What Skills Are

A skill is a folder. Each folder has a clear anatomy:

- **SKILL.md** = the standard operating procedure + orchestrator + router. The instructions.
- **references/** = knowledge. Domain docs, shared context, anything Claude needs to read for understanding.
- **scripts/** = code. Deterministic operations, validation, calculations.
- **assets/** = templates. Output patterns, reusable materials, files used in final output.
- **agents/** = agent instruction sets. Focused sub-agents for distinct phases (Tier 3). Separate from references because agents are instructions that drive behavior, not passive knowledge.

Instead of re-explaining workflows every conversation, skills teach Claude once. They pair with Claude's built-in capabilities and add a knowledge layer on top of MCP integrations.

**Skills are portable.** They work identically across Claude.ai, Claude Code, and the API. Build once, deploy everywhere.

**Skills are composable.** Claude can load multiple skills simultaneously. Each skill should work alongside others without conflict.

### Skills + MCP

MCP provides connectivity. Skills provide knowledge.

- **MCP:** Connects Claude to services, provides real-time data and tool invocation. What Claude CAN do.
- **Skills:** Teaches workflows and best practices for using those tools. How Claude SHOULD do it.

Without skills, users connect MCP but start from scratch every time. With skills, pre-built workflows activate automatically with consistent results.

## The 3-Tier Architecture

Every skill fits one of three tiers. Assess tier BEFORE building. This determines structure, resource needs, and creation approach.

### Tier 1: Simple Tasks

For straightforward, single-purpose tasks with clear inputs and outputs.

**Composition:** SKILL.md (instructions) + References (knowledge base) OR Assets (templates) + Tool use (built-in or MCP).

**Characteristics:** One workflow path. Minimal branching. Claude's native intelligence handles most decisions. Instructions plus knowledge are sufficient.

**Examples:** Style guide enforcement, single-format document creation, prompt generation for one model, simple data extraction.

**Signal phrases:** "When I say X, do Y." "Always format it like this." "Follow this template."

### Tier 2: Complex Tasks

For tasks requiring deterministic accuracy, multiple resource types, and validation.

**Composition:** SKILL.md + References + Assets (templates) + Scripts (deterministic code) + Tool use.

**Characteristics:** Multiple operation types. Some operations must be exact (calculations, formatting, data transforms). Probabilistic LLM behavior needs offset with deterministic scripts. Validation at critical points.

**Examples:** File format manipulation, data processing pipelines, API integrations with error handling, report generation with calculations.

**Signal phrases:** "Must be exact." "Can't have calculation errors." "Feeds into another system."

### Tier 3: Multi-Step Agentic Tasks

For multi-phase workflows where SKILL.md acts as orchestrator routing to specialized sub-agents.

**Composition:** SKILL.md (orchestrator/router) + Agents (phase-specific instruction sets in agents/) + References (knowledge) + Assets (templates) + Scripts (code) + Tool use (built-in and/or multiple MCP servers).

**Characteristics:** SKILL.md does NOT do the work. It assesses the request, determines which phase or agent handles it, and routes accordingly. Each sub-agent is a focused instruction set for one phase. Multi-MCP coordination common. Clear handoffs between phases.

**Examples:** End-to-end production workflows, multi-service orchestration, complex business processes with compliance gates.

**Signal phrases:** "Multiple steps across different tools." "Route to the right workflow." "Orchestrate across services."

### Tier Selection Decision Tree

```
Is the task a single workflow with one primary operation?
  YES -> Does it need scripts for accuracy-critical operations?
    NO  -> Tier 1
    YES -> Tier 2
  NO  -> Does it involve multiple phases, services, or routing logic?
    NO  -> Tier 2 (multiple operations, single orchestration)
    YES -> Tier 3
```

**When unsure, start Tier 2.** It covers most professional use cases. Upgrade to Tier 3 only when routing logic is clear and phases are genuinely distinct.

Load `references/tier-architecture.md` for detailed examples, anti-patterns, and implementation guidance per tier.

## Core Principles

### 1. Concise is Key

Context window is a shared resource. Claude is already very smart. Only add what Claude doesn't know. For every element, ask: Does Claude really need this? Does it justify its token cost?

Prefer concise examples over verbose explanations.

### 2. Reliability First

LLMs are probabilistic. When accuracy matters, use deterministic approaches. Choose scripts over LLM generation for calculations. Choose templates over free-form for structured output. Choose validation over trust for critical operations. Choose examples over rules for quality standards.

### 3. Set Appropriate Degrees of Freedom

- **High freedom (text instructions):** Multiple valid approaches, context-dependent.
- **Medium freedom (parameterized scripts):** Preferred pattern exists, some variation OK.
- **Low freedom (specific scripts):** Fragile operations, consistency critical.

### 4. Progressive Disclosure

Skills use three-level loading:

1. **YAML frontmatter.** Always loaded in system prompt. Tells Claude when to load the skill. Keep under ~100 words.
2. **SKILL.md body.** Loaded when Claude determines the skill is relevant. Aim for under 500 lines.
3. **Linked files.** Additional files Claude navigates only as needed. Unlimited size.

Load `references/predictable-skill-writing.md` before drafting or pruning instructions. It defines invocation load, leading words, completion criteria, split tests, and deletion rules. Apply it before adding architecture: the smallest skill that passes its behavior cases is the preferred design.

### 5. Composability

Skills must work alongside other skills. Avoid claiming exclusive ownership of broad task categories.

### 6. Explain the Why

Today's LLMs have good theory of mind. Explaining the reasoning behind instructions is more powerful than rigid MUSTs and NEVERs. If you find yourself writing ALWAYS in all caps, that's a yellow flag. Reframe and explain so the model understands why the thing matters.

## CRITICAL: Skill Format Requirements

These rules are mandatory. Violations cause packaging failures.

### Naming Convention

Kebab-case only: `my-skill-name`. Lowercase letters, digits, hyphens. No leading/trailing/consecutive hyphens. Max 64 characters. Folder name MUST exactly match frontmatter `name` field.

### Frontmatter

```yaml
---
name: skill-name              # Required. Kebab-case. Max 64 chars.
description: What and when.   # Required. Max 1024 chars. No angle brackets.
license: MIT                  # Optional.
allowed-tools: "Bash(python:*) WebFetch"  # Optional.
compatibility: "Requires Python 3.9+"     # Optional.
metadata:                     # Optional.
  author: Company Name
  version: 1.0.0
---
```

**Security:** No XML angle brackets (`<>`) in frontmatter. No skills named with "claude" or "anthropic" prefix.

### Description Requirements

Structure: `[WHAT it does] + [WHEN to use it] + [KEY capabilities]`

Include specific phrases users would say. Mention file types, tool names, domain terms. Be slightly "pushy" to combat undertriggering. Claude tends to undertrigger, so make descriptions assertive about when to use the skill.

Load `references/trigger-optimization.md` for comprehensive trigger guidance.

## Skill Anatomy by Tier

### All Tiers

```
skill-name/
├── SKILL.md              # Required. Instructions (or orchestrator for Tier 3).
├── references/           # Optional. Knowledge docs loaded into context as needed.
├── assets/               # Optional. Templates, fonts, icons used in outputs.
├── scripts/              # Optional (Tier 2+). Executable code for determinism.
└── agents/               # Optional (Tier 3). Sub-agent instruction sets.
```

### Tier 3 Structure (Orchestrator Pattern)

```
studio-production/
├── SKILL.md                    # Orchestrator. Routes to phase agents.
├── agents/
│   ├── agent-brief.md          # Sub-agent: creative brief phase
│   ├── agent-production.md     # Sub-agent: production phase
│   └── agent-review.md         # Sub-agent: review/QA phase
├── references/
│   ├── brand-guidelines.md     # Shared knowledge base
│   └── platform-specs.md       # Shared reference
├── assets/
│   ├── brief-template.md       # Template for brief phase
│   └── review-checklist.md     # Template for review phase
└── scripts/
    ├── validate_output.py      # Deterministic validation
    └── format_publish.py       # Deterministic formatting
```

**Why agents/ is separate from references/:** Agents are instruction sets that drive behavior. They tell Claude what to do and how. References are passive knowledge, context that informs decisions. Mixing the two muddies the distinction between "do this" and "know this." Keeping agents in their own directory makes the skill's architecture legible at a glance: you can see how many behavioral modes exist just by listing the agents/ folder.

The SKILL.md orchestrator pattern:

```markdown
## Router Logic
Assess the user's request and route to the appropriate phase:

**Creative brief request** -> Load `agents/agent-brief.md`, follow its workflow
**Production request** (with approved brief) -> Load `agents/agent-production.md`
**Review request** (with production output) -> Load `agents/agent-review.md`

If request is ambiguous, ask user which phase they need.
```

Load `references/tier-architecture.md` for complete Tier 3 orchestrator patterns.

## Reliability Decision Framework

**When to use scripts:** Calculations, exact values, consistent formatting, repeatable operations, validation checks.

**When to use templates:** Format consistency critical, standard structure, reusable patterns.

**When to use LLM reasoning:** Creativity valued, context-dependent judgment, approximate acceptable.

**Recommended hybrid:** LLM determines WHAT to do + Scripts execute HOW + LLM presents results + Scripts validate output.

Load `references/reliability-patterns.md` for comprehensive pattern guidance.

## Skill Creation Process

Follow these steps in order. The process applies to all tiers, with tier-specific branching noted.

### Step 1: Deep Discovery

Understand the user's intent. The current conversation might already contain a workflow to capture (e.g., "turn this into a skill"). If so, extract answers from conversation history first, then fill gaps.

#### Functional Requirements
- What should this skill enable Claude to do?
- Walk through a complete use case from start to finish.
- What variations exist? What would a user say to trigger this?

#### Reliability Requirements
- What must be 100% accurate versus approximate?
- Where do errors cause problems?
- What operations should be deterministic?

#### Edge Cases and MCP Dependencies
- What unusual inputs or scenarios exist? What could break this?
- Which MCP servers are needed? What errors are common with those tools?

Proactively ask about edge cases, example files, success criteria, and dependencies. Check available MCPs for research.

**Conclude when:** Clear sense of functionality, reliability needs, edge cases, and MCP dependencies.

### Step 2: Assess Tier

Based on discovery answers, use the Tier Selection Decision Tree above. State the tier explicitly to the user. Explain why. Get confirmation before proceeding.

### Step 3: Plan Resources

Identify what scripts, references, assets, and (for Tier 3) sub-agents the skill needs. Validate plan against discovery: Do resources address edge cases? Handle failure modes?

### Step 4: Initialize the Skill

```bash
python scripts/init_skill.py <skill-name> --path <output-directory> --tier <1|2|3>
```

Skip if skill already exists (go to Step 5).

### Step 5: Implement the Skill

#### 5A: Implement Bundled Resources

**Scripts:** Write with reliability focus. Test including edge cases. Add error handling.

**References:** Create focused markdown files for domain knowledge and shared context. Table of contents if over 100 lines.

**Agents (Tier 3):** Write sub-agent instruction sets in `agents/`. Each agent is a focused behavioral instruction set for one phase. Agents drive action, references provide knowledge. Keep them separate.

**Assets:** Add actual files, not placeholders. Verify formats.

#### 5B: Write SKILL.md

**Writing style:** Imperative form. "Extract text from PDF" not "You should extract text from PDF." Try to explain why things are important in lieu of heavy-handed MUSTs. Use theory of mind, make the skill general, not narrow to specific examples.

**For Tier 1 and 2:** Write workflow instructions. Reference bundled resources explicitly. Include examples.

**For Tier 3:** Write the orchestrator/router. Define routing logic. Reference each sub-agent in `agents/` with explicit load instructions.

**Keep SKILL.md under 500 lines.** Move detailed content to references/.

Load `references/workflows.md` for workflow patterns. Load `references/output-patterns.md` for output format guidance.

### Step 6: Test and Iterate

This is the eval loop. The single most important step for skill quality. Draft, run, grade, review, improve, repeat.

#### Write Test Cases

Come up with 2-3 realistic test prompts. The kind of thing a real user would actually say. Share them with the user for confirmation. Save to `evals/evals.json`. Don't write assertions yet, just prompts.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema including the `assertions` field.

#### Run the Eval Loop

Load `references/eval-loop.md` for the complete procedure. Summary of the cycle:

1. **Spawn runs** (with-skill AND baseline) for each test case
2. **Draft assertions** while runs execute (use the wait time)
3. **Capture timing** from task completion notifications
4. **Grade, aggregate, launch viewer** for user review
5. **Read feedback** and improve the skill
6. **Repeat** until the user is satisfied

The eval loop section covers workspace organization, grading procedures, benchmark aggregation, the interactive viewer, and improvement philosophy.

#### Testing Coverage

**Triggering tests.** 10+ realistic queries, split should-trigger and should-not-trigger. Focus edge cases on near-misses.

**Functional tests.** For each use case: Given (input), When (skill executes), Then (expected output).

**Performance comparison.** With-skill vs without-skill on same tasks.

#### Iteration Signals

- Skill doesn't trigger -> Improve description keywords
- Instructions not followed -> Simplify, put critical items at top, explain WHY
- Output inconsistent -> Add templates or validation
- Repeated code in runs -> Bundle as script (this is a strong signal)
- SKILL.md too long -> Move content to references

### Step 7: Description Optimization

After the skill is working well, optimize its description for better triggering accuracy.

#### Generate Trigger Eval Queries

Create 20 eval queries. Mix of should-trigger (8-10) and should-not-trigger (8-10).

Queries must be realistic. Include file paths, personal context, casual speech, abbreviations. Not abstract requests.

Bad: `"Format this data"`
Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a profit margin column"`

For should-not-trigger, the most valuable ones are near-misses. Queries that share keywords but actually need something different.

#### Review With User

Present the eval set using the HTML template from `assets/eval_review.html`. Replace the placeholders (`__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`), write to temp file, and open for user review.

#### Run the Optimization Loop (Claude Code only)

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

This handles full optimization automatically. It splits the eval set into 60% train / 40% held-out test, evaluates the current description (3 runs per query for reliability), calls Claude to propose improvements based on failures, re-evaluates, and iterates up to 5 times. Selects best description by test score to avoid overfitting.

Take `best_description` from the JSON output and update the skill's frontmatter. Show user before/after and report scores.

Load `references/trigger-optimization.md` for full guidance.

### Step 8: Package and Distribute

**Before packaging:** Run pre-packaging validation.

```bash
python scripts/quick_validate.py <path/to/skill>
```

Load `references/quality-checklist.md` for comprehensive quality gates by tier.

**Package:**

```bash
python scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

If `present_files` tool is available, present the .skill file to the user so they can install it.

## Environment-Aware Instructions

The core workflow (draft, test, review, improve, repeat) stays the same across environments. Some mechanics change.

### Claude.ai

No subagents. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. One at a time. This is less rigorous (you wrote the skill and you're running it), but it's a useful sanity check and user review compensates. Skip baseline runs. Skip quantitative benchmarking. Present results directly in conversation. For file outputs, save and tell the user where to download. Focus on qualitative feedback.

Description optimization (`run_loop.py`) requires `claude -p` which is only available in Claude Code. Skip it on Claude.ai.

### Claude Code

Full workflow available. Subagents for parallel execution, browser for viewer, `claude -p` for description optimization. This is the richest environment.

### Cowork

Subagents available. No browser or display. Use `--static <output_path>` for the eval viewer to write standalone HTML. Feedback works via file download ("Submit All Reviews" downloads `feedback.json`). Description optimization works via `claude -p`.

## Updating Existing Skills

When updating rather than creating:

1. **Preserve the original name.** Note the skill's directory name and `name` frontmatter field. Use them unchanged.
2. **Copy to a writable location before editing.** The installed skill path may be read-only. Copy to `/tmp/skill-name/`, edit there.
3. **If packaging manually, stage in `/tmp/` first**, then copy to the output directory.

## Communicating With the User

People across a wide range of familiarity use skill-creator. Pay attention to context cues. "Evaluation" and "benchmark" are borderline but OK. For "JSON" and "assertion," see cues from the user that they know what those are before using them without explaining. It's OK to briefly explain terms if in doubt.

If the user says "I don't need evals, just vibe with me," that's fine. Adapt.

## Resources in This Skill

### references/tier-architecture.md
Detailed guide for all three tiers with implementation examples, anti-patterns, orchestrator patterns. **Load when assessing tier or designing Tier 3 skills.**

### references/workflows.md
Workflow patterns: sequential orchestration, multi-MCP coordination, iterative refinement, context-aware tool selection. **Load when designing multi-step processes.**

### references/output-patterns.md
Patterns for consistent output: templates, examples, quality criteria. **Load when skill needs specific output formats.**

### references/reliability-patterns.md
Comprehensive reliability patterns: deterministic-first, validation-heavy, template-driven, error-aware. **Load when designing for production reliability.**

### references/quality-checklist.md
Pre-packaging validation checklist by tier. Includes testing methodology, quality gates. **Load before packaging.**

### references/predictable-skill-writing.md
Instruction quality layer for trigger precision, leading words, progressive disclosure, completion criteria, splitting, and pruning. **Load before drafting, restructuring, or compacting a skill.**

### references/trigger-optimization.md
Writing descriptions that trigger effectively. Keywords, use cases, action verbs, testing, automated pipeline. **Load when writing or improving descriptions.**

### references/eval-loop.md
Complete eval loop procedures: workspace organization, spawning runs, grading, benchmark aggregation, interactive viewer, improvement philosophy, blind comparison. **Load when running evals or iterating on skill quality.**

### references/schemas.md
JSON structures for evals.json, grading.json, benchmark.json, comparison.json, analysis.json, timing.json, metrics.json, history.json. **Load when generating or consuming eval data.**

### agents/grader.md
Instructions for the grader agent: evaluates assertions against outputs with evidence, critiques eval quality. **Load when grading test runs.**

### agents/comparator.md
Instructions for the blind comparator agent: judges two outputs without knowing which skill produced them. **Load for rigorous A/B comparison.**

### agents/analyzer.md
Instructions for the post-hoc analyzer: explains WHY the winner won and generates improvement suggestions. Also handles benchmark result analysis. **Load after blind comparison or benchmark aggregation.**

### scripts/
- `init_skill.py` - Initializes new skill directories with tier-appropriate templates
- `package_skill.py` - Validates and packages skills into .skill files
- `quick_validate.py` - Structure, frontmatter, and quality validation
- `run_eval.py` - Trigger evaluation for skill descriptions (Claude Code)
- `run_loop.py` - Full description optimization loop with train/test split (Claude Code)
- `improve_description.py` - Claude-powered description improvement (Claude Code)
- `aggregate_benchmark.py` - Aggregates grading results into benchmark statistics
- `generate_report.py` - Generates HTML report from optimization loop

### eval-viewer/
- `generate_review.py` - Serves interactive review page for eval results
- `viewer.html` - Template for the eval viewer interface

### assets/
- `eval_review.html` - Template for description optimization eval set review

---

Core loop for emphasis:

1. Figure out what the skill is about (discovery)
2. Assess tier and plan resources
3. Draft or edit the skill
4. Run test cases and evaluate outputs (eval loop with viewer)
5. Improve based on feedback
6. Repeat until satisfied
7. Optimize description for triggering
8. Package and distribute
