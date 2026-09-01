---
name: voice-test
description: Run agent-to-agent voice tests of a Raya bot using a persona "tester" agent, then grade the call MECHANICALLY against a standard grader contract — universal invariants on every call, script-aware matching, scoped prohibitions, fixture-hygiene checks, and call ids read from the run log rather than inferred. Use to reproduce a reported bug, verify a fix end-to-end, or regression-test scenarios before a demo.
---

# Voice Test — agent-to-agent call testing

Test a live Raya voice bot by having a **tester/persona agent** role-play a human, receive a call
from the **bot under test**, and grading the resulting transcript **against assertions, not
impressions**. This is how we find bugs ourselves instead of asking the user to place every call by
hand.

Two halves, and they are separate steps: **running** a call (§Run) and **grading** it (§Grader
contract). The runner does no grading. A dump that looks like a report is not a report.

## The setup (topology)

- **Tester agent** — an INBOUND agent whose single prompt is a *persona* (a human the bot talks to).
  Current tester: **"Testing Agent- Blue Dots"**, uuid `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`,
  inbound DID **`917946350285`**. It is set **non-interruptable** and **max_call_duration = 5 min**
  (bot agents are capped at 15 min by the API; the tester stays at 5 — set 2026-08-01 by Parth,
  superseding the earlier 4-min cap). Its persona is swapped by PATCHing its `instructions`.
- **Bot under test** — an OUTBOUND agent (e.g. KKB Hindi Signals `115b38a5-…`). It is *triggered* to
  place a call to the tester's DID; it runs its real prompt + real tools.
- We then read BOTH call legs and grade the bot.

## Prerequisites

- `raya/.env` (RAYA_BASE_URL, RAYA_API_TOKEN) — never commit.
- `scripts/raya_testcall.py` — `persona` (swap the tester's script), `lang hi|kn` (switch the
  tester's language+voice), `call` (fire one call), `whoami`.
- `scripts/raya_testrun.py` — fire ONE call + poll to completion + dump the **RAW** transcript
  (connect-retry built in). **Grading is a separate, mandatory step** — this script contains no
  assertions.
- `scripts/raya_call.py` — read past calls/transcripts for any agent, **including tool-call
  arguments** (a turn that makes a tool call has `content: null` and the real payload in
  `tool_calls[].function.arguments`).
- **A test manifest.** `raya/testcases/<bot-id>.json`, from `/generate-test-cases`. **Refuse to grade
  a bot that has none** — without it there is no case id, no assertion id, no FAIL SIGNAL, and no
  record of what was never exercised. Run `/generate-test-cases` first.
- Personas: `raya/personas/*.md`. Checklists: `reference/checklists/`.
- Production detectors: `raya/regression/location_integrity.py`, `raya/regression/apply_outcomes.py`
  — the third grading surface (§Three grading surfaces).

## Platform reality (learned the hard way — respect these or waste calls)

1. **Trigger:** `POST /api/call` with `agent_id` = **bot under test**, `to_number` = the tester's
   **10-digit** DID (`7946350285`; the `91` is prepended via `country_code`), `agent_args` = the
   bot's inputs. **OMIT `out_did`** — passing it explicitly gave `Unanswered`; omitting connects.
2. **Call creation is rate-limited** (~1 per ~13 s → HTTP 429 with `retry_after`). Space fires ≥ ~15 s.
3. **Bridging is intermittent** — a large fraction of dials fail instantly (`outcome`
   Failure/Unanswered, `dur=0`, no transcript). Flaky telephony, NOT a bug in the request. **Retry
   the connect** (the runner does, with a ~45 s cooldown). A burst of rapid calls degrades bridging.
4. **`GET /api/call/{uuid}` LAGS** after a call — `Pending`/`dur=0` for a while before the transcript
   + `call_output` finalize. Keep polling (the runner does).
5. **The tester (callee) receives NO `agent_args`.** `POST` args reach the `agent_id` (the bot) only.
   You **cannot** select a scenario per call via an arg — pick the persona by PATCHing the tester.
6. **The bot looks up the DIALED number** (`${contact_phone}` is bound to `to_number`), i.e. the
   tester DID — *not* whatever phone you pass in `agent_args`. So the backend identity the bot sees is
   always the tester DID; you cannot choose which record the read tool returns. Provision the record
   you want under that number. **Signals has no delete route** — a number cannot be reset to "new"
   once a record exists, so every "new caller" assertion on the shared DID is one-shot forever.
7. **`contact_memory` is platform-injected** when `memory_enabled` — it is not in `agent_args` and
   cannot be set per call. Assertions that depend on it are `UNGRADEABLE — input not observable`.
8. **A TTS tester cannot mumble.** Asked to be unintelligible it either speaks clearly or goes
   silent. ASR-garble rungs are not voice-testable.
9. **Each (record, target) action pair is single-use.** A repeat returns the limit error — a gift for
   the error arm, a blocker for the success arm.
10. **Target ids are instance-scoped.** A stale id yields a not-found error and looks like a bot bug.
11. **Payloads have arrived TRUNCATED at exactly 1023 chars** (analyser `D42`) from the campaign
    layer. Check the delivered args before blaming the bot.

## Concurrency (for running a batch faster)

- **Parallel calls DO bridge** — multiple calls to the tester DID overlap in time (verified).
- **BUT one tester = one persona at a time** (single prompt, no per-call arg). So you can only run the
  **same** scenario in parallel on one tester. For **different** scenarios in parallel you need **one
  tester agent per scenario** (each its own inbound DID + persona), then fan calls across them. K
  testers turn N serial calls into ~N/K wall-clock — this is the right way to afford a large suite.
- **Two test waves must never overlap on one tester.** A wave whose wait-loop watched only its own
  runs once started during another wave's gap and PATCHed the tester's persona out from under an
  in-flight call. See §Fixture hygiene, clause 5 (persona lock).
- Default to **sequential** on a single tester (PATCH persona → run → grade → next).

## Run ONE test

```bash
# 1. Load the persona onto the tester (swaps its prompt)
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<persona>.md
# 1b. Match the tester's language + voice to the bot under test
python3 scripts/raya_testcall.py lang <tester_uuid> hi|kn
# 2. Fire + poll + dump the RAW transcript  (grading is step 3, and it is not optional)
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "<case-id>-<target-id>"
```

`<args.json>` = the bot's `agent_args`, from `raya/testcases/args/` (one fixture per input-state
equivalence class) or copied from a known-good past call via `scripts/raya_call.py <bot_uuid>`.

