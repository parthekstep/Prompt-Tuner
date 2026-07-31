---
name: bug-fix
description: End-to-end bug-fixing loop from the Consolidated Feedback Tracker (Google Sheet) to the live Raya agents. Runs the fixed sequence — find issues → root-cause each against its real call transcript → fix only genuine prompt gaps → propagate to sibling bots where the same bug exists → verify nothing broke → repeat → summarize last. Marks the sheet "Fixed for UAT" on deploy. Use when the user says "process the feedback sheet", "fix the reported bugs", "run the bug-fix loop", or points at the tracker.
---

# Bug-fix loop (sheet → transcript → root-cause → fix → propagate → verify → sheet → summary)

Ties together `scripts/gsheets.py` (sheet R/W), the Raya call + agent APIs, `/raya-reconcile`,
`/update-prompt`, `/port-feature`, `scripts/raya_deploy.py`, and the regression check.

## THE SEQUENCE (do these in order — do not skip, do not reorder, summary is ALWAYS last)

1. **Find** — pull every OPEN issue for the target owner from the sheet.
2. **Root-cause with the real call** — for EACH issue, pull the actual Raya transcript and find what truly happened. **No fix without a transcript** (see rule below).
3. **Classify** — prompt-fixable | backend | runtime/tool-adherence | no-repro | verbiage | ops. Only *prompt-fixable* gets a prompt edit (see the classification table).
4. **Fix** the genuine prompt gaps (via `/update-prompt`), surgically.
5. **Propagate** — check the sibling bots; if the SAME bug/gap is present there, port the fix (via `/port-feature`). Don't assume — verify presence.
6. **Verify nothing broke** — regression-check the edits (contradictions with existing rules, flow intact, Hindi↔Kannada parity). Reconcile anything the new rule contradicts, then deploy.
7. **Deploy** to the live agents (API PATCH), read-back-verified + in-sync.
8. **Write the sheet status** — `Fixed for UAT` for deployed fixes (see status discipline).
9. **Repeat** for every issue.
10. **Summarize LAST** — only after all issues are worked, write the MD summary (what fixed / how / why prior attempts failed / what's pending). Never write the summary before the work is done.

## The two non-negotiable rules (the ones the user keeps repeating)

- **NO FIX WITHOUT A TRANSCRIPT.** Never edit a prompt off a sheet report, a hunch, or a static/analyser finding alone. Pull the actual call, read the offending turns, confirm the bug is real and understand its root cause FIRST. A "plausible" static gap that no transcript reproduces is **not** a fix — it's an ungrounded change (see r70 2026-07-27: a static "gap" that 40 calls never reproduced). If you can't reproduce it in a recent call, do NOT fix — ask the reporter for the specific call uuid + timestamp.
- **"Fixed for UAT" ≠ confirmed.** Deploying lands the fix; it does not prove it works. Mark the sheet `Fixed for UAT` (= deployed, ready for the user's acceptance test) — but do NOT claim it's *confirmed* until a **post-deploy** call transcript shows the corrected behavior. If there are no post-deploy calls yet, say so.

## Credentials / prerequisites
- `raya/.env` — `RAYA_BASE_URL`, `RAYA_API_TOKEN` (git-ignored).
- Google service-account key — `scripts/gsheets.py` finds it (`$GOOGLE_SA_KEY` → `secrets/gsheets-sa.json` → `~/Downloads/service-account.json`). SA `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com` has edit access.
  - **If `~/Downloads/service-account.json` is blocked** (macOS TCC — the app process loses folder access on restart), the same key lives base64-encoded in `kaam-ki-baat/.env.local` as `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`. Decode it into `secrets/gsheets-sa.json` (git-ignored) — pipe base64→file, never print the private key. Or ask the user to copy the key into `secrets/gsheets-sa.json`.
- Tracker id: `1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU`, tab **`All Issues`** (NOT "Doc 1 Issues" — that tab is gone).

## Sheet columns (`All Issues`)
`A DATE · B STATUS · C Bot · D Title · E Type · F Issue description · G Owner · H Priority · I ETA · J Call IDs · K Additional comments · L "Fixed, Date/call id"`.
Status vocab in use: `Open · Accepted to Fix · Fixed for UAT · Flagged - Backend Issue · Rejected / Not an Issue · Closed`.
Note: column J "Call IDs" are the team's own ids and do **not** map to the Raya API — identify calls by **agent uuid + date** instead.

## Sheet "Bot" label → repo file → Raya target (uuids in `raya/agents.json`)
| Sheet "Bot" | repo file | target id |
|---|---|---|
| KKB (Ghaziabad) | KKB/KKB Placeholder Hindi.md | kkb-hi-out |
| KKB Kannada | KKB/KKB Placeholder Kannada.md | kkb-kn-out |
| KKB placeholder Inbound | KKB/KKB Placeholder Inbound.md | kkb-hi-in |
| KKB Kannada Inbound | KKB/KKB Placeholder Inbound Kannada.md | kkb-kn-in |
| **KKB HE** (Higher-Ed = Maya) | Maya/Maya Hindi.md | maya-hi-out |
| **KKB HE Inbound** | Maya/Maya Inbound.md | maya-hi-in |
| DKB (Ghaziabad) | DKB/DKB Hindi.md / DKB Kannada.md | dkb-hi-out / dkb-kn-out |

## Root-cause classification (step 3) — only ONE class gets a prompt edit
| Class | Signal | Action |
|---|---|---|
| **prompt-fixable** | transcript shows a genuine prompt gap (missing guard, wrong wording, missing step) | fix via `/update-prompt`, propagate, deploy, → `Fixed for UAT` |
| **backend** | tool returns HTTP 4xx/5xx with a valid-looking payload; placeholder job inventory (`job_id "1"/"2"` → "Job not found") | do NOT edit the prompt → `Flagged - Backend Issue` + escalate |
| **runtime / tool-adherence** | the model ignores an instruction the prompt already states clearly (e.g. `get_profile` not firing despite HARD BLOCKs) | do NOT pile on more prose — that regresses (see below). Escalate for platform **tool-forcing** → `Flagged - Backend Issue` |
| **no-repro** | not reproduced in recent calls | do NOT fix; keep `Open` + comment asking for the reproducing call uuid |
| **verbiage** | pure wording/tone request, not a bug | reassign (Aryan) — out of our scope; note it |
| **ops** | telephony / spam / account (e.g. Truecaller verification) | not a prompt; leave for Ops |

**Do NOT try to prose-fix a runtime tool-adherence failure.** If the prompt already mandates the behavior and the model ignores it, adding more/stronger prose is the single highest-regression-risk move — it has already backfired here: the 2026-07 attempt to force `get_profile` by reframing it as "silent/invisible" made the model *stop calling it* (regression, reverted; see bug-patterns D25). The durable fix is platform-side (Raya tool-forcing / static first-message). Escalate; don't experiment on the live flow.

## Step details

**Step 2 — ground in the transcript.** Identify the call by agent + date:
```
GET {BASE}/api/call?agent_id=<uuid>&limit=20   -> {calls:[{uuid, caller_no, to_number, created_at, call_duration, outcome}]}
GET {BASE}/api/call/<call_uuid>                -> {call_transcript:[…], call_output:{drop_reason,…}, agent_args}
```
(headers `X-API-Key`, `User-Agent: Mozilla/5.0`. Pagination: `&offset=N` (max `limit`≈100). No server-side phone filter — match `caller_no` for **inbound** callers / `to_number` for **outbound** callers, client-side.)

**Read the transcript PROPERLY — the tool-call arguments are how you catch payload bugs.** Each `call_transcript` turn has `role`, `content`, `tool_calls`, `tool_call_id`:
- An **assistant turn that makes a tool call** has `content: null` and a `tool_calls` array: `[{id, type:"function", function:{name, arguments}}]`. `function.arguments` is a JSON string = **the EXACT payload the model sent** (e.g. `apply_job {"job_id":"…","profile_id":"5051"}`). **This is where wrong field values live** — a dumper that prints only `content` shows *nothing* here and you will miss the bug.
- A **tool turn** (`role:"tool"`) holds the **result/error** in `content`, with a `tool_call_id` linking back. Errors carry `response_body_excerpt` (e.g. `{"error":"Invalid or missing profile_id"}`).
- To diagnose a tool failure: read the assistant turn's `tool_calls.function.arguments` (what was sent) **and** the next tool turn's `content` (what came back), and compare field-by-field.

**Known payload gotcha (caused a large share of apply 404s):** `create_profile` returns BOTH a numeric top-level `id` (internal record number, e.g. `5051`) AND a `profileId` (a UUID). `apply_job`'s `profile_id` MUST be the **`profileId` UUID** — the numeric `id` is rejected with "Invalid or missing profile_id" (404). (`get_profile`'s top-level `id` already IS the UUID, so the returning-caller path is fine.)

Use `scripts/raya_call.py <agent_uuid> [limit] [offset]` — it prints `tool_calls.function.{name,arguments}` + linked results (and caller_no/to_number/agent_args). Don't hand-roll a `content`-only reader. **If the API ever omits a field you need, say so explicitly** and don't guess. For a batch, fan out with a Workflow (one grounding agent per issue + an adversarial verify), but every verdict must quote the actual `tool_calls`/result.

**Step 4 — reconcile before editing.** `scripts/raya_deploy.py diff <target>`. If Raya is ahead (console-only edits, real inventory), `pull` it into the repo and commit BEFORE editing. Then fix via `/update-prompt`: surgical, additive, Hindi source-of-truth mirrored verbatim (agnostic) / adapted (spoken) to Kannada, Maya divergences preserved. Snapshot first (`prompt-version.sh save`), append `CHANGELOG.md`, and add/sharpen a `bug-patterns.md` class.

**Step 5 — propagate.** After fixing, check the sibling bots (KKB ↔ Maya; both directions; in/out) for the SAME structural gap. If present, port via `/port-feature` (re-domain to the sibling's variables/tools/spoken lines). This is standard — not email-gated — when it's the identical bug. (An email approval is only needed for broad *agent-agnostic* propagation the user hasn't already scoped.)

**Step 6 — verify nothing broke.** After the edits (before deploy), regression-check: does any new rule CONTRADICT an existing line (e.g. a new canonical-spelling rule vs the file's own sample-dialogue spellings — see the 2026-07-27 Kannada virama / Maya MPL catches)? Did an insertion split a section or break the greeting→fork→apply→failure flow? Is Hindi↔Kannada scaffolding still parallel? Reconcile every contradiction, then re-verify. A Workflow with one regression agent per changed file works well.

**Step 7 — deploy.** API PATCH, name-guarded, read-back-verified, recorded to `raya/deploy-history.md`. `scripts/raya_deploy.py deploy <target>` does this. Never edit the live agent in the Raya console (it clobbers console-only content). Confirm all changed targets are `in sync` afterward. A deploy is NOT the finish line: the fix is not done until a **post-deploy** voice-test/transcript confirms the corrected behavior AND overall sanity holds (nothing else regressed) — `Fixed for UAT` means deployed + ready-to-test, never *confirmed*.

**Step 8 — sheet status discipline (always flip the status, not just a comment):**
- deployed prompt fix → **`Fixed for UAT`** (+ comment: root cause + call uuid + what changed + deploy date; note "awaiting post-deploy call to confirm").
- backend / runtime → **`Flagged - Backend Issue`** (+ what's needed from LitWiz/console).
- no-repro → keep **`Open`** (+ "not reproduced in N calls; need the specific call uuid").
- verbiage → note + reassign. ops → leave.
Never leave a deployed fix marked `Open`.

## Safety
- Fix only OPEN issues; temporal-check against `CHANGELOG.md` first (already shipped after the report date → set `Fixed for UAT`, make no change).
- Every prompt change is snapshotted + surgical; parity preserved; deploys name-guarded + response-verified + recorded.
- Rollback: `scripts/prompt-version.sh restore <agent> <pre-fix-label>` → re-PATCH.
