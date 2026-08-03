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
2. **Well-formatted HTML email** (`send_digest.py`) — multi-provider, auto-detected from whichever secret is
   present. Skipped cleanly (exit 0) when none is set, so the workflow never fails just because email isn't
   wired up. Priority order:

| # | Provider | Secrets | Needs Workspace admin? |
|---|---|---|---|
| 1 | **Gmail API as you** (OAuth refresh token) | `GMAIL_OAUTH_CLIENT_ID` + `_CLIENT_SECRET` + `_REFRESH_TOKEN` | **No** — your own consent |
| 2 | **Resend** HTTP API | `RESEND_API_KEY` | No — no Google at all |
| 3 | **Generic SMTP** (app password, Mailgun, SES…) | `SMTP_HOST/_PORT/_USER/_PASS` | No (app passwords can be org-blocked) |
| 4 | Service account + domain-wide delegation | `GMAIL_SA_JSON_BASE64` | **Yes** — admin must grant `gmail.send` |

`build_digest.py [daily|weekly]` renders `latest-report.json` to HTML; `send_digest.py` sends it;
`test_email.py` does a one-command local end-to-end send using `secrets/*`.

### Recommended setup — Gmail via Google Cloud Console (no admin needed)
The DWD route (#4) requires a Workspace super-admin. The **Cloud Console OAuth** route (#1) needs only your
own consent:

1. **console.cloud.google.com** → pick/create a project (e.g. `operation-rozgar`)
2. *APIs & Services → Library* → enable **Gmail API**
3. *OAuth consent screen* → **Internal** (or External + add yourself as a Test user); add scope
   `https://www.googleapis.com/auth/gmail.send`
4. *Credentials → Create credentials → OAuth client ID* → **Desktop app** → **Download JSON**
5. `python3 raya/regression/setup_gmail_oauth.py ~/Downloads/client_secret_*.json`
   — opens a browser for consent, stores the refresh token in `secrets/gmail-oauth.json` (git-ignored), and
   offers to set the three GitHub secrets via `gh`. The token is never printed.
6. Test end to end: `python3 raya/regression/test_email.py`

`GMAIL_SENDER` / `GMAIL_TO` override the from/to (both default to `parth@ekstepplus.org`).
For Resend without a verified domain, the from-address **must** be `onboarding@resend.dev`.

- **Weekly live** needs the Raya token + Signals keys as GitHub secrets to fire real calls from the cloud
  (they're git-ignored locally by design). Until then the weekly run is static-only.
