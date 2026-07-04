---
name: update-output
description: Create or update a voice agent's output prompt — the language-agnostic spec that extracts structured call variables from a finished transcript. Use when the user wants to capture a new variable, change an enum or extraction rule, or create an output prompt for an agent that lacks one (Maya). One output prompt per agent; no cross-language sync needed.
---

# Update Output

Create or update an agent's **output prompt**. Output prompts are **language-agnostic** —
one file per agent; extracted text uses the speaker's words and `final_summary` is English —
so there is no Hindi/Kannada twin and no cross-language sync.

Resolve files via the path map in the repo root `CLAUDE.md`. Read `reference/output-anatomy.md`
(this skill's folder) for the two valid layouts (DKB phase-based, KKB field-list +
EXAMPLE OUTPUT), the field types, and the extraction rules. `DKB/DKB Output.md` and
`KKB/KKB Output.md` are the reference implementations.

## Procedure (update)

1. Open the agent's output file and note which layout it uses.
2. Apply the change:
   - **New captured variable** → add the field (name + allowed values/description). If the
     file is KKB-style, also add it to the EXAMPLE OUTPUT JSON and reference it in the Rules block.
   - **Enum change** → update that field's allowed-value list.
   - **Extraction-behavior change** → edit the Rules block.
3. Preserve the extraction rules (never infer; use speaker's words; `"NA"`/`[]`/`0` sentinels;
   mutually-exclusive arrays; no hallucinated names/salaries; English `final_summary`).
4. Append an entry to `<Agent>/CHANGELOG.md`.
5. Report what changed.

## Procedure (create)

Use when an agent has no output prompt (currently Maya).
1. Pick the layout matching the agent's family — Maya follows **KKB style** (field list +
   EXAMPLE OUTPUT + Rules).
2. Start from the sibling's output file (`KKB/KKB Output.md` for Maya) and re-domain.
3. Add the agent's extra captured variables per `reference/output-anatomy.md` (Maya adds
   `hr_contact_shared`, `benefits_mentioned`, `mml_offered`, `mml_registered`) to both the
   field list and the EXAMPLE OUTPUT.
4. Keep the full extraction Rules block.
5. Create the file at the path-map location, append a `CHANGELOG.md` entry, and report.

## Guardrails

- **Surgical edits only.** Make the smallest change that accomplishes the task; preserve every other field, rule, and line exactly. Prefer additive changes; never reformat or delete unrelated content. See `CLAUDE.md` → "Surgical edits only".
- `final_summary` is always English regardless of call language.
- Keep sentinels consistent: `"NA"` strings, `[]` arrays, `0` counts.
- Array-of-objects fields stay full objects — never flatten to strings.
