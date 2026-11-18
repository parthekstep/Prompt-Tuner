#!/usr/bin/env python3
"""Reference post-call step for the KKB bot on VoicERA + AI DPG: builds call_output.

Spec: KKB-VoicERA/KKB VoicERA Output.md. Part A is computed here from the AI DPG telemetry; Part B is
extracted by a model whose instructions are read from the spec file itself (the "> " block), so the
code and the spec cannot drift apart.

Inputs (files, as exported from the systems):
  --jaeger FILE      Jaeger API JSON ({"data": [trace, ...]}) for the call's session
  --loki FILE        Loki lines: the raw export (one {"ts_ns","stream","line"} per line) or a
                     query_range API response
  --transcript FILE  VoicERA transcript text ("[ts] role: text" lines), or
  --harness FILE     the AI DPG voice-bench call record (legs[].turns[].caller/reply)
  --call FILE        optional VoicERA call record JSON (call_response, custom_variables, duration)
  --session ID       optional session_id (<phone>:<call_id>); default: the one found in the telemetry
  --llm MODEL        run Part B with this OpenAI model (needs OPENAI_API_KEY); without it Part B
                     fields are left out and the model prompt is written next to the output
  --partb FILE       merge a Part B JSON produced by any other model from that prompt file
  --out FILE         write the result here (default: stdout)

Output: {"call_output": {...}, "tool_calls": [...], "turns": [...], "call_transcript": [...]}
call_transcript is Raya-shaped ({role, content, tool_calls}) so a Raya webhook receiver reads it.
"""
import argparse, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "KKB-VoicERA", "KKB VoicERA Output.md")
PART_B_FIELDS = ["call_engaged", "call_language", "primary_topic", "jobs_interest", "jobs_shown",
                 "jobs_offered_count", "job_roles_offered", "job_no_match", "applied_job_matches_choice",
                 "preferred_location", "preference_mismatch_reason", "services_pitched", "service_interest",
                 "service_callback_slot", "service_offered", "call_later_request", "drop_reason",
                 "final_summary"]
ORDER = ["seeker_name", "participant_id", "call_answered", "call_engaged", "call_language", "primary_topic",
         "jobs_interest", "jobs_fetched", "jobs_shown", "jobs_offered_count", "job_roles_offered",
         "job_no_match", "consent_status", "profile_saved", "applied_to_job", "applications_count",
         "jobs_applied", "jobs_failed_to_apply", "applied_job_matches_choice", "preferred_location",
         "preference_mismatch_reason", "services_pitched", "service_interest", "service_callback_slot",
         "service_offered", "call_later_request", "drop_reason", "phases_visited", "final_summary"]


# ---------- telemetry ----------

def load_loki(path):
    """Return parsed log records: {ts, traceid, body, attrs}."""
    raw = open(path, encoding="utf-8").read().strip()
    lines = []
    if raw.startswith("{") and '"data"' in raw[:200]:          # query_range API response
        for stream in json.loads(raw)["data"]["result"]:
            for ts, line in stream["values"]:
                lines.append((int(ts), line))
    else:                                                        # raw export, one JSON per line
        for l in raw.splitlines():
            r = json.loads(l)
            lines.append((int(r["ts_ns"]), r["line"]))
    out = []
    for ts, line in sorted(lines):
        try:
            b = json.loads(line)
        except ValueError:
            continue
        out.append({"ts": ts, "traceid": b.get("traceid", ""), "body": b.get("body", ""),
                    "attrs": b.get("attributes", {})})
    return out


def load_jaeger(path):
    d = json.load(open(path, encoding="utf-8"))
    return d.get("data", d) if isinstance(d, dict) else d


