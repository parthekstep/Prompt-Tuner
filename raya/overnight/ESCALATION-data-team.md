# Two data-side blockers found in production traffic — 2026-09-04

Neither is a prompt bug. Both are currently experienced by real callers as the bot saying something
useless or wrong, and neither can be fixed in the prompt.

---

## 1. `age: 18` looks like a default, and the Signals API blocks applies for minors

**What happens.** `apply_job` returns `422 MINOR_ACTION_CHANNEL_BLOCKED` — *"This participant is a
minor; actions for minors must be completed in the app and can't be performed via this channel."*
The caller is then told "technical issue", and because the bot cannot read the error reason (see
`ESCALATION-litwiz.md` §2) it goes on to offer more jobs, every one of which fails identically. On
`a5547492` the caller sat through two full apply attempts, both blocked, both reported as a technical
fault.

**Why it looks like a data default, not real ages.** 13 occurrences across 2026-09-01→04, all on
profiles whose stored `age` is exactly **18**. Three unrelated inbound callers the same day —
`b48f70fb`, `2d8b7cb1`, `a5547492` — all carry `age: 18`. On `af52d37c` the stored age was 18 and the
caller said on the call that she is 28. A real 18-year-old is also not a minor, so either the stored
value is a placeholder or the backend's minor test is not reading age at all (there is no
`dateOfBirth` on these profiles).

**The ask.** Confirm what populates `age` on profile creation, and whether the minor check reads
`age` or a DOB we are not sending. If 18 is a default fill, every caller carrying it is permanently
unable to apply by phone and we are telling them it is a glitch.

---

## 2. The campaign is sending full postal addresses in `location`

**What happens.** 272 of today's outbound calls were dialled with a `location` argument holding a
complete postal address rather than a city — e.g.

    183, Maharajpur, Sahibabad Industrial Area, Ghaziabad, Uttar Pradesh - 201010 Ghaziabad
    ( Municipal Corporation ), Tehsil- Ghaziabaad, District- Ghaziabad, Uttar Pradesh, Pin Code-201010

**Two consequences.**
1. The prompt's job is to read that location back for confirmation. A 200-character address is not
   speakable, so the bot either has to reduce it to a city itself or fall back to asking openly —
   which is the very complaint that produced tracker rows 106/108. (The prompts now say to speak only
   the town/city part, which mitigates it; it does not fix the input.)
2. Every location detector we have matches the argument against the job cities, so an address that
   *contains* "Ghaziabad" scores as "no job in this location". 271 of today's `C MISMATCH NOT NAMED`
   findings are that, not bot behaviour. It hides real findings in noise.

Stored profile locations have the same shape — `b48f70fb`'s profile location is
`VILL-MURARI TAND KAKO, PO-BHADSARA,PS-PALI,DIST-JEHANABAD,PIN-804418`.

**The ask.** Send `location` as the city (or city + locality) that the matching actually uses, and
keep the full address in a separate field if it is needed downstream. If the address is all that
exists, say so and we will do the reduction on our side deliberately rather than incidentally.

---

## 3. Not a blocker, but worth knowing: stale campaign job ids

`TARGET_ITEM_NOT_FOUND` fired 20 times in the same window. Those are `job_id`s that were live when the
campaign was built and are not live now. `${recommendations}` should be built from current job ids at
send time; a caller who agrees to apply to a job that no longer exists is told the apply failed.

---

## 4. The recommendation array carries duplicate postings

`morejobs-22` — a real campaign payload captured as a fixture — holds **22 entries with only 18
distinct role+company pairs**. "Crew Member - McDonald's / MacDonalds" appears **five** times:

| job_id | location | salary |
|---|---|---|
| `b256308a` | Main, Grand Trunk Road, Nehru Nagar, 201001, Ghaziabad | 13000 - 15000 |
| `af81c643` | Raj Nagar Extension, 201003, Ghaziabad | 13000 - 15000 |
| `c9857e06` | Padmana Naidu Marg, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |
| `d0864e33` | 9, PVR, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |
| `699304e1` | 9, PVR, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |

Four of the five are genuinely different branches, which is fine — but the **last two are identical in
company, role, location and salary** and differ only by `job_id`. The same pattern appears on
"Customer Support Executive / CY FUTURE" (two Noida entries).

The bot is instructed to walk the array in order and never skip, so on call `4982c225` the caller
heard "क्रू मेंबर - मैकडॉनल्ड्स, तेरह हज़ार से पंद्रह हज़ार" up to five times, twice with nothing to
tell the two apart. **The ask:** de-duplicate exact role+company+location+salary matches before
building `${recommendations}`. Distinct branches are worth listing separately; two rows for the same
vacancy are not.

