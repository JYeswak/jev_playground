# README stranger run (2026-09-25)

- Source: local checkout /Users/josh/Developer/jev.

## Source and environment

- Clone commit: `89a5e071a500f57a1fcd000eafdfa221a41059ae`.
- Tools: `v22.23.3`, `Python 3.9.6`, `uv 0.9.28 (Homebrew 2026-01-29)`.
- Child command timeout: `600s` per command.
- Child environment: only PATH, HOME, TMPDIR, LANG, TERM and USER; API-key variables were absent.
- Regenerate: `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --source <checkout> --expect docs/demos/upstream-repro/stranger-run-expected.tsv --out docs/demos/upstream-repro/stranger-run.md`.

## Command inventory

The script extracts runnable fenced commands and inline command spans in README order. Exact duplicate commands run once; all README line occurrences are listed. Commands containing `<...>` are listed as `TEMPLATE` and are never executed.

| # | README lines | command |
|---:|---|---|
| 1 | L12 | `git clone https://github.com/JYeswak/jev_playground.git` |
| 2 | L13 | `npm ci --prefix kit` |
| 3 | L14 | `npx --prefix kit --no-install jev doctor --robot` |
| 4 | L16 | `npx --prefix kit --no-install jev ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot` |
| 5 | L17 | `npx --prefix kit --no-install jev verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot` |
| 6 | L18 | `npx --prefix kit --no-install jev score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot` |
| 7 | L19 | `npx --prefix kit --no-install jev classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot` |
| 8 | L28 | `node kit/bin/jev.mjs rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot` |
| 9 | L32 | `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install jev ask choice --state kit/examples/state.json --question kit/examples/question.json --robot \|\| { rc=$?; exit "$rc"; }` |

## Results

`Quoted numbers` checks numbers in a same-line README `#` comment; it is a substring check, not semantic verification.

| # | README lines | command | exit/status | wall s | quoted numbers | failure class | first error line |
|---:|---|---|---:|---:|---|---|---|
| 1 | L12 | `git clone https://github.com/JYeswak/jev_playground.git` | 0 | 7.53 | — | none | — |
| 2 | L13 | `npm ci --prefix kit` | 0 | 4.21 | — | none | — |
| 3 | L14 | `npx --prefix kit --no-install jev doctor --robot` | 2 | 2.16 | — | needs key | {"status":"NOT_RUN","reason":"no key","model":"jev-1.13.0","key_source":"none","sdk":"@typesafe-ai/sdk","omp":{"repo":"/Users/josh/Developer/jev","tools":[{"path":".omp/tools/jev-rerank.ts","present":true},{"path":".omp/tools/jev-claim-check.ts","present":true},{"path":".omp/tools/jev-screen.ts","pr |
| 4 | L16 | `npx --prefix kit --no-install jev ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot` | 0 | 2.09 | — | none | — |
| 5 | L17 | `npx --prefix kit --no-install jev verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot` | 0 | 2.19 | — | none | — |
| 6 | L18 | `npx --prefix kit --no-install jev score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot` | 0 | 1.98 | — | none | — |
| 7 | L19 | `npx --prefix kit --no-install jev classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot` | 0 | 2.08 | — | none | — |
| 8 | L28 | `node kit/bin/jev.mjs rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot` | 0 | 0.15 | — | none | — |
| 9 | L32 | `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install jev ask choice --state kit/examples/state.json --question kit/examples/question.json --robot \|\| { rc=$?; exit "$rc"; }` | 2 | 2.03 | — | needs key | NOT_RUN: no key |

Result: `9` rows, `7` exit 0, `2` nonzero, `0` TEMPLATE.

## Failures requiring README action

The classes below are assigned from the captured output and a fresh-clone `git ls-files` check. `expected nonzero` is retained for README commands that explicitly document a failing bar; `TEMPLATE` commands are not failures and are never executed; every other nonzero row is listed for follow-up.

- L14: **needs key** — `npx --prefix kit --no-install jev doctor --robot` — {"status":"NOT_RUN","reason":"no key","model":"jev-1.13.0","key_source":"none","sdk":"@typesafe-ai/sdk","omp":{"repo":"/Users/josh/Developer/jev","tools":[{"path":".omp/tools/jev-rerank.ts","present":true},{"path":".omp/tools/jev-claim-check.ts","present":true},{"path":".omp/tools/jev-screen.ts","pr
- L32: **needs key** — `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install jev ask choice --state kit/examples/state.json --question kit/examples/question.json --robot || { rc=$?; exit "$rc"; }` — NOT_RUN: no key

## Boundary (NO-CLAIM)

- No Jev, OpenAI, Anthropic, xAI or OpenRouter request was authorized or sent; this is keyless only.
- The command output check does not prove that a cited number was produced by the intended computation; it only checks text containment.
- This run uses the current GitHub default branch at the recorded commit. It does not claim reproducibility on another commit, OS, or tool version.
