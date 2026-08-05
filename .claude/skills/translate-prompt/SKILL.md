---
name: translate-prompt
description: Take a bot's conversation prompt that exists in a master language and stand it up in ANOTHER Indic language — re-authoring the spoken content the way that language is actually spoken (not a literal translation), re-deriving the spoken-form/TTS machinery natively per language, keeping every language-agnostic line byte-identical, then registering, deploying and voice-testing the NEW agent in that language. Supports Hindi, Kannada, Telugu, Malayalam, Tamil, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese and Urdu. Use when the user says "take this bot into Telugu/Tamil/Marathi…", "translate the prompt", "add a new language", "make it multi-language", "localise this bot", "we need a Malayalam version", or a project (e.g. Purple Dots) is being expanded to more languages.
---

# Translate Prompt — take a bot into a new Indic language

Produce a **new language variant** of a bot's conversation prompt from an existing **master**
language file, then stand up and verify the **new agent** that runs it.

This is not a translation job. A translated prompt makes a bot that *sounds translated* — and a
bot that sounds translated on a phone call to a low-literacy or access-constrained caller loses
the caller in the first ten seconds. **The output must read the way the target language is
actually spoken by that audience.** A rendering that is semantically correct but idiomatically
dead is a **FAILURE** of this skill, not a partial success.

Assume **N projects, N bots, N languages** (Blue Dots: KKB / DKB / Maya; Purple Dots: the
disability rail; more to come). Nothing here is specific to KKB or to Hindi↔Kannada.

## The three rules that govern every decision here

1. **AGNOSTIC content is copied byte-identically.** Call flow, phase/step structure, conditions
   and routing, `${variable}` names, tool names, JSON payloads and field names, fixed params,
   prohibited-behavior rules, dignity/safety checks, the section skeleton. Classification is
   governed by `../update-prompt/reference/prompt-anatomy.md` (the AGNOSTIC / SPECIFIC / MIXED
   taxonomy) — cite it in your report.
2. **Instructions are ALWAYS in English.** Every rule, heading, condition and explanatory note in
   the new file is in **English**, exactly as in the master. The ONLY things in the target language
   are the words the bot literally **speaks**: quoted spoken lines, example dialogues, and
   number-to-word spellings. A section whose rules are written in Telugu/Tamil/Urdu is a bug.
3. **SPECIFIC content is RE-AUTHORED, never translated.** Read the master's spoken line, work out
   what a real speaker of the target language would say **in that situation on a phone call**, and
   write that. Same job, same meaning, same length budget — native words.

## Inputs

| Input | Example | Where it comes from |
|---|---|---|
| Bot + variant | `Purple Dots`, outbound, Signals backend | intake summary `raya/intake/<bot-id>.md`, or ask |
| **Master language file** | `Purple Dots/Purple Dots Hindi.md` | the path map in the root `CLAUDE.md` |
| **Target language** | Telugu (`te`) | the user |
| Region / audience of the target | rural Telangana job-seekers | the user — decides register + place names |
| Raya uuid of the NEW agent | from `raya_deploy.py list` | hand-copied, never inferred |

## Read before you start

- `../update-prompt/reference/prompt-anatomy.md` — the AGNOSTIC / SPECIFIC / MIXED taxonomy and the
  per-section tags. **This is the governing classification.**
- `reference/language-matrix.md` (this skill) — per-language script, register, numerals-as-words,
  code-mixing level, honorifics, greetings, real place names, TTS/ASR pitfalls.
- The **master file end to end**, plus one existing non-master variant of any bot (e.g.
  `KKB/KKB Placeholder Kannada Signals.md`) to see what "re-derived natively" looks like in
  practice — its `Language and Script Rules`, `TTS Normalization Rules`, `Canonical Location
  Spellings` and `Sample Conversational Patterns` sections are the model.
- `../prompt-analyser/reference/bug-patterns.md` — **D1** (hard/Sanskritised vocabulary), **D2**
  (numbers not spelled as words), **D3** (script separation: spoken vs payload), **D4** (voice-gender
  inconsistency), **D6** ("/" voiced literally), **D8** (internal term spoken aloud), **D26**
  (no canonical place spellings), **E1** (examples contradict the rules), **E3** (memory block
  missing). These are the failure classes a new language variant ships with by default.
- `../voice-test/reference/checklists/generic.md` §8 (language/script consistency) — the grading bar.

---

## Procedure

### 1. Fix the scope and the register decision

Confirm, and write down: bot • master language file • target language + ISO code • direction
(inbound/outbound — each is its own prompt and its own agent) • the **region and audience** of the
target-language callers.

