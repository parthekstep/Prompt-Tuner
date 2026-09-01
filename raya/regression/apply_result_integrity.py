#!/usr/bin/env python3
"""apply_result_integrity.py — the bot must not contradict itself about the apply, or narrate a write it never made.

Two failures, both found by testing rather than by a report (2026-09-01):

  X. CONTRADICTORY APPLY RESULT — the same call tells the caller both "अभी इस जॉब में अप्लाई पूरा नहीं
     हो पाया" and "अप्लाई हो गया है". Seen on call `14f90f64`: apply_job returned 422, the bot spoke the
     failure line, then two turns later — bridging out of the Need Capture answer — spoke the whole
     Apply Success block. The caller cannot know which is true, and the second one is false.

  Y. NARRATED WRITE — the bot says a field was updated/saved ("मैंने उम्र 26 साल अपडेट कर दी है") on a
     call with NO `update_profile` / `create_profile` tool call anywhere in the transcript. Seen on
     call `0decf61a`, where the caller corrected their age from 29 to 26 and the correction went
     nowhere. The record stays wrong and nobody finds out, because the caller was told it was fixed.

  Z. SUCCESS CLAIMED WITH NO SUCCESSFUL TOOL RESULT — "अप्लाई हो गया है" on a call where apply_job
     never returned success (already a hard failure in the prompt; asserted here on real traffic).

Exit 1 on any finding.

Usage: python3 raya/regression/apply_result_integrity.py [--since YYYY-MM-DD] [--agent <id|uuid>]
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/")
KEY = _env["RAYA_API_TOKEN"]

FAIL_LINE = re.compile(r"अप्लाई पूरा नहीं हो|apply complete नहीं|ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ|apply complete ಆಗಿಲ್ಲ")
OK_LINE   = re.compile(r"अप्लाई हो गया|ಅಪ್ಲೈ ಆಗಿದೆ")
WROTE     = re.compile(r"(अपडेट कर दी|अपडेट कर दिया|सेव कर दिया|सेव कर दी|ಅಪ್‌ಡೇಟ್ ಮಾಡಿದ್ದೀನಿ|ಸೇವ್ ಮಾಡಿದ್ದೀನಿ)")


def get(path, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={
                "X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    turns = d.get("call_transcript") or []
    said = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "assistant")
    tools_called = [ (tc.get("function") or {}).get("name")
                     for m in turns for tc in (m.get("tool_calls") or []) ]
    tool_out = " ".join(str(m.get("content") or "") for m in turns if m.get("role") == "tool")
    apply_ok = bool(re.search(r"'status':\s*'success'|\"status\":\s*\"success\"", tool_out))
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created)
    out = []
    f, o = bool(FAIL_LINE.search(said)), bool(OK_LINE.search(said))
    if f and o:
        out.append(dict(base, kind="X CONTRADICTORY APPLY RESULT",
                        detail="the call says both that the apply did not go through AND that it did"))
    if o and not apply_ok:
        out.append(dict(base, kind="Z SUCCESS WITH NO SUCCESS RESULT",
                        detail="spoke the apply-success line with no successful apply_job result in the transcript"))
    if WROTE.search(said) and not ({"update_profile", "create_profile"} & set(tools_called)):
        out.append(dict(base, kind="Y NARRATED WRITE",
                        detail=f"claimed a field was saved/updated; tools actually called: {sorted(set(filter(None, tools_called))) or 'none'}"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    for t in targets:
        off = 0
        while True:
            d = get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100&offset={off}")
            cs = d.get("calls") or []
            if not cs:
                break
            older = False
            for c in cs:
                if str(c.get("created_at"))[:19] < a.since:
                    older = True
                    continue
                if (c.get("call_duration") or 0) >= 20:
                    work.append((t["id"], c["uuid"]))
            if older or len(cs) < 100:
                break
            off += 100
    print(f"apply-result integrity check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None:
                errs += 1
            else:
                bad.extend(res)
    print(f"fetch errors: {errs}\n")
    if not bad:
        print("  clean — no contradictory apply results and no narrated writes")
        return 0
    for f in bad:
        print(f"  {f['kind']:32} {f['at']}  {f['bot']:20} {f['call']}")
        print(f"        {f['detail']}")
    return 1


def _safe(fn, arg):
    try:
        return fn(*arg)
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
