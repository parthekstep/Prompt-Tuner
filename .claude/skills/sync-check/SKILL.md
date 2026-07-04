---
name: sync-check
description: Audit whether an agent's Hindi and Kannada conversation prompts have drifted out of sync — detect when one language is "a version ahead" of the other on language-agnostic logic, separate real drift from expected language differences, and reconcile. Use when the user wants to check multilingual prompt parity, before making a prompt change, or whenever asked to verify the prompts are in sync. Runs automatically as the first step of /update-prompt.
---

# Sync Check

Detect and reconcile drift between an agent's language variants. "Drift" = a
**language-agnostic** section that differs between Hindi and Kannada because a change
landed in one language but not the other. Expected language differences (different script,
spoken lines, number-words) are **not** drift.

Applies to **KKB** and **DKB** (both have Hindi + Kannada). **Maya is Hindi-only — nothing
to sync; report and stop.**

## Inputs

- Target agent: `KKB`, `DKB`, or `all` (default `all` if unspecified).
- Resolve files via the path map in the repo root `CLAUDE.md`.

## Reference

Read `.claude/skills/update-prompt/reference/prompt-anatomy.md` for the section taxonomy and
the AGNOSTIC / SPECIFIC / MIXED tags. Drift is only possible in AGNOSTIC content and in the
AGNOSTIC portions of MIXED sections.

## Procedure

1. **Load both files** for the agent (Hindi and Kannada) and extract their section heading
   lists (`^#{1,3} ` lines). Note any heading present in one file but missing in the other —
   a missing whole section is the strongest drift signal.
2. **Walk the taxonomy section by section.** For each section, compare the two files:
   - **AGNOSTIC section** → the text should be effectively identical (modulo the script of
     inline English words). Any difference in logic, conditions, variable names, tool
     payloads, ordering, or added/removed rules = **agnostic drift**.
   - **MIXED section** → compare only the rule/logic parts. A new or changed *rule* on one
     side that is absent on the other = drift. A different *spoken line* is expected, not drift.
   - **SPECIFIC section** → differences are expected. Only flag if a section is entirely
     missing on one side, or if a structural sub-point (e.g. a new TTS category) exists on
     one side only.
3. **Use the changelogs as evidence.** Read `<Agent>/CHANGELOG.md`. An entry describing a
   change whose content you find in only one language file confirms which side is ahead.
4. **Report a drift table:**

   | Section | Status | Ahead | Missing from laggard |
   |---|---|---|---|
   | … | in sync / **AGNOSTIC DRIFT** / expected diff | Hindi/Kannada/— | short description |

   Summarize: N sections in sync, M drifted, which language is generally ahead.
5. **Offer to reconcile.** For each drifted section, propose bringing the laggard up to date:
   copy the AGNOSTIC content verbatim; for the AGNOSTIC part of a MIXED section, insert the
   rule and adapt any accompanying spoken line to the laggard's language per the localization
   conventions in `prompt-anatomy.md`. Ask before writing unless the caller (e.g.
   `/update-prompt`) has already authorized reconciliation.
6. **After reconciling,** append a `CHANGELOG.md` entry noting the sync (what was brought
   into alignment, which direction).

## When invoked from /update-prompt

Run steps 1–4 silently-but-reported, then:
- If **no drift**, say so and let the change proceed.
- If **drift found**, surface the table and reconcile the affected sections first (so the new
  change lands on an aligned base), then continue. Do not silently overwrite — show what you
  aligned.

## Notes

- **Surgical edits only.** When reconciling, change only the drifted content; touch nothing
  else. Bring the laggard up with the smallest edit, preserving all other lines exactly. Prefer
  additive changes; never reformat or delete unrelated content. See `CLAUDE.md` → "Surgical edits only".
- Never "fix" an expected language difference by making Kannada match Hindi's script — that
  would be a regression.
- If you cannot tell whether a difference is a deliberate language choice or true drift, flag
  it as **uncertain** and ask the user rather than guessing.
