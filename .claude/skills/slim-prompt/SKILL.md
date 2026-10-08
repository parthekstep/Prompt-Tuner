---
name: slim-prompt
description: Rewrite a long voice-agent conversation prompt into a much shorter "slim" version WITHOUT losing behaviour, stood up as a NEW variant on its own A/B agent (never an overwrite of production), proven equivalent by a contract coverage table, a static audit and N>=3 live calls per branch, and compared head-to-head against the original on latency per turn and checklist pass rate before any traffic moves. Use when the user says "slim this prompt", "compress the prompt", "make the prompt shorter", "cut the prompt down", "the prompt is too long", "reduce prompt size", "reduce latency by shrinking the prompt", "get the prompt under 50k", or "do for <bot> what we did for KKB Slim".
---

# Slim Prompt: a shorter prompt that still does everything the long one did

Turn a long, accreted conversation prompt into a short one that a reviewer can read end to end, as
a **separate A/B variant**, and prove it is no worse before anyone points a caller at it.

This skill codifies the September 2026 KKB Hindi Signals rewrite (`9afc12a`: 219,519 -> 68,744
chars, bot `140d13ca`) and everything that went wrong after it (`KKB-Slim/CHANGELOG.md`,
`raya/slim/README.md`). Read the "Lessons" section at the end before you start; every rule in the
procedure exists because one of those lessons cost real calls.

Read `<bot>` as the source bot, `<Bot>-Slim` as the new variant, and `<lang>` as any language the
bot speaks. Resolve every file through the root `CLAUDE.md` path map and `raya/agents.json`; never
hard-code a bot list or a language pair.

---

## 1. Is slimming worth it? Decide BEFORE writing a line

**Be honest about the payoff. The only measured result we have is small.**

| | chars | median s per agent turn | invariant failures (5 calls) |
|---|---|---|---|
| fat `kkb-hi-signals` | 219,518 | 16.00 | 7 |
| slim `kkb-hi-signals-slim` | 68,744 | 14.75 | 5 |

A 69% cut bought about **7% per turn** (`7d164b9`), and both prompts failed on the **same classes**
at similar rates (Latin company names, ordinal restarts, location substitution). The extra prose was
not buying adherence, and removing it did not fix anything either. The dominant latency cause at
the time had nothing to do with size: `hold_message` was never played, so 348/348 tool calls sat in
silence for the whole round-trip.

So, before starting, check and write down:

- [ ] **What is the goal?** Latency, cost, reviewability, or "the team set a char target". If it is
      latency, first look for a non-prompt cause (tool round-trips in silence, platform settings,
      ASR timeouts). Expect single-digit percent from size alone.
- [ ] **Is it a behaviour bug in disguise?** Slimming does not fix a mechanism bug (a competing
      instruction, a rule far from the line that consumes it). Route those to `/update-prompt`.
- [ ] **Measure the composition** (step 3 below) and state the realistic floor. The KKB floor with
      behaviour intact was ~68k; the team's 50k target was reachable only by deleting the worked
      calls, the ASR section, the Situations and the canonical spellings together (still 56,657).
      **Below the floor you are cutting behaviour, and that is an owner decision with a menu**, not
      something this skill does silently.
- [ ] **Owner sign-off** on: the target size, that a new A/B agent will be created, and the A/B
      decision gate in step 11.

Where slimming genuinely helped on KKB: the call became **14 numbered steps in call order** instead
of 148 sections in no order, a duplicated 23,723-char `# No-Match Fallback` became one section, and
the slim bot became the safe place to run behaviour experiments (the ordinal-counter fix was proven
there first: `0ab57b0`, `eadf269`). Reviewability and an experiment bed are real benefits; claim
those, not a quality gain.

---

## 2. Never-drop list (a slim prompt that loses one of these is a regression, whatever its size)

- [ ] **Every tool contract**: tool name, when it fires, every payload field, fixed params
      (`sourceService`, `app_instance`, `languageSpoken`), enum values, how its result is read
      (which item, which field, live vs draft), and every failure-row line.
