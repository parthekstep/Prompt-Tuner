#!/usr/bin/env python3
"""Run ONE agent-to-agent voice test end-to-end and dump the graded transcript.

A TESTER agent (inbound DID, non-interruptable, short max-duration) role-plays a human persona;
the BOT UNDER TEST (outbound agent) is triggered to call the tester's DID; they converse; we
pull the transcript + call_output to grade against the checklists in
.claude/skills/voice-test/reference/checklists/.

Flow: fire `POST /api/call` (agent_id = bot, to_number = tester 10-digit DID, out_did OMITTED)
-> poll to terminal -> dump bot transcript (with tool_calls) + call_output + the tester leg.

Reality of the platform (learned the hard way — see the /voice-test skill):
  * `POST /api/call` is rate-limited ~1 per ~13s (429 -> back off).
  * Bridging is INTERMITTENT: some dials fail immediately (outcome Failure/Unanswered, dur=0,
    no transcript). We retry the connect CONNECT_TRIES times with a cooldown.
  * Passing out_did explicitly gave 'Unanswered'; omitting it connects.
  * `GET /api/call/{uuid}` LAGS after a call (shows Pending/dur=0 briefly) -> keep polling.
  * The tester (callee) receives NO agent_args -> a scenario cannot be selected per call via
    agent_args; select the persona by PATCHing the tester prompt (scripts/raya_testcall.py persona).

Usage: raya_testrun.py <bot_uuid> <to_10digit> <args_json> <tester_uuid> [label]
Env: raya/.env (RAYA_BASE_URL, RAYA_API_TOKEN). Token never printed.
"""
import json, os, sys, time, urllib.request, urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip()
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]
CONNECT_TRIES = 4
CONNECT_BACKOFF = 45   # seconds between connect attempts (tight retries all fail)


def req(method, path, body=None, tries=4):
    for a in range(tries):
        data = json.dumps(body).encode() if body is not None else None
        h = {"X-API-Key": KEY, "User-Agent": "Mozilla/5.0"}
        if data is not None:
            h["Content-Type"] = "application/json"
        r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read().decode()
                return resp.status, (json.loads(raw) if raw.strip() else {})
        except urllib.error.HTTPError as e:
            return e.code, {"_err": e.read().decode()[:300]}
        except Exception as e:
            if a == tries - 1:
                return 0, {"_err": str(e)[:150]}
            time.sleep(4)


def main():
    bot, to, args_path, tester = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    label = sys.argv[5] if len(sys.argv) > 5 else "test"
    agent_args = json.load(open(args_path, encoding="utf-8"))
    body = {"agent_id": bot, "to_number": to, "agent_args": agent_args,
            "country_code": "91", "timezone": "Asia/Kolkata"}  # out_did omitted on purpose

    def fire():
        for _ in range(6):
            st, resp = req("POST", "/api/call", body)
            if st == 429:
                ra = 15
                try: ra = int(json.loads(resp["_err"]).get("retry_after", 15))
                except Exception: pass
                print(f"[{label}] 429; waiting {ra + 2}s"); time.sleep(ra + 2); continue
            print(f"[{label}] POST /api/call -> {st} {json.dumps(resp)[:140]}")
            return resp.get("uuid") if isinstance(resp, dict) else None
        return None

    def poll(uuid):
        c = {}
        for i in range(22):
            time.sleep(18)
            _, c = req("GET", f"/api/call/{uuid}")
            oc = c.get("outcome"); turns = len(c.get("call_transcript") or [])
            print(f"[{label}] poll {i}: outcome={oc!r} dur={c.get('call_duration')} turns={turns}")
            if oc == "Completed" and turns > 0:
                return c
            if oc in ("Failure", "Unanswered", "No Answer", "Rejected"):
                return c
        return c

    final = None
    for attempt in range(CONNECT_TRIES):
        uuid = fire()
        if not uuid:
            print(f"[{label}] no call uuid; abort"); return
        c = poll(uuid)
        if c.get("outcome") == "Completed" and len(c.get("call_transcript") or []) > 0:
            final = c; break
        print(f"[{label}] connect attempt {attempt + 1} did not bridge "
              f"(outcome={c.get('outcome')}); retrying in {CONNECT_BACKOFF}s")
        time.sleep(CONNECT_BACKOFF)

    if final is None:
        print(f"\n[{label}] NEVER BRIDGED after {CONNECT_TRIES} attempts (flaky telephony)."); return

    print("\n" + "=" * 76)
    print(f"[{label}] BOT {final.get('uuid')} outcome={final.get('outcome')} dur={final.get('call_duration')}")
    print("call_output:", json.dumps(final.get("call_output"), ensure_ascii=False, indent=2))
    print("\nTRANSCRIPT:")
    for t in (final.get("call_transcript") or []):
        role = t.get("role")
        for tc in (t.get("tool_calls") or []):
            fn = tc.get("function") or {}
            print(f"[{role}->TOOL] {fn.get('name')}({fn.get('arguments')})")
        content = t.get("content")
        if content:
            content = content if role == "tool" else str(content).replace("\n", " ")
            print(f"[{role}] {content[:600]}")

    _, td = req("GET", f"/api/call?agent_id={tester}&limit=1")
    tc = (td.get("calls") or [])
    if tc:
        _, tcc = req("GET", f"/api/call/{tc[0]['uuid']}")
        print(f"\n[{label}] TESTER leg {tc[0]['uuid'][:8]}: outcome={tcc.get('outcome')} "
              f"dur={tcc.get('call_duration')} turns={len(tcc.get('call_transcript') or [])} "
              f"call_output={json.dumps(tcc.get('call_output'), ensure_ascii=False)[:200]}")


if __name__ == "__main__":
    main()
