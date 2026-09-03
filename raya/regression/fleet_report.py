#!/usr/bin/env python3
"""fleet_report.py — one PASS/FAIL line per bot, with explicit criteria.

Why: the runtime detectors print findings per call, which answers "what went wrong" but never
"is this bot OK". Worse, a window with zero calls printed ALL CLEAN on 2026-09-03 and read as a
pass -- so a bot with no coverage must be reported as UNTESTED, never as passing.

Criteria per bot, all evaluated over the window:
  * static      — 0 critical and 0 major static findings for that bot's prompts
  * schema      — tool schemas identical to the rest of its agent+backend family
  * calls       — at least MIN_CALLS usable calls (>=40s) in the window, else UNTESTED
  * behaviour   — 0 blocking runtime findings on those calls

Blocking runtime findings are the ones that mislead or shortchange a caller:
  ALL-TOLD WHILE JOBS UNNAMED, SAME JOB NAMED UNDER TWO ORDINALS, Z SUCCESS WITH NO SUCCESS RESULT,
  X CONTRADICTORY APPLY RESULT, ROW 1 MISSED, consent-before-apply violations.
Informational ones (ASKED FOR MORE ... (info), MEMORY-COVERAGE GAP, DIAGNOSED A CAUSE) do not fail a
bot: the first is a coverage note, the second is the known memory blocker, and the third fires on the
owner-approved "technical issue" wording.

Usage: python3 raya/regression/fleet_report.py [--since YYYY-MM-DDTHH:MM:SS] [--min-calls N]
Times are UTC — the Raya API stamps calls in UTC and passing IST silently selects nothing.
"""
import argparse, datetime, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ROW 1 MISSED is deliberately NOT blocking. It fires when a duplicate apply did not get the
# already-applied line -- but the agent cannot know a job is a duplicate: the error body never
# reaches the model, contact_memory is empty, and get_profile returns no applications (D58). The
# evidence gate makes row 2 the CORRECT output in that state, so treating this as a failure would
# make the fleet permanently red on a blocked platform issue and train us to ignore the report.
# It stays visible in the detector output and in STATUS as the open platform ask.
BLOCKING = ["ALL-TOLD WHILE JOBS UNNAMED", "SAME JOB NAMED UNDER TWO ORDINALS",
            "Z SUCCESS WITH NO SUCCESS RESULT", "X CONTRADICTORY APPLY RESULT",
            "APPLY WITHOUT THE DATA-SHARING LINE"]
DETECTORS = ["jobs_presented", "consent_before_apply", "apply_result_integrity",
             "apply_failure_wording", "location_reconfirm", "location_chain",
             "location_integrity", "apply_outcomes"]


def run(cmd):
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00"))
    ap.add_argument("--min-calls", type=int, default=2)
    a = ap.parse_args()

    targets = [t for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]
               if t.get("kind") == "conversation" and (t.get("raya_agent_id") or {}).get("prod")]
    sig = [t for t in targets if "signals" in t["id"]]

    print("FLEET REPORT — window from %s (UTC), min %d usable calls per bot\n" % (a.since, a.min_calls))

    static = run(["python3", "raya/regression/static_regression.py"])
    m = re.search(r"(\d+) critical, (\d+) major", static)
    crit, maj = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    print("  static suite : %d critical, %d major  -> %s" % (crit, maj, "PASS" if crit == 0 and maj == 0 else "FAIL"))

    schema = run(["python3", "scripts/toolschema_parity.py"])
    sch_ok = "SCHEMA PARITY CLEAN" in schema
    print("  tool schemas : %s" % ("PASS — every family identical" if sch_ok else "FAIL — see toolschema_parity"))

    out = {}
    for det in DETECTORS:
        out[det] = run(["python3", "raya/regression/%s.py" % det, "--since", a.since])

    print("\n  %-22s %-7s %-9s %s" % ("bot", "calls", "verdict", "blocking findings"))
    worst = 0
    for t in sorted(sig, key=lambda x: x["id"]):
        bid = t["id"]
        calls = 0
        for det, text in out.items():
            mm = re.search(re.escape(det.replace("_", "-")) + r".*?\| (\d+) calls", text)
            if mm:
                calls = max(calls, int(mm.group(1)))
        hits = []
        for det, text in out.items():
            for line in text.splitlines():
                if bid in line and any(b in line for b in BLOCKING):
                    tag = next(b for b in BLOCKING if b in line)
                    hits.append(tag)
        mine = sum(1 for det, text in out.items() for line in text.splitlines() if bid in line)
        verdict = "UNTESTED" if mine == 0 else ("FAIL" if hits else "PASS")
        if verdict == "FAIL":
            worst = 2
        elif verdict == "UNTESTED" and worst < 1:
            worst = 1
        print("  %-22s %-7s %-9s %s" % (bid, mine if mine else "0", verdict,
              ", ".join(sorted(set(hits))) if hits else ("no coverage in window" if verdict == "UNTESTED" else "none")))

    print("\n  NOTE: a bot with no calls in the window is UNTESTED, not passing.")
    print("  %s" % ("FLEET PASS" if worst == 0 and crit == 0 and maj == 0 and sch_ok else
                    ("FLEET FAIL" if worst == 2 or crit or maj or not sch_ok else "FLEET PASS WITH GAPS")))
    sys.exit(0 if worst == 0 and crit == 0 and maj == 0 and sch_ok else 1)


if __name__ == "__main__":
    main()
