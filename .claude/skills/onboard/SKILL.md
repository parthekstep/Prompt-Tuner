---
name: onboard
description: Customer-facing intake for a NEW user/customer bringing a voice bot to the Prompt Tuner. Walks them, one friendly question at a time, through sharing everything needed to start improving and testing their bot — what the bot does, languages, the prompt(s), the platform (Raya) + agent uuids/DIDs, the tools/APIs it calls, their test cases + success criteria, and any known bugs. Produces a concrete intake summary the tuner can act on and hands off to /load-context and /voice-test. Use when someone new arrives, says "I have a bot I want to improve", "help me get started", "onboard my agent", or you don't yet know which bot they mean.
---

# Onboard — new-customer intake

Someone new has come to the **Prompt Tuner** with a voice bot. Your job here is to make them
feel welcome and collect — in plain language, **one question at a time** — everything we need
to start improving and testing their bot. You are the friendly front desk, not an interrogator.

**What the Prompt Tuner does for them (say this in your own warm words up front):**
we take their voice bot's prompt and (1) iterate on it from real feedback and bugs, (2) keep
its language versions in sync so a fix in one language always lands in the other, (3) deploy the
updated prompt to the live agent, and (4) **test the bot ourselves** by having a "tester" agent
role-play a caller, place a real call, and grade the transcript — so we catch problems before
their users do.

## How to run this (tone + pace)

- **One question at a time.** Ask, wait, acknowledge the answer, then ask the next. Never dump
  the whole list at once.
- **Plain, friendly, non-technical.** No jargon walls. If they don't know an answer, that's fine —
  note it as "TBD" and move on; we can start with less (see *Minimum to start*).
- **Say what happens with each answer** as you collect it (see *What each answer unlocks*), so they
  see the value of sharing it — but keep it to a sentence, don't lecture.
- **Do not touch any prompt file, `agents.json`, or the live agent during onboarding.** This skill
  only *gathers* and *files an intake summary*. Editing, registering, and deploying happen later
  through the proper skills. Onboarding is read-and-record only.

---

## Step 1 — Warm open + which path

Greet them, give the one-paragraph "what we do for you" above, then find out which situation
they're in with a single question: **"Is this one of the bots we already work on, or a new bot
you're bringing to us?"**

- If they name **KKB / DKB / Maya**, or anything already listed in `raya/agents.json` → **Branch A**.
- If it's a **new bot** → **Branch B**.

If unsure, glance at `raya/agents.json` (targets: KKB, DKB, Maya — Hindi/Kannada, inbound/outbound)
to see whether their bot is already a known deploy target.

---

## Branch A — a bot we already have

This is quick. We only need to pin down *which* target, then we can go straight to work.

Ask, one at a time:
1. **Which bot?** (KKB job-matching / DKB employer / Maya campus — or the name they use.)
2. **Which language?** (Hindi / Kannada — Maya is Hindi-only.)
3. **Inbound or outbound?** (the bot receives calls, or the bot places them.)

Then confirm the match against `raya/agents.json` — each target has an `id` (e.g. `kkb-hi-out`,
`dkb-kn-out`, `maya-hi-in`), its prompt `file`, and its `raya_agent_id` per environment. Read back
what you found: *"Great — that's `<id>`, prompt at `<file>`, live on Raya as `<raya_name>`."*

Confirm we can proceed straight to a grounded briefing and a test pass:
- **`/load-context`** for the grounded briefing (track MOC, latest decisions, tool contracts,
  linked paths), then
- **`/voice-test`** to run a first call and grade it, or **`/bug-fix`** if they arrived with a
  specific reported bug.

Still fill in a short intake summary (below) capturing anything new they told you (a fresh bug,
a new test scenario). Then hand off.

---

## Branch B — a new bot they're bringing

Collect the following **one item at a time**, in this order. After each answer, drop the
one-line "here's what that lets us do" note. Record answers into the intake summary as you go;
mark anything missing as **TBD** rather than blocking.

