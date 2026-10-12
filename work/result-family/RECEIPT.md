# N1 result-family receipt

## Overall N1 bake-off

**NOT_RUN.** No N1 main-arm result, winner, ship decision, or model-quality claim is recorded here. The time-window dataset below is a separate, already-scored dataset under its pre-existing preregistration; it is not pooled with the N1 held-session arms.

## Folded dataset: jev-4se3 temporal replication

Source preregistration: [1mwork/longres-rep/PREREG-timewindow.md[0m, frozen at commit [1mfba075a1[0m before the 2026-10-02T22:00:00Z to 2026-10-04T22:00:00Z collection window. The population is 200 long toolResult events (100 DEV, 100 HELD), split by source file with no file crossing the split. The committed sample refuses overlap with the three preregistered prior corpora and contains no full result text; the non-mutating checks are covered by [1mtest_committed_sample_is_disjoint_and_has_no_full_result_text[0m and [1mtest_old_excluded_corpus_is_never_a_write_target[0m.

Reproduction (offline, no new Jev calls):

- [1mpython3 -m unittest work/longres-rep/test_score_timewindow.py -v[0m — 6 tests passed, including the planted later-read miss, zero-drop comparator refusal, hash mismatch refusal, disjointness/no-raw-text check, and protected excluded-corpus path.
- [1mnice -n 10 python3 work/longres-rep/score_timewindow.py --corpus work/longres-rep/timewindow-corpus.json --rows work/longres-rep/timewindow-rows.jsonl --json[0m — PASS, 200/200 recorded calls scored.

| Measure | Jev | HELD-matched baseline |
|---|---:|---:|
| REFERENCED misses | 11/44 (25%) | 11/44 (25%) |
| HELD-row miss rate | 11/100 (11%) | 11/100 (11%) |
| UNREFERENCED characters saved | 752,560 | 429,328 |
| Savings ratio | 1.7529× | — |

Primary result: **PASS** (equal HELD miss count; Jev savings strictly greater). The frozen secondary original bar is **FAIL**; keep that verdict distinct. The scorer reports 148,990 input tokens, $0.006258, median latency 187 ms, and weekly Jev savings estimate 4,180,471 tokens for this window only. Corpus SHA-256: [1m706754624f46db70bb92fc1ced3aea8491911d945a631bb07b989a5974930a33[0m; rows SHA-256: [1m86a6d02ab9f2965df57f7039c07ee64fbf0ed4f2fa20bac307c7565ccc66d3c7[0m.

## Distinct prior replication failure

The earlier independent 7-day replication in comment 1527 remains a separate FAIL: savings 21.6 against an 82.8 bar. Comment 1540 records the separate time-window preregistration, not a run. The temporal dataset above neither replaces nor reverses the earlier result; this receipt's temporal result is backed by the committed rows and scorer rerun.

## Boundary

No new live calls, no N1 main-arm scoring, and no deployment or general-population claim. This receipt records the folded temporal dataset only.
