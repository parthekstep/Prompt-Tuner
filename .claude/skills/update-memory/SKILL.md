---
name: update-memory
description: Create or update a voice agent's memory prompt — the language-agnostic instruction that updates the per-user memory JSON after each call (English output). Use when the user wants to add/rename/retire a memory field, change an enum, adjust the summary rules, or create a memory prompt for an agent that lacks one (KKB, Maya). One memory prompt per agent; no cross-language sync needed.
---

# Update Memory

Create or update an agent's **memory prompt**. Memory prompts are **language-agnostic** —
one file per agent, all output values in English — so there is no Hindi/Kannada twin and no
cross-language sync.

Resolve files via the path map in the repo root `CLAUDE.md`. Read `reference/memory-anatomy.md`
(this skill's folder) for the required sections, the flat entity-map shape, the layer
structure, and per-agent re-domaining notes. `DKB/DKB Memory.md` is the reference
implementation.

## Procedure (update)

1. Open the agent's memory file. Identify the change (new/renamed/retired field, enum change,
   summary-rule change).
2. Apply it. **Keep the Entity Map description and the Output JSON schema identical** — if you
   add/rename/retire a field, edit both. Update enum value lists in the Entity Map line.
3. Preserve the invariants: flat 1-level keys, English-only output, `*_exact` companion fields
   for bracketed enums, the three derived fields (`recent_changes`,
   `last_conversation_summary`, `overall_conversation_summary`), and the update rules.
4. Append an entry to `<Agent>/CHANGELOG.md`.
5. Report what changed and confirm the schema and Entity Map still match.

## Procedure (create)

Use when an agent has no memory prompt (currently KKB and Maya).
1. Start from `DKB/DKB Memory.md` as the template.
2. Re-domain the Role line and the entity-map layers to the agent's domain per
   `reference/memory-anatomy.md` (KKB/Maya = seeker memory; Maya adds campus fields).
3. Write all required sections in order, ending with the exact Output JSON schema (every
   field, then the three derived fields).
4. Ensure it backs whatever the conversation prompt expects from memory (e.g. KKB's
   "Introduction Priority Rule" needs prior-call state to pick the opening line).
5. Create the file at the path-map location.
6. **Ensure the memory injection block** (enabling memory requires it). Check that **every**
   conversation prompt for this agent, in **every** language, contains exactly:
   ```
   ### Contact context
   Here is the caller context:
   {${contact_memory}}
   ```
   These three English lines are language-agnostic — add them verbatim (never translate). If a
   file is missing the block, add it inside the intro rules where the agent has it, or at the
   end of the Input Variables section otherwise. See `CLAUDE.md` → "Memory injection block".
7. Append a `CHANGELOG.md` entry (note both the new memory prompt and any conversation files
   that received the injection block), and report.

## Guardrails

- **Surgical edits only.** Make the smallest change that accomplishes the task; preserve every other field, rule, and line exactly. Prefer additive changes; never reformat or delete unrelated content. See `CLAUDE.md` → "Surgical edits only".
- Output values are **always English**; keep the Language rule section.
- No nested objects, no arrays of objects in the entity map.
- Entity Map and Output JSON schema must always list the same fields.