The region decision is not cosmetic. It picks the variety (Telangana vs Coastal Andhra Telugu),
the greeting (`ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ` vs `ਨਮਸਤੇ`; `নমস্কার` vs `আসসালামু আলাইকুম`), the honorifics, and the
place names in examples. Ask for it; do not default it silently. Record the answer in the QA
record (step 11) so the next person knows why the file reads the way it does.

**Ask the native-reviewer question here too — it is a required input of this step, not a step-12
discovery:** *who will read this language back to us — a named speaker of the target language — and
if nobody, we ship it **VERIFY-PENDING**; confirm that is acceptable before we start.* For every
language the matrix marks `[needs native review]` (Telugu, Tamil, Marathi, …) there is no
call-verified precedent, so VERIFY-PENDING is the realistic outcome of every pass unless a reviewer
is lined up now. Write the answer — a name, or **NONE** plus who accepted VERIFY-PENDING — into the
QA record before you author a single line, so nobody learns it at step 12 of 17 with the file already
written and deployed.

If the bot has more than one prompt (inbound + outbound, or a backend variant), translate **one at
a time** and treat each as its own end-to-end pass through this procedure.

### 2. Reconcile against live, then snapshot

Mandatory, in this order, before you read the master for content:

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py diff <master-target-id>      # is the LIVE master ahead of the repo?
python3 scripts/raya_deploy.py pull <master-target-id>      # only if live is ahead: adopt live → repo
scripts/prompt-version.sh save <Agent> pre-<iso>-translation "translating <Bot> to <Language>"
```

You are about to clone the master's logic into a second file. **If the repo master is behind live,
you clone stale logic into a brand-new language and it stays wrong for as long as that language
lives.** If `diff` shows Raya ahead, `pull` first and review `git diff` before going on. If GET is
flaky or returns empty, use `/raya-reconcile` (browser sha-boolean) instead of trusting a GET. See
`raya/README.md` → *Reconcile-before-fix*.

> `scripts/prompt-version.sh` resolves `<agent>` from a hard-coded list (`KKB | DKB | Maya`). For a
> new bot, add its case to `resolve_agent()` first, or `prompt-version.sh save` exits 1 with
> `error: unknown agent '<x>' (expected KKB | DKB | Maya)` — a loud failure, not a silent one — and
> `raya_deploy.py deploy` then refuses to push (`pre-deploy snapshot failed (no snapshot, no push)`).
> Never proceed without a snapshot.

### 3. Build the classification ledger — every section, before you write anything

Extract the master's heading list and classify **every** section against
`prompt-anatomy.md`. Do not translate a single line before this table exists.

```bash
grep -n '^#\{1,4\} ' "<Bot>/<Bot> <Master Language>.md"
```

| # | Section (master heading) | Tag | Action for the new file |
|---|---|---|---|
| 1 | Introduction | MIXED | copy the rules verbatim; re-author the persona name + spoken intro |
| … | … | AGNOSTIC | copy byte-identical |
| … | … | SPECIFIC | re-author natively from scratch |

The classification test (from the anatomy): *"if this exact text appeared in the other language's
file unchanged, would it be correct?"* Yes → AGNOSTIC. No, it must be in the other script/idiom →
SPECIFIC. Partly → MIXED (copy the rule, re-author the quoted speech).

Sections that are **always** SPECIFIC and must be rebuilt, not translated: `Language and Script
Rules`, `TTS Normalization Rules`, `Sample Conversational Patterns`, the loanword list, the tone
markers, the prohibited-phrase list, `Canonical Location Spellings`.

Sections that are **always** AGNOSTIC and must survive byte-identical: `Input Variables`,
`Hallucination Guard`, `Conversation State Model`, `Tool Call Rules` + every payload,
`Action and Consent Rule`, `Dignity Safety Check`, `What You Must Always Preserve`.

### 4. Create the file and copy the AGNOSTIC spine byte-identically

File name follows the path-map convention: `<Bot>/<Bot> <Language>.md` (plus the variant tokens the
master carries — `Inbound`, `Signals`, …), e.g. `Purple Dots/Purple Dots Telugu.md`,
`KKB/KKB Placeholder Tamil Signals.md`.

Copy the master, then work section by section down the ledger. For AGNOSTIC sections **change
nothing** — not the wording, not the ordering, not the whitespace. Verify mechanically afterwards:

```bash
M="<Bot>/<Bot> <Master>.md"; T="<Bot>/<Bot> <Target>.md"

