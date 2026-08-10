# TRRAIN — bot-specific voice-test checklist

Run **alongside** `generic.md` (all sections, especially §14 accessibility, §15 audio check).
TRRAIN is a short **outbound-only** follow-up campaign calling seekers who have **already applied**
to a job. It offers one free support service and records the answer. **Its only tool is `get_profile`** —
used once, silently, to greet the caller by name; there is nothing else it can look up or change.

Path map: `TRRAIN/TRRAIN Hindi.md` (master) · `TRRAIN/TRRAIN Kannada.md` (mirror).
Raya: `TRRAIN Hindi` `cf39a59a-3b24-4842-ba03-4248ec245aa1` · `TRRAIN Kannada` `dfeda883-3d2d-4a74-a0b5-1a47fdde2282`.

The two things most likely to go wrong here are **pitching twice** and **naming the partner**, so
both are also captured as fields in the output prompt (`offer_repeated`, `partner_named`) — check
the call record as well as the transcript.

---

## 1. The offer itself

- [ ] The offer is made **exactly once** per call.
  *Why / how to detect:* Count occurrences of the offer's substance ("जॉब मिलने के चांस…फ्री सर्विस" / "ಜಾಬ್ ಸಿಗುವ ಚಾನ್ಸ್…ಫ್ರೀ ಸರ್ವಿಸ್"). Two or more is a fail, including a "let me put it another way" rephrase after a refusal. The ONE permitted exception is a single re-ask immediately after the caller asked "what is this service?" and got the one-sentence answer.

- [ ] No discovery questions precede the offer.
  *Why / how to detect:* Between the caller acknowledging the application and the offer, the bot must ask nothing else. "क्या आपको काम मिला?", "क्या आप अभी भी काम ढूंढ रहे हैं?", "क्या आपको ट्रेनिंग चाहिए?" are all fails — the offer is supposed to come straight after the acknowledgement.

- [ ] **TRRAIN is never named**, and no partner organisation is named.
  *Why / how to detect:* Search the transcript for "TRRAIN" / "ट्रेन" / any org name. Any occurrence is a **critical fail**. `partner_named` in the call record must be "No".

- [ ] The service is never itemised.
  *Why / how to detect:* Fail on any mention of interview preparation, certificates, English coaching, course lists, or duration. The bot does not know these and must not invent them.

- [ ] "काउंसलिंग" / "ಕೌನ್ಸೆಲಿಂಗ್" is never used as the label for the service.
  *Why / how to detect:* Search the transcript. The permitted labels are "सर्विस" / "मदद करने वाली टीम" (and the Kannada equivalents). This framing was explicitly rejected because seekers do not identify with needing counselling.

- [ ] "फ्री" / "ಫ್ರೀ" is used — not "मुफ़्त" / "ಉಚಿತ".
  *Why / how to detect:* Direct string check on the offer line.

## 2. Reading the answer

- [ ] A clear yes → confirmation line + `trrain_interest` = Yes.
- [ ] A clear no → "कोई बात नहीं, धन्यवाद।" + `trrain_interest` = No, **and no further attempt of any kind**.
  *Why / how to detect:* Everything after the refusal must be closing only. Any re-offer, benefit restatement, or "are you sure?" is a fail.
- [ ] An ambiguous answer → the "our team will contact you, you can decide then" line + `trrain_interest` = Maybe.
  *Why / how to detect:* An ambiguous answer must NOT be recorded as Yes. Check the call record against the transcript.

## 3. Gates — when the offer must NOT happen

- [ ] **Wrong person** (says they never applied / wrong number) → apologise and close, **offer never made**.
  *Why / how to detect:* `trrain_pitched` must be "No". An offer made to someone who just said they never applied is a **critical fail**.
- [ ] **Do-not-call** → comply immediately, no final pitch.
- [ ] **Proxy** (someone else answers) → no offer, no detail about the application disclosed to them.
- [ ] **Busy / angry** → no offer, brief courteous close.

## 4. The silent profile fetch

- [ ] `get_profile` is called exactly once, right after the caller confirms they can hear, and BEFORE the introduction.
  *Why / how to detect:* Check `tool_calls` in the transcript. Zero calls means the personalisation never happens; two or more is a fail. A call placed after the introduction means the name could not have been used in it.

- [ ] The fetch is never narrated.
  *Why / how to detect:* Fail on any "आपकी जानकारी देख रही हूँ" / "आपकी जानकारी मिल गई" / "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" or any permission ask. A short neutral hold is the only thing allowed while it runs.

- [ ] `phone_number` is passed exactly as `${contact_phone}` — 12 digits, no `+`, and NOT re-prefixed with 91.
  *Why / how to detect:* Read the tool payload. A 14-digit number (91 doubled) is a known bug class and will match nobody.

- [ ] When a profile comes back, the first name is used once in the introduction; when it comes back empty, the greeting simply carries no name.
  *Why / how to detect:* An empty fetch must produce a normal nameless greeting — NOT a comment about missing records, and NOT a wrong-number exit. Only the caller saying so makes it a wrong number.

- [ ] The profile's `nameOfJobRolesInterestedIn` is never spoken as the job they applied to.
  *Why / how to detect:* The applied role comes only from `${applied_job_role}`. If the transcript names a role that appears in the profile but not in the args, that is a **critical fail** — the bot has told the caller they applied to something they did not.

## 5. Truthfulness (nothing else can be looked up)

- [ ] The bot never claims an application status, shortlist, interview, or employer decision.
  *Why / how to detect:* If the caller asks "what happened to my application?", the only acceptable answer is that the bot does not have that information + shortlisting means the employer contacts them. Any invented status is a **critical fail**; `promised_outcome` must be "No".
- [ ] The bot never promises a job or a training outcome.
- [ ] No job is presented and no application is taken.
  *Why / how to detect:* If the caller asks for more jobs, the bot must redirect, not list anything. This bot has no job inventory at all — any specific job offered is fabricated.

## 6. Variable handling

- [ ] "Not Available" is never spoken aloud, in any language.
  *Why / how to detect:* Run the unknown-role scenario (`applied_job_role` = "Not Available"). The bot must use the generic wording ("एक जॉब के लिए अप्लाई किया था"). Speaking "not available", or a `${...}` placeholder, is a **critical fail**.
- [ ] The seeker's phone number is never read aloud.
- [ ] When the role IS known, it is spoken in the correct script and matches `${applied_job_role}` exactly — no substituted or invented role.

## 7. Length and tone

- [ ] The call stays short — the flow is audio check → introduction → offer → answer → close.
  *Why / how to detect:* More than ~6 bot turns on a cooperative call means the bot is padding, asking discovery questions, or re-pitching.
- [ ] The bot never implies the seeker is at fault for not having found work.

---

## Scenario set

| Scenario | Persona | Args | The thing being checked |
|---|---|---|---|
| Known role, accepts (asks what it is first) | `hi-trrain-accepts` | `applied_job_role` set | One-sentence clarification, one offer, `trrain_interest` = Yes |
| Unknown role | `hi-trrain-accepts` | role = "Not Available" | Generic wording; "not available" never spoken |
| Wrong person | `hi-trrain-wrong-person` | any | Offer never made; `trrain_pitched` = No |
| Kannada decline | `kn-trrain-declines` | Kannada args | Mirror works; refusal accepted; **no second pitch** |
| Do-not-call | (reuse a do-not-call persona) | any | Comply, no final pitch |