**Always pass a real `<case-id>-<target-id>` as the label** — it is the only thing tying the call to
the manifest.

**The dump is lossy.** `raya_testrun.py` truncates turn content at 600 chars (tool results included,
so a failure reason code can be cut off) and never prints `agent_args`. **Grade from the full call
JSON, never from the printed dump:** `python3 scripts/raya_call.py <bot_uuid> 3` or
`GET /api/call/{uuid}`, and persist it (§Provenance).

---

## Grader contract — MANDATORY

**A grading result produced without this contract is void.** Five clauses.

### 1. Assertion form

Every checklist item and every manifest case becomes a record with a **stable id**:

```
{ id, scope: universal|bot|scenario,
  source: transcript|tool_args|tool_result|call_output|agent_args,
  matcher, pass_condition, FAIL_SIGNAL, scope_turns, compare, evidence_required }
```

- **`FAIL_SIGNAL` is the literal thing that proves failure** — a token, a count, a missing key — not
  the inverse of the pass criterion. Grading is two-sided. A grader that knows only what *should*
  happen scores a call "pass" when the mandated line appears and misses the forbidden line that
  appeared alongside it.
- An item that cannot be written this way is **not a grading item.** It moves to the checklist's
  `## Observations (not graded)` block, is reported as commentary, and **may never produce PASS or
  FAIL**. "Nothing implied the caller was a burden", "not an abrupt cut and not an endless tail",
  "did not derail into an extended off-topic exchange" — these are observations. Honest observation
  beats a fake PASS, and a run full of impressionistic passes drags the mechanical items down to the
  same register.
- Mechanise what can be mechanised: "two questions in one turn" → counted interrogative markers with
  the mandated tag-question forms on an allow-list; "off-topic derail" → *N consecutive bot turns
  containing no token from the current step's mandated line set*; "verbatim repeat" → normalised
  string-equality count with the legitimate re-prompt lines enumerated per bot.

### 2. Verdict states — five, not two

`PASS` · `FAIL` · `NOT_EXERCISED` · `VOID` · `INPUT-INVALID`

