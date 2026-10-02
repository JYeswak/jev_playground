# PREREG — longres 48-hour temporal replication (jev-4se3 follow-up)

Frozen before analyzing eligible rows or live calls. Consumer: adjudicate whether
the original matched-miss savings result reproduces on later traffic, after the
observed overlapping-sample defect. Retirement: at 48-hour horizon, report PASS,
FAIL, or NOT ENOUGH DATA; no ongoing artifact.

## Population and collection

Eligible events are toolResult messages whose own SessionEntry `timestamp` is
>= 2026-10-02T22:00:00Z and < 2026-10-04T22:00:00Z, with text length >=10,000
characters. No pre-cutoff result is eligible, even from a session file modified
later. Scan omp session files across default and profile roots. Exclude every
source file whose SHA-256 canonical path occurs in any of:
`work/longres/corpus.json`, `work/longres-rep/corpus.json`,
`work/longres/corpus2.json` (130 unique files at preregistration). Before calls,
assert zero eligible-row source path hashes against that union and zero exact
full-result hashes against every prior corpus row. Split 200 rows into dev 100 /
held 100 by source file, deterministic seed 20261008; no file crosses split.
If fewer than 200 eligible rows or fewer than 20 REFERENCED and 20
UNREFERENCED held rows, stop NOT ENOUGH DATA, no live calls. Labels use the
frozen mechanical rule: REFERENCED iff any of three evenly-spaced 60-char
probes occurs later in the same source file. Record event timestamp and full
result hash in corpus; never include full result text.

## Frozen arms and analysis

Jev `Choice` `keep/summarize/drop`, prompt/classes/state construction, pinned
`jev-1.13.0`, 20s timeout, invalid/refused -> KEEP, exactly one call per row.
Question and class wording are verbatim from `work/longres/PREREG-longres.md`.
Baseline: DROP iff size >= T and tool in {read,bash,eval,grep,glob,find,
web_search,web_extract,fetch}; fit T on dev-100 with Youden-J, UNREFERENCED
positive, tie highest T. No tuning after calls.

Primary: held-100 matched-miss baseline. On held rows, choose threshold with
minimum absolute difference from Jev's referenced-drop miss count; ties choose
higher baseline savings on unreferenced rows, then larger T. Report exact miss
counts/rates, Wilson 95% CIs, and unreferenced savings (summarize saves
(size-400)/size, drop saves 100%). Jev advantage iff its savings strictly exceed
matched-miss baseline; report ratio and both absolute values. Secondary: frozen
original bar on held rows (Jev miss <= fitted baseline miss AND Jev savings >=
1.2x fitted-baseline savings). NO-CLAIM beyond eligible temporal population.

## Caps and schedule

Collection closes exactly at 2026-10-04T22:00:00Z. <=200 live calls, $0.015
spend cap at $0.042/M input tokens, no retry storm, stop immediately on 401/402/
403, checkpoint one row/call with status/tokens/latency, no raw result text in
receipt. Score, commit rows, scorer, corpus hashes and result after horizon;
never inspect interim model results or extend the window post hoc. Any extension
requires a new prereg before looking at outcomes.