def tool_log(traces, logs, session):
    """One entry per action.execute span, in time order, with status from its http_call child."""
    by_trace = {}
    for r in logs:
        by_trace.setdefault(r["traceid"], []).append(r)
    calls, turns = [], []
    for t in sorted(traces, key=lambda t: min(s["startTime"] for s in t["spans"])):
        spans = t["spans"]
        tags = lambda s: {x["key"]: x["value"] for x in s.get("tags", [])}
        if session and not any(tags(s).get("session_id") == session for s in spans):
            continue
        turn = len(turns)
        phase = next((r["attrs"].get("next_subagent_id") for r in by_trace.get(t["traceID"], [])
                      if r["body"] == "orchestrator.stream_turn_complete"), None)
        intent = next((r["attrs"].get("intent") for r in by_trace.get(t["traceID"], [])
                       if r["body"] == "orchestrator.stream_turn_complete"), None)
        turns.append({"turn": turn, "trace_id": t["traceID"], "next_phase": phase, "intent": intent})
        children = {}
        for s in spans:
            for ref in s.get("references", []):
                children.setdefault(ref["spanID"], []).append(s)
        for s in sorted(spans, key=lambda s: s["startTime"]):
            if s["operationName"] != "action.execute":
                continue
            st = tags(s)
            http = next((c for c in children.get(s["spanID"], []) if c["operationName"].endswith("http_call")), None)
            code = tags(http).get("http.status_code") if http else None
            entry = {"turn": turn, "tool": st.get("tool_name"), "category": st.get("category"),
                     "status_code": code, "success": bool(code) and 200 <= int(code) < 300,
                     "latency_ms": round(s["duration"] / 1000), "params": None, "response": None}
            for r in by_trace.get(t["traceID"], []):           # DEBUG lines, when the tool service logs them
                if r["attrs"].get("tool_name") != entry["tool"]:
                    continue
                if r["body"].startswith("rest_api_request") and isinstance(r["attrs"].get("params"), dict):
                    entry["params"] = r["attrs"]["params"]
                elif r["body"].startswith("rest_api_response") and "body" in r["attrs"]:
                    entry["response"] = r["attrs"]["body"]
            calls.append(entry)
    return calls, turns


def jobs_from_responses(calls):
    """item_id -> {role, company_name, company_location} from logged fetch_jobs bodies (may be cut at 2,000 chars)."""
    jobs = {}
    for c in calls:
        if c["tool"] != "fetch_jobs" or not c["response"]:
            continue
        body = c["response"] if isinstance(c["response"], str) else json.dumps(c["response"])
        ids = list(re.finditer(r'"item_id"\s*:\s*"([0-9a-f-]{36})"', body))
        for i, m in enumerate(ids):
            chunk = body[m.end():ids[i + 1].start() if i + 1 < len(ids) else len(body)]

            def get(*keys):
                for k in keys:
                    v = re.search(r'"%s"\s*:\s*"([^"]*)"' % k, chunk)
                    if v:
                        return v.group(1)
                return "NA"
            jobs[m.group(1)] = {"role": get("role", "title"), "company_name": get("jobProviderName", "companyName", "company_name"),
                                "company_location": get("jobProviderLocation", "location")}
    return jobs


# ---------- transcript ----------

def load_transcript(a):
    if a.harness:
        rec = json.load(open(a.harness, encoding="utf-8"))
        turns = []
        for leg in rec.get("legs", []):
            for t in leg.get("turns", []):
                turns.append({"role": "user", "content": t.get("caller", "")})
                turns.append({"role": "assistant", "content": t.get("reply", "")})
        return turns, rec.get("phone", "")
    turns = []
    for line in open(a.transcript, encoding="utf-8"):
        m = re.match(r"\s*(?:\[[^\]]*\]\s*)?(user|caller|human|assistant|agent|bot)\s*:\s*(.*)", line, re.I)
        if m:
            role = "user" if m.group(1).lower() in ("user", "caller", "human") else "assistant"
            turns.append({"role": role, "content": m.group(2).strip()})
    return turns, ""


# ---------- Part A ----------

def part_a(call, calls, turns, transcript):
    ok = lambda name: [c for c in calls if c["tool"] == name and c["success"]]
    fail = lambda name: [c for c in calls if c["tool"] == name and not c["success"]]
    cv = (call or {}).get("custom_variables") or {}
    answered = any(t["role"] == "user" and t["content"].strip() for t in transcript)
    if call and call.get("call_response") and call["call_response"] != "answered":
        answered = False
    phases = [t["next_phase"] for t in turns if t["next_phase"]]
    seen = list(dict.fromkeys(phases))
    consent = "NA"
    if "consent_declined" in phases:
        consent = "Declined"
    else:
        idx = [i for i, p in enumerate(phases) if p in ("consent", "consent_reask")]
        if idx and any(p in ("profile_setup", "apply_confirm") for p in phases[idx[0] + 1:]):
            consent = "Given"
        if any((c["params"] or {}).get("profile_consent") is True for c in ok("save_profile")):
            consent = "Given"
    jobs = jobs_from_responses(calls)
    def job(c, with_reason=False):
        jid = (c["params"] or {}).get("job_item_id") or (c["params"] or {}).get("item_id") or "NA"
        o = {"job_id": jid, **jobs.get(jid, {"role": "NA", "company_name": "NA", "company_location": "NA"})}
        if with_reason:
            msg = ""
            if c["response"]:
                m = re.search(r'"message"\s*:\s*"([^"]+)"', str(c["response"]))
                msg = " - " + m.group(1) if m else ""
            o["failure_reason"] = f"HTTP {c['status_code']}{msg}" if c["status_code"] else "no response"
        return o
    return {
        "seeker_name": cv.get("contact_name") or "Unknown",
        "participant_id": cv.get("participant_id") or "NA",
        "call_answered": "Yes" if answered else "No",
        "jobs_fetched": "Yes" if ok("fetch_jobs") else "No",
        "profile_saved": "Yes" if ok("save_profile") or ok("update_profile") else "No",
        "consent_status": consent,
        "applied_to_job": "Yes" if ok("apply_job") else "No",
        "applications_count": len(ok("apply_job")),
        "jobs_applied": [job(c) for c in ok("apply_job")],
        "jobs_failed_to_apply": [job(c, True) for c in fail("apply_job")],
        "phases_visited": ", ".join(seen) or "NA",
    }


