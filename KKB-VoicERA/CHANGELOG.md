# KKB on VoicERA + AI DPG: changelog

The Blue Dots job-seeker bot on VoicERA (Hubli campaign first). The conversation prompts live in
AI DPG's config repo, not here: read them with `scripts/dpg_prompts.py` from the export in
`raya/voicera/dpg/` (git-ignored) and send changes to AI DPG keyed by `source`. This folder holds
what we own: the call output spec.

## 2026-11-18 - Call output spec created (no output prompt exists on AI DPG)
- **Feedback/bug:** "VoicEra Blue Dots Hubli Campaign" thread (Amar, 17 Nov): VoicERA's post-call step
  needs the call_output spec (field names, values, drop-reason list). Aniket (17 Nov): AI DPG has no
  output prompt and produces no call_output; compute it from VoicERA's transcript plus AI DPG traces.
- **Change:** new `KKB VoicERA Output.md`, built from `KKB-Slim/KKB Slim Output.md`. Part A (tool
  outcomes, consent, phases) is computed from Jaeger/Loki telemetry, never by a model; Part B is
  model-extracted from the transcript with Part A as fixed facts. drop_reason uses the dashboard's
  9 buckets. New field `applied_job_matches_choice`. Fields the AI DPG flow never asks (PIN,
  landmark, interview readiness and others) are left out. Reference step:
  `scripts/voicera_call_output.py`.
- **Tested:** static only, on AI DPG's sample call `vb-T21-0-0-168782` (17 Nov, test number): Part A
  read the failed then successful save_profile and the successful apply_job (HTTP 201); a model run of
  Part B gave `applied_job_matches_choice = "No"` (caller chose Vishwas Works, application went to
  Ganga Fabricators, the defect AI DPG noted). After that run, job_no_match was reworded (an empty
  first search followed by jobs the caller accepted is "No"). No VoicERA campaign call exists yet:
  **NOT VERIFIED on a live call.**
- **Files:** `KKB-VoicERA/KKB VoicERA Output.md`, `scripts/voicera_call_output.py`,
  `scripts/dpg_prompts.py`
