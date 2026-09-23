# W1.2 upstream proofs

HEAD at run: `33fe6ae`. Kit copy: `/tmp/jev-rc-p1/omp-kit-copy/omp-kit`, extracted from `/Users/josh/Downloads/omp-kit (1).zip`. Starter-kit argument: `/tmp/jev-intake/franken-zip/starter-kit`. Suites ran from the copy, not from the jev tree.

## Preregistered

Written from the plan before interpreting the suite output. Expectation: the four suites run and report counts. The planted-failure arm (remove one rule, disable the guard block) should fail 4 of 10 e2e scenarios if the feasibility arm (a clean e2e) can call the model. A suite that cannot run is `NOT_RUN`, not a pass.

## Results

| suite | command | exit | count | wall | failure |
|---|---|---|---|---|---|
| e2e-live | `sh tests/e2e-live.sh /tmp/jev-intake/franken-zip/starter-kit` | 1 | 0 passed / 10 failed | 30.3s | every scenario: `omp never called the model` |
| run-ttsr-tests | `OMP=omp sh tests/run-ttsr-tests.sh` | 0 | 25 passed / 0 failed | 9.5s | none |
| kit-guard.test.ts | `bun test tests/kit-guard.test.ts` | 0 | 39 pass / 0 fail | 9ms | none |
| omp-continue.test.sh | `sh tests/omp-continue.test.sh /tmp/jev-intake/franken-zip/starter-kit` | 2 | 0 scenarios | 1.2s | `initial commit failed` before the first check |

## Planted negative

`NOT_RUN`. The clean e2e feasibility arm failed 10/10 with `omp never called the model`. Removing a rule on that copy would not show that the harness can fail for the author's reason. The temp transcript paths in the suite output were already deleted when re-opened.

NO-CLAIM: 25/25 and 39/39 are the kit's own cases on a `/tmp` copy. They are not a live jev pane interrupt. The e2e 0/10 is an infrastructure failure, not a proof that the kit rules fail.