- [ ] **Every consent, disclosure and safety rule**: data-sharing line before apply, consent gates
      (step 3.5 style), AI/recording disclosures and every early exit that must still carry them
      (D103), dignity checks, do-not-call, proxy caller, distress handling.
- [ ] **Every mandated spoken line**, verbatim, and every **named ban** whose exact wording is the
      failure (KKB kept "पक्का call आएगा" and "selection हो जाएगा" quoted, because a paraphrased ban
      does not stick).
- [ ] **Every input variable** (`${...}`), unrenamed, and the memory injection block, byte for byte:
      ```
      ### Contact context
      Here is the caller context:
      {${contact_memory}}
      ```
- [ ] **TTS / script machinery**: number-to-word rules, canonical place spellings, slash handling,
      abbreviation handling, the `[slot]` marker rule (D77), the `*( )*` note rule.
- [ ] **Every branch of every multi-branch step**, including the rare ones (ask-the-pin when none is
      held, empty fetch, no-match, second consecutive failure).
- [ ] **Every pre-close owed item** (services offer, Need Capture, read-back), each named in the exit
      checklist (D96).

What you MAY drop: provenance prose (call ids, "this used to say", anecdotes, dates), exact duplicate
paragraphs, a second copy of a section, multiple wordings of one rule, sample dialogues beyond the
few that demonstrate each branch, quotes of past bugs (they live in `CHANGELOG.md` and
`bug-patterns.md`), and caller utterances that only pad a sample.

---

## 3. Procedure

### Step 0. Reconcile and snapshot

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py diff <source-target>     # is live ahead of the repo? (or /raya-reconcile)
python3 scripts/raya_deploy.py pull <source-target>     # only if live is ahead; commit before going on
scripts/prompt-version.sh save <Agent> pre-slim "baseline before slim rewrite"
```

Never slim a file that is behind live: you would bake a stale inventory or a stale rule into the new
variant. The source prompt itself is **not edited** by this skill at any point.

### Step 1. Real-traffic latency baseline

Score the source bot's recent real calls with the same scorer you will use for the A/B, so the
number the slim bot must beat is known before it exists (KKB: median 13.4 s per agent turn over the 7
most recent measurable calls).

```bash
python3 raya/slim/ab_compare.py --score-only
```

### Step 2. Measure the composition

Count, do not guess. Report each as chars and percent of the file:

- [ ] provenance prose (call ids, "used to", "was changed because", dates inside rules)
- [ ] exact duplicate paragraphs
- [ ] duplicated sections (grep every `^# ` heading for repeats; KKB had `# No-Match Fallback` twice)
- [ ] paragraphs over 400 chars (KKB: 37% of the file in 128 such paragraphs)
- [ ] sample conversations (count them and their chars)

```bash
grep -n '^#' "<source prompt>" | sort -k2 | uniq -f1 -d      # repeated headings
python3 -c "import sys,collections;p=[x.strip() for x in open(sys.argv[1],encoding='utf-8').read().split('\n\n') if x.strip()];c=collections.Counter(p);d=sum(len(k)*(v-1) for k,v in c.items() if v>1);t=sum(map(len,p));print('dup chars',d,'of',t,round(100*d/t,1),'%');print('long paras',sum(1 for x in p if len(x)>400))" "<source prompt>"
```

From this, state the expected size and the floor in the plan you show the owner.

### Step 3. Extract the contract mechanically

```bash
python3 raya/slim/extract_spec.py "<source prompt>" -o raya/slim/<target>/spec-source.json
```

`extract_spec.py` matches tools against a **hard-coded regex**; it does not know newer tools
(`record_consent`, `get_services`, `get_recommended_jobs` were added after it was written). List the
agent's real tools from its toolspecs / the live agent and add any the extractor missed to the
coverage table by hand. Do not trust an empty tool diff until you have checked the tool list.

### Step 4. Build the coverage table (the inventory). Nothing is written until this exists

One row per contractual item in the source. Save it as `raya/slim/<target>/coverage.md`.

