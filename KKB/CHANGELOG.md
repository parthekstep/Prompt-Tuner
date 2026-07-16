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

## 2026-07-15 — Refresh KKB Placeholder Inbound to the latest flow + create Kannada inbound twin
- **Feedback/bug:** The inbound agent (`KKB Placeholder Inbound.md`, Hindi) was a version behind the just-finalized outbound KKB placeholder flow, and had no Kannada twin.
- **Change (Hindi inbound — carried the outbound "latest flow" into the get_profile-driven, hardcoded-inventory structure; did NOT reintroduce `${new_seeker}`/`${recommendations}`):**
  - **Ranking (C8):** Default Presentation Rule + Step 2 now treat the hardcoded Job Inventory as a POOL ranked by role → location → salary, presenting the 3 best-fit role-matched-first (not inventory order); the fallback draws the next best-fit batch of up to 3 from the rest of the inventory. Hallucination Guard reaffirmed (re-order only, never invent).
  - **Orient / pool-overview (C8):** Step 1 restructured into Case A (target role known → area question → ranked list) / Case B (role unknown → short pool overview naming only real inventory role types, no counts → "which interests you?" → rank), with the fork-safety guard (never the opener; changes nothing about the greeting or the silent fetch).
  - **Apply-time decision checkpoint (C7):** Step 4 now leads with the binary "Did `get_profile` return a profile in this call? YES → `apply_job` ONLY, `profile_id` = the fetch's top-level `id`, NO `create_profile`; NO → `create_profile` then `apply_job`." Added the create_profile **HARD GUARD** and bound apply_job `profile_id` to the fetch result.
  - **Bridge-once (B1):** apply_job rules now say the bridge line once, silent between/around tools, no extra apply-narration.
  - **Step 3.5 age/gender (HARD BLOCK):** new pre-apply step; skips any field already present on the fetched profile.
  - **Reading the get_profile response (C6):** new field-map (top-level `id` = profile_id; metadata.name/role/gender/age/etc.; present ⇒ known ⇒ never re-ask). The "known caller" branch now greets by first name and confirms role as its own turn (A7).
  - **+91 phone prefix (C3):** all `get_profile`/`create_profile` phone references now `+91`-prefixed, with the "Phone format (critical)" note.
  - **Examples (E1):** added the canonical-flow note; refreshed Example 1 (new caller) to ask name + age + gender before the single bridge; clarified Examples 2 & 5 skip age/gender validly (already on profile); `+91` in the get_profile/create_profile annotations.
- **Change (Kannada inbound — NEW FILE `KKB Placeholder Inbound Kannada.md`, structural parity with the refreshed Hindi):** mirrored the Hindi inbound section-for-section (112 headings identical, bar the expected "Devanagari" vs "Kannada transliteration" line). AGNOSTIC content (logic, rules, tool payloads, section skeleton, the memory-injection block) copied verbatim; SPECIFIC content (spoken lines, number-words, markers) translated to Kannada — reusing the existing Kannada translations from `KKB Placeholder Kannada.md` for all shared sections (Language/TTS/Speech-Recognition/Style/Prohibited/tool rules/success-failure/post-app/emotional/special-journey/graceful-exit/dignity) and translating the inbound-specific spoken lines.
- **Files:** `KKB/KKB Placeholder Inbound.md` (refreshed), `KKB/KKB Placeholder Inbound Kannada.md` (new).
- **Ported from:** KKB outbound placeholder (2026-07-15 latest flow). Self-checked both files against `bug-patterns.md` / `section-checklists.md` (C7, C6, C8, B1, A7, C3, memory block, TTS number-words, Devanagari/Kannada script separation) — no new bug class, so no analyser change (carrying already-working behaviour into a sibling variant + a new language twin).
- **Decision/flag:** the Kannada inbound's hardcoded inventory keeps the **real UP job data** (same `job_id`s, companies, salaries, Ghaziabad/Noida locations) rather than swapping to Bengaluru-region jobs — `job_id` is an `apply_job` payload key bound to those specific backend jobs, so localizing company/location would decouple the spoken details from the job actually applied to (a C3-class data risk). Only the `qualification` display strings were translated to Kannada, and salary/vacancy are spoken in Kannada number-words per the TTS rules. Sample-conversation place names therefore stay Ghaziabad/Noida (in Kannada script), not Bengaluru, since they must reference real inventory jobs.

