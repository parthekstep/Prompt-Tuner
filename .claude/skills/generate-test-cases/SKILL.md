---
name: generate-test-cases
description: Derive the complete test suite for ONE specific bot from its own prompt — enumerate the prompt's axes mechanically (sections, branch arms, tool contracts, enum values, bounded counters, conditional spoken lines, input-variable states, worked examples), compute the scenario count instead of inventing it, run the static example audit before any call is placed, and emit the manifest + personas + bot checklist with a printed coverage denominator so a thin suite is visible on sight. Use right after /onboard or /register-bot, or when someone says "generate test cases", "what should we test on this bot", "build the test suite for Purple Dots", "seed the checklist and personas", "how do we prove issue pd-i02 is fixed", "is our testing deep enough", or a bot has no bot-specific checklist yet.
---

# Generate Test Cases

Build the **bot-specific** test suite for one bot. This skill is the bridge between `/onboard`
(which captured what the bot does and what is broken) and `/voice-test` (which places the calls and
grades them). It produces artifacts, not calls — the calls happen in `/voice-test`.

Works for any project, any bot, any number of languages. Read `<bot>`, `<project>`, `<lang>` as
placeholders — nothing here assumes a fixed set of bots or a fixed pair of languages.

**Read `reference/test-case-taxonomy.md` before you start.** It holds the six case families, the
assertion vocabulary every pass/fail rule must be written in, the priority/severity rubrics, the
bug-pattern applicability map, and the JSON schema.

> **This SKILL.md overrides taxonomy §9's absolute case-count caps.** Any text that reads
> "`core` ~15–25" or implies a ~40-case suite is superseded by §4 below. Those numbers were a
> budget ceiling mistaken for a spec, and they are the single reason a 1,856-line prompt shipped
> with ~25 scenarios (10% of its derived set) and four defects that a human tester found in
> production. Case counts are **computed from the prompt**, never chosen.

---

## The first law: coverage is COMPUTED, not asserted

A suite is not "comprehensive" because it feels proportionate to the effort spent. It is
comprehensive when every obligation the prompt states has an assertion id, and the ones that do not
are named with a legitimate reason. So this skill does three things a prose recipe cannot:

1. **It measures the prompt** and prints the denominators (§1, §2). A reviewer divides and sees the
   ratio. A suite whose case count is within 20% of a previous bot's, on a prompt of materially
   different size, is evidence the derivation was skipped — say so in the report.
2. **It audits the prompt's own worked examples** before any call is placed (§3). This is the
   highest-yield pass in the skill and it costs zero calls.
3. **It reconciles the emitted manifest line-by-line against the axis enumeration** (§9). If the
   reconciliation does not close, the manifest is incomplete — not "gap-annotated".

**Refuse to emit a manifest** whose case count is not reconciled against §2, or whose
`coverage_gaps` exceed 10% of headings, or which lists any obligation as a gap with a reason
outside the enum in §6.

## What a run produces

| Artifact | Path | Purpose |
|---|---|---|
| Derivation ledger | `raya/testcases/<bot-id>.md` §0–§2 (in-document) | the measured axes, the counts, the formula, the coverage ratio |
| Test manifest (human) | `raya/testcases/<bot-id>.md` | what a third person reads to know what this bot is tested for |
| Test manifest (machine) | `raya/testcases/<bot-id>.json` | consumed by `/voice-test` and by the daily Tier-3 suite |
| Static audit findings | `raya/testcases/<bot-id>-static.md` | the §3 example audit + contradiction blockers, routed to `/update-prompt` |
| Not-testable register | `raya/testcases/<bot-id>.md` §NT + `untestable[]` in JSON | every obligation the harness cannot reach, **each with its substitute check** |
| `agent_args` fixtures | `raya/testcases/args/<bot-id>-<state>.json` | one per input-variable equivalence class |
| Tester personas | `raya/personas/<lang>-<behavior>.md`, repros as `raya/personas/<lang>-repro-<issue-id>.md` | one per behavioural scenario, **per language** |
| Bot checklist | `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` | the bot-specific grading items, on top of `generic.md` |

Both manifests are generated from the same case list — never hand-write one and forget the other.

---

## Procedure

### 0. Gather the derivation sources (read-only)

Nothing is invented. Collect, in this order, and note what is missing:

1. **The intake summary** — `raya/intake/<bot-id>.md` from `/onboard`: audience + access needs,
   languages + master, tools, scenarios + success criteria, and the **issue records** (`<bot-key>-i<NN>`).