| id | item | kind | source location(s) | times stated | points of use | decision | slim location | why |
|---|---|---|---|---|---|---|---|---|
| R-012 | never invent a job | guard | L98, L141, L520, ... | 17 | batch template, deep dive, no-match | MERGE + pointers | law 1; 6b template; 7 | one statement, one-line pointer at each composition site |
| T-apply | `apply_job` payload | tool contract | L1673-1783 | 1 | step 10 | KEEP | Tools / apply_job | never dropped |
| L-pin-ask | ask-pin line | spoken line | L540 | 1 | Turn B, no pin held | KEEP + demonstrate | Turn B; worked call B | branch must be demonstrated (D102) |

`kind` is one of: tool contract, input variable, spoken line, named ban, branch, guard/rule, owed
item, TTS/script rule, situation, worked example, provenance.

Decision rules:

- [ ] **KEEP** every never-drop item (section 2). No exceptions without the owner's written yes.
- [ ] **MERGE** a rule stated N times into **one statement at its point of use**, and leave a
      **one-line pointer at every other site where the governed text is composed**. Record the
      number of statements before and after. "Times stated" going from 17 to 3, all at the top of
      the file, is how KKB Slim started inventing jobs (`45e2cb3b`, `a4f378b9`; fat was clean on 5/5).
      Consolidate to the *composition site*, not to the top of the file.
- [ ] **DROP** only provenance, duplicates, and surplus sample dialogue. Every DROP row names where
      the content still lives (changelog, bug-patterns) or why it is dead.
- [ ] A ban **quoting a template with a slot** (e.g. "never 'आप Any का काम देख रहे हैं'") is also a
      ready-made sentence (`69155e23` spoke it verbatim). Keep the ban as a class, and quote the
      exact string only when the exact string is the failure.
- [ ] Any row you cannot classify: stop and ask.

### Step 5. Write the slim prompt from the flow, not from the text

Do not compress the old file sentence by sentence. Rewrite it around the call:

- [ ] **Numbered steps in the order the call happens**, each owning its turn(s), each saying what it
      guarantees. Then reference sections the steps point into (Tools, No-Match once, Speaking,
      Hearing, Situations) and never restate. Add the flow map to the bot's slim README so the
      design is reviewable without reading the prompt (`9a71555`).
- [ ] **Instructions in English; only spoken lines in the target language** (root `CLAUDE.md`).
- [ ] **Tables for parallel cases** (failure rows, input -> decision), but never a table whose cells
      can be read aloud as a sentence. Use a separator like ` · ` in input/decision tables (D102).
- [ ] **Every guard must be checkable from the turn being composed.** No running counts across turns
      (D76: the ordinal counter failed on 14/24 multi-batch calls), no "recall the tool result from
      five turns ago". If the source relies on cross-turn state, flag it; do not silently keep it.
- [ ] **Skip tests and tool triggers are defined by type, and name the weaker fact they must not
      accept** (D95). "Skip if you can point at a landmark" let an area satisfy a landmark test
      (asked on 2/12 calls with area+pin vs 5/6 without).
- [ ] **Every "do not invent X" has a MANDATORY, terminal honest path when X is absent** (D98), not
      just a guard against misusing the escape line.
- [ ] **Prohibitions name every kind of thing that could fill the slot**, not one category (D97:
      "never in the same turn as another question" let a statement share the turn, `d4dd4668`).
- [ ] **Terminal phrases are scoped to the turn** ("nothing follows it in this turn") and every
      exit checklist lists every owed item (D96).
- [ ] **No promise of finality before the last turn.** A line saying "आखिरी सवाल" makes every turn
      after it unreachable (the pin turn never fired behind it: `d47db4c0`).
- [ ] **No `[slot]` markers or `*( )*` notes inside spoken templates or example dialogue lines**
      (D77). Annotations go outside the quoted turn.
- [ ] **Tool schemas are not a shortcut.** Do not move a skippable step into a required tool
      parameter to save prose: the model fills it falsely (D91, `6ae79885`).

