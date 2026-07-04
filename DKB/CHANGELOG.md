# DKB Changelog

Every prompt edit to DKB is logged here. Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

---

## 2026-06-29 — Full reconciliation: DKB Hindi brought up to Kannada
- **Feedback/bug:** A sync-check found DKB Kannada was a newer, stricter version than DKB Hindi (behavioral drift, not cosmetic). Kannada is the source of truth here. Bring Hindi up to parity (agnostic logic only; all Hindi spoken lines preserved).
- **Change (behavioral / bug fixes ported Kannada → Hindi):**
  - **Bug:** fixed the malformed `${phone(number}` → `${phoneNumber}` in all three tool payloads (update_job_status, update_job_details, create_job).
  - **Bug:** removed the redundant Phase 1 trailing block that used `status=active`/`status=closed` (the real values are `"open"`/`"closed"`) and had a typo ("thel"). Removed the duplicate Phase Entry "NO — no jobs present" bullet.
  - Added the global "Tool calls are silent and internal" CRITICAL note and per-phase `INTERNAL NOTE` headers (Phases 1–3).
  - Reframed Phase 1 owner-responses with `[INTERNAL: …]` discipline + CRITICAL ("call update_job_status for every job before proceeding").
  - Phase 2: added the `${city}` already-known rule (never re-ask the city of an existing job), per-answer internal `update_job_details` discipline, and fixed the payload field name `work_experience_years` → `workExperienceYears` in prose.
  - Phase 3 Step 3b: replaced the bullet rules with Kannada's mandatory numbered internal tool-call sequence + CRITICAL ("never call create_job before consent; never skip get_talent_insights").
  - Tool Usage Rules: tightened the "When to call" entries for get_talent_insights / update_job_status / update_job_details / create_job ("never announce", consent guards); "queries" → "parameters".
- **Deliberately NOT changed (per fragility constraint):** Hindi spoken lines; region-appropriate example values (Ghaziabad/UP vs Kannada's Dharwad/Karnataka); language-specific rules ("plain spoken Hindi", Devanagari script rules); Hindi's slightly richer graceful-exit guidance. Residual differences are cosmetic (backticks, line-wrapping) or correct language differences — behavior is now in parity.
- **Files:** `DKB/DKB Hindi.md`

## 2026-06-29 — Add memory injection block
- **Feedback/bug:** Memory is enabled for DKB (memory prompt exists), but the conversation prompts were missing the required `### Contact context` injection block.
- **Change:** Added the exact language-agnostic block (`### Contact context` / `Here is the caller context:` / `{${contact_memory}}`) at the end of the Input Variables section in both language files. KKB and Maya already had it.
- **Files:** `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap.
- **Change:** No prompt changes. DKB already has the complete set (Hindi, Kannada, Memory, Output) and serves as the reference implementation for the new skills' anatomy docs.
- **Files:** none
