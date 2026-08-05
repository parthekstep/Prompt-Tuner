# N-language parity — master + N mirrors

Mechanics for `/sync-check` when a bot has **more than two** languages. Two languages
(Hindi ↔ Kannada) is the special case of this, not the model. Nothing here enumerates a language
list: the language set is always **discovered** from `raya/agents.json`, so taking a bot into an
eighth language requires no edit to this file or to `SKILL.md`.

Read together with `../../update-prompt/reference/prompt-anatomy.md` (the AGNOSTIC / SPECIFIC /
MIXED taxonomy) — every parity decision below depends on those tags.

---

## 1. Resolving the family

### Sync family
A **sync family** is the set of files that are *the same bot in different languages*. Key it on
`(bot, direction, backend/variant)`. Files from different families are **not** each other's
mirrors and must never be diffed against each other — e.g. `KKB Placeholder Kannada.md` (legacy
Dhiway) is not a mirror of `KKB Placeholder Hindi Signals.md` (Signals DPG), and an outbound
prompt is not a mirror of an inbound one.

Print every family and its languages straight from the manifest:

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 -c "
import json, collections
targets = json.load(open('raya/agents.json'))['targets']
fam = collections.defaultdict(dict)
for t in targets:
    if t.get('kind') != 'conversation':      # memory/output prompts have no language twin
        continue
    variant = 'signals' if (t.get('signals') or 'Signals' in t['file']) else 'legacy'
    fam[(t['agent'], t['direction'], variant)][t['language']] = (t['id'], t['file'])
