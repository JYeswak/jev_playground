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

## L2 (loaded)

`omp --profile=muse --mode=rpc` `get_state` from the repo root, 2026-09-24: `xd://jev_claim_check` and
`xd://jev_claim_check_ext_probe` both present in `systemPrompt`. Listed, not working; L3 below is the
working proof.

## Results

Bar committed at `ae01091` before any call. Dogfood run 2026-09-24T02:43Z, 38/38 answered on the first
pass, 0 `not_run`, 0 `refused`. Rows: `work/jev-claim-check/rows.jsonl`. Re-score with no key:
`python3 work/jev-claim-check/score.py` (exit 0 = PASS). `build.py --check` reproduces `cases.jsonl`
from README.md and claims.tsv as they stood at `ae01091`; later README edits change the build input,
never the committed labels.

| Set | supported | unsure | unsupported |
|---|---:|---:|---:|
| 19 true README claims | 12 | 5 | 2 |
| 19 planted false claims | 0 | 5 | 14 |

| Metric | Tool | always `supported` | always `unsupported` | Bar | Met |
|---|---:|---:|---:|---|---|
| (a) planted called `supported` | **0/19** | 19/19 | 0/19 | <= 1 | yes |
| (b) catch-rate | **14/19** | 0/19 | 19/19 | >= 14 | yes, at the floor |
| (c) supported-rate | **12/19** | 19/19 | 0/19 | >= 12 | yes, at the floor |
| (d) AUC of p | **0.953** | 0.5 | 0.5 | >= 0.80 | yes |

**PASS** (`[live]`, N=38, `jev-1.13.0`). Catch by plant kind: number changed 7/9, verdict flipped 7/10;
the other 5 plants landed `unsure` (p 0.23–0.68), none `supported`. Two of the four criteria passed at
exactly their floor, so the margin is zero on both; one more `unsure` in either set would have failed
the bar.

**Every true claim the tool did not support, read** (descriptive; labels and bar unchanged):

| Claim | p | Verdict | What the evidence holds | Class |
|---|---:|---|---|---|
| `inj-fresh-haiku` | 0.19 | unsupported | 579 and 584 are in `jev-sec-bench-w70-20260923.md`; **grok-4's 558 is not** | registry: proof file holds part of the sentence |
| `calibration-2026-09-22` | 0.19 | unsupported | ECE and Brier are in the window; `rows: 80` sits in the file header and choice appears as `choice_accuracy: 0.95`, outside the tail window | evidence-window miss (README is right: 80 rows, 0.95 = 19/20) |
| `official-sdk` | 0.37 | unsure | TypeScript client source; shows `retry`, `timeout`, `new TypeSafeClient` | code proof, stated risk before the run |
| `inj-fresh-discordants` | 0.69 | unsure | 61/5 and p = 2.6e-13 present; **65 and "the reverse on 5" are not** | registry: proof file holds part of the sentence |
| `agent-attribution` | 0.67 | unsure | 28/35 vs 23/35 present; "too few rows to call" is our reading, not stated | tool: interpretive clause not in evidence |
| `real-corpus-bar` | 0.74 | unsure | `always-BAD 6,181 (78.8%)` in a table row; "real command traffic" not said in the window | tool: context not stated in window |
| `tool-routing-refused` | 0.27 | unsure | 192 and 252 present in the JSON; "exits 3" is not | registry: proof file holds part of the sentence |

**No README error found.** Every non-supported true claim traces to the proof side, not to a wrong
README number. The finding the tool did surface is about `foundation/kit/claims.tsv`: for three rows
(`inj-fresh-haiku`, `inj-fresh-discordants`, `tool-routing-refused`) the registered proof file holds
the registered substring but not the whole README sentence. Stage 15 checks the substring, so it cannot
see this; `jev_claim_check` can. The missing numbers (grok-4 558, Haiku-wrong 65, `exits 3`) exist in
other receipts; this run did not check which.

