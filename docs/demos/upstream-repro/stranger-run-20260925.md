# README stranger run (2026-09-25)

A fresh network clone of [`JYeswak/jev_playground`](https://github.com/JYeswak/jev_playground) was run with no API key and a clean `HOME`.

## Source and environment

- Clone commit: `ee4f0b3051cf340fb0914f9b7431def639141b0d`.
- Tools: `v22.23.3`, `Python 3.9.6`, `uv 0.9.28 (Homebrew 2026-01-29)`.
- Child command timeout: `600s` per command.
- Child environment: only PATH, HOME, TMPDIR, LANG, TERM and USER; API-key variables were absent.
- Regenerate: `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --out docs/demos/upstream-repro/stranger-run-20260925.md`.

## Command inventory

The script extracts runnable fenced commands and inline command spans in README order. Exact duplicate commands run once; all README line occurrences are listed. Commands containing `<...>` are listed as `TEMPLATE` and are never executed.

| # | README lines | command |
|---:|---|---|
| 1 | L20 | `git clone https://github.com/JYeswak/jev_playground.git` |
| 2 | L21 | `cd jev_playground` |
| 3 | L22,L34 | `node demos/guard/demo.mjs` |
| 4 | L23,L255,L276 | `bash scripts/quickstart.sh` |
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
| 68 | L211 | `node work/jev-prevalence-first/prevalence-check.mjs work/jev-real-corpus-eval/corpus.jsonl --truth outcome` |
| 69 | L218,L263 | `./scripts/sync-docs.sh` |
| 70 | L218,L265 | `./scripts/sync-docs.sh --check` |
| 71 | L224 | `node scripts/measure-framing-flip.mjs` |
| 72 | L233,L262 | `br sync --import-only` |
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

| # | README lines | command | exit/status | wall s | quoted numbers | failure class | first error line |
|---:|---|---|---:|---:|---|---|---|
| 1 | L20 | `git clone https://github.com/JYeswak/jev_playground.git` | 0 | 6.2 | — | none | — |
| 2 | L21 | `cd jev_playground` | 0 | 0.01 | — | none | — |
| 3 | L22,L34 | `node demos/guard/demo.mjs` | 0 | 0.08 | — | none | — |
| 4 | L23,L255,L276 | `bash scripts/quickstart.sh` | 0 | 9.51 | — | none | — |
| 5 | L26 | `npm ci --prefix work/sdk` | 0 | 0.62 | — | none | — |
| 6 | L35 | `node demos/rag/demo.mjs` | 0 | 0.07 | — | none | — |
| 7 | L36 | `node demos/citation/demo.mjs` | 0 | 0.06 | — | none | — |
| 8 | L37 | `node demos/skill-suggest/demo.mjs` | 0 | 0.07 | — | none | — |
| 9 | L38 | `node demos/chief/demo.mjs` | 0 | 0.07 | — | none | — |
| 10 | L39 | `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs` | 0 | 7.22 | — | none | — |
| 11 | L40 | `node demos/function-call/demo.mjs` | 0 | 0.08 | — | none | — |
| 12 | L41 | `node demos/classify/demo.mjs` | 0 | 0.08 | — | none | — |
| 13 | L42 | `node demos/rerank/demo.mjs` | 0 | 0.07 | — | none | — |
| 14 | L43 | `node demos/date/demo.mjs` | 0 | 0.08 | — | none | — |
| 15 | L44 | `node demos/entity/demo.mjs` | 0 | 0.06 | — | none | — |
| 16 | L45 | `node demos/hierarchy/demo.mjs` | 0 | 0.06 | — | none | — |
| 17 | L46 | `node demos/autoformat/demo.mjs` | 0 | 0.07 | — | none | — |
| 18 | L47 | `node demos/parallel/demo.mjs` | 0 | 0.06 | — | none | — |
| 19 | L48 | `node demos/semantic-find/demo.mjs` | 0 | 0.06 | — | none | — |
| 20 | L49 | `node demos/cascade/demo.mjs` | 0 | 0.07 | — | none | — |
| 21 | L50 | `node demos/ontology-gate/demo.mjs` | 0 | 0.07 | — | none | — |
| 22 | L51 | `node demos/consistency/demo.mjs` | 0 | 0.07 | — | none | — |
| 23 | L52 | `node demos/consistency-noul/demo.mjs` | 0 | 0.07 | — | none | — |
| 24 | L53 | `node demos/preparsed/demo.mjs` | 0 | 0.07 | — | none | — |
| 25 | L90 | `python3 work/compaction-need/need.py score` | 0 | 0.22 | — | none | — |
| 26 | L90 | `python3 work/compaction-keep/keep.py score` | 0 | 0.14 | — | none | — |
| 27 | L90 | `python3 work/loss-depth/compaction/replay.py` | 0 | 0.27 | — | none | — |
| 28 | L92 | `python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md` | 0 | 7.96 | — | none | — |
| 29 | L117 | `git clone https://github.com/Gaurav-Gosain/jev-sec-bench jev-sec-bench && git -C jev-sec-bench checkout fdb16b9` | 0 | 1.25 | — | none | — |
| 30 | L118,L216,L258 | `python3 work/nev-differential/fresh-20260923/score.py` | 0 | 0.04 | 4/4 | none | — |
| 31 | L119 | `python3 work/nev-differential/variance-20260924/variance.py` | 0 | 0.12 | 3/3 | none | — |
| 32 | L120 | `python3 work/nev-differential/analyze_diff.py` | 0 | 0.04 | — | none | — |
| 33 | L128,L215,L259 | `node --test work/nev-injection/seat-guard.test.mjs` | 0 | 0.27 | — | none | — |
| 34 | L141 | `python3 work/gate-observe-dogfood/readout3b.py` | 0 | 0.24 | — | none | — |
| 35 | L141 | `python3 work/gate-observe-dogfood/readout4.py score` | 0 | 0.57 | — | none | — |
| 36 | L160 | `python3 work/loss-depth/pokejev-components/component_eval.py --heldout` | 2 | 0.07 | — | needs key | NOT_RUN (missing prerequisite: git clone https://github.com/sethkarten/pokechamp && git -C pokechamp checkout 0f84c46) |
| 37 | L165 | `python3 work/score-sst5/score.py` | 0 | 0.05 | 4/4 | none | — |
| 38 | L166 | `python3 work/jev-variance/score.py` | 0 | 16.32 | — | none | — |
| 39 | L167 | `python3 work/choice-banking77/score.py` | 0 | 0.06 | 5/5 | none | — |
| 40 | L168 | `python3 work/choice-banking77/score.py --set full-prompted` | 0 | 0.38 | 4/4 | none | — |
| 41 | L169 | `python3 work/choice-clinc150/score.py` | 0 | 0.12 | 6/6 | none | — |
| 42 | L170 | `python3 work/noul-scifact/score.py` | 0 | 20.51 | 4/4 | none | — |
| 43 | L171 | `python3 work/haiku-variance/score.py` | 0 | 12.48 | — | none | — |
| 44 | L172 | `python3 work/noul-scifact/score.py work/noul-fever` | 0 | 12.11 | 2/2 | none | — |
| 45 | L173 | `python3 work/noul-variance/score.py` | 0 | 98.86 | 1/1 | none | — |
| 46 | L174 | `python3 work/noul-scifact/compare-criteria.py` | 0 | 10.66 | 2/2 | none | — |
| 47 | L175 | `python3 work/noul-scifact/compare-criteria.py work/noul-fever` | 0 | 11.22 | 4/4 | none | — |
| 48 | L176 | `python3 work/second-incumbent/score.py` | 0 | 7.4 | 7/7 | none | — |
| 49 | L177 | `python3 work/second-incumbent/score_n4j.py` | 0 | 0.66 | 4/4 | none | — |
| 50 | L178 | `python3 work/second-incumbent/grok_variance.py` | 0 | 74.94 | 2/2 | none | — |
| 51 | L179 | `python3 work/grok-incumbent-3/score.py` | 0 | 14.49 | 4/4 | none | — |
| 52 | L180 | `python3 work/score-stsb/score.py` | 0 | 82.43 | 2/2 | none | — |
| 53 | L181 | `python3 work/rerank-scifact/score.py` | 0 | 11.4 | 6/6 | none | — |
| 54 | L182 | `python3 work/game-floors/aggregate.py work/game-floors/rows` | 0 | 0.12 | 3/3 | none | — |
| 55 | L183 | `python3 work/miniwob-jev/score.py` | 0 | 0.1 | 4/4 | none | — |
| 56 | L184 | `python3 work/bicameral-gate/score-b.py` | 0 | 0.1 | 7/7 | none | — |
| 57 | L185 | `python3 work/bicameral-gate/verify-labels-b.py` | 0 | 0.1 | 3/3 | none | — |
| 58 | L186 | `python3 work/bicameral-gate/gate-variance.py` | 0 | 0.19 | 9/9 | none | — |
| 59 | L187 | `python3 work/bicameral-gate/score-grok-gate.py` | 0 | 0.22 | 7/7 | none | — |
| 60 | L188 | `python3 work/bicameral-gate/score-grok-criteria.py` | 0 | 0.31 | 6/6 | none | — |
| 61 | L189 | `node work/jev-billing-units/measure.mjs` | 0 | 0.18 | 4/4 | none | — |
| 62 | L190 | `python3 work/bicameral-gate/score-inplace-agree.py` | 0 | 0.06 | 2/2 | none | — |
| 63 | L191 | `python3 work/jev-injection-flag/score.py` | 0 | 0.05 | 2/2 | none | — |
| 64 | L192 | `python3 work/jev-toolout-flag/score.py` | 0 | 0.18 | 4/4 | none | — |
| 65 | L193 | `python3 work/jev-claim-check/score-close.py` | 1 | 0.07 | 3/3 | expected nonzero | FAIL |
| 66 | L194 | `python3 work/noul-toxicity/score.py` | 0 | 137.09 | 2/2 | none | — |
| 67 | L197 | `node work/omp-harm-rule/verify-claim.mjs` | 0 | 0.1 | — | none | — |
| 68 | L211 | `node work/jev-prevalence-first/prevalence-check.mjs work/jev-real-corpus-eval/corpus.jsonl --truth outcome` | 0 | 0.11 | — | none | — |
| 69 | L218,L263 | `./scripts/sync-docs.sh` | 0 | 126.28 | — | none | — |
| 70 | L218,L265 | `./scripts/sync-docs.sh --check` | 0 | 1.74 | — | none | — |
| 71 | L224 | `node scripts/measure-framing-flip.mjs` | 2 | 0.18 | — | needs key | NOT_RUN (no TypeSafe key in env; run under infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- node scripts/measure-framing-flip.mjs to spend) |
| 72 | L233,L262 | `br sync --import-only` | 127 | 0.01 | — | named prerequisite | /bin/bash: br: command not found |
| 73 | L233,L239,L262 | `bash foundation/gates.sh --portable` | 1 | 0.03 | — | named prerequisite | Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh |
| 74 | L235,L261 | `bash foundation/gates.sh` | 1 | 0.03 | — | named prerequisite | Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh |
| 75 | L237 | `python3 work/sr-adopt/audit_bars.py` | 0 | 6.56 | — | none | — |
| 76 | L241 | `python3 scripts/run-registered-suites.py` | 0 | 73.62 | — | none | — |
| 77 | L243 | `python3 scripts/ci-main-status.py` | 2 | 0.04 | — | named prerequisite | CI main NOT_RUN gh not installed; install it from https://cli.github.com, then run: gh auth login |
| 78 | L249 | `python3 work/omp-jev-review/surface-census.py --fleet-line` | 0 | 0.04 | — | none | — |
| 79 | L249,L264 | `python3 scripts/omp-secret-probe.py` | 2 | 0.05 | — | named prerequisite | NOT_RUN omp is not on PATH |
| 80 | L256 | `bash scripts/quickstart.sh --mine` | 2 | 0.04 | — | named prerequisite | you have no such logs, the fixture answers (./scripts/quickstart.sh) still show what the tools do. |
| 81 | L257 | `node demos/<name>/demo.mjs` | TEMPLATE | 0.0 | — | TEMPLATE | — |
| 82 | L260 | `node scripts/jev-probe.mjs --replay docs/demos/jev-probe/probe-response-20260918.json` | 0 | 0.06 | — | none | — |

Result: `82` rows, `72` exit 0, `9` nonzero, `1` TEMPLATE.

## Failures requiring README action

The classes below are assigned from the captured output and a fresh-clone `git ls-files` check. `expected nonzero` is retained for README commands that explicitly document a failing bar; `TEMPLATE` commands are not failures and are never executed; every other nonzero row is listed for follow-up.

- L160: **needs key** — `python3 work/loss-depth/pokejev-components/component_eval.py --heldout` — NOT_RUN (missing prerequisite: git clone https://github.com/sethkarten/pokechamp && git -C pokechamp checkout 0f84c46)
- L224: **needs key** — `node scripts/measure-framing-flip.mjs` — NOT_RUN (no TypeSafe key in env; run under infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- node scripts/measure-framing-flip.mjs to spend)
- L233,262: **named prerequisite** — `br sync --import-only` — /bin/bash: br: command not found
- L233,239,262: **named prerequisite** — `bash foundation/gates.sh --portable` — Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh
- L235,261: **named prerequisite** — `bash foundation/gates.sh` — Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun ./foundation/gates.sh
- L243: **named prerequisite** — `python3 scripts/ci-main-status.py` — CI main NOT_RUN gh not installed; install it from https://cli.github.com, then run: gh auth login
- L249,264: **named prerequisite** — `python3 scripts/omp-secret-probe.py` — NOT_RUN omp is not on PATH
- L256: **named prerequisite** — `bash scripts/quickstart.sh --mine` — you have no such logs, the fixture answers (./scripts/quickstart.sh) still show what the tools do.

## Boundary (NO-CLAIM)

- No Jev, OpenAI, Anthropic, xAI or OpenRouter request was authorized or sent; this is keyless only.
- The command output check does not prove that a cited number was produced by the intended computation; it only checks text containment.
- This run uses the current GitHub default branch at the recorded commit. It does not claim reproducibility on another commit, OS, or tool version.