2. **The registration** — `raya/agents.json` (target ids, files, languages, directions, uuids) is the
   **hard requirement**: if the bot is not there, stop and run `/register-bot` first — a manifest full of
   unresolvable target ids is worse than none. `raya/regression/fleet.json` (labels, role, backend,
   `required_tools`, `sync_group`) is used when present.
3. **The bot's own prompt** — the master-language conversation prompt, read **in full**. Skimming the
   headings is how whole sections go unexercised.
4. **The live tool schemas** — the real `tools` on the live agent (Raya GET / the console). Prose and
   schema disagree more often than you would think, and a param the prose demands but the schema does
   not mark `required` is a latent bug (cf. `D25`, `D40`).
5. **The learned patterns** — `.claude/skills/prompt-analyser/reference/bug-patterns.md` and
   `reference/section-checklists.md`, plus any `/prompt-analyser` report on this bot. Run
   `/prompt-analyser` first if it has not been run — it is read-only and cheap.
6. **Real call history + real `agent_args`** — `python3 scripts/raya_call.py <bot_uuid> 20`. This is
   where the error codes the backend *actually* returns come from, and where malformed-input shapes
   (truncation, sentinels, misplaced fields) come from. Both are derivation sources, not anecdotes.

### 1. Measure the prompt — print the complexity vector

One shell pass. Every number goes in the manifest header, beside the case count.

```bash
P="<path to master prompt>"
wc -l "$P"                                                        # lines
grep -cE '^#{1,4} ' "$P"                                          # headings
grep -oE '"[^"]{3,}"' "$P" | sort -u | wc -l                      # distinct quoted strings
grep -oE '"[^"]{15,}"' "$P" | grep -P '[^\x00-\x7F]' | sort -u | wc -l   # distinct spoken utterances
grep -oiE 'never|must not|MANDATORY|forbidden|do not' "$P" | wc -l       # prohibition density
grep -oiE 'exactly ONCE|only ONCE|say once|once per call|at most (one|two|three)|HARD CAP|only ONE|exactly ONE' "$P" | wc -l
grep -cE '^[-*>#]?[[:space:]]*\**(If|When|On|Case|Path|Row|Otherwise|Caller) ' "$P"   # branch openers
for t in <tool names>; do echo -n "$t "; grep -c "$t" "$P"; done   # tool mention density
```

`complexity_vector = {lines, headings, quoted_strings, spoken_utterances, prohibitions, counters,
branch_openers, tools, enum_values, input_states, examples}`. Nothing downstream may be sized
independently of it. A prompt three times longer than the last one gets three times the enumeration
work — that is the whole point.

### 2. Enumerate the eight axes mechanically — each with a count

Each axis is produced by a command plus a walk, not by judgement. **Print every count.** These are
the denominators; the case list is reconciled against them in §9.

**Axis 1 — Named sections.** Every `#`/`##`/`###`. Classify each as
`FLOW` (a call can be in this state) · `ASSERT` (provable by reading the prompt or the tool schema:
TTS rules, script rules, canonical spellings, prohibited language, payload rules) ·
`PROSE` (tone, internal state models, dignity checks — non-behavioural). **`PROSE` is the only
bucket that may be omitted, and it is listed with its reason, never dropped silently.**

**Axis 2 — Branch arms.** One case per **ARM**, never per fork. Walk every if/else, every branch on
an input variable, every branch on a tool result, every terminal state, every row of every lookup
table. Record the arm count per section. This is normally the largest axis and the one prose
recipes undercount by an order of magnitude.

**Axis 3 — Tool contracts × sub-checks × error codes.** Per tool, four sub-checks minimum:
**fires-when-it-should · does NOT fire when it must not · correct payload · each failure branch**.
Enumerate required params, fixed params that must never change, exact enum strings, which upstream
response field each identifier is bound from, and format contracts (country-code prefix, hyphenated
UUID, Latin-only values). Then enumerate **every error code** named in the prompt or observed in
real call history, and **rank them by provisioning cost** — a code reachable by repeating a prior
action (`ACTION_LIMIT_REACHED`), by pointing at a draft record (`PROFILE_NOT_LIVE`), or by using a
stale id (`TARGET_ITEM_NOT_FOUND`) is among the **cheapest** arms in the whole suite and belongs in
P0, not the long tail. A forbidden tool gets a `never(tool)` assertion.

**Axis 4 — Enum VALUES, not enum fields.** One assertion **per value**. A 7-value enum is 7
assertions, not 1 — especially when each value routes to a different conditional follow-up with its
own sub-enum. Most are `static` ("the prompt's mapping table lists this value byte-exact"); the ones
that need a live call to prove the mapping fires get one persona per branch, batched.

