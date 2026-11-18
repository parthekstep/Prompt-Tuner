# KKB on VoicERA + AI DPG: call output (call_output) spec

The post-call report for the Blue Dots job-seeker bot on VoicERA, where the conversation runs on AI
DPG (Agent Core). It replaces Raya's output prompt (`KKB-Slim/KKB Slim Output.md`) for the Hubli
campaign and every later VoicERA campaign. AI DPG has no output prompt and does not produce
`call_output`, so VoicERA's post-call step builds it from two sources:

- **The VoicERA call record:** `call_id`, `call_response`, duration, `custom_variables` (the campaign
  CSV row) and the transcript.
- **The AI DPG telemetry for the call**, found by `session_id = <caller_phone>:<call_id>`:
  - Jaeger `action.execute` spans (`tool_name`) with their child `action.rest_api.http_call` span
    (`http.status_code`).
  - Loki `orchestrator.stream_turn_complete` lines (`next_subagent_id` = the phase the turn routed to,
    `intent`).
  - When the tool service logs at DEBUG, Loki `rest_api_request` / `rest_api_response` lines carry
    each tool's parameters and response body (cut at 2,000 characters).

Read the telemetry 30 to 60 seconds after the call ends. A reference implementation of this whole
step, tested on AI DPG's sample call, is `scripts/voicera_call_output.py`.

The report has two parts. **Part A is computed in code from the records and never by a model.**
**Part B is extracted by a model from the transcript**, with Part A given to it as facts it must not
contradict. The field names match Raya's output wherever the meaning is the same, so the Blue Dots
dashboard reads both.

---

## Part A: computed from the records (code, no model)

A tool call **succeeded** when its `http_call` span has a 2xx status code. Any other status, or a
missing `http_call` span, is a failure. Never decide a tool outcome from what the bot said.

| Field | Rule | Values |
|---|---|---|
| `seeker_name` | `custom_variables.contact_name` from the campaign CSV | text, `"Unknown"` if absent |
| `participant_id` | `custom_variables.participant_id` | text, `"NA"` if absent |
| `call_answered` | `call_response` is `answered` and the transcript has at least one caller turn | `"Yes"` / `"No"` |
| `jobs_fetched` | at least one `fetch_jobs` call succeeded | `"Yes"` / `"No"` |
| `profile_saved` | at least one `save_profile` or `update_profile` call succeeded | `"Yes"` / `"No"` |
| `consent_status` | `"Declined"` if any turn routed to `consent_declined`. Otherwise `"Given"` if a turn routed to `consent` or `consent_reask` and a later turn routed to `profile_setup` or `apply_confirm`, or a `save_profile` that succeeded carried `profile_consent: true`. Otherwise `"NA"` (the consent question was never reached, or the caller had already consented on an earlier call). | `"Given"` / `"Declined"` / `"NA"` |
| `applied_to_job` | at least one `apply_job` call succeeded | `"Yes"` / `"No"` |
| `applications_count` | number of `apply_job` calls that succeeded | integer, `0` if none |
| `jobs_applied` | one object per successful `apply_job`: `{ "job_id": <job_item_id parameter, or "NA" when parameters are not logged> }`, plus `role`, `company_name`, `company_location` when that id appears in a logged `fetch_jobs` result, else `"NA"` | array, `[]` if none |
| `jobs_failed_to_apply` | one object per failed `apply_job`: same fields plus `"failure_reason": "HTTP <code>"` (add the response `message` when logged) | array, `[]` if none |
| `phases_visited` | the distinct `next_subagent_id` values, in first-seen order, comma-separated | text, `"NA"` if none were logged |

`jobs_applied` and `jobs_failed_to_apply` are exclusive: a job either succeeded or failed.

---

## Part B: extracted from the transcript (model)

Give the model: the transcript (caller and agent turns in order), the campaign CSV values, the Part A
values, and the job list from logged `fetch_jobs` results if there is one. Then use the instructions
below as its prompt.

