---
name: onboard
description: Customer-facing intake for a NEW user, customer, or project bringing a voice bot to the Prompt Tuner. Walks them, one friendly question at a time, through sharing everything needed to start improving and testing their bot — which project it belongs to (Blue Dots / Purple Dots / other), what the bot does, who the callers are and any access needs, every language it speaks and which one is the master, the prompt(s), the platform (Raya) + agent uuids/DIDs, the tools/APIs it calls, their test cases + success criteria, and the issues they want fixed captured as individually testable issue records with stable ids. Produces a concrete intake summary the tuner can act on, then immediately reproduces each reported issue via /voice-test before any fix, and hands off to /register-bot, /prompt-analyser, /generate-test-cases, /translate-prompt or /update-prompt. Use when someone new arrives, says "I have a bot I want to improve", "help me get started", "onboard my agent", "onboard a new project/bot", "here are the issues we want fixed", or you don't yet know which bot they mean.
---

# Onboard — new-customer intake

Someone new has come to the **Prompt Tuner** with a voice bot. Your job here is to make them
feel welcome and collect — in plain language, **one question at a time** — everything we need
to start improving and testing their bot. You are the friendly front desk, not an interrogator.

The Tuner is a **shared rail across several BlueDot-team projects**, not a three-bot tool. Assume
**N projects, N bots, N languages**: whoever is in front of you may be bringing a bot in a language
we've never handled, for a project that doesn't exist in the repo yet. That's normal — never imply
they have to fit into KKB / DKB / Maya or into Hindi and Kannada.

**What the Prompt Tuner does for them (say this in your own warm words up front):**
we take their voice bot's prompt and (1) iterate on it from real feedback and bugs, (2) keep
its language versions in sync so a fix in one language always lands in the other, (3) deploy the
updated prompt to the live agent, (4) **test the bot ourselves** by having a "tester" agent
role-play a caller, place a real call, and grade the transcript — so we catch problems before
their users do — and (5) **take the bot into new languages** when they want it: a version that
reads as the language is actually spoken, not a dictionary translation.

## How to run this (tone + pace)

- **One question at a time.** Ask, wait, acknowledge the answer, then ask the next. Never dump
  the whole list at once.
- **Plain, friendly, non-technical.** No jargon walls. If they don't know an answer, that's fine —
  note it as "TBD" and move on; we can start with less (see *Minimum to start*).
- **Say what happens with each answer** as you collect it (see *What each answer unlocks*), so they
  see the value of sharing it — but keep it to a sentence, don't lecture.
- **Take issues one at a time and write each as a testable record, not prose.** When they start
  listing what's broken, slow down and capture each complaint as its own **issue record with an id**
  (see *Structured issue capture*). A paragraph of complaints cannot be tested; a list of issue
  records can.
- **Promise a test, never a fix.** It is fine — and honest — to say "we'll reproduce that on a real
  call first". Some reported bugs turn out to be input or backend faults, and we say so rather than
  editing a prompt.
- **Do not touch any prompt file, `agents.json`, or the live agent during onboarding.** This skill
  only *gathers*, *files an intake summary*, and *runs reproduction test calls*. Editing,
  registering, and deploying happen later through the proper skills. Onboarding is
  read-record-and-reproduce only.

---

## Step 1 — Warm open + which project + which path

Greet them, give the one-paragraph "what we do for you" above, then settle two things — still
**one question at a time**, and still conversationally.

**First, the project.** *"Which project is this bot part of?"* The project is what scopes
everything downstream — the bot's folder, its section of the path map, its `agents.json` target
ids, its regression-fleet entry and its digest label — so it's worth 10 seconds up front.

- **Blue Dots** — the employment rail (KKB job-matching, DKB employer, Maya campus).
- **Purple Dots** — the rail for **people with disabilities**.
- **Anything else, including something brand-new** — perfectly fine. Record the project name and
  treat it as first-class (`project: <kebab-case-name>`), never as an exception.

