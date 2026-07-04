# KKB Changelog

Every prompt edit to KKB is logged here. Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

---

## 2026-06-29 — Reconcile Job Presentation drift (Hindi ↔ Kannada)
- **Feedback/bug:** The two language files had drifted: Kannada had a `## Pre-check (Before anything else)` step under Job Presentation Flow that Hindi lacked; Hindi had a second `# No-Match Fallback` section (after Step 4) that Kannada lacked. Decision: add both to both (additive, no deletions).
- **Change:** Added the `## Pre-check` block to KKB Hindi (verbatim agnostic logic). Added the second `# No-Match Fallback` to KKB Kannada (agnostic trigger/close logic copied; used the existing Kannada fallback message). Both files now contain both sections.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`

## 2026-06-29 — Add company name to job presentation
- **Feedback/bug:** When presenting job options, the agent did not name the company. This behavior existed in Maya but in neither KKB language.
- **Change:** Ported the company-name feature from Maya. Step 2 spoken format now reads `[role], [company], [location], सैलरी/ಸ್ಯಾಲರಿ [salary]` for 1/2/3-job cases; Step 3 deep-dive now names the company; added a Step 2 rule to speak `[company]` where present and skip silently if missing/"Not Available". Applied to Hindi (source) and mirrored to Kannada. Maya's neighboring `benefits`/`hr_contact` lines were intentionally NOT ported — KKB's `${recommendations}` has no such fields. `${recommendations}` already includes `company`, so no schema change was needed.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`
- **Ported from:** Maya

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap; KKB had no memory prompt.
- **Change:** Created `KKB Memory.md` (language-agnostic seeker memory, English output), modeled on `DKB Memory.md` and re-domained to the seeker/job-search context. Backs the conversation prompt's "Introduction Priority Rule" via `last_action` / `last_options_presented` / `jobs_applied`.
- **Files:** `KKB/KKB Memory.md`