### Step 6. Worked examples: few, real, branch-complete, and unfabricable

The examples are what the model actually follows (D50). In a slim prompt they carry more weight,
not less, because there is less prose around them.

- [ ] **Few**: one worked call per distinct path, chosen for disjoint paths (KKB: 2 at first, 4 by
      October). Each shows its **input state** so the branch taken is visibly caused by the input.
- [ ] **Every branch of every multi-branch step is demonstrated at least once.** A branch described
      only in rule prose fired 0 times in 41 calls (D102).
- [ ] **Every example performs every mandatory step** on its path (disclosure, offer, read-back).
      Count it: "k of N examples close without the offer" is a finding.
- [ ] **Values drawn from real data, varied, and never reusable as a fabrication.** No concrete value
      (pin, phone, name, company, id, salary) repeated across examples; each example value paired
      with its own place so it cannot be transplanted. KKB's examples used pin `110045` 12 times and
      the bot read it back to callers who had no pin (`2027e477`, `d9111476`, `ff13bfaa`).
- [ ] **Example values must not be in the current live inventory or a tester profile** in a way that
      lets the bot "find" them, and must match the bot's real backend (no Bengaluru examples on a
      Ghaziabad bot, D105).
- [ ] **No JSON example whose field values could become an output.** An output-prompt example value
      was copied verbatim as `call_direction: "outbound"` on an inbound call (`2027e477`).
- [ ] **Examples do not demonstrate a shortening the rules forbid** (KKB's location table collapsed
      `Muradnagar, Delhi 110098` to one word, and the bot did exactly that: `591e5c28`, `6ff40ebb`).

### Step 7. Static audit: prove nothing was lost before any call

```bash
python3 raya/slim/compare_spec.py "<source prompt>" "<slim prompt>" --json raya/slim/<target>/diff.json
```

- [ ] **Every dropped spoken line classified by hand** (KKB: 118 drops, each one a forbidden quote,
      a past-bug quote, a caller utterance, a table cell or a twin-language line; 2 real drops found
      by grep and restored). Zero unexplained drops.
- [ ] **Zero new spoken lines** unless the owner asked for a behaviour change.
- [ ] **Coverage table diff**: every source row has a slim location or a justified DROP.
- [ ] **Input-variable set identical** to the source's real arguments. Raya derives `agent_args` from
      the `${...}` tokens in the instructions (the fat KKB prompt carried a stray `${college_name}`),
      so a token added or lost changes the agent's arguments. Use the broad token pattern from
      `../sync-check/reference/n-language-parity.md` (camelCase names exist).
- [ ] **Orphaned references**: grep every heading, step number, case/path/row label and section name
      that the rewrite removed or renamed, across the whole slim file. KKB Slim still says
      "go to Need Capture" and "Path A" after the services step replaced that section, and law 1
      still says "Never call `get_jobs`" after `get_jobs` became one of its tools (both copied into
      the Kannada twin for parity, 2026-10-05). Also every `per step N` / `see section X`
      cross-reference (D51, D97).
      ```bash
      grep -n -E 'Need Capture|Path [A-Z]|Case [A-Z]|Row [0-9]|per step|see section|step [0-9]+' "<slim prompt>"
      ```
- [ ] **Guard placement**: for each MERGE row, confirm the pointer exists at every composition site
      listed in "points of use".
- [ ] **Example audit**: every concrete example value grepped across the examples (no repeats) and
      every branch demonstrated (step 6).
- [ ] **Memory block** present byte for byte; **instructions English-only**; no `[slot]`/`*( )*`
      inside spoken lines.
- [ ] **`/prompt-analyser`** on the slim prompt. Fix every critical/major finding through this
      skill's rewrite before deploy (it is still a new file, not yet a live prompt).
- [ ] Record the final char count in the coverage file.

### Step 8. Register as a NEW variant on its own agent via `/register-bot`

Never overwrite the production prompt and never deploy the slim file to the production agent.