**Axis 5 — Bounded counters.** Grep
`once|only ONE|exactly ONE|at most|HARD CAP|never a second|up to`, dedupe to distinct counters, and
emit one assertion per counter: `spoken_once(<line>)`, `turn_count_between(...) <= N`, or
`tool_fired(<tool>, count=1)`. Do **not** "fold into the case whose path crosses the gate" — that is
how a question asked twice in consecutive turns ships. Most are static or free-rider live, so the
marginal call cost is near zero and the yield is high: doubled questions, doubled bridge lines,
doubled promises and blown caps are the highest-frequency historical bug class in this repo.

**Axis 6 — Conditional spoken lines.** Extract every quoted string. Short banned tokens become
`spoken_absent(...)` static assertions. Full utterances each need `spoken_once`, or
`spoken_contains ... at/before/after <gate>`, or `spoken_absent` when the path is not taken. Build a
**spoken-line registry** (key → prompt line number → anchor substring) in the manifest; every
assertion cites a key.

> **Anchor rule.** A grep anchor must be ≥30 chars or mid-line-distinctive. A mandated line and an
> example's substitute wording routinely share their first 20 characters — a short anchor reports a
> violated rule as satisfied.

**Axis 7 — Input-variable STATES, not presence.** Presence/absence is not an axis; states are.
Enumerate, per variable, every equivalence class the prompt itself names — blank, missing, an
unsubstituted `${...}` token, each sentinel string (`"Any"`, `"NA"`, `"None"`, `"null"`, `"-"`,
`"Not Available"`), a coarser value than expected (state only, pincode only), garbled, campaign
metadata, malformed JSON, truncated payload (cf. `D42`), and each shape of the read-tool's response
(empty · id null · one live · one draft · live-not-first · multiple · error). Each state becomes an
**`agent_args` fixture** in `raya/testcases/args/`, not a new persona — args-only cases are the
cheapest live cases there are.

**Axis 8 — Worked examples.** See §3. `examples × mandatory_steps + examples × payload_rules`
static assertions.

### 3. The static example audit — MANDATORY, before any call (analyser D50)

**The prompt's own sample conversations are a derivation source and a defect source.** The
catalogued root cause of repeated fix failures is that the examples demonstrate the violation the
rules forbid; every prose fix then competes with a live counter-demonstration. No test that ignores
the examples can find this, and prose fixes for it do not stick.

Run this **before** a single call is placed — a prompt whose examples contradict its rules will fail
the live test for reasons the transcript cannot explain.

- **E0.** Locate the example section. Count the examples.
- **E1.** Build the **mandatory-step list** from the rules: every step the prompt says must happen,
  in its mandated turn position, with its mandated wording (audio check · disclosure position ·
  silent lookup · each gate as its own turn · each mandated spoken format · each consent line · the
  read-back · the closing offer · the goodbye).
- **E2.** For **each (mandatory step × example)**: assert the example demonstrates it, or carries an
  explicit in-example annotation saying why it legitimately does not. Emit
  `static_check{target: prompt, assert: contains_verbatim|absent, scope: example_N}`.
  **Report as a count** — "N of M examples do X" — because the count is the finding.
- **E3.** Build the **payload-rule list** (location format, script of payload values, byte-exact
  enums, identifier formats, "a third party's value is never the caller's value"). For **each
  (payload rule × example)**: assert no example violates it.
- **E4. Contradiction pre-pass.** For each mandated spoken line, grep its distinctive tokens against
  the prohibition lists. For each H1, check for a verbatim duplicate heading with a different body.
  For each example stage direction, check the behaviour it names still exists in the rules.
- **E5. Route every failure to `/update-prompt` as an EXAMPLE edit** (or a rule deletion) — never as
  more prose. "Edit the demonstrations, not the prose."

**Contradictions are BLOCKERS, not test cases.** A case written against either side of a
contradiction produces a random verdict, and re-running it produces a different one — which is how
a fix "passes" one day and regresses the next with no edit in between. **Do not generate live cases
for a section that contradicts itself**; emit the blocker, hand it to `/update-prompt`, and say in
the report that those arms are un-derivable until it is resolved.

Write the whole audit to `raya/testcases/<bot-id>-static.md` with per-assertion counts.

### 4. Compute the two ledgers

Two ledgers, never one number. Assertions size the **grader**; scenarios size the **calls**.

**(A) Assertion ledger — every atomic obligation.**

