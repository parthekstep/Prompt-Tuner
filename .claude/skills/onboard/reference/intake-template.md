# Bot Intake Summary

> Filled by `/onboard`. Save to `raya/intake/<bot-id>.md` — use the existing `raya/agents.json`
> target `id` for a Branch A bot, and a **project-unique** bot key for a new one, so two projects
> can never collide on one filename. Every field the tuner needs to start without re-asking. Use
> **TBD** for anything not yet known (a TBD is a to-do, not a blocker).

- **Date:**
- **Onboarded by:**
- **Project (slug / label):**  <!-- blue-dots / Blue Dots · purple-dots / Purple Dots · <kebab-slug> / <Label> — scopes the folder, path-map section, agents.json `project`, regression fleet entry, digest label -->
- **Bot key:**  <!-- short, project-unique, lowercase — used in issue-ids and target ids, e.g. kkb, dkb, maya, pd -->
- **Path:** Branch A (existing bot) | Branch B (new bot)

## 1. What the bot does
- **Bot name / persona:**
- **Domain:**
- **Who it talks to (audience):**
- **Goal of one call (what "done" means):**
- **Direction:** inbound (receives calls) | outbound (places calls) | both

### 1b. Caller context + access needs
> How the bot must SPEAK to these callers. A design constraint on behaviour — never a topic the bot
> raises. "Nothing special" is a valid answer.

- **Who is on the other end (in their words):**
- **Access / interaction needs:**  <!-- e.g. slower pace, longer silence tolerance before re-prompting, always repeat on request, short turns, spoken menu instead of free-form answer, no rushed decisions -->
- **Anything the bot must NOT do:**  <!-- e.g. never name or ask about a condition; never assume the caller can answer at a default speed -->
- **Graded where:** generic checklist §14 Accessibility (`.claude/skills/voice-test/reference/checklists/generic.md`) — applies to every bot on the rail — **plus** this bot's own `X`-family cases in `raya/testcases/<bot-id>.json`

## 2. Languages
- **Languages spoken (ALL of them):**  <!-- any set of Indic languages; not limited to Hindi/Kannada -->
- **Source-of-truth (master) language:**  <!-- edited first, mirrored from -->
- **Mirror languages:**  <!-- every non-master language; agnostic content copied byte-identically, spoken lines adapted; audited by /sync-check -->
- **Languages wanted but NOT built yet:**  <!-- these are /translate-prompt jobs, not mirror jobs: new spoken idiom + TTS/script conventions re-derived + a new Raya agent -->

## 3. Prompt(s)
- **Conversation prompt(s):**  <!-- per language: pasted? or file path -->
  - `<lang>` → `<Bot>/<Bot> <Lang>.md` (proposed path)
- **Memory prompt?** yes / no →  `<Bot>/<Bot> Memory.md`
- **Output prompt?** yes / no →  `<Bot>/<Bot> Output.md`
- **If memory enabled:** memory-injection block present in every conversation prompt? yes / no / TODO

## 4. Platform
- **Runs on Raya?** yes / no
- **If not Raya:** platform =  ; note what we can/can't do (iterate + sync + analyse = yes; auto-deploy + agent-to-agent call harness = Raya-only)
- **Raya agent uuid(s):**  <!-- may be several: per language × per direction -->
  - `<lang>/<direction>` → prod: ____  staging: ____
- **Phone number / DID(s):**

## 5. Tools / APIs the bot calls
> One row per tool. Leave blank if the bot calls nothing.

| Tool name | Endpoint | Auth | Payload shape (key fields) | Fixed params (never change) | Constraints / quirks |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 6. Test cases + success criteria
> These become tester personas + bot-specific checklist items (on top of the generic checklist),
> emitted per language the bot speaks by `/generate-test-cases`. Reproduction cases for reported
> issues are NOT listed here — they come from the issue-ids in §7b.

| Scenario | What a GOOD call looks like (success criteria) |
|---|---|
|  |  |