# ---------- Part B ----------

def part_b_prompt(a_fields, transcript, cv, jobs):
    spec = open(SPEC, encoding="utf-8").read()
    instructions = "\n".join(l[2:] if l.startswith("> ") else l[1:] for l in spec.splitlines() if l.startswith(">"))
    lines = "\n".join(f"{'caller' if t['role'] == 'user' else 'agent'}: {t['content']}" for t in transcript)
    return (instructions
            + "\n\nFACTS FROM THE SYSTEM'S RECORDS (never contradict):\n" + json.dumps(a_fields, ensure_ascii=False, indent=1)
            + "\n\nCAMPAIGN CSV VALUES:\n" + json.dumps(cv, ensure_ascii=False)
            + ("\n\nJOBS RETURNED BY THE SEARCH (id -> details):\n" + json.dumps(jobs, ensure_ascii=False) if jobs else "")
            + "\n\nTRANSCRIPT:\n" + lines
            + "\n\nReturn ONE JSON object with exactly these keys: " + ", ".join(PART_B_FIELDS) + ".")


def run_llm(model, prompt):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set")
    body = {"model": model, "temperature": 0, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": "Extract the fields now."}]}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", json.dumps(body).encode(),
                                 {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    out = json.load(urllib.request.urlopen(req, timeout=120))
    return json.loads(out["choices"][0]["message"]["content"])


def enforce(o):
    """Rules in code: tool facts win, drop_reason NA when not answered or applied."""
    if o["call_answered"] == "No" or o["applied_to_job"] == "Yes":
        o["drop_reason"] = "NA"
    if o["applied_to_job"] == "No":
        o["applied_job_matches_choice"] = "NA"
    for k in ("jobs_offered_count",):
        try:
            o[k] = int(o.get(k) or 0)
        except (TypeError, ValueError):
            o[k] = 0
    return o


def raya_transcript(transcript, calls, turns):
    """Raya-shaped turn list: tool calls attached to the agent reply of the turn they ran in."""
    out, turn = [], -1
    for t in transcript:
        if t["role"] == "user":
            turn += 1
            out.append({"role": "user", "content": t["content"]})
        else:
            names = [c["tool"] for c in calls if c["turn"] == turn]
            msg = {"role": "assistant", "content": t["content"]}
            if names:
                msg["tool_calls"] = [{"function": {"name": n}} for n in names]
            out.append(msg)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jaeger", required=True); p.add_argument("--loki", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--transcript"); g.add_argument("--harness")
    p.add_argument("--call"); p.add_argument("--session"); p.add_argument("--llm"); p.add_argument("--partb"); p.add_argument("--out")
    a = p.parse_args()

    call = json.load(open(a.call, encoding="utf-8")) if a.call else None
    transcript, phone = load_transcript(a)
    traces, logs = load_jaeger(a.jaeger), load_loki(a.loki)
    session = a.session
    if not session and call and call.get("call_id"):
        session = next((r["attrs"]["session_id"] for r in logs
                        if str(r["attrs"].get("session_id", "")).endswith(":" + call["call_id"])), None)
    calls, turns = tool_log(traces, logs, session)
    fields = part_a(call, calls, turns, transcript)
    cv = (call or {}).get("custom_variables") or {}
    prompt = part_b_prompt(fields, transcript, cv, jobs_from_responses(calls))
    if a.llm or a.partb:
        b = run_llm(a.llm, prompt) if a.llm else json.load(open(a.partb, encoding="utf-8"))
        fields.update({k: b.get(k, "NA") for k in PART_B_FIELDS})
        fields = enforce(fields)
    elif a.out:
        open(a.out + ".partB-prompt.txt", "w", encoding="utf-8").write(prompt)
    result = {"call_output": {k: fields[k] for k in ORDER if k in fields},
              "tool_calls": [{k: v for k, v in c.items() if k != "response"} for c in calls],
              "turns": turns, "call_transcript": raya_transcript(transcript, calls, turns)}
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
        print(json.dumps(result["call_output"], ensure_ascii=False, indent=1))
    else:
        print(text)


if __name__ == "__main__":
    main()
