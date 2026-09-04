# Two platform asks for LitWiz (Raya) — 2026-09-03

Both block behaviour we cannot fix in the prompt. Each has call ids.

---

## 1. Speak the apply confirmation from the runtime, on a real result

**The bug.** The agent sometimes tells a caller their application went through when `apply_job` was
never invoked. On `19616c90` the only tool call in the whole call was `get_profile`; the caller heard
"अप्लाई हो गया है" and rang off. Rate is roughly **1 call in 7** where an apply is discussed.
Instances: `19616c90`, `29c4f152`, `1fe093a9`, `4b0ea64d`.

**Why it is not fixable in the prompt.** Three mechanisms were tried and each held on several calls
then failed:
1. a positional rule that the success line may only appear in the same turn as the tool result;
2. declaring parentheticals non-speech and marking every tool annotation in the samples;
3. moving the constraint into the `apply_job` tool description (it is there now, 902 chars).

On `29c4f152` and `1fe093a9` the model even emitted a fabricated stage direction —
`*(Silent tool call: apply_job)*` — as spoken text. That string appears in no prompt; what was copied
is the *format* of a tool call, not any wording, which is why no amount of rewording reaches it.

**We checked for a configuration-side fix and there is none.** Enumerated on agent
`115b38a5-42ef-4082-be69-84a871bb226a`: agent fields are `instructions`, `memory_instructions`,
`output_instructions`, `output_fields`, `tools`, `agent_args`, `webhook_url`, voice/timing settings.
Tool entries carry only `type`, `function`, `api_details{url, header, method, payload_template}`.
There is no post-tool or on-success message hook to configure.

**The ask — either would close it:**
- **(a)** let the runtime speak the confirmation when `apply_job` returns success, the way
  `hold_message` is already spoken when a tool is invoked; or
- **(b)** have the runtime refuse/flag an assistant turn containing the success line when no
  successful `apply_job` result exists in that turn.

(a) is preferred: it makes the sentence unfabricatable rather than policed.

**We rejected a workaround rather than risk the core flow.** Making `hold_message` a required
parameter with a single-value enum would tie the "I'm applying now" line to actually invoking the
tool — but if Raya validates enums strictly and the model sends any other string, `apply_job` fails
and applying breaks outright. Not worth it on the most important function in the product.

---

## 2. Surface the tool error reason to the model

**The bug.** The agent cannot tell "you have already applied" from "this failed for a technical
reason", so real duplicates are reported to callers as technical faults (`d6e545d4`, `d401d6cf`) and,
before we gated it, a never-attempted job was called already-applied (`c5a10922`).

**Why.** The model receives only `[Error: apply_job request failed (HTTP 422).]`. The reason —
`ACTION_LIMIT_REACHED`, `TARGET_ITEM_NOT_FOUND` — is in a `__RAYA_TOOL_DEBUG__` block written for the
transcript, not given to the model. Proven across 10 calls. Both causes return 422, so status alone
cannot separate them either.

The other two possible sources are also closed: `contact_memory` is empty on the calls where it
matters, and `get_profile` does **not** return the caller's applications (verified on `d6e545d4` —
its only non-profile item was an unrelated draft job posting the test number owns as a provider).

**The ask — any one of:**
- pass the response body's `error` / `message` fields to the model with the tool result; or
- return distinct HTTP statuses per cause; or
- include an applications list in `get_profile`.

Until one lands, the owner's three-outcome spec (already-applied / technical / success) is not
achievable, and the prompt is deliberately gated to say the neutral technical line rather than guess.

### 2026-09-04 — this is now measured, not inferred (tracker row 103)

Row 103 ("bot is saying technical issue instead of already applied") was re-opened. The proof that no
prompt change can close it:

**Every named error class produces the same spoken line.** Across all six Signals bots, 2026-09-01 to
2026-09-04, 133 tool errors carrying a named `error` field in the response body:

| error in the response body | events | what the bot said next |
|---|---|---|
| `ACTION_LIMIT_REACHED` | 95 | the generic failure line ("technical issue है") |
| `TARGET_ITEM_NOT_FOUND` | 20 | the same generic failure line |
| `MINOR_ACTION_CHANNEL_BLOCKED` | 13 | the same generic failure line |
| `SOURCE_ITEM_NOT_FOUND` | 2 | the same generic failure line |
| `INVALID_ITEM_STATE` | 2 | no failure line at all (the write was narrated as done) |
| `PROFILE_LIMIT_REACHED` | 1 | the same generic failure line |

