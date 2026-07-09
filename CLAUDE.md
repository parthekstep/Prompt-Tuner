# Prompt Tuner — Voice Agent Prompt Maintenance

This repo holds the system prompts for three voice AI agents. The job of anyone
working here is to **iterate on these prompts from feedback/bugs while keeping the
language variants in sync**. Do not treat these as ordinary docs — a wording change
in one language that does not land in its twin is a regression.

## Surgical edits only — these prompts are fragile

These prompts run live voice agents; a stray change can break the whole agent. Every edit
must be **surgical**: change only what the task requires, and nothing more.

- Make the **smallest edit** that accomplishes the goal. Do not reformat, re-wrap, re-style,
  re-order, or "clean up" surrounding text while you're in there.
- **Preserve exactly:** spoken lines, variable names (`${...}`), tool names, JSON payloads
  and field names, fixed params (e.g. `sourceService: "ONESTAGENT"`, `app_instance`), and
  section structure — unless the change is explicitly about one of them.
- Prefer **additive** changes. Do not delete content the task didn't ask you to remove.
- Never localize a variable/tool/payload name; never paste one language's spoken text into
  the other file.
- When in doubt, do less and ask. After editing, the diff should contain **only** the intended
  change — if it shows incidental edits, revert them.
- One real exception: a fix the user explicitly approved that is broad by nature (e.g. the
  DKB full reconciliation). Even then, scope it to the approved items and preserve everything else.

## Agents

- **KKB** — government job-matching agent for workers/seekers (Hindi + Kannada). Persona: *काम की बात / ಕೆಲಸದ ಮಾತು*.
- **DKB** — "Dhandhe Ki Baat", job verification & capture agent for MSME business owners/employers (Hindi + Kannada). Persona: *धंधे की बात*.
- **Maya** — a KKB spinoff for higher-ed graduates in UP; campus-recruitment context. **Hindi only.** Persona: *माया, [college_name] की ओर से*.

Each agent has three prompt types: a **conversation prompt** (one file per language),
a **memory prompt** (one language-agnostic file, English output), and an
**output prompt** (one language-agnostic file that extracts call variables).

## File path map

Filenames are kept as-is (note KKB's "Placeholder" naming). Always resolve files through this map.

| Agent | Hindi | Kannada | Memory | Output |
|---|---|---|---|---|
| KKB | `KKB/KKB Placeholder Hindi.md` | `KKB/KKB Placeholder Kannada.md` | `KKB/KKB Memory.md` | `KKB/KKB Output.md` |
| DKB | `DKB/DKB Hindi.md` | `DKB/DKB Kannada.md` | `DKB/DKB Memory.md` | `DKB/DKB Output.md` |
| Maya | `Maya/Maya Hindi.md` | — (none) | `Maya/Maya Memory.md` | `Maya/Maya Output.md` |

## Core principle: agnostic vs language-specific

Every conversation prompt is built from two kinds of content. **Every edit must be
classified before it is mirrored.**

- **Language-agnostic** — call-flow logic, phase/step structure, input-variable names,
  tool-call rules and JSON payloads, conditions/routing, prohibited-behavior rules,
  dignity safety checks, the section skeleton itself. → **Copied verbatim** across languages.
- **Language-specific** — spoken greeting scripts, example dialogues, TTS
  number-to-word spellings, script rules (Devanagari vs Kannada), tone markers,
  culturally-adapted prohibited phrases, sample conversations (incl. place/person
  names). → **Translated and adapted** to the target language's idiom, script, and
  conventions. Kannada uses "Kanglish", Kannada-script numerals spelled as words, and
  local place names (Bengaluru/Mysuru/Dharwad rather than Pune/Ghaziabad).

The full section-by-section taxonomy with agnostic/specific tags lives in
`.claude/skills/update-prompt/reference/prompt-anatomy.md`.

Memory and Output prompts are **single language-agnostic files per agent** (their output
values are always English) — they have no cross-language twin and are edited once.

## Sync rule

A conversation-prompt change is never "done" after editing one language. The Hindi file
is the **source of truth**; changes are applied there first, then mirrored to Kannada
(verbatim for agnostic content, adapted for language-specific content). Before applying
any new change, the prompt pair must already be in sync — `/update-prompt` runs
`/sync-check` first to guarantee this.

## Maya rule (flag-and-ask)

Maya inherits KKB's language-agnostic core but has its own divergences that must **never**
be overwritten by a KKB sync:

- `${college_name}` input variable and campus caller-identity ("माया, [college] की ओर से", not government)
- optional `hr_contact` and `benefits` recommendation fields
- the **Experience Capture** section
- HR-number sharing post-apply
- the **Marketing Masters League** fallback offer
- the explicit **feminine-voice** rule (Hindi feminine verb forms only)

When a KKB change touches shared core logic, **flag it and ask** the user whether to
also apply it to Maya Hindi before doing so. Maya is Hindi-only — there is no Kannada sync for it.

## Memory injection block (required when memory is enabled)

Once an agent has memory enabled (its memory prompt exists), **every** conversation prompt
for that agent — in every language — must contain this block **exactly**, verbatim:

```
### Contact context
Here is the caller context:
{${contact_memory}}
```

This is the injection point where the memory prompt's output (`contact_memory`) is fed back
into the conversation prompt. It is **language-agnostic** — the same three lines in English
in every language file; never translate or alter them. Placement: inside the intro rules
(KKB/Maya) or at the end of the Input Variables section (DKB) — wherever the agent already
has it; if absent, add it at the end of Input Variables. Creating/enabling a memory prompt
(`/update-memory`) must verify and, if needed, add this block to all of the agent's
conversation prompts.

All three agents currently have memory enabled, so all five conversation prompts carry this block.

## Changelog rule

Every prompt edit appends an entry to the agent's `CHANGELOG.md`
(`KKB/CHANGELOG.md`, `DKB/CHANGELOG.md`, `Maya/CHANGELOG.md`). Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

## Bug-fix feedback loop (pre-empt the next occurrence)

Fixing a **bug** in a prompt is not done until the analyser is taught to catch it. Whenever a
bug is fixed (via `/update-prompt`, `/port-feature`, `/update-memory`, or `/update-output`),
you must also update **`/prompt-analyser`** so the same failure class is flagged pre-emptively
in future audits:

- Add or sharpen an entry in `.claude/skills/prompt-analyser/reference/bug-patterns.md` —
  symptom → root cause → **detection heuristic** → fix direction → source agent + date.
- If the bug implies a section that must always exist for that use case, update
  `.claude/skills/prompt-analyser/reference/section-checklists.md`.

The `CHANGELOG.md` entry records *what* changed; the analyser update ensures the scenario is
*detected before it ships again*. This applies to bug fixes only — not to pure feature
additions or ports of already-working behaviour.

## How to make a change

| Task | Skill |
|---|---|
| Apply a feedback item / bug fix to a conversation prompt (both languages) | `/update-prompt` |
| Create or edit an agent's memory prompt | `/update-memory` |
| Create or edit an agent's output prompt | `/update-output` |
| Audit whether the language variants have drifted | `/sync-check` |
| Carry a feature from one agent to another (e.g. KKB → DKB / Maya) | `/port-feature` |
| Audit a prompt for latent gaps / bug-prone patterns before running it | `/prompt-analyser` |

`/update-prompt` auto-runs `/sync-check` first, so a new change always lands on an
aligned base. `/prompt-analyser` is a read-only pre-flight review (flags, does not fix);
route its confirmed findings to `/update-prompt`.
