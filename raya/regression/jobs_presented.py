#!/usr/bin/env python3
"""jobs_presented.py — count jobs actually READ ALOUD, script-independently.

Why this exists: twice now I have graded "how many jobs did it name?" with a Latin-vs-Devanagari
substring match and got 0 when the real answer was 3. The job array is Latin ("Sales executive",
"Alien Energy"); the bot speaks Devanagari ("सेल्स एग्जीक्यूटिव", "एलियन एनर्जी"). Any matcher built on
the array's own strings is a false-negative machine — it is written up as D49 in the analyser and I
walked into it again.

The reliable signal is script-native and language-native: the ORDINAL MARKERS the presentation format
mandates. Hindi "पहला:/दूसरा:/तीसरा:/चौथा:…", Kannada "ಒಂದು:/ಎರಡು:/ಮೂರು:…", plus the "one option"
singular forms. Counting those counts presented jobs without ever touching the array.

Reports, per call: jobs supplied, distinct jobs presented, whether the caller asked for more, and
whether a "that is all we have" line was spoken while any job was still unnamed (the real defect).
Exit 1 only on that last one.

Usage: python3 raya/regression/jobs_presented.py [--since ...] [--agent <id>]
"""
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); KEY = _env["RAYA_API_TOKEN"]

# Kannada ran only to 6 here, so a Kannada bot could never score above 6 however many jobs it named
# -- arr-kn-1 read out all EIGHT and this list could not see the last two. Both languages run to ten.
ORDINALS = [
    (u"पहला", 1), (u"दूसरा", 2), (u"तीसरा", 3), (u"चौथा", 4),
    (u"पाँचवाँ", 5), (u"पांचवां", 5), (u"छठा", 6),
    (u"सातवाँ", 7), (u"आठवाँ", 8), (u"नौवाँ", 9), (u"नौवां", 9), (u"दसवाँ", 10),
    (u"ಒಂದು", 1), (u"ಎರಡು", 2), (u"ಮೂರು", 3), (u"ನಾಲ್ಕು", 4),
    (u"ಐದು", 5), (u"ಆರು", 6), (u"ಏಳು", 7), (u"ಎಂಟು", 8),
    (u"ಒಂಬತ್ತು", 9), (u"ಹತ್ತು", 10),
    # The prompts now hand the model ordinals to twenty-two (a real campaign sent 22 jobs on
    # c472f2c8). A detector that stops at ten under-counts and turns a good call into a finding.
    (u"ग्यारहवाँ", 11), (u"बारहवाँ", 12), (u"तेरहवाँ", 13), (u"चौदहवाँ", 14), (u"पंद्रहवाँ", 15),
    (u"सोलहवाँ", 16), (u"सत्रहवाँ", 17), (u"अठारहवाँ", 18), (u"उन्नीसवाँ", 19), (u"बीसवाँ", 20),
    (u"इक्कीसवाँ", 21), (u"बाईसवाँ", 22),
    (u"ಹನ್ನೊಂದು", 11), (u"ಹನ್ನೆರಡು", 12), (u"ಹದಿಮೂರು", 13), (u"ಹದಿನಾಲ್ಕು", 14), (u"ಹದಿನೈದು", 15),
    (u"ಹದಿನಾರು", 16), (u"ಹದಿನೇಳು", 17), (u"ಹದಿನೆಂಟು", 18), (u"ಹತ್ತೊಂಬತ್ತು", 19), (u"ಇಪ್ಪತ್ತು", 20),
    (u"ಇಪ್ಪತ್ತೊಂದು", 21), (u"ಇಪ್ಪತ್ತೆರಡು", 22),
]
ONE_OPTION = re.compile(u"एक ऑप्शन है|ಒಂದು ಆಪ್ಷನ್ ಇದೆ")
ASK_MORE = re.compile(u"और कौन|और क्या|बाकी|जो भी जॉब|सारी जॉब|ಬೇರೆ ಯಾವ|ಎಲ್ಲಾ ಹೇಳಿ|ಇನ್ನೇನು")
ALL_TOLD = re.compile(u"सब मैंने बता दीं|इतने ही|इवಿಷ್ಟೇ|ಇವಿಷ್ಟೇ|ಎಲ್ಲಾ ಜಾಬ್‌ಗಳನ್ನ ನಾನು ಹೇಳಿದ್ದೀನಿ|और कोई जॉब नहीं")


