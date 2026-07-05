# Maya Changelog

Every prompt edit to Maya is logged here. Maya is Hindi-only (KKB spinoff). Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

---

## 2026-07-05 — Fix profile-handling bugs surfaced in testing
- **Feedback/bug:** On live calls: (1) `new_seeker`="yes" applied to a job without ever calling `create_profile` (no profile_id); (2) `new_seeker`="no" (returning caller) did not call `get_profile` at the start and jumped to recommendations; (3) age/gender were never asked. KKB Hindi did not show these. Root cause: Maya's pre-apply profile logic is textually near-identical to KKB, but Maya's heavier prompt (Caller Identity gate, college confirmation, HR line, Experience Capture, MML) causes the model to drop the profile steps; plus a latent contradiction in the "no" branch (header "caller already has a profile" vs body "MANDATORY IF PROFILE DOES NOT EXIST"). Age/gender are only optional `create_profile` payload fields — never explicitly asked.
- **Change (Maya Hindi only):**
  - "no" branch: reworded the mandatory line to remove the contradiction and make `get_profile` a hard gate — must fetch before presenting any jobs.
  - "yes" branch: added an explicit hard gate — since `get_profile` is skipped there is no `profile_id`, so `create_profile` MUST be called before `apply_job`.
  - Step 4 (Application): reinforced the same create_profile-before-apply gate at the point of action.
  - Experience Capture: added age (asked) and gender (inferred, or asked only if unclear), mapped to the `create_profile` `age`/`gender` fields.
- **Files:** `Maya/Maya Hindi.md`
- **Not done (flagged):** Maya still lacks KKB's `Post-Application Info Gathering` + `update_profile` sections (post-apply profile completion). Not one of the reported bugs; can be ported separately if desired.

## 2026-06-29 — Replicate new_seeker fork (ported from KKB)
- **Feedback/bug:** KKB added a `new_seeker` fork in the intro: when `new_seeker` is "yes", skip the (failing) `get_profile` call and gather details conversationally, doing only `create_profile` before application; when "no", fetch the profile via `get_profile`. Maya previously always attempted `get_profile`. Replicate the fork in Maya.
- **Change:** (1) Added the `${new_seeker}` input variable to Contact Variables. (2) Restructured "New contact — No old contact memory…" into `## Profile Handling after introduction (branch on new_seeker)` with the existing get_profile flow as the `"no"` path and a new `"yes"` path that skips `get_profile` and routes to Experience Capture. (3) Updated the Experience Capture trigger to also fire when `new_seeker` is "yes". Maya divergences (college identity, HR/MML, feminine voice, Experience Capture) preserved. Hindi only — Maya has no Kannada variant.
- **Files:** `Maya/Maya Hindi.md`
- **Ported from:** KKB

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap; Maya had no memory or output prompt.
- **Change:** Created `Maya Memory.md` (seeker memory + campus fields: `college_name`, `hr_contact_shared`, `mml_offered`, `mml_registered`) and `Maya Output.md` (KKB-style extraction + `college_confirmed`, `experience_captured`, `hr_contact_shared`, `benefits_mentioned`, `mml_offered`, `mml_registered`).
- **Files:** `Maya/Maya Memory.md`, `Maya/Maya Output.md`
