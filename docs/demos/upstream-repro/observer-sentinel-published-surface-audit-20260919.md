# Published numeric sentinel surface audit

**Unit:** P2-34
**Scope:** README.md numeric table cells, `docs/demos/STATUS.tsv`, and every numeric value-bearing
path under `work/omp-harm-rule/`. No source changes.

## Findings

| Published value / family | Source | Can silently default? | Note |
|---|---|---|---|
| README tool rows: 98.878%, 0.0447% | `README.md:116-117`; `demos/usage-shape/bin/shape.mjs`, `demos/routing-backtest/` | NO | static published values with named runnable artifacts; not runtime fallback fields |
| README repo census rows | `README.md:176-187`; linked receipts in each retained row | NO | literals backed by receipt paths; deleted unsupported rows are no longer published |
| README harm rows: 12/12, 0/38, historical 11/12 and 5/12 | `README.md:260-262`; `work/omp-harm-rule/verify-claim.mjs`, historical receipt | NO | deterministic row is recomputed; historical rows are explicitly marked historical |
| README ensemble rows | `README.md:336-339`; cited judgment/security receipts | NO | static historical receipt values, not runtime defaults |
| README compaction session rows | `README.md:357-362`; `compaction-retention-oracle-20260919.md` | NO | receipt-backed literals |
| README usage-share rows | `README.md:399-402`; `docs/demos/jev-probe/census-20260918.json` and usage-shape command | NO | committed census values and rerunnable command |
| README command inventory/fresh-clone rows | `README.md:637-647, 675-682` | NO | command descriptions, exit observations, and explicit prerequisite notes; no generated default field |
| README troubleshooting numbers | `README.md:719-724` | NO | literal guidance values, not persisted runtime measurements |
| STATUS rung/score/count columns | `docs/demos/STATUS.tsv:11-35` | NO | literal machine-readable state rows; each row carries a receipt path; no runtime default path |
| harm probabilities baseline `0.01` | `work/omp-harm-rule/harm-rule.ts:19` | NO | explicit deterministic prior assigned for every command class, not a missing-data fallback |
| harm fire probabilities `0.96` | `work/omp-harm-rule/harm-rule.ts:20-23` | NO | explicit regex outputs |
| harm rule cost `0` | `work/omp-harm-rule/harm-rule.ts:24` | NO | deterministic regex has no model call; this is an explicit known cost, not absent-cost substitution |
| harm threshold `0.5` | `work/omp-harm-rule/harm-rule.ts:63` | NO | explicit decision threshold |
| harm decision `score = ... : 0` | `work/omp-harm-rule/harm-rule.ts:53-60`, persisted at `:62-70` | **YES — STORED** | if `classify()` throws or probabilities remain null, the persisted decision score becomes numeric zero, indistinguishable from a genuine low-risk score; `error` is stored alongside it but consumers could ignore it |
| verifier expected counts and printed counts | `work/omp-harm-rule/verify-claim.mjs:47-58` | NO | counts derive from loaded arrays and decision rows; no missing-data fallback creates the published result |
| installer comments `12/12`, `0/40`, `11/12`, `5/12` | `work/omp-harm-rule/install-harm-rule.sh:14-16` | NO | static historical comments, though the `0/40` text is stale relative to the corrected README denominator |

## Result

R39's refusal is **overturned by its own trigger**. One reader-facing shipped artifact contains a
stored numeric sentinel: `harm-rule.ts:60` writes `score: 0` after classification failure. This is
the exact class R39 said would justify dispatching a scoped checker. No checker was built in this
unit, per instruction. The narrow next scope is the harm-rule error-score contract: preserve the
error and make absent score distinguishable from a measured low score.

## NO-CLAIM

This audit does not establish frequency, live traffic impact, or a production rate for the harm-rule
error path. It does not claim the README/STATUS literals are freshly rerun beyond their cited
artifacts. The only trigger-level defect established here is the source-level stored fallback at
`work/omp-harm-rule/harm-rule.ts:60`, persisted by the decision object at lines 62-70.
