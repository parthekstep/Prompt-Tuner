---
name: register-bot
description: Register a NEW bot (or a new language/direction variant of an existing bot) into the Prompt Tuner so every skill and script can operate on it — creates the bot's folder + prompt files + CHANGELOG, adds it to the project-aware path map in the root CLAUDE.md, writes its deploy target(s) into raya/agents.json with hand-copied Raya uuids, adds it to the standing-regression fleet manifest, and hands off to /generate-test-cases. Use right after /onboard, or whenever someone says "add this bot to the tuner", "register the new bot", "make this bot deployable", "wire up Purple Dots", "add a Tamil variant", or a skill fails because the bot isn't in the path map / agents.json.
---

# Register Bot — make a new bot operable by the tuner

`/onboard` ends with a filled intake summary. That summary is not yet a bot the tuner can work
on: no folder, no path-map row, no deploy target, no regression coverage. **This skill closes
that gap** — it is the purely mechanical, fully verifiable step between "we finished intake" and
"every skill in this repo resolves this bot".

Everything here is bookkeeping: folders, one markdown file per language, a JSON target, two
manifest rows. **Nothing here writes prompt prose and nothing here deploys.** Prompt content
comes from the customer (via `/onboard`), from `/update-prompt`, or from `/translate-prompt`;
deploying is `scripts/raya_deploy.py deploy`, run later and separately.

The repo now serves **multiple projects** (Blue Dots: KKB / DKB / Maya; Purple Dots: the
disability rail; more to come). Assume **N projects, N bots, N languages** throughout — never
hard-code a bot list or a language pair.

---

## Inputs this skill needs before it can run

Get these from the intake summary (`raya/intake/<bot-id>.md`) or by asking. Do not guess.

| Input | Example | Why it is needed |
|---|---|---|
| **Project** | `purple-dots` (slug) / `Purple Dots` (label) | the `project` field everywhere; digest labels (G7) |
| **Bot name + folder slug** | `Purple Dots` → folder `Purple Dots/` | folder + filenames + target ids |
| **Languages, master first** | `hi` (master), `ta`, `mr` | one conversation file + one target per language |
| **Directions** | outbound, inbound, or both | one target per language **per direction** |
| **Which prompts exist** | conversation only / + memory / + output | which files to create; memory-block requirement |
| **Backend / variant tag** | `signals`, `dhiway`, or none | fleet `backend`, regression checks, target id suffix |
| **Bot role** | seeker / provider / service-navigator | which regression tool checks apply |
| **Raya uuid per agent, per env** | from `raya_deploy.py list` | `raya_agent_id.{prod,staging}` |
| **Live agent name on Raya** | `Purple Dots Hindi` | `raya_name` + `expected_name_contains` guard |

If the bot has **no Raya presence yet**, that is fine — register it with empty uuids and
`deploy: false`, and read the customer the honest capability split in *Guardrails → Not on Raya*.

---

## Procedure

### 1. Recon — read before you write

