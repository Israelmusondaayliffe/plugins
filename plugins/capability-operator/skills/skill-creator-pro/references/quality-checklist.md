# Quality Checklist

Pre-packaging validation by tier. Includes testing methodology, quality gates, and common issues.

## Tier-Specific Quality Gates

### Tier 1 Quality Gates

- [ ] SKILL.md is clear and concise (under 300 lines ideal)
- [ ] Instructions use imperative form
- [ ] Examples show realistic input/output pairs
- [ ] References provide domain knowledge Claude doesn't have natively
- [ ] No unnecessary scripts (Tier 1 should rarely need them)
- [ ] Description triggers on relevant queries
- [ ] Works alongside other skills without conflict

### Tier 2 Quality Gates

Everything from Tier 1, plus:

- [ ] Accuracy-critical operations use scripts (not LLM generation)
- [ ] Scripts tested with happy path, edge cases, and error cases
- [ ] Scripts include error handling and meaningful error messages
- [ ] Templates in assets/ for consistent output format
- [ ] Validation at critical checkpoints
- [ ] Clear documentation of what's deterministic vs probabilistic
- [ ] References hold detailed docs, not SKILL.md (no duplication)
- [ ] Error recovery documented

### Tier 3 Quality Gates

Everything from Tier 2, plus:

- [ ] SKILL.md functions as orchestrator/router (not worker)
- [ ] Router logic covers all expected request types
- [ ] Fallback for ambiguous requests (asks user for clarification)
- [ ] Each sub-agent lives in agents/ (not references/)
- [ ] Each sub-agent has clear scope, inputs, outputs, and validation
- [ ] Sub-agents don't overlap in scope
- [ ] Handoff validation between phases (previous phase output verified)
- [ ] Shared knowledge in references/ is distinct from behavioral agents in agents/
- [ ] Shared resources clearly identified and accessible to all phases
- [ ] Multi-MCP coordination tested across service boundaries
- [ ] Phase dependencies documented

---

## Testing Methodology

### 1. Triggering Tests

Create 10+ realistic test queries:

**Should-trigger queries (5-7):**
- Direct requests matching skill purpose
- Paraphrased requests using different words
- Casual/informal versions of the same request
- Edge cases where skill should activate but phrasing is unusual

**Should-not-trigger queries (5-7):**
- Near-misses sharing keywords but needing different skills
- Adjacent domain requests
- Queries that naive keyword matching would catch but shouldn't

**Quality bar:** Queries must be realistic. Include file paths, personal context, casual speech, abbreviations. Not abstract requests.

Bad: "Format this data"
Good: "I have a CSV in downloads called q4-revenue.csv, need to add a profit margin column. Revenue is column C, costs column D."

### 2. Functional Tests

For each use case from discovery:

```
Test: [Descriptive name]
Given: [Specific inputs]
When: Skill executes workflow
Then:
  - [Expected output 1]
  - [Expected output 2]
  - [Validation passes]
  - [No errors]
```

**Tier-specific functional tests:**

**Tier 1:** Test that instructions produce expected output format. Test with varied inputs to check generalization.

**Tier 2:** Test script outputs with known inputs (deterministic verification). Test validation catches bad input. Test error handling with intentionally broken inputs. Test template compliance.

**Tier 3:** Test routing logic with each request type. Test phase handoffs with valid and invalid inputs. Test that orchestrator refuses to proceed when prerequisites missing. Test each sub-agent independently.

### 3. Performance Comparison

Compare with-skill vs without-skill:

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| User instructions needed | Repeated each time | Embedded |
| Back-and-forth messages | Many | Minimal clarification |
| Failed operations | Common | Rare/zero |
| Output consistency | Variable | Consistent |

### Success Criteria

**Quantitative:**
- Triggers on 90%+ of relevant queries
- Completes workflow in target tool calls
- Zero failed operations per workflow run

**Qualitative:**
- Users don't need to prompt Claude about next steps
- Workflows complete without user correction
- Consistent results across sessions
- New user succeeds on first try

---

## Architecture Validation

### 1. Architecture Decisions

- [ ] Identified accuracy-critical operations
- [ ] Scripts handle deterministic operations
- [ ] Templates handle consistent formatting
- [ ] Documented reliability approach in SKILL.md