Record it as `project:` in the intake summary. If they don't think in "projects", ask who owns the
bot and use that as the project name.

**Then, the path.** *"Is this a bot we already work on, or a new bot you're bringing to us?"*

- If the bot is **already registered in `raya/agents.json`** — today that's KKB / DKB / Maya and
  their language × direction variants, but *the manifest is the test, not the name* → **Branch A**.
- If it's a **new bot** — including a bot that already runs live somewhere but has no `agents.json`
  entry yet → **Branch B**.

If unsure, glance at `raya/agents.json` and match on `agent` / `raya_name` / `raya_agent_id`. Every
registered target carries its own `language` and `direction`, so the manifest answers "do we
already have this one?" without guessing from the bot's filename (a real pitfall: "KKB Placeholder
Inbound.md" is the *Hindi* inbound bot — the name doesn't say so).

---

## Branch A — a bot already registered in `raya/agents.json`

This is quick. We only need to pin down *which* target(s), then we can go straight to work.

Ask, one at a time:
1. **Which bot?** (Any bot in the manifest — the friendly examples are KKB job-matching, DKB
   employer, Maya campus, but it may equally be a newer project's bot. Take whatever name they use
   for it and resolve it against the manifest yourself.)
2. **Which language(s)?** (Whichever ones that bot speaks — KKB/DKB run Hindi + Kannada today,
   Maya is Hindi-only, another project's bot may speak a completely different set. If more than
   one, note which is the **master**. If they want a language it doesn't speak yet, that's a
   **`/translate-prompt`** job — note it, don't try to solve it here.)
3. **Inbound or outbound?** (the bot receives calls, or the bot places them — a bot can have a
   registered target for each, and they are tested separately.)

Then confirm the match against `raya/agents.json` — each target has an `id` (e.g. `kkb-hi-out`,
`dkb-kn-out`, `maya-hi-in`), its prompt `file`, and its `raya_agent_id` per environment. Read back
what you found: *"Great — that's `<id>`, prompt at `<file>`, live on Raya as `<raya_name>`."* If it
turns out the bot **isn't** in the manifest after all, don't force it — that's Branch B plus
`/register-bot`.

Confirm we can proceed straight to a grounded briefing and a test pass:
- **The grounded briefing, from in-repo sources** — read `raya/intake/<bot-id>.md` (if the bot was
  onboarded before), its `raya/agents.json` entry, the bot's `CHANGELOG.md`, and `docs/WORKFLOW.md`
  for how the pipeline chains; **`/prompt-analyser`** gives the read-only pre-flight on the prompt
  itself. (The vault's `/load-context` is a *vault-only* skill — available only when working from the
  EkStep vault root; skip it if you only have the Prompt Tuner repo.) Then
- **`/voice-test`** to run a first call and grade it, or **`/bug-fix`** if they arrived with a
  specific reported bug already logged in the tracker.

Still fill in a short intake summary (below) capturing anything new they told you (a fresh bug,
a new test scenario, a language they want added). If they arrived with complaints, capture each one
as a **structured issue record** (next section) rather than prose — then run *Step 2 — Reproduce the
reported issues* before anyone edits a prompt. Then hand off.

---

## Branch B — a new bot they're bringing

Collect the following **one item at a time**, in this order. After each answer, drop the
one-line "here's what that lets us do" note. Record answers into the intake summary as you go;
mark anything missing as **TBD** rather than blocking.

**(a) What the bot does.** What's the bot's job? Who does it talk to, and what's the goal of a
single call? (domain • audience • the outcome a good call reaches)
→ *Unlocks:* the bot's persona/audience, which test **checklist family** fits, and a new entry in
`../port-feature/reference/agent-schemas.md` so future edits know its shape.

**(a2) Who the callers are, and how the bot should speak to them.** Ask this gently, as *audience
understanding*: **"Tell me a little about the people who'll be on the other end of the call — and is
there anything about how they'd want the bot to talk to them? Speaking pace, being patient when
there's a pause, happy to repeat something if they ask?"** Write down whatever they say (speak
slower, leave longer before re-prompting, always repeat on request, keep turns short, don't rush a
decision, don't assume the caller can answer at a default speed, offer a spoken menu rather than
expecting a free-form answer). "Nothing special" is a perfectly good answer — record it and move on.
**Never make a caller's disability or condition a topic of the call.** It is a constraint on *how
the bot speaks*, never something the bot raises, names, or asks about.
→ *Unlocks:* access-needs grading (pacing, silence tolerance, repeat-on-request, short turns) — these
items land in the **generic** checklist's Accessibility section (`generic.md` §14), which every bot on
the rail is graded against, **and** additionally as this bot's own **`X`**-family cases in
`raya/testcases/<bot-id>.json`. Plus pacing/patience rules written into the prompt up front instead of
being discovered from a bad call later.

