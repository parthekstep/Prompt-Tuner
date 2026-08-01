#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static regression suite — runs daily (cloud-scheduled), fast + reliable, no telephony.

Checks EVERY conversation prompt for the failure classes we've hit. Precision over recall: a noisy
daily email is worse than none, so checks are tuned to avoid false positives (tokens that only ever
appear as Dhiway/Signals CONTRACT markers, not ones that can show up in a "never speak these field
names" ban). Produces raya/regression/latest-report.md + latest-report.json (the `critical` list
drives the email digest).

Backend: a filename containing "Signals" -> Signals DPG; else legacy Dhiway/up-getjob.
Agent role: DKB is an employer/provider bot (no get_profile/apply_job); KKB/Maya are seeker bots.

Usage: python3 raya/regression/static_regression.py
"""
import json, os, re, sys, io

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def discover_prompts():
    out = []
    files = {
        "KKB": ["KKB Placeholder Hindi.md","KKB Placeholder Kannada.md","KKB Placeholder Inbound.md",
                "KKB Placeholder Inbound Kannada.md","KKB Placeholder Hindi Signals.md","KKB Placeholder Kannada Signals.md",
                "KKB Placeholder Inbound Signals.md","KKB Placeholder Inbound Kannada Signals.md"],
        "DKB": ["DKB Hindi.md","DKB Kannada.md","DKB Hindi Signals.md","DKB Kannada Signals.md"],
        "Maya": ["Maya Hindi.md","Maya Inbound.md","Maya Hindi Signals.md","Maya Inbound Signals.md"],
    }
    for agent_dir, fns in files.items():
        for fn in fns:
            p = os.path.join(REPO, agent_dir, fn)
            if not os.path.exists(p): continue
            name = fn.lower()
            out.append({"path": os.path.join(agent_dir, fn), "agent": agent_dir,
                        "lang": "kn" if "kannada" in name else "hi",
                        "direction": "inbound" if "inbound" in name else "outbound",
                        "backend": "signals" if "signals" in name else "dhiway",
                        "seeker": agent_dir in ("KKB","Maya"),
                        "text": io.open(p, encoding="utf-8").read()})
    return out

# CONTRACT-ONLY tokens (never appear in a "never-speak-these-fields" ban) -> unambiguous leakage.
SIGNALS_CONTRACT = ["item_state","lifecycle_status","acting_as_user_id","educationCategory",
                    "workExperienceYearsConditional","otherHelpNeeded","PROFILE_NOT_LIVE",
                    "INVALID_ITEM_STATE","job_posting_1.0","blue_dot"]
DHIWAY_CONTRACT  = ["up-getjob","ONEST-AGENT","onest-lite","jobs-onest-interface","job-up.seeker",
                    "jobs.onest.seeker"]

def check(p):
    f=[]; t=p["text"]; be=p["backend"]
    add=lambda s,c,m: f.append((s,c,m))
    # 1. cross-backend contract leakage (contract-only tokens)
    for tok in (DHIWAY_CONTRACT if be=="signals" else SIGNALS_CONTRACT):
        if tok in t:
            add("critical","leakage",f"{be} prompt contains the other backend's contract token '{tok}'")
    # 2. phone-doubling template
    if be=="signals" and re.search(r"(?<![+\w])91\$\{contact_phone\}", t):
        add("critical","phone-doubling","Signals '91${contact_phone}' can double the 91 — use ${contact_phone} as-is")
    if be=="dhiway" and ("+91${contact_phone}" in t or "+91<contact_phone>" in t):
        add("critical","phone-doubling","Dhiway '+91${contact_phone}' can double the +91 — use ${contact_phone} as-is")
    # 3. memory-injection block
    if "{${contact_memory}}" not in t:
        add("critical","memory-block","missing the verbatim memory-injection block {${contact_memory}}")
    # 4. Signals seeker enum-exactness (only prompts that carry the new Phase-2 fields)
    if be=="signals" and p["seeker"] and "educationCategory" in t:
        for enum in ["ITI / Other Vocational Trainings","Polytechnic / Diploma","3-5 Years","B.Tech/B.E."]:
            if enum not in t:
                add("critical","enum-drift",f"missing byte-exact enum '{enum}' (a wrong enum 400s the write)")
    # 5. required sections by role
    if "Graceful Exit" not in t and "graceful exit" not in t.lower():
        add("major","missing-section","no Graceful Exit section")
    if p["seeker"] and "get_profile" not in t:
        add("major","missing-section","seeker prompt missing get_profile")
    if p["agent"]=="DKB" and "create_job" not in t:
        add("major","missing-section","DKB prompt missing create_job")
    return f

def sync_parity(prompts):
    out=[]; by={}
    for p in prompts:
        by.setdefault((p["agent"],p["direction"],p["backend"]),{})[p["lang"]]=p
    for key,L in by.items():
        if "hi" in L and "kn" in L:
            h=len(re.findall(r"(?m)^#{1,2} ",L["hi"]["text"])); k=len(re.findall(r"(?m)^#{1,2} ",L["kn"]["text"]))
            d=abs(h-k)
            if d>2:
                sev="major" if d>6 else "minor"
                out.append((sev,"sync-drift",f"{key[0]} {key[1]} {key[2]}: Hi/Kn header-count drift ({h} vs {k})",L["hi"]["path"]))
    return out

def main():
    prompts=discover_prompts(); findings=[]
    for p in prompts:
        for s,c,m in check(p): findings.append({"severity":s,"category":c,"file":p["path"],"message":m})
    for s,c,m,path in sync_parity(prompts): findings.append({"severity":s,"category":c,"file":path,"message":m})
    order={"critical":0,"major":1,"minor":2}; findings.sort(key=lambda x:order.get(x["severity"],3))
    crit=[x for x in findings if x["severity"]=="critical"]; maj=[x for x in findings if x["severity"]=="major"]
    outdir=os.path.join(REPO,"raya/regression")
    io.open(os.path.join(outdir,"latest-report.json"),"w",encoding="utf-8").write(
        json.dumps({"prompts_checked":len(prompts),"total_findings":len(findings),"critical":crit,"major":maj,"all":findings},ensure_ascii=False,indent=1))
    lines=["# Static regression report","",f"Prompts checked: **{len(prompts)}** | Findings: **{len(findings)}** (critical **{len(crit)}**, major **{len(maj)}**)",""]
    if not findings: lines.append("✅ No static findings — all prompts clean.")
    else:
        for sev in ("critical","major","minor"):
            g=[x for x in findings if x["severity"]==sev]
            if g:
                lines.append(f"## {sev.upper()} ({len(g)})")
                for x in g: lines.append(f"- [{x['category']}] `{x['file']}` — {x['message']}")
                lines.append("")
    io.open(os.path.join(outdir,"latest-report.md"),"w",encoding="utf-8").write("\n".join(lines))
    print(f"Static regression: {len(prompts)} prompts | {len(crit)} critical, {len(maj)} major, {len(findings)-len(crit)-len(maj)} minor")
    return 0

if __name__=="__main__":
    sys.exit(main())
