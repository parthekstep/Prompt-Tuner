#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static regression suite — runs daily (cloud-scheduled), fast + reliable, no telephony.

Checks EVERY conversation prompt for the failure classes we've hit. Precision over recall: a noisy
daily email is worse than none, so checks are tuned to avoid false positives (tokens that only ever
appear as Dhiway/Signals CONTRACT markers, not ones that can show up in a "never speak these field
names" ban). Produces raya/regression/latest-report.md + latest-report.json.

Each finding carries the BOT it belongs to (friendly name + blurb) and a plain-English message, so
build_digest.py can render an email that a reader with no context can act on.

Backend: a filename containing "Signals" -> Signals DPG; else legacy Dhiway/up-getjob.
Agent role: DKB is an employer/provider bot (no get_profile/apply_job); KKB/Maya are seeker bots.

Usage: python3 raya/regression/static_regression.py
"""
import json, os, re, sys, io

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# What each agent is, in words a newcomer understands.
AGENT_BLURB = {
    "KKB": "Government-job matching for workers / job-seekers",
    "DKB": "Job posting & verification for employers (MSMEs)",
    "Maya": "Campus recruitment for UP graduates",
    "TRRAIN": "Follow-up call offering a free support service to seekers who already applied",
}
# Agents whose callers are job-seekers (vs employers) — drives the seeker-only checks.
SEEKER_AGENTS = ("KKB", "Maya", "TRRAIN")
DIRECTION_BLURB = {"outbound": "the bot phones the person", "inbound": "the person phones the bot"}
BACKEND_BLURB = {"signals": "new Signals DPG backend", "dhiway": "older Dhiway/ONEST backend"}


def discover_prompts():
    """Derive the checked set from raya/agents.json — never a hard-coded list.

    Gap G4. This list used to be hand-maintained and twice fell behind reality: the two DKB
    inbound bots (2026-08-05) and then TRRAIN (2026-08-10) were live deploy targets that the
    daily suite silently ignored, while the digest read as full coverage. Deriving it from the
    same manifest the deploys use means a newly registered bot is checked the day it lands.
    coverage_gap() stays as the backstop.
    """
    out = []
    manifest = json.load(io.open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
    for t in manifest.get("targets", []):
        if t.get("kind") != "conversation" or not t.get("deploy"):
            continue
        rel = t["file"]
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            continue
        agent_dir = rel.split("/")[0]
        name = rel.lower()
        lang = "Kannada" if t.get("language") == "kn" or "kannada" in name else "Hindi"
        direction = t.get("direction") or ("inbound" if "inbound" in name else "outbound")
        backend = "signals" if (t.get("signals") or "signals" in name) else "dhiway"
        out.append({
            "path": rel, "agent": agent_dir,
            "lang": "kn" if lang == "Kannada" else "hi",
            "direction": direction, "backend": backend,
            "seeker": agent_dir in SEEKER_AGENTS,
            # friendly identity used throughout the email
            "bot": f"{agent_dir} {lang} \u00b7 {direction} \u00b7 {'Signals' if backend=='signals' else 'legacy'}",
            "blurb": (f"{AGENT_BLURB.get(agent_dir, agent_dir)} \u2014 {DIRECTION_BLURB[direction]}, in {lang}, "
                      f"on the {BACKEND_BLURB[backend]}"),
            "text": io.open(p, encoding="utf-8").read()})
    out.sort(key=lambda x: (x["agent"], x["direction"], x["lang"]))
    return out


# CONTRACT-ONLY tokens (never appear in a "never-speak-these-fields" ban) -> unambiguous leakage.
SIGNALS_CONTRACT = ["item_state","lifecycle_status","acting_as_user_id","educationCategory",
                    "workExperienceYearsConditional","otherHelpNeeded","PROFILE_NOT_LIVE",
                    "INVALID_ITEM_STATE","job_posting_1.0","blue_dot"]
DHIWAY_CONTRACT  = ["up-getjob","ONEST-AGENT","onest-lite","jobs-onest-interface","job-up.seeker",
                    "jobs.onest.seeker"]


def check(p):
    """Return findings for one prompt. Messages are written for a non-expert reader."""
    f = []; t = p["text"]; be = p["backend"]
    other = "Dhiway/ONEST" if be == "signals" else "Signals"
    mine = "Signals" if be == "signals" else "Dhiway/ONEST"

    def add(sev, cat, msg, detail=None):
        f.append({"severity": sev, "category": cat, "message": msg, "detail": detail or {}})

    # 1. cross-backend contract leakage (contract-only tokens)
    for tok in (DHIWAY_CONTRACT if be == "signals" else SIGNALS_CONTRACT):
        if tok in t:
            add("critical", "leakage",
                f"This bot talks to the {mine} system, but its script still mentions "
                f"\"{tok}\" — a field or address belonging to the {other} system.",
                {"token": tok, "this_backend": mine, "other_backend": other})

    # 2. phone-doubling template
    if be == "signals" and re.search(r"(?<![+\w])91\$\{contact_phone\}", t):
        add("critical", "phone-doubling",
            "The script puts \"91\" in front of the caller's phone number, but that number already "
            "starts with 91 — so the bot builds 9191… and the caller lookup fails.",
            {"found": "91${contact_phone}", "should_be": "${contact_phone}"})
    if be == "dhiway" and ("+91${contact_phone}" in t or "+91<contact_phone>" in t):
        add("critical", "phone-doubling",
            "The script puts \"+91\" in front of the caller's phone number, but that number already "
            "carries +91 — so the bot builds +91+91… and the caller lookup fails.",
            {"found": "+91${contact_phone}", "should_be": "${contact_phone}"})

    # 3. memory-injection block
    if "{${contact_memory}}" not in t:
        add("critical", "memory-block",
            "The block that feeds in what we already know about the caller is missing, so this bot "
            "starts every call blind and will re-ask things the caller already answered.",
            {"expected_block": "{${contact_memory}}"})

    # 4. Signals seeker enum-exactness (only prompts that carry the new Phase-2 fields)
    if be == "signals" and p["seeker"] and "educationCategory" in t:
        for enum in ["ITI / Other Vocational Trainings", "Polytechnic / Diploma", "3-5 Years", "B.Tech/B.E."]:
            if enum not in t:
                add("critical", "enum-drift",
                    f"The answer option \"{enum}\" is missing or reworded. The backend accepts only this "
                    f"exact wording, so anything else makes saving the caller's profile fail.",
                    {"expected_option": enum})

    # 5. required sections by role
    if "Graceful Exit" not in t and "graceful exit" not in t.lower():
        add("major", "missing-section",
            "No \"Graceful Exit\" section — the part that tells the bot how to end a call politely when "
            "the caller declines or wants to stop.", {"section": "Graceful Exit"})
    # A toolless bot (e.g. the TRRAIN follow-up campaign) has no profile flow BY DESIGN — it only
    # talks and listens. Requiring get_profile of it is a false positive, so exempt it explicitly.
    toolless = "You have no tools" in t
    if p["seeker"] and not toolless and "get_profile" not in t:
        add("major", "missing-section",
            "This is a job-seeker bot, but its script never looks the caller up (no get_profile), so it "
            "cannot tell a returning caller from a brand-new one.", {"section": "get_profile"})
    if p["agent"] == "DKB" and "create_job" not in t:
        add("major", "missing-section",
            "This is an employer bot, but its script never posts the job (no create_job) — the whole "
            "point of the call would go unsaved.", {"section": "create_job"})
    return f


def sync_parity(prompts):
    """Compare each Hindi/Kannada twin pair. Same bot, two languages -> same skeleton expected."""
    out = []; by = {}
    for p in prompts:
        by.setdefault((p["agent"], p["direction"], p["backend"]), {})[p["lang"]] = p
    for key, L in by.items():
        if "hi" in L and "kn" in L:
            h = len(re.findall(r"(?m)^#{1,2} ", L["hi"]["text"]))
            k = len(re.findall(r"(?m)^#{1,2} ", L["kn"]["text"]))
            d = abs(h - k)
            if d > 2:
                sev = "major" if d > 6 else "minor"
                agent, direction, backend = key
                out.append({
                    "severity": sev, "category": "sync-drift",
                    "file": L["hi"]["path"], "bot": L["hi"]["bot"], "agent": agent,
                    "blurb": L["hi"]["blurb"],
                    "message": (
                        f"The Hindi and Kannada versions of this bot are laid out differently — Hindi has "
                        f"{h} sections, Kannada has {k}. Both languages are meant to follow the same script, "
                        f"so a gap can mean one language is missing a rule the other has. A small gap is "
                        f"usually just formatting."),
                    "detail": {"hindi_sections": h, "kannada_sections": k, "difference": d,
                               "kannada_file": L["kn"]["path"]}})
    return out


def coverage_gap(prompts):
    """Self-check: is any LIVE conversation deploy target missing from this suite?

    Added 2026-08-05 after two live bots (dkb-hi-in, dkb-kn-in) sat unchecked for days because
    discover_prompts() hard-codes its file list while raya/agents.json is the real fleet. A suite
    that can silently under-cover the fleet is worse than no suite: the digest reported "16 bots
    checked" and read as full coverage. This makes that failure loud instead of invisible.
    """
    out = []
    try:
        d = json.load(io.open(os.path.join(REPO, "raya/agents.json"), encoding="utf-8"))
        targets = d["targets"] if isinstance(d, dict) and "targets" in d else d
        live = {t["file"]: t.get("id", "?") for t in targets
                if t.get("kind") == "conversation" and t.get("deploy")}
    except Exception as e:
        return [{"severity": "major", "category": "coverage", "file": "raya/agents.json",
                 "bot": "(suite self-check)", "agent": "-", "blurb": "regression suite coverage",
                 "message": f"Could not read the deploy manifest to verify fleet coverage ({e}); "
                            f"this suite cannot prove it checked every live bot.", "detail": {}}]
    checked = {p["path"] for p in prompts}
    for f, tid in sorted(live.items()):
        if f not in checked:
            out.append({"severity": "critical", "category": "coverage", "file": f,
                        "bot": f"(unchecked: {tid})", "agent": "-",
                        "blurb": "a live bot this suite is not checking",
                        "message": (f"'{f}' is a LIVE deploy target ({tid}) but this daily suite is "
                                    f"not checking it — so nothing here says anything about that "
                                    f"bot's health. Add it to discover_prompts()."),
                        "detail": {"target_id": tid}})
    return out


def main():
    prompts = discover_prompts()
    findings = coverage_gap(prompts)
    bots = []
    for p in prompts:
        fs = check(p)
        for x in fs:
            x.update({"file": p["path"], "bot": p["bot"], "agent": p["agent"], "blurb": p["blurb"]})
            findings.append(x)
        bots.append({"bot": p["bot"], "blurb": p["blurb"], "agent": p["agent"], "file": p["path"],
                     "findings": 0})
    findings += sync_parity(prompts)

    counted = {}
    for x in findings:
        counted[x["bot"]] = counted.get(x["bot"], 0) + 1
    for b in bots:
        b["findings"] = counted.get(b["bot"], 0)

    order = {"critical": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda x: order.get(x["severity"], 3))
    crit = [x for x in findings if x["severity"] == "critical"]
    maj  = [x for x in findings if x["severity"] == "major"]
    mino = [x for x in findings if x["severity"] == "minor"]

    outdir = os.path.join(REPO, "raya/regression")
    io.open(os.path.join(outdir, "latest-report.json"), "w", encoding="utf-8").write(
        json.dumps({"prompts_checked": len(prompts), "total_findings": len(findings),
                    "bots": bots, "critical": crit, "major": maj, "minor": mino, "all": findings},
                   ensure_ascii=False, indent=1))

    lines = ["# Static regression report", "",
             f"Prompts checked: **{len(prompts)}** | Findings: **{len(findings)}** "
             f"(critical **{len(crit)}**, major **{len(maj)}**, minor **{len(mino)}**)", ""]
    if not findings:
        lines.append("No static findings — all prompts clean.")
    else:
        for sev in ("critical", "major", "minor"):
            g = [x for x in findings if x["severity"] == sev]
            if g:
                lines.append(f"## {sev.upper()} ({len(g)})")
                for x in g:
                    lines.append(f"- **{x['bot']}** (`{x['file']}`) — {x['message']}")
                lines.append("")
    io.open(os.path.join(outdir, "latest-report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"Static regression: {len(prompts)} prompts | {len(crit)} critical, {len(maj)} major, {len(mino)} minor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