Also note the company name is spelled **three different ways** across those five rows —
`MacDonalds`, `McDonald's` — which the bot has to speak, so it says the brand differently depending on
which row it is reading.


---

## 5. Send a cleaned `location_spoken` argument (added 2026-09-08)

**The ask:** alongside `location`, send a second argument — `location_spoken` — containing the same
place with **every digit removed and the words already in the call's script** (Devanagari for Hindi,
Kannada for Kannada). The prompt would then read it verbatim.

**Why the prompt cannot do this itself — three failures, three wordings.** The caller-place slot in
the location sentence carries two instructions that cannot both be obeyed: "this is a literal
substituted token, there is nothing to resolve" (added because six calls resolved it to the
profile's stale city) and "convert it first — drop the digits, write it in Devanagari" (added for
the PIN and Latin leaks). Reading it literally leaks the raw value; trying to convert it makes the
model reach for a place it already knows in Devanagari.

| call | `location` sent | spoken | |
|---|---|---|---|
| `a899617e` | `Muradnagar, 110045` | "मुराद नगर, ११००४५" | PIN as a quantity |
| `7b841e6b` | `Sarjapur, 110045` | "Sarjapur, 110045" | raw, Latin + PIN |
| `a5ba6894` | `10987, Sarhanpur` | "10987, Sarhanpur" | raw, after the fix |
| `1450f797` | `Sarjapur, 110045` | "गाज़ियाबाद" | **wrong place** — the jobs' city |

Reading a substituted token verbatim is the one thing this prompt does reliably. Give it a token
that is already sayable and the whole class disappears.

**What the values actually look like** (from the calls above and the 272 with postal addresses):
`Muradnagar, 110045` · `Sarjapur, 110045` · `10987, Sarhanpur` · `9, PVR, Indirapuram, 201014,
Ghaziabad`. So the cleaning is: drop every digit-only fragment, drop house/plot numbers, keep the
locality and city. That is a few lines where the argument is assembled, and it is the same
transformation we are currently asking a language model to perform on every call.

**Separately, and cheaper:** `location` values that are a bare PIN, a state name, or campaign
metadata (`"Call status: not_dialled"`) should not be sent at all — the prompt already treats them
as empty, so sending them only creates the risk of one being read aloud.

### Sharper diagnosis, added after four more calls

The substituted place is not arbitrary. Of the four substitutions now on record, **three named
साहिबाबाद and one गाज़ियाबाद — and both are entries in the prompt's Canonical Location Spellings
list**:

| call | bot | `location` sent | spoken |
|---|---|---|---|
| `1450f797` | fat | `Sarjapur, 110045` | गाज़ियाबाद |
| `8eb83bc2` | slim | `Sarjapur, 110045` | साहिबाबाद |
| `f90a0b97` | slim | `Sarjapur, 110045` | साहिबाबाद |
| `fa9a16c0` | fat | `Sarjapur, 110045` | साहिबाबाद |

So the mechanism is not simply "two competing instructions" — it is that **the canonical list acts
as an attractor.** The conversion step says *"Use Canonical Location Spellings for a place on that
list. A place NOT on the list is converted exactly the same way."* With the list sitting immediately
below, list-membership becomes the salient operation, and a value that is not on it gets mapped
**to** a member rather than converted on its own terms. The off-list clause is read as "find the
nearest listed place", which is exactly what a Ghaziabad-locality list makes easy.

That predicts the failure will keep happening for any locality outside the list, on either prompt
size, which is what the four calls show. It also gives one more prompt-only thing worth trying
before the upstream change: state that **the list is a spelling table, never a menu** — if a value is
not on it you still say that value, never a list member. That is not another wording of the same
guard; it names the attractor the guard never mentioned. It is queued as the next experiment on the
slim A/B bot rather than applied to live traffic.

### Correction, same day — the substitution half of this is not a production rate

The four "spoke a different place" calls quoted above (`1450f797`, `8eb83bc2`, `f90a0b97`,
`fa9a16c0`) and six more found later are **all harness dials on the tester DID**, whose stored
profile carries `location: "Sahibabad, Ghaziabad, India"` while the fixture sends
`"Sarjapur, 110045"`. Split by caller over 449 calls since 01-09: **real callers 3 RAW, 0
SUBSTITUTED; harness 10 SUBSTITUTED, 0 RAW.** The substitution is a genuine precedence weakness that
reproduces whenever the profile and the argument disagree — but it has not been seen on a real
caller, and it was wrong of me to quote it as a caller-facing rate.

**The ask below is unchanged and rests on the RAW calls, which ARE real callers** — `a899617e`,
`7b841e6b` and `a5ba6894`, the last of them after the fix, with `location: "10987, Sarhanpur"`
(digits first, a shape the prompt's worked examples do not cover). A `location_spoken` argument that
is already digit-free and already in the call's script removes that class entirely.