> Analyse the call transcript and extract the fields below. The conversation may be in Hindi or
> Kannada. Extract only what is in the transcript. Never infer, never guess, never invent a name,
> place, company or salary. Use `"NA"` for a missing string and `0` for a missing count.
>
> **The facts you are given (applied_to_job, consent_status and the rest of Part A) come from the
> system's own records. Never contradict them.** If the agent said "your application has been sent"
> but `applied_to_job` is `"No"`, the application was not sent.
>
> 1. **call_engaged**: did the caller take part beyond a word or two? `"Yes"` if they had three or
>    more turns with real content, `"No"` otherwise.
> 2. **call_language**: the language the caller spoke: `"Kannada"`, `"Hindi"`, `"English"`, `"Other"`.
> 3. **primary_topic**: `"Job search"` if the call was about finding work, `"Profile update"` if the
>    caller mainly gave or changed their details, `"Services"` if it was mainly about a support
>    service, `"No engagement"` if it never got past the greeting.
> 4. **jobs_interest**: at the start, did the caller say they want work? `"Yes"` (they want work,
>    named a trade, or asked what there is), `"No"` (a clear no: not looking now), `"Unclear"` (no
>    real answer).
> 5. **jobs_shown**: did the agent describe at least one job aloud? `"Yes"` / `"No"`.
> 6. **jobs_offered_count**: how many different jobs the agent described aloud across the call.
>    Count jobs spoken, not jobs returned by the search. Integer.
> 7. **job_roles_offered**: the job roles the agent spoke, comma-separated, in English (for example
>    `"Welder, Welder Helper"`). `"NA"` if none.
> 8. **job_no_match**: `"Yes"` if, by the end of the call, the caller had been told there was no job
>    for what they wanted and no suitable job was described; `"No"` if at least one suitable job was
>    described at any point, even after an earlier search found nothing (for example "nothing in
>    Dharwad" and then jobs in another city the caller agreed to); `"NA"` if jobs never came up.
> 9. **applied_job_matches_choice**: when `applied_to_job` is `"Yes"`: did the job the agent said it
>    applied to match the job the caller chose? Compare the company and role in the agent's
>    confirmation line with the job the caller asked to apply for. `"Yes"`, `"No"` (a different
>    company or role), or `"NA"` when nothing was applied or the caller never named a choice.
> 10. **preferred_location**: a place the caller said they want to work, in their own words, in
>     English letters (for example `"Hubli"`, `"Vidyanagar, Hubli"`). Only what the caller said or
>     clearly agreed to aloud. Never from the CSV, a job's location or the stored profile. `"NA"` if
>     none.
> 11. **preference_mismatch_reason**: if the caller turned the jobs down: `"Location"` (too far, wrong
>     city), `"Role"` (not the work they want), `"Salary"`. `"NA"` if they did not turn them down, or
>     applied, or gave no reason.
> 12. **services_pitched**: did the agent offer a support service (training, counselling, placement
>     help)? `"Yes"` / `"No"`.
> 13. **service_interest**: the caller's answer to that offer, from the caller's words only: `"Yes"`
>     (a clear yes, or a yes and a time for the callback), `"Maybe"` (only "हाँ"/"ಹೂಂ"/"ok" with
>     nothing after it, or no answer), `"No"` (a refusal; the last answer wins), `"NA"` if no offer.
> 14. **service_callback_slot**: the time the caller named for the service team to call:
>     `"Morning"`, `"Afternoon"`, `"Evening"`, `"Anytime"`, `"Other: <their words in English>"`,
>     `"NA"`.
> 15. **service_offered**: the organisation the agent named in the offer, exactly as spoken. `"NA"`
>     if none was named.
> 16. **call_later_request**: did the caller ask to be called back later? `"Yes: <the time they
>     named, in English, or 'no time given'>"`, or `"NA"`. Only the caller's own request counts.
> 17. **drop_reason**: why this answered call did not end in an application. `"NA"` when
>     `call_answered` is `"No"` or `applied_to_job` is `"Yes"`. Otherwise exactly one of:
>     - `silent_user`: the caller said almost nothing (three words or fewer).
>     - `early_hangup`: the caller showed some interest but the call ended with no clear outcome (no
>       application, no refusal, no rejection of the jobs, no failure). Use this when nothing else
>       clearly fits and the caller was not silent.
>     - `bot_didnt_understand`: the agent kept asking the caller to repeat, or answered something
>       they did not say.
>     - `profile_collection_loop`: the agent got stuck asking for details (name, age, place) and the
>       caller gave up before a job was discussed.
>     - `no_matching_jobs`: the caller clearly turned the jobs down (place, pay, kind of work), or was
>       told there was nothing for them.
>     - `apply_failed`: the caller wanted to apply and the application did not go through (see
>       `jobs_failed_to_apply`), or the agent never started it.
>     - `user_declined`: the caller clearly said no (not looking, not now, later), or refused
>       consent.
>     - `language_mismatch`: the caller wanted another language, or spoke one the agent could not
>       handle.
>     - `other`: none of the above. This should be rare.
>     When several apply, pick the one the call ended on.
> 18. **final_summary**: two or three factual sentences in English: whether the caller wanted work,
>     which trade, place and pay were discussed, and whether they applied (and to which job). No
>     opinions.

---

## Output

One flat JSON object with every field from Part A and Part B, in this shape. The values below show
the format only; never copy them.

```json
{
  "seeker_name": "<from CSV>",
  "participant_id": "<from CSV>",
  "call_answered": "Yes",
  "call_engaged": "Yes",
  "call_language": "Kannada",
  "primary_topic": "Job search",
  "jobs_interest": "Yes",
  "jobs_fetched": "Yes",
  "jobs_shown": "Yes",
  "jobs_offered_count": 2,
  "job_roles_offered": "<role>, <role>",
  "job_no_match": "No",
  "consent_status": "Given",
  "profile_saved": "Yes",
  "applied_to_job": "Yes",
  "applications_count": 1,
  "jobs_applied": [
    { "job_id": "<id>", "role": "<role>", "company_name": "<company>", "company_location": "<place>" }
  ],
  "jobs_failed_to_apply": [],
  "applied_job_matches_choice": "Yes",
  "preferred_location": "NA",
  "preference_mismatch_reason": "NA",
  "services_pitched": "No",
  "service_interest": "NA",
  "service_callback_slot": "NA",
  "service_offered": "NA",
  "call_later_request": "NA",
  "drop_reason": "NA",
  "phases_visited": "profile_resolve, job_match, job_details, consent, profile_setup, apply_confirm",
  "final_summary": "<two or three sentences in English>"
}
```

## Rules

- Use these field names exactly. `"NA"` for empty text, `[]` for empty lists, `0` for empty counts.
- Tool outcomes (`applied_to_job`, `applications_count`, `jobs_applied`, `jobs_failed_to_apply`,
  `profile_saved`, `jobs_fetched`) come from the telemetry only, never from what the agent said.
- `drop_reason` is `"NA"` whenever the call was not answered or an application succeeded. A failed
  application with a caller who stayed on the line is `apply_failed`.
- `final_summary` is always in English.

## The funnel

| Stage | Field |
|---|---|
| Answered | `call_answered = "Yes"` |
| Wants work | `jobs_interest = "Yes"` or `"Unclear"` |
| Jobs heard | `jobs_offered_count > 0` |
| Consent | `consent_status = "Given"`, or a returning caller who already consented (`consent_status = "NA"` with `applied_to_job = "Yes"`) |
| Applied | `applied_to_job = "Yes"` |
| Why not | `drop_reason` on every answered call that did not apply |

On AI DPG the consent question comes after the caller picks a job (it is asked only when it is
needed), so "jobs heard" comes before "consent" in this funnel, unlike on Raya.

## Not carried over from Raya's KKB-Slim output

The AI DPG flow does not ask these, so they are left out rather than always `"NA"`:
`ready_for_interview`, `nearest_landmark`, `pin_code`, `home_area`, `input_location_had_jobs`,
`asked_job_location`, `service_need_matched`, `user_intent`. `jobs_recommended` is replaced by
`jobs_offered_count` and `job_roles_offered`, because AI DPG does not log which search rows were read
out.
