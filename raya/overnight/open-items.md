# Open items for Parth — decisions/actions I left to you

As of ~02:50 IST 2026-07-30 (overnight run). These are things I deliberately did NOT auto-fix — either dicey (could be a harness artifact), needing a real call I can't place, needing backend info, or a data/campaign issue outside the prompt. Each has the evidence + a ready-to-go fix if you approve.

## 1. Verify the INBOUND fixes with a real inbound call (can't be harness-tested)
- **What:** KKB inbound Hi (`b6222233`) + Kn (`4ac90bf1`) got the **D31 new-caller apply fix** (create→WAIT→apply, no batching) + **D34 neutral hold**. Both are DEPLOYED + rollback-snapshotted, but **verify-pending** — the tester agent can only RECEIVE calls, so it can't dial an inbound bot to test it.
- **On you:** place one real inbound call to each as a NEW caller (no profile) who picks a job + consents → confirm `create_profile` fires, then `apply_job` succeeds (no 404). If it still 404s, see item #8.
- **Alt I can build:** give the tester an `out_did` so it can DIAL the inbound bot's `in_did` (inbound harness). Needs your OK to modify the tester config / a spare out_did.

## 2. kkb-kn-out — create_profile sent a MALFORMED phone → HTTP 400 (dicey: harness artifact vs real)
- **Evidence:** harness call `fa530906` — `create_profile phone:"+9197946350285"` → `400 "Invalid Indian phone number format"`. The seeker couldn't be created → apply failed.
- **Why dicey:** in the harness, `${contact_phone}` binds to the tester DID, so the malform may be a DID artifact. But production OUTBOUND calls pass `contact_phone` already `+91`-prefixed (e.g. `+916364306440`), and the template prepends `+91` again → the same double/malformed shape would hit real seekers who answer. No real outbound transcript exists to confirm (outbound calls mostly go unanswered).
- **Ready fix (needs your OK / a real-call confirmation):** the **exactly-one-`+91`** composition (D17/D39 direction) — use `contact_phone` as-is if already `+91`, else prepend once; never double. Port-ready to kkb-kn-out (confirmed malform). **NOTE: Maya-out create_profile phone was CLEAN (single `+91`, call `baf836fe`) — so this is NOT universal; it's specific to kkb-kn-out's phone template** (kkb-hi-out unconfirmed). I held off because it's a live production bot and whether real (non-harness) outbound calls malform is unconfirmed.

## 3. Phone double-prefix LATENT on kkb-hi-out + maya-hi
- Analyser flagged the `+91`-hard-prepend template; no real repro found (inbound siblings send a single `+91`). Same **exactly-one-`+91`** fix as #2 is ready. Bundle with #2 if you want it applied.

## 4. DKB phone format — Kn `create_job` example uses bare 10-digit, Hindi uses `+91`
- **Evidence:** DKB Kn `create_job`/`update_job_details` examples show `"phoneNumber":"9108790249"`; Hindi shows `"+919108790249"`. The write may silently fail if the backend keys on one format.
- **On you / backend:** confirm the up-postjob required `phoneNumber` format. If `+91…`, I'll align the Kn examples + add an exactly-one-`+91` rule. (Not changed tonight — needs the backend answer.)

## 5. DKB scheduled agent_args are field-misaligned (DATA issue, not prompt)
- **Evidence:** real DKB calls have `city:"200"`, `salary:"Sector 63, 201309"` (an address in the salary field), `job_role:"Not Available"`. The campaign is populating `agent_args` wrong.
- **On you / data team:** fix the DKB campaign's arg mapping. No prompt change can fix mis-supplied inputs.

## 6. Memory-substitution (D32) — confirmed LATENT, left as-is
- kkb-hi-in + kkb-kn-out: the memory-resume opener does NOT actually substitute for get_profile in real/harness calls (fetch still fires; bot doesn't assert stale memory). Left the opener unchanged. **Decision:** if you want the belt-and-suspenders neutral-opener + "memory-is-not-a-fetch" guard (as on the Signals bots) anyway, say so — it's port-ready.

## 7. Tester harness limitations (for richer testing)
- **One tester DID** → can't run different scenarios in parallel (callee gets no agent_args; one persona at a time). More tester DIDs = parallel scenario testing.
- **Signals has no delete route** → the tester DID's Signals profile can't be reset to "new"; new-seeker Signals paths can't be re-tested on it. A reset/delete or a second dummy number would help.
- **Inbound bots** can't be harness-tested (see #1).

## 8. D31 fix has a runtime tool-adherence residue (watch on verify)
- The KKB-inbound apply-404 was partly the model *hallucinating* a profile_id / skipping create_profile. The deployed fix removes the batching language (should hold), but if a post-fix real inbound call STILL shows a fabricated/empty `profile_id`, prose won't be enough → needs a **platform/tool-schema backstop** (e.g. Raya capturing the create_profile response into a variable the apply step must use). Flagging so we escalate to LitWiz rather than piling on prose.

## 9. Maya — D31 NOT present (false alarm); real exposure is D34
- **Corrected:** Maya does NOT carry the D31 create→apply batching. `Maya/Maya Hindi.md` line 457 uses a different design — `create_profile` runs EARLIER in the flow, so apply is `apply_job` alone (no same-turn create+apply). The analyser's D31-flag-on-Maya was a stale heuristic; **no Maya D31 fix needed.**
- **Real Maya exposure: D34 — CONFIRMED ACTIVE + FIXED.** Maya-out test `baf836fe` showed the create_profile hold narrated; ported the neutral-hold fix → DEPLOYED maya-hi-out `47fdffe6` + maya-hi-in `df99f501` (inbound verify-pending). Maya's distinctive features all confirmed WORKING in the same call: campus identity, feminine voice, student gate, and the MPL Competition offer (first live observation). So no residual Maya action beyond the inbound verify.