```
A = flow_sections + branch_arms + tool_checks + enum_values + counters
    + conditional_lines + input_states + example_assertions
```

Split `A` by `run_mode`: **STATIC** (0 calls: banned-token absences, enum values, example
assertions, format/structural contracts, structural counters) and **LIVE-BEARING** (the remainder).
On a long prompt the static half is typically the majority — and it is free.

**(B) Scenario ledger — how many CALLS the live subset needs.** Not the cross-product. The full
cross-product of the independent state dimensions runs to five figures; that is not the target. The
suite is a **covering array**:

```
S_lang = ceil(FORCING_arms / arms_forceable_per_call)      # 1-wise: every arm at least once
       + Σ pair_scenarios over the named interacting pairs # 2-wise: only where state carries
       + |X accessibility family|
       + |R reported issues|
```

- Partition the arms into **FREE-RIDER** (observed on whatever call runs — greeting shape,
  disclosure position, TTS, canonical spellings, banned lines, one-question-per-turn, closing) and
  **FORCING** (needs a specific persona behaviour or a specific precondition). Free-riders cost zero
  extra calls; grade them on every call.
- `arms_forceable_per_call` ≈ **4** — a single persona can force about four distinct branch choices
  on one path before the path diverges. Use 4 unless you can justify otherwise.
- **Interacting pairs** are the only place 2-wise coverage is required: wherever state is **written
  in one step and read in another**. Derive them from the prompt and **enumerate them in the
  manifest** — typical families: input-state × downstream value-source walk · record-state × consent
  gate · action-outcome × closing-offer position · known-field lock × later gathering phase ·
  result-set shape × no-match gate · memory-state × opening/lookup separation · placeholder value ×
  confirmation · second-action-in-one-call × field re-ask lock. **These pairs are where the
  expensive defects live** — a defect reachable only by combining two axes is invisible to a suite
  built of single-axis cases.
- **Variant multiplier.** `S_total = Σ over variants of S_lang`, computed per variant, never
  extrapolated. The shared-agnostic core is usually ~80% common, so a sibling variant costs roughly
  `0.2 × S_lang + universal_invariants` — but it is never zero. Repo law.

**Print the ratio.** `scenarios_run / S_lang` and `assertions_exercised / A` go on the front page of
every report. That ratio is the answer to "is our testing deep enough" — a number, not an opinion.

### 5. Write pass/fail detection as observable evidence — both sides

Every case's `detection.pass_if` / `fail_if` uses the assertion vocabulary in taxonomy §8 —
`tool_fired(…)`, `tool_arg(…) matches …`, `spoken_once(…)`, `spoken_absent(…)`,
`turn_count_between(…) <= N`, `call_output.<field> == …`, `backend_record_count(…)`.

- **`fail_if` is MANDATORY**, and where the wrong output is known it must name the **literal wrong
  string or payload value** — the banned line, the forbidden field value, the doubled question.
  Grading is a two-sided test. A grader who knows only what *should* happen scores a call "pass"
  when the mandated line appears and misses that a forbidden line appeared alongside it — which is
  exactly how a failure line asserting a false cause survived: the failure *was* acknowledged, and
  the wording was the defect.
- **For every bug ever fixed on this bot, add the pre-fix output verbatim as a `fail_if`** on the
  corresponding `R` case. That is the D50 grep, encoded and permanent.
- **"Looks right" / "handles it gracefully" is not detection.** Rewrite it or delete the case. An
  item that cannot be written mechanically is not a grading item — it goes to the checklist's
  observations block (`/voice-test` §Observations), which can never produce PASS or FAIL.
- Any case involving a tool or an outcome carries at least one `tool_calls` or `call_output`
  predicate. Speech-only predicates suffice only for pure-speech cases.
- Name **preconditions as backend state**, not prose ("a live record exists for the tester DID"),
  with `irreversible: true` where the state cannot be undone.
- **Each case names its forcing gate(s)** — see §7's sharing rule.

### 6. The NOT-TESTABLE-BY-VOICE register — an alternative check per item, always

A scenario that cannot be executed is not a scenario. But an obligation the harness cannot reach is
**not** allowed to vanish: it gets an id, a reason from the enum, and a **substitute check**.

`coverage_gaps[].why` is restricted to **exactly** these reasons; anything else is a missing case,
not a gap:

| reason | means | required companion field |
|---|---|---|
| `not-testable-by-harness` | a named platform limit blocks it | `harness_limit` + `substitute` |
| `non-behavioural-prose` | Axis-1 `PROSE` bucket | — |
| `deferred-P2` | real, scheduled, not yet run | `run_order` |

