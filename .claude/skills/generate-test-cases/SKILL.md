---
name: generate-test-cases
description: Generate the custom test suite for ONE specific bot — derived from its own prompt flow, its tools, its real audience, the issues reported at onboarding, and the learned bug patterns — layered on top of the generic checklist every bot already runs. Emits a test manifest (raya/testcases/<bot-id>.md + .json), one tester persona per behavioural scenario (raya/personas/<lang>-<behavior>.md), and a bot-specific voice-test checklist with explicit pass/fail detection. Use right after /onboard or /register-bot, or when someone says "generate test cases", "what should we test on this bot", "build the test suite for Purple Dots", "seed the checklist and personas", "how do we prove issue pd-i02 is fixed", or a bot has no bot-specific checklist yet.
---

# Generate Test Cases

Build the **bot-specific** test suite for one bot. This skill is the bridge between `/onboard`
(which captured what the bot does and what is broken) and `/voice-test` (which places the calls and
grades them). It produces artifacts, not calls — the calls happen in `/voice-test`.

Works for any project, any bot, any number of languages. Read `<bot>`, `<project>`, `<lang>` as
placeholders — nothing here assumes a fixed set of bots or a fixed pair of languages.

**Read `reference/test-case-taxonomy.md` before you start.** It holds the six case families, the
assertion vocabulary every pass/fail rule must be written in, the priority/severity rubrics, the
bug-pattern applicability map, and the JSON schema. This SKILL.md is the procedure; that file is the
contract.

## What a run produces

| Artifact | Path | Purpose |
|---|---|---|
| Test manifest (human) | `raya/testcases/<bot-id>.md` | what a third person reads to know what this bot is tested for |
| Test manifest (machine) | `raya/testcases/<bot-id>.json` | consumed by `/voice-test` and, once config-driven, by the daily Tier-3 suite |
| Tester personas | `raya/personas/<lang>-<behavior>.md`, repros as `raya/personas/<lang>-repro-<issue-id>.md` | one per behavioural scenario, **per language** |
| Bot checklist | `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` | the bot-specific grading items, on top of `generic.md` |

Both manifests are generated from the same case list — never hand-write one and forget the other.

---

## Procedure

### 1. Gather the five derivation sources (read-only)

Nothing is invented. Collect, in this order, and note what is missing:

1. **The intake summary** — `raya/intake/<bot-id>.md` from `/onboard`: audience + access needs,
   languages + master, tools, scenarios + success criteria, and the **issue records** (`<bot-key>-i<NN>`).
2. **The registration** — `raya/agents.json` (target ids, files, languages, directions, uuids) is the
   **hard requirement**: if the bot is not there, stop and run `/register-bot` first — a manifest full of
   unresolvable target ids is worse than none. `raya/regression/fleet.json` (labels, role, backend,
   `required_tools`, `sync_group`) is used **when present**; it does not exist yet — the first
   `/register-bot` run creates it — so until then derive role/backend/label the way
   `raya/regression/static_regression.py`'s `discover_prompts()` does today, and note the gap in the
   report. Do **not** block on a missing `fleet.json`.
3. **The bot's own prompt** — the master-language conversation prompt. `grep -nE '^#{1,3} ' <file>`
   for the skeleton, then read the flow, fork, tool and exit sections properly.
4. **The live tool schemas** — the real `tools` on the live agent (Raya GET / the console). Prose and
   schema disagree more often than you would think, and a param the prose demands but the schema does
   not mark `required` is a latent bug (cf. `D25`, `D40`).
5. **The learned patterns** — `.claude/skills/prompt-analyser/reference/bug-patterns.md`, plus any
   `/prompt-analyser` report already run on this bot. Recommended: run `/prompt-analyser` first; its
   confirmed findings become the highest-value guard cases.

If `/prompt-analyser` has not been run, say so and offer to run it — it is read-only and cheap.

### 2. Derive the case list, family by family

Follow the recipes in `reference/test-case-taxonomy.md` §2–§7. Summary of the coverage obligation:

- **`F` Flow & branch** — one case per phase, **one per fork arm** (not per fork), one per terminal
  state (success, each decline gate, no-match, wrong person, voicemail, mid-flow hangup, tool-failure
  dead-end). Every heading in the prompt skeleton maps to a case id, or is listed in `coverage_gaps`.
- **`T` Tool contract** — per tool: **fires-when-it-should · does-NOT-fire-when-it-must-not · correct
  payload · each documented failure branch**. Enumerate required params, fixed params, exact enum
  strings, which upstream response field each identifier is bound from, and format contracts
  (country-code prefix, hyphenated UUID, Latin-only values). One assertion each.
