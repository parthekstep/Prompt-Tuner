# OVERNIGHT AUTONOMOUS RUN — state + plan (single source of truth)

Started 2026-07-29 late night (IST). User asleep; autonomous mandate. Resume from **NEXT ACTION**
on every re-invocation (background-task completion OR cron heartbeat). Keep this file updated.

## GOAL (user's words, distilled)
Wake up to: all bots significantly improved + fixed, **nothing broken**; new skills created;
an **Excel report** of issues found / test cases run / what got fixed / what needed recurring
rounds; a separate **open-items list** for the user (only truly-dicey decisions — otherwise just
fix); improvement ideas; all existing skills updated with today's learnings; the whole
test→fix→deploy system coherent and demo-ready.

## SAFETY RULES (never violate — "nothing broken" is the hard constraint)
1. **Snapshot before every prompt edit.** `scripts/raya_deploy.py deploy` auto-snapshots + GET-backup
   + read-back verify. Also `scripts/prompt-version.sh save` for extra safety.
2. **Revert on any regression.** If a deploy read-back fails, or a post-deploy test shows worse
   behavior than before, restore the snapshot and redeploy the known-good version. Log it.
3. **No fix without a reproducing transcript.** Static/analyser findings must be confirmed by a real
   call before editing a live prompt. If no repro, log to open-items (don't guess-fix).
4. **Prefer PORTING proven fixes** (location-required, live-selection D37, enum-mapping D38, phone
   D39, role-update) over reinventing — but ONLY where the backend matches (Signals fixes apply to
   Signals bots only; up-getjob/up-postjob bots are different).
5. **Sync Hindi↔Kannada; never deploy a drifted pair.** Maya is Hindi-only.
6. **Dicey/ambiguous → open-items list, do NOT touch the live prompt.** Cap autonomous fix→deploy
   cycles at 2 per bot to avoid thrashing.
7. **Tool-adherence misses → tool-schema lever, not more prose** (D25/D40). Backend/data issues →
   escalate to open-items, never experiment on the live flow.
8. **Voice tests are SEQUENTIAL** (one tester line; callee gets no agent_args; burst-throttle).
   Approach B (pipeline PATCH→fire→wait-answer→next) only if bridging is behaving; else pure
   sequential. If a call fails to bridge, retry (runner does); after repeated fails, cool down 2+ min.
9. **Never raise tester max_call_duration above 4 min.** May lower temporarily for short smokes.
10. **Changelog + analyser entry for every bug fix** (bug-fix feedback loop).
11. **VOICE-TEST EVERY BOT I CHANGE (mandatory, per user).** For each bot I modify: (a) a PRE-fix
    repro call that confirms the bug via the harness; (b) the fix; (c) a POST-fix verify call that
    confirms the fix AND regression-checks the happy path, graded against generic.md + the bot's
    checklist. Nothing ships without a passing post-fix call. Re-test the language twin too. If a
    call can't bridge after retries, cool down and retry; if truly stuck, mark the fix
    "deployed, verify pending" in the report (never claim verified without a post-deploy transcript).

## INVENTORY
- Tester: "Testing Agent- Blue Dots" `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, inbound DID `917946350285`
  (dial as 10-digit `7946350285`), non-interruptable, max_dur 4. Persona swapped via
  `scripts/raya_testcall.py persona <uuid> <file>`; language via `... lang hi|kn`.
- Bots (uuid | backend | direction | testable-via-harness?):
  - KKB Hi Signals `115b38a5-42ef-4082-be69-84a871bb226a` | Signals | outbound | YES (primary; heavily tested)
  - KKB Kn Signals `33037201-78ce-405d-b509-a3b6934e20f1` | Signals | outbound | YES (UNTESTED twin — priority)
  - KKB Hi out `da612923-1927-45d7-9ad0-b1c7cbb15294` | up-getjob | outbound | YES
  - KKB Kn out `87ab9108-5d66-4a13-a20a-575eaa9aae36` | up-getjob | outbound | YES
  - DKB Hi `57814ac8-5d79-41f5-bab7-bcfe2d9aac4f` | up-postjob | outbound(employer) | YES (needs employer persona + DKB args)
  - DKB Kn `d1a1614f-fa7e-41c1-8963-e7f3af213a13` | up-postjob | outbound(employer) | YES
  - Maya Hi out `47fdffe6-0cb0-4fcf-8762-135ddadfb194` | up-getjob(campus) | outbound | YES (student persona + college_name)
  - KKB Hi in `b6222233...`, KKB Kn in `4ac90bf1...`, Maya Hi in `df99f501...` | inbound | ??? (can an inbound agent place an outbound call? TEST once; if not, flag not-harness-testable)
- Harness scripts: `scripts/raya_testcall.py` (persona/lang/call/whoami), `scripts/raya_testrun.py`
  (fire+poll+dump, connect-retry), `scripts/raya_call.py` (read past calls).
- Checklists: `.claude/skills/voice-test/reference/checklists/{generic,kkb,dkb,maya}.md`.
- Personas: `raya/personas/*.md`. Scenario catalog: `raya/personas/scenario-catalog.md`.
- Known-good agent_args live in each bot's recent calls (pull via `raya_call.py <uuid>`).
- Signals test profile lives under the tester DID (role drifts as tests update it — fine).

## DELIVERABLES (for the morning)
- [ ] `/voice-test` skill (DONE — SKILL.md + 4 checklists staged).
- [x] `/onboard` skill (DONE — registered).
- [ ] Existing skills updated with today's learnings (Signals mechanics, harness, D40, role-update, 1:1).
- [ ] Excel report: issues found / tests run / fixed / recurring — `reports/overnight-YYYY-MM-DD.xlsx`.
- [ ] Open-items list for the user (dicey/decision bugs + backend escalations) — markdown.
- [ ] Improvement ideas + demo-packaging notes — markdown.
- [ ] All fixes committed + pushed; deploy-history + changelog + analyser updated.

## SCOPE ADDENDUM (user, ~00:05 IST 2026-07-30)
- **"All bots" = the FULL set:** KKB inbound + outbound, Hindi + Kannada; DKB (Hi + Kn); Maya (Hi
  out + in). Inbound must be covered too. Harness reality: it triggers the bot to CALL the tester,
  which tests **outbound** behavior. To test an INBOUND bot properly the tester must DIAL the bot's
  in_did (tester needs an out_did — it has none). PLAN for inbound: (a) static analysis (done in the
  workflow), (b) review historical real inbound transcripts (scenario-catalog + `raya_call.py`),
  (c) PROBE whether the tester can be given an out_did to dial an inbound bot; if infeasible, log to
  open-items and cover inbound via (a)+(b). Do NOT force a broken inbound harness.
- **New auto-variable `${call_direction}`** → "inbound" | "outbound" (Raya replaces it). Useful for
  the combined bots below, and note wherever a prompt should branch on direction.
- **Create-agent API available:** `POST /api/agent` (name, instructions, output_fields,
  output_instructions, dids, language_id, voice_id, tools, durations, say_hello, etc.). Lets us mint
  new agents programmatically. (Auth = same key already in raya/.env; never commit it.)
- **BONUS (only if core is done + time remains; gated on confidence):** build **5 combined
  inbound+outbound bots** — KKB Hi, KKB Kn, DKB Hi, DKB Kn, Maya Hi — each a SINGLE prompt that
  branches on `${call_direction}` (merging today's separate inbound/outbound prompts). These are
  NON-Signals (up-getjob / up-postjob). Test + COMPARE vs the standard split bots; **do NOT migrate
  / replace the live bots** — only report readiness so the user decides. Create them as NEW agents
  (POST /api/agent) so nothing existing is touched.
- **FURTHER BONUS (only if all above done):** port the 5 combined bots to Signals too.

## PLAN / PHASES  (checkbox = done)
### Phase 0 — setup (DONE)
- [x] Approach B chosen; /voice-test skill written; checklists staged; plan file created.
- [x] Cron heartbeat set — job 15487546, fires :13/:43 each hour, ONLY when REPL idle → clean cooldown-resume, no double-dispatch. (Auto-expires after 7 days.)
- [x] /onboard skill authored + registered (SKILL.md + reference/intake-template.md).
- [x] Static-analysis workflow launched (wf_4fd4ce5d) — 8 bots → scratchpad/analysis/<key>.md.
- [x] KKB Kn Signals cooperative test launched (bivpyhtqa) — first Phase-2 call.

### Phase 1 — static analysis (parallel, no calls) → prioritized bug list
- [ ] Analyse each bot's live prompt against analyser bug-patterns + checklists → structured findings
  (severity, symptom, whether a proven sibling fix exists, needs-transcript-to-confirm). Output:
  scratchpad/analysis/<bot>.md + a merged prioritized list scratchpad/PRIORITY_BUGS.md.

### Phase 2 — sequential voice testing (confirm high-priority findings + regression the happy paths)
Test matrix (persona × bot), sequential. Start with the untested/priority:
- [ ] KKB Kn Signals — cooperative(existing), not-interested, wants-different (needs KN personas + lang kn).
- [ ] KKB Hi/Kn out (up-getjob) — cooperative, not-interested (needs up-getjob args + seeker persona).
- [ ] DKB Hi/Kn — employer happy-path, wrong-number, "talk now" (needs DKB args + employer persona).
- [ ] Maya Hi out — student intro/gate (needs college_name + student persona).
- [ ] (one) inbound-agent trigger probe → testable or not.
Log every call (uuid, scenario, pass/fail per checklist, issues) to scratchpad/TEST_LOG.md.

### Phase 3 — fix high-priority (conservative, ported, reverted-on-fail)
- [ ] For each confirmed high-priority bug: port a proven fix or make the smallest surgical edit;
  snapshot→deploy→re-test→revert-on-regress; changelog + analyser. Cap 2 cycles/bot. Dicey→open-items.

### Phase 4 — report + skills + packaging
- [ ] Build the Excel report (xlsx skill). Build open-items + ideas markdown. Update all existing
  skills. Verify system coherence. Commit + push everything. Write a morning summary.

## PROGRESS LOG (append-only; newest at bottom)
- 2026-07-29 ~23:50 IST — Phase 0. /voice-test skill written; checklists staged (generic47/kkb51/dkb39/maya60); runner productionized to scripts/raya_testrun.py. Approach B confirmed.
- 2026-07-30 ~00:05 IST — Phase 0 DONE: cron heartbeat 15487546 set; /onboard skill done+registered; static-analysis workflow wf_4fd4ce5d launched (8 bots); KKB Kn Signals cooperative test launched (bivpyhtqa). Scope expanded (inbound too, ${call_direction}, create-agent API, bonus combined bots).
- KKB HI SIGNALS results already banked today (pre-plan): new-seeker apply bug (location→draft→PROFILE_NOT_LIVE) FIXED (location required on both Signals bots); existing-seeker happy path PASS; not-interested PASS; wants-different PASS; role-mismatch→update-role feature ADDED + verified; 1:1 live-selection verified. Changelog + analyser D40 logged.
- 2026-07-30 ~00:20 IST — KKB Kn Signals cooperative PASS (b3ef7abe; full parity w/ Hindi). Checkpoint committed+pushed (e7663c8: skills, harness scripts, personas, catalog, Signals role-update+1:1, D40). TEST_LOG.md seeded. DKB employer + Maya student personas staged. AWAITING static-analysis workflow to build PRIORITY_BUGS, then targeted confirm-calls + fixes on production bots.

## TEST LOG POINTER → scratchpad/TEST_LOG.md (create + append every call: uuid, bot, scenario, pass/fail per checklist, issues). PRIORITY_BUGS → scratchpad/PRIORITY_BUGS.md (merge from analysis/).

- 2026-07-30 ~00:35 IST — Static analysis DONE (8 bots). HIGH cluster: kkb-hi-in D31 (create→apply batched→empty profile_id, x2), kkb-kn-out D32 (memory substitutes for get_profile), kkb-hi-out + maya-hi +91-double-prefix, kkb-hi-signals stale D39 phone bullet. Merge+ground subagent dispatched (aa81e181) → PRIORITY_BUGS.md with ACTIVE/LATENT classification from real transcripts. **Discovery: production outbound bots pass contact_phone WITH +91 (e.g. +918630988821), so the +91-prepend double-prefix finding is likely ACTIVE.** DKB scheduled agent_args are field-misaligned (data/campaign issue, not prompt). Production outbound recent calls mostly outcome=Failure (verify: no-answer vs phone-bug). Tester currently in KANNADA mode + kn cooperative persona.

## NEXT ACTION
1. When bivpyhtqa (KN Signals) lands → grade vs kkb.md + generic.md; append TEST_LOG; note parity vs Hindi.
2. When wf_4fd4ce5d (static analysis) lands → read scratchpad/analysis/*.md; build scratchpad/PRIORITY_BUGS.md (HIGH first; mark which have a proven sibling fix to PORT; which need a repro call).
3. Drive Phase-2 sequential testing across the matrix (KKB Hi/Kn out [up-getjob], DKB Hi/Kn [employer persona + DKB args], Maya Hi [student persona + college_name], + inbound probe). Pull known-good agent_args per bot from its recent calls (raya_call.py). Create personas as needed (kn done for seeker; need employer + student personas).
4. Phase 3: fix HIGH-priority confirmed bugs (port proven fixes; snapshot→deploy→re-test→revert-on-fail; changelog+analyser; cap 2 cycles/bot; dicey→open-items).
5. Phase 4: Excel report (xlsx skill) + open-items.md + ideas.md; update existing skills (bug-fix/prompt-analyser/etc. with harness + Signals learnings); commit+push; morning summary.
6. BONUS (only if 1–5 done + time): 5 combined ${call_direction} bots (new agents, don't touch live) → test+compare → report readiness. FURTHER BONUS: port combined to Signals.
Between voice calls, do the NON-call deliverables (report scaffolding, skill updates) so the slow call pipeline is never the bottleneck.
