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
- **Seen in:** Maya 2026-07-08 (Experience Capture ran before `get_profile` until it was forbidden as the first post-greeting action); Maya 2026-07-13 (the `new_seeker="no"` branch *still* bypassed `get_profile` despite that HARD GATE, because the standalone `## Experience Capture` section was the salient next action — fixed only by deleting the section and inlining gathering into the branch, mirroring KKB, which has no such section).

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

---

## B. Repetition & loops

### B1 — One-time utterance/consent fired repeatedly
- **Symptom:** a bridge line, a consent ask, or a confirmation is spoken/asked several times in one call.
- **Root cause:** a one-time action is attached to a per-entity loop ("do X once for each provider/job") or re-triggered each turn, with no "exactly once" bound.
- **Detection:** find every "for each …" / multi-entity action and check whether any spoken line or consent is inside that loop. Find every consent/bridge line and confirm it has an explicit "say/ask **once**" bound. Multiple backend entities (N providers, N jobs) + one human-facing action = high-risk.
- **Fix direction:** "Ask/say once; on a single confirmation, loop the tool calls **silently**." Separate the human-facing ask from the per-entity backend loop.
- **Seen in:** Maya 2026-07-08 (apply bridge spoken 3–4× per apply); Purple Dots review (share-consent asked per provider).

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
- **Detection:** for each payload, trace every value to its source. Check coordinate order (GeoJSON = `[lng, lat]`), check field names match the schema exactly, scan for stray/unbalanced brackets in `${...}`, confirm identifier **formats** match what the target store expects (phone with/without `+91`) **and that a write (create) and its later read (fetch/lookup) use the same format**, and flag any hardcoded id that contradicts a dynamic search in the same flow.
- **Fix direction:** correct the mapping/format; make create and lookup use the identical key format; reconcile hardcoded vs dynamic.
- **Seen in:** DKB 2026-06-29 (`${phone(number}` → `${phoneNumber}`, `workExperienceYears`); Maya 2026-07-13 (`get_profile`/`create_profile` passed the bare number → ~14/80 empty fetches; fixed to `+91`-prefixed on both); Purple Dots review (lat/lng swap; hardcoded provider `item_id`).

### C4 — Fixed-param / enum integrity
- **Symptom:** downstream system rejects the payload or mis-routes.
- **Root cause:** a fixed param drifted (`sourceService`, `eventType`, `app_instance`, `network`, `item_type`), or an enum field was populated in the wrong language / with a value outside the allowed set.
- **Detection:** verify every "always use this exact value" param is present and unchanged. For every enum field, confirm the prompt constrains it to the exact allowed strings **in English/Latin** and forbids the conversational-language version.
- **Fix direction:** restate the fixed value and the strict enum list at the payload.
- **Seen in:** DKB (fixed params `ONESTAGENT`, `app_instance`); Purple Dots (`disability_type`/`looking_for`/`documents_available` enum + English-only rule).

### C5 — Outcome narrated without the tool actually running/succeeding (hallucinated success)
- **Symptom:** the agent says the action succeeded ("अप्लाई हो गया") but the tool was never called, or was called and errored.
- **Root cause:** the success message is a canned line with no rule binding it to an actual successful tool result; the model emits it from memory — often right after a *preceding* tool (e.g. `create_profile`) while skipping the real terminal action (`apply_job`).
- **Detection:** for every "success" spoken line, check for an explicit rule "speak this ONLY after <tool> was actually called AND returned success; otherwise use the failure line." Also confirm the terminal tool is stated as always-called (not optional). Missing either = flag.
- **Fix direction:** gate the success line on a real successful result; state the terminal tool must actually run every time; on error / no-call, use the failure path.
- **Seen in:** Maya 2026-07-13 (`apply_job` never fired but "अप्लाई हो गया" was spoken after `create_profile`).

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

---

## E. Examples, consent & standing rules

### E1 — Few-shot examples contradict the rules
- **Symptom:** the agent does the thing the prose forbids / skips a mandatory step.
- **Root cause:** an example models the shortcut. Models mimic concrete examples over abstract prose, even with a "don't mimic examples" disclaimer.
- **Detection:** walk each example against the mandatory flow. Any example that skips a "mandatory" step, contradicts a canonical spoken line, uses a different greeting than the defined one, or contains garbled text = flag. Also check place/person-name localization for the target language.
- **Fix direction:** repair examples to model the mandatory path and match canonical lines.
- **Seen in:** KKB/Maya (feature/behaviour patterns learned from examples); Purple Dots review (Example 1 skips Solution Enablers; Ex 2 greeting garbled + skips `get_profile`).

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
