#!/usr/bin/env python3
"""fix_presence.py — assert that every fix we have shipped is still present on EVERY bot that needs it.

The failure this closes has happened three times. A fix is worked out on one bot, mirrored by hand,
and lands on some of its twins:

  * 2026-09-03  `duplicate_check` was a required `apply_job` param on 1 of 12 bots; the prompt text
                was mirrored everywhere, so nothing looked wrong.
  * 2026-09-03  the ACTION_LIMIT_REACHED mapping in the tool description: 1 of 6 Signals bots.
  * 2026-09-04  the TRRAIN-naming policy landed in Hindi and never reached Kannada — 7 references
                against 0 — while heading counts matched 54/54, so the sync check saw an aligned pair.

`static_regression.py` checks contracts and structure; `toolschema_parity.py` checks tool schemas;
`sync_check` compares a language pair's skeleton. None of them knows what we FIXED. This does: one
row per shipped fix, naming the token that proves it and the bots that must carry it. A fix that gets
reverted, reworded away, or missed on a mirror shows up here as a hard failure the next time anything
runs.

Adding a row is part of shipping a fix. If a fix cannot be reduced to a token, say so in `note` and
give the closest proxy — a weak check that runs beats a strong one that does not exist.

Usage: python3 raya/regression/fix_presence.py [--verbose]
Exit 1 if any required fix is missing from any bot that should carry it.
"""
import argparse, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KKB_CONV = sorted(f for f in glob.glob(os.path.join(REPO, "KKB", "*.md")) if "CHANGELOG" not in f)
MAYA_CONV = sorted(f for f in glob.glob(os.path.join(REPO, "Maya", "*.md"))
                   if "CHANGELOG" not in f and "Memory" not in f and "Output" not in f)
TRRAIN_CONV = [os.path.join(REPO, "TRRAIN", "TRRAIN Hindi.md"), os.path.join(REPO, "TRRAIN", "TRRAIN Kannada.md")]
DKB_SIGNALS = [os.path.join(REPO, "DKB", "DKB Hindi Signals.md"), os.path.join(REPO, "DKB", "DKB Kannada Signals.md")]
DKB_ALL_CONV = [os.path.join(REPO, "DKB", n) for n in
                ("DKB Hindi Signals.md", "DKB Kannada Signals.md", "DKB Hindi.md",
                 "DKB Kannada.md", "DKB Inbound Hindi.md", "DKB Inbound Kannada.md")]


def seeker_conv():
    """KKB + Maya conversation prompts (memory/output excluded — they carry no spoken flow)."""
    return [f for f in KKB_CONV if "Memory" not in f and "Output" not in f] + MAYA_CONV


def inbound_conv():
    return [f for f in seeker_conv() if "Inbound" in os.path.basename(f)]


def outbound_conv():
    return [f for f in seeker_conv() if "Inbound" not in os.path.basename(f)]