- [ ] Folder `<Bot>-Slim/` with the slim conversation file(s) and a `CHANGELOG.md` whose header says:
      A/B twin of `<source-target>`, the ONLY difference is the conversation prompt, not a language
      variant, so `/sync-check` must not treat it as a mirror of the production prompts.
- [ ] Path-map row in root `CLAUDE.md`; `raya/agents.json` target `<bot>-<lang>-<variant>-slim` with
      an `_note` (clone source, "no production traffic until the A/B has run") and
      `expected_name_contains` carrying both `Slim` and the language token.
- [ ] Clone the agent so the prompt is the only difference:
      ```bash
      python3 raya/slim/create_slim_bot.py --source <source-uuid> --name "<Bot> Slim- <Lang> (A/B)" --instructions "<slim prompt>" --dry-run
      python3 raya/slim/create_slim_bot.py --source <source-uuid> --name "<Bot> Slim- <Lang> (A/B)" --instructions "<slim prompt>"
      ```
      (for a slim mirror in another language, `scripts/raya_clone_agent.py plan|apply <settings_target> <language_target> ...`).
      The create endpoint rejects some keys, so it is POST-then-PATCH. Tool blobs carry live keys:
      moved in memory, **never written to disk, never committed**.
- [ ] **Verify field by field** after creation: language and voice ids, whole tool schema, DIDs,
      interruption and silence timings, nudges, max duration, webhook, memory and output prompts.
      Any difference voids the A/B.
- [ ] uuid copied by hand from `python3 scripts/raya_deploy.py list` (the `/register-bot` uuid rule).
- [ ] Add the slim target to the regression fleet; add a `raya/divergences.json` entry for anything
      the slim family deliberately does differently from production.
- [ ] If the slim agent will own its own output or memory prompt, give it its own file (KKB Slim's
      live output prompt drifted 18,274 vs 15,068 chars ahead of the shared one before it was adopted
      into `KKB-Slim/KKB Slim Output.md`).

### Step 9. Deploy to the slim agent only

```bash
python3 scripts/raya_deploy.py deploy <slim-target>     # PATCH, verified against the PATCH response
```

Record in `raya/deploy-history.md`. Read-back proves it shipped, never that it behaves.

### Step 10. Test: every tier, on the slim agent, every language

The whole prompt was rewritten, so **every branch is a changed branch**.

1. **Build the suite**: `/generate-test-cases` on the slim target, seeded from the coverage table
   (one scenario per branch row, one per tool contract, one per owed item, one per early exit).
   Reuse the source bot's checklist (`.claude/skills/voice-test/reference/checklists/<bot>.md`) plus
   `generic.md`, so both sides are graded on the same list.
2. **Tier 1, equivalence**: `/voice-test` every scenario on the slim agent, **N >= 3 per branch**,
   same persona, same fixture class. Report `k/N`; `0 < k < N` is `UNRESOLVED`, never "flaky".
   - Assert against the **input**, not just the behaviour: "read back THE INPUT'S pin" (D102).
   - Fixture hygiene: split harness dials from real callers before quoting any rate. Every KKB
     location "substitution" was manufactured by a fixture that disagreed with the tester DID's
     stored profile (`4b6ab6e`).
3. **Tier 2, A/B against the source** (same fixture, same persona, dialled **alternating**, at
   least 3 pairs, more if turn counts differ):
   ```bash
   python3 raya/slim/ab_compare.py --selftest
   python3 raya/slim/ab_compare.py --pairs 3 --fixture <args.json> --persona raya/personas/<persona>.md
   ```
   Report per side: median seconds per agent turn **with the turn counts**, invariant failures,
   and the bot-checklist pass rate. A failure class counts as a **slim regression only if the source
   passes it on the same fixture across N calls**. One call is an anecdote: KKB first recorded a
   slim regression on Latin company names off `90658584` vs fat `02c5f7f0`, then fat `ea0477f4`
   did it five times in one call.
4. **Tier 3**: the slim target is in the daily fleet (step 8). It does not replace tiers 1-2.