for key in sorted(fam):
    langs = fam[key]
    print(f\"{key[0]} · {key[1]} · {key[2]}  ({len(langs)} lang)\")
    for lang in sorted(langs):
        tid, f = langs[lang]
        print(f'    {lang:4} {tid:22} {f}')
"
```

A family with **one** language has nothing to mirror → report and stop.

### Master language
Resolution order — first hit wins:
1. An explicit `master_language` on the project/family block of the standing-regression
   **fleet manifest** `raya/regression/fleet.json` (not created yet — see `/register-bot`), or a
   target flagged `"master": true` in the **deploy manifest** `raya/agents.json`.
2. The `master_language` recorded on a `raya/divergences.json` entry for that family.
3. The repo default recorded in the root `CLAUDE.md` sync rule for that bot (today: **Hindi**
   for KKB / DKB / Maya — "the Hindi file is the source of truth").
4. For a newly onboarded project with none of the above: **ask the owner**, then get it written
   into the manifest by `/register-bot`. Do not guess, and do not silently treat whichever file
   is largest as the master.

The master is the baseline for every comparison. Mirrors are compared **against the master**,
never against each other — that keeps the work O(N) and stops two mirrors from ratifying a shared
mistake.

---

## 2. What must match, what must differ

This is the false-positive firewall. With 2 languages a spurious flag is noise; with 8 it drowns
the signal, and the reader stops reading the audit.

| Content | Across languages | Flag when it differs? |
|---|---|---|
| **AGNOSTIC** — call flow, phase/step structure, conditions and routing, input-variable names, tool names, JSON payloads and field names, fixed params, enum literals, prohibited-behavior rules, dignity/safety checks, section skeleton | byte-identical | **YES — this is drift** |
| **MIXED — the rule half** — the English instruction wrapping a spoken line | byte-identical | **YES — this is drift** |
| **MIXED — the spoken half** — the quoted line inside the rule | adapted per language | **NO** |
| **SPECIFIC** — spoken lines, greetings, example dialogues, TTS number/money/time word spellings, script rules, tone markers, culturally-adapted banned phrases, place and person names | different by design | **NO — never flag merely for differing** |

**Never flag a mirror because:**
- its spoken lines are in a different script or idiom (that is the entire point);
- its numbers/money/times are spelled as words differently (`ಹದಿನೆಂಟು ಸಾವಿರ` vs `अठारह हज़ार`);
- its example dialogue uses different place/person names (Bengaluru/Mysuru vs Pune/Ghaziabad);
- its banned-phrase list is culturally adapted;
- a section is longer or shorter, or has different line wrapping;
- **the file has more or fewer heading lines** — count parity is not content parity.

**Always flag when:**
- a heading exists in the master and not in the mirror (or vice versa);
- an AGNOSTIC rule, condition, gate, or ordering exists on one side only;
- a `${variable}`, tool name, payload field, fixed param or enum literal appears on one side only;
- a variable/tool/payload name has been **translated or transliterated** in a mirror (always a
  bug, never a legitimate localization);
- rule/instruction prose in any file is written in the target language instead of English
  (a bug in its own right — report it, do not propagate it);
- the memory-injection block is present but its heading or lead line has been translated or
  otherwise altered — the block is verbatim English in **every** language (see Pass 4);
- a required spoken element the master added has **no counterpart at all** in the mirror
  (a new fallback line, a new TTS category, an example for a newly added branch) — this is a
  **spoken-content gap**, reported separately from AGNOSTIC drift because the fix is a
  translation, not a copy.

---

## 3. The five comparison passes

Run all five for each mirror, master-vs-mirror. Passes 1 and 3 are mechanical and cheap — do them
first; they localize the reading you have to do in passes 2, 4, 5.

### Pass 1 — skeleton (heading sets)
```bash
M="KKB/KKB Placeholder Hindi Signals.md"        # master
X="KKB/KKB Placeholder Kannada Signals.md"     # mirror
diff <(grep -oE '^#{1,3} .*' "$M") <(grep -oE '^#{1,3} .*' "$X")
```
Headings are English in every language file, so this diff is meaningful across scripts. Lines
only in the master = **missing sections in the mirror**. Lines only in the mirror = mirror-only
content (either drift the other way, or a registered divergence). Reordering matters too — the
step/phase order is AGNOSTIC.

**One expected false positive:** a heading that *names its own script or language* differs by
design — e.g. the real KKB Signals pair differs only at
`## English-origin words are allowed only in Devanagari transliteration` vs
`## … only in Kannada transliteration`. Same section, same rule, correctly localized noun. Match
headings by **intent**, not string equality, and never "reconcile" a script name.

Note that pass 1 will **not** surface a divergence that lives in section *bodies* (the
2026-08-04 ಮಾಯಾ/Maya persona + opening-line + intro-turn-rule divergence changes no headings).
The registry is therefore consulted at the section-body level, in passes 2–3.

### Pass 2 — taxonomy walk (section by section)
For each heading present on both sides, look up its tag in `prompt-anatomy.md` and apply the
table in § 2. For MIXED sections, read only the English rule prose and compare that; ignore the
quoted spoken text. Record per section: tag, status, which side is ahead, what the laggard is
missing.

### Pass 3 — token census (the N-language workhorse)
Every machine-readable token must be identical across all languages. This pass finds most real
drift without reading prose, and is the one to script.

```bash
# input variables
diff <(grep -oE '\$\{[A-Za-z0-9_]+\}' "$M" | sort -u) \
     <(grep -oE '\$\{[A-Za-z0-9_]+\}' "$X" | sort -u)

# tool names + payload field names + fixed params (repo convention: backticked snake_case)
diff <(grep -oE '`[a-z][a-z0-9_.]{2,}`' "$M" | sort -u) \
     <(grep -oE '`[a-z][a-z0-9_.]{2,}`' "$X" | sort -u)

# enum / fixed-value literals inside tool sections (exact English strings the backend requires)
diff <(grep -oE '"[A-Za-z][A-Za-z0-9 ./&+-]{2,40}"' "$M" | sort -u) \
     <(grep -oE '"[A-Za-z][A-Za-z0-9 ./&+-]{2,40}"' "$X" | sort -u)
```
Interpretation: any token on one side only is drift **or** a localization bug. The third command
is the noisiest (English words appear inside prose) — read its output scoped to the tool/payload
sections, and treat a missing backend enum (`"ITI / Other Vocational Trainings"`,
`"Polytechnic / Diploma"`, `"3-5 Years"`) as critical, since an inexact enum makes the write fail.

### Pass 4 — standing-rule presence
Confirm every repo-wide mandatory block is present in **each** language, not just the master —
most importantly the memory-injection block, which must appear verbatim in every conversation
prompt of a memory-enabled bot. Check **all three lines as one exact string** — grepping only for
`{${contact_memory}}` passes a mirror whose `### Contact context` heading or `Here is the caller
context:` lead line was translated or reworded, which is exactly the failure the rule exists to
prevent (bug E3):
```bash
python3 - "<file1>" "<file2>" ... <<'PY'
import io, sys
BLOCK = "### Contact context\nHere is the caller context:\n{${contact_memory}}"
for p in sys.argv[1:]:
    t = io.open(p, encoding="utf-8").read()
    state = ("VERBATIM OK" if BLOCK in t
             else "PRESENT BUT ALTERED" if "${contact_memory}" in t
             else "MISSING")
    print("%-58s memory-block: %s" % (p, state))
PY
```
`PRESENT BUT ALTERED` and `MISSING` are both bugs, and both are fixed by restoring the exact
three-line English block — never by translating it to match the mirror.

Same treatment for any section the bot's use case requires per
`../../prompt-analyser/reference/section-checklists.md` (Graceful Exit, consent gate, …).

### Pass 5 — changelog corroboration
Read `<Bot>/CHANGELOG.md` newest-first. For each entry, check which language files actually
carry its content. An entry whose change is present in the master and 3 of 7 mirrors names the
exact languages that were never updated — and gives you the date the drift started. An entry that
**declares** a divergence with no matching `raya/divergences.json` record is a registry gap.

---

## 4. Report shape

With N languages a prose diff does not scale — lead with the matrix so a reader sees at a glance
which of 8 languages is behind, then give detail only for the rows that are not clean.

### Headline (one line)
```
KKB · outbound · signals — master hi · 8 languages: 5 CURRENT, 2 LAGS, 1 UNCERTAIN · 3 differences suppressed as registered divergences
```

### Table 1 — per-language status (one row per mirror; the master is the baseline)

| Language | In sync? | Missing AGNOSTIC content | Spoken-content gaps | Registered divergences | Verdict |
|---|---|---|---|---|---|
| kn (`kkb-kn-signals`) | ✗ | Step 3.5 conditional-qualification block; `otherHelpNeeded` payload field | — | 1 (`kkb-kn-signals-maya-name`) | **LAGS (2)** |
| te (`kkb-te-signals`) | ✓ | — | TTS number-words missing for lakh/crore | 0 | **CURRENT (spoken gap)** |
| ta (`kkb-ta-signals`) | ✓ | — | — | 0 | **CURRENT** |
| mr (`kkb-mr-signals`) | ? | intro-turn rule differs — deliberate or drift? | — | 0 | **UNCERTAIN** |
| bn (—) | — | file not created | — | 0 | **MISSING** |

Verdict vocabulary (use these words exactly, so the report is greppable):
- **CURRENT** — no AGNOSTIC drift. Add `(spoken gap)` if a translation is owed.
- **LAGS (n)** — n AGNOSTIC drift items; the master is ahead. This is the actionable state.
- **AHEAD** — the mirror carries AGNOSTIC content the master lacks. Escalate to the master
  first via `/update-prompt`, then fan out; never mirror-to-mirror.
- **DIVERGED (registered)** — the only differences found are covered by the registry. Not drift.
- **UNCERTAIN** — a difference that could be deliberate. Ask; do not guess.
- **MISSING** — no file for this language yet (a `/translate-prompt` job, not a sync job).

### Table 2 — drift detail (only for rows that are not CURRENT)

| Language | Section | Tag | Status | Ahead | Missing from laggard |
|---|---|---|---|---|---|
| kn | Step 3.5 — Phase 1 | MIXED | **AGNOSTIC DRIFT** | master (hi) | conditional-qualification follow-up rule |
| kn | Introduction / Intro-turn rules | MIXED | EXPECTED (registered `kkb-kn-signals-maya-name`) | — | — |
| te | TTS Normalization Rules | SPECIFIC | spoken gap | master (hi) | lakh/crore number-words |

Then, per laggard, the proposed reconciliation (verbatim copy vs translate-and-adapt), and the
snapshot label you will take before writing.

---

## 5. Registry — `raya/divergences.json`

### Why this location
It lives next to `raya/agents.json` because it is **fleet data**, not skill prose: `/sync-check`,
`/update-prompt`, `/port-feature` and the daily static suite (`raya/regression/`) all need to load
it, it must be git-tracked and reviewable in a diff, and it must be readable by a Python check
without parsing markdown. Putting it inside a skill folder would hide fleet truth inside one
skill's private reference material.

### Schema
Top level: `schema_version`, `_note`, `_schema` (self-documenting field notes), `divergences: []`.

Each entry:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable kebab-case key, cited verbatim in audit reports |
| `project` / `bot` | yes | the bot the divergence belongs to (e.g. `KKB`) |
| `sync_family` | yes | `bot · direction · variant` — scopes the entry to one family |
| `targets` | yes | `raya/agents.json` target ids the divergence applies to |
| `master_language` | yes | the family's master at the time of approval |
| `languages_affected` | yes | the language codes that legitimately differ |
| `direction` | yes | `mirror-only` (mirror has content the master lacks), `master-only`, or `both-differ` |
| `scope[]` | yes | the sections/lines that legitimately differ — each with `section` (heading, matched by intent), `kind` (`persona` / `spoken-line` / `rule`), `what` (plain English), and `contains[]` (tokens a script can match in the actual delta) |
| `why` | yes | the owner's reason, in plain English |
| `approved_by` | yes | the human who decided (name + how: "explicit instruction", "email approval") |
| `approved_on` | yes | `YYYY-MM-DD` |
| `changelog_ref` | yes | the `CHANGELOG.md` entry that records the edit |
| `still_must_match` | yes | everything the entry does **not** excuse — audited normally |
| `not_applied_to` | no | sibling targets deliberately left alone (stops scope creep) |
| `review_on` | no | date after which the entry must be re-confirmed; past-due → registry gap |
| `expires` | no | hard expiry; after it the divergence is drift again |

### Matching rule (how a check uses it)
A difference is **EXPECTED (registered divergence)** only if **all** hold:
1. the file's target id is in `targets` (and its family matches `sync_family`);
2. the file's language is in `languages_affected`;
3. the differing section matches a `scope[].section` (by intent, not exact string);
4. the actual delta text contains at least one of that scope item's `contains` tokens.

Anything else — a different section, a different language, a delta with none of the tokens — is
**UNREGISTERED** and gets flagged as drift. A registry entry is a narrow carve-out, never a
blanket "this language is allowed to differ".

### Staleness
If an entry's `contains` tokens are **no longer present** in the files it covers, the divergence
was undone (probably by a naive sync). Report it as a **registry gap / possible silent revert**
and ask the owner — do not quietly delete the entry, and do not quietly re-apply it.

### Who writes entries
`/update-prompt` and `/port-feature` — in the same change as the prompt edit and the changelog
entry — whenever they knowingly apply a change to some languages of a family and not others, or
otherwise suspend the mirror rule. `/sync-check` only **reads** the registry, except in step 10,
where it may add the entry for a divergence the owner just confirmed during reconciliation.
