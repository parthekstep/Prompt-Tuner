---
name: port-feature
description: Carry a feature, section, rule, or behavior from one voice agent's prompt to another — including unrelated agents (e.g. a feature built in KKB extended to DKB or Maya). Re-domains the feature to the target's variables, tools, persona, and audience instead of copying verbatim, applies it to the target's Hindi prompt, then syncs to its Kannada. Use when the user wants to reuse or extend something that exists in one agent across other agents.
---

# Port Feature

Extend a feature from a **source** agent to one or more **target** agents, re-domaining it
to each target's schema. Targets may be unrelated agents (KKB → DKB, KKB → Maya, etc.).

Read `reference/agent-schemas.md` (this skill's folder) for each agent's input variables,
tools, persona, and the re-domaining cheatsheet. Read
`../update-prompt/reference/prompt-anatomy.md` for section placement and tags. Resolve files
via the path map in the repo root `CLAUDE.md`.

## Procedure

1. **Identify** the source agent + the feature (a section, rule, spoken behavior, or flow
   step) and the target agent(s). Read the feature in the source's Hindi file in full.
2. **Map the schema gap.** Compare the variables/tools the feature uses against the target's
   schema (agent-schemas.md). For each:
   - direct equivalent → remap the name (e.g. KKB `recommendations[].job_id` → DKB `${job_id}`);
   - no equivalent → **flag it for the user**; do not invent a target variable, tool, or
     payload field. Pause and confirm how to proceed.
3. **Re-domain the content.** Rewrite the feature for the target's audience and persona (a
   seeker-facing line becomes an employer-facing one for DKB; add Maya's feminine voice for
   Maya). Keep the underlying logic; change only what the domain requires.
4. **Place it correctly.** Insert the re-domained feature into the matching section of the
   target's **Hindi** file per the anatomy. If the target lacks that section, add it in the
   taxonomy-appropriate position.
5. **Sync languages.** Run the `/update-prompt` mirror step for the target: copy AGNOSTIC
   parts to the target's Kannada verbatim, adapt SPECIFIC parts. **Skip for Maya (Hindi only).**
6. **Changelog.** Append to the **target** agent's `CHANGELOG.md` with a
   `**Ported from:** <source agent>` line in addition to the standard fields.
7. **Report.** Show what was ported, the variable/tool remapping table used, any flagged gaps,
   and the files touched per target.

## Test before done (MANDATORY — the port is not DONE until tested)

A change is NOT done when the files are edited/deployed — only when it has been TESTED and confirmed working, with overall sanity intact. Never report a prompt/agent change as "done", "fixed", or "confirmed" until you have actually tested it. Where a bot cannot be harness-tested (inbound bots — the tester can only receive, not dial in; or telephony is down), do the best available verification (post-deploy transcript review + static sanity) and explicitly mark the residual VERIFY-PENDING — never claim done/confirmed on an untested change. Revert on any regression (see `/prompt-version`).

After porting + deploying: **voice-test the TARGET bot** (`/voice-test`) on a scenario that exercises the ported feature, confirm it behaves correctly in the target's own domain/persona, and sanity-check the target's existing flow still works (and its sibling language). Untestable → best-available verification + VERIFY-PENDING.

## Notes

- **English instructions rule:** the ported feature's instructions/rules are written in English; only the target agent's spoken lines are localized. Do not carry over Hindi/Kannada rule prose — re-express the rules in English and quote the (re-domained) spoken lines in the target language.

- **Surgical edits only.** Insert the re-domained feature with the smallest possible footprint; preserve every other line in the target file exactly. Prefer additive changes; never reformat or delete unrelated content. See `CLAUDE.md` → "Surgical edits only".
- Port to one target at a time; repeat for multiple targets so each re-domaining is deliberate.
- Porting INTO Maya is a deliberate, user-requested act — it is not the same as the KKB→Maya
  "flag-and-ask" sync in `/update-prompt`. Here the user is explicitly extending a feature to Maya.
- If the feature depends on a tool the target doesn't have (e.g. KKB has no
  `get_talent_insights`), that is a hard gap — flag it; do not fabricate the tool.
