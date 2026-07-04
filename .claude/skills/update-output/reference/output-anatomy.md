# Output Prompt Anatomy

An output prompt is a **language-agnostic** extraction spec: it reads a finished call
transcript and emits a structured object of call variables. The call may be in any
language; extracted text uses the speaker's words and `final_summary` is always **English**.
One output prompt per agent (no language twin). `DKB/DKB Output.md` and `KKB/KKB Output.md`
are the reference implementations — two valid layouts:

- **DKB style:** organized by call **phase** (Phase 1 Freshness → Phase 2 Details → Phase 3
  New Job → Phase 4 Insights → Summary), each phase listing its fields with allowed values.
- **KKB style:** a numbered list of fields, each with name, description, and allowed values,
  followed by a full **EXAMPLE OUTPUT** JSON and a **Rules** block.

Either layout is fine; match the one the agent already uses.

## Field types

- **Enum field** — fixed value set, e.g. `job_status`: Active / Closed / Unverified / N/A;
  `call_answered`: Yes / No. List every allowed value with a one-line meaning.
- **Free-text value field** — captured as the speaker stated it; blank/`"NA"` if not mentioned.
- **Count field** — integer (e.g. `applications_count`, `fields_updated`); `0` if none.
- **Array-of-objects field** — e.g. `jobs_recommended`/`jobs_applied`; each object a complete
  record (do not flatten to strings). Failure arrays add a `failure_reason`.
- **`final_summary`** — 2–3 sentences, plain English, factual, no opinions/speculation.

## Extraction rules (always include)

- Never infer or assume — extract only what was explicitly stated by the user.
- If unclear or the call dropped before a field could be confirmed, leave blank / use the
  agent's "unverified" sentinel.
- Use the **user's** words, not the bot's, to fill fields.
- Sentinels: `"NA"` for absent strings, `[]` for empty arrays, `0` for empty counts (don't mix them up).
- Mutually-exclusive arrays stay mutually exclusive (a job is applied OR failed, never both).
- Never hallucinate names, salaries, or contact details — only what's in the transcript/recommendations.
- `final_summary` is always English regardless of call language.
- Some fields must always be filled (e.g. DKB `job_status`) — state which.

## Per-agent notes

- **DKB** — phase-based; key field `job_status` (always filled). Complete.
- **KKB** — field-list + EXAMPLE OUTPUT JSON; job arrays carry `{job_id, role, company_name,
  company_location, salary_offered, qualification_required}` (+ `failure_reason` on failures);
  `drop_reason` captures **seeker behavior only**, not technical failures. Complete.
- **Maya** — KKB output + campus fields: `hr_contact_shared` (Yes/No), `benefits_mentioned`
  (Yes/No), `mml_offered` (Yes/No), `mml_registered` (Yes/No). Add these to both the field
  list and the EXAMPLE OUTPUT.

## Common edits

- **Add a captured variable:** add the field (name + values/description) AND, if KKB-style,
  add it to the EXAMPLE OUTPUT JSON and the Rules block.
- **Change an enum's values:** update the allowed-value list for that field.
- **Tighten extraction behavior:** edit the Rules block.
