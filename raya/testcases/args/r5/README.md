# r5 fixtures (2026-09-08)

Each reproduces a failure that was seen on a real call, so a dial either confirms the fix or does not.
Pass conditions are one line each — no interpretation needed.

| fixture | reproduces | pass condition |
|---|---|---|
| `sarjapur-offlist.json` | `7b841e6b` — `location: "Sarjapur, 110045"`, a place on no list in the prompt, spoken raw in Latin with the PIN. Also carries the 12-job payload with `SARA ENTERPRISES`, `MAHARAJA ENGINEERING WORKS`, `GLOBAL CHEMICALS`, so it exercises the company-name conversion and the deep-dive qualification line in the same call | the location sentence says **सरजापुर**; no Latin and no digits anywhere in a spoken turn |
| `maya-vmlg-offlist.json` | `08a8ff4f` — `college_name: "VMLG College"` (the value on 345 of 460 cached Maya calls) **with** `contact_memory: "Not Available"`, which is what made branch B fire | the opener says **वीएमएलजी कॉलेज**; not "मैं माया बोल रही हूँ" |
| `dkb-no-company-name.json` | `564e1d45`, `be4ab8c3` — no `company_name` argument at all, which the emptiness test did not cover | the opener is **"हैलो, क्या आप एक बिज़नेस ओनर हैं?"**; the words "Not Available" appear nowhere |
| `dkb-latin-business-name.json` | `0da5e1f9` — `company_name: "VANS TRADING COMPANY"` read out in Latin to that business's own owner | the opener says **वैन्स ट्रेडिंग कंपनी**; no `VANS`/`TRADING`/`COMPANY` in Latin, and no `[company_name]` marker |
| `readback-kn.json` (in `r3/`) | the end-of-call read-back, on the Dharwad instance where the tester's applications are not saturated | after a successful apply, name, age, gender, role, qualification and area are read back, then **"ಎಲ್ಲಾ ಸರಿನಾ?"** |

**Which bot to dial each on** — the fixture does not encode it:

```
sarjapur-offlist         115b38a5 (kkb-hi-signals)  and 140d13ca (slim)
maya-vmlg-offlist        904f333f (maya-hi-signals)
dkb-no-company-name      fabda71d (dkb-hi-signals)
dkb-latin-business-name  fabda71d (dkb-hi-signals)   persona: hi-employer-cooperative
readback-kn              33037201 (kkb-kn-signals)   persona: kn-force-apply, language kn
```

Tester agent `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, inbound DID `7946350285`. Set the persona with
`scripts/raya_testcall.py persona <tester> <persona.md>` and the language with `… lang <tester> hi|kn`
before dialling — the tester keeps whatever was set last, and a Kannada fixture on a Hindi persona
proves nothing.

## A confound in `sarjapur-offlist.json` — read this before quoting a rate from it

`get_profile` on the tester DID returns a profile carrying **`location: "Sahibabad, Ghaziabad,
India"`**. This fixture sends `location: "Sarjapur, 110045"`. So every dial with it creates a
**profile-versus-argument conflict**, and the bot has two ways to be wrong and one to be right:

| what it says | what that means |
|---|---|
| सरजापुर | correct — argument obeyed and converted (`317bd6e0`, `cea642ea`) |
| साहिबाबाद / गाज़ियाबाद | the **profile** beat `${location}` — a precedence failure, not a conversion one |
| `Sarjapur, 110045` | conversion failed — the raw written value |

That makes it a good two-in-one test and a **terrible source of a production rate**: real callers are
generally dialled where their profile says they live, so the conflict this fixture guarantees is rare
in traffic. Ten "substitution" findings were reported as a caller-facing rate before being split by
caller; all ten were dials with this fixture and not one was a real caller.

**So:** use it to test conversion and precedence, read the three outcomes above as three different
findings, and take rates only from `location_said.py`'s REAL CALLERS line.
