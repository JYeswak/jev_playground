# MU-H3 prevalence measurability resolution

Status: **first phase UNASKABLE in the current lane; ruling needs amendment.**
Candidate: MU-H3 runtime redaction, selected as a second project on entropy evidence plus one
external practitioner complaint.
Question: can unknown-credential prevalence be measured honestly from a source this lane controls?

## Evidence available

Q39's widening receipt is decisive:

- the 111-journal corpus is exhausted;
- only seven additional journals exist outside it;
- credential-shaped scan results total 97 rows in 1,185,721 content rows;
- the shapes include 41 ghp-like, 20 sk-live-like, 22 AKIA-like, 12 private-key-like, and 2 xox-like;
- the receipt explicitly says shape is not secret because repository fixtures and documentation can echo
  fake values;
- verifying whether any hit is a real credential would require secret-handling the lane forbids;
- honest widening therefore yields zero credential-injection cases and recommends a synthetic-only retry.

This is not merely a small stratum. The corpus has no ground-truth path from a secret-shaped match to
“real credential” without either exposing a secret or creating a synthetic canary. A prevalence
number over the 97 shapes would be a prevalence of **patterns**, not prevalence of credentials.

## Answer to (a): measurable here?

**No, not as real outbound unknown-credential prevalence.** The lane can measure:

- pattern hits over historical content;
- synthetic canary detection and redaction recall;
- entropy/pattern false positives on deterministic benign sentinels;
- no-raw-byte invariants in a fake provider boundary;
- counts of redaction decisions in a controlled test transport.

It cannot honestly measure the denominator the ruling asks for: real unknown credentials crossing
real provider-bound traffic. The only available source is exhausted, zero credential-injection cases
were classified, and the 97 shape hits are contaminated by known fixtures/documentation. The Q39 strike
therefore applies directly to MU-H3's prevalence phase.

The Q19 entropy probe remains valuable but does not rescue prevalence. It used 23 deterministic
sentinels; entropy thresholds caught unknown forms only by flagging many benign high-entropy values.
That is a detector tradeoff, not a real-traffic rate.

## Answer to (b): what source would support it?

A defensible prevalence source would need all of:

1. A pinned manifest of outbound model requests or tool-result payloads from multiple real agent
   harnesses;
2. raw values kept behind a local trusted boundary, never committed or sent to an external model;
3. deterministic canary injection or an operator-controlled secret registry that lets the local
   redactor know ground truth without revealing values;
4. a content-hash/length/span receipt that proves what crossed the provider boundary;
5. a human or owner-approved label for ambiguous non-canary hits;
6. separate counts for known patterns, unknown candidates, benign high-entropy values, and detector
   errors;
7. a privacy/retention policy that makes the corpus legally and operationally usable.

Inside this lane, the only honest source is a **synthetic runtime canary corpus**: generated sentinel
values inserted into tool results, nested messages, retries, persistence, and provider-bound request
serialization. That measures detector coverage and false redaction, not real-world prevalence.

A real prevalence estimate requires an external partner or production telemetry owner willing to run a
local instrument under a secrets policy. It is outside the current lane's available evidence and
human authority. A future source must arrive as a redacted, pinned manifest; “we found 97 shapes” is
not enough.

## Answer to (c): does MU-H3 retain its second-project position?

**Not in its original form.** The first phase named in `RULING.md`—measure unknown-credential
prevalence in real outbound traffic—is unavailable in this lane. The ruling should be amended from:

```text
MU-H3 deserves a project; first phase = prevalence
```

to:

```text
MU-H3 is a conditional project candidate; first phase = synthetic canary boundary measurement.
Real prevalence is an external prerequisite, not a lane phase.
```

MU-H3 remains defensible as a **Jev-free deterministic redaction tool** plus a synthetic evaluation
harness. Q19 showed the entropy-only baseline has no safe operating point on the sentinel set, but it
did not show whether the unknown class is common in production. A Jev judgment stage only becomes
relevant if a safe metadata/context path can reduce false positives without sending raw unknown values
to Jev.

The second-project ranking should therefore say “conditional, data-source blocked” rather than treat
MU-H3 as equally ready with COD-H2. If a trusted external corpus appears, MU-H3 can return to the
prevalence phase. If only the synthetic canary path exists, it earns a narrower Jev-free security
project, not a market claim about real unknown-secret frequency.

## What this means for the ruling

Both selected project directions now have first-phase constraints, but they are different:

- COD-H2: specification convergence first; the current corpus cannot support whole-policy rung 4.
- MU-H3: synthetic boundary measurement first; real prevalence is absent from the lane and cannot be
  inferred from shape counts.

The honest headline is therefore not “two candidates and their first phases.” It is:

> Two candidate directions survive conceptually, but both first phases are blocked from making their
> broadest claims by evidence the current lane cannot supply. COD-H2 needs a widened verifiable action
> corpus; MU-H3 needs a trusted outbound redaction/prevalence source or must narrow to synthetic
> canaries.

This is not a kill. Missing prevalence is **HELD/UNASKABLE**, exactly as §3c requires. No one should
manufacture credential labels from the 97 shape hits.

## Retry condition

Reopen real-prevalence measurement only when a named external owner supplies a local redacted/pinned
outbound corpus with a secret registry or deterministic canaries and a legal retention boundary. A
synthetic-only run can start now and should report detector recall, benign false positives, no-raw-byte
proof, and boundary latency; it must not be reported as prevalence.

## NO-CLAIM

No real secret was read, no external provider request was made, and no prevalence number was inferred.
This resolution uses Q39's measured zero/97-shape evidence and Q19's 23-sentinel probe only to state
what the lane can and cannot measure.