**(b) Languages + source of truth.** Which languages does it speak today? If more than one, **which
one is the master** that we edit first and mirror from? And are there languages they *want* it to
speak that it doesn't yet?
→ *Unlocks:* the file map and the **sync rule** — we edit the master language, then mirror
language-agnostic logic verbatim to **each** mirror language and translate/adapt only the spoken
lines (for KKB/DKB that's Hindi → Kannada; for an N-language bot it's master → every mirror, and
`/sync-check` audits the master against all of them). A language it doesn't speak yet is **not** a
mirror job — it's a **`/translate-prompt`** job: a version in the language as it's actually spoken,
with that language's own TTS number-words, script rules and code-mixing conventions re-derived from
scratch, plus a new Raya agent to run it.

**(c) The prompt(s).** Can you paste the conversation prompt, or give a file path? One per
language. Also: does the bot have a **memory** prompt (remembers the caller between calls) and/or
an **output** prompt (pulls structured results out of each call) — or just the conversation prompt?
→ *Unlocks:* where each file gets filed under our path-map convention (see *What each answer
unlocks*), and — if memory is on — the required memory-injection block in every conversation prompt.

**(d) The platform.** Does the bot run on **Raya** (our deploy + test platform)? If yes: the
agent **uuid(s)** (there is usually one per language, and another per direction), and
the **phone number / DID** each uses. If it's **not** Raya, tell them what we can still do (iterate,
sync, and analyse the prompt files; design test cases) and what we can't do automatically
(one-click deploy and the agent-to-agent call harness are Raya-specific).
→ *Unlocks:* registering the bot as a **deploy target** in `raya/agents.json` and, if Raya, running
live tests against its DID.

**(e) The tools / APIs the bot calls.** Does the bot call any tools or backend APIs during a call
(look up a profile, apply to a job, post a job, etc.)? For each: the endpoint, how it authenticates,
the payload shape, any **fixed parameters** that must never change, and any known limits/quirks.
→ *Unlocks:* our edits will **preserve those payloads exactly**, and our tester + analyser can verify
the right tool actually fired with the right values.

**(f) Test cases + what "good" looks like.** What scenarios do you already want covered (the happy
path, tricky callers, edge cases)? And for each, **what does a successful call look like** — the
success criteria we grade against?
→ *Unlocks:* these become tester **personas** and bot-specific **checklist** items on top of our
generic checklist — i.e. exactly what we grade the first test call against.

**(g) The issues they want fixed — one testable item at a time.** Anything misbehaving right now?
Don't take this as a paragraph. Walk them through their list **one issue at a time**, and for each
one get: the symptom in a single line • which bot/language/direction it happens on • how to make it
happen • what should have happened instead • the call reference/uuid if a real call shows it (that
one is gold — **we never fix a bug without seeing the actual call transcript**) • and how badly it
hurts. Write each as an issue record with its own **issue-id** — see *Structured issue capture*
below.
→ *Unlocks:* one named reproduction test case per issue-id (`/generate-test-cases`), the
reproduction calls in *Step 2*, and a per-issue answer to "is this one fixed yet?" that still makes
sense to a third person two months from now.