`substitute` must be one of: **`static_check`** (prove it by reading the prompt/schema) ·
**`production_detector`** (a `raya/regression/` script over real traffic — name the script, or write
it) · **`human_call`** (a person dials it; say who and when) · **`platform_ask`** (an escalation with
what is being asked for). **A blocked obligation with no substitute is an open gap with its own id,
reported on the front page — never omitted.**

The standing harness limits that populate this register (verify each against
`/voice-test` → "Platform reality" before citing):

- **ASR-garble rungs are not voice-testable.** A TTS tester cannot mumble: asked to be
  unintelligible it either speaks clearly or goes silent. → `static_check` + `human_call`.
- **Platform-injected inputs are not settable per call** (e.g. `contact_memory` when memory is
  enabled — it is not in `agent_args`). → `production_detector`.
- **Lookup identity cannot be selected.** The platform overrides `contact_phone` with the dialled
  number, so every harness call uses the tester DID and returns that DID's actual current record.
  → provision by **ordering** (all "no record exists" cases first, `irreversible: true`), or a second
  tester DID, else `production_detector`.
- **Backends without a delete route** make "new caller" a one-shot state, permanently.
- **Single-use action pairs** — each (record, target) pair can be actioned once; a repeat returns the
  limit error. This is a *provisioning gift* for the error arm and a *blocker* for the success arm.
- **Truncated/corrupt campaign payloads** arrive from the campaign layer, not from `agent_args`.
- **Inbound variants cannot be harness-dialled** (the tester can only receive). Mark
  `testable_live: false`, route to post-deploy transcript review + static checks, mark
  **VERIFY-PENDING**.
- **Instance-scoped target ids** — a stale id yields a not-found error and looks like a bot bug.
  Fixtures must carry ids valid on that variant's instance.

### 7. Tier the suite to real harness throughput

Throughput ground truth: calls are serial per tester; creation is rate-limited (~1 per ~13 s, then
429 with `retry_after`); bridging fails on a large fraction of attempts and needs a retry with a
cooldown; one tester holds one persona at a time; the tester caps at 5 minutes. Budget
**~10–14 completed live calls per hour per tester.**

| Tier | Size | Contents | Gate |
|---|---|---|---|
| **Tier 0 — STATIC** | all STATIC assertions, **0 calls**, minutes | the §3 example audit · enum values byte-exact · banned-string absences · format/structural contracts · structural counters · the contradiction pre-pass | **Blocks live testing and blocks deploy.** Runs first. |
| **P0 — SMOKE** | **≤ 6 calls per variant** | **risk-derived, not shape-derived**: the end-to-end happy path, **plus one case per interacting pair that has EVER produced a defect on this bot family**, plus every open `R` case, plus the cheapest error arms from Axis 3 | **All must pass before any other case runs.** |
| **P1 — CORE** | one sitting (~2–2.5 h) | the interacting-pair scenarios, every terminal state, every tool contract | repo **Tier-2 blast radius** |
| **P2 — EXTENDED** | weekly rotation, ordered by `run_order` | the remaining 1-wise forcing arms, the audience long tail, the `X` accessibility family | — |
| **P3 — NOT TESTABLE** | enumerated, never omitted | §6 register, each with its substitute | reported, marked VERIFY-PENDING |

**Why smoke is risk-derived.** A smoke set of four single-axis shapes (happy path · primary write ·
hard decline · headline issue) structurally cannot cover an interaction between two axes, and it
passes green on a bot carrying production defects. Keep the ≤6 cap by **rotating** pairs across
runs, and enumerate the pair list in the manifest so the rotation is visible.

**Make the number tractable instead of shrinking the suite to fit the clock:**

- Tier 0 removes the whole static half from the live budget, for free.
- Free-rider arms are graded off calls that were going to happen anyway.
- **Call sharing, gated on two things, not one.** Set `shares_call_with` only where cases share
  persona, language, direction **and preconditions** — *and* their **persona forcing functions are
  compatible at every gate the path crosses**. Two cases may share a persona and preconditions yet
  need the caller to do opposite things at the same gate (decline the location vs name one; answer
  the doubts question "no" vs ask a real question). Marked as sharing, one of them is not actually
  exercised and the manifest records both as passed — a false green on top of a thin suite. **Each
  case names its forcing gate(s); validate that no two shared cases name the same gate with
  different required behaviour.**
