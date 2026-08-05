---
name: sync-check
description: Audit whether a bot's conversation prompts are in sync across ALL its languages — one master language against N mirrors — detecting when a mirror lags because a language-agnostic change landed in only some languages, separating real drift from expected language differences and from owner-approved deliberate divergences (raya/divergences.json), and reconciling the laggards. Use when the user wants to check multilingual prompt parity, asks "are the languages in sync / which language is behind / did that fix land everywhere", before making a prompt change, or when a bot is being taken into new languages. Runs automatically as the first step of /update-prompt.
---

# Sync Check

Detect and reconcile drift between a bot's language variants. "Drift" = a
**language-agnostic** section that differs between two language files because a change
landed in one language but not the other(s). Expected language differences (different script,
spoken lines, number-words) are **not** drift. Neither is a **registered deliberate
divergence** — an owner-approved, recorded difference (see "The divergence registry" below).

## The model: one master, N mirrors

Two languages is the **special case**, not the model. A bot's languages are a **master +
N mirrors** fan-out:

- The **master language** is the source of truth. A change is made there first, then mirrored.
- Every other language is a **mirror**. Auditing = comparing the master against **each mirror
  independently**, then reporting a **per-language matrix** — which mirrors are current, which
  lag, and exactly what each one is missing.
- **Adding a language must never require editing this skill.** The language set is *discovered*
  from the deploy manifest (`raya/agents.json`) + the path map, never enumerated here.

## Scope

Applies to any bot that has **more than one** conversation-prompt language. A bot whose sync
family has exactly **one** language has nothing to mirror — report "single-language, nothing to
sync" and stop. (Today: **KKB** and **DKB** are `hi` + `kn`; **Maya** is Hindi-only; **Purple
Dots** is going multi-Indic. None of that is hard-coded — it is read from the manifest.)

## Inputs

- Target: a bot id (`KKB`, `DKB`, `Maya`, `purple-dots`, …), a project, or `all`
  (default `all` if unspecified).
- Optional: `--languages kn,te,ta` to audit a subset of mirrors.
- Resolve files via the path map in the repo root `CLAUDE.md` and the deploy manifest
  `raya/agents.json`. Never infer a file's language from its filename alone — the manifest's
  `language` field is authoritative (e.g. `KKB Placeholder Inbound.md` is Hindi).

## Reference

- `.claude/skills/update-prompt/reference/prompt-anatomy.md` — the section taxonomy and the
  AGNOSTIC / SPECIFIC / MIXED tags. Drift is only possible in AGNOSTIC content and in the
  AGNOSTIC portions of MIXED sections.
