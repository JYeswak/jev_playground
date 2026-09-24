# jev_claim_check: does this evidence support this claim? An omp tool, dogfooded on our own README (bead `jev-sp5`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**What ships.** `.omp/tools/jev-claim-check.ts`, a model-callable omp custom tool `jev_claim_check`
with params `{claim, evidence}`, registered through `.omp/extensions/jev-claim-check.ts` (listed in
`.omp/config.yml`, the loader this repo relies on). It asks one Noul over state `{claim, evidence}`:
instructions *"Does the evidence support the claim?"*, criteria `true`: *"The evidence states the claim
or directly implies that it is true"*, `false`: *"The evidence contradicts the claim, or does not
address what the claim asserts"*. That is the SciFact wording that beat Claude Haiku 4.5 on AUC,
Brier and ECE (bead `jev-9er`, [`noul-scifact-20260924.md`](noul-scifact-20260924.md)) with
"abstract" renamed "evidence". The rename is ours and was not measured on SciFact.

**Cuts, fixed here.** `supported` at p >= 0.8, `unsupported` at p <= 0.2, `unsure` between. Chosen
from the committed SciFact Jev rows, before any call of this tool: at those cuts SciFact gives
supported 119/132 true (90.2%), unsupported 212/216 false (98.1%), unsure 52/400. Confidence is
derived, max(p, 1 − p): a Noul answer carries no confidence field. No key, a missing SDK, a transport
or HTTP failure, or a throw returns verdict `not_run` with `NOT_RUN` in the text and no probability. A
malformed answer (not a finite number in [0, 1]) or an empty claim/evidence returns `refused`. Neither
ever returns one of the three verdicts.

**L0** (`node --test work/jev-claim-check/claim-check.test.mjs`, no key, fetch armed to throw): 7 tests,
each with a planted failure (see the test header).

**L3, stated before the session.** A fresh `omp --mode=rpc` session from the repo root, key from
Infisical, driven by `work/jev-claim-check/l3-drive.mjs`. The prompt asks the model to read
`docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md` and call `jev_claim_check` twice with that
file's text as evidence: once on the README sentence it proves (*"Its own suite passes 189 tests and
still exits 1 on unhandled aborts."*), once on a planted false twin (*"Its own suite passes 189 tests
and exits 0 with no unhandled aborts."*). L3 holds when both `tool_execution_end` frames for
`jev_claim_check` are present and the true claim returns `supported` while the false one returns
`unsupported`. Anything else is reported as it came back.

**Dogfood corpus.** Every row of `foundation/kit/claims.tsv` (19 rows at build time). Claim = the
README sentence carrying the row's `readme_pattern`; evidence = the row's `proof_path` text, whole
file up to 6,000 characters, else 3,000 characters either side of the row's `expected_substr`
widened to whole lines. Both rules are in `work/jev-claim-check/build.py`'s header. Plus 19 planted
false claims in `work/jev-claim-check/planted.tsv`, one per row, each the true sentence with one number
changed (9, `kind=number`) or one verdict flipped (10, `kind=verdict`), checked against the same
evidence as its twin. Labels: `cases.jsonl`, 38 rows, sha256
`a5c1e7d0b27da98f3177dd13bc1f72c376aa9b2f9cd672e7fdd98a444258d0a0`, rebuilt byte-identical by
`python3 work/jev-claim-check/build.py --check`. The runner `work/jev-claim-check/run.mjs` drives the
shipped tool's `execute` with its default live asker, so the measured thing is the tool.

**Metrics and bar** (`work/jev-claim-check/score.py`). A case with no verdict counts against the tool
and enters the AUC at 0.5.

| # | Metric | Bar | always `supported` | always `unsupported` |
|---|---|---|---:|---:|
| a | planted false claims called `supported` | <= 1 of 19 | 19 | 0 |
| b | catch-rate: planted false called `unsupported` | >= 14 of 19 | 0 | 19 |
| c | supported-rate: true README claims called `supported` | >= 12 of 19 | 19 | 0 |
| d | AUC of p, true vs planted | >= 0.80 | 0.5 | 0.5 |

**PASS** = all four. Both constants fail. `unsure` is neither a catch nor a support. Stated risks,
before any answer: two proof files are code or data whose text cannot state a run's result
(`inj-fresh-rescore` is a Python scorer, `official-sdk` a TypeScript client), and some README sentences
name numbers that may sit in a different receipt from the one registered. Every true claim the tool
does not call `supported` is read and classed after the run as one of: README error, registry points
at a file that does not hold the claim, evidence-window miss, or tool miss. That reading is
descriptive; labels and the pass rule are not changed after the answers.

**Stated before running:** 38 Jev calls for the dogfood and 2 for L3, one Noul each; the L3 session's
own model tokens are recorded from its frames.

**NO-CLAIM.** Advisory only; the tool never blocks a commit. One wording, one Jev version, one run. The
true labels assume the registry is right; the planted claims are ours, written by the scorer's author,
so the catch-rate measures these plants, not README errors in general. A green L0 proves the policy and
the fail-safe direction, not that any verdict is correct.

## L0 (offline, no key, before any call)

`env -u TYPESAFE_API_KEY node --test work/jev-claim-check/claim-check.test.mjs`: **7/7 pass**
(`[test]`, 2026-09-24, node v22.22.0). Mutation arm (`[mutation]`): five mutants of the tool, each
written to `/tmp/claimcheck-mut/` with only the jev-client import made absolute, run through the same
suite with `CLAIM_CHECK_TOOL=<mutant>`. Every mutant turns at least one test red:

| Mutant | Tests that go red |
|---|---|
| `SUPPORTED_AT = 0.5` | cuts |
| malformed guard removed (any value classified) | malformed answer is refused |
| failure paths return verdict `unsupported` | keyless; asker failure and thrower |
| empty-input check removed | empty claim or evidence is refused |
| confidence = p | confidence is max(p, 1-p) |