- **`A` Audience behaviour** — who really calls and how they really behave: hesitant, interrupts,
  background noise, hands the phone to someone else, low literacy, code-mixes, rushes ahead, hostile,
  wrong number, silent. Keep the ones real for **this** audience; reuse an existing persona whenever
  one fits.
- **`R` Reported issues** — **1:1 with the intake issue records, no merging**, each tagged with its
  `<bot-key>-i<NN>` so "is `pd-i02` fixed?" is answerable by re-running exactly one case.
- **`G` Pattern guards** — walk the applicability map (taxonomy §7). Every pattern that this bot's
  shape makes possible gets a guard case citing its id; every pattern that does not apply gets a
  one-line reason in `patterns_not_applicable`. Silently dropping a pattern is not allowed.
- **`X` Accessibility** — the standing family, emitted for **every** bot (taxonomy §6): pacing,
  tolerance of long silences, repeat-on-request, never talking over the caller, reaching the goal for
  someone who cannot respond at default speed, never making a disability the subject of the call, and
  a companion answering on the caller's behalf.

### 3. Write pass/fail detection as observable evidence

Every case's `detection.pass_if` / `fail_if` uses the assertion vocabulary in taxonomy §8 —
`tool_fired(…)`, `tool_arg(…) matches …`, `spoken_once(…)`, `spoken_absent(…)`,
`turn_count_between(…) <= N`, `call_output.<field> == …`, `backend_record_count(…)`. Rules:

- **"Looks right" / "handles it gracefully" is not detection.** Rewrite it or delete the case.
- Any case involving a tool or an outcome carries at least one `tool_calls` or `call_output` predicate.
  Speech-only predicates are enough only for pure-speech cases (greeting, script, TTS, vocabulary,
  repetition).
- Name the **preconditions** as backend state, not prose ("a live record exists for the tester DID"),
  with `irreversible: true` where the state cannot be undone.

### 4. Set priority, run mode, severity and run order

- **Smoke ≤ 6 cases per variant** — happy path end-to-end, the primary write/action succeeding, the
  hard decline exit, the headline reported issue. These gate everything: no other case runs, and no fix
  is called done, until the smoke set passes.
- `core` = all fork arms + terminal states + tool checks + remaining reported issues.
  `extended` = pattern guards, audience long tail, accessibility long tail (weekly/rotation).
- **`run_mode`** — `static` for anything provable by reading the prompt or the tool schema (memory
  block, enum strings, fixed params, phone template, required section); `live` for behaviour, ASR/TTS
  and runtime adherence; `both` for a static pre-check a live call confirms. Static cases cost nothing
  and the daily suite can carry them — prefer them wherever the assertion allows, **but never for an
  `R` case, and never for any case cited as Tier-1 evidence**. Tier-1 fix verification is a real
  post-deploy transcript, so every `R` case is `live` or `both` (taxonomy §5).
- **Severity if failed** — `critical` (caller harmed/blocked, wrong data written, fabricated success,
  consent violated) / `major` / `minor`.
- **`run_order`** respects irreversibility: every "no record exists yet" case runs **before** any case
  that creates a record on the tester DID, or uses a second tester DID. Some backends have no delete
  route — a number that has a record can never be "new" again.
- Set `shares_call_with` where several cases can be graded from one transcript (same persona,
  language, direction, preconditions). This is what turns ~40 cases into ~15 live calls per variant.

**Why the caps are hard:** live calls are serial and rate-limited — call creation ~1 per ~13 s (429
with `retry_after` beyond that), bridging is intermittently flaky and needs a retry with a cooldown,
one tester agent holds one persona at a time (the tester receives **no** `agent_args`, so a scenario
cannot be selected per call), and the tester caps at 5 minutes. Budget **~10–14 completed live calls
per hour per tester**.

### 5. Set `variants` — every variant, tested independently

List in `variants` every target id the case must run on: each language, each direction, each backend
variant. Repo law: **each variant is tested independently — never extrapolate.** "It passed in the
master language, so the mirror is fine" is a recipe for disaster; ASR, TTS and runtime adherence differ
per language and a byte-identical mirrored edit can land differently. A case is `passed` only for the
variants that actually ran; the rest stay `untested`.