If they trail off or don't have much, that's fine — jump to *Minimum to start*.

---

## Structured issue capture (the issues they want fixed)

The most valuable thing this intake produces. Every issue the customer wants fixed becomes **one
record with a stable id**, and that id is what every downstream step keys off — so "is issue 3
fixed?" has a real answer instead of a feeling. Applies to both branches.

### The issue-id

`<bot-key>-i<NN>` — the bot's short key, then a two-digit number: `kkb-i01`, `pd-i03`, `dkb-i07`.

- **Bot-scoped, not variant-scoped.** One symptom appearing in three languages is **one** id with
  three affected variants — not three ids. (Each of those variants is still tested separately.)
- **Assigned in the order raised; never renumbered, never reused.** A closed `pd-i02` stays `pd-i02`
  forever, so an old test case, changelog line, or analyser note still resolves years later.
- **Lowercase and hyphen-safe** — it becomes part of filenames and run labels.

### The record

Ask for each field in plain language. **TBD** is allowed everywhere except *symptom* and *where*
(without those there is nothing to test).

| Field | What goes in it | Notes |
|---|---|---|
| `issue-id` | `<bot-key>-i<NN>` | You assign it, then read it back to them ("let's call that one `pd-i01`"). |
| `symptom` | ONE line, in observable terms: what the caller hears or experiences. | "The bot asks for the phone number twice" — not "memory is broken". Diagnoses go in the root-cause step, not here. |
| `where` | The affected variants, as `raya/agents.json` target ids: `pd-hi-out`, `pd-kn-in`, … | List them explicitly. **Never write "all languages"** — we test every variant independently, so we need the actual list. "Unknown, to be probed" is a legitimate value. |
| `trigger` | How to make it happen: caller state (new vs returning), the input/`agent_args` values that matter, and the turn or step where it shows up. | This is the field a tester **persona** is written from. Vague trigger ⇒ unreproducible issue ⇒ no fix. |
| `expected` | One concrete line: what should have happened. | |
| `actual` | One concrete line: what happened instead. | |
| `call-ref` | Real Raya call uuid(s) that show it, with dates. | "none yet" is fine **at intake** — it blocks the *fix*, not the intake. Ask for it; it is the cheapest possible reproduction. |
| `severity` | `blocker` · `major` · `minor` · `wish` | `blocker` = the call fails, a wrong action fires, or wrong data is written. `major` = the task completes but degraded. `minor` = wording/cosmetic. `wish` = a feature request wearing a bug's clothes — name it as a feature out loud, kindly. |
| `status` | The ladder below. | Starts at `reported` for everything. |

### The status ladder (one issue's whole life)

```
reported                        as the customer described it — nothing verified yet
  ├─ repro-confirmed            a real transcript shows the failure  → eligible for a fix
  ├─ no-repro                   we tried and it didn't happen        → need a reproducing call uuid
  └─ not-a-prompt-bug: data-input | backend | runtime-adherence      → no prompt edit; say why
       ↓ (from repro-confirmed, after /update-prompt + deploy)
fixed-for-uat                   edited + deployed, awaiting the customer's acceptance test
  ↓
verified                        a POST-deploy transcript shows the corrected behaviour,
                                on EVERY affected variant
```

`fixed-for-uat` is **not** "confirmed". Only `verified` is, and only with a post-deploy transcript
per variant. If the customer's issues also live in the Consolidated Feedback Tracker (`All Issues`),
carry the same issue-id into the sheet row so the two never drift apart.

### Record it in the summary as a table

```
| issue-id | symptom | where (target ids) | trigger | expected | actual | call-ref | severity | status |
|---|---|---|---|---|---|---|---|---|
| pd-i01 | Bot re-asks the caller's name after they've given it | pd-hi-out, pd-kn-out | returning caller, profile exists; happens at the pre-apply field check | name taken from the fetched profile, not re-asked | asks again in turn 6 | 3f9c… (2026-08-03) | major | reported |
```

### How these ids are reused downstream (why the format matters)

