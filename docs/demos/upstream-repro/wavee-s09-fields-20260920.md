# §9 SDK-surface field traps — PASS (2026-09-20)

Level: `live` (real code paths executed; deterministic shapes, no model calls).

## Field inventory (read from source, then executed)

- `askJev` → `{ok, scores: {q: p}, confidence?, latencyMs, model}`.
- `askJevChoice` → `{ok, choice, confidence, probabilities: {label: p}, ...}` —
  NO `scores` field.
- `recording()` keys on `result.scores`; fed a successful choice it files a
  failure-shaped row (demonstrated just now: `questionKey 'q', score null` for a
  0.91-confidence success). Four extensions' good calls would have entered the
  register as errors, silently.
- `recordingChoice()` files one row per label + `__choice__` (4 rows for the same
  call, just now). Test 12 (`register.test.mjs:123`) plants exactly this negative;
  suite 13/13 green.

## Rule: refuse silent null scoring

Any consumer reading a field that is not there records a gap (`ok:false`, named
failure), never coerces (`register.test.mjs:66`). The register's else-branches do
this; the `recording()`/choice mismatch is what happens one layer up when the
WRAPPER assumes the shape.

## Ruling: `.score`'s absence is a correct refusal, not a gap

A singular `.score` on a Choice response would collapse the distribution to one
number — the argmax without its margin, i.e. precisely the information the
multiclass conversion was built to preserve (48f834b). jev-client correctly
exposes full distributions and no convenience scalar. Any future `.score` must
carry its reduction rule in the name (e.g. `top1`, `margin`), or it re-invents
the silent null.

## Ledger line

SECTION 9 SDK-surface field traps — PASS — `recording()` misfiles a 0.91-confidence choice as failure-shaped (live demo quoted); `recordingChoice` writes 4 label rows; 13/13 incl. planted test 12 — NO-CLAIM: deterministic shapes only; no prevalence population, UNKNOWN.
