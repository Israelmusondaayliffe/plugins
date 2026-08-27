# Context profiles and tolerance matrix

Six profiles. Auto-detect from content cues, or user overrides by naming a profile.

---

## Auto-detection cues

| Signal | Inferred profile |
|---|---|
| Under 300 words + hashtags or @ mentions | `linkedin` |
| Code blocks, API references, technical architecture terminology | `technical-blog` |
| Salutation + investor/fundraising language | `investor-email` |
| Step-by-step instructions, parameter docs, README structure | `docs` |
| Short + casual + conversational (Slack, DM, quick note) | `casual` |
| No strong signals | `blog` (safest default, all rules at full strength) |

If auto-detection feels wrong, state which profile you're using and why.

---

## Profile definitions

**`linkedin`**: Short-form social. Punchy fragments work. Visual formatting (single-line paragraphs) is expected. 1-2 emoji at end of a line are acceptable. Hooks matter.

**`blog`**: Default. Standard long-form prose. All rules at full strength.

**`technical-blog`**: Long-form with code, architecture, APIs. Technical terms get a pass. Tone rules still apply. Some hedging ("may," "can") is accurate precision, not AI-ism.

**`investor-email`**: High-trust audience. Tighten everything. Promotional language is the biggest risk. Extra strict on significance inflation. Zero vague attributions.

**`docs`**: Documentation, READMEs, guides. Clarity over voice. Lists are appropriate. Voice recovery is minimal.

**`casual`**: Slack messages, internal notes, quick replies. P0 only. Don't over-police.

---

## Tolerance matrix

Rules not listed apply at full strength across all profiles. "Skip" means don't audit that category. "Relaxed" means flag only clear violations, not borderline cases. "Extra strict" means flag even borderline instances.

| Rule | linkedin | blog | technical-blog | investor-email | docs | casual |
|---|---|---|---|---|---|---|
| Authored em dashes in editable prose | zero | zero | zero | zero | zero | zero |
| Bold overuse | relaxed (bold hooks OK) | strict | strict | strict | relaxed | skip |
| Emoji in headers | relaxed (1-2 end-of-line OK) | strict | strict | strict | skip | skip |
| Excessive bullets | skip (lists work on LinkedIn) | strict | relaxed (technical lists OK) | strict | skip | skip |
| Hedging | strict | strict | relaxed ("may" is accurate in technical) | strict | relaxed | skip |
| Word replacement table | strict | strict | partial (see below) | strict | relaxed | P0 only |
| Promotional language | relaxed (some sell expected) | strict | strict | extra strict | strict | skip |
| Significance inflation | strict | strict | strict | extra strict | relaxed | skip |
| Copula avoidance | skip | strict | relaxed | strict | skip | skip |
| Uniform paragraph length | skip (short-form) | strict | strict | strict | relaxed | skip |
| Numbered list inflation | relaxed | strict | relaxed | strict | skip | skip |
| Rhetorical questions | relaxed (1 as hook OK) | strict | strict | strict | strict | skip |
| Transition phrases | skip (short-form) | strict | strict | strict | relaxed | skip |
| Generic conclusions | skip | strict | strict | extra strict | skip | skip |
| Preserve voice texture | high | high | medium | medium | low | none |

---

## Technical-blog word table exceptions

These terms have legitimate technical meaning and should NOT be flagged in technical content:

- `robust`: acceptable when describing system properties
- `comprehensive`: acceptable for API or feature coverage
- `seamless`: acceptable for integration descriptions
- `ecosystem`: acceptable for describing dev toolchains
- `leverage`: acceptable when discussing actual platform leverage or API features
- `facilitate`: acceptable for technical workflow descriptions
- `underpin`: acceptable for architectural descriptions
- `streamline`: acceptable for pipeline descriptions

Still flag even in technical content: `delve`, `tapestry`, `beacon`, `embark`, `testament to`, `game-changer`, `harness`.

---

## Investor-email notes

"Extra strict" means: flag even borderline instances. In investor emails, a single "thriving ecosystem" can undermine the whole message. Specific numbers, named customers, and real metrics always beat adjectives here. If a sentence doesn't contain a fact, it should probably be cut.