## 2026-07-15 — Refresh sample conversations to the ported flow (E1)
- **Feedback/bug:** After the Maya port, the 6 sample conversations still modelled the older lead-in and (critically) applied WITHOUT the Step 3.5 age/gender step — an E1 risk (examples override prose; the model could learn to skip a HARD BLOCK).
- **Change (both languages):** rewrote **Example 1** to model the full new shape — profile-found greet + role-confirm as its own turn → separate orient/area turn → **ranked** list (role-matched first) → deep-dive → **age/gender asked (not on profile)** → ONE bridge → `apply_job` (no `create_profile`); added the apply-checkpoint note. Added a **canonical-flow note** to the Sample Conversational Patterns header clarifying the shape and that returning/profile-found examples correctly *skip* the age/gender ask because those fields are already known (a valid Step 3.5 skip, not an omission).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`.

## 2026-07-15 — Fix bare phone → +91 prefix in get_profile/create_profile (C3)
- **Feedback/bug:** Spotted during the Maya port — KKB passed the bare 10-digit `${contact_phone}` to `get_profile` (`phoneNumber: ${contact_phone}`) and built `create_profile` payloads with a bare `phone`. Same class as the Maya C3 bug: profiles are stored with a `+91` country-code prefix, so a bare number returns empty fetches and creates mismatched profiles.
- **Change (AGNOSTIC — both language files, verbatim):** `phoneNumber: +91${contact_phone}` in all `get_profile` references (Profile Handling, get_profile rules, Example 1); create_profile minimum payload `"phone": "+91<contact_phone>"`; additional-example phone `+91…`; Contact-Context-Variables note + a "**Phone format (critical)**" rule (no double-prefix if a country code is already present).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (parity verified: 7 `+91` each, no bare phones). Analyser **C3** "Seen in" extended to KKB.

## 2026-07-15 — Port full Maya presentation + apply set to KKB placeholder (both languages)
- **Feedback/bug:** Parth: carry the Maya changes forward to KKB placeholder — the "we have a/b/c kinds of jobs, which interests you, then show the rest" overview, plus (chosen: full set) the ranking, apply-time checkpoint, bridge-once, and turn barriers.
- **Change (KKB Hindi source-of-truth, mirrored verbatim to Kannada; spoken lines adapted per language):**
  - **Default Presentation Rule → ranking:** treat `${recommendations}` as a pool; rank by **role → location → salary** and present the **3 best-fit**, role-matched first, instead of blind array order. Replaces "always first 3 / jobs 4–10 / lower-index". Applies to both new_seeker paths.
  - **Profile Handling "no" → "Using the fetched profile":** greet by first name, confirm role (turn ENDS on that question — WAIT), rank role-matched first, never re-ask known fields. New "## Reading the get_profile response" field-map (binds top-level `id` as `profile_id`).
  - **Step 1 → "Lead-in and orient" (Case A / Case B):** Case A (role known) → area question → ranked Step 2; Case B (role unknown) → short **pool overview** naming real role types → "which interests you?" → rank. Removes the old ask-before-show ("इस तरह का काम देख रहे हैं?" before listing). Includes the fork-safety guard (overview is never the opener, never replaces the profile-permission question).
  - **Step 2:** present the ranked best-fit 3 (role-matched first), fallback draws next best-fit from the rest of the pool (same ranking, batched up to 3).
  - **Step 4 → decision-first apply checkpoint:** "Did `get_profile` run in this call? → YES: `apply_job` ONLY (profile_id from the fetch result), no `create_profile`; NO: `create_profile` then `apply_job`." + create_profile **HARD GUARD** (no duplicate when a profile was fetched) + apply_job payload `profile_id` bound to the fetch result + **bridge-once** (silent between/around tools, no extra apply-narration).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (parity verified: 0 stale refs, identical marker counts).
- **Ported from:** Maya (2026-07-13/15 ranking + overview + apply-checkpoint + bridge-once work). Not a new bug class — no analyser change (port of already-working behaviour).
- **Not done / flagged:** (1) the 6 sample conversations still model the older Case-A lead-in (they don't depict the Case B overview or the Step 3.5 age/gender step — largely consistent, optional refresh). (2) KKB `get_profile`/`create_profile` still pass the **bare** `${contact_phone}` (no `+91`) — this is the same C3 format bug Maya fixed (~14/80 empty fetches); left untouched as out-of-scope for this port, worth a separate fix.

## 2026-07-15 — No-Match line: drop the "galti ho gayi" self-blame
- **Feedback/bug:** The No-Match Fallback opened by admitting fault ("लगता है हमसे एक गलती हो गई —" / "ನಮ್ಮಿಂದ ಒಂದು ತಪ್ಪಾದಂತೆ ಕಾಣ್ತಿದೆ —"). Parth: remove the "galti ho gayi" wording — the bot shouldn't confess a mistake to the caller.
- **Change:** Removed the self-blame clause from both No-Match Fallback occurrences in each language; the line now opens directly with the status. Hindi: "आपके लिए relevant jobs अभी नहीं दिख रहीं। हम जल्द ही सही options ढूंढकर आपको बताएंगे।" Kannada: "ನಿಮಗೆ relevant ಜಾಬ್‌ಗಳು ಈಗ ಕಾಣ್ತಿಲ್ಲ. ನಾವು ಶೀಘ್ರದಲ್ಲೇ ಸರಿಯಾದ ಆಪ್ಷನ್‌ಗಳನ್ನು ಹುಡುಕಿ ತಿಳಿಸುತ್ತೇವೆ." (SPECIFIC spoken line — adapted per language, not verbatim.) KKB Inbound has no apology phrasing, so it was untouched.
- **Files:** `KKB/KKB Placeholder Hindi.md` (2 occurrences), `KKB/KKB Placeholder Kannada.md` (2 occurrences).

## 2026-07-13 — Reconcile repo to the live working copy: add Step 3.5 (Pre-Apply age/gender)
- **Feedback/bug:** While fixing the fork, a full compare of the repo files against the prompt Parth was actually running revealed the repo was a version behind: the running copy had a **`## Step 3.5 — Pre-Apply Data Collection (age and gender — mandatory before apply)`** block (age + gender questions, skip-if-in-profile, and a HARD BLOCK gating `apply_job` on age+gender being known) that neither repo language file had. Everything else matched (headings, Step 4 body, Example 1 all identical; grep confirmed zero age/gender content in the repo). Left unreconciled, the repo fork fix and the running copy's Step 3.5 would live in different files.
- **Change:** Added Step 3.5 to **KKB Hindi** verbatim from the running copy, and mirrored to **KKB Kannada** — rules/logic/HARD BLOCK copied verbatim (AGNOSTIC); the spoken lines adapted to Kannada idiom (age Q "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು — ಸುಮಾರಾಗಿ ಹೇಳಿ?", confirm "ನೀವು [X] ವರ್ಷ ಅಂದ್ರಿ, ಸರಿನಾ?", gender "ನೀವು male ಆ, female ಆ?", decline "ಪರ್ವಾಗಿಲ್ಲ", seeker "ಹೌದು ಅಪ್ಲೈ ಮಾಡಿ"). Repo Hindi now == the running copy + the fork fix; both languages in sync (Step 1→2→3→3.5→4).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`.
- **Process note:** the fork fix earlier this session was applied after spot-checking only the fork lines against the pasted prompt, not a full compare — which is how the Step 3.5 gap went unnoticed at first. Lesson: when a user pastes a prompt, diff the whole thing against the repo copy before editing, so repo drift surfaces up front.

## 2026-07-13 — Fix the new_seeker fork: variable-interpolation order (G1) + branch contradiction (A4)
- **Feedback/bug:** The new_seeker fork wasn't working in KKB — the same failure fixed in Maya. Two mistakes: **(1) G1 (root cause):** the binding phrase read `Consider ${new_seeker} as new_seeker`, which interpolates at runtime to "Consider **no** as new_seeker" — the value lands where the label should be, so `new_seeker` never binds and the branch has nothing to switch on (falls through to a default path). Present in **two** places (Contact Variables line + Profile Handling step). **(2) A4:** the `new_seeker="no"` branch header says "caller already has a profile" but its body said "MANDATORY STEP IF USER PROFILE DOES NOT EXIST" — a header/body contradiction that muddies the returning-caller path. (Both were pre-flagged in the analyser from the Maya work: G1 was catalogued as "latent in KKB, not yet flipped"; A4 from Maya 2026-07-05.)
- **Change (both language files, AGNOSTIC → verbatim):**
  - Flipped both bindings to **`Consider new_seeker as ${new_seeker}`** (→ "Consider new_seeker as no", binds cleanly).
  - Rewrote the `"no"` branch's mandatory-step line to drop the "IF USER PROFILE DOES NOT EXIST" contradiction and state the path plainly: new_seeker "no" = caller already HAS a profile → the profile-permission question is the very next turn after the greeting, and `get_profile` must run before any job talk.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (identical fix, parity preserved); `.claude/skills/prompt-analyser/reference/bug-patterns.md` (G1 "Seen in" updated — KKB no longer latent, now flipped).
- **Not affected:** `KKB Placeholder Inbound.md` — that variant removed `${new_seeker}` entirely (fork decided by the `get_profile` result), so it has no binding bug.
- **Re-test:** a `new_seeker="no"` call must ask "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" and call `get_profile`; a `"yes"` call must NOT mention/fetch a profile.

## 2026-07-13 — New agent: KKB Placeholder Inbound (Hindi)
- **Feedback/bug:** Need an inbound clone of the outbound KKB Hindi agent — same persona and safety, but the seeker calls *in* rather than being called.
- **Change:** Created a new standalone inbound conversation prompt by cloning `KKB Placeholder Hindi.md` and re-domaining three things: (1) **Introduction** — dropped the outbound "मैं गवर्नमेंट की तरफ से कॉल कर रही हूँ / आपके लिए कुछ जॉब्स हैं" opener; new callers now get a welcome + discovery question ("बताइए, आप किस तरह का काम ढूंढ रहे हैं?"). Returning-caller resume (contact memory) retained. (2) **Input variables removed** — no `${contact_name}`, `${new_seeker}`, or `${recommendations}`. The new-vs-returning fork is now decided by the `get_profile` result (called silently at call start with the caller-ID `${contact_phone}`, no permission ask): profile found → known caller; nothing → new-caller path (gather → `create_profile` before apply). `${contact_phone}`/`${country_code}` (caller ID) and `${contact_memory}` retained as the only inputs. (3) **Hardcoded Job Inventory** — replaced `${recommendations}` with a 17-job internal inventory injected in-prompt, plus a new **Inbound Discovery** step (ask role/location/salary), full-inventory scan with synonym + salary-floor + nearby-location matching, top-3 presentation, and an **Inbound No-Match Fallback**. Deep-dive `benefits` and post-apply `hr_contact` sharing wired to the inventory fields. All 6 sample conversations rewritten to inbound flow using real inventory jobs. All language/TTS/speech-recognition/dignity/tool sections preserved verbatim.
- **Files:** `KKB/KKB Placeholder Inbound.md` (new)
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
