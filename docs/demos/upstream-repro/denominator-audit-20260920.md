# Denominator audit: guard runs on the public surface — 2026-09-20 `[pending]`

Every claim below with a regeneration command was run through
`scripts/pinned-denominator.sh` (exit codes unpiped). **Zero drifts found;
nothing fixed.** The finding is the second table.

## Guard runs (all agree)

| claim | claimed | regenerated | result |
|---|---|---:|---|
| locked dig questions (`cass-dig-rows.jsonl`) | 138 | `grep -c .` → 138 | agree |
| packages in census (`omp-jev-*` + harm-rule) | 21 | `ls -d … \| wc -l` → 21 | agree |
| pinned replay rows (fixture `c4e0e7c4…`) | 55 | `replay.mjs fixture \| awk` → 55, sha matches | agree |
| pinned replay api calls | 0 | same run → 0 | agree |
| frozen corpus rows | 7,846 | `wc -l <` → 7846 | agree |
| frozen isError count | 315 | python count → 315 | agree |
| routing-backtest suite | 29 | `npm test` → `# pass 29` | agree |

Method notes: the first replay attempt ran the LIVE register (200 rows,
sha `5aee3a…`) against the pinned claim — that disagreement is correct
guard behavior (live grows; pinned does not), and the claim names the
fixture. The first api-zero extraction printed `:` (wrong awk field);
fixed to the value field before recording agree.

## Cannot be re-derived (the finding — these rot silently)

- **Live-harvest family** (INTEGRATIONS:74): 216,507 dcg decisions,
  n=78,455 joinable, 3,098, 36,955/41,500 split. Source regenerates
  (77,767→78,242 and moving; file gitignored by design). No pinned
  command can agree with a sentence twice. These need "live and
  monotonic as of <date>" labels, not guards.
- **19-of-21 export numerator**: denominator re-derives (21, above);
  the 19 needs the per-package judgment sweep (3 packages needed
  judgment). No single command; re-sweep or it rots on the next package
  add/remove.
- **README historical runs** (254/305, 13/13 observer, 47,428/55,794,
  latencies, n=662/n=5,733, 0.59, 2/3, 0/10, 5/5, 11/12): past runs with
  no cheap regen. Spot-checked one (29/29, above); the rest are
  trust-me numbers aging at the speed of their corpora.

## NO-CLAIM

Seven guarded claims, not the whole surface. Agree-tonight is not
agree-forever — that is exactly what the guard is for; run it when
quoting. Live numbers are not drift defects, but unlabeled-live numbers
become them.
