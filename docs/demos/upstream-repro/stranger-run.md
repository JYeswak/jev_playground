# README stranger run (2026-10-16)

- Source: local checkout /Users/josh/Developer/jev/var/agent-tmp/qx7b.1756641624101/qx7b-clone.

## Source and environment

- Clone commit: `013b2debde2c11e30e4890621f36de66ba89ea56`.
- Tools: `v22.23.3`, `Python 3.9.6`, `uv 0.9.28 (Homebrew 2026-01-29)`.
- Child command timeout: `600s` per command.
- Child environment: only PATH, HOME, TMPDIR, LANG, TERM and USER; API-key variables were absent.
- Regenerate: `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --source <checkout> --expect docs/demos/upstream-repro/stranger-run-expected.tsv --out docs/demos/upstream-repro/stranger-run.md`.

## Command inventory

The script extracts runnable fenced commands and inline command spans in README order. Exact duplicate commands run once; all README line occurrences are listed. Commands containing `<...>` are listed as `TEMPLATE` and are never executed.

| # | README lines | command |
|---:|---|---|
| 1 | L70 | `git clone https://github.com/JYeswak/jev_playground.git` |
| 2 | L71 | `cd jev_playground` |
| 3 | L72 | `git remote get-url origin` |
| 4 | L73 | `git rev-parse HEAD` |
| 5 | L74 | `npm ci --prefix kit` |
| 6 | L75 | `npx --prefix kit --no-install classifier doctor --robot` |
| 7 | L77 | `npx --prefix kit --no-install classifier ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot` |
| 8 | L78 | `npx --prefix kit --no-install classifier verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot` |
| 9 | L79 | `npx --prefix kit --no-install classifier score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot` |
| 10 | L80 | `npx --prefix kit --no-install classifier classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot` |
| 11 | L81 | `npx --prefix kit --no-install classifier gate --command "npm publish --access public" --fake --robot` |
| 12 | L89 | `python3 -c 'from pathlib import Path; Path("var/agent-tmp/jev-omp-demo").mkdir(parents=True, exist_ok=True)' && git init -q var/agent-tmp/jev-omp-demo && npx --prefix kit --no-install classifier omp install --dir var/agent-tmp/jev-omp-demo --robot` |
| 13 | L116 | `npx --prefix kit --no-install classifier rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot` |
| 14 | L121 | `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --robot \|\| { rc=$?; exit "$rc"; }` |
| 15 | L182 | `python3 work/jev-jzgm/replay.py --days 30 --memory-cap 3 --policy cap3` |
| 16 | L194 | `python3 work/local-decision-arms/run.py --platt clefflash` |

## Results

`Quoted numbers` checks numbers in a same-line README `#` comment; it is a substring check, not semantic verification.

| # | README lines | command | exit/status | wall s | quoted numbers | failure class | first error line |
|---:|---|---|---:|---:|---|---|---|
| 1 | L70 | `git clone https://github.com/JYeswak/jev_playground.git` | 0 | 7.84 | — | none | — |
| 2 | L71 | `cd jev_playground` | 0 | 0.01 | — | none | — |
| 3 | L72 | `git remote get-url origin` | 0 | 0.02 | — | none | — |
| 4 | L73 | `git rev-parse HEAD` | 0 | 0.02 | — | none | — |
| 5 | L74 | `npm ci --prefix kit` | 0 | 2.17 | — | none | — |
| 6 | L75 | `npx --prefix kit --no-install classifier doctor --robot` | 1 | 1.7 | — | needs key | {"ok":false,"schema":"classifier.doctor.v1","status":"FINDINGS","data":{"schema_version":"1.0","tool":"jev","tool_version":"0.0.0","doctor_version":"1.0.0","doctor_contract_version":"1.0","run_id":"2026-10-16T18-21-14-034Z__8d20e646","run_dir":null,"started_at":"2026-10-16T18:21:14.034Z","finished_a |
| 7 | L77 | `npx --prefix kit --no-install classifier ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot` | 0 | 1.35 | — | none | — |
| 8 | L78 | `npx --prefix kit --no-install classifier verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot` | 0 | 1.28 | — | none | — |
| 9 | L79 | `npx --prefix kit --no-install classifier score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot` | 0 | 2.07 | — | none | — |
| 10 | L80 | `npx --prefix kit --no-install classifier classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot` | 0 | 1.31 | — | none | — |
| 11 | L81 | `npx --prefix kit --no-install classifier gate --command "npm publish --access public" --fake --robot` | 0 | 1.31 | — | none | — |
| 12 | L89 | `python3 -c 'from pathlib import Path; Path("var/agent-tmp/jev-omp-demo").mkdir(parents=True, exist_ok=True)' && git init -q var/agent-tmp/jev-omp-demo && npx --prefix kit --no-install classifier omp install --dir var/agent-tmp/jev-omp-demo --robot` | 0 | 1.42 | — | none | — |
| 13 | L116 | `npx --prefix kit --no-install classifier rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot` | 0 | 1.32 | — | none | — |
| 14 | L121 | `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --robot \|\| { rc=$?; exit "$rc"; }` | 2 | 1.29 | — | needs key | NOT_RUN: no key |
| 15 | L182 | `python3 work/jev-jzgm/replay.py --days 30 --memory-cap 3 --policy cap3` | 0 | 0.1 | — | none | — |
| 16 | L194 | `python3 work/local-decision-arms/run.py --platt clefflash` | 0 | 0.21 | — | none | — |

Result: `16` rows, `14` exit 0, `2` nonzero, `0` TEMPLATE.

## Failures requiring README action

The classes below are assigned from the captured output and a fresh-clone `git ls-files` check. `expected nonzero` is retained for README commands that explicitly document a failing bar; `TEMPLATE` commands are not failures and are never executed; every other nonzero row is listed for follow-up.

- L75: **needs key** — `npx --prefix kit --no-install classifier doctor --robot` — {"ok":false,"schema":"classifier.doctor.v1","status":"FINDINGS","data":{"schema_version":"1.0","tool":"jev","tool_version":"0.0.0","doctor_version":"1.0.0","doctor_contract_version":"1.0","run_id":"2026-10-16T18-21-14-034Z__8d20e646","run_dir":null,"started_at":"2026-10-16T18:21:14.034Z","finished_a
- L121: **needs key** — `if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --robot || { rc=$?; exit "$rc"; }` — NOT_RUN: no key

## Boundary (NO-CLAIM)

- No Jev, OpenAI, Anthropic, xAI or OpenRouter request was authorized or sent; this is keyless only.
- The command output check does not prove that a cited number was produced by the intended computation; it only checks text containment.
- This run uses the current GitHub default branch at the recorded commit. It does not claim reproducibility on another commit, OS, or tool version.