Every claim names a call id. Untested items are **DEPLOYED, NOT VERIFIED** or **VERIFY-PENDING**,
per row.

### Step 11. The decision gate: before ANY traffic moves

Present the owner one table: chars (source vs slim), median s/turn (both), checklist pass rate
(both), failure classes new in slim (must be zero), failure classes shared, branches still
`NOT_EXERCISED`, and languages verified. Traffic moves only on the owner's explicit yes, and only as
a recorded config change with the prior state saved for rollback (KKB moved the inbound DIDs on
2026-10-05 with state in `raya/live-snapshots/inbound_move_2026-10-05.json`). Then a post-move
real-traffic transcript review before anything is called "confirmed".

### Step 12. Mirror to every language

- [ ] The slim variant is a **new sync family**: slim master + slim mirrors. It is never a mirror of
      the production prompts, and `/sync-check` audits slim master against each slim mirror.
- [ ] Author each slim mirror from the **slim master** with the `/translate-prompt` rules: English
      instructions byte-identical, spoken content re-authored (reuse proven wording from that
      language's production prompt where an equivalent line exists), TTS/script machinery re-derived
      natively, examples re-set in local places with their own values, a fragment map, and a
      zero-foreign-script assertion so a missed line fails the build (the Kannada slim was built
      this way: no Devanagari allowed).
- [ ] Persona/name choices that differ by language are registered divergences (KKB Kannada slim
      speaks as ಮಾಯಾ to match its production twin, so the A/B compares like with like).
- [ ] **Each language is tested independently** through steps 10-11. The Kannada slim invented jobs
      on a missing array while the Hindi slim did not (`24e5dabd`, `7fa799eb`; D98).
- [ ] From now on there are two families to keep aligned. A fix landing in production that also
      applies to slim goes through `/port-feature`; note it in both changelogs.

### Step 13. Changelog, analyser, snapshot

- [ ] `<Bot>-Slim/CHANGELOG.md` entry: why, measured composition, size before/after, the never-drop
      checks, the A/B numbers, files, and a status per fix (DEPLOYED, NOT VERIFIED until each has a
      call id). Also a one-line pointer entry in the source bot's `CHANGELOG.md`.
- [ ] Every bug found during the slim work (including in the source) gets a `bug-patterns.md` entry
      via the normal bug-fix loop, plus `section-checklists.md` if it implies a mandatory section.
- [ ] `scripts/prompt-version.sh save <Bot>-Slim slim-v1 "first slim deploy"` and keep the first
      draft as a reference file so later passes can be diffed against it (KKB: `slim-v1-reference.md`).
- [ ] **Size budget**: record the char count in every later changelog entry. Slim prompts regrow:
      KKB Slim Hindi went from 68,744 to 127,826 chars as the live job/services APIs and new steps
      were added. Re-run steps 2 and 7 whenever it grows by more than ~20%.
- [ ] All later content edits to the slim files go through `/update-prompt` (or `/port-feature`).
      This skill only creates the slim variant; it is not a second edit path.

### Step 14. Report (short, root `CLAUDE.md` format)

- **Size**: source chars -> slim chars (%), floor and why.
- **A/B**: s/turn both sides with call ids, checklist pass rate both sides.
- **Verified / failed / not exercised**: one line per branch group, with call ids.
- **New bugs found**: one line each.
- **Next**: one line (usually the owner decision in step 11).

---

## Guardrails

- Never edit, overwrite or deploy over the source/production prompt. The slim file is new.
- Never drop a never-drop item (section 2) to hit a number. Below the floor, give the owner a menu.
- Never claim a quality gain from size alone. Report the measured latency delta, whatever it is.
- No behaviour changes smuggled into the rewrite. A deliberate one (e.g. dropping a cross-turn
  counter) is its own experiment, slim-only, owner-approved, measured alone, and recorded.
- Never write a third wording of a guard that failed twice, on either side; and never leave a rule
  aimed at the wrong mechanism in place (`d48bc07` was reverted 0/3 because it was).
- Tool snapshots never touch disk. Real users' numbers are read-only; test on the tester DID.
- No em dashes in anything this skill writes.

---

## Lessons from the KKB slim rewrite (Sept-Oct 2026)

| # | what happened | evidence | the rule it produced |
|---|---|---|---|
| 1 | 69% smaller bought ~7% per turn (16.00 vs 14.75 s); both prompts failed the same classes | `7d164b9`, `raya/slim/README.md` | section 1: be honest about the payoff |
| 2 | A slim "regression" was a one-call anecdote; fat did the same thing 5 times in one call | `90658584` vs `02c5f7f0`, then `ea0477f4` | step 10: regression only if source passes across N |
| 3 | Consolidating "never invent a job" from 17 statements to 3 at the top made the slim bot invent jobs on a 1-job array (2 of 3 dials) | `45e2cb3b`, `a4f378b9`; changelog 2026-09-09 | step 4: merge to the composition site, pointers elsewhere |
| 4 | The ask-pin branch was never demonstrated; it fired 0/41 and the example pin 110045 was read back to callers with no pin | `2027e477`, `d9111476`, `ff13bfaa`; D102 | step 6: demonstrate every branch, never repeat a value |
| 5 | The location examples collapsed two place words to one, and the bot copied them | `591e5c28`, `6ff40ebb` | step 6: examples must not demonstrate a forbidden shortening |
| 6 | An output-prompt JSON example became the answer (`outbound` on an inbound call) | `2027e477`; D50 | step 6: no copyable example values |
| 7 | `*( )*` stage directions from worked examples were spoken aloud (3/52 calls) | `b17a3bf2`, `bec28724`, `24e5dabd` | step 5: no notes inside example turns |
| 8 | Orphaned references survived later extensions: "Need Capture", "Path A", law 1 "Never call get_jobs", a stale "per step 11" clause | slim Hindi L392, L847, L1254, L1351; `d4dd4668`; D97 | step 7: orphan grep after every structural change |
| 9 | The pin turn never fired because the landmark line before it promised "आखिरी सवाल" | `d47db4c0`, `9c9f7e34` | step 5: no finality promise before the last turn |
| 10 | The landmark skip test accepted an area (2/12 vs 5/6 by input) | `462e2425`, `88c8ecdd`; D95 | step 5: tests by type, name the weaker fact |
| 11 | A pre-close checklist naming one item excused the services offer after a failed apply | `c883aa34`, `670cbb12` -> `6ae79885`; D96 | step 5: list every owed item |
| 12 | The Kannada slim invented jobs and applied with an invented job id when the array was missing | `24e5dabd`, `7fa799eb`; D98 | step 12: each language tested on its own |
| 13 | A required tool parameter meant to force the location turns was filled falsely and the turns skipped | `6ae79885`; D91 | step 5: schema is not a shortcut |
| 14 | An experiment built on a wrong diagnosis (fixture confound) was reverted 0/3; all "substitutions" were harness dials | `d48bc07`, `4b6ab6e` | step 10: split harness vs real callers |
| 15 | The ordinal counter failed 58%; removing it was proven on the slim bot first | `26a6314`, `0ab57b0`, `43e7e5e4` | section 1: the slim bot is the experiment bed |
| 16 | `extract_spec.py` paired quotes file-wide and hid 3 real lines; its tool regex is hard-coded | `9afc12a`, `raya/slim/README.md` | step 3: check the tool list by hand |
| 17 | A stray `${college_name}` gave the fat agent a seventh argument | `raya/slim/README.md` | step 7: token set must match |
| 18 | The slim agent's live output prompt drifted ahead of the shared file | `a9922c6` | step 8: own file for own prompts |
| 19 | The slim prompt regrew from 68,744 to 127,826 chars | `KKB-Slim/KKB Slim Hindi Signals.md` today | step 13: size budget per changelog entry |

Related analyser patterns: D50, D51, D71, D76, D77, D78, D91, D95, D96, D97, D98, D101, D102, D103,
D105 (`.claude/skills/prompt-analyser/reference/bug-patterns.md`).
