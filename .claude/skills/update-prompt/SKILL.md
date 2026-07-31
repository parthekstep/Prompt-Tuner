---
name: update-prompt
description: Create or update a voice agent's conversation prompt and keep the language variants in sync. Apply a feedback item or bug fix to an agent (KKB, DKB, or Maya); the change is made on Hindi (source of truth) and mirrored to Kannada — language-agnostic logic copied verbatim, native-language content translated and adapted. Use whenever the user reports a prompt bug, gives feedback on agent behavior, or wants to change what an agent says or does. Also creates a new conversation prompt or a new language variant from scratch.
---

# Update Prompt

Apply a change to an agent's **conversation prompt** and keep Hindi ↔ Kannada in sync.

Resolve files via the path map in the repo root `CLAUDE.md`. Read
`reference/prompt-anatomy.md` (in this skill's folder) for the section taxonomy and the
AGNOSTIC / SPECIFIC / MIXED tags, and the Hindi→Kannada localization conventions.

## Scope

- **KKB, DKB** — Hindi + Kannada. Edit Hindi first, mirror to Kannada.
- **Maya** — Hindi only. No mirror.

## Procedure (update)

**Reconcile against live FIRST — before step 0.** The live Raya agent can be AHEAD of the repo (the
team edits it directly — e.g. the real job inventory / `job_id`s). Run `scripts/raya_deploy.py diff
<agent-target>` (or `/raya-reconcile` if GET is flaky/empty). If **Raya is ahead**, adopt the live prompt
into the repo with `scripts/raya_deploy.py pull <agent-target>` and commit that reconciliation BEFORE
editing — never edit a repo file that is behind live (you would clobber live-only content, e.g. overwrite
a real job inventory with placeholders). `deploy` also refuses any prompt still carrying placeholder
`job_id`s / a `[PLACEHOLDER]` flag. See `raya/README.md → Reconcile-before-fix`.

0. **Snapshot first (rollback safety).** Before editing, checkpoint the target agent:
   `scripts/prompt-version.sh save <agent> pre-<short-change-slug> "<one-line why>"`. This
   captures the current stable files so any edit is instantly reversible via
   `scripts/prompt-version.sh restore <agent> <label>` (see the `/prompt-version` skill).
   Never skip this — it is the safety net for the surgical-edit rule.
1. **Sync first.** Run the `/sync-check` procedure for the target agent (read its
   `SKILL.md`). If the Hindi/Kannada pair has drifted, reconcile it before applying the new
   change, so the change lands on an aligned base. (Skip for Maya — Hindi only.)
2. **Locate the change.** From the user's feedback/bug, identify the agent and the target
   section(s) using the anatomy. Read the relevant section in the **Hindi** file (and its
   Kannada twin) before editing.
3. **Edit Hindi (source of truth).** Make the change in the Hindi file, matching the
   surrounding style.
4. **Classify the change** using the anatomy tags:
   - **AGNOSTIC** (logic, conditions, variable names, tool payloads, structure) → will be
     copied verbatim.
   - **SPECIFIC** (spoken lines, examples, number-words, tone markers) → will be translated
     and adapted to Kannada idiom/script.
   - **MIXED** → split: copy the rule verbatim, adapt the quoted speech.
5. **Mirror to Kannada.** Apply the classified change to the Kannada file: verbatim for
   AGNOSTIC; translated/adapted for SPECIFIC, following the localization conventions
   (Kannada script, Kanglish, Kannada number-words, local place names) and matching the
   existing Kannada section's phrasing.
6. **Maya gate (KKB changes only).** If the agent is **KKB** and the change touches shared
   core logic (anything Maya inherits), **stop and ask** the user whether to also apply it to
   Maya Hindi. If yes, apply it while preserving Maya's divergences (college identity,
   `${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing,
   Marketing Masters League, feminine-voice rule — see `CLAUDE.md`). Never overwrite those.
7. **Changelog.** Append an entry to `<Agent>/CHANGELOG.md` (date, feedback/bug, change,
   files touched). If Maya was also updated, add an entry to `Maya/CHANGELOG.md` too.
8. **Feedback loop (bug fixes only).** If this change fixed a bug, teach `/prompt-analyser` to
   catch it next time: add or sharpen an entry in
   `../prompt-analyser/reference/bug-patterns.md` (symptom → root cause → detection heuristic →
   fix direction → source agent + date), and update
   `../prompt-analyser/reference/section-checklists.md` if the bug implies a section that must
   always exist. See `CLAUDE.md` → "Bug-fix feedback loop". Skip for pure feature additions.
9. **Report.** Summarize what changed in each file, the classification used, and a
   structural-parity note (confirm Hindi/Kannada section skeletons still align). For MIXED
   changes, show the Hindi line and its Kannada adaptation side by side.

## Procedure (create — new prompt or new language variant)

- **New language variant of an existing agent:** copy the structure of the existing language
  file; keep all AGNOSTIC content verbatim; translate/adapt all SPECIFIC content to the new
  language. Verify section parity against the source.
- **New conversation prompt from scratch:** scaffold from the section taxonomy in
  `reference/prompt-anatomy.md`, filling each section for the new agent's domain. Pull the
  agent's variables/tools/persona from `../port-feature/reference/agent-schemas.md` (add a new
  entry there if it's a new agent). Then create both language files via the new-language-variant
  step above.

## Test before done (MANDATORY — the change is not DONE until tested)

A change is NOT done when the files are edited/deployed — only when it has been TESTED and confirmed working, with overall sanity intact. Never report a prompt/agent change as "done", "fixed", or "confirmed" until you have actually tested it. Where a bot cannot be harness-tested (inbound bots — the tester can only receive, not dial in; or telephony is down), do the best available verification (post-deploy transcript review + static sanity) and explicitly mark the residual VERIFY-PENDING — never claim done/confirmed on an untested change. Revert on any regression (see /prompt-version).

After deploying a conversation-prompt change:
1. **Voice-test the changed bot(s)** with `/voice-test`: exercise the exact scenario the change targets (for a bug, the pre-fix repro; for a wording/feature change, a call that hits the changed path) and confirm the NEW behavior appears in the live transcript — on BOTH language variants where the change is agnostic.
2. **Sanity-check the whole flow** — the change did the intended thing AND broke nothing else (greet → fetch → present → apply → close still work; the sibling language matches).
3. Only then is it DONE. Untestable → best-available verification + mark VERIFY-PENDING (never "done").

## Guardrails

- **Surgical edits only.** Make the smallest change that accomplishes the task; preserve every other line, spoken phrase, variable, tool name, and payload exactly. Prefer additive changes; never reformat or delete unrelated content. The resulting diff should contain only the intended change. See `CLAUDE.md` → "Surgical edits only".
- Hindi is always the source of truth; never let Kannada lead.
- **Instructions/rules are written in English; only the agent's spoken lines are in Hindi/Kannada.** When you add or change a rule, write the prose in English and quote any spoken line (e.g. *Offer line (say once): "एक और मौका…"*). Never write instruction/rule prose in Hindi/Kannada. A section whose rules are in Hindi/Kannada is a bug — rewrite the prose to English and keep only the spoken lines translated. This is why the Hindi and Kannada files share the SAME English instructions and differ only in quoted spoken text.
- Never localize a `${variable}` name, a tool name, or a fixed payload param.
- Never translate-copy an AGNOSTIC change — it must be byte-identical logic.
- Never adapt a SPECIFIC change by pasting Hindi text into the Kannada file.
- When unsure whether something is AGNOSTIC or SPECIFIC, consult the anatomy; if still
  unclear, ask.