- **Fan out.** K tester agents (each its own inbound DID + persona) turn N serial calls into ~N/K
  wall-clock. That is the correct fix for the budget — **not a smaller suite.**
- **Profile mutation is a scheduling constraint, not a coverage constraint.** Sort by `run_order`,
  snapshot the tester's backend state between tiers, and re-verify the entry state before each pair
  case (`/voice-test` → fixture protocol).

`run_mode`: `static` for anything provable by reading the prompt or the tool schema; `live` for
behaviour, ASR/TTS and runtime adherence; `both` for a static pre-check a live call confirms.
**Static is first-class and runs FIRST** — but **never** as the sole evidence for an `R` case and
never for anything cited as Tier-1 evidence. Static opens a finding; a post-deploy transcript closes
it.

### 8. Set `variants` — every variant, tested independently

List in `variants` every target id the case must run on: each language, each direction, each backend
variant. Repo law: **each variant is tested independently — never extrapolate.** "It passed in the
master language, so the mirror is fine" is a recipe for disaster; ASR, TTS and runtime adherence
differ per language and a byte-identical mirrored edit can land differently. A case is `passed` only
for the variants that actually ran; the rest stay `untested`.

Two dependencies to flag rather than fudge:
- **New language ⇒ the tester needs it.** `scripts/raya_testcall.py` carries a `LANG` map
  (`language_id` + `voice_id` harvested from live agents). A new Indic language needs its pair added
  — do not test a new language on the wrong voice.
- **Inbound bots cannot be harness-dialled** → §6 register.

### 9. Reconcile, then emit the manifests

**The acceptance rule.** A manifest is complete only when:

- every Axis-1 section names a case id or is in the `PROSE` bucket with its reason;
- **every branch arm** names a case id or a §6 reason;
- **every bounded counter** has an assertion;
- **every enum value** has an assertion;
- **every input-variable state** has an args fixture or a §6 reason;
- **every example assertion** from §3 is evaluated;
- every reported issue is 1:1 with an `R` case (**no merging**), tagged with its `<bot-key>-i<NN>`;
- every applicable learned pattern has a `G` guard case citing its id, and every non-applicable one
  has a one-line reason in `patterns_not_applicable`.

Then write:

- `raya/testcases/<bot-id>.json` — the schema in taxonomy §10 (`schema_version: 1`), plus
  `complexity_vector`, `axis_counts`, `assertion_ledger`, `scenario_ledger`, `interacting_pairs`,
  `untestable[]` (with `harness_limit` + `substitute`), `spoken_line_registry`. Join to
  `raya/agents.json` / `raya/regression/fleet.json` on `target_id`; **never copy a fleet field**
  (label, blurb, backend, role) into the test manifest — one source of truth per fact.
- `raya/testcases/<bot-id>.md` — same cases, readable. **§0 the complexity vector · §1 the axis
  counts · §2 the two ledgers and the coverage ratio** — then the P0 set up front, then one table
  per family with id · title · source · persona · preconditions · forcing gate · pass assertion ·
  **FAIL SIGNAL** · severity · variants, then §NT the not-testable register, then the coverage
  summary (`patterns_applied`, `patterns_not_applicable`, `coverage_gaps`) and proposed promotions.
- `raya/testcases/<bot-id>-static.md` — the §3 audit with counts and the contradiction blockers.
- `raya/testcases/args/<bot-id>-<state>.json` — one fixture per Axis-7 equivalence class, with
  target ids valid on that variant's instance.
- Create `raya/testcases/` and `raya/testcases/args/` if absent.
- Validate: `python3 -c "import json;json.load(open('raya/testcases/<bot-id>.json'));print('json ok')"`.

**The manifest is the gate, not the output.** `/voice-test` refuses to grade a bot with no
`raya/testcases/<bot-id>.json`, and reads the P0 subset straight out of it. Where a bot already has
an ungraded prose scenario catalogue, **migrate it in** as cases (they are real, grounded scenarios)
and derive the remainder from the axes — do not start from zero and do not leave two sources.

### 10. Emit the personas

One persona per behavioural scenario, per language, at `raya/personas/<lang>-<behavior>.md`
(reproductions: `raya/personas/<lang>-repro-<issue-id>.md`). Match the existing house style exactly —
read two existing personas first:

- An HTML-comment header stating what the persona is, what backend state it needs, what it
  exercises, **which forcing gate(s) it drives**, and which real call it is grounded in.
- `# YOU ARE A PERSONA — a real human …, NOT an assistant` and the never-break-character rules:
  never say it is an AI/bot/assistant, never try to help the caller, let the caller lead.