## 7. Known bugs / recent calls
- **Reported issues:**
- **Real call reference(s) / uuid(s) that show them:**  <!-- required before any fix -->

### 7b. Structured issue records (the issues they want fixed)
> ONE row per issue — each individually testable. `issue-id` = `<bot-key>-i<NN>`, assigned in the
> order raised, **never renumbered or reused**. `where` lists the affected `raya/agents.json` target
> ids explicitly (never "all languages" — every variant is tested independently). These ids are
> reused downstream by `/generate-test-cases` (persona `raya/personas/<lang>-repro-<issue-id>.md` +
> a `[repro <issue-id>]` checklist item), `/voice-test` (run label `repro-<issue-id>-<target-id>`),
> and the `CHANGELOG.md` / analyser entry — which is how "is this one fixed?" stays answerable.
>
> `severity`: `blocker` (call fails / wrong action fires / wrong data written) · `major` (completes
> but degraded) · `minor` (wording/cosmetic) · `wish` (feature request, say so).
> `status`: `reported` → `repro-confirmed` | `no-repro` | `not-a-prompt-bug: data-input` |
> `not-a-prompt-bug: backend` | `not-a-prompt-bug: runtime-adherence` → `fixed-for-uat` → `verified`
> (`fixed-for-uat` is NOT confirmed; only a post-deploy transcript per variant earns `verified`).

| issue-id | symptom (one line, observable) | where (target ids) | trigger (caller state • input args • turn/step) | expected | actual | call-ref (uuid + date) | severity | status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

- **Reproduction verdicts (filled in Step 2, before any fix):**  <!-- one line per issue-id: id → status → evidence (call uuid) → route (/update-prompt · escalate · need-uuid) -->

## 8. Registration + next steps (tuner-facing)
> These are the fields `/register-bot` needs. Derive them from the answers above — don't hand the
> customer the jargon.

- **Bot folder slug:**  <!-- e.g. `Purple Dots/` → files `Purple Dots/Purple Dots <Lang>.md` -->
- **Backend / variant tag:**  <!-- signals | dhiway | none — feeds the fleet entry + target id suffix -->
- **Bot role:**  <!-- seeker | provider | service-navigator | other — selects which regression tool checks apply -->
- **Proposed `raya/agents.json` target id(s):**  <!-- e.g. chai-hi-out, chai-kn-out -->

| Proposed target `id` | prompt `file` | language | direction | `raya_name` (live agent name) | `raya_agent_id` prod | `raya_agent_id` staging |
|---|---|---|---|---|---|---|
|  |  |  |  |  | `<FILL BY HAND>` | `<FILL BY HAND>` |

> **The uuid is copied by hand from `python3 scripts/raya_deploy.py list` — never inferred from a
> filename** ("KKB Placeholder Inbound.md" is the *Hindi* inbound bot). Leave `<FILL BY HAND>` until
> the real value is read off `list`; a target whose uuid for the active env is empty is skipped by
> deploy. `/register-bot` writes these entries — onboarding only records the values.

- **Phone number / DID per target:**
- **`expected_name_contains` guard tokens:**
- **Needs sync-check (multi-language)?** yes / no  <!-- master vs every mirror, pairwise -->
- **Snapshot label before first edit:**  <!-- scripts/prompt-version.sh save <bot> pre-<slug> "<why>" -->
- **Checklist to grade against:** generic + [ existing family checklist `<bot>.md` (today: kkb / dkb / maya) | NEW `<bot>.md` to be seeded by /generate-test-cases ]
- **Regression fleet entry needed?** yes / no  <!-- so the daily standing check covers this bot too -->
- **Immediate next action:**  <!-- /register-bot · /prompt-analyser · /generate-test-cases · /voice-test (reproduce the issue-ids) · /translate-prompt · /bug-fix · /update-prompt -->
- **Full pipeline reference:** `docs/WORKFLOW.md`
- **Open TBDs (and what each unblocks):**
