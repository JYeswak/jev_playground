# W1.2 upstream proofs

HEAD at run: `33fe6ae`. Kit copy: `/tmp/jev-rc-p1/omp-kit-copy/omp-kit`, extracted from `/Users/josh/Downloads/omp-kit (1).zip`. Starter-kit argument: `/tmp/jev-intake/franken-zip/starter-kit`. Suites ran from the copy, not from the jev tree.

## Preregistered

Written from the plan before interpreting the suite output. Expectation: the four suites run and report counts. The planted-failure arm (remove one rule, disable the guard block) should fail 4 of 10 e2e scenarios if the feasibility arm (a clean e2e) can call the model. A suite that cannot run is `NOT_RUN`, not a pass.

## Results

The first run is the inherited-profile row below. It is not a kit-logic failure.

| suite | command | exit | count | wall | failure |
|---|---|---|---|---|---|
| e2e-live, inherited profile | `KEEP=1 sh tests/e2e-live.sh /tmp/jev-intake/franken-zip/starter-kit` | 1 | 0/10 | 30s | `Model "mock/mock" not found`. This shell has `OMP_PROFILE=grok`. Suite writes `$HOME/.omp/agent/models.yml`. omp reads `$HOME/.omp/profiles/grok/agent/models.yml`. `main.ts:2304` exits before any model call. Verbatim line re-opened in `tmp.oY6ccyAbya/out0.txt`. |
| e2e-live, profile unset | `env -u OMP_PROFILE -u PI_PROFILE -u PI_CODING_AGENT_DIR KEEP=1 sh tests/e2e-live.sh ...` | 0 | 10/10 | subagent run | `log0.jsonl` in `tmp.lSXUAgIMMB` is 3 lines. Model was called. |
| e2e planted arm | same env, copy with `kit-test-skip.md` removed and guard returns disabled | 1 | 6 pass / 4 fail | subagent run | `tmp.wQDzTg3hSl` has 10 logs. The 4 failures are the two guard scenarios and the two skip scenarios. |
| run-ttsr-tests | `OMP=omp sh tests/run-ttsr-tests.sh` | 0 | 25/25 | 9.5s | none |
| kit-guard.test.ts | `bun test tests/kit-guard.test.ts` | 0 | 39/39 | 9ms | none |
| omp-continue, real HOME | `sh tests/omp-continue.test.sh ...` | 2 | 0 scenarios | 1.2s | line 8 swallows stderr. Cause is not missing identity. `~/.gitconfig:41` `templateDir` copies `commit-msg-verification-level.sh`, which refuses subject `init` at line 63. |
| omp-continue, isolated HOME, br on PATH | identity exported | 1 | 5 pass / 6 fail | subagent run | `br ready --json` exits 7. `omp-continue.sh:30` treats that as no ready work and never reads the JSONL. |
| omp-continue, isolated HOME, br off PATH | `command -v br` absent | 0 | 11/11 | subagent run | the suite does its job only in that environment |

## Planted negative

Earned. After the profile vars were unset, removing `kit-test-skip.md` and disabling the guard block made 4 of 10 scenarios fail. The clean suite in that same environment was 10/10, so the 4 failures are the plant, not the model-not-found exit.

NO-CLAIM: I re-opened the kept transcripts and the hook at line 63. I did not personally re-run the 10-scenario or 11-scenario suites. Those counts are the subagent runs whose artifacts I opened.
