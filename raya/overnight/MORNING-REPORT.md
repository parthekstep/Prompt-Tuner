# Overnight report — 2026-09-03, 06:10 IST

## Fixed and verified by call

| bug | bot(s) | proof |
|---|---|---|
| Location: bot spoke the profile's place, not the campaign's | KKB hi + kn Signals | 2a6ccc0b, 62dc3ee7 (दिल्ली) · 1119c329, af1c6e2a (ಹುಬ್ಬಳ್ಳಿ) |
| "Job posting expiring" told to NEW providers (sheet row 105) | DKB hi + kn Signals | 2c197514, b1b71d68, 9e2e0056 |
| DKB invented role / vacancies / salary / company name | DKB hi + kn Signals | 46812a71, 3f996a3d |
| Relevance filter hid jobs the caller asked to hear | KKB hi + kn Signals | d9bf1f43, 4b0ea64d |
| Location asked though the profile already had it | KKB hi inbound | a6ca5a12, 52ef63d2 |
| "No such job" + hang-up while jobs went unnamed | KKB hi + kn inbound | a6ca5a12, b45a7e22 |
| City slot named one city when jobs spanned two | KKB kn Signals | 8976c120 |
| TRRAIN on the Signals API (no migration needed) | TRRAIN hi + kn | c83fdf8d, 755b73ea |
| Maya: no false "we have <role> jobs" claim | Maya hi Signals | 962f4476, 4882a3c1 |

Earlier the same day: greeting waits (67058058, 7f3aa27d) · role changed without asking
(67058058, 4eed42c8) · consent/data-sharing line before apply (67058058) · read-back is one
question (0178c996, 503440a3) · apply-success not spoken after a failed apply (9cb7e453) ·
Muradnagar / गाज़ियाबाद spellings (0decf61a, 7f3aa27d).

## Open

1. **DKB says "गवर्नमेंट एम्प्लॉयमेंट प्रोग्राम की तरफ से" in 4 places.** Sheet rows 4/56 asked for
   that removal on KKB; it is absent from KKB and Maya but was never checked on DKB. Changing a
   bot's stated identity is a product decision — not touched.
2. **"Already applied" still says the generic line.** Not prompt-fixable: the conversation model
   never receives the tool error body (9 call ids). Needs LitWiz to surface it.

## The pattern worth keeping

Three separate bugs tonight had one cause: **the model could not SEE a value the prompt described.**
Location, DKB's posting fields, and the withheld jobs. Four wordings of a resolution rule failed
before the fix turned out to be printing the value (or substituting the token) at the point of use.
Wording was never the problem in any of them.

## Harness facts established
- Inbound bots ARE testable: PATCH `{"out_did": <INTEGER>}`, then dial the tester.
- The platform DROPS empty-string args; a missing field arrives as an unsubstituted token.
- `contact_memory` sent via agent_args does not reach the model; stored memory cannot be read.
- One tester DID = one call at a time. Keep `caffeinate` running or the machine sleeps mid-sweep.
