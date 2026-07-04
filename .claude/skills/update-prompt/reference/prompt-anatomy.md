# Conversation Prompt Anatomy

The canonical section taxonomy for the conversation prompts, distilled from the existing
KKB, DKB, and Maya files. Every section is tagged so a change can be classified and synced
correctly. This file is shared by `/update-prompt` and `/sync-check`.

## Tags

- **AGNOSTIC** — copy verbatim across languages. Logic, structure, variable names, tool rules.
- **SPECIFIC** — translate/adapt per language. Spoken text, scripts, examples, number-words.
- **MIXED** — section contains both. The logic/rules are AGNOSTIC; the spoken lines and
  examples inside it are SPECIFIC. Split the change accordingly.

## How to classify any edit

Ask: *"If this exact text appeared in the other language's file unchanged, would it be
correct?"*
- Yes → AGNOSTIC (copy verbatim).
- No, it must be in the other script/idiom → SPECIFIC (translate & adapt).
- Partly → MIXED (copy the rule, adapt the quoted speech).

A reliable tell: text inside spoken-line quotes, TTS number spellings, script names, tone
markers, and sample dialogue is almost always SPECIFIC. Conditions ("if X is Not
Available…"), variable names (`${job_id}`), tool payloads, phase ordering, and safety
checklists are almost always AGNOSTIC.

## Section taxonomy (union across KKB / DKB / Maya)

Section headings differ slightly per agent; match by intent, not exact string.

| Section | Tag | Notes |
|---|---|---|
| Introduction | MIXED | Persona name (काम की बात / ಕೆಲಸದ ಮಾತು / धंधे की बात) is SPECIFIC; core principles AGNOSTIC. |
| Core Role | AGNOSTIC | |
| Input Variables (+ Recommendations/Job variables) | AGNOSTIC | Variable names & presence rules. Never localize `${...}` names. |
| Hallucination Guard | AGNOSTIC | |
| No-Match Fallback | MIXED | Trigger logic AGNOSTIC; the spoken fallback message SPECIFIC. |
| User Universe / personas | AGNOSTIC | Descriptive; keep identical meaning across languages. |
| Conversation Principle | AGNOSTIC | |
| Call Introduction Rules / Priority / Decision | MIXED | Decision logic AGNOSTIC; the opening scripts SPECIFIC. |
| Profile Handling (branch on `new_seeker`) | AGNOSTIC | |
| Job Presentation Flow — Steps 1–4 | MIXED | Step rules AGNOSTIC; the "Spoken format" blocks SPECIFIC. |
| Language and Script Rules | SPECIFIC | Defines the script itself (Devanagari vs Kannada). |
| TTS Normalization Rules | SPECIFIC | Number/money/time-to-word spellings differ by language; the categories are AGNOSTIC. |
| Speech Recognition & Phonetic Confirmation | MIXED | Core rule AGNOSTIC; number-normalization variants & confirmation examples SPECIFIC. |
| Style Rules | MIXED | Principle AGNOSTIC; the example markers (अभी / ಈಗ) SPECIFIC. |
| Prohibited Language | MIXED | Rule AGNOSTIC; the listed banned phrases SPECIFIC (culturally adapted). |
| Conversation State Model | AGNOSTIC | |
| What You Must Always Preserve | AGNOSTIC | |
| Trade-off Rule | AGNOSTIC | |
| Action and Consent Rule | AGNOSTIC | |
| Tool Call Rules (per tool) + payloads | AGNOSTIC | Tool names, JSON payloads, fixed params (e.g. `sourceService: ONESTAGENT`) NEVER change. |
| Apply / Job-action Success & Failure Handling | MIXED | Logic AGNOSTIC; the spoken success/failure messages SPECIFIC. |
| Post-Application handling | MIXED | |
| Silence Handling | AGNOSTIC | (Any spoken bridge line inside is SPECIFIC.) |
| Emotional Handling | MIXED | Allowed/banned phrase lists SPECIFIC; the rule AGNOSTIC. |
| Special Journey Patterns | MIXED | Pattern logic AGNOSTIC; example lines SPECIFIC. |
| Tool Call General Instructions | AGNOSTIC | |
| Graceful Exit | MIXED | Close logic AGNOSTIC; the final words ("Goodbye"/नमस्ते) SPECIFIC. |
| Dignity Safety Check | AGNOSTIC | |
| Sample Conversational Patterns | SPECIFIC | Whole dialogues; also localize place/person names (Pune↔Bengaluru, रमेश↔ರಮೇಶ್). |

### DKB-only sections

| Section | Tag | Notes |
|---|---|---|
| Introduction After "Hello" — Turns 1–3 | MIXED | Turn logic AGNOSTIC; the spoken turn lines SPECIFIC. |
| Phase Entry Rule | AGNOSTIC | job_role presence routing. |
| Conversation Flow — Phase 1 Freshness / Phase 2 Completeness / Phase 3 New Job | MIXED | Phase logic AGNOSTIC; spoken examples SPECIFIC. |
| Tool Usage Rules — get_talent_insights / update_job_status / update_job_details / create_job | AGNOSTIC | Incl. payloads & fixed params. |
| Market Truth Delivery | MIXED | Data logic AGNOSTIC; phrasing SPECIFIC. |
| Error and Uncertainty Handling | MIXED | |

### Maya-only sections (divergences — never overwritten by a KKB sync)

| Section | Tag | Notes |
|---|---|---|
| Caller Identity (Strict) | MIXED | Campus identity logic; spoken intro SPECIFIC (Hindi only). |
| HR-number value line | MIXED | |
| Experience Capture | MIXED | |
| Voice gender (always feminine) | SPECIFIC | Hindi feminine verb forms (कर रही हूँ, not कर रहा हूँ). |
| HR number sharing (post-apply) | MIXED | |
| Marketing Masters League | MIXED | |

## Localization conventions (Hindi → Kannada)

When adapting a SPECIFIC change to Kannada:
- **Script:** Kannada script only; no Roman Kannada. English-origin words in Kannada script (ಜಾಬ್, ಮಾರ್ಕೆಟ್).
- **Register:** "Kanglish" — Kannada mixed naturally with commonly-used English words.
- **Numbers/money/time:** spell as Kannada words (ಎರಡರಿಂದ ಮೂರು; ಹದಿನೆಂಟು ಸಾವಿರ; ಬೆಳಗ್ಗೆ/ಮಧ್ಯಾಹ್ನ/ಸಂಜೆ/ರಾತ್ರಿ — never AM/PM).
- **Tone markers:** ಈಗ / ಸುಮಾರು / ಸಾಮಾನ್ಯವಾಗಿ rather than अभी / लगभग / आमतौर पर.
- **Places & names:** use the Kannada-region equivalents already used in the Kannada file (Bengaluru, Mysuru, Dharwad).
- **Match existing style:** read the surrounding Kannada section first and mirror its phrasing conventions rather than translating word-for-word.
