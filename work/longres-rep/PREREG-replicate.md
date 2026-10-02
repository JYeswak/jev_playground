# PREREG — longres independent replication (bead jev-4se3, OrangeFrog)

Frozen 2026-10-02 before any replay live call. Replicates WindyLantern's
longres (work/longres/PREREG-longres.md, commit 6622f7a4: Jev miss 0.04 vs
size baseline 0.31) on a DISJOINT population.

## Population (keyless, frozen)

Same roots and method as her `extract.py`: 200 long toolResults (>=10k
chars) from 7d sessions, split dev 100 / held 100 by file (no file in both).
Differences (all predeclared):
- seed 20261007 (hers: 20261006),
- LONGRES_EXCLUDE=corpus drops her exact 200 files (read from
  work/longres/corpus.json; her files never written),
- output work/longres-rep/corpus.json (hers untouched).
Her question, classes, timeout, invalid->KEEP rule, and runner shape reused
verbatim (runner copied to work/longres-rep/run_choice.mjs, paths local).

Labels (same mechanical rule, disclosed): REFERENCED iff any of 3
evenly-spaced 60-char probes appears later in the same file.

## Arms

- Jev: Choice keep/summarize/drop, state head350+tail350+task<=500,
  `jev-1.13.0`, 1 call/row, invalid/refused -> KEEP.
- Baseline: DROP iff size >= T AND tool in content tools, refit T (Youden-J
  on UNREFERENCED, tie-break highest T) on MY dev. No other tuning.

## Bar (held 100, fixed pre-call)

REPLICATE iff Jev miss rate <= baseline miss rate AND Jev tokens saved on
held UNREFERENCED rows >= 1.2x baseline savings (summarize saves
(len-400)/len, drop saves 100%). PLUS conductor's matched-miss comparison:
retune baseline T to match Jev's miss rate, compare savings at equal miss.
Report: miss both arms with Wilson CIs, savings both arms + matched-miss,
per-call model/status/tokens/latency/spend, exclusions. Either outcome is a
result (replication is confirmatory, not a ship decision).

## Caps

<= 200 calls, $0.015 cap (~$0.008 expected), stop 401/402/403, 20 s timeout,
checkpointed by sample_id. Receipt work/longres-rep/choice-rows.jsonl
(same columns as hers). NO-CLAIM beyond this sampled population.
