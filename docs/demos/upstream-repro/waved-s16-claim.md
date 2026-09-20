# §16 CLAIM STUB — omp-jev-observer live dogfood (pane 3, 2026-09-20)

Claiming this section per the Wave D protocol (two panes on the queue; stub receipt
names the section). Verified load-bearing facts before starting:

- `work/omp-jev-observer/package.json` has NO `omp.extensions` entry (name,
  private, type, engines, scripts.test only) — not installable as shipped.
- Register wiring lives in `src/classify-systemone.mjs` (`recordScore` import,
  line 9; `JEV_SCORE_REGISTER` env, line 11), not `src/index.ts` (no such file;
  entry is `src/observer.mjs`, which imports the classifier).

Target: working-profile co-presence + id-join beyond n=1 lab. Full receipt follows
on completion; this stub is the claim only.