# (id, description, files, must_contain, must_NOT_contain)
FIXES = [
    ("memory-injection", "the verbatim contact_memory injection block",
     seeker_conv(), ["{${contact_memory}}"], []),

    ("no-jobrec-alias", "the job_recommendations ALIAS is gone — the empty-jobs test named a variable "
                        "that does not exist, so it read as empty on every call (D66, call 8d3453b1)",
     seeker_conv(), [], ["job_recommendations"]),

    ("apply-bridge-dropped", "no licensed spoken line asserts the apply before the tool result (D65) — "
                             "the bridge line was what the model said INSTEAD of calling apply_job",
     seeker_conv(), ["are now FORBIDDEN in this position"],
     ["Allowed examples:\n- \"ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ.\"",
      "Allowed examples:\n- \"ಸರಿ, ನಿಮ್ಮ ಪರವಾಗಿ ಅಪ್ಲೈ ಮಾಡ್ತೇನೆ.\""]),

    ("row1-evidence-gate", "the already-applied line requires evidence you can point at (c5a10922)",
     seeker_conv(), ["REQUIRES EVIDENCE YOU CAN POINT AT"], []),

    ("failure-offers-another-job", "an apply that did not go through never ends the job conversation",
     outbound_conv(), ["ENDS ON THE OFFER OF ANOTHER JOB", "ENDS ON THE NEED CAPTURE QUESTION"], []),

    ("no-spoken-job-count", "the caller is never told how many jobs we hold",
     seeker_conv(), ["NEVER say how many jobs you have"], []),

    ("inbound-confirm-first", "a held location is CONFIRMED, never re-asked (D61, bbdb6eaf)",
     inbound_conv(), ["CONFIRM it, never ask openly"], []),

    ("inbound-caseB-location", "Case B has its own copy of the location check — the rule living in "
                               "Case A never reached a profile whose role is the placeholder 'Any' (D63, 7a98b7a0)",
     inbound_conv(), ["This branch is why Case B needs its own copy of the check"], []),

    ("no-postal-address-aloud", "only the town/city part of a stored location is spoken (b48f70fb)",
     inbound_conv(), ["never read a full postal address aloud"], []),

    ("maya-confirm-in-closed-set", "the confirm line is inside the location closed set (D64, 0baf8765)",
     MAYA_CONV, ["The confirm line is inside this closed set."], []),

    # Scoped to DKB_SIGNALS when first written, which is exactly why it passed while the LEGACY pair
    # still SCRIPTED the government line — live call 4b2d7dca on 2026-09-04 opened with "मैं गवर्नमेंट
    # एम्प्लॉयमेंट प्रोग्राम की तरफ से". A row that checks only the bots you happened to fix is not a
    # guard. Now every DKB conversation prompt, and the forbidden wording must be gone from the
    # SPOKEN lines (the rule itself quotes it, so the must-not list cannot be used here).
    ("dkb-not-government", "DKB is the city administration's initiative, never a government programme "
                           "— all SIX conversation prompts, not just the Signals pair (4b2d7dca)",
     DKB_ALL_CONV, ["never claim to be the government"], []),

    ("dkb-expiry-needs-a-role", "the expiry opener requires a real job_role (e2ce642a, 0eb3fc72)",
     DKB_SIGNALS, ["THE NEW-VACANCY OPENING IS THE DEFAULT"], []),

    ("trrain-names-the-partner", "TRRAIN Trust is introduced by name in BOTH languages — it landed in "
                                 "Hindi on 2026-08-12 and never reached Kannada until 2026-09-04",
     TRRAIN_CONV, ["TRRAIN Trust is the ONLY partner you may name"],
     ["Never name TRRAIN or any other partner organisation aloud"]),

    ("maya-college-two-openers", "the opener is TWO lines chosen by looking at the value, not one "
                                 "template with ${college_name} inside it (harness call 718aa8ab read "
                                 "the raw token aloud despite three rules forbidding it)",
     [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["AN UNSUBSTITUTED TOKEN COUNTS AS EMPTY"], []),

    ("token-counts-as-empty", "every prompt with a ${token} inside a QUOTED SPOKEN line says that an "
                              "unsubstituted token counts as EMPTY — the platform drops empty args, so "
                              "an unsupplied field arrives as the raw token and is read aloud (D67, 718aa8ab)",
     [os.path.join(REPO, "KKB", "KKB Placeholder Hindi Signals.md"),
      os.path.join(REPO, "KKB", "KKB Placeholder Kannada Signals.md"),
      os.path.join(REPO, "TRRAIN", "TRRAIN Hindi.md"),
      os.path.join(REPO, "TRRAIN", "TRRAIN Kannada.md")] + DKB_SIGNALS
     + [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["UNSUBSTITUTED TOKEN COUNTS AS EMPTY"], []),

    ("no-item-state-in-dhiway", "the Dhiway prompts must never mention item_state — it is a Signals-only "
                                "contract token and leaked twice",
     [f for f in seeker_conv() if "Signals" not in os.path.basename(f)], [], ["item_state"]),

    # ---- 2026-09-08, the written-value-spoken-verbatim family (D71-D74) ----

    ("offlist-value-still-converted", "a name that is on NO list in the prompt is converted exactly "
                                      "like one that is — the off-list branch of every script rule "
                                      "(D71; 7b841e6b said 'Sarjapur, 110045', b6353cfb said 'VMLG College')",
     seeker_conv(), ["not an exemption"], []),

    ("location-converted-before-spoken", "`${location}` is reduced to place words and written in the "
                                         "target script BEFORE the sentence is said — and the old "
                                         "'say the sentence as it arrives' permission is gone (D71)",
     [os.path.join(REPO, "KKB", "KKB Placeholder Hindi Signals.md"),
      os.path.join(REPO, "KKB", "KKB Placeholder Kannada Signals.md")],
     ["a written value is not sayable"],
     ["**Say the sentence as it arrives — but speak only the PLACE WORDS in it.**"]),

    ("no-latin-field-label-spoken", "no English field label is left inside a Hindi spoken template or "
                                    "sample — the Kannada twins already transliterated it (D72, 9d5e9848)",
     [f for f in seeker_conv() if "Kannada" not in os.path.basename(f)], [], ["Qualification: "]),

    ("dkb-absent-company-name", "the company-name emptiness test covers the ABSENT argument, not just "
                                "the string 'Not Available' and NULL — 7 live calls greeted owners as "
                                "'Not Available' because the arg was never sent (D73, 564e1d45, be4ab8c3)",
     DKB_SIGNALS + [os.path.join(REPO, "DKB", "DKB Hindi.md"),
                    os.path.join(REPO, "DKB", "DKB Kannada.md")],
     ["AN UNSUBSTITUTED TOKEN COUNTS AS ABSENT"], []),

    ("no-token-in-sample-speech", "no sample conversation shows the agent speaking a raw ${token} — the "
                                  "samples outvoted four rules and taught the pass-through (D74, b6353cfb)",
     MAYA_CONV, [], ["> **Agent:** नमस्ते। मैं माया, ${college_name} की ओर से"]),

    ("qualification-not-an-occupation", "an education qualification in the profile `role` field is NOT a "
                                        "usable role — QA heard 'आप अभी बी०टेक०(ई०सी०एस) का काम कर रहे हैं' "
                                        "(D64/D71, QA call 5035574; reproducing call id still pending)",
     seeker_conv(), ["never what they DO"], []),

    ("company-converted-at-point-of-use", "the job-presentation format itself says [role]/[company]/"
                                          "[location] arrive in Latin and are converted — the "
                                          "Devanagari rule was stated five times elsewhere and the "
                                          "payload still went out raw, 5x in one call (D71, ea0477f4, "
                                          "90658584)",
     seeker_conv(), ["arrive from `${recommendations}` in LATIN script"], []),

    ("maya-collegename-only-decides", "ONLY the college_name value line picks Maya's opener — the bare "
                                      "string 'Not Available' in `contact_memory` was satisfying branch B, "
                                      "so branch A fired 48/48 on maya-hi-out and 2/14 on maya-hi-signals "
                                      "(D75, 08a8ff4f)",
     [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["No other field's value has any bearing on it"], []),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    cache = {}
    fails = []
    print("fix-presence check | %d fixes" % len(FIXES))
    for fid, desc, files, must, must_not in FIXES:
        missing, leaked = [], []
        for f in files:
            if f not in cache:
                if not os.path.exists(f):
                    missing.append((os.path.basename(f), "FILE MISSING")); continue
                cache[f] = open(f, encoding="utf-8").read()
            text = cache[f]
            # must_contain is satisfied by ANY of the tokens: a fix may be worded per language, and
            # the point is that the fix is present, not that one exact spelling is.
            if must and not any(t in text for t in must):
                missing.append((os.path.basename(f), must[0][:60]))
            for t in must_not:
                if t in text:
                    leaked.append((os.path.basename(f), t.splitlines()[0][:60]))
        status = "OK" if not (missing or leaked) else "FAIL"
        print("  %-4s %-28s %d bot(s)  %s" % (status, fid, len(files), desc if a.verbose else ""))
        for b, t in missing:
            print("        MISSING   %-46s expected: %s" % (b, t)); fails.append(fid)
        for b, t in leaked:
            print("        REGRESSED %-46s must not contain: %s" % (b, t)); fails.append(fid)
    print("")
    if fails:
        print("FIX PRESENCE: %d failure(s) across %d fix(es)" % (len(fails), len(set(fails))))
        sys.exit(1)
    print("FIX PRESENCE CLEAN — every shipped fix present on every bot that needs it")


if __name__ == "__main__":
    main()