- A `## Language` section naming the language **and script**, instructing short colloquial phone
  sentences.
- A `## Who you are` block of fixed facts that must never be contradicted mid-call.
- `## How you behave` — the behavioural forcing function of the case (silence at a named gate,
  interruption, code-mixing, handing the phone over, refusing at every rung) and "answer only ONE
  thing at a time".
- `## Ending the call` — how the persona lets the call close.

**The persona's instructions are English; only the quoted lines the persona speaks are in the target
language.** Same law as the prompts. A persona whose rules are written in the target language is a bug.

Never write a persona that requires mumbling or unintelligible speech — TTS cannot do it. That arm
belongs in §6.

Reuse before you mint: a near-duplicate persona costs a tester PATCH per call and buys nothing.

### 11. Emit the bot-specific checklist — do not duplicate `generic.md`

Write `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` in the existing checklist style:
a one-paragraph header naming the bot and the backend arg-shapes, then `## <section>` blocks ordered
**along the call flow**, each item a `- [ ]` line followed by an italic `*Why / how to detect:*` line
stating the observable evidence and citing the pattern id (`cf. D37`) and, for repros, the tag
`[repro <issue-id>]`.

Additional obligations, from the grader contract in `/voice-test`:

- **Every item carries a stable id** — `<bot>.<section>.<n>` — because a result that cannot be cited
  cannot be tracked across runs.
- **Every prohibition item declares its `scope_turns`** (`intro_turn`, `acknowledgement_lines`,
  `failure_turn`, `phase2_turns`, `whole_call`). The default is **not** `whole_call`. A scoped
  prohibition graded globally flags the very boilerplate the bot is required to say.
- **Cross-script comparisons are typed** `compare: cross_script` so the grader routes them through
  transliteration instead of returning a false clean.
- **Unfalsifiable items go to an `## Observations (not graded)` block**, never as `- [ ]` items.
  Honest observation beats a fake PASS.
- Emit `raya/testcases/<bot-id>/required-lines.json` — every spoken line a rule marks **mandatory**,
  extracted from the prompt. It drives both the positive assertions and the prohibition mask, so a
  token cannot be simultaneously required and banned without the conflict showing up as a build
  error. Regenerate on every prompt change.

**Generic vs custom split — the rule:** if the item would be true of *any* voice bot, it belongs in
`generic.md` and must **not** be restated here; cite it instead (`generic §3`). This file carries only
what is specific to **this** bot: its flow gates, its tool payloads and enums, its
inventory/result-set logic, its domain vocabulary, its reported-issue repros. Read `generic.md`
first and de-duplicate; record which generic sections you rely on in
`coverage.generic_checklist_sections_relied_on`.

**Accessibility promotion (roadmap G8).** The durable accessibility items — pacing, silence
tolerance, repeat-on-request, never talking over the caller, working for a caller who cannot respond
at default speed, never making the disability the subject of the call — are **bot-agnostic** and
belong in `generic.md` so the whole fleet inherits them. Propose that in `promotions_proposed` and
**ask the user before editing `generic.md`** — that file changes how every bot in the fleet is
graded, so it is never edited as a side effect of onboarding one bot.

### 12. Hand off to `/voice-test`

Give the exact commands for the first P0 case, with this bot's real values:

```bash
# Tier 0 FIRST — static gate, zero calls. Blocks the live run.
#   (the §3 audit + banned-token/enum/counter greps; see raya/testcases/<bot-id>-static.md)
python3 raya/regression/static_regression.py            # fleet-wide static suite

# load the persona onto the tester (swaps its prompt)
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<lang>-<behavior>.md
# match the tester's language + voice to the bot under test
python3 scripts/raya_testcall.py lang <tester_uuid> <lang>
# fire + poll + dump the RAW transcript (grading is a separate, mandatory step)
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> raya/testcases/args/<bot-id>-<state>.json <tester_uuid> "<case-id>-<target-id>"
# read past calls/transcripts (full tool arguments) for any agent
python3 scripts/raya_call.py <bot_uuid>
```

Then grade against `generic.md` + `<bot-slug>.md` **under the `/voice-test` grader contract**, and
write each result into the manifest's per-case `status.<target-id>` (`result`, `last_run`,
`call_uuid`, `evidence`).

### 13. Report

Front page, in this order:

1. **The coverage ratio** — `scenarios_derived` vs `scenarios_run`, `assertions_total` vs
   `assertions_exercised`, and `NOT_EXERCISED` with its denominator. A green report over a low
   coverage ratio is itself the defect; it must be impossible to produce one without saying so.
