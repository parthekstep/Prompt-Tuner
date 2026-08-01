# Regression harness (Tier-3 daily standing check)

The third testing tier (see repo `CLAUDE.md` → "The three testing tiers"): a standing regression that
runs automatically and mails critical findings, so drift is caught even when nobody is looking.

**Cadence (user-chosen 2026-08-01): daily static + weekly live.** Digest → **parth@ekstepplus.org**.

## Daily — static suite (fast, reliable, no telephony)
`python3 raya/regression/static_regression.py` checks EVERY conversation prompt for the failure classes
we've actually hit, and writes:
- `latest-report.md` — human-readable
- `latest-report.json` — machine-readable; the `critical` array drives the email digest

Checks (tuned for precision — a noisy daily email is worse than none):
- **cross-backend leakage** — a Signals prompt carrying a Dhiway contract token (`up-getjob`, `ONEST-AGENT`,
  `*.dhiway` host, …) or a Dhiway prompt carrying a Signals contract token (`item_state`, `lifecycle_status`,
  `educationCategory`, `compliance`, …). Contract-only tokens (never appear in "never-speak-these-fields" bans).
- **phone-doubling** — the `+91${contact_phone}` (Dhiway) / `91${contact_phone}` (Signals) templates that make
  the model double the country code (the CD6 class).
- **memory-injection block** — the verbatim `{${contact_memory}}` must be present.
- **enum-drift** — the byte-exact Signals Phase-2 enums (`ITI / Other Vocational Trainings`, `3-5 Years`, …);
  a wrong enum 400s the write.
- **missing sections** — Graceful Exit; seeker bots need `get_profile`; DKB needs `create_job`.
- **Hindi↔Kannada sync-drift** — header-skeleton parity per pair.

## Weekly — live voice regression (sampled)
A fuller live pass over more bots via the tester agent + the `/voice-test` checklists (generic + bot-specific).
Not daily (one tester = serial calls; 100+ live calls/day isn't feasible). The weekly routine picks a rotating
set of bots, fires the harness calls, grades, and appends live findings to the digest.

## The scheduled routines (cloud — survive the dev machine being off)
Two cron routines run Claude Code in the cloud:
- **daily** (e.g. 06:30 IST): run the static suite → read `latest-report.json` → if any `critical`, email a
  well-formatted digest to parth@ekstepplus.org; else a one-line "all clear" (or silent).
- **weekly** (e.g. Mon 06:30 IST): run the static suite + a sampled live voice regression → email the digest.

Routine prompt (daily): *"Run `python3 raya/regression/static_regression.py` in the Prompt Tuner repo, read
`raya/regression/latest-report.json`, and if `critical` is non-empty, email a well-formatted digest of the
critical + major findings to parth@ekstepplus.org (subject `[Prompt Tuner] Daily regression — N critical`).
If clean, send a one-line all-clear."*