# Tool-call sections. Loop over the headings the master ACTUALLY has — they are per-tool
# (`# get_profile Tool Call Rules`, `# create_profile Tool Call Rules`,
# `# apply_job Tool Call Rules`, `# update_profile Tool Call Rules`) plus
# `# Tool Call General Instructions`. There is NO `# Tool Call Rules` heading in any prompt:
# hard-coding one makes BOTH sides of the diff empty and the check "passes" without comparing
# a single line — a false pass on the most safety-critical section. An empty extract is a FAIL.
grep -E '^#{1,4} .*Tool Call' "$M" > /tmp/toolheads
[ -s /tmp/toolheads ] || echo "FAIL: no tool-call heading matched in master — fix the pattern"
while IFS= read -r h; do
  esc=$(printf '%s' "$h" | sed 's/[].[^$*\/]/\\&/g')
  sed -n "/^$esc\$/,/^#\{1,4\} /p" "$M" > /tmp/m.sec
  sed -n "/^$esc\$/,/^#\{1,4\} /p" "$T" > /tmp/t.sec
  if [ ! -s /tmp/m.sec ] || [ ! -s /tmp/t.sec ]; then
    echo "FAIL (empty extract — NOT a pass): $h"
  else
    diff /tmp/m.sec /tmp/t.sec > /dev/null && echo "OK identical: $h" || echo "DRIFT: $h"
  fi
done < /tmp/toolheads

# input variables — the broad form from ../sync-check/reference/n-language-parity.md Pass 3.
# The narrow '\${[a-z_]*}' silently misses camelCase names such as ${phoneNumber} (live in 5
# DKB files), so a dropped or localized one would diff empty and read as "parity proved".
diff <(grep -ohE '\$\{[A-Za-z0-9_]+\}' "$M" | sort -u) \
     <(grep -ohE '\$\{[A-Za-z0-9_]+\}' "$T" | sort -u)   # must be empty
