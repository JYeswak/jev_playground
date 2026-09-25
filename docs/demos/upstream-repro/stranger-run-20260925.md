# README stranger run (2026-09-25)

A fresh network clone of [`JYeswak/jev_playground`](https://github.com/JYeswak/jev_playground) was run with no API key and a clean `HOME`.

## Source and environment

- Clone commit: `108c22c1f97c8affc57696b33d9b25b5232024b9`.
- Tools: `v22.23.3`, `Python 3.9.6`, `uv 0.9.28 (Homebrew 2026-01-29)`.
- Child command timeout: `600s` per command.
- Child environment: only PATH, HOME, TMPDIR, LANG, TERM and USER; API-key variables were absent.
- Regenerate: `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --out docs/demos/upstream-repro/stranger-run-20260925.md`.

## Command inventory

The script extracts runnable fenced commands and inline command spans in README order. Exact duplicate commands run once; all README line occurrences are listed.

| # | README lines | command |
|---:|---|---|
| 1 | L20 | `git clone https://github.com/JYeswak/jev_playground.git` |
| 2 | L21 | `cd jev_playground` |
| 3 | L22,L34 | `node demos/guard/demo.mjs` |
| 4 | L23,L255,L277 | `bash scripts/quickstart.sh` |
| 5 | L26 | `npm ci --prefix work/sdk` |
| 6 | L35 | `node demos/rag/demo.mjs` |
| 7 | L36 | `node demos/citation/demo.mjs` |
| 8 | L37 | `node demos/skill-suggest/demo.mjs` |
| 9 | L38 | `node demos/chief/demo.mjs` |
| 10 | L39 | `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs` |
| 11 | L40 | `node demos/function-call/demo.mjs` |
| 12 | L41 | `node demos/classify/demo.mjs` |
| 13 | L42 | `node demos/rerank/demo.mjs` |
| 14 | L43 | `node demos/date/demo.mjs` |
| 15 | L44 | `node demos/entity/demo.mjs` |
| 16 | L45 | `node demos/hierarchy/demo.mjs` |
| 17 | L46 | `node demos/autoformat/demo.mjs` |
| 18 | L47 | `node demos/parallel/demo.mjs` |
| 19 | L48 | `node demos/semantic-find/demo.mjs` |
| 20 | L49 | `node demos/cascade/demo.mjs` |
| 21 | L50 | `node demos/ontology-gate/demo.mjs` |
| 22 | L51 | `node demos/consistency/demo.mjs` |
| 23 | L52 | `node demos/consistency-noul/demo.mjs` |
| 24 | L53 | `node demos/preparsed/demo.mjs` |
| 25 | L90 | `python3 work/compaction-need/need.py score` |
| 26 | L90 | `python3 work/compaction-keep/keep.py score` |
| 27 | L90 | `python3 work/loss-depth/compaction/replay.py` |
| 28 | L92 | `python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md` |
| 29 | L117 | `git clone https://github.com/Gaurav-Gosain/jev-sec-bench jev-sec-bench && git -C jev-sec-bench checkout fdb16b9` |
| 30 | L118,L216,L258 | `python3 work/nev-differential/fresh-20260923/score.py` |
| 31 | L119 | `python3 work/nev-differential/variance-20260924/variance.py` |
| 32 | L120 | `python3 work/nev-differential/analyze_diff.py` |
| 33 | L128,L215,L259 | `node --test work/nev-injection/seat-guard.test.mjs` |
| 34 | L141 | `python3 work/gate-observe-dogfood/readout3b.py` |
| 35 | L141 | `python3 work/gate-observe-dogfood/readout4.py score` |
| 36 | L160 | `python3 work/loss-depth/pokejev-components/component_eval.py --heldout` |
| 37 | L165 | `python3 work/score-sst5/score.py` |
| 38 | L166 | `python3 work/jev-variance/score.py` |
| 39 | L167 | `python3 work/choice-banking77/score.py` |
| 40 | L168 | `python3 work/choice-banking77/score.py --set full-prompted` |
| 41 | L169 | `python3 work/choice-clinc150/score.py` |
| 42 | L170 | `python3 work/noul-scifact/score.py` |
| 43 | L171 | `python3 work/haiku-variance/score.py` |
| 44 | L172 | `python3 work/noul-scifact/score.py work/noul-fever` |
| 45 | L173 | `python3 work/noul-variance/score.py` |
| 46 | L174 | `python3 work/noul-scifact/compare-criteria.py` |
| 47 | L175 | `python3 work/noul-scifact/compare-criteria.py work/noul-fever` |
| 48 | L176 | `python3 work/second-incumbent/score.py` |
| 49 | L177 | `python3 work/second-incumbent/score_n4j.py` |
| 50 | L178 | `python3 work/second-incumbent/grok_variance.py` |
| 51 | L179 | `python3 work/grok-incumbent-3/score.py` |
| 52 | L180 | `python3 work/score-stsb/score.py` |
| 53 | L181 | `python3 work/rerank-scifact/score.py` |
| 54 | L182 | `python3 work/game-floors/aggregate.py work/game-floors/rows` |
| 55 | L183 | `python3 work/miniwob-jev/score.py` |
| 56 | L184 | `python3 work/bicameral-gate/score-b.py` |
| 57 | L185 | `python3 work/bicameral-gate/verify-labels-b.py` |
| 58 | L186 | `python3 work/bicameral-gate/gate-variance.py` |
| 59 | L187 | `python3 work/bicameral-gate/score-grok-gate.py` |
| 60 | L188 | `python3 work/bicameral-gate/score-grok-criteria.py` |
| 61 | L189 | `node work/jev-billing-units/measure.mjs` |
| 62 | L190 | `python3 work/bicameral-gate/score-inplace-agree.py` |
| 63 | L191 | `python3 work/jev-injection-flag/score.py` |
| 64 | L192 | `python3 work/jev-toolout-flag/score.py` |
| 65 | L193 | `python3 work/jev-claim-check/score-close.py` |
| 66 | L194 | `python3 work/noul-toxicity/score.py` |
| 67 | L197 | `node work/omp-harm-rule/verify-claim.mjs` |
| 68 | L211 | `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label` |
| 69 | L218,L263 | `./scripts/sync-docs.sh` |
| 70 | L218,L265 | `./scripts/sync-docs.sh --check` |
| 71 | L224 | `node scripts/measure-framing-flip.mjs` |
| 72 | L233 | `br sync --import-only` |
| 73 | L233,L239,L262 | `bash foundation/gates.sh --portable` |
| 74 | L235,L261 | `bash foundation/gates.sh` |
| 75 | L237 | `python3 work/sr-adopt/audit_bars.py` |
| 76 | L241 | `python3 scripts/run-registered-suites.py` |
| 77 | L243 | `python3 scripts/ci-main-status.py` |
| 78 | L249 | `python3 work/omp-jev-review/surface-census.py --fleet-line` |
| 79 | L249,L264 | `python3 scripts/omp-secret-probe.py` |
| 80 | L256 | `bash scripts/quickstart.sh --mine` |
| 81 | L257 | `node demos/<name>/demo.mjs` |
| 82 | L260 | `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` |

## Results

`Quoted numbers` checks numbers in a same-line README `#` comment; it is a substring check, not semantic verification.

| # | README lines | command | exit | wall s | quoted numbers | failure class | first error line |
|---:|---|---|---:|---:|---|---|---|
| 1 | L20 | `git clone https://github.com/JYeswak/jev_playground.git` | 0 | 11.73 | — | none | — |
| 2 | L21 | `cd jev_playground` | 0 | 0.01 | — | none | — |
| 3 | L22,L34 | `node demos/guard/demo.mjs` | 0 | 0.13 | — | none | — |
| 4 | L23,L255,L277 | `bash scripts/quickstart.sh` | 0 | 18.64 | — | none | — |
| 5 | L26 | `npm ci --prefix work/sdk` | 0 | 0.9 | — | none | — |
| 6 | L35 | `node demos/rag/demo.mjs` | 0 | 0.12 | — | none | — |
| 7 | L36 | `node demos/citation/demo.mjs` | 0 | 0.1 | — | none | — |
| 8 | L37 | `node demos/skill-suggest/demo.mjs` | 0 | 0.12 | — | none | — |
| 9 | L38 | `node demos/chief/demo.mjs` | 0 | 0.11 | — | none | — |
| 10 | L39 | `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs` | 0 | 7.92 | — | none | — |
| 11 | L40 | `node demos/function-call/demo.mjs` | 0 | 0.1 | — | none | — |
| 12 | L41 | `node demos/classify/demo.mjs` | 0 | 0.1 | — | none | — |
| 13 | L42 | `node demos/rerank/demo.mjs` | 0 | 0.13 | — | none | — |
| 14 | L43 | `node demos/date/demo.mjs` | 0 | 0.13 | — | none | — |
| 15 | L44 | `node demos/entity/demo.mjs` | 0 | 0.08 | — | none | — |
| 16 | L45 | `node demos/hierarchy/demo.mjs` | 0 | 0.12 | — | none | — |
| 17 | L46 | `node demos/autoformat/demo.mjs` | 0 | 0.09 | — | none | — |
| 18 | L47 | `node demos/parallel/demo.mjs` | 0 | 0.13 | — | none | — |
| 19 | L48 | `node demos/semantic-find/demo.mjs` | 0 | 0.13 | — | none | — |
| 20 | L49 | `node demos/cascade/demo.mjs` | 0 | 0.09 | — | none | — |
| 21 | L50 | `node demos/ontology-gate/demo.mjs` | 0 | 0.11 | — | none | — |
| 22 | L51 | `node demos/consistency/demo.mjs` | 0 | 0.11 | — | none | — |
| 23 | L52 | `node demos/consistency-noul/demo.mjs` | 0 | 0.1 | — | none | — |
| 24 | L53 | `node demos/preparsed/demo.mjs` | 0 | 0.1 | — | none | — |
| 25 | L90 | `python3 work/compaction-need/need.py score` | 0 | 0.39 | — | none | — |
| 26 | L90 | `python3 work/compaction-keep/keep.py score` | 0 | 0.21 | — | none | — |
| 27 | L90 | `python3 work/loss-depth/compaction/replay.py` | 0 | 0.41 | — | none | — |
| 28 | L92 | `python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md` | 0 | 10.8 | — | none | — |
| 29 | L117 | `git clone https://github.com/Gaurav-Gosain/jev-sec-bench jev-sec-bench && git -C jev-sec-bench checkout fdb16b9` | 0 | 1.3 | — | none | — |
| 30 | L118,L216,L258 | `python3 work/nev-differential/fresh-20260923/score.py` | 0 | 0.09 | 4/4 | none | — |
| 31 | L119 | `python3 work/nev-differential/variance-20260924/variance.py` | 0 | 0.21 | 3/3 | none | — |
| 32 | L120 | `python3 work/nev-differential/analyze_diff.py` | 0 | 0.1 | — | none | — |
| 33 | L128,L215,L259 | `node --test work/nev-injection/seat-guard.test.mjs` | 0 | 0.44 | — | none | — |
| 34 | L141 | `python3 work/gate-observe-dogfood/readout3b.py` | 0 | 0.36 | — | none | — |
| 35 | L141 | `python3 work/gate-observe-dogfood/readout4.py score` | 0 | 0.72 | — | none | — |
| 36 | L160 | `python3 work/loss-depth/pokejev-components/component_eval.py --heldout` | 1 | 0.26 | — | missing tracked input | Traceback (most recent call last): |
| 37 | L165 | `python3 work/score-sst5/score.py` | 0 | 0.09 | 4/4 | none | — |
| 38 | L166 | `python3 work/jev-variance/score.py` | 0 | 18.09 | — | none | — |
| 39 | L167 | `python3 work/choice-banking77/score.py` | 0 | 0.06 | 5/5 | none | — |
| 40 | L168 | `python3 work/choice-banking77/score.py --set full-prompted` | 0 | 0.41 | 4/4 | none | — |
| 41 | L169 | `python3 work/choice-clinc150/score.py` | 0 | 0.1 | 6/6 | none | — |
| 42 | L170 | `python3 work/noul-scifact/score.py` | 0 | 13.14 | 4/4 | none | — |
| 43 | L171 | `python3 work/haiku-variance/score.py` | 0 | 11.5 | — | none | — |
| 44 | L172 | `python3 work/noul-scifact/score.py work/noul-fever` | 0 | 12.85 | 2/2 | none | — |
| 45 | L173 | `python3 work/noul-variance/score.py` | 0 | 94.31 | 1/1 | none | — |
| 46 | L174 | `python3 work/noul-scifact/compare-criteria.py` | 0 | 9.12 | 2/2 | none | — |
| 47 | L175 | `python3 work/noul-scifact/compare-criteria.py work/noul-fever` | 0 | 9.86 | 4/4 | none | — |
| 48 | L176 | `python3 work/second-incumbent/score.py` | 0 | 6.46 | 7/7 | none | — |
| 49 | L177 | `python3 work/second-incumbent/score_n4j.py` | 0 | 0.55 | 4/4 | none | — |
| 50 | L178 | `python3 work/second-incumbent/grok_variance.py` | 0 | 46.59 | 2/2 | none | — |
| 51 | L179 | `python3 work/grok-incumbent-3/score.py` | 0 | 16.68 | 4/4 | none | — |
| 52 | L180 | `python3 work/score-stsb/score.py` | 0 | 83.49 | 2/2 | none | — |
| 53 | L181 | `python3 work/rerank-scifact/score.py` | 0 | 10.53 | 6/6 | none | — |
| 54 | L182 | `python3 work/game-floors/aggregate.py work/game-floors/rows` | 0 | 0.08 | 3/3 | none | — |
| 55 | L183 | `python3 work/miniwob-jev/score.py` | 0 | 0.09 | 4/4 | none | — |
| 56 | L184 | `python3 work/bicameral-gate/score-b.py` | 0 | 0.08 | 7/7 | none | — |
| 57 | L185 | `python3 work/bicameral-gate/verify-labels-b.py` | 0 | 0.07 | 3/3 | none | — |
| 58 | L186 | `python3 work/bicameral-gate/gate-variance.py` | 0 | 0.14 | 9/9 | none | — |
| 59 | L187 | `python3 work/bicameral-gate/score-grok-gate.py` | 0 | 0.21 | 7/7 | none | — |
| 60 | L188 | `python3 work/bicameral-gate/score-grok-criteria.py` | 0 | 0.27 | 6/6 | none | — |
| 61 | L189 | `node work/jev-billing-units/measure.mjs` | 0 | 0.18 | 4/4 | none | — |
| 62 | L190 | `python3 work/bicameral-gate/score-inplace-agree.py` | 0 | 0.06 | 2/2 | none | — |
| 63 | L191 | `python3 work/jev-injection-flag/score.py` | 0 | 0.05 | 2/2 | none | — |
| 64 | L192 | `python3 work/jev-toolout-flag/score.py` | 0 | 0.16 | 4/4 | none | — |
| 65 | L193 | `python3 work/jev-claim-check/score-close.py` | 1 | 0.05 | 3/3 | expected nonzero | FAIL |
| 66 | L194 | `python3 work/noul-toxicity/score.py` | 0 | 142.83 | 2/2 | none | — |
| 67 | L197 | `node work/omp-harm-rule/verify-claim.mjs` | 0 | 0.13 | — | none | — |
| 68 | L211 | `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label` | 2 | 0.14 | — | README wrong | prevalence-check: ENOENT: no such file or directory, open 'rows.jsonl' |
| 69 | L218,L263 | `./scripts/sync-docs.sh` | 0 | 130.0 | — | none | — |
| 70 | L218,L265 | `./scripts/sync-docs.sh --check` | 0 | 3.39 | — | none | — |
| 71 | L224 | `node scripts/measure-framing-flip.mjs` | 2 | 0.17 | — | needs key (crashed) | ERROR no key in env. Run under: infisical run --projectId=... -- node scripts/measure-framing-flip.mjs |
| 72 | L233 | `br sync --import-only` | 127 | 0.01 | — | named prerequisite | /bin/bash: br: command not found |
| 73 | L233,L239,L262 | `bash foundation/gates.sh --portable` | 1 | 0.05 | — | named prerequisite | Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh |
| 74 | L235,L261 | `bash foundation/gates.sh` | 1 | 0.05 | — | named prerequisite | Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh |
| 75 | L237 | `python3 work/sr-adopt/audit_bars.py` | 0 | 11.07 | — | none | — |
| 76 | L241 | `python3 scripts/run-registered-suites.py` | 0 | 114.22 | — | none | — |
| 77 | L243 | `python3 scripts/ci-main-status.py` | 2 | 0.06 | — | named prerequisite | CI main NOT_RUN gh not installed; install it from https://cli.github.com, then run: gh auth login |
| 78 | L249 | `python3 work/omp-jev-review/surface-census.py --fleet-line` | 0 | 0.06 | — | none | — |
| 79 | L249,L264 | `python3 scripts/omp-secret-probe.py` | 2 | 0.07 | — | named prerequisite | NOT_RUN omp is not on PATH |
| 80 | L256 | `bash scripts/quickstart.sh --mine` | 2 | 0.05 | — | named prerequisite | you have no such logs, the fixture answers (./scripts/quickstart.sh) still show what the tools do. |
| 81 | L257 | `node demos/<name>/demo.mjs` | 1 | 0.01 | — | README wrong | /bin/bash: name: No such file or directory |
| 82 | L260 | `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | 0 | 0.09 | — | none | — |

Result: `82` rows, `71` exit 0, `11` nonzero.

## Failures requiring README action

The classes below are assigned from the captured output and a fresh-clone `git ls-files` check. `expected nonzero` is retained for README commands that explicitly document a failing bar; every other nonzero row is listed for follow-up.

- L160: **missing tracked input** — `python3 work/loss-depth/pokejev-components/component_eval.py --heldout` — Traceback (most recent call last):
- L211: **README wrong** — `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label` — `rows.jsonl` is an unbound placeholder; no input corpus is supplied.
- L224: **needs key (crashed)** — `node scripts/measure-framing-flip.mjs` — ERROR no key in env. Run under: infisical run --projectId=... -- node scripts/measure-framing-flip.mjs
- L233: **named prerequisite** — `br sync --import-only` — /bin/bash: br: command not found
- L233,239,262: **named prerequisite** — `bash foundation/gates.sh --portable` — Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh
- L235,261: **named prerequisite** — `bash foundation/gates.sh` — Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh
- L243: **named prerequisite** — `python3 scripts/ci-main-status.py` — CI main NOT_RUN gh not installed; install it from https://cli.github.com, then run: gh auth login
- L249,264: **named prerequisite** — `python3 scripts/omp-secret-probe.py` — NOT_RUN omp is not on PATH
- L256: **named prerequisite** — `bash scripts/quickstart.sh --mine` — you have no such logs, the fixture answers (./scripts/quickstart.sh) still show what the tools do.
- L257: **README wrong** — `node demos/<name>/demo.mjs` — /bin/bash: name: No such file or directory

## Boundary (NO-CLAIM)

- No Jev, OpenAI, Anthropic, xAI or OpenRouter request was authorized or sent; this is keyless only.
- The command output check does not prove that a cited number was produced by the intended computation; it only checks text containment.
- This run uses the current GitHub default branch at the recorded commit. It does not claim reproducibility on another commit, OS, or tool version.
