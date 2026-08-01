#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn latest-report.json into a well-formatted HTML digest (email body / job summary).

Usage: python3 raya/regression/build_digest.py [daily|weekly]  > digest.html
Reads raya/regression/latest-report.json (produced by static_regression.py).
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
kind = (sys.argv[1] if len(sys.argv) > 1 else "daily").capitalize()
r = json.load(open(os.path.join(REPO, "raya/regression/latest-report.json"), encoding="utf-8"))

crit, maj = r["critical"], r["major"]
minor = [x for x in r["all"] if x["severity"] == "minor"]
n = r["prompts_checked"]

def chip(num, label, ok=False):
    bg, bd, fg = ("#f2fbf4", "#cdeccf", "#137333") if ok else ("#f7f8fa", "#e0e0e0", "#666")
    return (f'<td style="padding:8px 16px;background:{bg};border:1px solid {bd};border-radius:6px;'
            f'text-align:center"><div style="font-size:22px;font-weight:700;color:{fg if ok else "#1a1a1a"}">'
            f'{num}</div><div style="font-size:12px;color:{fg}">{label}</div></td><td style="width:10px"></td>')

def section(title, items, color):
    if not items:
        return ""
    rows = "".join(
        f'<div style="margin-bottom:4px">· <span style="color:{color};font-weight:600">[{x["category"]}]</span> '
        f'<code>{x["file"]}</code> — {x["message"]}</div>' for x in items)
    return (f'<div style="font-size:13px;color:#333;border-top:1px solid #eee;padding-top:10px;margin-top:12px">'
            f'<div style="font-weight:600;margin-bottom:6px">{title} ({len(items)})</div>{rows}</div>')

clean = not crit and not maj
headline = ('<p style="margin:0 0 12px"><strong style="color:#137333">✅ No critical findings.</strong> '
            'All Signals + legacy prompts are clean — no cross-backend leakage, no phone-doubling templates, '
            'memory-injection blocks present, Signals Phase-2 enums byte-exact, required sections present.</p>'
            if clean else
            f'<p style="margin:0 0 12px"><strong style="color:#b00020">⚠ {len(crit)} critical, {len(maj)} major.</strong> '
            'Act before this ships — details below.</p>')

html = f"""<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:640px;color:#1a1a1a">
<h2 style="margin:0 0 4px">Prompt Tuner — {kind.lower()} regression digest</h2>
<div style="color:#666;font-size:13px;margin-bottom:16px">Static suite over every conversation prompt · daily static + weekly live</div>
<table style="border-collapse:collapse;margin-bottom:18px"><tr>
{chip(len(crit), "critical", ok=(len(crit)==0))}{chip(len(maj), "major")}{chip(len(minor), "minor")}{chip(n, "prompts")}
</tr></table>
{headline}
{section("Critical", crit, "#b00020")}
{section("Major", maj, "#b26a00")}
{section("Minor (informational)", minor, "#888")}
<p style="font-size:12px;color:#999;margin-top:18px;border-top:1px solid #eee;padding-top:10px">
Full report: <code>raya/regression/latest-report.md</code> (attached to the workflow run as an artifact).</p>
</div>"""

sys.stdout.write(html)
