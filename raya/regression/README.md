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

## The scheduler — GitHub Actions (`.github/workflows/regression.yml`)
The requirement was "runs even if my system is shut off." The two **local** schedulers can't do that:
`scheduled-tasks` MCP only runs "while this app is open"; `CronCreate` is "session-only, gone when Claude
exits." The only mechanism that survives the dev machine being off is a **cloud** runner — and since this
repo is on GitHub (`parthekstep/Prompt-Tuner`), that's **GitHub Actions**: it runs on GitHub's infra, checks
out the repo, runs the suite with **zero secrets**, and notifies.

- **daily** `7 1 * * *` (06:37 IST) — static suite.
- **weekly** `7 1 * * 1` (Mon 06:37 IST) — static suite (+ live once Raya/Signals secrets are added; see below).
- `workflow_dispatch` — a manual "Run workflow" button in the Actions tab.

Two independent email paths:
1. **Guaranteed, zero-config** — on any critical finding the job **exits non-zero**, so GitHub emails the repo
   owner about the failed run; the run page shows the full digest (`build_digest.py` → job summary + artifact).
2. **Well-formatted HTML via the Gmail API** (`send_digest.py`) — a service account with **domain-wide
   delegation** for `gmail.send` impersonates a sender in the ekstepplus.org domain (same auth model as the
   repo's Sheets service account; no SMTP, no app password). A **no-op until** `GMAIL_SA_JSON_BASE64` is set.

`build_digest.py [daily|weekly]` renders `latest-report.json` into the HTML digest; `send_digest.py` sends it.

### To activate
- **Merge the workflow to `main`** — GitHub only fires `schedule:` triggers from the **default branch**.
- **Gmail-API secrets** (*Settings → Secrets and variables → Actions*):
  - `GMAIL_SA_JSON_BASE64` — base64 of a service-account JSON whose **domain-wide delegation** includes
    `https://www.googleapis.com/auth/gmail.send` (a Workspace **super-admin** enables the scope in the admin
    console → *Security → API controls → Domain-wide delegation*; the existing Sheets SA can be reused if the
    scope is added to it).
  - `GMAIL_SENDER` — address to send as (e.g. `parth@ekstepplus.org`); `GMAIL_TO` — recipient(s).
- **Weekly live** needs the Raya token + Signals keys as GitHub secrets to fire real calls from the cloud
  (they're git-ignored locally by design). Until then the weekly run is static-only.