**L3** (`[live]`, `wired-and-proven-to-trip`), fresh `omp --profile=muse --mode=rpc --max-time=420`
from the repo root, key from Infisical, 2026-09-24, driven by `work/jev-claim-check/l3-drive.mjs`. The
model (`claude-opus-5-5`) read the receipt and called the tool through the `xd://jev_claim_check` write
bridge twice, evidence = the file's full text (2,054 characters, the tool trims the trailing newline).
Both `tool_execution_end` frames, evidence elided here and verbatim in `work/jev-claim-check/l3-frames.jsonl`
lines 237 and 390:

```json
{"type":"tool_execution_end","toolCallId":"toolu_01LC8xwbirsUEgzZXdwjTcav","toolName":"write","result":{"content":[{"type":"text","text":"calledModel=true verdict=supported p=0.910 confidence=0.910 cuts=0.8/0.2 model=jev-1.13.0"}],"details":{"xdev":{"tool":"jev_claim_check","mode":"execute","args":{"claim":"Its own suite passes 189 tests and still exits 1 on unhandled aborts.","evidence":"<2054 chars>"},"tier":"exec","inner":{"verdict":"supported","reason":null,"calledModel":true,"probability":0.91,"confidence":0.91,"latencyMs":184,"usage":{"input_tokens":1105,"output_tokens":20}}}}},"isError":false}
{"type":"tool_execution_end","toolCallId":"toolu_01Bo8R5pdBpnQppHPydpexNU","toolName":"write","result":{"content":[{"type":"text","text":"calledModel=true verdict=unsupported p=0.050 confidence=0.950 cuts=0.8/0.2 model=jev-1.13.0"}],"details":{"xdev":{"tool":"jev_claim_check","mode":"execute","args":{"claim":"Its own suite passes 189 tests and exits 0 with no unhandled aborts.","evidence":"<2054 chars>"},"tier":"exec","inner":{"verdict":"unsupported","reason":null,"calledModel":true,"probability":0.05,"confidence":0.95,"latencyMs":162,"usage":{"input_tokens":1105,"output_tokens":20}}}}},"isError":false}
```

Opposite verdicts, as the bar requires: **L3 BAR MET.** Negative direction also covered: the keyless
path returns `not_run` (L0, real asker, key deleted).

**Spend.** 40 Jev calls: 38 dogfood (74,352 input / 760 output tokens reported by the API, p50 130 ms,
p95 271 ms) and 2 in L3 (2,210 / 40). The L3 session's own model reported $1.62 across its turns
(647,218 input tokens including cache reads, 3,003 output), almost all of it the session's system
prompt read from cache. Jev's billed units were not read and are not stated.

