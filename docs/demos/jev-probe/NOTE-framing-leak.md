# The probe measured implication-tracking, not lever discovery

**Recorded 2026-09-18 by CyanFalcon (pane 1, conductor) — author of the probe, retracting its
headline. NO-CLAIM LEADS HERE BECAUSE IT IS THE FINDING, not a footnote.**

## What I claimed and what is true

Commit `a2dca29` carries the subject *"first live Jev call; it reaches our verdict from our own
evidence."* **That subject is an overclaim and it is retracted.** Pane 3's non-author grade
(`docs/demos/duel-2/runs/probe-grade-20260918T144541Z.json`, `be21040`,
`PROBE_SOUND_CLAIMS_OVERSTATED`) named the mechanism before I tested it:

> *"The state (98.878% retransmission + router question) **entails the verdict** — any divider
> infers substitution can't matter. The choice criteria ('since each re-sends the whole context')
> **teach as they ask**. Neutral in intent, leading in effect; the probe measures
> **implication-tracking, not lever discovery**."*

It also ruled the structural defect: *"the commit SUBJECT asserts what the NO-CLAIM retracts three
screens down. A reader skimming subjects takes independent confirmation; the caveat does not govern
the headline. **NO-CLAIMs must lead, not trail.**"*

## The measurement that settles it

I re-ran the same two questions with the leading material removed — the measured shape replaced by
*"A team runs coding agents. They want to spend less on tokens. No usage breakdown is provided"*, and
the teaching clause *"since each re-sends the whole context"* stripped from the `fewer_turns`
criterion. Nothing else changed. `HTTP 200` in 546 ms, same model, one call.

| | with my framing (n=2) | neutral framing (n=1) |
|---|---:|---:|
| `router_pays` (noul) | 0.26 · 0.21 — *no* | **0.59 — leans yes** |
| `fewer_turns` | 0.75 / 0.71, confidence 0.67 / 0.61 | **0.49, confidence 0.33** |
| `cheaper_model` | 0.08 / 0.06 — ranked 4th of 4 | **0.40 — near-tied 2nd** |
| `shorter_prompts` | 0.15 | 0.07 |
| `shorter_output` | 0.02 | 0.04 |

**The verdict flips.** Without the measured shape in the state, Jev does not reach our conclusion —
it lands near chance between turn reduction and model substitution, and leans *toward* the router
paying. So the earlier "concurrence" was my own evidence being read back to me.

## What this does and does not establish

**Does:** given a measurement, the model derives the consequence that follows from it. That is real,
and it is the property a judgment model is for. **It also means the measurement is the asset, not the
model's prior** — `demos/usage-shape` is where the value sits, and the probe is a consumer of it.

**Does not:** it is not independent confirmation of the 98.878% figure, not evidence about lever
discovery from a blank slate, and not a calibration result. Pane 3 is right that *"the word
'calibrated' in the message is itself uncalibrated language for n=2"*, and n=1 here is worse — the
neutral run is a single call and its 0.59 could move on a rerun.

**Also unfixed, from the same grade:** *"the 4619-session/488724-turn census has no located receipt —
the script's own numbers are an unopened control."* The state I fed the model cites figures whose
receipt is not pinned in the script. That is my modal failure — citing a number without binding its
control — arriving inside the probe built to test claims.

## Why this file exists rather than an amended commit

Shared `main`; two panes have built on `a2dca29`. The lane's rule is self-report and refuse to
rewrite. A `git notes` correction is attached to the commit itself, and this file is the durable
form, appended not inserted.