- **`/generate-test-cases`** emits, per issue-id: a reproduction persona
  `raya/personas/<lang>-repro-<issue-id>.md` and a bot-checklist item in
  `.claude/skills/voice-test/reference/checklists/<bot>.md` tagged `[repro <issue-id>]` with explicit
  pass/fail detection (what in the transcript / `tool_calls` / `call_output` proves it).
- **`/voice-test`** runs each reproduction with the label `repro-<issue-id>-<target-id>`, so every
  dumped transcript says which issue and which variant it belongs to.
- **`/update-prompt`** cites the issue-id in the bot's `CHANGELOG.md` entry; if it was a bug, the new
  `/prompt-analyser` bug-pattern entry cites it too — that's how the failure class gets caught
  pre-emptively next time.
- **The standing regression suite** can carry the same id on its case, so a fixed issue that comes
  back is caught by name rather than rediscovered.

---

## What each answer unlocks (the mechanics, grounded in this repo)

Tell the customer the relevant bits in plain terms; the detail here is for you.

- **Where the prompt gets filed — path-map convention.** Each agent lives in its own top-level
  folder with files named `<Bot> <Language>.md` for conversation, `<Bot> Memory.md` for memory,
  `<Bot> Output.md` for output. (Existing examples: `KKB/KKB Placeholder Hindi.md`,
  `DKB/DKB Kannada.md`, `Maya/Maya Hindi.md`, `KKB/KKB Memory.md`, `KKB/KKB Output.md`.) A new bot
  named e.g. *Chai* would get `Chai/Chai Hindi.md`, `Chai/Chai Telugu.md` (one file per language it
  speaks — the set is whatever they told you in (b), not a fixed pair), plus optional
  `Chai/Chai Memory.md` / `Chai/Chai Output.md`, and a fresh `Chai/CHANGELOG.md`. The canonical
  path map is in the repo-root `CLAUDE.md`; you don't edit it here — **`/register-bot` creates the
  folder, the files and the path-map entry** from this intake summary, and it is `/register-bot` that
  adds the **per-project** sections (a `### Projects` list plus a long-form table per project) the
  first time a new project is registered.