- `reference/n-language-parity.md` (this skill's folder) — how to resolve a **sync family** and
  its master, the five comparison passes (incl. the variable/tool/payload **token census**), the
  exact report tables, the false-positive discipline, and the divergence-registry schema. Read it
  before auditing more than two languages.
- `raya/divergences.json` — the **deliberate-divergence registry** (see below).

## Procedure

1. **Resolve the sync family and the master.** Group the bot's conversation prompts into
   **sync families** — one family per `(bot, direction, backend/variant)` — and list the
   languages present in each. Two files only belong in the same family if they are meant to be
   the same bot in different languages. Determine the master language for the family
   (resolution order in `reference/n-language-parity.md § Resolving the family`). One command
   prints the whole fan-out; use it rather than eyeballing filenames.
2. **Reconcile against live, per language target.** Any mirror can be AHEAD in production (the
   team edits the Raya console directly). Run `python3 scripts/raya_deploy.py diff <target>` for
   **every** target in the family — master and each mirror — before judging who lags. If a live
   agent is ahead, adopt it first (`scripts/raya_deploy.py pull <target>`, or `/raya-reconcile`
   if GET is flaky) so the audit compares real live content, not a stale repo file.
3. **Load every file in the family** and extract their section heading lists (`^#{1,3} ` lines).
   Compare each mirror's skeleton against the master's. A heading present in the master but
   missing from a mirror — or vice versa — is the strongest drift signal.
4. **Walk the taxonomy section by section, master vs each mirror.** For each section:
   - **AGNOSTIC section** → the text should be **byte-identical**, with one narrow carve-out —
     a heading or rule that *names its own script/language* legitimately carries that language's
     name (Devanagari vs Kannada). Any other English word rendered in the target script inside an
     instruction is a bug (English-instructions rule), not a localization. Any difference in
     logic, conditions, variable names, tool payloads, ordering, or added/removed rules =
     **agnostic drift**.
   - **MIXED section** → compare only the rule/logic parts. A new or changed *rule* on one
     side that is absent on the other = drift. A different *spoken line* is expected, not drift.
   - **SPECIFIC section** → differences are expected. Only flag if a section is entirely
     missing on one side, or if a structural sub-point (e.g. a new TTS category) exists on
     one side only. Also flag a **spoken-content gap**: the section exists but a required
     spoken element the master has (a fallback line, a TTS number category, an example for a
     new branch) has no counterpart in the mirror's language.
5. **Run the token census.** Extract every `${variable}`, tool name, payload field name, fixed
   param and enum literal from each file and set-compare master vs each mirror. These must be
   **identical across all languages** — a token present in one language only is drift or a
   localization bug (a localized variable/tool name is always a bug). Commands in
   `reference/n-language-parity.md § Pass 3`.
6. **Consult the divergence registry** (`raya/divergences.json`) before reporting anything.
   For each difference found in steps 3–5, check whether a registry entry covers it — matching
   on bot/target, language, section, and the entry's `contains` tokens. If covered, report it as
   **EXPECTED (registered divergence)** with the entry `id`, and never propose "fixing" it.
   An **UNREGISTERED** difference in AGNOSTIC content is what gets flagged as drift.
7. **Use the changelogs as evidence.** Read `<Bot>/CHANGELOG.md`. An entry describing a
   change whose content you find in only some language files confirms which side is ahead, and
   which languages the change never reached. A changelog entry that declares a divergence but has
   **no registry entry** is a registry gap — say so and offer to add the entry (step 10).
8. **Report the per-language matrix** — the headline every reader needs first, then detail.
   Exact table shapes and the verdict vocabulary are in
   `reference/n-language-parity.md § Report shape`. Summary form:

   **Table 1 — per-language status** (one row per mirror; the master is the baseline)

   | Language | In sync? | Missing AGNOSTIC content | Spoken-content gaps | Registered divergences | Verdict |
   |---|---|---|---|---|---|
   | … | ✓ / ✗ | short list | short list | count + ids | CURRENT / LAGS (n) / AHEAD / UNCERTAIN / MISSING |

   **Table 2 — drift detail** (only for rows that are not CURRENT)

   | Language | Section | Tag | Status | Ahead | Missing from laggard |
   |---|---|---|---|---|---|
   | … | … | AGNOSTIC/MIXED/SPECIFIC | **AGNOSTIC DRIFT** / spoken gap / EXPECTED (registered) / uncertain | master / mirror / — | short description |

   Close with one headline line: master language, N languages audited, how many CURRENT /
   LAGGING / UNCERTAIN, and how many differences were suppressed as registered divergences.
9. **Offer to reconcile — fan out to every laggard.** Snapshot first
   (`scripts/prompt-version.sh save <bot> pre-sync-<slug> "<why>"`). Then, for each drifted
   section in each laggard: copy the AGNOSTIC content verbatim; for the AGNOSTIC part of a
   MIXED section, insert the rule and adapt any accompanying spoken line to that mirror's
   language per the localization conventions in `prompt-anatomy.md` (and, for a language the
   repo has no conventions for yet, via `/translate-prompt`). Ask before writing unless the
   caller (e.g. `/update-prompt`) has already authorized reconciliation. Reconcile mirrors
   **one language at a time** and report each — never batch-apply blind.
10. **After reconciling,** append a `CHANGELOG.md` entry noting the sync (what was brought into
    alignment, which direction, **which languages**). If the reconciliation deliberately *left*
    a difference in place at the owner's instruction, add or update the corresponding
    `raya/divergences.json` entry in the same change — an intentional divergence that is not in
    the registry will be "fixed" as drift by the next audit.
11. **Deploy every reconciled target — before any testing.** A reconciliation that lands only in
    the repo leaves live behind: the same "the fix landed in one place, not the other" split the
    sync rule exists to prevent, and a `/voice-test` run against an un-deployed agent grades the
    OLD prompt (a meaningless PASS, or a bogus FAIL). So for **each** reconciled language target:

    ```bash
    python3 scripts/raya_deploy.py verify <target>   # right URL + name guard, read-only
    python3 scripts/raya_deploy.py diff   <target>   # must show the reconciled delta and nothing else
    python3 scripts/raya_deploy.py deploy <target>   # snapshot → GET backup → guard → diff → confirm → PATCH → read-back
    ```

    `deploy` is the only write path: it is gated (asks for confirmation), name-guarded (refuses a
    uuid whose live agent name does not match the target), and **read-back byte-compares** the
    live prompt against the local file — never trust a bare GET as proof of what is live. If the
    diff shows anything beyond the reconciled sections, stop and re-check the edit. Append each
    deploy to `raya/deploy-history.md`. Never edit the prompt in the Raya console instead — that
    clobbers console-only content. Deploy the master too if the reconciliation touched it, and
    confirm every changed target reads `in sync` afterward. Only then run the testing tiers below,
    per language.

## The divergence registry (`raya/divergences.json`)

Some language differences are **intentional** and must never be reconciled away. Real case:
on **2026-08-04** the two KKB **Kannada Signals** bots were deliberately given a personal name
(**ಮಾಯಾ / Maya**) in their persona line, opening line and intro-turn rules, while the Hindi
Signals twins intentionally kept the institution-only intro (see the 2026-08-04 entry in
`KKB/CHANGELOG.md`). A naive N-language audit reads that as intro drift, and a future
maintainer "corrects" it — silently undoing an owner decision.

So the registry is **machine-checkable state, not prose**:

- **Location:** `raya/divergences.json`, alongside `agents.json`. It belongs with the deploy
  manifest, not inside a skill folder: it is data about the fleet — read today by `/sync-check`,
  and specified for `/update-prompt`, `/port-feature` and the daily static suite (not yet wired
  — G3 follow-up) — and it must be git-tracked, reviewable in a diff, and loadable by a Python
  check.
- **Each entry records:** which bot/targets, which languages diverge from the master, which
  sections/lines legitimately differ (with `contains` tokens so a script can match the actual
  delta), **why**, **who approved it**, the **date**, the changelog reference, and what must
  **still** match. Full field-by-field schema in `reference/n-language-parity.md § Registry`.
- **`/sync-check` consults it in step 6** and downgrades covered differences to
  **EXPECTED (registered divergence)**. Only **unregistered** differences are flagged as drift.
- **`/update-prompt` (and `/port-feature`) MUST add an entry** whenever it makes an intentional
  language-specific divergence — i.e. whenever it deliberately applies a change to some
  languages of a family and not others, or suspends the mirror rule. Same change, same commit as
  the prompt edit and the changelog entry. No entry = the divergence will be reverted as drift.
- **A registry entry is not a licence to drift.** It is scoped: it covers only the listed
  sections and tokens for the listed languages. Everything in `still_must_match` is still
  audited normally, and an entry that has gone stale (`review_on` passed, or the divergence no
  longer present in the file) is reported as a **registry gap**, not silently honoured.

## When invoked from /update-prompt

Run steps 1–8 silently-but-reported, then:
- If **no drift**, say so and let the change proceed.
- If **drift found**, surface the matrix and reconcile the affected sections in every laggard
  first (so the new change lands on an aligned base across all languages), then continue. Do
  not silently overwrite — show what you aligned, per language.
- If the change `/update-prompt` is about to make is itself an intentional single-language
  change, tell it to register the divergence (step 10) rather than treating the resulting
  difference as a future bug.

## Relationship to the daily static suite (gaps G3/G4)

Tier 3 (`raya/regression/static_regression.py`) currently does a **crude two-language parity
check**: `sync_parity()` buckets prompts by `(agent, direction, backend)`, requires exactly
`hi` and `kn` to be present, counts `^#{1,2} ` headings in each, and flags a difference of more
than 2. That is a placeholder — it cannot see a third language, it compares counts rather than
content, and it has no idea the Maya/Kannada divergence is deliberate. It should become:

- **Manifest-driven** — build the sync families from `raya/agents.json` (conversation targets
  grouped by bot/direction/variant) instead of the hard-coded file list in `discover_prompts()`,
  so a new bot or a new language is picked up with no code edit (G4).
- **N-language** — for each family, compare the master against **each** mirror and emit one
  finding per lagging language, instead of requiring an `hi`/`kn` pair.
- **Structural, not numeric** — compare the heading *sets* (symmetric difference) plus the
  token census (`${variables}`, tool names, payload fields), not heading counts. Counts hide a
  swapped section and invent noise from formatting.
- **Registry-aware** — load `raya/divergences.json` and suppress covered differences, reporting
  them (if at all) as informational "expected divergence", so the digest's signal survives
  going from 2 languages to 8.

**Do not edit that script from this skill** — this is the specification for the G3/G4 follow-up
work recorded in `docs/MULTI-PROJECT-ROADMAP.md § 5`.

## Test before done (MANDATORY — a reconciliation is not DONE until tested)

Reconciling changes live prompt files, so it is a prompt change and carries the same bar. A
change is NOT done when the files are edited/deployed — only when it has been TESTED and
confirmed working, with overall sanity intact. Never report a sync reconciliation as "done",
"fixed", or "in sync" until you have actually tested it. **A Tier-1 test run before the reconciled
file is deployed proves nothing** — it grades the old live prompt. Deploy each reconciled target
first (step 11), then test it. Run the **three testing tiers** (repo `CLAUDE.md` → "The three
testing tiers"):

1. **Tier 1 — Fix verification:** `/voice-test` each reconciled language on the scenario the
   copied-in logic governs, and confirm the new behavior in a real transcript.
2. **Tier 2 — Blast-radius regression:** confirm the inserted rule broke nothing adjacent in
   that language — the whole flow still runs, the tool payloads it touched are still valid, and
   the mirror's own SPECIFIC content (spoken lines, TTS spellings) was not damaged.
3. **Tier 3 — Daily general regression:** the standing suite in `raya/regression/` catches
   longer-tail drift; it does not replace tiers 1–2.

**Test EVERY reconciled language independently — never extrapolate.** "The Hindi base was fine
and the copy is byte-identical, so Kannada/Telugu/Tamil are fine" is the recipe-for-disaster
rule this repo exists to prevent: runtime adherence, ASR and TTS differ per language, so a
byte-identical mirrored edit can still land differently. With N mirrors that means N tests, one
per language, plus each direction (outbound/inbound) the family covers. Where a variant cannot
be harness-tested (inbound-only, telephony down), do the best available verification
(post-deploy transcript review + static sanity) and mark the residual **VERIFY-PENDING** — never
claim done. Revert on any regression (`/prompt-version`).

## Guardrails

- **Surgical edits only.** When reconciling, change only the drifted content; touch nothing
  else. Bring the laggard up with the smallest edit, preserving all other lines exactly. Prefer
  additive changes; never reformat or delete unrelated content. See `CLAUDE.md` → "Surgical edits only".
- Never "fix" an expected language difference by making a mirror match the master's script — that
  would be a regression. Same for spoken lines, TTS number-words, tone markers, place and person
  names, and culturally-adapted banned-phrase lists: **differing is their correct state.**
- Never localize a `${variable}` name, a tool name, or a fixed payload param in any language —
  and never "reconcile" one by translating it.
- Never propose reconciling a difference that a `raya/divergences.json` entry covers. If you
  believe a registered divergence is wrong, say so and ask the owner; do not edit it away.
- **Instructions are always English; only spoken lines are in the target language.** If you find
  rule/instruction prose written in Hindi/Kannada/Telugu/etc. in any file, that is a bug in its
  own right — report it (and route it to `/update-prompt`), don't mirror it to other languages.
- The master language always leads; never let a mirror lead a reconciliation. If a mirror
  genuinely has better content, escalate it to the master first via `/update-prompt`, then
  fan out.
- Reconcile mirrors one language at a time, and reconcile **before** applying a new change, not
  during — a new change landing on top of half-aligned files is how a family goes three ways.
- If you cannot tell whether a difference is a deliberate language choice or true drift, flag
  it as **uncertain** and ask the user rather than guessing. With N languages, one wrong guess
  fans out N times.
- Never git commit or push as part of an audit.