```

**Never localize** a `${variable}` name, a tool name, a JSON field, or a fixed param (e.g.
`sourceService: "ONESTAGENT"`, `app_instance`). Payload *values* stay Latin/English; only spoken
output is in the target script — crossing those is bug **D3**.

### 5. Re-author the spoken content (this is the actual work)

For every SPECIFIC item and every quoted line inside a MIXED section:

1. Read the master line and state, in English, **what it has to accomplish** in that turn (greet;
   disclose AI + recording; ask one field; confirm a misheard number; bridge to a silent tool call;
   deliver a refusal without shaming; close).
2. Write what a real speaker of the target language, on a phone call, in that region, **would
   actually say** to accomplish that. Write it fresh. Do not look at the master's word order while
   you write the line — look at it again only to check the meaning afterwards (step 10).
3. Keep the **length budget**: a spoken line that doubles in syllables changes the pacing of the
   call and blows the turn-taking. Trim to the master's spoken duration, not its word count.
4. Match the **register** from `reference/language-matrix.md`: the polite pronoun and verb ending,
   the politeness particle (Telugu `అండి`, Punjabi `ਜੀ`, Tamil `-ங்க`, Urdu `جی`), the address
   forms, the natural code-mixing level.
5. Prefer the **everyday** word over the correct-but-bookish one. This is bug **D1** and it is the
   most common literal-translation tell: `దరఖాస్తు` where a real speaker says `అప్లై`,
   `விண்ணப்பம்` where they say `அப்ளை`, `नियोजन` where they say `जॉब`. The matrix gives the natural
   loanword level per language; when the loanword is what people say, **use the loanword**, written
   in the target script.
6. Watch **diglossia**. Tamil, Malayalam, Bengali and Telugu each have a literary register that a
   machine translation will reach for and that no one speaks: Tamil literary `கூறுங்கள்` vs spoken
   `சொல்லுங்க`; Bengali *sadhu-bhasha* vs *cholit-bhasha*; Telugu *granthika* vs spoken. Literary
   register on a phone call reads as a news bulletin. Always the spoken form.
7. Preserve **voice gender** agreement throughout if the bot has one (bug **D4**) — in gendered
   languages every verb, participle and adjective must agree, in every single spoken line. Check
   the whole file, not the lines you happened to touch.

### 6. Re-derive the spoken-form / pronunciation machinery natively — never copy it

The master carries machinery whose only purpose is making speech come out right. **All of it is
per-language and none of it transfers.** Rebuild each row for the target language using
`reference/language-matrix.md`, and keep the section's English scaffolding identical to the master's:

| Machinery | What to re-derive | Guards |
|---|---|---|
| Script output rule | the exact script permitted; Roman/Latin and mixed-script forbidden | D3, generic §8 |
| Loanword list | which English words are natural in that language's **speech**, spelled in its script | D1 |
| Numbers | every digit written as words in that language's counting idiom | D2 |
| Money + ranges | the language's own money phrasing (worked examples in the matrix) | D2 |
| Per-unit rates | "per day/month" phrasing — never the "/" symbol | D6 |
| Dates | long spoken form; no `DD/MM/YYYY` | D2 |
| Times | day-part words (morning/afternoon/evening/night) — never AM/PM | D2 |
| Phone numbers | digit-by-digit words, **including which zero-word people actually say** | D2 |
| Email | speakable spelling of `@` and `.` in that language | D2 |
| Abbreviations | expanded as that language's spoken letter names | D2 |
| "/" symbol | the language's word for "or"; never voice the symbol | D6 |
| Honorifics / address | the polite pronoun, verb ending, particle, name suffix | matrix |
| Greeting + farewell | the natural phone greeting and close for that region/audience | matrix |
| AI + recording disclosure | re-authored natively, still before the pitch | generic §1 |
| Hold / wait filler | a neutral "one moment" — must NOT narrate the step | B2, D34 |
| Read-back confirmation | how you naturally ask "you said X, correct?" | generic §6 |
| ASR confusion pairs | the homophone/consonant pairs that language's ASR actually collapses | matrix |
| Prohibited phrases | culturally adapted — the master's banned phrases may not exist here, and this language will have its own shaming/pressure phrasings to ban | matrix |
| Canonical place spellings | one pinned spelling per place, overriding all dynamic transliteration | **D26** |
| Tone markers | the language's own softeners ("now", "about", "usually") | anatomy |

Two rules that catch most of the damage here:

- **Never emit native-script digits** (`౧౨౩`, `১২৩`, `૧૨૩`, `۱۲۳`). Numbers appear as **words**;
  where the master's English scaffolding shows a numeral for illustration, keep the scaffolding
  identical and change only the spelled-out target-language form.
- **Pin place names** (D26). Any place the flow, the inventory, or the examples can mention gets one
  exact spelling in a `Canonical Location Spellings` section that explicitly overrides the general
  transliteration and phonetic-matching rules. Same section, same English wording as the master,
  target-script values.

### 7. Localise the examples — including the people and the places

`Sample Conversational Patterns` and every few-shot example are fully SPECIFIC. Rebuild them as
conversations that could have happened in the target language's own region:

- **Person names** native to that language (`ರಮೇಶ್` in Kannada, `செல்வி` in Tamil, `আরিফ` in Bengali),
  written in the target script.
- **Place names** from that language's real region — see the matrix. A Telugu example set in
  Ghaziabad is a tell that the file was translated, not written.
- **Job / service / benefit examples** that are plausible where those callers live.
- Examples must **agree with the rules** in the same file (bug **E1**): if the file bans a phrase,
  no example may use it; if the file mandates a read-back, an example that skips it is a bug.
- Same **number of examples**, same slots, same English framing labels as the master. Different
  words, identical scaffolding.

### 8. Structural parity + the memory-injection block

- If the bot has memory enabled, the new file must contain this block **exactly**, verbatim, in
  English, unaltered (repo `CLAUDE.md`; bug **E3**):

  ```
  ### Contact context
  Here is the caller context:
  {${contact_memory}}
  ```

  Same placement as the master (inside the intro rules, or at the end of Input Variables).

- Heading skeletons must match one-for-one:

  ```bash
  diff <(grep '^#\{1,4\} ' "<Bot>/<Bot> <Master>.md") \
       <(grep '^#\{1,4\} ' "<Bot>/<Bot> <Target>.md")   # expect empty
  ```

  Any difference is either a missed section or a section you invented — resolve it, don't explain it.

- Then run **`/sync-check`** for the bot. It now audits one master against **N** mirrors and knows
  `raya/divergences.json` for owner-approved deliberate divergences. A new language must come out
  of `/sync-check` clean before it is deployed. Any divergence you introduced on purpose (e.g. a
  region-specific greeting the owner approved) belongs in `raya/divergences.json`, not in an
  unexplained diff.

### 9. QA Gate 1 — the monolingual read gate (blocks literal-translation slop)

**Read ONLY the new file. Do not look at the master during this gate** — close it. Read every
spoken line aloud as if you were the bot on a real call, and ask one question per line:

> **Would a real speaker of this language actually say this, out loud, on a phone call, to this
> caller?**

Flag and rewrite anything that is:

- **bookish / literary** — a written register no one speaks;
- **machine-translated-sounding** — source word order, calques, an English idiom rendered literally,
  a pronoun or copula that a real speaker would simply drop;
- **over-formal or over-familiar** for this audience — wrong pronoun, missing politeness particle,
  or a familiarity a stranger on the phone hasn't earned;
- **unpronounceable or ambiguous for TTS** — long compounds, script forms the matrix flags as weak,
  digits, symbols, Latin script inside a spoken line;
- **too long for its turn** — a line the caller will interrupt;
- **purist coinage where the loanword is what people say** (D1).

Record every flag and its rewrite in the QA record. **A file that produced zero flags on its first
monolingual read has almost certainly not been read properly — say so and read it again.**

### 10. QA Gate 2 — the round-trip meaning gate

Now open the master. For every spoken line, pair-wise:

1. Back-translate the new line to **English** from the target language alone.
2. Diff that English against the **English meaning** of the master's spoken line.

Judge **meaning**, not wording. Different wording is expected and desired — that was the whole
point of step 5. What this gate catches is **drift**:

- a lost obligation (the disclosure, the consent ask, the read-back, the "say this once");
- a changed condition ("if the profile is empty" → "if the profile is wrong");
- a promise the master never made, or a fact the master never asserted (fabrication);
- a softened refusal that now reads as a commitment;
- a dropped constraint (a cap, a limit, a "never");
- a number, name or ID that changed value.

Any meaning drift is a **fix**, not a note. Fix it and re-run Gate 1 on the rewritten line — the two
gates pull in opposite directions and both must pass on the final text.

### 11. Write the per-language QA record

Save to **`raya/translations/<bot-id>-<iso>.md`** (create `raya/translations/` if absent) so a
reviewer can see what was actually checked, and so the next language pass can reuse the decisions:

```markdown
# <Bot> — <Language> (<iso>) translation QA record
- Date / author:
- Master file + the commit/snapshot it was cloned from:
- New file:
- Region + audience assumed:                     # why the register/greeting/places are what they are
- Native-reviewer answer (asked at step 1, BEFORE writing): <name> / **NONE — ships
  VERIFY-PENDING, accepted by <who>**