- **`NOT_EXERCISED`** — the call never reached the state. A PASS whose evidence is "nothing found"
  **is** `NOT_EXERCISED`. Folding it into PASS is precisely why untested sections looked green.
- **`VOID`** — ungradeable (fixture contaminated, persona changed mid-call, prompt sha mismatch). An
  ungradeable call is **not** a passing call.
- **`INPUT-INVALID`** — the input pre-assertions failed; the bot is not at fault. This is the
  mechanical form of the repo's "push back before fixing" rule.
- A **universal invariant** may return PASS, FAIL or VOID — **never** `NOT_EXERCISED`. If it cannot
  be evaluated, the call is VOID.

### 3. Evidence — no locator, no verdict

Every emitted verdict carries `{call_uuid, turn_index, exact_substring}` or
`{call_uuid, tool_call_index, tool_name, arg_path, arg_value}`. A verdict with no locator is not
emitted. "The bot handled it correctly" is not evidence; `turn 19: "…"` is.

### 4. Normalisation before any match

See §Script-aware matching. A match run on raw strings is not a match.

### 5. Result schema — results are files, not prose

```
raya/testcases/results/<bot>/<run-id>.json
{ run_id, bot_target_id, prompt_sha, deployed_sha, started_at,
  cases: [ { case_id, persona, persona_sha, args_file, call_uuid,
             fixture_pre, fixture_post, fixture_delta,
             verdicts: [ { assertion_id, state, evidence } ] } ] }
```

`prompt_sha` and `deployed_sha` **must match** or the whole run is `VOID` — a run graded against a
prompt that is not the deployed one is worthless. Roll up to
`raya/testcases/results/<bot>/coverage.json`: per assertion id — last state, last call uuid, run
count, consecutive-pass count, `last_exercised_at`. **An assertion with `last_exercised_at: null` is
the coverage report.** Feed the rollup into the Tier-3 digest so "N assertions not exercised in 30
days" is mailed rather than discovered in production by a human tester.

> **Tooling status, stated honestly.** `grade_call.py`, `textnorm.py` and `fixture_state.py` do not
> exist yet; `raya/regression/location_integrity.py` and `apply_outcomes.py` are the working proof
> that this is buildable in ~150 lines each, and both caught real defects that prose grading missed.
> Until the scripts land, do every clause of this contract **by hand and write the result JSON
> anyway** — the artifact is the point. Build them the first time a run needs more than one pass; the
> normalisation table already exists inside `location_integrity.py` and should be extracted, not
> re-typed.

---

## Universal invariants — asserted on EVERY completed call

Coverage must not be a function of what the grader thinks the scenario is "about". Section-scoped
checking is how a missing closing offer survived on apply-success calls (the grader was checking the
apply payload), how a doubled question survived on a gathering-phase call, and how a borrowed
payload value survived on a location-themed call. **These run on every call, automatically, from
machine-readable surfaces only.**

1. Turn 1 is the mandated opener alone (the audio check for outbound `say_hello=false` bots); the
   platform-injected leading `[user] hello` is ignored.
2. Recording / AI disclosure present, **in its mandated position**.
3. No `${...}`, `{`, `}`, JSON fragment, field name, tool name or UUID in any spoken turn.
4. No digits, `₹`, AM/PM, or a literal `/` spoken as "slash" in any spoken turn.
5. Spoken script == the call's language; no Latin-script rule prose in speech (borrowing allow-list
   excepted).
6. No banned machinery token **within its declared scope** (masked per §Required boilerplate).
7. The read/lookup tool fires exactly once, before any personal detail is spoken.
8. Every phone-bearing arg is single-prefixed E.164 for that backend; never doubled (`9191…`).
9. Every tool arg value is Latin script; no Devanagari/Kannada in any payload.
10. Every enum-typed arg holds a literal from the live enum set, byte-exact.
11. A create and its dependent action are never in the same turn/batch; the dependent action's
    identifier arg is non-empty and correctly formatted.
12. Every identifier arg matches its format contract (e.g. 8-4-4-4-12 with all four hyphens) **and**
    is present in the delivered `agent_args` inventory — or, for inbound bots, in the prompt's own
    inventory. Resolve the bot family FIRST (cf. `D46`).
