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

