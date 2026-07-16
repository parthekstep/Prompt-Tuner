# Section Checklists

What a conversation prompt **must contain** to be safe to run. A missing critical section is a
top-severity flag. Two parts: (1) use-case archetypes with their required sections, (2) the
universal rule checklist that applies to every voice agent here.

Match sections by **intent, not exact heading string** (agents name them differently — see
`../update-prompt/reference/prompt-anatomy.md`). "Critical" = its absence causes a live failure
or a safety/compliance gap.

---

## Part 1 — Use-case archetypes

Pick the closest archetype (or combine). State which one you matched and why.

### Universal core (every voice agent, all archetypes)
Critical:
- **Identity & persona** — name, role, audience, tone; **modality** (inbound vs **outbound**) stated.
- **Core voice rules** — one-question-per-turn, short responses, acknowledge-then-proceed.
- **Input variables** — declared, with presence/"Not Available" rules; `${...}` names never localized.
- **Conversation pipeline / phase structure** — ordered, with entry conditions.
- **Language & script rules** + **TTS normalization** (numbers/money/date/time/phone as words).
- **Prohibited language** — including a domain **banned→preferred vocabulary list** (not just abstract "simple words").
- **Guardrails** — forbidden topics, dignity/safety, eligibility/age hard-stop, relevance + functional-sanity.
- **Tool section** — every tool used is **declared** here (referenced-but-undeclared = flag), with exact payloads, fixed params, and enum lists (English/Latin).
- **Graceful exit / closing** — a fixed closing script consistent with the modality.
- **Memory-injection block** — `### Contact context / {${contact_memory}}` **iff** memory is enabled.
- **Few-shot examples** — present, and they model the **mandatory** flow (don't skip gated steps).

### Archetype: Outbound data-collection / profiling bot
*(the Purple Dots disability-needs bot; any bot that calls a user, fetches a profile, collects/verifies fields, and connects them onward)*
Add, and treat as critical:
- **Opening consent gate** (recording/data) — asked once; **hard-stop on decline** with no tool calls.
- **Silent profile fetch** — gated behind consent; not announced; name confirmation from the fetched record.
- **Profile completion/verification** — field-by-field, single-question, with skip-if-already-correct.
- **Mandatory-but-silent terminal tool sequence** (update → match/search → connect) with:
  - a **must-run gate** per step, and a **"do not close the call before <terminal tool> (or the decline path)"** gate (C1);
  - **cascade awareness** — downstream phases gated on an upstream tool must note the upstream miss risk.
- **Second consent gate** (share/hand-off) — distinct from the opening consent; asked **exactly once** even when N downstream records exist (B1).
- **Uncertain-user framework** — how to guide someone who can't name their need (open, in-context questions; no forced mapping).
- **Scope boundaries** — explicit list of what the bot must never promise/do/simulate.
- **Voice-gender rule** — if the persona has a gender, an explicit verb-form rule (D4).

### Archetype: Job-matching / recommendation bot (KKB, Maya)
Add, and treat as critical:
- **`new_seeker` (or equivalent) branch** — new vs returning caller drives fetch-vs-create; no re-fetch at action time.
- **Reading the fetched profile** — a "reading the response" section: field map, most-recent-record rule when the response is an array, and "present ⇒ known ⇒ never re-ask"; the profile is actually *used* (address by first name, confirm role) not fetched-and-ignored (C6); the record's `id` is bound as the reusable `profile_id` and the create path is forbidden when a profile was found (C7).
- **Recommendation presentation flow** — steps for 1/2/3+ options; company/role/location/salary spoken format; results **ranked by the caller's known signals** (role → location → salary), not raw array order, with an orient/overview turn when the target role is unknown (C8).
- **Primary action (apply) + success/failure handling** — bridge line spoken **once** (B1); silent tool call; single result.
- **Post-action info gathering / profile update** (if the agent completes profile after the action).
- **Introduction priority rule** — opening line chosen from prior-call memory state.
- (Maya) its divergences: campus identity/`${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing, Marketing Masters League, feminine voice.

### Archetype: Employer / verification & capture bot (DKB)
Add, and treat as critical:
- **Turn-based introduction** (1–3 turns) and **phase-entry routing** on whether records already exist.
- **Freshness / completeness phases** — per-record internal tool discipline ("call <tool> for every record before proceeding").
- **Consent-gated create** — never create before explicit consent; never skip the insight/lookup step.
- **Market/insight delivery** — data logic separate from phrasing.

---

## Part 2 — Universal rule checklist (run on every prompt)

Tick each; flag misses. (Each ties to a pattern in `bug-patterns.md`.)

**Flow & gates**
- [ ] Every "mandatory" step has a **negative gate** on its competing action (A1).
- [ ] Skip logic (SKIP-AHEAD/ORDER-FLEX/"move silently") is balanced by a never-skippable list (A2).
- [ ] No two sections capture overlapping content without a sharp distinction + independent gate (A3).
- [ ] No header/body or intra-branch contradiction (A4).
- [ ] Adjacent askable steps have an explicit wait / separate-turn boundary; no two questions fused into one turn (A7).

**Repetition**
- [ ] Every consent/bridge/confirmation line is bounded to **"ask/say once"** (B1).
- [ ] Nothing human-facing sits inside a "for each <record>" loop (B1).
- [ ] Background tool calls are marked silent; no fetch/waiting narration allowed (B2).

**Tools & payloads**
- [ ] Every tool/sheet **named in the body is declared** in the tool section (C2).
- [ ] Terminal/background tool calls have must-run + "don't close before terminal tool" gates; cascades noted (C1).
- [ ] Every payload value traces to a source; coordinate order is `[lng, lat]`; field names match schema exactly (C3).
- [ ] No `${...}` with unbalanced/stray brackets; no hardcoded id contradicting a dynamic search (C3).
- [ ] All fixed params present & unchanged; all enum fields constrained to exact English/Latin allowed values (C4).

**Language, script & voice**
- [ ] A concrete **banned→preferred vocabulary list** exists (not just "use simple words") (D1).
- [ ] TTS section present AND examples obey it (words for numbers/money/date/time/phone) (D2).
- [ ] Script boundary stated: Devanagari for TTS, English/Latin for payloads + transliteration rules (D3).
- [ ] If persona is gendered, an explicit verb-form rule; no mixed/opposite forms in any line (D4).
- [ ] If outbound: a closing script + a ban on "call me/us back" phrasing (D5).

**Examples, consent, guards, memory**
- [ ] Examples model the mandatory path; greetings match the canonical one; no garbled text; names localized (E1).
- [ ] When a control variable (e.g. `new_seeker`) selects the opening/path, every example is labelled with its value and no example's opening can bleed onto the other branch; re-test the other branch after adding an example (E1).
- [ ] Each distinct consent gate asked once, with a clean decline hard-stop; distinct consents kept distinct (E2).
- [ ] Memory-injection block present verbatim iff memory enabled (else flag Verify) (E3).
- [ ] Guard sections all present: forbidden topics, dignity/safety, eligibility/age, relevance + functional sanity, scope boundaries (E4).

**Cross-language (pointer)**
- [ ] Any change that looks AGNOSTIC is noted for a `/sync-check` against the twin (F).
