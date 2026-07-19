# raya/ — Agentic deploy to Raya Voice AI

This directory configures `scripts/raya_deploy.py`, which pushes the local prompt
files into the live voice agents on **Raya Voice AI** (LitWiz Labs, getraya.app)
over Raya's REST API — always against a verified-correct agent/URL.

Prefer the **`/deploy-prompt`** skill for day-to-day use; it wraps the tool with
the sync-check gate, snapshots, diffs, confirmation, and read-back verification.

## Files

| File | Tracked? | What |
|---|---|---|
| `agents.json` | yes | **The source of truth** — explicit file → Raya agent-ID manifest. Never inferred from filenames. |
| `endpoints.json` | yes | API shape (endpoints, auth, prompt-field). **No secrets.** Fill CAPITALISED placeholders from Raya's docs. |
| `.env.example` | yes | Keys for `raya/.env`, empty values. |
| `.env` | **no (git-ignored)** | Real base URL + token. Never commit. |
| `deploy-history.md` | yes | Append-only log of what went live, when, and the rollback snapshot. |

## Setup (once)

1. `cp raya/.env.example raya/.env` and fill `RAYA_BASE_URL`, `RAYA_API_TOKEN`, `RAYA_ENV`.
2. Fill the CAPITALISED placeholders in `endpoints.json` from the Raya REST API docs (checklist below).
3. `scripts/raya_deploy.py list` → copy each agent's ID into the matching `raya_agent_id.<env>` in `agents.json`.
4. `scripts/raya_deploy.py verify --all` → confirms every mapped URL resolves and the live agent name matches its guard.

## Commands

```
scripts/raya_deploy.py targets [--check]        # print the manifest; --check errors on missing deploy:true files (LOCAL, no network)
scripts/raya_deploy.py list                      # GET Raya agents so you can fill agents.json
scripts/raya_deploy.py verify [<target>|--all]   # resolve URL + GET each target; confirm it exists + name matches (READ-ONLY) — the "right URL" gate
scripts/raya_deploy.py diff   <target>|--all     # unified diff: local file vs live remote prompt (READ-ONLY)
scripts/raya_deploy.py status [--all]            # per-target: in-sync | drifted | unmapped | missing-file | unreachable
scripts/raya_deploy.py deploy <target>|--all     # GATED write path: snapshot → GET backup → name guard → diff → confirm → PUT → read-back
```

`<target>` = a manifest `id` (`kkb-hi-in`), a file basename, or an `agent[:lang][:dir]`
selector (`kkb`, `dkb:kn`, `kkb:hi:inbound`). `deploy` requires an interactive
confirmation (type the target id) unless `--yes` is passed after a human has approved.
`deploy --all` stops on the first failure — never a silent partial batch.

## Safety

- **Secrets never committed** — `.env` is git-ignored; `agents.json`/`endpoints.json` hold no secrets.
- **Explicit mapping, never filename inference** — the #1 wrong-URL risk (`KKB Placeholder Inbound.md` is *Hindi*).
- **Every deploy**: auto-snapshot (`prompt-version.sh save`) → GET current remote (a backup of what you're about to overwrite) → name guard → dry-run diff → confirm → PUT → **read-back verify** (remote must byte-equal local).
- **Rollback**: `scripts/prompt-version.sh restore <agent> <pre-deploy-label>` (auto-snapshots current first) → `scripts/raya_deploy.py deploy <target>`.
- **Staging vs prod** is selected by `RAYA_ENV`. Test the voice harness against **staging**, never a production line — the prompts fire live backend writes (`create_profile`/`apply_job`).
- **Sync gate**: never deploy one language of a drifted KKB/DKB pair — run `/sync-check` first (the `/deploy-prompt` skill does this).

## API details to get from LitWiz (fills `endpoints.json`)

- **Base URL(s)** — prod and **staging/sandbox** (staging is required for voice testing).
- **Auth** — Bearer token vs API-key header; exact header name; how the token is scoped/rotated.
- **List agents** — endpoint + method; response shape: where the array lives (`list_items_path`), the id field (`item_id_field`), the name field (`item_name_field`); pagination?
- **Get agent** — endpoint + method; **does a GET return the current live prompt?** (needed for verify/backup/diff); where the object sits in the response (`get_item_path`); which field (or dotted path) holds the prompt (`prompt_field`).
- **Update** — endpoint + method (PUT/PATCH); **replace vs patch** (`update_mode`); required fields on update; UTF-8/Devanagari+Kannada safety; max prompt size (largest file ≈ 84 KB → set `request.max_prompt_bytes`).
- **Topology** — are inbound/outbound and Hindi/Kannada **separate agent objects/IDs**? How are phone numbers bound to agents?
- **Post-call prompts** — where do **Memory/Output** prompts live (separate fields/objects, or not in Raya)? Until confirmed, those 6 targets stay `deploy:false`.
- **Ops** — rate limits; idempotency-key support; does Raya keep its own prompt version history?