**Boundary.** One run, one wording (renamed from SciFact's and not re-measured there), one Jev version,
19 claims, plants written by the scorer's author. The pass sits at the floor on two criteria. L3 is one
scratch session, not a working one (L4 not claimed). The tool is advisory and wired into nothing that
blocks. Awaiting a non-author re-score from the committed rows before the bead closes. Scratch left in
place: `/tmp/claimcheck-mut/` (five mutants).

## Follow-up: the three partial-proof rows, registered (`[test]`, stage 15)

Each missing number was found in a committed file and registered as its own `claims.tsv` row (one
proof per row), so the original rows stay as they were:

| README span | Proof file | Substring |
|---|---|---|
| `and grok-4 on 558` | `work/nev-differential/DIFF-RECEIPT.json` | `"correct": 558,` (arm `A-xai-grok-4`) |
| `Jev right and Haiku wrong on 65` | `work/nev-differential/DIFF-RECEIPT.json` | `"jev_only": 65` (arm `B-anthropic-claude-haiku-4-5`) |
| `the reverse on 5, and 61` | `work/nev-differential/DIFF-RECEIPT.json` | `"arm_only": 5,` (same arm) |
| `exits 3 when a question does not beat its constant` | `work/jev-prevalence-first/prevalence-check.mjs` | `WEAK: 3, DEGENERATE: 3` (the CLI's `EXIT` map) |

`bash foundation/gates.d/15-kit-claim.sh`: 25/25 enforced rows pass, coverage 13/47 at floor 13/47;
`--selftest` SELFTEST_OK. No README number was left unproven, so README.md is unchanged.

## Non-author verification (K9z5Live, 2026-09-24, `[oracle]` re-score + `[mutation]` re-run)

Verifier: K9z5Live (background agent of pane 1; not the author ClaimCheckTool). Clean clone of
`main` at `786c042` into `/tmp/k9z5-verify-dsu`. No API calls; no repo file edited except this
section.

| # | Check | Result |
|---|---|---|
| 1 | `env -u TYPESAFE_API_KEY node --test work/jev-claim-check/claim-check.test.mjs` in the clean clone | **HOLDS.** 7/7 pass, 0 fail. |
| 2 | The 5 mutants, re-made independently: copies in `/tmp/k9z5-verify-sp5-mut/`, only the jev-client import made absolute, each run with `CLAIM_CHECK_TOOL=<copy>` | **HOLDS.** An unmutated control copy passes 7/7. `SUPPORTED_AT = 0.5` → "cuts" red. Malformed guard disabled → "malformed answer is refused" red. Failure paths return `unsupported` → "keyless" and "asker failure and thrower" red. Empty-input check removed → "empty claim or evidence is refused" red. `confidence = p` → "confidence is max(p, 1-p)" red. This is the receipt's table exactly. The shipped `.omp/tools/jev-claim-check.ts` was never written to: its sha256 `98e7653d…` equals `git show HEAD:` (byte-identical). |
| 3 | `python3 work/jev-claim-check/score.py`, keyless | **HOLDS.** Exit 0, PASS. True claims: supported 12 / unsure 5 / unsupported 2. Planted: 0 / 5 / 14. By kind: number 7/9, verdict 7/10. (a) 0 ≤ 1, (b) 14 ≥ 14, (c) 12 ≥ 12, (d) AUC 0.953 ≥ 0.80. Per-case p values match the Results table. The two floor-level criteria (b, c) have zero margin, as the receipt says. |
| 4 | Bar precedes rows; labels unchanged | **HOLDS.** `ae01091` is an ancestor of `e24263f`, the commit that adds `rows.jsonl` and `l3-frames.jsonl`. `git log ae01091..HEAD` on `score.py`, `cases.jsonl`, `planted.tsv` and the tool is empty. `cases.jsonl` sha256 is `a5c1e7d0…58d0a0`, as stated. `build.py --check` at `ae01091` prints "cases.jsonl up to date". |
| 5 | The two L3 frames (`l3-frames.jsonl` lines 237 and 390 of 415) | **HOLDS.** Both are `tool_execution_end` through the `write` bridge with `xdev.tool` `jev_claim_check`, `isError` false, and `calledModel` true. Line 237: the true claim ("…still exits 1 on unhandled aborts.") → `supported`, p 0.91. Line 390: the planted twin ("…exits 0 with no unhandled aborts.") → `unsupported`, p 0.05. Both evidence strings equal `typesafe-sdk-js-w70-20260923.md` at `e24263f` with the trailing newline stripped (2,054 chars), and that file does say "189/189 pass … but exit 1 via 8 unhandled". Opposite verdicts, as the L3 bar requires. |

Note (not a failure of any claim): at HEAD, `build.py --check` exits 1 with "claims.tsv row
claim-check-cuts has no plant". `claims.tsv` has gained rows since `ae01091`, so the build refuses
rather than silently rebuilding. The committed labels are unaffected (check 4), but the rebuild only
runs at `ae01091`.

Verdict: PASS reproduces from committed files under an unedited bar. The mutation arm and L3 hold as
written. Scratch left in place: `/tmp/k9z5-verify-dsu`, `/tmp/k9z5-verify-sp5-ae`,
`/tmp/k9z5-verify-sp5-mut/`.
