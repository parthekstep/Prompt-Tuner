---
name: update-prompt
description: Create or update a voice agent's conversation prompt and keep the language variants in sync. Apply a feedback item or bug fix to an agent (KKB, DKB, or Maya); the change is made on Hindi (source of truth) and mirrored to Kannada — language-agnostic logic copied verbatim, native-language content translated and adapted. Use whenever the user reports a prompt bug, gives feedback on agent behavior, or wants to change what an agent says or does. Also creates a new conversation prompt or a new language variant from scratch.
---

# Update Prompt

Apply a change to an agent's **conversation prompt** and keep Hindi ↔ Kannada in sync.

Resolve files via the path map in the repo root `CLAUDE.md`. Read
`reference/prompt-anatomy.md` (in this skill's folder) for the section taxonomy and the
AGNOSTIC / SPECIFIC / MIXED tags, and the Hindi→Kannada localization conventions.

## Scope

- **KKB, DKB** — Hindi + Kannada. Edit Hindi first, mirror to Kannada.
- **Maya** — Hindi only. No mirror.

## Procedure (update)

1. **Sync first.** Run the `/sync-check` procedure for the target agent (read its
   `SKILL.md`). If the Hindi/Kannada pair has drifted, reconcile it before applying the new
   change, so the change lands on an aligned base. (Skip for Maya — Hindi only.)
2. **Locate the change.** From the user's feedback/bug, identify the agent and the target
   section(s) using the anatomy. Read the relevant section in the **Hindi** file (and its
   Kannada twin) before editing.
3. **Edit Hindi (source of truth).** Make the change in the Hindi file, matching the
   surrounding style.
4. **Classify the change** using the anatomy tags:
   - **AGNOSTIC** (logic, conditions, variable names, tool payloads, structure) → will be
     copied verbatim.
   - **SPECIFIC** (spoken lines, examples, number-words, tone markers) → will be translated
     and adapted to Kannada idiom/script.
   - **MIXED** → split: copy the rule verbatim, adapt the quoted speech.
5. **Mirror to Kannada.** Apply the classified change to the Kannada file: verbatim for
   AGNOSTIC; translated/adapted for SPECIFIC, following the localization conventions
   (Kannada script, Kanglish, Kannada number-words, local place names) and matching the
   existing Kannada section's phrasing.
6. **Maya gate (KKB changes only).** If the agent is **KKB** and the change touches shared
   core logic (anything Maya inherits), **stop and ask** the user whether to also apply it to
   Maya Hindi. If yes, apply it while preserving Maya's divergences (college identity,
   `${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing,
   Marketing Masters League, feminine-voice rule — see `CLAUDE.md`). Never overwrite those.
7. **Changelog.** Append an entry to `<Agent>/CHANGELOG.md` (date, feedback/bug, change,
   files touched). If Maya was also updated, add an entry to `Maya/CHANGELOG.md` too.
8. **Report.** Summarize what changed in each file, the classification used, and a
   structural-parity note (confirm Hindi/Kannada section skeletons still align). For MIXED
   changes, show the Hindi line and its Kannada adaptation side by side.

## Procedure (create — new prompt or new language variant)

- **New language variant of an existing agent:** copy the structure of the existing language
  file; keep all AGNOSTIC content verbatim; translate/adapt all SPECIFIC content to the new
  language. Verify section parity against the source.
- **New conversation prompt from scratch:** scaffold from the section taxonomy in
  `reference/prompt-anatomy.md`, filling each section for the new agent's domain. Pull the
  agent's variables/tools/persona from `../port-feature/reference/agent-schemas.md` (add a new
  entry there if it's a new agent). Then create both language files via the new-language-variant
  step above.

## Guardrails

- **Surgical edits only.** Make the smallest change that accomplishes the task; preserve every other line, spoken phrase, variable, tool name, and payload exactly. Prefer additive changes; never reformat or delete unrelated content. The resulting diff should contain only the intended change. See `CLAUDE.md` → "Surgical edits only".
- Hindi is always the source of truth; never let Kannada lead.
- Never localize a `${variable}` name, a tool name, or a fixed payload param.
- Never translate-copy an AGNOSTIC change — it must be byte-identical logic.
- Never adapt a SPECIFIC change by pasting Hindi text into the Kannada file.
- When unsure whether something is AGNOSTIC or SPECIFIC, consult the anatomy; if still
  unclear, ask.
