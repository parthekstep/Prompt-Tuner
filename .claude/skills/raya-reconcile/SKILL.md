---
name: raya-reconcile
description: Before editing a live voice agent, reconcile the repo prompt against the LIVE prompt on the Raya console and decide who is ahead. The Raya REST API returns empty instructions, so the console editor is the source of truth for what is live — and someone may have edited it directly. Pulls the live prompt to a FILE via the browser (token-cheap; the prompt never enters the conversation) and diffs it against the repo. Use before any bug fix on a Raya agent, or to build a repo-vs-Raya sync map. Read-only.
---

# Raya reconcile (repo ↔ live)

Stage 1 of the deploy loop: **never edit an agent blind.** Pull what is LIVE, diff it
against the repo, decide who is ahead, and only then apply your fix. Reconcile is the
READ half; writing back (browser Save) is the deploy step.

## Token rule (do not skip)
**Never print or return the full prompt into the conversation.** It is ~70 KB and the
browser tool blocks raw returns anyway. Always route it to a FILE (a Blob download) and
diff on disk — only the diff (or "IN SYNC") reaches the conversation.

## Prerequisites
- Claude for Chrome connected, logged into `console.getraya.app`.
- `raya/agents.json` maps each target id → agent `uuid` (`raya_agent_id.prod`) + repo `file` + `raya_name`.
- Existing targets on Raya: `kkb-hi-out kkb-kn-out kkb-hi-in kkb-kn-in dkb-hi-out dkb-kn-out maya-hi-out maya-hi-in`
  (DKB inbound isn't created on Raya yet).

## Procedure (per agent)
1. **Resolve the uuid:** `scripts/raya_deploy.py targets` (or read `raya/agents.json`).
2. **Pull the live prompt to a file.** Navigate the browser to
   `https://console.getraya.app/agents/<uuid>` (Instructions tab), then run this in the page.
   It downloads to `~/Downloads` and returns only the length — no prompt text:
   ```js
   (() => {
     const cms=[...document.querySelectorAll('.CodeMirror')].map(e=>e.CodeMirror).filter(Boolean);
     const cm=cms.sort((a,b)=>b.getValue().length-a.getValue().length)[0];   // instructions = longest editor
     const v=cm.getValue();
     const a=document.createElement('a');
     a.href=URL.createObjectURL(new Blob([v],{type:'text/markdown'}));
     a.download='raya-live-<TARGET>.md';        // <-- put the target id here, e.g. raya-live-maya-hi-out.md
     document.body.appendChild(a); a.click(); a.remove();
     return {len:v.length};
   })()
   ```
   The editor is **EasyMDE / CodeMirror holding raw markdown**, so this is byte-exact — our `.md` files map 1:1.
3. **Diff:** `scripts/raya_deploy.py reconcile <target>`
   → prints `IN SYNC`, or `DRIFT` with the unified diff + a who-is-ahead hint.
   (Auto-finds the newest `~/Downloads/raya-live-<target>*.md`; or pass `--live <path>`.)
4. **Decide who is ahead:**
   - **IN SYNC** → nothing to reconcile; go straight to your edit.
   - **Repo ahead** (repo = live + your fixes) → repo wins; apply the new fix and deploy the repo version.
   - **Raya ahead** (live has content the repo lacks) → **pull live into the repo FIRST**: copy the
     downloaded file over the repo `file` (respect `/update-prompt`: Hindi is source of truth, mirror to
     Kannada, preserve Maya divergences), commit, then apply the new fix and deploy.

## Sync map (all agents)
Repeat steps 2–3 for each target to see exactly where repo and Raya have drifted, before any deploy.
`IN SYNC` results cost almost nothing (no diff printed).

## Then
Apply the fix on the reconciled base with `/update-prompt`, then write it back to the agent
(deploy — set the editor via CodeMirror `setValue`, click **Save agent**, reload, and **read-back verify**;
the Save POST can return 503 even on success, so trust the read-back, not the HTTP status).