**(a) What the bot does.** What's the bot's job? Who does it talk to, and what's the goal of a
single call? (domain • audience • the outcome a good call reaches)
→ *Unlocks:* the bot's persona/audience, which test **checklist family** fits, and a new entry in
`../port-feature/reference/agent-schemas.md` so future edits know its shape.

**(b) Languages + source of truth.** Which languages does it speak? If more than one, **which
one is the master** that we edit first and mirror from?
→ *Unlocks:* the file map and the **sync rule** — we edit the master language, then mirror
language-agnostic logic verbatim and translate/adapt only the spoken lines.

**(c) The prompt(s).** Can you paste the conversation prompt, or give a file path? One per
language. Also: does the bot have a **memory** prompt (remembers the caller between calls) and/or
an **output** prompt (pulls structured results out of each call) — or just the conversation prompt?
→ *Unlocks:* where each file gets filed under our path-map convention (see *What each answer
unlocks*), and — if memory is on — the required memory-injection block in every conversation prompt.

**(d) The platform.** Does the bot run on **Raya** (our deploy + test platform)? If yes: the
agent **uuid(s)** (there may be separate ones for Hindi/Kannada and for inbound vs outbound), and
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

**(g) Known bugs / recent calls.** Anything misbehaving right now? If a recent real call shows it,
the call reference/uuid is gold — **we never fix a bug without seeing the actual call transcript.**
→ *Unlocks:* the first `/voice-test` reproduction and, if confirmed, a `/bug-fix` pass.

If they trail off or don't have much, that's fine — jump to *Minimum to start*.

---

## What each answer unlocks (the mechanics, grounded in this repo)

Tell the customer the relevant bits in plain terms; the detail here is for you.

- **Where the prompt gets filed — path-map convention.** Each agent lives in its own top-level
  folder with files named `<Bot> <Language>.md` for conversation, `<Bot> Memory.md` for memory,
  `<Bot> Output.md` for output. (Existing examples: `KKB/KKB Placeholder Hindi.md`,
  `DKB/DKB Kannada.md`, `Maya/Maya Hindi.md`, `KKB/KKB Memory.md`, `KKB/KKB Output.md`.) A new bot
  named e.g. *Chai* would get `Chai/Chai Hindi.md`, `Chai/Chai Kannada.md`, plus optional
  `Chai/Chai Memory.md` / `Chai/Chai Output.md`, and a fresh `Chai/CHANGELOG.md`. The canonical
  path map is in the repo-root `CLAUDE.md`; **update it there when a new bot is added.**
