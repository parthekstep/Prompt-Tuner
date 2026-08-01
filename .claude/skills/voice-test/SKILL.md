---
name: voice-test
description: Run agent-to-agent voice tests of a Raya bot using a persona "tester" agent, and grade the call against generic + bot-specific checklists. Use to reproduce a reported bug, verify a fix end-to-end, or regression-test scenarios before a demo.
---

# Voice Test — agent-to-agent call testing

Test a live Raya voice bot by having a **tester/persona agent** role-play a human, receive a
call from the **bot under test**, and grading the resulting transcript against checklists. This
is how we find bugs ourselves instead of asking the user to place every call by hand.

## The setup (topology)

- **Tester agent** — an INBOUND agent whose single prompt is a *persona* (a human the bot talks
  to). Current tester: **"Testing Agent- Blue Dots"**, uuid `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`,
  inbound DID **`917946350285`**. It is set **non-interruptable** and **max_call_duration = 5 min**
  (bot agents are capped at 15 min by the API; the tester stays at 5 — set 2026-08-01 by Parth, superseding the earlier 4-min cap). Its persona is swapped by PATCHing its `instructions`.
- **Bot under test** — an OUTBOUND agent (e.g. KKB Hindi Signals `115b38a5-…`). It is *triggered*
  to place a call to the tester's DID; it runs its real prompt + real tools.
- We then read BOTH call legs and grade the bot.

## Prerequisites

- `raya/.env` (RAYA_BASE_URL, RAYA_API_TOKEN) — never commit.
- `scripts/raya_testcall.py` — `persona` (swap the tester's script), `lang hi|kn` (switch the
  tester's language+voice), `call` (fire one call), `whoami`.
- `scripts/raya_testrun.py` — fire ONE call + poll to completion + dump the graded transcript
  (connect-retry built in).
- `scripts/raya_call.py` — read past calls/transcripts for any agent.
- Personas: `raya/personas/*.md`. Checklists: `.claude/skills/voice-test/reference/checklists/`.

## Platform reality (learned the hard way — respect these or waste calls)

1. **Trigger:** `POST /api/call` with `agent_id` = **bot under test**, `to_number` = the tester's
   **10-digit** DID (`7946350285`; the `91` is prepended via `country_code`), `agent_args` = the
   bot's inputs. **OMIT `out_did`** — passing it explicitly gave `Unanswered`; omitting connects.
2. **Call creation is rate-limited** (~1 per ~13 s → HTTP 429 with `retry_after`). Space fires ≥ ~15 s.
3. **Bridging is intermittent** — some dials fail instantly (`outcome` Failure/Unanswered, `dur=0`,
   no transcript). This is flaky telephony, NOT a bug in the request. **Retry the connect** (the
   runner does, with a ~45 s cooldown). A burst of rapid calls degrades bridging; space them out.
4. **`GET /api/call/{uuid}` LAGS** after a call — it shows `Pending`/`dur=0` for a bit before the
   transcript + `call_output` finalize. Keep polling (the runner does); or trust the Raya console.
5. **The tester (callee) receives NO `agent_args`.** `POST` args reach the `agent_id` (the bot)
   only. So you **cannot** select a scenario per call via an arg — pick the persona by PATCHing the
   tester prompt.
6. **The bot looks up the DIALED number** (`${contact_phone}` is bound to `to_number`), i.e. the
   tester DID — *not* whatever phone you pass in `agent_args`. So the seeker/employer identity the
   bot sees is the tester DID. Provision the backend record you want under that number
   (e.g. a Signals profile for the tester DID) to set up existing-vs-new-user tests; Signals has
   **no delete route**, so a number can't be reset to "new" once a profile exists.

## Concurrency (for running a batch faster)

- **Parallel calls DO bridge** — multiple calls to the tester DID overlap in time (verified).
- **BUT one tester = one persona at a time** (single prompt, no per-call arg). So you can only run
  the **same** scenario in parallel on one tester. For **different** scenarios in parallel you need
  **one tester agent per scenario** (each its own inbound DID + persona), then fan calls across them.
- Default to **sequential** (PATCH persona → run → grade → next). It is the reliable mode on one
  tester and sidesteps the burst-throttle.

## Run ONE test

```bash
# 1. Load the persona onto the tester (swaps its prompt)
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<persona>.md
# 1b. (optional) switch tester language to match the bot under test
python3 scripts/raya_testcall.py lang <tester_uuid> hi|kn
# 2. Fire + poll + dump the graded transcript
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "<label>"
```

`<args.json>` = the bot's `agent_args` (copy the shape from a known-good past call via
`scripts/raya_call.py <bot_uuid>`). For a quick smoke test you may temporarily lower the tester's
`max_call_duration_mins` (e.g. to 2) to cap wait — **the tester's standing cap is 5 min**.

## Grade the call

Walk the dumped transcript + `call_output` against the checklists:
- **`reference/checklists/generic.md`** — bot-agnostic (off-topic, silence/re-prompt bounds,
  interruption, ASR mishearing, no-fabrication, language/script, PII/consent, hold-message, graceful
  exit, verbatim-repeat, "are you AI?"/do-not-call). Apply to EVERY bot.
- **`reference/checklists/{kkb,dkb,maya}.md`** — bot-specific must-verify items.
Each item says how to detect pass/fail from `tool_calls` / spoken turns / `call_output`, and cites
the analyser bug-pattern it guards (e.g. `cf. D40`).

## From a finding to a fix

- **No fix without a transcript.** Confirm the bug in a real call first (this skill).
- Route a confirmed **prompt gap** to **`/update-prompt`** (or **`/port-feature`** to carry a proven
  fix from a sibling bot — prefer porting over reinventing). **Runtime tool-adherence** misses (the
  model ignoring clear prose) are often better fixed with a **tool-schema lever** (e.g. a `required`
  param) than more prose — see analyser D25/D40.
- After fixing: **snapshot → deploy → re-test with this skill → revert on regression.** Then log the
  changelog + analyser entry (bug-fix feedback loop).
- Backend / data / true tool-adherence issues are NOT prose-fixable → escalate, don't experiment on
  the live flow.

## Persona library

`raya/personas/` holds grounded personas (from `scenario-catalog.md`, mined from real calls):
cooperative existing-seeker, not-interested, wants-different-job, silent, off-topic, and a
multi-scenario router (kept for reference; the per-call arg it needs does NOT reach the tester, so
select personas by PATCH). Add new personas as `<lang>-<behavior>.md` with an English instruction
header + in-language spoken lines.