**Red flags:**
- LLM performing calculations instead of scripts
- Format consistency without templates
- No mention of accuracy considerations

### 2. Edge Case Handling

- [ ] Discovery surfaced edge cases
- [ ] Edge cases documented in SKILL.md or references
- [ ] Scripts handle edge case inputs
- [ ] Validation catches edge case failures

**Red flags:**
- Generic "handles various inputs" without specifics
- No unusual cases mentioned
- Scripts not tested with edge cases

### 3. Validation and Error Handling

- [ ] Validation at critical checkpoints
- [ ] Clear pass/fail criteria
- [ ] Error handling in all scripts
- [ ] Recovery documented in SKILL.md

**Red flags:**
- No validation steps
- Errors surface late in workflow
- No recovery guidance

---

## Metadata Validation

### Frontmatter

- [ ] Name uses kebab-case (lowercase, hyphens only)
- [ ] Name is descriptive (not generic like "helper")
- [ ] Name matches folder name exactly
- [ ] Description explains WHAT and WHEN
- [ ] Description includes key terms users will say
- [ ] Description under 1024 characters
- [ ] No angle brackets in description
- [ ] Only allowed frontmatter keys used

### SKILL.md Content

- [ ] Overview clear (2-3 sentences)
- [ ] Triggers and scenarios specified
- [ ] Resources referenced with explicit load instructions
- [ ] Reliability approach documented
- [ ] Writing style: imperative form throughout
- [ ] No TODO placeholders remain
- [ ] Under 500 lines (content moved to references if longer)
- [ ] Completion names an observable artifact or state plus its proof surface
- [ ] Leading words make the workflow scannable
- [ ] Every rule maps to a behavior case or documented boundary

### Scripts (if present)

- [ ] All scripts executable (`chmod +x`)
- [ ] All scripts tested: happy path, edge cases, error cases
- [ ] Docstrings explain purpose
- [ ] Error handling with meaningful messages
- [ ] Referenced in SKILL.md with when-to-run guidance

### References (if present)

- [ ] Each file has specific purpose
- [ ] Referenced in SKILL.md with when-to-load guidance
- [ ] No duplication with SKILL.md content
- [ ] Table of contents if over 100 lines

### Assets (if present)

- [ ] Actually used in skill workflow (not just placeholders)
- [ ] File formats correct and tested
- [ ] Referenced in SKILL.md with location

### No Unnecessary Files

- [ ] No README.md inside skill folder
- [ ] No placeholder files from init script
- [ ] No test files included in package
- [ ] Every file has clear purpose
- [ ] No obsolete aliases, setup shims, or historical source layout remain

---

## Iteration Signals

After initial deployment, watch for:

**Undertriggering:** Skill doesn't load when it should.
Fix: Add more keywords, trigger phrases, file types to description.

**Overtriggering:** Skill loads for irrelevant queries.
Fix: Add specificity. Consider negative triggers: "Do NOT use for [adjacent task]."

**Instructions not followed:** Claude ignores or misinterprets guidance.
Fix: Put critical instructions at top. Explain WHY, not just WHAT. Use examples over rules. For critical validations, use scripts instead of prose.

**Output inconsistent:** Results vary across uses.
Fix: Add templates in assets/. Add validation scripts. Add examples showing expected output.

**Repeated code:** Each run independently writes similar helper scripts.
Fix: Bundle the common script in scripts/.

**SKILL.md too long:** Approaching or exceeding 500 lines.
Fix: Move detailed content to references/. Keep SKILL.md as orchestrator with pointers.

---

## Quick Validation

Run before packaging:

```bash
python scripts/quick_validate.py <path/to/skill>
```

Checks: frontmatter format, naming conventions, file structure, description length.

---

## Reliability Tiers (Quality Bar)

**Functional (minimum):** Covers happy path. Basic structure correct. Passes quick_validate.

**Reliable (target for most skills):** Handles edge cases. Scripts for accuracy-critical ops. Validation present. Error handling. Tested thoroughly.

**Production-Grade (high-stakes use):** Comprehensive error handling. Multiple validation points. Fallback mechanisms. Recovery procedures documented. Failure scenarios tested.

**Match quality bar to stakes.** Personal scripts: Functional acceptable. Team tools: Reliable required. Production systems: Production-Grade required.
