# Voice Extraction Guide

Systematic approach to identifying and preserving user voice markers before applying quality techniques.

## Core Principle

Voice preservation is not optional polish. It's infrastructure. Extract voice BEFORE fixing anything.

## Voice Marker Categories

### 1. Sentence Patterns

**Short and punchy:**
- Fragments used deliberately
- One idea per sentence
- Periods instead of semicolons

**Flowing and connected:**
- Longer compound sentences
- Transitional phrases
- Layered ideas

**Varied rhythm:**
- Mix of short and long
- Strategic fragments for emphasis
- Pacing through structure

**Detection method:** Count words per sentence. <10 average = punchy. >20 average = flowing.

### 2. Tone Markers

**Formal:**
- Complete sentences always
- No contractions
- Third person or passive voice
- Technical vocabulary

**Conversational:**
- Contractions common
- First/second person
- Questions to reader
- Colloquial phrases

**Direct:**
- Imperative verbs
- Clear stance
- Minimal hedging
- "Do X" not "You might consider X"

**Curious:**
- Questions embedded
- "I wonder" / "I noticed"
- Exploration language
- Uncertainty acknowledged

**Detection method:** Look for pronouns, contractions, question marks, hedge words.

### 3. Characteristic Phrases

**PRESERVE THESE EXACTLY** even if they trigger AI-tell detectors.

**Types to watch for:**
- Signature transitions: "Here's the thing," "The real insight is"
- Personal markers: "In my experience," "What I've found"
- Domain vocabulary: Technical terms the user prefers
- Emotional markers: How they express enthusiasm, doubt, conviction

**Detection method:** Look for repeated phrases across content. Ask: "Does this feel like a signature?"

### 4. Structure Preferences

**Prose-dominant:**
- Paragraphs flow into each other
- Headers rare or absent
- Ideas connected narratively

**List-dominant:**
- Bullets for key points
- Numbered steps for processes
- Headers for navigation

**Hybrid:**
- Prose for explanation
- Lists for actions/options
- Headers for major sections

**Detection method:** Count bullets vs. paragraphs. Note header frequency.

### 5. Emphasis Patterns

**Bold for emphasis:**
- Key terms bolded
- Important phrases highlighted

**Capitalization for emphasis:**
- ALL CAPS for strong points
- Title Case for terms

**Structural emphasis:**
- Short paragraphs for key points
- Line breaks for impact
- Repetition for reinforcement

**Detection method:** Look for formatting patterns. What does the user emphasize and how?

## Voice Extraction Workflow

### Step 1: Initial Scan

Read content once without editing. Note gut impressions:
- Does this feel formal or casual?
- Is it punchy or flowing?
- What words/phrases stand out?

### Step 2: Pattern Identification

**Count these:**
- Average sentence length
- Contraction frequency
- Question frequency
- Hedge word frequency
- Bullet vs. prose ratio

**List these:**
- Characteristic phrases (3-5 minimum)
- Banned patterns (from user preferences)
- Domain-specific vocabulary

### Step 3: Voice Profile Creation

Fill out template:

```
VOICE PROFILE
============
Tone: [formal / conversational / direct / curious / technical]
Sentence style: [short-punchy / flowing / varied]
Structure: [prose / lists / hybrid]

PRESERVE:
- [characteristic phrase 1]
- [characteristic phrase 2]
- [specific vocabulary terms]

BANNED:
- [em-dashes]
- [specific AI tells from user preferences]
- [patterns user dislikes]

EMPHASIS METHOD: [bold / caps / structural]

CONFIDENCE: [high / medium / low]
```

### Step 4: Profile Validation

Ask yourself:
- Would the user recognize content written in this profile as theirs?
- Am I capturing what's distinctive, not just what's present?
- Have I missed any signature patterns?

## Known User Profiles

### Example Profile (Pre-Built)

```
VOICE PROFILE: EXAMPLE WRITER
========================
Tone: Curious, practical, collaborative, direct without warmth loss
Sentence style: Short and punchy, fragments for emphasis
Structure: Hybrid - prose for explanation, structured for frameworks

PRESERVE:
- "Here's the thing"
- "I tested" / "I found" / "I built"
- Questions embedded in exploration
- Showing uncertainty when present
- Process visibility (show work, not just results)

BANNED:
- Em-dashes (—) → always replace
- AI clichés: delve, leverage, unlock, journey, game-changer
- Business jargon: synergy, scalable, robust, disruptive
- Hedge language: kind of, sort of, probably, maybe
- Generic transitions: however, moreover, furthermore

EMPHASIS METHOD: Structural (short paragraphs, line breaks)

CONFIDENCE: High (extensive sample data)
```

### Generic Professional Profile

```
VOICE PROFILE: GENERIC PROFESSIONAL
===================================
Tone: Clear, competent, appropriately formal
Sentence style: Medium length, complete thoughts
Structure: Headers for navigation, prose for content

PRESERVE:
- Industry-standard terminology
- Complete sentences
- Logical flow

BANNED:
- Em-dashes
- AI clichés
- Excessive hedging

EMPHASIS METHOD: Bold for key terms

CONFIDENCE: Low (default when no user data)
```

## Edge Cases

### Empty Voice Profile

**Situation:** Content too short or generic to extract patterns.

**Response:**
1. Check user memory for stored preferences
2. Apply generic professional profile
3. Use light-touch editing only
4. Flag: "I couldn't detect a strong voice pattern. I've applied minimal changes."

### Conflicting Signals

**Situation:** Content shows mixed patterns (e.g., formal tone but casual phrases).

**Response:**
1. Note the conflict explicitly
2. Ask user: "I see both formal and casual elements. Which should I preserve?"
3. If no response available, preserve both and minimize changes

### Voice vs. Quality Conflict

**Situation:** User's characteristic phrase triggers AI-tell detector.

**Response:**
1. Voice wins
2. Preserve the phrase
3. Note in output: "Preserved '[phrase]' as it matches your voice"
4. Accept slightly lower technical score

## Integration with Quality Techniques

### Before Negative Style Check
- Load voice profile
- Mark characteristic phrases as protected
- Only flag AI tells that aren't voice markers

### Before Cliché Scrubbing
- Exclude user's domain vocabulary
- Preserve signature transitions
- Only replace patterns that feel generic, not distinctive

### Before Divergence Enforcement
- Preserve exploration language if user voice is "curious"
- Force decisions only on conclusions, not exploration
- Match directness level to voice profile

### After All Techniques
- Compare output to voice profile
- Verify protected phrases intact
- Roll back any changes that broke voice consistency

## Testing Voice Preservation

**Quick test:** Read improved output aloud. Ask:
- Does this sound like the same person?
- Did I remove what's distinctive?
- Would the user recognize this as their writing?

**Detailed test:**
- [ ] Characteristic phrases preserved
- [ ] Tone matches profile
- [ ] Sentence rhythm preserved
- [ ] Structure preferences followed
- [ ] No banned patterns introduced

If any fail → revise with voice profile in focus.

## Remember

**Voice extraction is Phase 2 for a reason.** It comes before technique application because techniques should serve voice, not override it.

**The goal is not generic quality.** It's the user's quality. Their voice, but at their best.
