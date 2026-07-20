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

## 2026-07-20 — DKB (H+K): Yes/No Gate Capture — register the owner's answer before advancing
- **Feedback/bug:** Sheet row 26 — employers said yes/no clearly but the bot didn't register it and advanced anyway (wrong branch / skipped consent), causing frustrated drop-offs (calls 2465759, 3663530, 3664822).
- **Change:** Added a "Yes/No Gate Capture (Mandatory — Register Before Advancing)" section listing the five yes/no gates (identity, availability, job-freshness, new-vacancy, post-consent) and requiring the bot to capture + briefly confirm a clear yes/no before branching or firing a tool, with a single re-ask when no clear response is captured (an explicit "unsure" is itself a captured answer). (Analyser D14.)
- **Files:** DKB Hindi.md, DKB Kannada.md

## 2026-07-16 — DKB Inbound: drop `${country_code}` input assumption; always `+91`
- **Feedback/bug:** An inbound call has **no input variables**, so `${country_code}` is never passed — but the DKB inbound Input Variables section declared it as a caller-ID input "used for tool calls where required." This is a false-input assumption (C3-adjacent): if the model tried to build a phone value from a non-existent `${country_code}`, the `phoneNumber` lookup would be malformed/empty.
- **Change:**
  - Rewrote the `${country_code}` declaration to state it is **NOT a passed input** on an inbound call, must never be referenced in any tool payload, and that the country code is **always assumed `+91`** — the `phoneNumber` field is built from the caller's number with a literal `+91` prefix (pointing to `${contact_phone}`).
  - Strengthened the `${contact_phone}` declaration to require the `+91` prefix always (never the bare 10-digit number) and added the **don't-double-prefix guard** ("if `${contact_phone}` already includes a country code, do not double-prefix; the value must carry exactly one `+91`"), mirroring the KKB inbound precedent (`KKB Placeholder Inbound.md`).
  - **Audited all four tool payloads** (`create_job`, `update_job_status`, `update_job_details`, `get_talent_insights`): none references `${country_code}`; every `phoneNumber` already uses `${contact_phone}` "(in +91 form)" and the example payloads use literal `+919108790249`. No payload change was needed — only the input-variable declaration was wrong.
  - **Untouched (verified byte-identical):** all fixed params (`sourceService: "ONESTAGENT"`, `eventType: "UPDATE_JOB"`/`"JOB"`, `app_instance: "up-postjob"`), enum values, field names, the `### Contact context` memory block, and every spoken line.
  - Change is language-agnostic (payload/logic); applied to Hindi (source of truth) and mirrored **verbatim** to Kannada. The two edited declaration lines are byte-identical across H/K.
- **Files:** `DKB/DKB Inbound Hindi.md`, `DKB/DKB Inbound Kannada.md`

## 2026-07-15 — New agent: DKB Inbound (employer-inbound, Hindi + Kannada)
- **Feedback/bug:** Need an inbound variant of DKB — an MSME owner **calls in** to post or verify a job (rather than DKB calling out about an expiring posting). Built new, not an edit to the outbound files.
- **Change:**
  - **Intro reframed to inbound:** replaced the outbound turn-based screening ("are you the owner / your posting expires today / do you have 2 minutes / connect me to the owner") with an inbound welcome + AI-and-recording disclosure (said once, Turn 1) + a single discovery question ("क्या आप नई जॉब पोस्ट करना चाहते हैं, या किसी मौजूदा जॉब के बारे में बात करनी है?"). Kept a "who are you" handler and a non-employer/wrong-number close.
  - **Input variables:** removed all outbound job inputs (`${company_name}`, `${job_role}`, `${num_vacancies}`, `${job_id}`, `${city}`, `${salary}`, `${location}`, `${qualification}`, `${work_experience}`, `${work_experience_years}`). Kept caller-ID inputs `${contact_phone}` / `${country_code}` and the verbatim `### Contact context / {${contact_memory}}` memory-injection block.
  - **Phase Entry Rule → Inbound Routing Rule:** returning-vs-new fork is decided by the silently-read `${contact_memory}` (returning-owner opening + recalled roles) plus the owner's discovery answer — DKB has **no read/lookup tool**, so no tool fetch is used and none was invented. New-job capture (Phase 3) is the primary, fully tool-backed flow. Phase 1/2 (freshness/completeness) are kept but hard-gated on a `${job_id}` being available on the call (there is no `${job_id}` input inbound and `${contact_memory}.roles_posted` has no id); if none is available the agent must not fabricate one or call update_job_status/update_job_details — it re-captures via Phase 3.
  - **Preserved byte-identical:** all four tools and payloads (`get_talent_insights`, `update_job_status`, `update_job_details`, `create_job`), fixed params (`sourceService: "ONESTAGENT"`, `eventType: "UPDATE_JOB"`/`"JOB"`, `app_instance: "up-postjob"`), enum values, field names, Market Truth Delivery, Language/Script, TTS, Speech-Recognition, Prohibited, Consent, Error/Uncertainty, Silence, Emotional, Graceful Exit, Dignity. `phoneNumber` value is the inbound caller-ID `${contact_phone}` in `+91` form (consistent with the KKB inbound precedent and the C3 phone-format fix).
  - **Hindi is source of truth; Kannada mirrored** — agnostic logic/payloads verbatim, spoken lines reused from `DKB Kannada.md` for shared sections and adapted for the inbound intro/routing; region example values kept per convention (Hindi Ghaziabad/UP, Kannada Dharwad/Karnataka). Section headings verified identical across the two files.
- **Files:** `DKB/DKB Inbound Hindi.md` (new), `DKB/DKB Inbound Kannada.md` (new)

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
