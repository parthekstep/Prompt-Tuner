# Bug-Pattern Catalog

The distilled, reusable form of every failure class we've hit across KKB, DKB, Maya (and the
Purple Dots review). Each entry: **Symptom** (observable) → **Root cause** → **Detection
heuristic** (what to look for in a prompt) → **Fix direction** → **Seen in**. Apply every
heuristic during a sweep. When a new class appears, add it here (see SKILL.md → "Growing the
skill").

The recurring meta-lesson across almost all of these: **a rule being present in the prompt
does not mean it holds at runtime.** A competing action, an example, or skip logic can quietly
override it. Always check *why the rule would fail*, not just whether it exists.

---

## A. Flow & sequencing

### A1 — Mandatory step skipped because the competing action isn't forbidden
- **Symptom:** a step the prompt calls "mandatory" is intermittently skipped; the agent jumps to a later phase.
- **Root cause:** the prompt says what to DO but never forbids the rival action that fires instead. Positive reinforcement alone loses to a strong competing default.
- **Detection:** for each "must / mandatory / always" step, ask "what else could the model do at this moment, and is that explicitly forbidden here?" If there's no **negative gate** ("X may NOT run / begin until Y has happened"), flag it. **Strongest signal:** a branch whose paths point to a *separate top-level section* (its own `##` heading) rather than to an inline action — the model treats that prominent section as the default next thing. Compare to a sibling agent whose equivalent branch works and check whether it keeps the action inline.
- **Fix direction:** add a hard negative gate at the top of the competing action. **But a negative gate can still lose if the competing action is a prominent standalone section** — the reliable fix is to **delete that section and fold its action inline into the branch paths, so there is nothing to jump to** (mirror the sibling agent where the branch already works).
- **Seen in:** Maya 2026-07-08 (Experience Capture ran before `get_profile` until it was forbidden as the first post-greeting action); Maya 2026-07-13 (the `new_seeker="no"` branch kept bypassing `get_profile` through Step-0 removal, standalone-section deletion, AND hard gates — **none of these was the real fix**; the actual root cause was a variable-interpolation ordering bug, see **G1**. Removing the competing section is still good hygiene, but it was not what fixed this — a reminder not to declare victory on a plausible structural change without confirming it on a live call).

### A2 — Skip-forward pressure with no backpressure
- **Symptom:** phases/steps that require active work get treated as optional; agent races to the end.
- **Root cause:** aggressive SKIP-AHEAD / ORDER-FLEX / "move silently to the next phase" / "never retroactively verify" logic, with no counterbalancing "you must still do X before proceeding."
- **Detection:** count the skip-enabling rules vs the must-do gates. Heavy skip logic + few hard gates on the mandatory/terminal steps = flag. Especially dangerous on silent tool phases (see C1).
- **Fix direction:** pair every skip rule with an explicit exception list of steps that are never skippable.
- **Seen in:** Purple Dots review (Solution Enablers + Phase 4-5-6 tool calls skipped under `[SKIP-AHEAD]`/`[ORDER-FLEX]`).

### A3 — Overlapping/adjacent phases conflated
- **Symptom:** the agent believes a later step is "already done" because an earlier step captured something similar.
- **Root cause:** two sections capture conceptually overlapping content (e.g. Phase 2 "challenges/barriers" vs Phase 3 "missing enablers"), and NO-REPEAT/SKIP logic then marks the later one satisfied.
- **Detection:** look for two sections that both capture "what the user lacks / needs / barriers." Check whether the prompt draws a sharp line between them and whether the later one has its own must-run gate.
- **Fix direction:** state the distinction explicitly and give the later step an independent gate.
- **Seen in:** Purple Dots review.

### A4 — Latent contradiction inside one branch
- **Symptom:** behaviour flip-flops on the same input.
- **Root cause:** a section's header says one thing and its body says the opposite (e.g. header "caller already has a profile" vs body "MANDATORY IF PROFILE DOES NOT EXIST").
- **Detection:** read each branch header against its body; flag any header/body or intra-section contradiction. Also flag the same rule stated with different thresholds in different places.
- **Fix direction:** reconcile to one statement.
- **Seen in:** Maya 2026-07-05 (contradictory `new_seeker="no"` branch).

### A5 — Re-collecting data already available
- **Symptom:** the agent asks for a field (age, gender, location…) it already has from the fetched profile / prior context, making the call feel like a form.
- **Root cause:** the data-collection step is unconditional ("always ask age and gender") and never checks the fetched profile / known context first.
- **Detection:** for each "always ask / must collect" field, check whether the prompt first says "skip if already present in the profile/context." An unconditional MANDATORY/HARD-BLOCK ask, with a profile fetch upstream, = flag.
- **Fix direction:** gate each ask on "not already known — asked in this call OR present in the fetched profile"; ask only the genuinely missing fields.
- **Seen in:** Maya 2026-07-13 (age/gender re-asked for returning `new_seeker="no"` seekers whose profile already had them).

### A6 — Confirmation/interest asked before the content it refers to
- **Symptom:** the agent asks "are you interested in these?" *before* actually presenting the options, then presents them, then asks again — a confusing double-ask; the first ask has nothing concrete behind it.
- **Root cause:** an ordering rule mandates a confirmation turn *before* the listing turn (ask-before-show), often with "do NOT list yet" guards.
- **Detection:** look for a confirm/interest question that is required before the content (jobs/options/details) is shown. Flag any "confirm interest → then list" ordering, and any "do NOT list yet" gate that pushes the ask ahead of the content.
- **Fix direction:** present the content (with the details the user needs to judge), then ask for interest/selection. A brief lead-in is fine; a standalone interest question before the content is not.
- **Seen in:** Maya 2026-07-13 (Turn 1A asked "इस तरह का काम देख रहे हैं?" before Step 2 listed the jobs).

### A7 — Multiple questions/steps chained into one turn (no wait-for-answer)
- **Symptom:** the agent asks two or more distinct questions (or acknowledgement + question + a next-step question) in a single turn, "just keeps talking," and the caller can only answer the last one — so earlier answers (e.g. the role confirmation) are lost.
- **Root cause:** adjacent steps are described as flowing one into the next ("do X, then continue to Step 1") with no explicit "end the turn / wait for the answer" between them, so the model fuses them into one utterance. A voice channel needs a hard one-question-per-turn bound at each hand-off.
- **Detection:** wherever two askable things are adjacent (acknowledge→confirm→next-step, role-confirm→area, age→gender), check there is an explicit "STOP / wait for the answer / this is a separate turn" between them. "then continue to Step N" with no wait = flag. Also check examples don't model a fused turn. A non-question acknowledgement may ride with one question; two questions together may not.
- **Fix direction:** end each turn on exactly one question; add "wait for the answer; the next question is a separate turn"; keep transitions explicit at every step hand-off.
- **Seen in:** Maya 2026-07-13 (name-ack + role-confirm question + area question all fired in one turn — "…इसी तरह की जॉब्स देख रहे हैं? …किस इलाके…?" — so the seeker answered only the area and the role confirmation was skipped).

### A8 — Forceful one-branch mandate bleeds onto the other fork value (no decisive router)
- **Symptom:** a control-variable fork (e.g. `new_seeker` yes/no) routes to the WRONG branch — a branch written with forceful, unconditional-sounding "MANDATORY / NO EXCEPTIONS / the very next thing you say" language fires even when the variable holds the OTHER value. E.g. `new_seeker="yes"` (new caller) but the bot still asks the profile-permission question and calls `get_profile` (the "no"-branch mandate over-fired).
- **Root cause:** the forceful/mandatory wording on one branch is not scoped to its branch value, and there is no decisive up-front router that reads the variable FIRST and dispatches. The salient MANDATORY block dominates the weaker other branch. (Distinct from **G1**, where the value never binds — here it binds fine but the prose over-fires; distinct from **E1**, where an *example* bleeds — here it's the *prose*.)
- **Detection:** for any control-variable fork, check (a) a **DECISIVE ROUTER** at the top reads the variable FIRST and dispatches, naming each path's forbidden actions; (b) each branch's forceful/mandatory language is explicitly **scoped to its value** ("applies ONLY when X = …"); (c) the two branches are **equally forceful** — the "do NOT do Y" branch forbids Y as strongly as the other branch mandates it. Asymmetric forcefulness (one branch "MANDATORY/NO EXCEPTIONS", the other a mild "do not…") or a missing router = flag.
- **Fix direction:** add a decisive router (check the var first; state each path's forbidden actions + the rationale); scope the mandatory wording to its branch value; make the prohibition on the other branch as forceful as the mandate. Do NOT weaken the branch that was working.
- **Seen in:** KKB 2026-07-16 (`new_seeker="yes"` still asked "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" and called `get_profile` — the "no"-branch MANDATORY bled onto "yes"; fixed with a decisive router + scoping the mandate to "no" + a forceful "yes → fetch FORBIDDEN"); Maya 2026-07-16 (same latent risk — unscoped MANDATORY, no router — found and fixed the same way). **Meta:** the `new_seeker` fork has now failed in THREE distinct ways — binding (G1), example bleed (E1), prose over-fire (A8) — so when a control-variable fork misroutes, audit all three.

---

## B. Repetition & loops

### B1 — One-time utterance/consent fired repeatedly
- **Symptom:** a bridge line, a consent ask, or a confirmation is spoken/asked several times in one call.
- **Root cause:** a one-time action is attached to a per-entity loop ("do X once for each provider/job") **or to a multi-tool sequence** (bridge → `create_profile` → `apply_job`), so it re-fires at each entity/tool boundary. **A bare "say once" rule in prose is not enough** — the model still re-emits the line at the next tool call unless it is *also* told "once said, never again; say nothing between tools," and told to say it *only immediately before the tool, after all prerequisites are met* (not at an earlier consent moment while fields are still being collected).
- **Detection:** find every "for each …" / multi-entity action and every **multi-step tool sequence**, and check whether a spoken line sits at a boundary inside it. Confirm each consent/bridge line has (a) an explicit "say **once**", (b) a "once said, never repeat — stay silent between tool calls" bound, and (c) a gate that it is said only right before the tool. Multiple backend entities/tools + one human-facing line = high-risk.
- **Fix direction:** say the line once, immediately before the tool, after prerequisites; then loop/chain the tool calls **silently**; never re-emit between tools. Reduce the number of tools in the path where possible (e.g. no `create_profile` on the returning path) so there are fewer boundaries to trip on.
- **Seen in:** Maya 2026-07-08 (apply bridge spoken 3–4× per apply) and **again 2026-07-13** (bridge said at first consent *and* 2–3× more across the `create_profile`→`apply_job` sequence, despite a "say once" rule — needed the "never again / silent between tools / only-just-before-tool" bounds); Purple Dots review (share-consent asked per provider).

### B2 — Forbidden waiting/narration line leaks
- **Symptom:** agent narrates a background tool call ("प्रोफाइल देख रही हूँ…") though tool calls are meant to be silent.
- **Root cause:** the tool-call instruction leads with a data source that steers the model to narrate, and there's no explicit ban on waiting/fetch narration.
- **Detection:** for each background tool, check for an explicit "do not announce / no waiting line" rule. Flag any spoken line that describes fetching/looking up.
- **Fix direction:** add "silent and internal" per-tool + one result message only.
- **Seen in:** Maya 2026-07-08; DKB 2026-06-29 ("Tool calls are silent and internal").

---

## C. Tool calls & payloads

### C1 — Silent terminal tool calls dropped (no anchor, no gate)
- **Symptom:** end-of-call APIs (update/match/connect) intermittently never fire; the call ends early.
- **Root cause:** the phases are entirely silent background calls with no conversational cue and no "you may not close the call until X has run" gate. Heavy prompts amplify this (the model sheds steps).
- **Detection:** find every background-only phase. Check for (a) a must-run gate before the next action, and (b) a "never end/close the call before <final tool> (or the decline path) has run" gate. Check cascading gates — if phase N is gated on phase N-1's tool, a miss upstream silently kills all downstream calls.
- **Fix direction:** add `CRITICAL: you MUST call <tool> before proceeding` per phase + a hard "do not close before <terminal tool>" gate; mark calls mandatory-but-silent.
- **Seen in:** DKB 2026-06-29 ("call update_job_status for every job before proceeding"); Purple Dots review (Phase 4-5-6).

### C2 — Tool referenced but not declared
- **Symptom:** a step that depends on a lookup sheet/tool is skipped or hallucinated.
- **Root cause:** the step names a tool/"sheet" that is never declared in the tools/source-of-truth section, so the model can't ground it.
- **Detection:** list every tool/sheet *named in the body* and diff against the tools *declared* in the tool section. Any referenced-but-undeclared tool = flag.
- **Fix direction:** declare the tool, or remove the dependency.
- **Seen in:** Purple Dots review (`solution_enablers tool sheet` referenced, never declared alongside `Disabilitytypes`/`AssistiveAids`).

### C3 — Payload field/data bug
- **Symptom:** tool call returns wrong/empty results or targets the wrong record.
- **Root cause:** swapped or mislabeled fields (e.g. `searchlng ← lat`, `searchlat ← lng`), malformed variable names (`${phone(number}`), a wrong field name in prose vs payload (`work_experience_years` vs `workExperienceYears`), a **value-format mismatch** (e.g. a phone passed as a bare 10-digit string when the store expects a `+91`/country-code-prefixed value → empty lookup), or a **hardcoded ID overriding dynamic results**.
- **Detection:** for each payload, trace every value to its source. Check coordinate order (GeoJSON = `[lng, lat]`), check field names match the schema exactly, scan for stray/unbalanced brackets in `${...}`, confirm identifier **formats** match what the target store expects (phone with/without `+91`) **and that a write (create) and its later read (fetch/lookup) use the same format**, and flag any hardcoded id that contradicts a dynamic search in the same flow. **Also flag any assumption that `${country_code}` (or a similar country/prefix variable) is a passed input — INBOUND calls carry NO input variables, so it is unset at runtime; the phone must be built as the caller number with a literal `+91` prefix (exactly one prefix, never doubled), never sourced from a `${country_code}` variable.**
- **Fix direction:** correct the mapping/format; make create and lookup use the identical key format; reconcile hardcoded vs dynamic; hardcode `+91` (never rely on a passed `${country_code}`, especially on inbound).
- **Seen in:** DKB 2026-06-29 (`${phone(number}` → `${phoneNumber}`, `workExperienceYears`); Maya 2026-07-13 (`get_profile`/`create_profile` passed the bare number → ~14/80 empty fetches; fixed to `+91`-prefixed on both); KKB 2026-07-15 (same bare-number bug in both KKB placeholder language files — carried the fix over from Maya); KKB/Maya/DKB **inbound** 2026-07-16 (`${country_code}` declared as a passed input on inbound calls that have none → unset at runtime; fixed to "not a passed input → always assume `+91`", with the double-prefix guard); Purple Dots review (lat/lng swap; hardcoded provider `item_id`).

### C4 — Fixed-param / enum integrity
- **Symptom:** downstream system rejects the payload or mis-routes.
- **Root cause:** a fixed param drifted (`sourceService`, `eventType`, `app_instance`, `network`, `item_type`), or an enum field was populated in the wrong language / with a value outside the allowed set.
- **Detection:** verify every "always use this exact value" param is present and unchanged. For every enum field, confirm the prompt constrains it to the exact allowed strings **in English/Latin** and forbids the conversational-language version.
- **Fix direction:** restate the fixed value and the strict enum list at the payload.
- **Seen in:** DKB (fixed params `ONESTAGENT`, `app_instance`); Purple Dots (`disability_type`/`looking_for`/`documents_available` enum + English-only rule).

### C5 — Spoken line stands in for a tool call that never fires (fabricated result / hallucinated success / intent-without-action)
- **Symptom:** the agent SPEAKS a tool's outcome or intent as if done, but the tool was never actually emitted. Three shapes: (a) **hallucinated success** — "अप्लाई हो गया" but `apply_job` never ran (or errored); (b) **fabricated fetch** — a silent `get_profile` "first action" is narrated as done ("प्रोफ़ाइल मिल गई, [name]") with the name/role pulled from injected `${contact_memory}`, the tool never called; (c) **intent-without-action** — the apply bridge ("अप्लाई कर देती हूँ") is spoken (often repeated) but `apply_job` is never emitted; the model loops on the line.
- **Root cause:** the spoken line is treated AS the action. Nothing binds "profile found" / "I'll apply" / "applied" to an actually-emitted tool call, so the model fabricates the result from memory/context or repeats the intent line instead of firing the tool. Injected `${contact_memory}` makes fabrication especially tempting (the name is right there).
- **Detection:** for every tool whose result or intent has a spoken line (`get_profile` "profile found / name", the apply bridge, the success line), confirm the prompt states: the SPOKEN LINE IS NOT THE ACTION — the real tool call MUST be emitted (for a bridge, in the SAME turn); the result/name/id/`profile_id` comes ONLY from a real tool result, **never fabricated from `${contact_memory}` or context**; repeating the line is never a substitute; no waiting-narration around the call. Missing any = flag.
- **Fix direction:** bind the spoken line to a really-emitted tool call; ban inferring the result (name/role/id) from memory/context; require a bridge to be immediately followed by the tool call in the same turn and forbid re-speaking it as a stand-in; gate the success line on a real success result; ban waiting-narration.
- **Seen in:** Maya 2026-07-13 (`apply_job` never fired but "अप्लाई हो गया" spoken after `create_profile`); **Maya inbound 2026-07-16** (silent `get_profile` faked — "प्रोफ़ाइल मिल गई, [name]" spoken from `${contact_memory}`, tool never called → no `profile_id` → apply failed); **Maya outbound 2026-07-16** (bridge spoken twice, `apply_job` never emitted). Fixed by binding each spoken line to a really-emitted call, banning memory-fabrication + waiting-narration, and requiring the bridge→`apply_job` call in the same turn.

### C6 — Fetched response never consumed (no field map, no "use what's present" rule)
- **Symptom:** a lookup succeeds and returns rich data, but the agent proceeds generically — never addresses the caller by the returned name, never reflects the returned role/context, and re-asks fields the response already contains. The fetch was effectively pointless.
- **Root cause:** the prompt calls the tool but never (a) describes the **response shape / field meanings**, (b) says **which record to read** when the response is an array / multi-record, or (c) states that **any present field is authoritative and must be used, not re-asked**. With no read-back contract, the model treats the call as fire-and-forget and falls back to a generic script.
- **Detection:** for every data-returning tool (`get_profile`, `get_talent_insights`…), check the prompt has a "reading the response" section: a **field dictionary**, an **array / most-recent-record selection rule**, and an explicit **"present ⇒ known ⇒ ask only for genuinely missing"**. Also check at least one **example actually uses** the fetched data (greets by name, confirms role). Missing any = flag. (A5 — re-asking known fields — is one visible symptom of this broader gap.)
- **Fix direction:** add a response-field map + a most-recent-record rule + "present ⇒ known ⇒ never re-ask"; personalise from it (address by first name, reflect/confirm role); have an example model it.
- **Seen in:** Maya 2026-07-13 (`get_profile` returned a 6-profile array with name/role/age/gender; the agent ignored all of it, spoke the hold line, and jumped straight to the area question — no name, no role check — and would have re-asked age/gender. Fixed by adding a "Reading the get_profile response" field map + a "Using the fetched profile" name/role-confirm flow + Example 4).

### C7 — Fetched identifier not bound → downstream re-creates it (duplicate write)
- **Symptom:** a read/fetch already returned the record, but at action time the agent calls the **create/write** tool instead of reusing the fetched record — creating a duplicate — often because the response held several records and it was unclear which id to reuse. **The INVERSE also fails:** a NEW caller (no profile ever fetched) reaches apply and calls `apply_job` DIRECTLY, skipping the required `create_profile` — so no `profile_id` exists and the apply FAILS.
- **Root cause:** the prompt says "reuse the id from the fetch" but never (a) names the exact field (top-level `id` vs `userId`), (b) says **which record** when the response is an array, or (c) states "a record exists ⇒ reuse it ⇒ the create path is forbidden here." With no bound key, the model regenerates one via create (which conveniently returns a fresh id).
- **Detection:** for any flow that fetches a record then acts on it, check the prompt (1) names the exact id field, (2) picks one record deterministically (most-recent) when several return, and (3) **hard-forbids** the create/write path when the fetch succeeded (not merely "prefer reuse"). Missing any = flag. Cross-refs C6 (response not consumed). **Also check the fix is structural, not just prose** (see Fix direction) — a prompt with three "do not create" sentences can still fail this if the apply step doesn't lead with the binary checkpoint.
- **Fix direction:** bind "the most-recent record's `id` is THE `profile_id`; read it straight from the fetch result at action time"; make the create path visibly the **exception** (lead the action step with the reuse=one-tool path); add a **precondition STOP at the create tool's entry**. **Prose "do not create" guards alone are NOT enough** — the model still calls create because it needs an id and create is the tool that hands one back. The lever that holds is an action-time checkpoint keyed on the binary, in-context signal **"did the fetch run in this call?"**: if yes → the action tool (apply) is the ONLY call and its id comes from the fetch result; the create tool is forbidden. Reframe the action step to *decide with that one question first*, not to react with bans. **Both directions must be equally forceful:** the NO branch (no profile → `create_profile` FIRST, then `apply_job`) needs the same salience as the YES branch — state that `apply_job` without a `profile_id` FAILS and `create_profile` is the required first step (not optional), and that any "never mention/think about profiles" instruction given to a new caller applies to the conversation only, NOT to apply time.
- **Seen in:** Maya 2026-07-13 (`get_profile` returned a 6-profile array on the returning `new_seeker="no"` path; at apply the agent called `create_profile` and used its fresh id — a duplicate). **First fix (bind `id` + 3 hard "never create" guards) did NOT hold — it recurred the same day**: the agent still called `create_profile` at apply. The holding fix reshaped Step 4 to *lead* with "Did `get_profile` run in this call? → YES: `apply_job` ONLY, `profile_id` read straight from the fetch result; NO: create then apply", made the returning=one-tool path primary, and added a precondition STOP at `create_profile`'s entry — i.e. the decision-first checkpoint, not more bans. **KKB outbound 2026-07-16** — the INVERSE: `new_seeker="yes"` (new caller) reached apply and called `apply_job` directly with no `create_profile` → no `profile_id` → apply FAILED. Fixed by strengthening the NO-branch create-first gate to match the YES branch's force, then hardening the same gate **family-wide** across KKB inbound + Maya inbound + Maya outbound new-caller paths (preemptive — same class was latent in all of them).

### C8 — Result set presented in given order; known ranking signals not applied
- **Symptom:** the agent reads a list (jobs, options) in the order the array returned it, leading with an item that does not fit the caller, even though a better-matching item is present and the matching signal (profile role, stated preference) is known.
- **Root cause:** the prompt says the array is "sorted by relevance" (so the agent trusts array order) and/or never tells the agent to re-rank by the caller's known signals; the backend order isn't actually personalised to this caller.
- **Detection:** find where results are presented. Does the prompt (a) assume array order = relevance, and (b) omit an explicit "rank by <caller signals> before presenting"? If a known signal (profile role, stated preference) exists but isn't wired into ordering, flag it — especially when the pool is large.
- **Fix direction:** treat the array as a pool; rank it by the caller's known signals (role → location → salary) before presenting; put the matched items first; do not rely on the given order. When the target isn't known yet, orient first (short overview + one question), then rank.
- **Seen in:** Maya 2026-07-13 (profile role "Data Entry Operator" was known and confirmed, but the list still led with "Customer Support"; fixed by treating `${recommendations}` as a ~30-job pool ranked by role/location/salary and presenting the role-matched job first. Verified on a live `new_seeker="no"` call — Customer Support profile → list correctly led with Customer Support). The **pool-overview opener** for the role-unknown case was added second, only after the fork was live-verified, as **Step 1 Case B** (gated on role-unknown; names only real roles from the pool; explicit guard that it is never the call opener and never replaces the profile-permission question; **no from-greeting example added** — the prior attempt broke the fork precisely via a from-greeting `new_seeker="yes"` overview example, E1). Lesson: a redesign that touches presentation *and* risks a fork should ship in two verifiable steps — the fork-safe ranking first, the opener second, each live-tested on the branch it does not depict.

### C9 — Placeholder / sentinel field value spoken or acted on as if real
- **Symptom:** a fetched field carries a placeholder/sentinel value ("Any", "Not Available", "N/A", a generic "उपयोगकर्ता"/"अज्ञात" name) and the bot speaks it or acts on it as if real — e.g. profile `role="Any"` → "मैं देख रही हूँ कि आप अभी **Any** का काम देख रहे हैं — इसी तरह की जॉब्स?" (a role-confirm on a non-role), which also suppressed the pool-overview the unknown-role path should have given.
- **Root cause:** the "present & non-empty ⇒ KNOWN" rule (**C6**) treats ANY non-empty string as usable, but some fields carry domain sentinels that mean "unset." The empty-check (empty/null/missing) doesn't enumerate those sentinels, so "Any" reads as a real role.
- **Detection:** for each fetched field with a "present ⇒ use/confirm it" rule, check the prompt enumerates the field's **sentinel/placeholder values** ("Any", "Not Available", "N/A", generic names) and treats them as **ABSENT/unknown**, not present. A role/name/etc. that can be spoken or confirmed without a sentinel guard = flag. (Job `role="Not Available"` is already sentinel-guarded in the Variable Presence Rules — the gap is the fetched **profile** fields.)
- **Fix direction:** define the sentinel set per field; treat sentinel = absent/unknown; never speak the sentinel aloud; route on "unknown" (e.g. role unknown → pool overview / Case B, not a role-confirm).
- **Seen in:** KKB + Maya 2026-07-16 (profile `role="Any"` spoken and role-confirmed; fixed to treat "Any"/"Not Available"/empty/null/garbled as NOT a usable role → UNKNOWN → skip role-confirm → Step 1 Case B pool overview, surfacing the job-type summary upfront).

---

## D. Language, script & voice

### D1 — Hard/Sanskritised vocabulary despite a "simple language" rule
- **Symptom:** agent says tatsama/administrative words (सेवा प्रदाता, प्रशिक्षण, पुनर्वास, मूल्यांकन…) over a low-literacy voice channel.
- **Root cause:** only an abstract instruction ("use simple words / no technical terms") with **no concrete banned→preferred lexicon**. Abstract rules underperform explicit lists.
- **Detection:** if the prompt says "simple language" but has no do/don't substitution table for domain vocabulary, flag it. Bonus: scan the prompt's own spoken lines/examples for hard words it fails to gloss.
- **Fix direction:** add a substitution table + the rule "prefer the common English/Hinglish loanword over the pure-Hindi equivalent"; use the gloss pattern ("विकलांगता यानि डिसेबिलिटी").
- **Seen in:** Purple Dots review; general to all agents (each relies on explicit banned-phrase lists).

### D2 — TTS number/date/time/money not spelled as words
- **Symptom:** TTS mangles digits, `₹`, AM/PM, DD/MM/YYYY, phone numbers.
- **Detection:** confirm a TTS-normalization section exists AND that examples obey it (numbers as words, money in words, सुबह/दोपहर/शाम/रात not AM/PM, phone digit-by-digit). Flag any digit/`₹`/AM-PM/short-date in a spoken line or example.
- **Fix direction:** enforce word-spelling; fix offending examples.
- **Seen in:** all agents (standing TTS rules).

### D3 — Script separation: conversation vs payload
- **Symptom:** Devanagari leaks into API payloads, or Roman/Latin Hindi leaks into spoken output.
- **Detection:** confirm the prompt states (a) all TTS output = Devanagari (no Roman/mixed Hindi), and (b) all payload values = English/Latin, with transliteration rules for names/addresses. Flag missing/weak either side.
- **Fix direction:** restate the strict boundary + transliteration examples.
- **Seen in:** all agents (payload script-separation rule).

### D4 — Voice-gender inconsistency
- **Symptom:** a female-persona agent uses masculine verb forms (or offers both).
- **Root cause:** no explicit feminine-only rule, and/or a line offering "…रहा हूँ/रही हूँ".
- **Detection:** if persona is female, confirm an explicit "feminine verb forms only" rule and scan for any masculine form or "रहा हूँ/रही हूँ" dual-option.
- **Fix direction:** add the feminine-voice rule; remove masculine options.
- **Seen in:** Maya (explicit feminine-voice divergence); Purple Dots review (§7 "समझ रहा हूँ/रही हूँ" on a female persona).

### D5 — Modality leak (outbound bot invites callbacks)
- **Symptom:** an outbound (bot-calls-user) agent ends with "you can call me / call back when you need."
- **Root cause:** modality is declared once at the top but there's no closing script and no ban on inbound-framed language; the model falls back to trained call-center endings.
- **Detection:** if modality = outbound, confirm (a) a fixed Graceful-Exit/closing script and (b) an explicit ban on "call me/us back"-type phrasing. Bare "close the call" with no script = flag.
- **Fix direction:** add a closing script matching the true modality (e.g. "the center will contact you") + prohibition on callback phrasing.
- **Seen in:** Purple Dots review.

### D6 — Symbol/punctuation voiced literally (e.g. "/" read as "slash")
- **Symptom:** the bot speaks a punctuation symbol out loud — most often "/" pronounced "slash"/"स्लैश"/"ಸ್ಲ್ಯಾಶ್" when reading a role/category label ("सेल्स/मार्केटिंग", "कस्टमर सपोर्ट/बीपीओ") or a rate.
- **Root cause:** the prompt writes labels/values containing "/" and the TTS-normalization section either lacks a slash rule or has only a generic one that never mentions the role/category labels the bot actually forms, so the model emits the literal "/".
- **Detection:** grep the prompt for "/" inside spoken lines, pool-overview groupings, and inventory role labels ("X / Y", "A/B"). If any exist, confirm a TTS rule that (a) bans voicing "/" and (b) shows the role/category-label conversion to "या"/"ಅಥವಾ" (or the per-form for rates). A bare "speak / as या" one-liner that does not cover labels = flag.
- **Fix direction:** add/strengthen a "## Slash ( / ) symbol" rule with concrete label examples; never voice the symbol. Applies to every spoken-output prompt (inbound + outbound, both languages) — cross-agent.
- **Seen in:** KKB/Maya inbound live calls, 2026-07-17 (Consolidated Feedback rows 65/73).

### D7 — Inbound get_profile fork not hard-gated (fetch skipped / deferred / replaced with a permission-ask)
- **Symptom:** on an INBOUND (get_profile-driven) agent, the new-vs-returning fork misfires — the bot skips `get_profile` and jumps to discovery/jobs when the caller volunteers a role/city, defers the fetch behind a discovery turn, or invents a "can I fetch your profile?" permission-ask before finally calling it. The branch-on-result is usually correct; the fetch itself is the failure.
- **Root cause:** the inbound fork is written as soft prose ("As your first action, silently call get_profile") with no hard gate — unlike the outbound `new_seeker` DECISIVE ROUTER. Nothing forbids conversation/jobs before the fetch returns, and nothing forbids skipping when the caller front-loads a role/city.
- **Detection:** on any inbound/get_profile-driven prompt, confirm the fetch instruction is a HARD gate: (a) "NO conversation/jobs/permission-ask before it returns" and (b) "never skip if the caller volunteered a role or city." A bare "silently call get_profile first" with neither clause = flag.
- **Fix direction:** wrap the fetch in a DECISIVE ROUTER mirroring the proven outbound router — first action, real tool call, no conversation before it returns, never skip. Language-agnostic (verbatim across H/K).
- **Seen in:** KKB Placeholder Inbound + Maya Inbound live calls, 2026-07-14/17 (Consolidated Feedback rows 71/78; related: outbound profile-not-found path must still route to the Case-B pool overview, and the new-caller path must gate name+experience before create_profile — rows 74/80, 67/72).

### D8 — Internal technical term ("profile") spoken to the caller
- **Symptom:** the agent says an internal system word out loud — "profile"/"प्रोफाइल"/"ಪ್ರೊಫೈಲ್" — in the permission-ask, the found/not-found acknowledgement, or an example dialogue (e.g. "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?", "प्रोफ़ाइल मिल गई"). Callers don't understand the term and it erodes trust.
- **Root cause:** the prompt's OWN spoken lines/examples use the internal term, and there is no rule mapping it to a caller-friendly word.
- **Detection:** grep the prompt's spoken lines + `> **Agent:**` examples for internal system nouns ("profile", tool names, "payload", "database", "fetch", "id"). Any such word in a line the caller hears = flag. Then confirm a "never speak <term> aloud; say <friendly word> instead" rule exists.
- **Fix direction:** add a wording-rules section that bans the term aloud and gives the friendly replacement ("जानकारी" / "ಮಾಹಿತಿ" for profile), reconcile every spoken/example line, and on an empty fetch never announce the miss. Keep internal tool names + rule text unchanged.
- **Seen in:** KKB + Maya get_profile prompts, 2026-07-19 (Profile Wording Rules).

---

## E. Examples, consent & standing rules

### E1 — Few-shot examples contradict the rules (incl. cross-branch opening bleed)
- **Symptom:** the agent does the thing the prose forbids / skips a mandatory step. Special case: a control variable (e.g. `new_seeker`) is supposed to pick between two different openings, but the agent uses the wrong branch's opening — because an example modelled it.
- **Root cause:** an example models the shortcut/opening. Models mimic concrete examples over abstract prose, even with a "don't mimic examples" disclaimer. When two branches have different openings, an example for one branch bleeds into the other unless the branch variable is the decisive router AND every example is labelled with its branch value. **Adding a new example (or a salient new section) to lock in feature X can silently regress a working branch Y.**
- **Detection:** walk each example against the mandatory flow. Any example that skips a "mandatory" step, contradicts a canonical spoken line, uses a different greeting, or contains garbled text = flag. When a control variable selects between openings/paths, confirm EVERY example states its variable value in context and that no example's opening could be copied onto the other branch. Count how many examples model each opening — a lopsided majority pulls the model that way regardless of the branch value.
- **Fix direction:** repair examples to model the mandatory path and match canonical lines. For branch-conditioned openings, make the branch variable the **decisive router** (explicitly forbid each branch's opening on the other side) AND label every example with its branch value. **After adding any example, re-test the OTHER branch — the branch it does not depict is the one at risk.**
- **Seen in:** KKB/Maya (feature/behaviour patterns learned from examples); Purple Dots review (Example 1 skips Solution Enablers; Ex 2 greeting garbled + skips `get_profile`); Maya 2026-07-13 (adding Example 5 — a `new_seeker="yes"` pool-overview walkthrough — plus a salient Step 1 overview made the model open EVERY call, including `new_seeker="no"`, with the experience question + overview and skip the mandatory profile fetch; a "no" call that worked one test earlier regressed the moment the competing "yes" example landed. Fixed with a decisive new_seeker router forbidding the yes-opening on the "no" path + labelling every example's new_seeker value + **removing the competing from-greeting "yes"-overview example** (prose gates alone did not overpower it — the example itself had to go; the overview behaviour stayed in prose)).

### E2 — Consent handling: multiple gates, single-ask, hard-stop on decline
- **Symptom:** consent re-asked (see B1), or a decline doesn't cleanly stop the flow, or two different consents (recording/data vs sharing) get conflated.
- **Detection:** enumerate every distinct consent gate. For each: is it asked exactly once, and is there a clear "on decline, gently stop and make no tool calls" hard-stop? Are distinct consents kept distinct?
- **Fix direction:** one ask per gate, explicit decline hard-stop, distinct wording per gate.
- **Seen in:** Purple Dots review.

### E3 — Memory-injection block missing (repo standing rule)
- **Symptom:** a memory-enabled agent doesn't receive per-caller context.
- **Root cause:** the conversation prompt lacks the exact `### Contact context / Here is the caller context: / {${contact_memory}}` block required by repo `CLAUDE.md` for any agent with memory enabled.
- **Detection:** if the agent has (or should have) a memory prompt, confirm the block is present **verbatim** in every language file. Distinguish a live-profile fetch (`get_profile`) from cross-call memory — if only the former exists, flag as **Verify** (confirm whether cross-call memory is intended).
- **Fix direction:** route to `/update-memory` to add the block.
- **Seen in:** repo `CLAUDE.md` rule; DKB 2026-06-29 (block was missing, added).

### E4 — Guard sections thin or absent
- **Symptom:** unsafe/off-scope handling, missing age/eligibility hard-stop, options that aren't physically realistic for the disability/context.
- **Detection:** confirm presence of: forbidden-topics list, dignity/safety check, eligibility/age hard-stop, relevance + functional-sanity rule (options realistic for the stated condition), and a scope-boundary list (what the bot must never promise/do).
- **Fix direction:** add the missing guard.
- **Seen in:** standard across agents; sanity-check formalized in Purple Dots review.

---

## F. Cross-language (pointer)
Drift between an agent's Hindi and Kannada files (AGNOSTIC logic landing in one language only)
is its own audit — **don't reimplement it here.** This skill reviews one file. For parity, run
`/sync-check`. Flag only: "this change looks language-agnostic and should be sync-checked
against the twin."

---

## G. Templating & variable interpolation

### G1 — Variable placeholder precedes its label in a binding phrase (garbles after interpolation)
- **Symptom:** a branch/decision that depends on a control variable behaves as if the value were missing or wrong, even though the variable is passed correctly. Structural fixes, hard gates, and case-normalization all fail to help — because the value never actually binds.
- **Root cause:** the prompt binds the variable with the **placeholder first**, e.g. `Consider ${new_seeker} as new_seeker.` At runtime `${new_seeker}` is interpolated to its value, so the model literally reads **"Consider no as new_seeker"** — the value is presented *as if it were the label*, so "new_seeker = no" is never established. The model is left with no clean value and falls through to a default / natural-conversation path.
- **Detection:** scan for any binding/assignment phrase where a `${VAR}` placeholder appears **before** its human-readable label — `Consider/treat/use/read ${X} as X`, `${X} as x`, etc. Mentally interpolate it: does it still read as "x = <value>"? If it reads backwards ("<value> as x"), flag it — **critical** for any variable that drives a branch (new_seeker, flags, modes), lower for glossary lines that have a description to disambiguate.
- **Fix direction:** put the **label first, placeholder last** — `Consider new_seeker as ${new_seeker}` → interpolates to "Consider new_seeker as no" (binds cleanly). General forms: `<var_name> is ${VAR}` / `<var_name> = ${VAR}`.
- **Seen in:** Maya 2026-07-13 (`Consider ${new_seeker} as new_seeker` interpolated to "Consider no as new_seeker"; the `new_seeker="no"` branch never fired until the order was flipped to `Consider new_seeker as ${new_seeker}`. This — not the section deletion or gates — was the actual fix). **KKB 2026-07-13** — same backwards binding found in both `KKB Placeholder Hindi.md` and `Kannada.md` (two places each: the Contact-Variables glossary line and the Profile-Handling step) once the fork was reported broken there too; flipped both to `Consider new_seeker as ${new_seeker}` and simultaneously fixed a co-located **A4** header/body contradiction ("caller already has a profile" vs "MANDATORY … IF USER PROFILE DOES NOT EXIST"). **Lesson:** when this bug is confirmed in one agent, grep every sibling for the same `Consider ${VAR} as VAR` pattern immediately — it had been catalogued as "latent in KKB" for days before the fork broke in production.
