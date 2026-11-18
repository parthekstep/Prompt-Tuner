#!/usr/bin/env python3
"""Read the AI DPG prompt export for the Blue Dots bot on VoicERA, and write change proposals for it.

On VoicERA the conversation runs on AI DPG (Agent Core). Its prompts are not one file: they are a
persona, 19 phase prompts, fixed lines, understanding examples and tool texts in AI DPG's config repo,
changed only through a PR there. AI DPG shares them as one read-only JSON export in which every value
names its `source` (file -> key). We propose changes keyed by that source; they apply them.
Guide: raya/voicera/dpg/ai-dpg-prompts-for-prompt-engineers.md.

The export is kept out of git (raya/voicera/dpg/ is ignored): it is AI DPG's config.

Commands
  phases                         every phase: id, tools, where it can route next
  show <phase-id>                one phase: prompt, fixed lines, pending questions, tools, routing
  locate "<words>"               which source holds this text (a line the bot said, a rule)
  speech [--phase ID]            every spoken (Devanagari / Kannada script) line, with its source
  diff <old.json> [new.json]     what changed between two exports, by source
  propose <source> --old "<text>" --new "<text>" --why "<reason>" [--field F]
                                 add a proposal to raya/voicera/dpg/proposals/<date>.json, after
                                 checking the old text is really at that source in the export
Options: --export FILE (default raya/voicera/dpg/blue-dots-hindi-prompts.json)
"""
import argparse, datetime as dt, difflib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPG = os.path.join(ROOT, "raya", "voicera", "dpg")
DEFAULT = os.path.join(DPG, "blue-dots-hindi-prompts.json")
SPOKEN = re.compile(r"[ऀ-ॿಀ-೿]")          # Devanagari or Kannada script


def leaves(node, source=None, field=""):
    """Yield (source, field, text) for every string under a node that names a source."""
    if isinstance(node, dict):
        src = node.get("source", source)
        for k, v in node.items():
            if k == "source":
                continue
            sub = k if src != source or not field else f"{field}.{k}"
            yield from leaves(v, src, sub)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from leaves(v, source, f"{field}[{i}]")
    elif isinstance(node, str) and source:
        yield source, field, node


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def load(path):
    if not os.path.exists(path):
        sys.exit(f"no export at {path}: save AI DPG's JSON export there (it is git-ignored)")
    return json.load(open(path, encoding="utf-8"))


def cmd_phases(d, a):
    for p in d["phases"]:
        nxt = sorted({r.get("next_subagent_id") or r.get("to") or "?"
                      for r in (p.get("routing") or {}).get("rules", []) if isinstance(r, dict)})
        tools = p.get("tools_offered") or []
        print(f"{p['id']:24} tools={','.join(tools) if tools else '-':34} next={','.join(nxt) or '-'}")


def cmd_show(d, a):
    p = next((p for p in d["phases"] if p["id"] == a.phase), None)
    if not p:
        sys.exit(f"no phase {a.phase}; see `phases`")
    print(f"# {p['id']}: {p.get('name', '')}\n{p.get('description', '')}\n")
    for key in ("system_prompt", "fixed_lines", "pending_questions", "tools_offered", "runs_before_model", "routing"):
        if p.get(key):
            print(f"## {key}" + (f"   [{p[key]['source']}]" if isinstance(p[key], dict) and "source" in p[key] else ""))
            v = p[key]
            print(v["text"] if isinstance(v, dict) and "text" in v else json.dumps(v, ensure_ascii=False, indent=1))
            print()


def cmd_locate(d, a):
    q = norm(a.words)
    hits = [(s, f, t) for s, f, t in leaves(d) if q in norm(t)]
    if not hits:                                                     # closest lines instead
        scored = []
        for s, f, t in leaves(d):
            for line in t.splitlines():
                r = difflib.SequenceMatcher(None, q, norm(line)).ratio()
                if r > 0.5:
                    scored.append((r, s, f, line.strip()))
        for r, s, f, line in sorted(scored, reverse=True)[:8]:
            print(f"~{r:.2f}  {s}  [{f}]\n       {line[:160]}")
        if not scored:
            print("not found")
        return
    for s, f, t in hits:
        flat = re.sub(r"\s+", " ", t).strip()
        i = flat.lower().find(q)
        print(f"{s}  [{f}]\n       ...{flat[max(0, i - 60):i + len(q) + 60]}...")


def cmd_speech(d, a):
    for s, f, t in leaves(d):
        if a.phase and f"id={a.phase}]" not in s:
            continue
        for line in t.splitlines():
            if SPOKEN.search(line):
                print(f"{s}  [{f}]\n    {line.strip()}")


def cmd_diff(d, a):
    old = {(s, f): t for s, f, t in leaves(load(a.old))}
    new = {(s, f): t for s, f, t in leaves(load(a.new) if a.new else d)}
    for k in sorted(set(old) | set(new)):
        if old.get(k) == new.get(k):
            continue
        tag = "ADDED" if k not in old else "REMOVED" if k not in new else "CHANGED"
        print(f"{tag}  {k[0]}  [{k[1]}]")
        if tag == "CHANGED":
            for l in difflib.unified_diff(old[k].splitlines(), new[k].splitlines(), lineterm="", n=1):
                if not l.startswith(("---", "+++")):
                    print("    " + l)


def cmd_propose(d, a):
    matches = [(s, f, t) for s, f, t in leaves(d) if s == a.source and (not a.field or f == a.field)]
    if not matches:
        sys.exit(f"no source {a.source!r} in the export")
    found = [(s, f, t) for s, f, t in matches if a.old in t]
    if len(found) != 1:
        sys.exit(f"the old text is at {len(found)} places under that source (need exactly 1; add --field)")
    s, f, t = found[0]
    meta = d.get("_meta", {})
    path = os.path.join(DPG, "proposals", dt.date.today().isoformat() + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {
        "against_commit": meta.get("commit"), "language": meta.get("language"), "proposals": []}
    doc["proposals"].append({"source": s, "field": f, "old": a.old, "new": a.new, "why": a.why})
    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"added to {os.path.relpath(path, ROOT)} ({len(doc['proposals'])} proposals, export commit {meta.get('commit')})")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export", default=DEFAULT)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("phases")
    x = s.add_parser("show"); x.add_argument("phase")
    x = s.add_parser("locate"); x.add_argument("words")
    x = s.add_parser("speech"); x.add_argument("--phase")
    x = s.add_parser("diff"); x.add_argument("old"); x.add_argument("new", nargs="?")
    x = s.add_parser("propose"); x.add_argument("source"); x.add_argument("--old", required=True)
    x.add_argument("--new", required=True); x.add_argument("--why", required=True); x.add_argument("--field")
    a = p.parse_args()
    d = None if a.cmd == "diff" and a.new else load(a.export)
    globals()["cmd_" + a.cmd](d, a)


if __name__ == "__main__":
    main()
