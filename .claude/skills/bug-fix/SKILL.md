---
name: bug-fix
description: End-to-end bug-fixing loop from the Consolidated Feedback Tracker (Google Sheet) to the live Raya agents. Reads the sheet, picks OPEN issues, temporal-checks them against the changelog, grounds each in the real call transcript, fixes the prompt where a gap exists, deploys the fix to the live agent, and writes the status back to the sheet. Propagates agent-agnostic fixes to sibling agents (gated by an email approval). Use when the user says "process the feedback sheet", "fix the reported bugs", "run the bug-fix loop", or points at the tracker.
---

# Bug-fix loop (sheet → transcript → fix → deploy → sheet)

The closed loop, proven 2026-07-18. Ties together: `scripts/gsheets.py` (sheet R/W),
the Raya call + agent APIs, `/raya-reconcile`, `/update-prompt`, `scripts/raya_deploy.py`,
and the temporal check. **Fix only OPEN issues. Ground every change in a real transcript.
Deploys are gated and verified.**

## Credentials / prerequisites
- `raya/.env` — `RAYA_BASE_URL`, `RAYA_API_TOKEN` (git-ignored).
- Google service-account key for the sheet — `scripts/gsheets.py` finds it (`$GOOGLE_SA_KEY` → `secrets/gsheets-sa.json` → `~/Downloads/service-account.json`). SA `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com` must have edit access.
- The tracker id: `1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU`, tab `Doc 1 Issues`.

## Sheet → agent mapping (campaign label → repo file → Raya agent)
The sheet's "Bot name" uses campaign labels; map them (uuids live in `raya/agents.json`):

| Sheet "Bot name" | repo file | target id |
|---|---|---|
| KKB (Ghaziabad) | KKB/KKB Placeholder Hindi.md | kkb-hi-out |
| KKB Kannada | KKB/KKB Placeholder Kannada.md | kkb-kn-out |
| KKB placeholder Inbound | KKB/KKB Placeholder Inbound.md | kkb-hi-in |
| KKB Kannada Inbound | KKB/KKB Placeholder Inbound Kannada.md | kkb-kn-in |
| **KKB HE** (Higher-Ed = Maya) | Maya/Maya Hindi.md | maya-hi-out |
| **KKB HE Inbound** | Maya/Maya Inbound.md | maya-hi-in |
| DKB (Ghaziabad) | DKB/DKB Hindi.md / DKB Kannada.md | dkb-hi-out / dkb-kn-out |

## Sheet columns (Doc 1 Issues)
`A DATE · B Title · C Type · D Issue description · E Bot name · F Owner · G Priority · H Status · I ETA · J Call IDs · K Additional comments`. Status vocab: `1. Submitted / 2. Accepted to Fix / 3. Rejected, not an issue / 4. Fixed for UAT / 5. Pending / 6. Passed to Field / 7. Closed`.

## Procedure

### 1. Pull + filter
`scripts/gsheets.py --sheet-id <id> get "'Doc 1 Issues'!A1:K200" --out <scratch>/issues.csv`.
Keep rows where Owner contains the target person AND Status is OPEN (Submitted / Accepted / Pending / WIP / Open). Skip `Fixed`, `Confirmed working`, `Closed`, `Rejected`. Order by DATE then Priority (P1 first).

### 2. Temporal check (before any change)
For each open issue: get the call datetime (the DATE column, or the transcript's `created_at`).
Then check `<agent>/CHANGELOG.md` — **did we ship a fix for this specific issue AFTER that date?**
If yes and the sheet still says open → **assume fixed; set Status = "4. Fixed for UAT" with a note; make NO prompt change.** Only proceed to fix issues with no post-dating fix.

### 3. Ground in the transcript (mandatory)
Never change a prompt without seeing the call. The sheet's numeric call IDs do NOT map to the API (open gap) — identify the call by **agent + date** instead:
```
GET {BASE}/api/call?agent_id=<uuid>&limit=20     -> {calls:[{uuid, caller_no, created_at, call_duration, outcome}]}
GET {BASE}/api/call/<call_uuid>                   -> {call_transcript:[{role,content}], call_output:{drop_reason,...}, outcome}
```
(headers `X-API-Key`, `User-Agent: Mozilla/5.0`.) Save transcripts to files; grep for the symptom — quote the offending turns. `call_output.drop_reason` (e.g. `apply_failed`) is a strong signal. For an unknown-size batch, use a Workflow to fan out one diagnosis agent per bug + an **adversarial verify** agent per diagnosis (see the 2026-07-18 run). Decide per issue: real prompt bug / backend / data / not-reproduced.

### 4. Reconcile (who's ahead) before editing
The live prompt can hold console-only edits. Reconcile the target with `/raya-reconcile` (browser sha-boolean — the Raya **GET returns empty instructions**, so never trust a GET for the live content). If Raya is ahead, pull live into the repo first; if repo is ahead / in sync, proceed.

### 5. Fix (only real prompt gaps)
Use `/update-prompt`: surgical, additive; Hindi is source of truth, mirror agnostic content **verbatim** to Kannada and **adapt** language-specific examples; preserve tool payloads / variable names / section structure; keep Maya's divergences (flag-and-ask). Snapshot first (`scripts/prompt-version.sh save`). Append a `CHANGELOG.md` entry and, per the bug-fix loop, add/sharpen a `prompt-analyser/reference/bug-patterns.md` class.

### 6. Deploy (gated, verified)
Deploy via the **API PATCH** — it works and self-verifies even though GET is broken:
```
PATCH {BASE}/api/agent/<uuid>   body {"instructions": <file content>}   -> 200, response echoes "instructions"
```
Verify: `normalize(response.instructions) == normalize(file)`. Name-guard first (GET returns `name` correctly). Record to `raya/deploy-history.md`. `scripts/raya_deploy.py deploy <target>` does this with a snapshot + confirm + response-verify; batch stops on first failure. **Human gate:** confirm the target list before pushing to production agents.

### 7. Write status back
`scripts/gsheets.py update` (or the Sheets `values:batchUpdate` for many rows at once). Set Status = `4. Fixed for UAT` for deployed fixes; `3. Rejected` / a "Not reproduced" note for non-bugs; `Flagged — backend` / `Flagged — data` for out-of-prompt causes. Put the evidence + what changed in column K.

## Cross-agent propagation (email-gated)
When a fix is **not agent-specific** (a spoken-output rule, a routing gate, a guard — e.g. the slash rule, the inbound fork gate), it should land on every sibling agent that shares the logic. Before doing that:
1. Identify the sibling agents/files (agnostic logic → all languages + in/out).
2. **Send an approval email** describing the fix + the list of agents it would propagate to (Gmail MCP: `create_draft` / send). 
3. **Read the reply** (`search_threads` / `get_message`); proceed only on approval, honoring any scoping the reply gives. If declined, apply only to the originally-reported agent.
4. Then fix + deploy the approved siblings and update their sheet rows.

## Safety
- Fix only OPEN issues; never re-fix something the temporal check shows already-shipped.
- Every prompt change is snapshotted + surgical; Hindi↔Kannada parity preserved.
- Deploys are name-guarded, response-verified, recorded, and human-confirmed for production.
- Rollback: `scripts/prompt-version.sh restore <agent> <pre-fix-label>` → re-PATCH.
- Long-term this shrinks to the *new delta* rows each cycle plus self-triggered test calls (Stage 2).
