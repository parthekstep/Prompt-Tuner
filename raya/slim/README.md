# The slim-prompt experiment

`KKB Placeholder Hindi Signals.md` is **219,519 characters**. The team's target for optimal Raya
performance is **under 50,000**. This directory holds the rewrite, the bot it runs on, and the
tooling that decides whether the rewrite is as good as the original.

## What is here

| file | what it does |
|---|---|
| `extract_spec.py` | pulls the behavioural contract out of a prompt — every distinct spoken line, tool, input variable and payload identifier |
| `compare_spec.py` | diffs two prompts' specs and lists what the slim one dropped, drifted or invented |
| `create_slim_bot.py` | clones a live Raya agent field-by-field, changing ONLY `instructions`, so an A/B measures the prompt and nothing else |
| `ab_compare.py` | dials both bots with the same fixture and persona, alternating, and scores every call mechanically — latency proxy plus nine shared invariants |
| `slim-v1-reference.md` | the first draft, kept so later compression passes can be diffed against it |
| `diff-hi.json` | the machine-readable spec diff |

## The bots

| | uuid | prompt | chars |
|---|---|---|---|
| fat (live) | `115b38a5-42ef-4082-be69-84a871bb226a` | `KKB/KKB Placeholder Hindi Signals.md` | 219,518 |
| slim (A/B) | `140d13ca-c80f-47c4-9454-5edb3fd38c96` | `KKB-Slim/KKB Slim Hindi Signals.md` | 68,744 |

Everything else on the two agents is identical and was verified field by field after creation:
language and voice ids, the whole tool schema, the DID, `allow_interruption`,
`min_user_speech_to_interrupt`, `required_silence_after_speech`, the nudge thresholds,
`max_call_duration_mins`, the webhook, and the memory and output prompts. The slim bot carries no
production traffic.

Two incidental differences worth knowing: Raya **derives `agent_args` from the `${...}` tokens in
the instructions**, so the fat bot has a seventh argument, `college_name`, that KKB does not use
(a stray mention somewhere in the 219k), and the slim bot has only the six real ones. And the
create endpoint rejects `agent_args`, `memory_enabled` and `memory_instructions`, so the clone is
POST-then-PATCH, one key per PATCH — the Zod schema rejects the whole body if any single key is
unrecognised.

## Why it is 68,744 and not 50,000

The 219k is not padding. Measured composition of the original: 10% is provenance prose (call ids,
"this used to say", failure anecdotes), 4.9% is exact duplicate paragraphs, **`# No-Match Fallback`
appears twice** (23,723 chars for one section), and 37% of the file sits in 128 paragraphs of over
400 characters each. Removing all of that — every duplicate, every anecdote, one copy of No-Match,
and rewriting the guard prose as tables and single imperatives — lands at **68,744 (a 69% cut)**
with the contract intact.

Getting from there to 50,000 means removing behaviour, not words. The arithmetic, for the record:

| candidate | saves | leaves | what it costs |
|---|---|---|---|
| both worked calls | 5,754 | 62,990 | the samples are what the model actually follows — analyser D50, D63, D74 all describe a sample outvoting a rule |
| the whole ASR/confirmation section | 2,958 | 65,786 | phonetic confirmation on roles, places, option numbers and experience |
| all Situations | 1,472 | 67,272 | silence, distress, proxy callers, do-not-call, "are you a bot" |
| Canonical Location Spellings | 1,777 | 66,967 | the caller hears a mangled version of their own town |

All four at once still leaves **56,657** — and would have removed the samples, the ASR guards, the
dignity handling and the TTS spellings. So 50,000 is not reachable for this bot's current behaviour
surface. The honest options are to cut behaviour deliberately (an owner decision, with the list
above as the menu) or to accept 68,744.

**And the premise is testable.** The 50k target is a proxy for latency. There is a *measured*
latency cause that has nothing to do with prompt size: `hold_message` is never played during a tool
call — **348 of 348** tool calls across 1,152 calls on all 18 bots had no audio at all for the whole
tool round-trip, 189 of them `get_profile`, which fires at the top of every call (see
`ESCALATION-litwiz.md` §3). So before spending more on characters, `ab_compare.py` should say
whether 68k is measurably faster than 219k at all.

## A/B results — 10 calls, 5 per side, same fixture and persona

Run alternating so line conditions hit both sides.

| | median s per agent turn | turn counts | applies | invariant failures |
|---|---|---|---|---|
| fat, 219,518 chars | **16.00** | 14, 6, 18, 16, 16 | 6 | 7 |
| slim, 68,744 chars | **14.75** | 12, 12, 70, 17, 10 | 4 | 5 |

**A 69% prompt cut bought about 7% per turn.** The fat bot's figure is strikingly consistent across
calls of very different lengths — 16.0, 16.0, 16.5, 16.06, 13.44 — which says the metric is measuring
something real and that the per-turn cost is nearly independent of how long the call is. Slim's set
contains one 70-turn outlier at 4.43 s/turn; excluding it the median is 14.97, so the conclusion does
not rest on it.