def get(path, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(BASE + path, headers={
                "X-API-Key": KEY, "User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except Exception:
            if i == tries - 1: raise
            time.sleep(1.5 * (i + 1))


def check(bot, uuid):
    d = get("/api/call/" + uuid)
    aa = d.get("agent_args") or {}
    rec = aa.get("recommendations")
    if isinstance(rec, str):
        try: rec = json.loads(rec)
        except Exception: rec = None
    supplied = len(rec) if isinstance(rec, list) else 0
    if not supplied:
        return []
    turns = [str(t.get("content") or "") for t in (d.get("call_transcript") or [])
             if t.get("role") == "assistant" and t.get("content")]
    user = " ".join(str(t.get("content") or "") for t in (d.get("call_transcript") or [])
                    if t.get("role") == "user")
    said = " ".join(turns)
    # Highest ordinal spoken is NOT the presented count: on live call 54a0daa8 the bot reached
    # आठवाँ by naming Solar Energy Consultant twice, under तीसरा AND सातवाँ, leaving the eighth
    # job unspoken. Count DISTINCT job identities instead, read off the words after each ordinal.
    highest = 0
    slots = {}
    for word, n in ORDINALS:
        # Anchor on the mandated "<ordinal>:" -- Kannada number-words nest, so ಹದಿನೆಂಟು ("eighteen",
        # inside a salary) contains ಎಂಟು ("eight") and a bare substring test read a salary as the
        # eighth job -- a bogus duplicate on 15f6d453 and d9bf1f43.
        if re.search(re.escape(word) + u"\\s*:", said):
            highest = max(highest, n)
            m = re.search(u"(?:^|[\\s\u2014\\-*(])" + re.escape(word) + u"\\s*:\\s*([^।\\n]{2,90})", said)
            if m:
                # key on role AND company: two different jobs can share a role ("Data Entry
                # Operator" at two firms) and keying on the role alone called that a duplicate.
                seg = re.sub(u"\\s+", u" ", m.group(1)).strip().lower()
                # Job identity is the job_id and the bot never says it, so this key is the best
                # available proxy: role + company. It cannot be made exact. Two fields raise a false
                # positive on payloads holding posts that differ only by location (a5443b59: two CY
                # FUTURE Customer Support posts, five McDonald's Crew Member posts); three fields
                # raise a false NEGATIVE when one job is described slightly differently on its two
                # mentions, which lost the confirmed duplicate on 54a0daa8. Two fields, erring toward
                # flagging, and the finding is INFORMATIONAL in fleet_report for exactly this reason.
                slots[n] = u", ".join(seg.split(u",")[:2]).strip()
    distinct = len(set(slots.values())) if slots else highest
    dupes = sorted(v for v in set(slots.values()) if list(slots.values()).count(v) > 1)
    if highest == 0 and ONE_OPTION.search(said):
        highest = distinct = 1
    asked = bool(ASK_MORE.search(user))
    all_told = bool(ALL_TOLD.search(said))
    created = str(d.get("created_at"))[:19]
    base = dict(bot=bot, call=uuid, at=created, supplied=supplied, presented=distinct, asked=asked)
    out = []
    if dupes:
        out.append(dict(base, kind="SAME JOB NAMED UNDER TWO ORDINALS",
                        detail=f"ordinals reached {highest} but only {distinct} distinct jobs; repeated: {'; '.join(dupes)}"))
    if all_told and distinct < supplied:
        out.append(dict(base, kind="ALL-TOLD WHILE JOBS UNNAMED",
                        detail=f"said it had told the caller everything after presenting {distinct} of {supplied}"))
    elif asked and distinct < supplied:
        out.append(dict(base, kind="ASKED FOR MORE, NOT ALL SHOWN (info)",
                        detail=f"caller asked to hear more; {distinct} of {supplied} were presented"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    ap.add_argument("--agent", default=None)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--call", action="append", default=[],
                    help="grade only these call uuids (repeatable) -- the list API lags a few minutes")
    a = ap.parse_args()
    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and t["raya_agent_id"].get("prod")]
    if a.agent:
        targets = [t for t in targets if a.agent in (t["id"], t["raya_agent_id"]["prod"])]
    work = []
    if a.call:
        bot = targets[0]["id"] if targets else "?"
        work = [(bot, c) for c in a.call]
    else:
     for t in targets:
      for c in (get(f"/api/call?agent_id={t['raya_agent_id']['prod']}&limit=100").get("calls") or []):
            if str(c.get("created_at"))[:19] < a.since: continue
            if (c.get("call_duration") or 0) >= 40: work.append((t["id"], c["uuid"]))
    print(f"jobs-presented check | since {a.since} | {len(work)} calls", flush=True)
    bad, errs = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(lambda i: _safe(check, i), work):
            if res is None: errs += 1
            else: bad.extend(res)
    print(f"fetch errors: {errs}\n")
    hard = [f for f in bad if "info" not in f["kind"]]
    if not bad:
        print("  clean — no call claimed to be out of jobs while any remained unnamed")
    for f in bad:
        print(f"  {f['kind']:36} {f['at']}  {f['bot']:18} {f['call']}")
        print(f"        supplied={f['supplied']} presented={f['presented']} asked_for_more={f['asked']} — {f['detail']}")
    return 1 if hard else 0


def _safe(fn, arg):
    try: return fn(*arg)
    except Exception: return None


if __name__ == "__main__":
    sys.exit(main())