Two dependencies to flag rather than fudge:
- **New language ⇒ the tester needs it.** `scripts/raya_testcall.py` carries a `LANG` map with `hi`/`kn`
  only (`language_id` + `voice_id` harvested from live agents). A new Indic language needs its pair
  added — do not test a new language on the wrong voice.
- **Inbound bots cannot be harness-dialled** (the tester can only receive). Mark those variants
  `testable_live: false` and route them to post-deploy transcript review + static checks, marked
  **VERIFY-PENDING**.

### 6. Emit the personas

One persona per behavioural scenario, per language, at `raya/personas/<lang>-<behavior>.md`
(reproductions: `raya/personas/<lang>-repro-<issue-id>.md`). Match the existing house style exactly —
read two existing personas first:

- An HTML-comment header stating what the persona is, what backend state it needs, what it exercises,
  and which real call it is grounded in.
- `# YOU ARE A PERSONA — a real human …, NOT an assistant` and the never-break-character rules: never
  say it is an AI/bot/assistant, never try to help the caller, let the caller lead.
- A `## Language` section naming the language **and script**, instructing short colloquial phone
  sentences.
- A `## Who you are` block of fixed facts that must never be contradicted mid-call.
- `## How you behave` — the behavioural forcing function of the case (silence at a named gate,
  interruption, code-mixing, handing the phone over) and "answer only ONE thing at a time".
- `## Ending the call` — how the persona lets the call close.

**The persona's instructions are English; only the quoted lines the persona speaks are in the target
language.** Same law as the prompts. A persona whose rules are written in the target language is a bug.

Reuse before you mint: a near-duplicate persona costs a tester PATCH per call and buys nothing.

### 7. Emit the bot-specific checklist — do not duplicate `generic.md`

Write `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` in the existing checklist style:
a one-paragraph header naming the bot and the backend arg-shapes, then `## <section>` blocks ordered
**along the call flow**, each item a `- [ ]` line followed by an italic
`*Why / how to detect:*` line stating the observable evidence and citing the pattern id (`cf. D37`)
and, for repros, the tag `[repro <issue-id>]`.

**Generic vs custom split — the rule:** if the item would be true of *any* voice bot, it belongs in
`generic.md` and must **not** be restated here; cite it instead (`generic §3`). This file carries only
what is specific to **this** bot: its flow gates, its tool payloads and enums, its inventory/result-set
logic, its domain vocabulary, its reported-issue repros. Before writing, read `generic.md`'s 13
sections and de-duplicate against them; record which generic sections you are relying on in the
manifest's `coverage.generic_checklist_sections_relied_on`.

**Accessibility promotion (roadmap G8).** The durable accessibility items — pacing, silence tolerance,
repeat-on-request, never talking over the caller, working for a caller who cannot respond at default
speed, never making the disability the subject of the call — are **bot-agnostic** and belong in
`generic.md` as a new section so the whole fleet inherits them. Propose that promotion in
`promotions_proposed` and **ask the user before editing `generic.md`** — that file changes how every
bot in the fleet is graded, so it is never edited as a side effect of onboarding one bot. Keep only
genuinely bot-specific access items in the per-bot checklist.

### 8. Write the manifests

- `raya/testcases/<bot-id>.json` — exactly the schema in taxonomy §10 (`schema_version: 1`). Join to
  `raya/agents.json` / `raya/regression/fleet.json` on `target_id`; **never copy a fleet field** (label,
  blurb, backend, role) into the test manifest — one source of truth per fact.
- `raya/testcases/<bot-id>.md` — the same cases, readable: a header (bot, project, audience, variants,
  master language, generated date), the **smoke set** up front, then one table or block per family with
  id · title · source · persona · preconditions · expected · detection · severity · variants, then the
  coverage summary (`patterns_applied`, `patterns_not_applicable`, `coverage_gaps`) and the proposed
  promotions.
- Create `raya/testcases/` (and `raya/testcases/args/` for `agent_args` payload files) if absent.
- Validate: `python3 -c "import json;json.load(open('raya/testcases/<bot-id>.json'));print('json ok')"`.

### 9. Hand off to `/voice-test`

Give the exact commands for the first smoke case, using this bot's real values:

```bash
# load the persona onto the tester (swaps its prompt)
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<lang>-<behavior>.md
# match the tester's language + voice to the bot under test
python3 scripts/raya_testcall.py lang <tester_uuid> <lang>
# fire + poll to completion + dump the graded transcript
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> raya/testcases/args/<bot-id>-<shape>.json <tester_uuid> "<case-id>-<target-id>"
# read past calls/transcripts for any agent
python3 scripts/raya_call.py <bot_uuid>
```

