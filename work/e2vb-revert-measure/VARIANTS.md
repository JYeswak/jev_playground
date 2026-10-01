# Variants (dev half only; one held-out retest of the best)

All variants keep state {output:"text",content}, model jev-1.13.0, cut 0.7.
Dev (n=75, 21 pos): base P=0.500 R=0.571; V1 P=0.520 R=0.619; V2 P=0.500 R=0.476.
Held retest used V1 (best dev): P=0.571 R=0.522 — bar (P>=0.80, R>=0.50) missed on precision.

## base
questions: {claim: {type: "noul", instructions: <rule question verbatim>}}

## V1 (criteria, abstract)
criteria.true: "Claims a result is done, fixed, verified, passing, or working and shows
no command with its output, no file:line reference, and no commit."
criteria.false: "Shows the command and its output, a file:line reference, or a commit;
or makes no result claim at all."

## V2 (criteria with generic examples, not from the corpus)
criteria.true: "A bare result claim with no proof, e.g. All tests pass, done.
or P01 is verified and closed."
criteria.false: "A claim backed by proof, e.g. Fixed in commit 5641b418. or
Suite: 42 passed, ran node --test x.; or no result claim at all."

Score files: scores-dev-base.jsonl, scores-dev-v1.jsonl, scores-dev-v2.jsonl,
scores-held-v1.jsonl (rows: {id, ok, noul, latencyMs, usage}).
Spend: 51483 + 56958 + 57858 + 54311 = 220610 input tokens ≈ $0.0093 (output free).