- Variety / register chosen (and what was rejected):
- Classification ledger: N sections — A agnostic (byte-identical, verified by diff), S specific
  (re-authored), M mixed
- Spoken-form machinery re-derived: numbers / money / rates / dates / times / phone / email /
  abbreviations / "/" / honorifics / greeting / farewell / disclosure / hold / read-back /
  prohibited list / canonical places / tone markers / loanword list      # tick or note "n/a — why"
- Structural parity: heading diff empty? memory block verbatim? variable set identical?
- /sync-check result (+ any entry added to raya/divergences.json, with the owner's approval):
- **Gate 1 — monolingual read:** flags raised → rewrites made (list them)
- **Gate 2 — round-trip:** meaning drifts found → fixes made (list them)
- Native reviewer: <name> / **NONE — VERIFY-PENDING**
- External ear on the first live call (step 15, required): <name> + verdict on the Gate-1 question /
  **no speaker reachable — stays VERIFY-PENDING**
- Platform: Raya uuid • agent name • language_id • voice_id • DID • verified by `whoami`
  (`whoami` is the only source of language_id/voice_id; `list` gives id + name only)
- Live tests: call uuids, personas used, checklist results, what is still open
```

### 12. Native review — or an honest VERIFY-PENDING

Gates 1 and 2 are done by the author. They are necessary and **not sufficient**: neither one is a
native speaker. You asked who the reviewer would be back at step 1 — this is where you act on that
answer, not where you discover it.

- **Native reviewer available** → give them the new file plus the QA record and ask specifically:
  does this sound like a real person on a phone call, and is any line bookish, rude, over-familiar,
  or unclear? Record their name and their verdict.
- **No native reviewer** → do the best available verification (Gates 1 + 2, plus a live call whose
  audio/transcript you review, plus the analyser pass) and mark the language
  **VERIFY-PENDING** in the QA record, the changelog entry, and your report. Never write "done",
  "confirmed" or "native-verified" without a named human. Repo `CLAUDE.md` → *Testing is mandatory*.

### 13. Stand up the NEW agent on Raya

A new language means a **new agent**. Registration is mechanical bookkeeping — route it through
**`/register-bot`** (its *variant addition* path: new language of an existing bot). It creates
nothing you have to re-do and it also adds the variant to the standing-regression fleet manifest.
What must be true when it finishes:

- **The agent exists on Raya.** Created by whoever owns the console (usually cloned from the master
  agent so the tool config comes along). This skill does not create agents.
- **`raya/agents.json` has a target row** with: `id` (`<bot>-<iso>-<dir>[-<backend>]`, e.g.
  `pd-te-out`), `file` (the new prompt path), `agent`, `language` (the **ISO code**: `te`, `ta`,
  `ml`, `mr`, `bn`, `gu`, `pa`, `or`, `as`, `ur`), `direction`, `kind: "conversation"`,
  `profile: "conversation"`, `raya_name`, `raya_agent_id: { prod, staging }`, `deploy`.
- **The uuid is hand-copied from `python3 scripts/raya_deploy.py list`** and pasted into the row.
  **Never infer a uuid from a filename** — `agents.json`'s own `_note` says so, and the live trap is
  real: `KKB Placeholder Inbound.md` is the **Hindi** agent, which no filename tells you. Read the
  name from `list`, then copy the id sitting next to it.
- **`expected_name_contains` is a real wrong-target guard** — include the bot token **and** the
  language/variant token, e.g. `["Purple Dots", "Telugu"]`, `["KKB", "Tamil", "Signals"]`. Deploy
  aborts if the live agent's name lacks all of them. A guard of just `["KKB"]` will happily let you
  PATCH a Telugu prompt onto the Hindi agent.

Then the part registration does **not** cover — **the agent's language and voice**:

```bash
python3 scripts/raya_testcall.py whoami <new_agent_uuid>   # prints name / language_id / voice_id / DIDs
```

If the cloned agent still carries the **master's** `language_id` / `voice_id`, the bot will read
your new script with the wrong language's TTS voice. This is the single most common
"the file looks perfect, the call sounds broken" failure, and the matrix names the audible cases
(a Hindi voice reading Marathi; a Bengali voice reading Assamese).

Harvest the pair with `python3 scripts/raya_testcall.py whoami <uuid>` run against an agent that
**already runs that language** — `whoami` is the only command that prints `language_id`/`voice_id`.
Use `raya_deploy.py list` only to find that agent's uuid by name: `list` prints **id and name and
nothing else**, so it can never give you the ids. If **no agent runs the language yet** (the normal
case for the first Telugu/Tamil bot), request the `language_id` + `voice_id` from **LitWiz Labs**;
until you have them, live testing in this language is **BLOCKED** — say so and mark the variant
VERIFY-PENDING rather than testing on another language's voice. The agent's own language/voice is
set on the Raya console by whoever owns the agent config — `raya_deploy.py deploy` PATCHes
**`instructions` only**. Re-run `whoami` and confirm before you test.

Then add that same pair to the `LANG` dict in `scripts/raya_testcall.py` (near the top, ~line 32; it
holds `hi` and `kn` only). **This is the real blocker for testing any new language:**
`raya_testcall.py lang` validates the ISO code against `LANG` and hard-exits with
`unknown lang '<iso>'; known: ['hi', 'kn']`, so until the pair is in the dict the **tester** agent
cannot be switched into the new language at all (step 15). If Raya has **no voice for the
language**, live testing is blocked — say so plainly and mark VERIFY-PENDING; do not quietly test in
a different language.

### 14. Deploy by PATCH, with read-back verification

```bash
python3 scripts/raya_deploy.py verify <new-target-id>   # right URL + name guard, read-only
python3 scripts/raya_deploy.py diff   <new-target-id>   # what will change
python3 scripts/raya_deploy.py deploy <new-target-id>   # snapshot → GET backup → guard → diff → confirm → PATCH → read-back
```

`deploy` is the only write path: it snapshots, backs up the current remote, runs the name guard,
shows the diff, requires the confirmation, PATCHes, and **verifies the read-back byte-equals the
local file**. Never trust a bare GET for live content. `deploy` also refuses any prompt still
carrying placeholder `job_id`s or a `[PLACEHOLDER SAMPLE DATA]` flag — if you cloned a placeholder
inventory into the new language, fix that before deploying, never after. Append the deploy to
`raya/deploy-history.md`.

### 15. `/voice-test` the new language — with a native-language persona

The new variant is tested **on its own**. It inherits nothing from the master's test results
(repo `CLAUDE.md` → *Test EVERY variant — never extrapolate*).

1. **Write a persona in the target language.** `raya/personas/<iso>-<behaviour>.md`, following the
   existing convention: an **English** instruction header (who they are, how they behave, never
   break character) with the **spoken lines in the target language and script**, using native
   person and place names — e.g. `te-seeker-cooperative.md`, `ta-service-navigator-silent.md`. A
   persona whose spoken lines are translated Hindi is not a test of the new language.
2. **Switch the tester into the language and fire the call:**

   ```bash
   python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<iso>-<behaviour>.md
   python3 scripts/raya_testcall.py lang    <tester_uuid> <iso>
   python3 scripts/raya_testrun.py <new_agent_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "<label>"
   ```

   Respect the platform reality in `../voice-test/SKILL.md`: omit `out_did`, space calls ≥ ~15 s,
   retry flaky bridges, keep polling while `GET /api/call/{uuid}` lags.
3. **Grade** against `../voice-test/reference/checklists/generic.md` (all of it, §8 especially) plus
   the bot's own checklist — and these **translation-specific** items, which only a live call in the
   new language can settle:

   - [ ] Every spoken turn is in the target language and **script** — no Latin, no master-language
         residue, no English rule-text leaking to the caller (§8, D3).
   - [ ] Numbers, money, dates, times and phone digits came out as **words**, and TTS pronounced
         them correctly (D2). Listen to money and to a phone number specifically.
   - [ ] Place and person names came out in the **pinned canonical** form, identically on every
         mention (D26).
   - [ ] The voice is the **target language's** voice, at a natural pace, with no obvious
         mispronunciation of the script's hard cases (see the matrix's pitfalls row).
   - [ ] Nothing sounded bookish or translated — the Gate-1 question, now answered from real audio.
   - [ ] Voice gender agreement held across every spoken line (D4).
   - [ ] Tool calls fired with **unchanged** names and payloads, and payload values are Latin
         (D3) — the translation must not have moved a single tool arg.
   - [ ] **Cheap external ear (required — no language ships purely self-graded).** Gates 1 and 2 were
         both performed by the author of the lines; this is the one check that isn't. Have **any**
         speaker of the target language — not necessarily the reviewer of record — listen to this
         first live call's audio and answer the Gate-1 question: *would a real speaker say this, out
         loud, on a phone call, to this caller?* Record their **name and verdict** in the QA record.
         If no speaker at all is reachable, write that down as the reason the language stays
         **VERIFY-PENDING**.

4. Run the **three tiers** below on this variant. Route any confirmed prompt gap to
   **`/update-prompt`** (never hand-edit); if the gap also exists in the master, fix it there and
   let `/sync-check` carry it to every mirror.

### 16. Wire the new variant into the standing nets

Not done until the language is *covered going forward*:

- **Fleet manifest / standing regression** — `/register-bot` step 6 adds the variant; confirm it
  landed, or the daily Tier-3 suite (`raya/regression/`) never checks this language. Note that
  `static_regression.py`'s `sync_parity()` historically special-cased `hi`/`kn` — verify the new
  ISO code is actually picked up rather than assuming it is.
- **Personas** — at least the happy path plus one hard case exist under the new `<iso>-` prefix
  (gap G5); `/generate-test-cases` can generate the full set.
- **Path map** — the root `CLAUDE.md` path map lists the new file (done by `/register-bot`).
- **CHANGELOG** — append to `<Bot>/CHANGELOG.md`:

  ```
  ## YYYY-MM-DD — <Language> variant created (<iso>)
  - **Feedback/bug:** <why this language, who asked>
  - **Change:** new <Language> conversation prompt re-authored from <master file>; AGNOSTIC spine
    byte-identical; spoken content + spoken-form machinery re-derived natively; new Raya agent
    <uuid> registered and deployed
  - **Files:** <Bot>/<Bot> <Language>.md, raya/agents.json, raya/translations/<bot-id>-<iso>.md,
    raya/personas/<iso>-*.md, raya/deploy-history.md, CLAUDE.md
  - **Verification:** Gate 1 / Gate 2 / native reviewer <name or VERIFY-PENDING> / live call <uuids>
  ```

- **Analyser** — a **new language variant is a feature addition, not a bug fix**, so it does not by
  itself owe `/prompt-analyser` an entry. But if this pass **uncovered a bug** (a missing section, a
  spoken-form class the master never handled, a variable that garbled), that *is* a bug fix: add or
  sharpen the pattern in `../prompt-analyser/reference/bug-patterns.md` (symptom → root cause →
  detection heuristic → fix direction → source + date) and update
  `../prompt-analyser/reference/section-checklists.md` if it implies a section that must always
  exist. Repo `CLAUDE.md` → *Bug-fix feedback loop*.

### 17. Report

Report: the new file path • the classification ledger totals (agnostic byte-identical / specific
re-authored / mixed) with the verification commands that proved parity • the spoken-form machinery
re-derived, row by row • Gate 1 flags and Gate 2 drifts, with the rewrites • the native-review
status (named reviewer, or **VERIFY-PENDING**) • the agent uuid / name / language / voice actually
confirmed by `whoami` • the deploy read-back result • the live-call uuids and checklist outcomes •
and anything still open. For a handful of representative lines, show the master line, the
re-authored line, and its back-translation side by side — that is what lets a reviewer see this was
re-authored and not translated.

---

## Test before done (MANDATORY — a translation is not DONE until tested)

A new language variant is **not** done when the file is written, and not when it is deployed — only
when it has been TESTED in that language and confirmed working, with overall sanity intact. Never
report a translation as "done", "fixed" or "confirmed" until you have actually tested it. Where a
variant cannot be harness-tested (inbound bots — the tester can only receive, not dial in; no Raya
voice for the language; telephony down), do the best available verification (post-deploy transcript
review + static sanity + Gates 1/2) and explicitly mark the residual **VERIFY-PENDING**. Revert on
any regression (`/prompt-version`).

Run the **three testing tiers** from the repo `CLAUDE.md`, **on this language variant
independently — never extrapolate** ("Hindi passed, so Tamil is fine" is a recipe for disaster;
runtime adherence, ASR and TTS all differ per language, and a byte-identical agnostic spine can
still land differently):

1. **Tier 1 — Fix/feature verification:** `/voice-test` the new variant on its core happy path and
   on the scenarios the bot exists for, and confirm the new-language behavior in a real transcript.
2. **Tier 2 — Blast-radius regression:** confirm nothing adjacent broke — the whole flow
   (greet → disclose → fetch → present → act → close) still works in the new language; the tool
   payloads are byte-identical to the master's and still valid; the master and every other mirror
   still pass `/sync-check`; adding the variant did not perturb the shared master file.
3. **Tier 3 — Daily standing regression:** the scheduled 100+‑case suite (`raya/regression/`) must
   actually include the new variant (step 16) — it catches longer-tail drift and does not replace
   tiers 1–2.

Only after tiers 1–2 pass **on this variant** is it DONE.

---

## Guardrails

- **A literal translation is a failure.** Semantically correct but idiomatically dead does not pass.
  If you cannot write a line the way a real speaker would say it, say so and ask — do not ship the
  dictionary rendering.
- **Surgical edits only.** The new file's smallest possible difference from the master is: the
  target-language spoken lines, the re-derived spoken-form sections, and the localised examples.
  Nothing else moves. Do not reformat, re-wrap, re-order, "improve" or clean up the master's
  structure while you are in there, and **never edit the master** during a translation pass —
  a master fix is a separate `/update-prompt` change.
- **Instructions in English, always.** A rule, heading, condition or note written in the target
  language is a bug — rewrite the prose to English and keep only the spoken lines localised.
- **Never localize** a `${variable}` name, a tool name, a JSON field, or a fixed param; never let
  target-script text into a tool argument, and never let Latin script into a spoken line (D3).
- **Never copy spoken-form machinery across languages.** Numbers, money, dates, phone digits,
  loanwords, honorifics, greetings and place spellings are re-derived per language, from the matrix,
  every time. Copying Kannada's number-words into Telugu is exactly the failure this skill exists
  to prevent.
- **Reconcile before edit; snapshot before deploy.** The live master can be ahead. Clone reconciled
  logic, never stale logic.
- **Both gates, in order, every time.** Gate 1 without Gate 2 ships meaning drift. Gate 2 without
  Gate 1 ships fluent-sounding literalism. Neither substitutes for a native speaker.
- **Honesty over confidence.** Where the matrix says *needs native review*, treat it as unknown:
  make the best call, flag it in the QA record, and mark the language VERIFY-PENDING. A flagged
  uncertainty is useful; a confident guess about someone's language is a liability.
- **Push back before "fixing".** If a reported problem with a translated bot turns out to be wrong
  input args, a backend fault, or a Raya voice/ASR limitation, say "the prompt is fine" and escalate
  — do not pile prose onto a prompt to fix a platform problem (D25).
- **All prompt edits go through `/update-prompt`;** all cross-agent reuse through `/port-feature`;
  all registration through `/register-bot`. This skill authors a new language variant and stands up
  its agent — it does not become a second editing path.