**Not one call in 133 produced a line that distinguishes one error class from another**, while the
prompt names `ACTION_LIMIT_REACHED` in five separate places and the `apply_job` tool description
carries the mapping. Over the same window the model demonstrably reads *successful* tool results — it
speaks names, roles, ages and locations out of `get_profile` on every call. So it is not that the
model ignores the reason; it is that the reason is not in what it receives.

Confirmed again by harness call `row103-hi-postfix` (tester leg `ae2481e6`), run after two prompt
fixes that removed the last two internal contradictions blocking the branch: `apply_job` returned
`ACTION_LIMIT_REACHED` with the message "An active request already exists between these two profiles"
and the bot still spoke the technical line. Row 2's own definition — *"an error with no reason you can
read"* — is the correct branch on every failure while the body is withheld, so the already-applied
branch is **unreachable by construction**, not intermittent.

### It fails in BOTH directions, which is the part that makes it unfixable in prose

Without the reason, the model is choosing between two lines with no information, and it gets both
wrong:

| direction | measurement |
|---|---|
| says **"technical issue"** when the application really was already in place | **45 of 60** `apply_job` calls that returned `ACTION_LIMIT_REACHED`, 2026-09-03/04 (tracker row 103) |
| says **"your application is already in place"** with no evidence for it | **8 calls** in 668, 2026-09-03/04 — `c5a10922`, `49938255`, `fd464bc0`, `c00e7ba5`, `87427928`, `72112c10`, `537549c6`, and `5f0d3671` where the error was `USER_NOT_FOUND` |

The prompt already gates the second direction: row 1 requires either an `apply_job` retry for the
same job inside the call, or `contact_memory.jobs_applied` naming it. Those eight calls satisfied
neither. Every prose tightening we can make on one direction pushes the failure into the other, which
is what happened when we tried it: the fix that made row 1 reachable off the error name produced
`5f0d3671`, and reverting it restored the 45-of-60. There is no wording that resolves a distinction
the model cannot observe.

**One extra thing you should know about inbound:** inbound calls arrive with **empty `agent_args`**,
so `contact_memory` is never present on them. On an inbound bot the evidence gate can therefore only
ever be satisfied by a same-job retry inside the call — memory evidence is structurally unavailable.
Three of the eight are inbound for exactly that reason.

Standing check: `raya/regression/apply_result_integrity.py`, findings `V` (guessed row 1) and
`W`/`W?` (what the model asserted vs what the API said).

**Add to the ask, in priority order:** an applications list on `get_profile` would also close it
(and would let the pre-tool duplicate check work, which is the only path that has ever produced the
line correctly), but passing `error`/`message` through with the tool result is the smallest change
and fixes all six classes at once.

**One of the six is a data problem, not yours:** `MINOR_ACTION_CHANNEL_BLOCKED` ("This participant is
a minor; actions for minors must be completed in the app") fired 13 times, on profiles whose stored
`age` is 18 — a value that looks like a default rather than a real age (`a5547492` age 18, caller
said 28 on `af52d37c`). Any caller carrying that default can never apply by phone, and today they are
told "technical issue" and then offered more jobs that fail identically. That one is for the data
team.

---

## What we did on our side

- Gated the already-applied line on citable evidence, so the agent can no longer invent it
  (`e654b215`, `a5a68701`: three failing applies, no false duplicate claim).
- `raya/regression/apply_result_integrity.py` check Z detects every fabricated success, and
  `fleet_report.py` treats it as blocking — the fleet reads FAIL while ask 1 is open, by design.

---

## A fourth prompt attempt we considered and rejected

The obvious next move is to **invert the default**: instruct that unless a successful `apply_job`
result is visible in this turn, the line the agent says is the technical-issue line. That is
mechanically different from the three attempts above — it changes which output is the fallback rather
than forbidding the wrong one — so it is not merely a fourth wording.

We are not doing it, because **its downside is symmetric with the bug it fixes.** If the model fails
to "see" a result that did arrive, it tells a caller their application failed when it actually
succeeded. That caller re-applies (and hits `ACTION_LIMIT_REACHED`, which we cannot explain to them
either) or gives up on a job they already hold a live application for. Trading a false success for a
false failure is not an improvement; it just moves who gets hurt.

This is why the ask is a runtime one. The runtime is the only place that knows, with certainty,
whether the write happened — and a confirmation spoken from that knowledge cannot be wrong in either
direction. Everything a prompt can do here is a guess about what the model can see.
