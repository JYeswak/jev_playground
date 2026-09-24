# .11: deterministic applicability gate replaces the Jev pre-gate (TopazRaven)

Bead `jev-deep-kit-8q7.11` (pane-1 decision on .6/.10 data, not a question
revision). Bar: keyless comparison table with every disagreement; the 4
code-mixed SHAs applicable; L0; L3 docs-refused-0-calls + code-scored-live.

## Keyless comparison (same 686 draw, `02f6c5b~1`)

New rule (not thin AND touches `.ts/.mjs/.py/.sh` — the only source-code
extensions in the draw's file inventory) vs the recorded noul verdicts
(`/tmp/ompfit/drawlive.jsonl`): **agree 556/567 = 98.1%**.
Disagreements (11): 4× applicable-here / Jev-refused
(f0fcf328 0.47, 66fa05d9 0.28, 35f86884 0.48, 7ddb7ded 0.48 — all
applicable under the new rule, as required); 7× refused-here /
Jev-scored (b801c109, a6e74825, bc568d33, 584534ed, 3e20121e, d2314321,
c27d0a79 — package.jsons, run JSON, gitignore, flywheel md, and the
extensionless `githooks/pre-commit`, honestly not covered by an
extension set).
Zero live calls for this table (drawlive.jsonl is the recorded W7.0 run).

## L0: `node --test work/omp-jev-review/test/review.test.mjs` 14/14

Code diff applicable, docs/data-only not, thin not; isThinDiff boundaries
(hunks, 9-vs-10, headers never count); touchesCodeFile cases incl.
extensionless-is-not-code; planted >100-line code diff scores; single
scoring call with exactly behaviour+boundary. Two suite tests were
already red at HEAD (fakes lacked `clone()` for the current SDK) —
fixed, disclosed in .6.

## L3: real omp sessions, extension via `-e` (nothing installed anywhere)

Docs-only `git diff` (15-line README): 2× `review_not_applicable`
`non-code-diff`, zero Jev calls —
`2026-09-24T01-32-57-345Z` row `{"kind":"review_not_applicable",
"applicable":false,"command":"git diff","reason":"non-code-diff",
"timestamp":"2026-09-24T01:33:04.941Z"}`.
Code `git show HEAD` (15-line .mjs): 2× `review_scored` live —
`{"kind":"review_scored","command":"git show HEAD",
"probabilities":{"behaviour":0.05,"boundary":0.03},"latencyMs":354,
"model":"jev-1.13.0","timestamp":"2026-09-24T01:36:15.435Z"}`.
L2 (loads without error) shown by contrast with the bad-path
`Failed to load extension` frame.

## Boundary

Live spend: 2 Jev calls (the code-diff scoring; the refusal spent none),
model `jev-1.13.0`, key via infisical. The retired noul gate's 98.1%
agreement is measured on the draw, not asserted. NO-CLAIM: deterministic
applicability is not review quality; scores still come from Jev.

## Rows committed — 2026-09-24

`/tmp/ompfit/drawlive.jsonl` copied byte-identical (`cmp`) to `work/tmp-rescue/ompfit-drawlive.jsonl`, sha256 `e2cb533deb5e18d838fd1f912e8d7fca45c510b3ee03cb9aa79c331536589871`. The 556/567 figure re-scores from this file. The `/tmp` copy was not deleted.
