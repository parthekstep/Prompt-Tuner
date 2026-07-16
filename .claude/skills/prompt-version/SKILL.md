---
name: prompt-version
description: Save, list, diff, and restore version snapshots of an agent's prompts so you can roll back to a last-stable copy without relying on git commits/pushes. Use when the user wants to checkpoint a stable prompt version before risky edits, roll back a change that broke an agent, compare the current prompt against an earlier snapshot, or mark a durable stable point. Backs the "we don't push every change to git instantly" workflow. Pairs a local file-snapshot store (versions/) with git tags for durable markers.
---

# Prompt Version History

Lightweight version history for the Prompt Tuner prompts, so a known-good version is always one command away — independent of git pushes. Two layers ("Both"):

1. **File snapshots** (primary, git-independent) — full copies of an agent's prompt files under `versions/<Agent>/<stamp>__<label>/`. Instant, visible, restorable. `versions/` snapshot bodies are git-ignored (local safety net); the per-agent `HISTORY.md` logs are tracked.
2. **Git tags** (durable markers) — annotated tags on committed stable points, shareable via git.

All operations go through `scripts/prompt-version.sh` (run from the repo root).

## Commands

```
scripts/prompt-version.sh save    <agent> <label> [note...]   # snapshot current prompts
scripts/prompt-version.sh list    [agent]                     # list snapshots
scripts/prompt-version.sh diff    <agent> <label> [file]      # current vs a snapshot
scripts/prompt-version.sh restore <agent> <label>            # roll back (auto-saves current first)
scripts/prompt-version.sh tag     <agent> <label> [note...]   # git tag the current HEAD
```

- `<agent>` ∈ `KKB | DKB | Maya` (case-insensitive).
- `<label>` is a short kebab slug: `stable-2026-07-15`, `pre-inbound-build`, etc.
- A snapshot copies every `*.md` in the agent's dir **except `CHANGELOG.md`** (history, never restored).
- `restore` auto-snapshots the current state first (`pre-restore-<stamp>`), so a rollback is itself reversible.

## When to use

- **Before any risky/large edit** — `save <agent> pre-<change>` to set a rollback point. `/update-prompt` does this automatically (see below); do it manually before hand-edits or big refactors.
- **A change broke the agent** — `list <agent>`, then `restore <agent> <label>` to the last good snapshot.
- **Compare** — `diff <agent> <label>` to see exactly what changed since a snapshot.
- **Mark a durable stable point** — once a stable state is committed, `tag <agent> stable-<date>` (or a repo-wide `git tag`).

## Convention

- Label a genuinely-verified-good version `stable-<date>`; label a rollback point taken before edits `pre-<change>`.
- Note the *why* in the `[note...]` — it lands in `versions/<Agent>/HISTORY.md`.
- Snapshots are cheap; take one whenever you're about to do something you might want to undo.