Then grade against `generic.md` + `<bot-slug>.md`, and write each result back into the manifest's
per-case `status.<target-id>` (`result`, `last_run`, `call_uuid`).

### 10. Report

Report: paths written · case counts per family · the smoke set · patterns applied vs not-applicable
(with reasons) · coverage gaps · promotions proposed and awaiting approval · the live-call budget
estimate (cases × variants ÷ ~12 calls/hour) · the exact next command. State plainly which cases are
`untested` — which, on a fresh manifest, is all of them.

---

## Test before done (the manifest is not DONE until it has been run)

This skill writes no prompt prose and deploys nothing, so it needs no `CHANGELOG.md` entry and no
snapshot. But an untested manifest is a document, not a test suite:

- **A case that cannot fail is not a test.** Execute the **smoke set** at least once via `/voice-test`
  on each `testable_live` variant, confirm each case is runnable (persona loads, args are the right
  shape, preconditions hold) and that its detection rule actually discriminates. Fix any case whose
  assertion cannot be evaluated from the dumped transcript / `tool_calls` / `call_output`.
- Then record the real results in `status.<target-id>` and paste them into the report. Never describe a
  manifest as validated on the strength of a variant you did not run.
- The suite exists to serve the repo's **three testing tiers** (repo `CLAUDE.md` → "The three testing
  tiers"): **Tier 1** fix verification = re-run the `R` case for the issue-id; **Tier 2** blast-radius
  regression = re-run the `F`/`T` cases around the section, the shared agnostic logic, the mirrored
  sibling language/bot and the tool payload the fix touched; **Tier 3** daily standing check = the
  `run_mode: static|both` cases, once the suite is fleet-manifest-driven (roadmap G4/G7).
- **Test every variant independently — never extrapolate.** Where a variant genuinely cannot be
  harness-tested (inbound bots; telephony down), do the best available verification (post-deploy
  transcript review + static checks) and mark it **VERIFY-PENDING** — never "done".

---

## Guardrails

- **This skill generates test artifacts. It never edits a prompt, never deploys, and never fixes
  anything.** Confirmed findings route to `/update-prompt` (or `/port-feature` to carry a proven fix
  from a sibling bot). Runtime tool-adherence misses are usually better fixed with a **tool-schema
  lever** (a `required` param) than more prose — cf. `D25`/`D40`.
- **No case without a source.** Every case names one of the five sources, with a bug-pattern id or an
  issue-id where applicable. Invented coverage gets deleted in review.
- **No fix without a transcript** applies here too: an `R` case whose issue has no reproducing call is
  written `repro_status: "unconfirmed"`, and its job is to establish whether the bug is real. Do not
  pre-write a fix, and do not let an unconfirmed case justify a prompt edit.
- **Push back before fixing.** If the reported call's **input args** show the fault was data/user input
  (values in the wrong field, malformed args, mis-mapped campaign args) or backend (a 4xx with a
  well-formed id, bad inventory, region-specific endpoint behaviour), write the case as a **graceful-
  degradation guard** with `classification: "data-input"` / `"backend"`, and say out loud in the report
  that the prompt is fine and the inputs were wrong. Sometimes there is no bug.
- **Do not duplicate `generic.md`.** Cite it. And do not edit it without explicit approval — it grades
  every bot in the fleet.
- **Surgical edits only** where you touch an existing file (an existing persona, an existing
  checklist): smallest change, additive, preserve spoken lines, `${variables}`, tool names, payload
  field names and section structure. Never localize a `${variable}`, a tool name, or a fixed payload
  param — not in a case, not in a persona, not in a checklist item.
- **Instructions in English; only spoken lines in the target language.** Applies to personas and
  checklist items exactly as it applies to prompts.
- **One source of truth per fact.** Deploy identity lives in `raya/agents.json`; fleet labels/roles live
  in `raya/regression/fleet.json`; test coverage lives here. Join on the target id; never re-copy.
- **Case ids are permanent.** A retired case keeps its number with `result: "retired"` so historical run
  records, digest items and changelog references stay resolvable.
- If the bot is not registered in `raya/agents.json`, or the prompt file is not in the repo, stop and
  hand back to `/register-bot` — do not guess target ids. A missing `raya/regression/fleet.json` is
  **not** a blocker (it is created by the first `/register-bot` run): derive role/backend/label as
  `static_regression.py`'s `discover_prompts()` does and note the gap in the report.