Read, in this order, and do not skip: the root `CLAUDE.md` **File path map** section;
`raya/agents.json` (the whole file — you must match its exact key order and shape);
`raya/regression/static_regression.py`'s `discover_prompts()` and `AGENT_BLURB` (read-only — you
need the fleet fields it derives and the exact bot-label format); and one existing
`<Bot>/CHANGELOG.md` for the header format. Then check whether the bot is **already** partly
registered:

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py targets | grep -i "<bot-slug>"     # already a target?
ls -d "<Bot>" 2>/dev/null                                        # folder already there?
grep -n "<Bot>" CLAUDE.md                                        # already in the path map?
```

If any of it exists, this is a **variant addition** (new language / new direction), not a fresh
bot: skip step 2's folder creation, add only the missing files and the missing target rows, and
leave every existing row untouched.

### 2. Create the bot's folder + files (path-map convention)

**Folders are bot-named and live at the repo root — the project is metadata, not a directory
level.** `scripts/prompt-version.sh` snapshots `versions/<Agent>/` from a depth-1
`<Agent>/*.md` glob, and `static_regression.py` joins `REPO/<agent_dir>/<filename>`. Nesting a
bot under `Purple Dots/bots/…` silently breaks both. Do not invent a new layout.

```
<Bot>/
  <Bot> <Language>.md          # one per language, master first  (conversation)
  <Bot> Inbound <Language>.md  # only if the bot has a separate inbound prompt
  <Bot> Memory.md              # optional, language-agnostic, English output
  <Bot> Output.md              # optional, language-agnostic, English output
  CHANGELOG.md                 # always
```

Follow the existing naming exactly (`Purple Dots/Purple Dots Hindi.md`, matching
`DKB/DKB Hindi.md`, `Maya/Maya Hindi.md`). Keep the language token as the **language's English
name** (`Hindi`, `Kannada`, `Tamil`, `Telugu`, `Marathi`) — that is what every existing file and
every derivation rule in `static_regression.py` expects. Append a variant token after the
language when there is one (`… Hindi Signals.md`), mirroring `KKB Placeholder Hindi Signals.md`.

Content rules for this step:

- The **master-language** conversation file gets the customer's supplied prompt **pasted
  verbatim** — no reformatting, no re-wrapping, no "cleanup", no section reordering. Surgical
  rule applies to creation too: what they gave us is the baseline we diff future edits against.
- **Do not create empty stub files** for languages that have no content yet. An empty file makes
  `raya_deploy.py targets --check` pass on a bot that does not exist, and a `deploy` would blank
  a live agent. Register a language's target only once its file has real content. Non-master
  languages are produced later by `/translate-prompt`.
- If the bot has a **memory prompt**, verify every one of its conversation prompts contains this
  block **verbatim** (root `CLAUDE.md` → "Memory injection block"):

  ```
  ### Contact context
  Here is the caller context:
  {${contact_memory}}
  ```

  It is language-agnostic English in every language file — never translated, never altered. If a
  file lacks it, do not hand-patch it here: route to `/update-memory`, which owns that block.
- Seed `<Bot>/CHANGELOG.md` with the standard header (copy the format from `KKB/CHANGELOG.md`)
  plus a creation entry:

  ```
  ## YYYY-MM-DD — Registered <Bot> in the Prompt Tuner
  - **Feedback/bug:** n/a — new bot registration (project: <Project>)
  - **Change:** created <Bot>/ with <n> conversation prompt(s) (<languages>, master: <lang>),
    <memory/output present?>; added path-map rows, raya/agents.json target(s) <ids>,
    and the regression fleet entry.
  - **Files:** <every file created or edited, repo-relative>
  ```

### 3. Update the root `CLAUDE.md` path map — and make it project-aware (gap G1)

`CLAUDE.md` is the operating manual and the map every skill resolves files through. **Edits here
are additive only:** never reword, reflow, re-order or delete an existing row, heading or rule.

The existing table is `| Agent | Hindi | Kannada | Memory | Output |` — one column per language.
That shape cannot survive twelve Indic languages. Make it project-aware without breaking it:

1. **Insert** a projects index immediately under the `## File path map` intro line:

   ```markdown
   ### Projects

   | Project | Bots | Languages (master first) | Notes |
   |---|---|---|---|
   | Blue Dots | KKB, DKB, Maya | Hindi (master), Kannada | Maya is Hindi-only |
   | Purple Dots | Purple Dots | Hindi (master), … | disability rail; accessibility checks apply |
   ```

2. **Keep the existing three-row table byte-identical**, under a new heading above it:
   `### Blue Dots — file paths` (wide form, one column per language — grandfathered).

3. **Append** a new section per new project using the **long form**, which scales to N languages
   (one row per bot × language):

   ```markdown
   ### Purple Dots — file paths

   | Bot | Language | Conversation prompt | Memory | Output |
   |---|---|---|---|---|
   | Purple Dots | hi (master) | `Purple Dots/Purple Dots Hindi.md` | `Purple Dots/Purple Dots Memory.md` | `Purple Dots/Purple Dots Output.md` |
   | Purple Dots | ta | `Purple Dots/Purple Dots Tamil.md` | (same) | (same) |
   ```

4. Add one sentence under `### Projects`, once:
   *"Wide (one column per language) is grandfathered for Blue Dots; every new project uses the
   long form — one row per bot × language — so it scales to N languages. `raya/agents.json` is
   the machine-readable source of truth for deploys; this map is the human index. `/register-bot`
   maintains both."*

**Mark the master language in the map** (`hi (master)`) as the human-readable record. The
**machine-readable** master lives in `raya/regression/fleet.json`'s `master_language` (step 6) —
that is what `/sync-check` and `/translate-prompt` resolve first; the path-map row is not read by
either (resolution order: `.claude/skills/sync-check/reference/n-language-parity.md` §
*Master language*).

### 4. Register the deploy target(s) in `raya/agents.json`

**One entry per conversation prompt — per language, per direction, per variant.** Read the real
file first and match its shape exactly; append entries at the end of the `targets` array and
touch nothing else.

```json
{
  "id": "pd-hi-out",
  "project": "purple-dots",
  "file": "Purple Dots/Purple Dots Hindi.md",
  "agent": "Purple Dots",
  "language": "hi",
  "direction": "outbound",
  "kind": "conversation",
  "profile": "conversation",
  "expected_name_contains": ["Purple Dots", "Hindi"],
  "raya_name": "Purple Dots Hindi",
  "raya_agent_id": { "prod": "", "staging": "" },
  "deploy": false
}
```

- **`expected_name_contains` carries the bot token AND the language/variant token** — never a
  single generic token, which is not a guard at all (see step 5 for the live hazard).
- **`project` is the new field** this skill introduces (gap G1). Add it to new entries; backfill
  existing entries with `"project": "blue-dots"` **only if the user approves** touching them —
  otherwise leave them alone and treat a missing `project` as `blue-dots` by default.
- **`id` convention** (from the existing ids `kkb-hi-out`, `kkb-hi-in`, `dkb-kn-signals`,
  `maya-hi-in-signals`): `<bot-slug>-<lang>-<out|in>[-<variant>]`. Short, lowercase, unique. It
  is the handle every script and every report uses — pick it once and never rename it.
- **`profile` must name a profile that exists in `raya/endpoints.json`** — today
  `conversation` | `memory` | `output`. An unknown profile makes every command for that target die.
- **Memory / output prompts get their own entries** with `kind`/`profile` `memory`/`output`,
  `language: "xx"`, `direction: "postcall"`, and `deploy: false` when they are not separately
  deployable — copy `kkb-memory` / `kkb-output`. When a memory prompt *is* deployed onto the same
  agent as a conversation prompt, it reuses that agent's uuid and gets its own direction-scoped
  entry — copy `maya-out-memory` / `maya-in-memory`.
- **`deploy: false` until the uuid is in hand.** `raya_deploy.py targets` reports every
  `deploy:true` target with no uuid for the active env as `unmapped`, and `status` calls it out —
  don't add noise. Flip `deploy` to `true` in the **same edit** that pastes the uuid.
- Add an `"_note"` when the entry needs explaining (a repurposed uuid, a clone source, a pending
  Raya build) — that is the established habit in this file, e.g. the Signals entries.
- **Validate the JSON before moving on:**
  `python3 -c "import json;json.load(open('raya/agents.json'));print('ok')"`

### 5. The uuid rule — read this out loud, every time

> **The Raya agent uuid is filled in BY HAND from `python3 scripts/raya_deploy.py list`, and is
> NEVER inferred from a filename, a folder name, or a pattern in the other entries.**

```bash
python3 scripts/raya_deploy.py list          # prints: <uuid>  <live agent name>
```

Copy the uuid for the row whose **name** matches the bot/language/direction you are registering,
into `raya_agent_id.<env>` for the matching env (`prod` / `staging`; the tool picks the one
matching `RAYA_ENV` in `raya/.env`). If two live agents have confusingly similar names, stop and
ask — do not pick one.

**Why the rule is absolute — a real pitfall in this repo:** `KKB/KKB Placeholder Inbound.md` is
the **HINDI** inbound prompt. Nothing in the filename says Hindi. `Maya/Maya Inbound.md` carries
no language token at all. Any "the filename tells me the language, so the uuid must be the
Hindi-looking one" reasoning ships a prompt onto the wrong live agent.

`expected_name_contains` is the **wrong-target guard**: `deploy` aborts if the live agent's name
contains **none** of these tokens. Start with the bot token, then **tighten it once you have seen
the real names from `list`** — add the language and/or variant token (`["Purple", "Tamil"]`,
`["KKB", "Signals"]`) so a Hindi prompt can never land on the Tamil agent. A single generic token
is a weak guard, not a guard.

### 6. Add the bot to the standing-regression fleet (gaps G4 / G7)

The daily Tier-3 suite (`raya/regression/static_regression.py`, run by
`.github/workflows/regression.yml`) currently discovers its fleet from a **hard-coded file dict**
inside `discover_prompts()` — today all **18** conversation prompts (8 KKB, 6 DKB, 4 Maya), matching
the 18 `kind: conversation` targets in `raya/agents.json` — and derives language/direction/backend
from filename substrings and role from `agent_dir in ("KKB","Maya")`. A new bot is therefore
**invisible to the daily check until the fleet is config-driven.** It is invisible *loudly*, not
silently: `coverage_gap()` cross-checks the dict against every `deploy:true` conversation target in
`raya/agents.json` and emits a **critical `coverage` finding, bot `(unchecked: <target-id>)`**, for
any it does not check — which is exactly what a newly registered `deploy:true` bot will produce until
the switch below lands. (That check was added 2026-08-05, after `dkb-hi-in` / `dkb-kn-in` sat
unchecked while the digest reported the fleet as 16.)

**This skill writes the config; it does not touch the script.**

Write/extend **`raya/regression/fleet.json`**. Entry shape (one per conversation prompt, same
granularity as `agents.json`) — illustrative; **`scripts/build_fleet_manifest.py` and the existing
entries in the real file are the authority on the exact field names**, so read the file before you
append and match it key-for-key:

```json
{
  "id": "pd-hi-out",
  "project": "purple-dots",
  "project_label": "Purple Dots",
  "agent": "Purple Dots",
  "path": "Purple Dots/Purple Dots Hindi.md",
  "language": "hi",
  "language_label": "Hindi",
  "direction": "outbound",
  "backend": "signals",
  "role": "service-navigator",
  "master_language": "hi",
  "sync_group": "pd-out",
  "label": "Purple Dots Hindi · outbound · Signals",
  "blurb": "Connects people with disabilities to services and enablers — the bot phones the person, in Hindi, on the new Signals DPG backend",
  "required_tools": ["get_profile"],
  "enum_set": null
}
```

Field-by-field rationale — each one replaces a hard-coded assumption in the script:

- `id` — **must equal the `agents.json` target id** so reports, `open-items.json` and deploys join.
- `project` / `project_label` — fixes **G7**: digest bot labels are derived from the manifest
  instead of the `AGENT_BLURB` dict that knows only KKB/DKB/Maya.
- `language` / `language_label` — replaces `"kn" if "kannada" in filename else "hi"`, which
  silently calls every Tamil/Telugu/Marathi prompt Hindi.
- `direction` / `backend` — replaces the `"inbound" in filename` / `"signals" in filename`
  substring sniffing.
- `role` (`seeker` | `provider` | `service-navigator` | …) + `required_tools` — replaces
  `seeker = agent in ("KKB","Maya")` and the hard-coded "seeker needs `get_profile`, DKB needs
  `create_job`" branch. State the bot's real must-fire tools; leave `[]` if none.
- `master_language` + `sync_group` — replaces the Hindi↔Kannada **pair** parity check with
  **N-language group** parity (gap G3): every member of a `sync_group` is compared against the
  group's master. Two prompts share a `sync_group` only if their language-agnostic skeletons are
  meant to be identical (same bot, same direction, same backend).
- `label` — **must follow the existing format** `<Agent> <LanguageLabel> · <direction> ·
  <Signals|legacy>`, because `raya/regression/open-items.json` joins its curated items to bots by
  that exact string (e.g. `"KKB Kannada · inbound · legacy"`). A different format orphans the
  open items in the digest.
- `blurb` — the plain-English sentence the email digest shows a reader with no context.
- `enum_set` — names a byte-exact enum family to assert (`"signals-seeker-phase2"`), or `null`.

**Never hand-transcribe the existing fleet — generate it:**

```bash
python3 scripts/build_fleet_manifest.py --check   # is the manifest present and current?
python3 scripts/build_fleet_manifest.py           # (re)write raya/regression/fleet.json
```

The builder derives the manifest from the two authoritative sources — `raya/agents.json` and
`static_regression.py`'s `discover_prompts()` — including the exact `label` format, and cross-checks
them, so behaviour is unchanged and nothing can be silently omitted. **Review the diff** and confirm
it lists all **18** existing conversation prompts, then append the new bot's entry by hand, matching
the generated file's field names exactly. A partial manifest is worse than none — the follow-up
switch would drop every missing bot off the daily check.

Wrap the array in an object with a `_note` explaining the file's role, mirroring the house style
of `agents.json` and `open-items.json`.

**Follow-up code change to hand off (do NOT make it here):** replace `discover_prompts()`'s
hard-coded `files` dict and its filename/agent derivations with a read of
`raya/regression/fleet.json`, and drive `AGENT_BLURB` / `DIRECTION_BLURB` / `BACKEND_BLURB` and
the Hi↔Kn pair-parity check from the manifest's `blurb` / `label` / `sync_group` / `role` /
`required_tools` fields. **Acceptance test for that change:** with the generated manifest,
`python3 raya/regression/static_regression.py` must produce a `latest-report.json` **identical to
the pre-change run** for the 18 bots the dict already covers, plus new findings for the newly
registered bot — and the `unchecked:<target-id>` CRITICAL for that bot must disappear. Log
this as an explicit open item (state it in your report; add it to `open-items.json` only if the
user asks) and tell the user plainly: **until that switch lands, the new bot is in the manifest
but not yet in the daily email.**

### 7. Seed the test surface — hand off to `/generate-test-cases`

Registration makes the bot *addressable*; it does not make it *testable*. Hand off with the
intake summary's scenarios and success criteria so `/generate-test-cases` can emit:

- tester **personas** per scenario **per language** → `raya/personas/<lang>-<behavior>.md`
  (gap G5 — personas exist only for `hi`/`kn` today; a new language needs its own, with an
  English instruction header and in-language spoken lines)
- a **bot-specific checklist** →
  `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` (gap G6), with explicit
  pass/fail detection per item (what in `tool_calls` / spoken turns / `call_output` proves it)
- the bot still also grades against
  `.claude/skills/voice-test/reference/checklists/generic.md` — **every** bot does. For a bot
  serving people with disabilities, the accessibility items (pacing, silence tolerance,
  repetition on request, never making disability the identity of the call) live in the **generic**
  checklist, not a per-bot one (gap G8).

Also recommended, in this order, before any live call: **`/prompt-analyser`** on the newly filed
master prompt (read-only pre-flight against the learned bug patterns in
`.claude/skills/prompt-analyser/reference/bug-patterns.md`), then
**`/generate-test-cases`**, then **`/voice-test`**.

### 8. Verify the registration — it is not done until the target resolves

Run all of these and paste the real output into your report. **Registration is not complete
until `targets` lists the new id and its file resolves.**

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"

# a) JSON is valid (both manifests)
python3 -c "import json;json.load(open('raya/agents.json'));json.load(open('raya/regression/fleet.json'));print('json ok')"

# b) the new target exists, with the right lang/dir, and its file is found
python3 scripts/raya_deploy.py targets | grep -i "<bot-slug>"
python3 scripts/raya_deploy.py targets --check      # errors if any deploy:true file is missing

# c) sane live state (only meaningful once a uuid is set + deploy:true)
python3 scripts/raya_deploy.py status <target-id>   # in-sync | drifted | unmapped | missing-file | unreachable
python3 scripts/raya_deploy.py diff   <target-id>   # read-only; who is ahead, repo or live?

# d) the daily suite still runs clean (it will not see the new bot until the G4 switch)
python3 raya/regression/static_regression.py

# e) the path map resolves the files it claims
grep -n "<Bot>" CLAUDE.md
ls -1 "<Bot>/"

# f) the snapshot tool knows the new bot (it is the gate on the FIRST deploy)
bash scripts/prompt-version.sh list "<Bot>"
```

Expected, and how to read it:

| Check | Pass looks like | If not |
|---|---|---|
| `targets \| grep` | one row per registered variant, correct `lang/dir`, `file?` = `ok` | fix the `file` path — do not create an empty file to satisfy it |
| `targets --check` | `OK: every deploy:true target's file exists.` | a `deploy:true` row points at nothing — set `deploy:false` or fix the path |
| `status` | `unmapped` while the uuid is blank (expected); `in-sync`/`drifted` once mapped | `unreachable` → check `raya/.env` + `RAYA_ENV`, not the manifest |
| `diff` | a clean diff either way — **repo ahead is normal for a brand-new bot** | if **live is ahead**, `pull` it into the repo and reconcile BEFORE any edit |
| `static_regression.py` | the same pre-existing findings, **plus** one CRITICAL `unchecked:<new-target-id>` from `coverage_gap()` — expected until the G4 switch lands | any *other* new failure means you touched something you shouldn't have — revert it |
| `prompt-version.sh list "<Bot>"` | `== <Bot> ==` (`(no snapshots)` is fine — it resolved) | `error: unknown agent …` → the bot is not resolvable, so it can be neither snapshotted nor deployed; fix per the Guardrails bullet **before** the first deploy |

Then report: files created, path-map rows added, target ids registered (with uuid present/absent),
fleet entry, the G4 follow-up, and the exact next command the user should run.

---

## Test before done

Registration itself is **verified statically** — by step 8, not by a phone call. There is no
live behaviour to test yet, and you may not manufacture one by deploying.

But the moment any **prompt content** changes (the first `/update-prompt`, the first
`/translate-prompt` output, the first `/update-memory`), the repo's mandatory testing regime
applies in full (root `CLAUDE.md` → "Testing is mandatory" and "The three testing tiers"):

1. **Tier 1 — fix verification.** Reproduce the exact target scenario on the real bot and confirm
   the new behaviour in a live transcript. No transcript, no claim.
2. **Tier 2 — blast-radius regression.** Test what the change could have broken next door — the
   same section, the shared agnostic logic, the mirrored sibling language, the tool payload touched.
3. **Tier 3 — daily standing check.** `raya/regression/` via the scheduled cloud worker. Not a
   substitute for tiers 1–2 — and **remember the new bot is not in it until the G4 switch lands.**

**Test every variant independently — never extrapolate.** "It works in Hindi so Tamil is fine" is
a recipe for disaster: ASR, TTS and runtime adherence differ per language. Every language, every
direction, every bot is tested on its own. Also **snapshot before the first edit**
(`scripts/prompt-version.sh save <Bot> <label> "<why>"` — confirm at step 8f that the script
actually resolves the new bot first; see Guardrails) and **reconcile before every edit**
(`scripts/raya_deploy.py diff <target>`; `pull` if live is ahead).

Report a registration as **registered**, never as "done/working/confirmed" — the bot is not
confirmed working until it has been voice-tested. Where a variant cannot be harness-tested
(inbound bots — the tester can only receive, not dial in), do the best available verification and
mark the residual **VERIFY-PENDING** explicitly.

---

## Guardrails

- **Registering never deploys.** This skill makes no `PATCH`/`PUT` and calls no write path. Do
  not run `raya_deploy.py deploy` from here, not even `--dry-run`, and not even if the user says
  "and push it live" — that is a separate, gated, human-confirmed step after the prompt has been
  analysed and tested.
- **Never edit another bot's prompt files.** Registration touches only: the new bot's folder,
  the root `CLAUDE.md` path map (additively), `raya/agents.json` (appended entries), and
  `raya/regression/fleet.json`. Any diff line outside those is a mistake — revert it.
- **Additive-only in `CLAUDE.md`.** It is the operating manual every session reads first. Never
  reword, reflow, re-order or delete an existing row, heading or rule; insert new sections and
  new rows. If a change to an existing line seems necessary, ask first.
- **Do not edit `raya/regression/static_regression.py`.** Write the manifest; hand off the code
  change. Editing the live daily suite mid-registration risks breaking the standing check for
  every existing bot.
- **Never invent a uuid.** Blank is correct and safe; wrong is a prompt shipped onto someone
  else's live agent. Uuids come from `raya_deploy.py list`, by hand, matched by live agent name.
  Tighten `expected_name_contains` as soon as you see the real names.
- **No empty prompt files, no placeholder inventory.** A stub file satisfies `--check` while the
  bot does not exist, and `deploy` refuses any prompt carrying placeholder `job_id`s or a
  `[PLACEHOLDER SAMPLE DATA]` flag anyway. Register a language only when its file has real content.
- **Never localize** a `${variable}`, a tool name, or a fixed payload param — not in a filename,
  not in a manifest field, not in the memory-injection block. `contact_memory` is
  `contact_memory` in every language.
- **Instructions in English; only spoken lines in the target language.** When you paste a
  customer's prompt, if its rules are written in Hindi/Kannada/Telugu, that is a **bug** to flag
  for `/update-prompt` — not something to fix silently while registering.
- **Verify the snapshot tool resolves the new bot — it gates the first deploy.**
  `scripts/prompt-version.sh`'s `resolve_agent()` **dies loudly** on a bot it cannot resolve
  (`error: unknown agent '<x>' (known bots: …)`), and `raya_deploy.py deploy` step 5 calls
  `snapshot_local()` — which shells out to `prompt-version.sh save <agent> …` with the target's
  `agent` value — under a **no snapshot, no push** rule. So a bot the script can't resolve can be
  neither snapshotted nor deployed. `resolve_agent()` discovers bot folders (a top-level dir with a
  `CHANGELOG.md` **and** at least one other `*.md`), matching case-insensitively and treating `-`/`_`
  as spaces, so step 2 done properly is what makes the bot resolvable — a folder with only a
  CHANGELOG, or none, will not resolve. **Verify it at step 8f**; do not skip it because "it's just a
  snapshot". If the script is ever back to a hard-coded `case` list (`kkb|dkb|maya`), the fix is one
  line covering **both spellings the argument arrives as** — the lowercased folder name *with its
  space* and the slug — e.g. `"purple dots"|purple-dots|pd) echo "Purple Dots" ;;`, plus adding the
  bot to `cmd_list()`'s default agent list (`agents=(KKB DKB Maya)`) or a bare `list` silently skips
  it. Either way that is a **script change outside this skill's file set**: flag it to the user (or
  confirm it has landed) rather than editing the script here, and report it as a blocker if missing.
- **`id` is permanent.** Reports, `open-items.json`, deploy history and the fleet manifest all
  join on it. Choose it once; renaming orphans history.
- **Never `git commit` or `git push`** from this skill. Show the user the diff and let them commit.
- **The bot's shape belongs in the schema reference too.** If this is a brand-new agent, note
  that `/update-prompt` and `/port-feature` read
  `.claude/skills/port-feature/reference/agent-schemas.md` — a new bot needs an entry there
  before those skills can re-domain anything to it. Flag it; `/update-prompt` owns writing it.

### Not on Raya — say exactly what still works

If the bot does not (yet) run on Raya, register it anyway with empty uuids and `deploy: false`,
and tell the user plainly which half of the tuner they get:

**Works without Raya** — prompt iteration via `/update-prompt`; N-language expansion via
`/translate-prompt`; language parity via `/sync-check`; read-only gap audit via
`/prompt-analyser`; test-case, persona and checklist **design** via `/generate-test-cases`;
snapshot/rollback via `scripts/prompt-version.sh`; the CHANGELOG discipline; and the daily
**static** regression suite (it reads files, never places a call) once the G4 switch lands.

**Does not work without Raya** — one-click deploy (`scripts/raya_deploy.py deploy`, an API PATCH
against a Raya uuid); reconcile/pull against live (`diff` / `pull`); the agent-to-agent call
harness (`scripts/raya_testcall.py`, `scripts/raya_testrun.py` — they need a Raya tester agent
and an inbound DID); transcript grading and `/bug-fix`'s root-cause step
(`scripts/raya_call.py` reads Raya calls); and the weekly **live** voice regression. Without live
calls there is **no transcript**, and the house rule stands: **no fix without a transcript** — so
on another platform the customer must supply real call transcripts themselves, or bugs stay
unfixable by us.