13. No spoken success claim without a matching successful tool result in the same or a prior turn.
14. No profile-write value (`location`, `role`, `age`) the caller did not say aloud — script-aware
    (this is `location_integrity.py`'s rule, and a third party's city is never the caller's city).
15. Every mandated say-once line occurs **exactly once** (normalised equality).
16. The mandated closing offer present on any engaged call, absent on do-not-call / never-engaged.
17. Every mandated pre-goodbye step completed before the closing turn; goodbye last and once.
18. `call_output.drop_reason` / `call_outcome` consistent with the transcript's terminal event.
19. Every `call_output` field the output prompt declares is populated or explicitly `NA`; no field
    populated from an input variable the caller never spoke.
20. `agent_args` sanity: parses as JSON, **not exactly 1023 chars** (`D42` truncation), no phantom
    args beyond the declared set, no sentinel values passed through as real ones.
21. `deployed_sha == prompt_sha`.
22. Fixture pre/post recorded (§Fixture hygiene).

**Per-scenario assertions** are the only ones allowed to be `NOT_EXERCISED`: the specific branch
taken, the specific tool error provisioned, the specific line under test, the reported-bug
reproduction. They carry the `FAIL_SIGNAL` from the manifest case.

---

## Script-aware matching (do not skip — this has produced false results in both directions)

The transcript is in-script, the payloads and `agent_args` are Latin, and the prompt itself uses both
spellings of the same borrowed word. Bare substring search fails **two** ways, and both are lethal:
searching the native spelling misses the Latin-spelled mandated line (a real line scored as never
said → the defect stays hidden), and comparing Latin arg values against in-script speech returns
zero matches (→ four bogus CRITICALs in one sweep; cf. `D46`/`D49`).

Required pre-steps, before **any** match:

1. **`norm(s)`** — NFC-normalise; strip nuqta variants (गाज़ियाबाद ≡ गाजियाबाद); collapse whitespace,
   ZWJ/ZWNJ; casefold Latin.
2. **`variants(term)`** — generate {native-script form, Latin form, common Latin-in-native
   borrowing}. `option ⇄ ऑप्शन`, `profile ⇄ प्रोफाइल`, `apply ⇄ अप्लाई`, `record ⇄ रिकॉर्ड`. A match
   against **any** variant is a match. The borrowing table already exists as `TRANSLIT` /
   `spoken_forms()` in `raya/regression/location_integrity.py` — extract it to
   `raya/regression/textnorm.py` so there is one table, not two. Its coverage is itself testable:
   every Latin word appearing inside a quoted spoken line in the prompt must have an entry.
3. **Cross-script comparisons are TYPED.** Any assertion comparing a payload/arg value to spoken text
   declares `compare: cross_script` and routes through `variants()`. **A cross-script assertion that
   finds zero matches on both sides returns `INCONCLUSIVE`, never FAIL** — zero-on-both-sides is the
   signature of a broken matcher, not of a silent bot. This one rule kills the whole false-positive
   class.
4. **Transliteration is evidenced.** A FAIL from a cross-script comparison prints both the normalised
   needle and the normalised haystack window, so a matcher bug is visible in the report instead of
   being laundered into a verdict.

## Required boilerplate — the prohibition exclusion list

Prohibitions in these prompts are **scoped** ("never say X *in these lines*", "never read the memory
out"), and the required and the forbidden collide on the same token. Grading a scoped prohibition
globally flags the very line the bot is required to say — e.g. the mandatory recording disclosure
contains `रिकॉर्ड`, which is banned in the acknowledgement lines. That is a FAIL on a correct bot,
and it turns every scoped rule in a long prompt into a false-positive generator.

1. **Scope is part of the assertion.** Every prohibition carries `scope_turns`, resolved
   mechanically: `intro_turn`, `acknowledgement_lines`, `failure_turn`, `phase2_turns`,
   `whole_call`. **The default is NOT `whole_call`** — an assertion with no declared scope fails
   validation and does not run.
2. **Mask the required lines first.** `raya/testcases/<bot-id>/required-lines.json` (generated by
   `/generate-test-cases` from the prompt, not hand-written) lists every spoken line a rule marks
   mandatory: disclosure, audio check, consent line, action bridge, closing offer, read-back. Mask
   every required-line span in the transcript, then evaluate prohibitions **on the masked text only**.
   The same file drives the positive assertions, so the mandatory set is one source of truth and a
   token cannot be simultaneously required and banned without the conflict showing as a build error.
   Regenerate on every prompt change; fail the run if the file is staler than `prompt_sha`.

## Provenance — call ids are READ, never inferred

**Pairing a scenario to a call by ordinal position or recency is banned.** Under concurrent or
retried calls it misattributes evidence, and the failure is undetectable from the report: a
well-formed verdict citing a real call uuid that belongs to a different scenario looks exactly like a
correct verdict. It also corrupts the fixture chain — if you cannot say which call ran which persona,
you cannot say which call mutated the backend record, so every later scenario's interpretation is
guesswork. And the repo rule "the word *fixed* requires a call id" is unenforceable when the id is
inferred.

1. **The runner persists.** `raya_testrun.py` appends one JSON line per attempt to
   `raya/testcases/runs/<run_id>.jsonl` **at the moment of `POST /api/call`**, before any polling:
   `{run_id, case_id, persona_file, persona_sha, args_file, args_sha, bot_target_id, tester_uuid,
   to_number, posted_at, call_uuid_from_post_response, connect_attempt}` — then a second line on
   terminal state with `outcome`, `duration`, `turns`. The `uuid` in the POST response is the
   authoritative binding; it is already available in the script and currently only printed.
2. **The grader reads the log, never the call list.** Resolve the uuid from the jsonl by
   `--run <run_id> --case <case_id>`. Fetching `?agent_id=…&limit=N` and pairing by position or time
   is banned outright.
3. **Tester leg by identity, not `limit=1`.** Search the tester's recent calls for the leg whose start
   time falls inside this call's window **and** whose duration matches; mark
   `tester_leg_uncertain: true` when more than one candidate matches rather than silently picking one.
4. **Persist the full call object** per case at `raya/testcases/runs/<run_id>/<call_uuid>.json`,
   unmodified — `agent_args`, every turn, every `tool_calls[].function.arguments`, every tool result.
   Truncation belongs in the human view only, and the human view marks it (`… [+N chars, see JSON]`).

## Fixture hygiene — pre-state, drift, and voiding

The tester DID's backend record **mutates as tests run**: role, age, location get overwritten by the
bot under test, so later scenarios silently inherit earlier ones' writes. This is asymmetric and
therefore dangerous — drift produces **false FAILs** (the bot answered correctly against a record the
persona doesn't match) *and* **false PASSes** (the bot skipped a question because a previous test had
already written that field, indistinguishable from correct "don't re-ask known fields" behaviour).
Both have happened. State the facts is not enough; this is a procedure.

1. **Pre-state, every call, before firing.** Read the record out-of-band (the bot's own read tool via
   the backend API, *not* via a call) and store the full response as `fixture_pre` with a
   `fixture_sha`.
2. **Post-state, every call.** Re-snapshot immediately after terminal state; store `fixture_post` and
   the computed `fixture_delta` (fields written, by which tool, with which value). The delta is a
   first-class result — it is how you learn what this call did to the next one.
3. **Precondition declaration.** Every manifest case declares
   `requires_fixture: {record_state: none|draft|live, role, gender, location, actioned_targets_excludes: […]}`.
   Compare it against `fixture_pre` **before** grading. Mismatch → every verdict in that case is
   `VOID (fixture-contaminated)` with the offending field named. VOID is never reported as FAIL and
   never as PASS; re-run after restoring the fixture, or reclassify as fixture-blocked.
4. **Ordering is derived, not remembered.** Sort a wave by fixture destructiveness:
   `record_state: none` cases **first** (one-shot forever — no delete route), then `draft`, then
   `live`, then the enrichment cases that overwrite fields, then the action cases (each (record,
   target) pair is single-use). **Refuse to fire a `record_state: none` case when `fixture_pre`
   already shows a live record** — firing it and grading the wreckage is worse than skipping it.
5. **Persona lock.** Record `persona_sha` at fire time; re-read the tester's live `instructions` at
   terminal state. If the sha changed mid-call, the case is `VOID` (another wave PATCHed over it) —
   and VOID is *reported*, not silently retried.
6. **`fixture_blocked` is a declared outcome, not an omission.** When a precondition is unreachable on
   this harness (new-caller gates on a DID that already has a record, a specific stored value,
   per-record `contact_memory`), mark the case `fixture_blocked: <reason>` and **name its substitute
   route** — a production detector, a human call, or a platform ask. List blocked cases explicitly in
   the report. Silently dropping them is how "cannot test Fix A" became "Fix A untested and
   unmentioned".
6b. **Which record the bot picks is NOT `items[0]` — it is the most COMPLETE live one.** Learned the
   hard way on 2026-09-01: to force an `ACTION_LIMIT_REACHED` I pre-applied (via the backend API) the
   pair `(items[0], job)` on the tester DID, on the strength of the prompt's own rule ("the first item
   whose `lifecycle_status` is `live`"). The call then applied as `items[1]` — the profile carrying a
   real name, age and role — the duplicate never occurred, and the apply SUCCEEDED. The test proved
   nothing and looked like a pass. **Before any fixture precondition that names a specific record,
   determine empirically which record the bot actually selects** (fire one throwaway call and read the
   `profile_id` out of its `apply_job`/`update_profile` arguments), and pin the precondition to THAT
   id. Where a DID carries several live records, expect the choice to follow completeness, and record
   the observed `profile_id` in the manifest case so the next run does not have to rediscover it.

6c. **An `agent_args` precondition is easier than a backend one — but `contact_memory` is NOT proven
   authoritative, so do not treat it as a controlled variable.** Expressing the duplicate-application
   precondition as `contact_memory: {"jobs_applied": [...]}` in the args fixture is far cheaper than
   arranging a real prior application on a shared record, it is per-call, and it leaves no residue on
   the DID. Prefer it. **But the value you send is recorded in `agent_args` and is not necessarily what
   the model reads.** On 2026-09-01, call `6620c025` was sent
   `contact_memory: {"session_count": 1, "last_conversation_summary": "First contact. No location
   details captured yet."}` and the bot nonetheless opened with an accurate callback clause about a
   previous conversation; `9cb137ed` was sent `"No Old Memory…"` and did the same. Two readings fit and
   they have different fixes: either the platform's own stored memory reaches the model alongside or
   instead of the arg (the `contact_phone` pattern), or the bot inferred "we spoke before" from the
   FETCHED PROFILE, which its own rules forbid. **Discriminate before you rely on either:** send a
   fixture containing a fact the platform memory cannot possibly hold — a fabricated role or company
   the DID has never discussed — and see whether the bot voices it. Until that is settled, a test whose
   verdict depends on memory content must say which reading it assumed, and a memory-gated SKIP is
   better proven by the production shape (omit `contact_memory` entirely and let the platform inject)
   than by a fixture.

7. **Standing escalation.** One DID means one shared history. The ask is **additional tester DIDs,
   one per fixture class** (never-recorded, live-recorded, draft-recorded). Until then, state in
   **every** report that new-caller assertions are permanently unreachable on the shared DID.

## Input pre-assertions — run before behaviour is graded

Failing these classifies the call `INPUT-INVALID`; it does **not** produce a bot FAIL. This is
"the prompt is fine, the inputs were wrong" as a **computed** verdict instead of a judgement call.

- The delivered inventory/recommendations arg parses as JSON, and `len(arg) != 1023` (`D42`).
- Every identifier in it resolves on **this variant's** region instance.
- No phantom args beyond the declared set; no sentinel (`"Any"`, `"NA"`, `"Not Available"`,
  unsubstituted `${…}`) sitting where a real value belongs — and, if one is there, the assertion
  under test becomes "the bot did not speak it", not "the bot mishandled it".
- Where a required input is platform-injected and unreadable (`contact_memory`), the affected
  assertions are marked **`UNGRADEABLE — input not observable`** in the checklist itself, so they stop
  looking like checks that pass.

## Three grading surfaces

Every assertion declares `graded_by`:

| surface | when | contract |
|---|---|---|
| `harness` | reachable by a tester call | this skill |
| `static` | provable by reading the prompt / tool schema | Tier 0; runs **first** and blocks the live run |
| `production_detector` | precondition unreachable on the harness | a `raya/regression/` script over real traffic — `--since`, exit 1 on violation, prints call uuid + evidence line |
| `human_call` | genuinely untestable by TTS (garble rungs) | a person dials; say who and when |

**A blocked assertion with no route is an open gap with its own id, reported — never omitted.** The
harness limits each silently delete a set of assertions; with no routing rule the deletion is
invisible and reads identically to a pass.

`raya/regression/location_integrity.py` (a profile written with a location the caller never gave) and
`raya/regression/apply_outcomes.py` (which caller-facing line was spoken on each backend failure
reason) are the two working detectors. Generalise new ones into `raya/regression/detectors/` sharing
`textnorm.py` and one call-fetch helper — both current scripts duplicate the env loader, the fetcher,
the target enumeration and the paging loop, so a third should be a 40-line file. **Register every
detector in the Tier-3 daily job** and cite it in the report next to the harness rows:
`graded_by: production_detector | last run | violations`. That is what makes "the harness cannot test
this" an answer rather than an excuse.

---

## Report contract

### 1. Per-fix rows, never a batch verdict

One row per fix, never per deploy:

```
| fix_id | state | call_uuid | evidence (exact line or arg) | variant |
```

`state` ∈ `CONFIRMED | FAILED | VOID | NOT_EXERCISED | FIXTURE-BLOCKED | DEPLOYED, NOT VERIFIED`.

A fix with no `call_uuid` may only be `DEPLOYED, NOT VERIFIED` or `VERIFY-PENDING`. The words
"fixed", "working", "done", "confirmed", "resolved" are **lexically forbidden** on such a row. The
same row text goes into the changelog, the commit message, and what you tell the user — the three
cannot diverge. **When several fixes ship together, each needs its own call id**; one passing call
does not verify the other three.

### 2. Evidence is the line, not a paraphrase

Quote the exact substring or `arg_path=value`, with the turn index.

### 3. Every variant gets its own row

Hindi and Kannada, outbound and inbound, each bot separately. A variant with no call id of its own is
`VERIFY-PENDING` — **never inherited from its twin.** "It works for Hindi so Kannada is fine" is a
recipe for disaster.

### 4. Repeats are mandatory for branching behaviour

Any fix touching a spoken line or a branch runs **N ≥ 3** times on the same persona, same args, same
fixture class. Report `k/N`.

- `k == N` → `CONFIRMED`
- `k == 0` → `FAILED`
- `0 < k < N` → **not a result.** Report
  `UNRESOLVED — nondeterministic, ladder step reached: <1-5>` and show the ladder walked, in order.

### 5. "Intermittent" is not a result — the escalation ladder (root `CLAUDE.md`)

Never report a behaviour as "works sometimes", "flaky", "intermittent" or "runtime adherence" and
stop there. That is a description of a defect, not an outcome. If the same prompt, on the same error,
with byte-identical tool results, produces the right line on one call and the wrong line on the next,
**the wrong output is still available to the model.** Walk all five:

1. **Grep the bot's wrong output verbatim against the whole prompt** (`D50`). A hit inside a sample
   conversation is the cause, and it is **proof, not a theory**. Fix the demonstration. This is the
   single highest-yield diagnostic in the catalogue, and it is what finally made a twice-failed fix
   pass on the very next call.
2. **Find the competing instruction and delete or scope it.** A prohibition sitting next to a
   requirement licenses the model to obey the prohibition.
3. **Remove the wrong option instead of forbidding it.** A generic fallback that makes a factual
   claim will be chosen for cases it is false about, however loudly you forbid it. Give every case
   its own mandatory line with no general default, or rewrite the default so it asserts nothing that
   can be false. **Make the worst case truthful rather than trying to make the wrong case
   unreachable.**
4. **Move the decision out of prose** — tool parameter descriptions, `required` fields, enums and
   payload templates are read at the moment of use and are far stickier than rules paragraphs.
5. **Only if 1–4 are exhausted**, escalate to the platform, stating what you tried, the evidence, and
   the change you are asking for — **with both call ids and the diff of the two tool results proving
   they were identical.** "The model ignores it" is not an escalation.

The word "intermittent" without a recorded ladder step is a contract violation. And **never add a
third wording of a guard that has already failed twice** — two failures of the same prohibition is
the signal to change mechanism, not volume (`D25`, `D47`, `D49`, `D50`).

### 6. `NOT_EXERCISED` is printed, always

The report lists every assertion in the bot's set that no call in the run reached, with a count.
`NOT_EXERCISED: 51/92` on the front page is the number that prevents a green report over 27% branch
coverage. **A run cannot be reported green while `NOT_EXERCISED` is non-zero** — it is reported as
*partial*, with the uncovered assertion ids listed, plus `branch_coverage = arms_taken / arms_total`
from the manifest.

---

## Grade the call — the walk

1. **Resolve the call** from `raya/testcases/runs/<run_id>.jsonl` by case id. Fetch the full JSON.
2. **Check `deployed_sha == prompt_sha`** and `persona_sha` unchanged → else `VOID`.
3. **Input pre-assertions** → else `INPUT-INVALID`.
4. **Fixture pre/post + precondition match** → else `VOID (fixture-contaminated)`.
5. **Mask required lines**, then run the **22 universal invariants**.
6. Run the **per-scenario assertions** from the manifest case, each with its `FAIL_SIGNAL`.
7. Run the bot checklist items with ids, scopes and `compare` types:
   - **`reference/checklists/generic.md`** — bot-agnostic (off-topic, silence/re-prompt bounds,
     interruption, ASR mishearing, no-fabrication, language/script, PII/consent, hold-message,
     graceful exit, verbatim-repeat, "are you AI?"/do-not-call, closing offer). Applies to EVERY bot.
   - **`reference/checklists/{kkb,dkb,maya,trrain,<bot-slug>}.md`** — bot-specific must-verify items.
8. **Write the result JSON** and update `coverage.json`. Then write the report per §Report contract,
   and the per-case `status.<target-id>` back into `raya/testcases/<bot-id>.json`.

Every item cites the analyser bug-pattern it guards (e.g. `cf. D40`) so a FAIL routes straight to a
known fix direction.

## From a finding to a fix

- **No fix without a transcript.** Confirm the bug in a real call first (this skill). A static or
  analyser finding **opens** an item; it never closes one.
- Route a confirmed **prompt gap** to **`/update-prompt`** (or **`/port-feature`** to carry a proven
  fix from a sibling bot — prefer porting over reinventing). **Runtime tool-adherence** misses are
  often better fixed with a **tool-schema lever** (a `required` param) than more prose — `D25`/`D40`.
- **An example that demonstrates the violation is a prompt bug of its own.** If the wrong output
  greps to a sample conversation, the fix is an **example edit**, not more prose (`D50`).
- After fixing: **snapshot → deploy → re-test with this skill (N ≥ 3) → revert on regression.** Then
  log the changelog + analyser entry (bug-fix feedback loop).
- Backend / data / true tool-adherence issues are NOT prose-fixable → escalate, don't experiment on
  the live flow. Say "the prompt is fine, the inputs were wrong" out loud when that is what the args
  show.

## Testing quality — the three tiers (see repo `CLAUDE.md` → "The three testing tiers")

Every fix is verified in three tiers, in order, and **on every affected variant separately — never
extrapolate**:

0. **Tier 0 — static gate.** The `/generate-test-cases` static set, including the example audit.
   Runs first, blocks the live run and the deploy. Zero calls. (Bot-specific static checks do not run
   in the daily job yet — roadmap G4/G7 — so label Tier 0 as a manual/CI pass in the report.)
1. **Fix verification** — reproduce the EXACT reported failure; confirm it's gone in a real
   transcript, per variant, with a call id and the evidence line.
2. **Blast-radius regression** — the adjacent areas the fix could have broken (same section, shared
   agnostic logic, mirrored sibling variant, the tool payload touched), on each variant. Catches
   "fixed X, broke Y".
3. **Daily general regression** — the standing suite in `raya/regression/` run by the scheduled cloud
   worker (survives the machine being off), **plus the production detectors**. Not a substitute for
   tiers 1–2.

## Persona library

`raya/personas/` holds grounded personas (mined from real calls via `scenario-catalog.md`):
cooperative existing-seeker, not-interested, wants-different-job, silent, off-topic, machinery-bait,
and a multi-scenario router (kept for reference; the per-call arg it needs does NOT reach the tester,
so select personas by PATCH). Add new personas as `<lang>-<behavior>.md` with an English instruction
header + in-language spoken lines, and state the **forcing gate** the persona drives — two cases may
share a call only if their forcing functions are compatible at every gate the path crosses.

Never write a persona that requires mumbling or unintelligible speech: TTS cannot do it, and the
persona will either speak clearly or go silent. Route those rungs to `static` + `human_call`.