- **How it becomes a deploy target — `raya/agents.json`.** Each conversation prompt (per language,
  per direction) is one entry with: `id`, `file`, `agent`, `language`, `direction`,
  `kind: "conversation"`, `profile: "conversation"`, `expected_name_contains` (wrong-target guard),
  `raya_name`, `raya_agent_id: { prod, staging }`, and `deploy`. **The uuid is filled by hand from
  `scripts/raya_deploy.py list` — never inferred from the filename** (a real pitfall: "KKB
  Placeholder Inbound.md" is *Hindi*, not obvious from the name). Memory/output are separate
  entries with `kind`/`profile` `memory`/`output`. Actually writing these entries is a later step;
  onboarding just records the values so the entry can be created.
- **How a tester persona + checklist gets picked — `/voice-test`.** We stand up a **tester agent**
  (an inbound persona role-playing a caller), **trigger the bot under test to call it**, then grade
  both legs. **Every** bot is graded against the generic checklist
  `.claude/skills/voice-test/reference/checklists/generic.md`. If the bot matches a family we already
  have, we also use its bot-specific checklist (`.../checklists/{kkb,dkb,maya}.md`); a brand-new bot
  gets a new bot-specific checklist seeded from the success criteria in answer (f). Their scenarios
  become personas in `raya/personas/`.
- **What the customer gets back.** A **grounded briefing** on their bot (via `/load-context`) plus a
  **first test pass** (via `/voice-test`) graded against generic + bot-specific checklists, and a
  prioritized shortlist of fixes — each routed through `/update-prompt` (or `/port-feature` if it's a
  behavior we already built on a sibling bot).

---

## Produce the intake summary (the artifact)

The deliverable of `/onboard` is a filled **intake summary** the tuner can act on without re-asking.
Use the blank template in `reference/intake-template.md`. Fill every field you have; write **TBD**
for anything still missing (a TBD is a to-do, not a blocker).

- Show the filled summary to the customer and ask them to confirm/correct it.
- Offer to save it to **`raya/intake/<bot-id>.md`** (create the `raya/intake/` folder if needed) so
  the next skill picks up exactly where you left off. For an existing (Branch A) bot, use the
  existing target `id` as the filename.

The summary must capture, at minimum: what the bot does • languages + master • prompt file paths
(and whether memory/output exist) • platform + Raya uuid(s)/DID(s) • tools/APIs + fixed params •
test scenarios + success criteria • known bugs + any real call uuids • the proposed `agents.json`
target id(s) • and the immediate next step.

---

## Guardrails a newcomer must know (mention the relevant ones, don't recite all)

These are the house rules that keep a live bot from breaking. Surface them naturally as they
become relevant — e.g. mention sync when they say "two languages", mention transcripts when they
report a bug.

- **Surgical edits only.** We change the smallest thing the task needs and preserve everything else —
  spoken lines, variable names, tool names, payloads, section structure. No "cleanup" reformatting.
- **Language sync.** The master language is edited first; the change is mirrored to the other —
  language-agnostic logic copied verbatim, spoken lines translated/adapted (for KKB/DKB that's
  Hindi → Kannada). A fix that lands in one language but not its twin is a regression.
- **Instructions in English, spoken content in the language.** Every rule/heading/condition in a
  prompt is written in English; only the words the bot actually *speaks* are in Hindi/Kannada.
- **Bug fix ⇒ changelog + analyser.** Every edit appends to the bot's `CHANGELOG.md`; every *bug*
  fix also teaches `/prompt-analyser` to catch that failure class next time.
- **Snapshot before deploy.** We checkpoint the current stable prompt (rollback safety) before any
  edit, and reconcile against the live agent first — **the live prompt can be ahead of the repo**
  (the team edits real job inventory directly on the console). Deploy is API-PATCH only; never trust
  a Raya console GET (its read path is flaky and a console Save can wipe the live prompt).
- **No fix without a transcript.** We never edit a prompt off a report or a hunch — we pull the real
  call, confirm the bug, and understand the root cause first. Backend/API and pure tool-adherence
  misses aren't fixed with more prose; they're escalated.

---

## Minimum to start (the "not enough info yet" case)

If the customer is short on time or doesn't have all the details, don't stall. We can begin with
just three things:

1. **What the bot does** (one or two sentences — domain, who it talks to, goal of a call).
2. **The prompt** (paste it, or a file path — even one language is enough to start).
3. **One test case** (a single scenario + what a good outcome looks like).

With those we can already file a starter intake summary, run `/prompt-analyser` on the prompt for a
read-only gap check, and design a first `/voice-test`. Note everything else as **TBD** and tell them
what each missing piece would let us add (deploy needs the Raya uuid; live testing needs the DID;
bug fixes need a real call uuid). Collect the rest whenever they're ready.

---

## Hand-off (where onboarding ends)

Once the intake summary is confirmed:
- **Existing bot** → `/load-context` for the briefing, then `/voice-test` (or `/bug-fix` if they came
  with a reported bug).
- **New bot** → create the folder + files via `/update-prompt` (new-prompt path), register the
  target(s) in `raya/agents.json` and add it to the root `CLAUDE.md` path map, seed a bot-specific
  checklist + personas, then run the first `/voice-test`.

Tell the customer, in one line, exactly what happens next and who does it — then stop. Onboarding's
job is done when the tuner has a filled, confirmed intake summary and a clear first action.
