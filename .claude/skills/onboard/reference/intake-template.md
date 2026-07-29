# Bot Intake Summary

> Filled by `/onboard`. Save to `raya/intake/<bot-id>.md`. Every field the tuner needs to start
> without re-asking. Use **TBD** for anything not yet known (a TBD is a to-do, not a blocker).

- **Date:**
- **Onboarded by:**
- **Path:** Branch A (existing bot) | Branch B (new bot)

## 1. What the bot does
- **Bot name / persona:**
- **Domain:**
- **Who it talks to (audience):**
- **Goal of one call (what "done" means):**
- **Direction:** inbound (receives calls) | outbound (places calls) | both

## 2. Languages
- **Languages spoken:**
- **Source-of-truth (master) language:**  <!-- edited first, mirrored from -->

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
> These become tester personas + bot-specific checklist items (on top of the generic checklist).

| Scenario | What a GOOD call looks like (success criteria) |
|---|---|
|  |  |

## 7. Known bugs / recent calls
- **Reported issues:**
- **Real call reference(s) / uuid(s) that show them:**  <!-- required before any fix -->

## 8. Registration + next steps (tuner-facing)
- **Proposed `raya/agents.json` target id(s):**  <!-- e.g. chai-hi-out, chai-kn-out -->
- **`expected_name_contains` guard tokens:**
- **Needs sync-check (multi-language)?** yes / no
- **Snapshot label before first edit:**
- **Checklist to grade against:** generic + [ existing family: kkb/dkb/maya | NEW bot-specific to seed ]
- **Immediate next action:**  <!-- /load-context · /voice-test · /prompt-analyser · /bug-fix · /update-prompt (new-prompt path) -->
- **Open TBDs (and what each unblocks):**
