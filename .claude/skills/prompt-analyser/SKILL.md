---
name: prompt-analyser
description: Pre-flight audit of a voice-agent conversation prompt for latent gaps and bug-prone patterns BEFORE it runs live. Detects missing critical sections for the prompt's use case, and flags the recurring failure classes we've learned from past bugs — skipped mandatory steps, one-time actions spoken/asked repeatedly, modality leaks (outbound bot inviting callbacks), hard-Hindi/TTS vocabulary drift, missed tool calls, language/gender inconsistency, and payload/data bugs. Analysis-only by default (flags, does not fix). Use when the user shares a new or edited prompt and asks "what could go wrong / find the gaps / check before we run", when onboarding a new agent, or as a review gate before /update-prompt.
---

# Prompt Analyser

A **read-only pre-flight review** of a voice-agent conversation prompt. Its job is to catch
the gaps that cause live failures *before* a call is placed — the same failure classes we
have repeatedly fixed after the fact in KKB, DKB, and Maya. It **flags**; it does not edit.
Hand confirmed fixes to `/update-prompt` (or `/port-feature` / `/update-memory` /
`/update-output`) separately.

## When to use
- A new or edited prompt is shared and the user wants gaps flagged before running it.
- Onboarding a new agent (may not yet live in the repo — accept a pasted prompt or any path).
- As a review gate ahead of `/update-prompt`, or to triage a batch of reported live issues
  against the prompt text.

## Inputs
- The prompt: a file (resolve KKB/DKB/Maya via the path map in repo `CLAUDE.md`; otherwise any
  path or pasted text) — one language file at a time.
- Optional: reported live symptoms. If given, root-cause each against the prompt first, then
  do the full sweep.
- Optional: the use-case / agent archetype (outbound data-collection, job-matching, employer
  verification, campus recruitment…). If not given, infer it from the prompt and state the
  inference.

## References (read before analysing)
- `reference/bug-patterns.md` — the catalog of failure classes: symptom → root cause →
  **detection heuristic** → fix direction → the past bug it came from. This is the core of the
  skill and the thing that compounds — extend it after every new bug (see "Growing the skill").
- `reference/section-checklists.md` — per-use-case **critical-section checklists** ("what a
  prompt of this kind must contain"), plus the universal language/script/TTS/payload rule
  checklist. A missing critical section is a top-severity flag.
- `../update-prompt/reference/prompt-anatomy.md` — the canonical section taxonomy and
  AGNOSTIC/SPECIFIC/MIXED tags. Use it to name sections precisely and to know what *should* be
  present.
- Repo `CLAUDE.md` — the standing rules a prompt must satisfy (memory-injection block, sync
  rule, surgical-edit expectations, Maya divergences).
- The agents' `CHANGELOG.md` files — the ground truth of what has actually broken before.

## Procedure

1. **Identify use case & inventory sections.** Determine the archetype (state your inference)
   and extract the prompt's section headings. Compare against the matching checklist in
   `section-checklists.md` and the taxonomy in `prompt-anatomy.md`. **Missing critical
   section → flag (high).**
2. **If live symptoms were reported, root-cause each first.** Locate the exact lines that
   produce the behaviour; name the failure class from `bug-patterns.md`. Don't stop at the
   surface rule — check whether an *example*, a *competing action*, or *skip logic* overrides it.
3. **Run the full bug-pattern sweep.** Walk every pattern in `bug-patterns.md` and apply its
   detection heuristic to the prompt. Note every hit, including ones the user did not report.
4. **Run the universal-rules checklist** (language/script, TTS number-words, payload script
   separation, enum integrity, fixed-param integrity, variable-name well-formedness, tool
   declared-vs-referenced, few-shot hygiene, memory-block presence).
5. **Cross-check examples against rules.** Few-shot dialogues are behaviour references — a
   mandatory step that an example skips, or a canonical line an example contradicts/garbles, is
   a real defect (models mimic examples over prose). Flag each mismatch.
6. **Report** (see format). No edits.

## Root-cause lenses (apply to every flag)
These are the "why the stated rule didn't hold" checks that past bugs taught us — a rule can be
present and still fail:
- **Competing action not forbidden.** The prompt says what to DO but never forbids the rival
  action, so the rival wins (Maya Experience-Capture gate). → look for a **negative gate**.
- **One-time action inside a per-entity loop.** A line/consent/tool that should fire once is
  attached to a "for each X" loop → repeated N times (Maya apply-bridge). → look for an explicit
  "exactly once" bound.
- **Silent step with no anchor.** Background tool calls with no spoken cue and no "must run
  before you may proceed / close" gate get dropped (DKB tool-call reinforcement). → look for a
  hard sequencing gate.
- **Skip-forward pressure without backpressure.** Aggressive SKIP-AHEAD/ORDER-FLEX/"move
  silently" logic with no counterbalancing "you must still do X" makes mandatory steps optional.
- **Abstract instruction where a list is needed.** "Use simple words" / "don't repeat" under-
  performs a concrete banned→preferred list or an explicit count.
- **Example overrides prose.** Examples model the shortcut the rule forbids.

## Report format
Lead with the reported symptoms (root-caused), then the proactive findings. Keep it scannable.

```
## Prompt analysis — <agent / file> (<use case>)

### Reported symptoms (root-caused)
- <symptom> → **root cause:** <exact section/lines> · **class:** <pattern> · **better:** <direction>

### Proactive findings
| # | Severity | Section | Failure class | What's wrong | Direction |
|---|---|---|---|---|---|

### Missing / thin critical sections
- <section> — <why it matters for this use case>

### Verify (uncertain — confirm with user)
- <item>
```
Severity: **high** = will cause wrong behaviour or a broken/failed tool call; **medium** =
intermittent/quality; **low** = cosmetic/consistency. Rank high first.

## Guardrails
- **Analysis only.** Never edit the prompt from this skill. Propose directions; the user routes
  fixes to `/update-prompt`. (If they then say "fix these," hand off — do not fix in place here.)
- **Ground every flag in a line.** Quote or cite the exact section; no vibes-based findings.
- **Separate real gaps from expected language differences.** A Kannada spoken line differing
  from Hindi is not a bug (see `prompt-anatomy.md`). Cross-language *logic* gaps are — but note
  this skill reviews one file; use `/sync-check` for the Hindi↔Kannada parity audit.
- **Flag, don't guess.** If you can't tell whether something is deliberate, put it under
  "Verify" and ask.

## Growing the skill (this is how it compounds)
Every time a **new** class of live bug is found — here or via `/update-prompt` — add or sharpen
an entry in `reference/bug-patterns.md` (symptom, root cause, detection heuristic, fix
direction, source agent+date) and, if it implies a section that should always exist for a use
case, update `reference/section-checklists.md`. The changelogs are the feed; this catalog is the
distilled, reusable form.
