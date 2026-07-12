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

## 2026-07-13 — Real fix for the new_seeker branch: variable-interpolation order
- **Feedback/bug:** Even after the branch restructure below, `new_seeker="no"` (confirmed lowercase in input args) STILL ran the new-user path — asked about experience instead of fetching the profile, then called `create_profile`. The actual root cause (found by Parth): the binding line read `Consider ${new_seeker} as new_seeker`, which interpolates at runtime to **"Consider no as new_seeker"** — the value is placed where the label should be, so `new_seeker = no` never binds and the branch has no value to switch on. This is why case-normalization, Step-0 removal, section deletion, and hard gates all failed — none touched the garbled binding.
- **Change:** flipped the order to `Consider new_seeker as ${new_seeker}` (→ "Consider new_seeker as no"), which binds the value cleanly. (Parth fixed this in production; synced into the repo here.) Catalogued as prompt-analyser **G1** (variable placeholder before its label garbles after interpolation).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (added G1; corrected the A1 2026-07-13 note).
- **Flag:** KKB has the same backwards binding (`Consider ${new_seeker} as new_seeker`, Hindi + Kannada, lines ~64 and ~197) — latent, not yet flipped.

## 2026-07-13 — Batch fix: branch structure, apply hallucination, phone +91, job order, age/gender, intro
- **Feedback/bug:** Live transcripts (both `new_seeker="No"` and `"Yes"`) behaved identically — greeting → Experience Capture → `create_profile` → spoken "अप्लाई हो गया" with **no `apply_job` call**. Plus: apply bridge repeated 2–3×; jobs announced ("interested?") before being listed and without details; age/gender re-asked when already known; over-formal intro ("अवसरों"); and `get_profile` empty for ~14/80 (phone passed without `+91`). User confirmed lowercase `"no"` still failed → case was NOT the cause; pointed to KKB where the same branch works.
- **Root cause:** Maya diverged from KKB's clean single-branch structure by adding a redundant `Step 0` and a **standalone `## Experience Capture` section** that the model jumped to after the greeting — hijacking the `new_seeker` branch for both values. (KKB has neither; its `"yes"` path gathers inline.)
- **Change (Maya Hindi):**
  - **Branch (master):** deleted `Step 0`; deleted the standalone `Experience Capture` section; folded role/experience gathering **inline** into the Profile-Handling `"yes"`/`"no"` paths, mirroring KKB. Added a case-insensitive + empty-defaults-to-"no" clause. Updated dangling references (get_profile rules, create_profile).
  - **Apply hallucination:** success line may be spoken ONLY after `apply_job` actually returned success; `apply_job` must fire every time (Apply Success Handling + apply_job rules + Step 4).
  - **Phone:** `get_profile`/`create_profile` now prepend `+91` (both write and lookup), with a phone-format rule; updated the create_profile example to `+91…`.
  - **Age/gender:** Pre-Apply now uses the fetched profile — asks only genuinely missing fields (no re-ask for `new_seeker="no"`).
  - **Job order:** Step 1 is now a lead-in + area question (no premature interest question); Step 2 lists with details, then asks interest. Updated Example 1 to match.
  - **Intro:** "अवसरों" → "जॉब्स" (greeting + Example 1).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (sharpened A1, C3; added A5, A6, C5).
- **Guidance followed:** mirrored KKB Placeholder Hindi (the working reference). Maya divergences (college identity, HR line, benefits, feminine voice, MML) preserved.

## 2026-07-08 — Hard-gate Experience Capture for new_seeker="no"
- **Feedback/bug:** Even with `new_seeker="no"` confirmed passed, the agent skipped the profile-permission/`get_profile` step and went straight to Experience Capture (the "yes" path) right after the greeting. Prior reinforcement told the model what to DO on the "no" path but never forbade the competing action (Experience Capture), so Experience Capture kept winning.
- **Change:** Added a hard gate at the top of Experience Capture — when `new_seeker="no"`, it may NOT run as the first post-greeting action; it can run in the "no" path only after `get_profile` has been called and returned nothing/sparse. This leaves profile-permission → `get_profile` as the only valid first action for "no". Surgical, one section.
- **Files:** `Maya/Maya Hindi.md`

## 2026-07-08 — Sync to production prompt + fix apply-time tool path
- **Feedback/bug:** From live transcripts: (1) the new_seeker fork wasn't honored end-to-end — a new seeker's apply called `get_profile` (which returns nothing for a brand-new number) instead of `create_profile`, so `apply_job` fired with no valid `profile_id` and failed; (2) the apply bridge line ("अप्लाई कर देती हूँ") was spoken 3–4 times per apply, plus a forbidden "प्रोफाइल देख रही हूँ" waiting line. Root cause: Step 4 led with "use the `profile_id` from `get_profile` response," steering the model to the wrong tool at apply, which also caused the fumbling/repetition.
- **Change:** First synced `Maya Hindi.md` in the repo to the current production prompt (it had diverged — production added Step 0, Pre-Apply Data Collection, turn-based Step 1, etc.). Then applied surgical fixes:
  - **Step 4 (Application):** rewritten to branch on new_seeker — "yes" → `create_profile` then `apply_job` (never `get_profile`); "no" → reuse the `profile_id` from the post-intro `get_profile` (no re-fetch, no create). Added an explicit "never call get_profile at apply time" rule and a "one bridge line → silent tool call(s) → one result" sequence.
  - **get_profile rules:** added a hard rule that get_profile never runs at apply/consent time.
  - **apply_job bridge rules:** say the bridge once per application (never 2–3×); forbid the "प्रोफाइल देख रही हूँ" / profile-fetch / waiting narration; single result message.
- **Files:** `Maya/Maya Hindi.md`
- **Not done (flagged):** Did not reorder to create the profile *before* job presentation (your ideal "create → show jobs → update → apply" flow) — kept create-at-apply to stay surgical and not break the flow. No `update_profile` step added. Can do the fuller reorder separately if you want it.

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
