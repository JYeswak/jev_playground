# PREREG — failtriage tracks A+B (bead jev-irkq)

Frozen 2026-10-02 before any label or Choice call. xdzh single-Noul FAIL
(0.697 vs 0.753 majority) leaves the area open.

## Track A — deterministic detector (no model)

`work/failtriage/detect.py`: failure signals (isError, nonzero exit,
Traceback/Error/FAIL/Fatal/permission/command-not-found/No-such-file/
EACCES/ENOENT/panic) + next-turn check (no same-tool retry, no edit/write,
no error-token mention). Newer failures replace open ones (looseness noted).
Sample: 100 seeded rows (sha `e7ed1796e417`) from 4,118 candidates / 7d.

## Blind labels (all 100, before any Choice score exists)

Per row (failure span + next 2 turns): ADDRESSED (the skip didn't happen —
handled, retried, mentioned with effect, or the "failure" is benign output);
HARMLESS-IGNORE (real skip, inconsequential); HARMFUL-IGNORE (real skip, a
reasonable operator wants a nudge: blocked progress, data risk, wrong path).
Labels in `work/failtriage/labels.json` (sample_id -> {label}); corpus file
untouched post-sha.

## Bar A (fixed pre-label)

Nudge ON iff blind precision P(HARMFUL-IGNORE | would-nudge) >= 0.80
(Wilson reported). Else the nudge stays off.

## Track B — Choice, different primitive+pattern from xdzh

`askJevChoice` over {addressed, harmless-ignore, harmful-ignore}; state =
failure span + next 2 turns text (≤1500 chars each). Predict HARMFUL iff
P(harmful-ignore) >= cut, cut = Youden J fit on DEV (first 50 f000–f049),
tie-break lowest. Report HELD (last 50 f050–f099) paired vs track A on the
same rows. Bar B: held precision >= A precision AND held miss <= A miss
(miss = HARMFUL-IGNORE allowed / all HARMFUL-IGNORE).

## Caps

<= 100 Choice calls, $0.01 cap (~$0.004 expected), stop 401/402/403, 20 s
timeout, checkpointed by sample_id. Runner `work/failtriage/run_choice.mjs`;
receipt `choice-rows.jsonl` (sample_id, choice, probabilities, pred, status,
tokens, latency; no raw text). NO-CLAIM beyond sampled ignored-failure rows.
