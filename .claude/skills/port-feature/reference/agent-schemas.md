# Agent Schemas

Per-agent input variables, tools, persona, and audience. Used by `/port-feature` to
**re-domain** a feature when carrying it from one agent to another — variable and tool
names must be remapped to the target's schema, never copied verbatim from the source.

---

## KKB — worker / seeker job-matching

- **Persona:** *काम की बात / ಕೆಲಸದ ಮಾತು* — government/city-administration job board.
- **Audience:** job seekers (ITI graduates, daily-wage workers, women returning to work, displaced workers, persons with disability, proxy callers).
- **Languages:** Hindi, Kannada.
- **Input variables:**
  - `${contact_name}` — caller name (spoken sparingly)
  - `${contact_phone}` — caller phone (tool calls only, never spoken)
  - `${country_code}` — country code (tool calls only)
  - `${new_seeker}` — "yes"/"no"; drives profile-fetch branch
  - `${recommendations}` — JSON array (≤10), each: `job_id, role, company, qualification, salary, vacancy, location`
- **Tools:** `get_profile`, `create_profile`, `apply_job`, `update_profile`. **Never** call `get_jobs`.

## DKB — MSME employer job verification & capture

- **Persona:** *धंधे की बात (Dhandhe Ki Baat)* — government employment program calling employers.
- **Audience:** MSME business owners / employers.
- **Languages:** Hindi, Kannada.
- **Input variables** (describe jobs already posted by this employer; "Not Available" = missing):
  - `${company_name}`, `${job_role}`, `${num_vacancies}`, `${job_id}` (never spoken),
    `${city}`, `${salary}`, `${location}`, `${qualification}`,
    `${work_experience}` ("Worked before"/"Fresher"), `${work_experience_years}`
- **Tools:** `get_talent_insights`, `update_job_status`, `update_job_details`, `create_job`.
- **Tool payload fixed params (never change):** `sourceService: "ONESTAGENT"`;
  `eventType` per tool (`"UPDATE_JOB"`, `"JOB"`); `app_instance: "up-postjob"` (create_job only).

## Maya — campus recruitment (KKB spinoff)

- **Persona:** *माया, [college_name] की ओर से* — campus recruitment for higher-ed graduates in UP. NOT government.
- **Audience:** college students / recent graduates (fresher-heavy).
- **Languages:** Hindi only.
- **Input variables:** KKB's `${contact_name}`, `${contact_phone}`, `${country_code}`,
  **plus `${college_name}`** (spoken once in intro; fall back to non-college intro if empty).
  Maya does not use `${new_seeker}` — it branches on prior-call memory instead.
- **Recommendations:** KKB's fields **plus optional `hr_contact`** (shared only after a
  successful apply, only if present) and **`benefits`** (surfaced in deep-dive only if present).
- **Tools:** same as KKB (`get_profile`, `create_profile`, `apply_job`, `update_profile`).
- **Divergences (preserve on any KKB sync):** college caller-identity, `${college_name}`,
  `hr_contact`/`benefits`, Experience Capture, HR-number sharing, Marketing Masters League
  fallback, feminine-voice rule.

---

## Re-domaining cheatsheet (porting between agents)

| Source concept | KKB | DKB | Maya |
|---|---|---|---|
| The person on the call | seeker | business owner / employer | student / graduate |
| Phone variable | `${contact_phone}` | (employer phone in payloads) | `${contact_phone}` |
| Job data source | `${recommendations}` (incoming jobs to show) | `${job_role}` etc. (employer's own posted jobs) | `${recommendations}` (+ hr_contact/benefits) |
| Job ID | `recommendations[].job_id` | `${job_id}` | `recommendations[].job_id` |
| Primary action | `apply_job` | `update_job_*` / `create_job` | `apply_job` |
| Insight tool | — | `get_talent_insights` | — |

**Rules when porting:**
- If the source feature references a variable/tool the target has **no equivalent** for,
  **flag it for the user** — do not invent a target variable, tool, or payload field.
- Adapt persona/voice to the target audience (a seeker-facing reassurance line becomes an
  employer-facing one in DKB).
- Place the ported content in the matching section per `prompt-anatomy.md`.
- After applying to the target's Hindi file, run the normal Hindi→Kannada sync (skip for Maya — Hindi only).
- Log the port in the **target** agent's `CHANGELOG.md` with a "Ported from: <source>" line.