- **How it becomes a deploy target — `raya/agents.json`.** Each conversation prompt (per language,
  per direction) is one entry with: `id`, `file`, `agent`, `language`, `direction`,
  `kind: "conversation"`, `profile: "conversation"`, `expected_name_contains` (wrong-target guard),
  `raya_name`, `raya_agent_id: { prod, staging }`, and `deploy`. **The uuid is filled by hand from
  `scripts/raya_deploy.py list` — never inferred from the filename** (a real pitfall: "KKB
  Placeholder Inbound.md" is *Hindi*, not obvious from the name). Memory/output are separate
  entries with `kind`/`profile` `memory`/`output`. Target ids follow
  `<project-or-bot-key>-<lang>-<direction>` (`kkb-hi-out`, `pd-te-in`) — one entry per language ×
  direction, however many that is. Actually writing these entries is **`/register-bot`**'s job;
  onboarding just records the values (including the project) so the entries can be created.
- **How a tester persona + checklist gets picked — `/voice-test`.** We stand up a **tester agent**
  (an inbound persona role-playing a caller), **trigger the bot under test to call it**, then grade
  both legs. **Every** bot is graded against the generic checklist
  `.claude/skills/voice-test/reference/checklists/generic.md`. If the bot matches a family we already
  have, we also use its bot-specific checklist (`.../checklists/<bot>.md` — today `kkb`, `dkb`,
  `maya`); a brand-new bot gets its own `<bot>.md` seeded by **`/generate-test-cases`** from the
  success criteria in answer (f) and the issue records. Their scenarios become personas in
  `raya/personas/`, one per language the bot speaks.
- **How access needs become checks.** What they told you in (a2) lands in two places: the **generic**
  checklist's Accessibility section (`generic.md` §14) — pacing, silence tolerance, repeat-on-request
  and short-turn behaviour, graded on every bot on the rail; that file grades the whole fleet, so any
  change to it needs the owner's explicit approval (see `docs/WORKFLOW.md`) — **and** this bot's own
  **`X`**-family cases in `raya/testcases/<bot-id>.json`, seeded by `/generate-test-cases` (family `X`,
  taxonomy §6). The concrete pacing rules they asked for become prompt instructions via
  `/update-prompt` (written in English, with only the spoken lines in the bot's language).
- **What the customer gets back.** A **grounded briefing** on their bot (assembled from
  `raya/intake/<bot-id>.md`, its `raya/agents.json` entry, the bot's `CHANGELOG.md` and
  `/prompt-analyser`) plus a **first test pass** (via `/voice-test`) graded against generic +
  bot-specific checklists, a **reproduction verdict on every issue they reported** (confirmed /
  no-repro / not-a-prompt-bug), and a prioritized shortlist of fixes — each routed through
  `/update-prompt` (or `/port-feature` if it's a behavior we already built on a sibling bot).

---

## Produce the intake summary (the artifact)

The deliverable of `/onboard` is a filled **intake summary** the tuner can act on without re-asking.
Use the blank template in `reference/intake-template.md`. Fill every field you have; write **TBD**
for anything still missing (a TBD is a to-do, not a blocker).

- Show the filled summary to the customer and ask them to confirm/correct it. **Read the issue table
  back to them line by line** — that's the part they'll be held to and the part we'll test.
- Offer to save it to **`raya/intake/<bot-id>.md`** (create the `raya/intake/` folder if needed) so
  the next skill picks up exactly where you left off. For an existing (Branch A) bot, use the
  existing target `id` as the filename. Keep the bot key project-unique (e.g. `pd-…` for Purple
  Dots) so two projects can't collide on one filename.

The summary must capture, at minimum: **project** • what the bot does • who the callers are +
access needs • **all** languages + which is master (+ any languages wanted but not built yet) •
prompt file paths (and whether memory/output exist) • platform + Raya uuid(s)/DID(s) • tools/APIs +
fixed params • test scenarios + success criteria • **the structured issue records with their ids** +
any real call uuids • the proposed `agents.json` target id(s) with uuid placeholders • and the
immediate next step.

---

## Step 2 — Reproduce the reported issues (before anyone edits anything)

Onboarding does **not** end at a filed summary. The moment the customer has confirmed it, start
testing **the exact issues they reported** — one reproduction per issue-id, per affected variant.
This step decides whether there is anything to fix at all, and it is where "no fix without a
transcript" is actually honoured.

Work in severity order — `blocker`, then `major`, then the rest. Raya rate-limits call creation
(~1 per ~13 s; space fires >= ~15 s) and bridging is intermittent, so expect to retry a connect; see
`/voice-test` → *Platform reality*.

For each issue-id:

1. **Try an existing transcript first — it's free and instant.** If they gave a `call-ref`, read it
   with `python3 scripts/raya_call.py <bot_uuid>` (then the single-call read) and check whether the
   reported failure is genuinely in there. **Read the call's input `agent_args` too** — a large share
   of reported "bugs" are the inputs, not the prompt.
2. **If no usable call exists, place one.** Write a persona that reproduces the `trigger` (or let
   `/generate-test-cases` write it), load it onto the tester, and fire:
   ```bash
   python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<lang>-repro-<issue-id>.md
   python3 scripts/raya_testcall.py lang    <tester_uuid> <lang>
   python3 scripts/raya_testrun.py  <bot_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "repro-<issue-id>-<target-id>"
   ```
   Full topology, prerequisites and gotchas live in `/voice-test`. If the bot under test is
   **inbound**, the tester can only receive calls, not dial in — do the best available verification
   (post-hoc transcript review + static sanity) and mark the residual **VERIFY-PENDING**.
3. **Grade what comes back** against
   `.claude/skills/voice-test/reference/checklists/generic.md` plus the bot's own checklist, and set
   the issue's `status`.
4. **Test every affected variant independently — never extrapolate.** "It reproduced in the master
   language, so the mirror is the same" is exactly the assumption that burns us: ASR, TTS and runtime
   adherence differ per language, and inbound differs from outbound. One reproduction run per
   `where` entry.
5. **Then classify honestly — push back before fixing.**
   - genuine prompt gap → `repro-confirmed` → route to **`/update-prompt`** (or `/port-feature` if a
     sibling bot already has the fix).
   - the inputs were wrong (values in the wrong field, malformed/missing args, mis-mapped campaign
     args) → `not-a-prompt-bug: data-input`. Say plainly *"the prompt is fine, the inputs were
     wrong"* and **make no edit**.
   - backend 4xx/5xx, placeholder or empty inventory, region-specific endpoint behaviour →
     `not-a-prompt-bug: backend` → escalate for a platform fix; don't experiment on the live flow.
   - the model ignoring an instruction the prompt already states clearly →
     `not-a-prompt-bug: runtime-adherence` → the lever is usually a tool-schema change (e.g. a
     `required` param), not more prose (piling on prose regresses — analyser D25/D40).
   - couldn't reproduce → `no-repro`; ask for a reproducing call uuid and leave it open.
     **Do not fix on a hunch.**
6. **Report back per issue-id**, one line each: id → status → the evidence (call uuid) → the route.
   That list *is* the outcome of onboarding.

`/onboard` still edits nothing. It reproduces, grades and classifies; the editing happens in
`/update-prompt` / `/port-feature`.

**Test before done (inherited).** What you produce here is only the "before" picture. Any fix that
follows is **not DONE until tested**, through the **three testing tiers** in the repo `CLAUDE.md`
(Tier 1 fix verification on the exact repro → Tier 2 blast-radius regression on the neighbours and
the mirrored twin → Tier 3 the daily standing regression), run on **every** affected variant
separately. `fixed-for-uat` is not `verified`. Where a variant genuinely can't be harness-tested, do
the best available verification and mark it **VERIFY-PENDING** — never claim "done" or "confirmed"
on an untested change.

---

## Guardrails a newcomer must know (mention the relevant ones, don't recite all)

These are the house rules that keep a live bot from breaking. Surface them naturally as they
become relevant — e.g. mention sync when they say "more than one language", mention transcripts when
they report a bug.

- **Surgical edits only.** We change the smallest thing the task needs and preserve everything else —
  spoken lines, variable names, tool names, payloads, section structure. No "cleanup" reformatting.
- **Language sync.** The **master** language is edited first; the change is then mirrored to **each**
  other language — language-agnostic logic copied byte-identically, spoken lines translated and
  adapted (for KKB/DKB that's Hindi → Kannada; for an N-language bot it's master → every mirror). A
  fix that lands in one language but not its siblings is a regression.
- **Instructions in English, spoken content in the language.** Every rule/heading/condition in a
  prompt is written in English; only the words the bot actually *speaks* are in the target language.
  A section whose rules are written in Hindi/Kannada/Telugu/… is a bug, not a style choice.
- **Never localize a name.** `${variables}`, tool names and fixed payload params stay exactly as they
  are in every language — they are machine contracts, not words.
- **Bug fix ⇒ changelog + analyser.** Every edit appends to the bot's `CHANGELOG.md` (citing the
  issue-id); every *bug* fix also teaches `/prompt-analyser` to catch that failure class next time.
- **Snapshot before deploy.** We checkpoint the current stable prompt (`scripts/prompt-version.sh
  save …`) before any edit, and reconcile against the live agent first — **the live prompt can be
  ahead of the repo** (the team edits real job inventory directly on the console). Deploy is
  API-PATCH with read-back verification; never trust a Raya console GET (its read path is flaky and a
  console Save can wipe the live prompt).
- **No fix without a transcript.** We never edit a prompt off a report or a hunch — we pull the real
  call, confirm the bug, and understand the root cause first.
- **Push back before fixing.** Not every reported bug is a prompt bug. Wrong inputs, backend
  failures and pure runtime tool-adherence misses are named as such and escalated — we say "the
  prompt is fine, the inputs were wrong" out loud rather than editing to look responsive. More prose
  on a runtime-adherence miss makes it worse.
- **Test every variant independently — never extrapolate.** Every language, every direction, every
  bot is tested on its own. "It works in the master language, so the mirror is fine" is a
  recipe for disaster.
- **Access needs are a design constraint, never the topic.** If callers need slower pacing, longer
  silence tolerance or repetition on request, the bot's *behaviour* changes — the bot never raises,
  names or asks about anyone's disability or condition.

---

## Minimum to start (the "not enough info yet" case)

If the customer is short on time or doesn't have all the details, don't stall. We can begin with
just three things:

1. **What the bot does** (one or two sentences — domain, who it talks to, goal of a call).
2. **The prompt** (paste it, or a file path — even one language is enough to start).
3. **One test case** (a single scenario + what a good outcome looks like).

Plus the **project name**, which is one word and costs them nothing — it's what keeps their bot from
being filed as an exception. And if they arrived because something is broken, get **one issue record
with an id** (symptom + where + trigger, even with `call-ref: none yet`) — that's what turns a
complaint into something we can actually go test.

With those we can already file a starter intake summary, run `/prompt-analyser` on the prompt for a
read-only gap check, and design a first `/voice-test`. Note everything else as **TBD** and tell them
what each missing piece would let us add (deploy needs the Raya uuid; live testing needs the DID;
bug fixes need a real call uuid; a new language needs to know which language is the master).
Collect the rest whenever they're ready.

---

## Hand-off (where onboarding ends)

Once the intake summary is confirmed and *Step 2* has produced a verdict per issue-id, route by what
they actually need. The full picture of how these skills chain together is **`docs/WORKFLOW.md`** —
point a newcomer there rather than explaining the whole pipeline in chat.

- **New bot (Branch B)** → **`/register-bot`** (scaffolds the folder + prompt files + `CHANGELOG.md`,
  adds the project-scoped path-map entry, writes the `raya/agents.json` target(s) with the
  hand-copied uuids, and adds it to the regression fleet) → **`/prompt-analyser`** (read-only
  pre-flight audit against the learned bug patterns) → **`/generate-test-cases`** (scenarios →
  personas + the bot's own checklist, including a reproduction case per issue-id) →
  **`/voice-test`** (the first real graded calls).
- **Existing bot (Branch A)** → the in-repo grounded briefing (`raya/intake/<bot-id>.md` + its
  `raya/agents.json` entry + the bot's `CHANGELOG.md`, then **`/prompt-analyser`**), then
  **`/voice-test`** — or **`/bug-fix`** if their issues are already rows in the tracker sheet.
- **They want a language the bot doesn't speak yet** → **`/translate-prompt`** (spoken-idiom version
  with that language's own TTS/script conventions re-derived, plus its new Raya agent), then
  `/register-bot` for the new variant, `/generate-test-cases` for its personas, and `/voice-test`
  to grade it. Mirroring an *existing* change across languages is `/sync-check` + `/update-prompt`,
  not this.
- **Reported issues that reproduced** (`repro-confirmed`) → **`/update-prompt`** (or
  **`/port-feature`** if a sibling bot already carries the fix): snapshot → reconcile against live →
  surgical edit on the master → mirror to every other language → changelog citing the issue-id →
  analyser pattern → deploy → re-test all three tiers on every variant.
- **Issues that didn't** → hand back the classification, not a fix: `no-repro` (ask for the
  reproducing call uuid), `not-a-prompt-bug: data-input` (the inputs were wrong),
  `not-a-prompt-bug: backend` or `: runtime-adherence` (escalate for a platform fix).

Tell the customer, in one line, exactly what happens next and who does it — then stop. Onboarding's
job is done when the tuner has a filled, confirmed intake summary, a status on every issue-id, and a
clear first action.