That is not the step change a 219k → 50k target implies, and it is consistent with the measured
cause: `hold_message` is never played, so **348 of 348** tool calls sit in silence for a whole API
round-trip whatever the prompt length (`ESCALATION-litwiz.md` §3).

### Quality: the two prompts fail on the same things, at similar rates

Both sides produced the same failure classes. **This corrected a conclusion I had drawn from a single
call.** After the first run I recorded that slim had regressed on speaking payload company names
raw, because slim's `90658584` did it and the fat prompt had got it right on `02c5f7f0`. The second
run's fat call `ea0477f4` then did it **five times in one call** — `SARA ENTERPRISES`, `BayLink`,
`GLOBAL CHEMICALS` — so it is a shared bug of both prompts and not a cost of the rewrite.

| failure | fat | slim |
|---|---|---|
| payload value spoken in Latin | `ea0477f4` (×5) | `90658584` (×3), `f90a0b97` (×1, a salary in digits) |
| ordinals restarted at पहला | `09978532` | `4d6d4d02` (four restarts) |
| introduction spoken twice | `891ff246` | — |
| caller's place substituted in the location sentence | `1450f797` (गाज़ियाबाद) | `8eb83bc2` (साहिबाबाद) |

**What that means for the rewrite.** The 219k of extra prose is not buying adherence on any of the
classes the harness can see. It also is not the *cause* of them: the location substitution and the
company-name leak occur at the same rate on both. Both findings point the same way — these are
mechanism problems (a competing instruction, a rule stated nowhere near the line that consumes the
value), and neither more prose nor less changes them.

The company-name leak has since been fixed the way D71 says to fix this class — the conversion is now
stated **at the point of use**, in the job-presentation format itself, in all 12 KKB/Maya prompts and
in the slim prompt. That is the one place the rule was never stated, despite being stated five times
elsewhere. Both sides need re-dialling to confirm it.

## Running the comparison

```
python3 raya/slim/compare_spec.py "KKB/KKB Placeholder Hindi Signals.md" \
    "KKB-Slim/KKB Slim Hindi Signals.md"

python3 raya/slim/ab_compare.py --selftest
python3 raya/slim/ab_compare.py --pairs 3 \
    --fixture raya/testcases/args/r5/sarjapur-offlist.json \
    --persona raya/personas/hi-detail-then-apply.md
python3 raya/slim/ab_compare.py --score-only
```

`ab_compare.py` alternates fat and slim so line conditions hit both sides, and prints
`FEWER THAN 2 CALLS ON A SIDE — this is not yet a comparison, it is an anecdote` rather than
reporting a median off one call. Its scorer self-tests against four hand-built transcripts,
including the real `7b841e6b` leak.

## Latency baseline, from real traffic

Scored over the fat bot's 7 most recent calls with a measurable turn count: **median 13.4 seconds
per agent turn** (turn counts 12, 2, 3, 2, 5, 13, 4). That is the number the slim bot has to beat.
Same scorer, same fixture, same persona, so the comparison is like-for-like.

## Contract coverage of the slim prompt

`compare_spec.py` reports 181 of the fat prompt's 306 distinct spoken lines kept, 7 drifted and 118
dropped. Every one of the 118 was classified by hand; none is a live agent line. They are:

- **lines the fat prompt quotes in order to FORBID them** — "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ",
  "आपकी जानकारी देख रही हूँ", "ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ", "मैंने report कर दिया है", and
  the deleted "आपके लिए relevant jobs अभी नहीं दिख रहीं…". The slim prompt bans these as classes and
  keeps verbatim only the ones whose exact wording is the failure.
- **quotes of past bugs** — "आप अभी बी०टेक०(ई०सी०एस) का काम कर रहे हैं", "अभी बेंगलुरु के लिए … उपलब्ध
  नहीं हैं", "मुराद नगर, ११००४५ है". Those live in `CHANGELOG.md` and `bug-patterns.md`.
- **caller utterances** from sample dialogues — "और कोई जॉब है क्या", "हाँ अप्लाई कर दो".
- **TTS and canonical-spelling table cells** the extractor reads as speech — "₹५००/day", "सेक्टर पाँच".
- **Kannada lines** cited from the twin's bugs.

Two real drops were found by grep after the spec diff and restored: **"पक्का call आएगा"** and
**"selection हो जाएगा"**, both named bans. Naming the exact wrong string is what makes a ban stick,
so they are quoted rather than paraphrased.

The extractor had a bug worth knowing about: it originally paired quotes across the whole file, so
one stray unmatched quote shifted every pairing after it and **three spoken lines that were present
in the slim prompt were reported as dropped**. It now scans per block (a run of `> ` lines, or a
single line), so a stray quote can only corrupt its own block.

## Known open item in both prompts

The location sentence's caller-place slot is **not prose-fixable** and the slim prompt carries the
same conflict as the fat one, deliberately, so the A/B measures size rather than a behaviour change.
Three wordings have failed: `a899617e` spoke the PIN as a quantity, `7b841e6b` and `a5ba6894` read
the raw Latin value, and `1450f797` substituted the jobs' city for the caller's place. See
`KKB/CHANGELOG.md` (2026-09-08, later entry) and `ESCALATION-data-team.md` §5.
