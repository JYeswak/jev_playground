# MU-H3 rung-2 entropy probe

Status: deterministic sentinel measurement, no Jev call, no key, no real secret.
Candidate: MU-H3 runtime outbound redaction.
Question: can Shannon entropy handle unknown credential values, or is there a real residual for a
judgment stage?

## Command actually run

```sh
node --input-type=module - <<'JS'
import {scan} from './demos/preaction-abstention/src/redact.mjs';
// fixed hand-authored credential and benign sentinels
// compute Shannon entropy and run the committed pattern scanner
// report thresholds 3.0, 3.5, 4.0, 4.5
JS
```

The run used 24 deterministic values:

- 5 known-pattern credential sentinels (`AKIA`, `ghp`, `xox`, `sk-live`, private-key header);
- 7 unknown credential sentinels: random-looking base64/hex, bearer, OAuth, JWT, readable
  password, and database URL forms;
- 11 benign high-entropy values: SHA-like hashes, UUID/trace IDs, integrity/base64/ciphertext,
  cache key, public key, minified text, and package integrity text.

No candidate was sent to a model. `redact.scan()` only saw the local sentinel bytes and returned
pattern IDs/hashes. The entropy classifier was a measurement-only comparison over supplied token
strings, not a claim that production extraction is solved.

## Measured result

| Shannon threshold | Unknown credentials caught | Unknown recall | Benign values falsely flagged | Benign FP rate | Combined precision |
|---:|---:|---:|---:|---:|---:|
| 3.0 | 7/7 | 100.0% | 11/11 | 100.0% | 38.9% |
| 3.5 | 7/7 | 100.0% | 10/11 | 90.9% | 41.2% |
| 4.0 | 5/7 | 71.4% | 7/11 | 63.6% | 41.7% |
| 4.5 | 4/7 | 57.1% | 6/11 | 54.5% | 40.0% |

The known-format scanner independently caught the known-pattern cases. The unknown forms were not
matched by the committed patterns, as intended.

## Interpretation

Entropy alone has no useful operating point on this sentinel set. At 3.5 bits/character it catches
all seven unknown credential forms but flags ten of eleven benign high-entropy values. Raising the
threshold reduces false positives only by missing unknown classes: the 4.0 threshold misses the
unknown hex and readable-password forms, and 4.5 misses more. The result is not a clean
Jev-free solution; it is a recall/false-positive tradeoff.

The unknown-credential case therefore exists as a concrete structural class, but this probe does
**not** establish its real-world prevalence. The corpus was balanced by design to expose the boundary;
it is not a market sample and cannot support a “material rate” claim about deployed tool results.

## Rung-2 decision

**MU-H3 CLEARED conditionally on the unknown-candidate wedge, not as a completed implementation.**

Reason: a Shannon threshold does not simultaneously handle unknown credential forms and benign
high-entropy content. A future judgment stage could be useful only if it receives safe metadata,
redacted structure, or a reversible local representation; it must never send the unknown raw value
to Jev to ask whether the value is a credential. If the only proposed judgment input is the raw
candidate, the design remains unsafe and returns to HELD.

This is not a claim that MU-H3 beats entropy in production. The probe establishes the deterministic
baseline's failure shape and the exact next experiment. It also preserves the Jev-free composition
option: deterministic patterns plus entropy can remain the first local layer, with a judgment stage
reserved for unresolved metadata/context cases.

## Required next measurement

Use a separately pinned, real-but-redacted tool-result corpus with human labels for unknown secret,
benign identifier, and ambiguous value. Measure recall, false-positive redaction, no-raw-byte
invariant, and coverage at each threshold. A Jev arm may inspect only safe metadata and must report
withhold/error paths; it may not receive raw candidate values. If the labelled corpus shows entropy
alone meets the safety/utility threshold, ship MU-H3 as Jev-free with a retry condition. If entropy
misses a material class and metadata judgment reduces false positives without exposing secrets, the
Jev wedge survives.

## NO-CLAIM

No real secret, provider key, Jev request, network call, user label, or production tool output was
used. The values are deterministic sentinels. This receipt proves only the entropy/pattern tradeoff
on the 24-case synthetic set and does not establish prevalence, calibration, safety certification,
or adoption.
