# jev-wb7j REPORT (WildCarp, 2026-10-01) — VERDICT: FAIL (precision)

## Bar (preregistered in bead comment BEFORE outcomes)
- 100 sampled (prompt, memory) pairs, seed 42, blind human labels (borderline → RELEVANT).
- One Noul per pair, `jev-1.13.0`, DROP iff noul < 0.5, invalid → KEEP.
- PASS iff precision_of_drop ≥ 0.90 AND token_reduction ≥ 0.40.

## Census (keyless, 7d session files, cutoff 2026-09-24T08:30Z)
- 270 files walked, 84 sessions. 76/84 session_init `<memories>` hits are
  documentation prose, not injections. Real ambient blocks: **8 session_init
  blocks (328 items, ~9.6k tokens) + 6 ee-task-context blocks (19 items,
  ~1.4k tokens)** = 347 pairs. Sampled 100 (96 session_init + 4 EE).
- Boundary: per-turn Mnemopi `<memories>` seen live in-context is NOT
  persisted to session files; file census undercounts live per-turn volume.
  Absolute opportunity is small: ~11k memory-block tokens / 7d on disk.

## Blind labels (frozen BEFORE live calls, labels.jsonl)
- RELEVANT 21 / IRRELEVANT 79. Relevant tokens 548/1989 (27.6%).
- Oracle ceiling: dropping all 79 saves 72.4% of memory tokens.

## Live run (score_live.mjs, bounded)
- 100/100 ok, 0 retries, 0 aborts. Median latency 119ms.
- Input tokens 79,441 → spend **$0.0033** at $0.042/M. Rows: rows.jsonl.
- Key via `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- ...`; never in tree/logs.

## Result @ tau=0.5 (pre-committed, no tuning)
- Jev DROPPED 91/100 (kept 9). TP=75 FP=16 TN=4 FN=5.
- **precision_of_drop = 75/91 = 0.824 (< 0.90 → FAIL)**
- **token_reduction = 1704/1989 = 0.857 (≥ 0.40 → pass)**
- Overall: FAIL. NO-CLAIM: no hook built; no design bead filed.

## Autopsy of 16 FPs (keyless, no extra spend)
- 8/16 are my borderline→RELEVANT calls on generic facts/practices
  (model-id pin ×3, receipt-generation practice ×2, sample-rate caveat ×3):
  label-noise direction, not model failure. A strict rule flips most.
- 6/16 are live hook/gate receipts vs prompts that explicitly forbid live
  material ("Do not use live Jev/API/keys"): Jev's DROP is arguably correct;
  my "bears on the topic" label is debatable.
- 4 missed drops (kept junk): opaque SHAs/commits scored 0.51–0.64 —
  near-threshold, low-cost misses.

## Ranked one-variable hypotheses (follow-up bead, NOT run here)
1. Label rule too lax: strict re-label ("directly usable in the demanded
   response") may pass precision with zero model change. (Tests oracle.)
2. Question underspecified: add criterion sentence ("would quote or act on
   this memory while doing the task"); replay on the 21 disputed pairs.
3. Prompt-length dilution: score (task-slice, memory) not (full-task, memory).
4. tau operating point: ROC needs a FRESH prereg sample (bar forbade tuning).
5. Wrong primitive: Choice keep/drop or Score-with-rubric instead of Noul.

## Artifacts (work/jev-wb7j/)
BAR.md, census.py, census.json, sample.jsonl, label.py, labels.jsonl,
labelsheet.txt, score_live.mjs, rows.jsonl, REPORT.md.
Reproduce: `python3 census.py` (keyless) then infisical-wrapped
`node score_live.mjs` (≤110 calls, ~$0.004).