2. The complexity vector and the eight axis counts.
3. The §3 static audit result, as counts, and every contradiction blocker routed to `/update-prompt`.
4. Paths written · case counts per family · the P0 set · the interacting-pair list.
5. Patterns applied vs not-applicable (with reasons) · `coverage_gaps` **per reason, with counts** ·
   the §6 register with each substitute.
6. The live-call budget estimate (`scenarios × variants ÷ ~12 calls/hour`) and the fan-out needed to
   fit it.
7. Promotions proposed and awaiting approval · the exact next command.
8. Which cases are `untested` — which, on a fresh manifest, is all of them.

---

## Test before done (the manifest is not DONE until it has been run)

This skill writes no prompt prose and deploys nothing, so it needs no `CHANGELOG.md` entry and no
snapshot. But an untested manifest is a document, not a test suite:

- **A case that cannot fail is not a test.** Execute the **P0 set** at least once via `/voice-test`
  on each `testable_live` variant, confirm each case is runnable (persona loads, args are the right
  shape, preconditions hold) and that its detection rule actually discriminates. Fix any case whose
  assertion cannot be evaluated from the call JSON / `tool_calls` / `call_output`.
- Then record the real results in `status.<target-id>` and paste them into the report. Never describe
  a manifest as validated on the strength of a variant you did not run.
- The suite serves the repo's **three testing tiers** (root `CLAUDE.md`): **Tier 1** fix verification
  = re-run the `R` case for the issue-id; **Tier 2** blast-radius regression = re-run the `F`/`T`
  cases around the section, the shared agnostic logic, the mirrored sibling variant and the tool
  payload the fix touched; **Tier 3** daily standing check = the `static|both` cases plus the
  production detectors. Note honestly that bot-specific static checks do not run in the daily job
  yet (roadmap G4/G7) — until they do, Tier 0 is a manual/CI grep pass and must be **labelled as
  such** in the report.
- **Test every variant independently — never extrapolate.** Where a variant genuinely cannot be
  harness-tested, do the best available verification and mark it **VERIFY-PENDING** — never "done".

---

## Guardrails

- **This skill generates test artifacts. It never edits a prompt, never deploys, and never fixes
  anything.** Confirmed findings route to `/update-prompt` (or `/port-feature` to carry a proven fix
  from a sibling bot). Runtime tool-adherence misses are usually better fixed with a **tool-schema
  lever** (a `required` param) than more prose — cf. `D25`/`D40`.
- **No case without a source.** Every case names one of the six sources, with a bug-pattern id or an
  issue-id where applicable. Invented coverage gets deleted in review.
- **No fix without a transcript** applies here too: an `R` case whose issue has no reproducing call
  is written `repro_status: "unconfirmed"`, and its job is to establish whether the bug is real. Do
  not pre-write a fix, and do not let an unconfirmed case justify a prompt edit.
- **Push back before fixing.** If the reported call's **input args** show the fault was data/user
  input (values in the wrong field, malformed args, mis-mapped campaign args) or backend (a 4xx with
  a well-formed id, bad inventory, region-specific endpoint behaviour), write the case as a
  **graceful-degradation guard** with `classification: "data-input"` / `"backend"`, and say out loud
  in the report that the prompt is fine and the inputs were wrong. Sometimes there is no bug.
- **Do not duplicate `generic.md`.** Cite it. And do not edit it without explicit approval — it
  grades every bot in the fleet.
- **Surgical edits only** where you touch an existing file (an existing persona, an existing
  checklist): smallest change, additive, preserve spoken lines, `${variables}`, tool names, payload
  field names and section structure. Never localize a `${variable}`, a tool name, or a fixed payload
  param — not in a case, not in a persona, not in a checklist item.
- **Instructions in English; only spoken lines in the target language.** Applies to personas and
  checklist items exactly as it applies to prompts.
- **One source of truth per fact.** Deploy identity lives in `raya/agents.json`; fleet labels/roles
  in `raya/regression/fleet.json`; test coverage here. Join on the target id; never re-copy.
- **Case and assertion ids are permanent.** A retired case keeps its number with `result: "retired"`
  so historical run records, digest items and changelog references stay resolvable.
- If the bot is not registered in `raya/agents.json`, or the prompt file is not in the repo, stop and
  hand back to `/register-bot` — do not guess target ids. A missing `raya/regression/fleet.json` is
  **not** a blocker: derive role/backend/label as `static_regression.py`'s `discover_prompts()` does
  and note the gap in the report.
