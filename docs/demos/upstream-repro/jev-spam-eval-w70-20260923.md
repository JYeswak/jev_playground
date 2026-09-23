# jev-spam-eval W7.0 fresh run (2026-09-23, pane 4 MistyTurtle)

- jev HEAD at bar commit: `9e8199b`; run 2026-09-23.
- Clone: `jev-spam-eval @ 76ef183` (bitnovus, MIT). Status: only the 2
  pre-existing M results files (EVAL.md:1197 oracle note); verified by pane 4.
- Prior receipts are LEADS, never passes (lingspam-20260918.md,
  ood-20260918.json, EVAL.md:277).

## T4 BAR (preregistered — predates the first live call)

Pinned `jev-1.13.0`; shipped labelled splits, no pooling; per-split Noul
accuracy + CI; floor = `tfidf_baseline.py` SAME rows per split. Seat per
split iff Jev lower-CI ≥ floor.

## Results

| id | status | evidence |
|---|---|---|
| T1 | PASS | SHA/license/status/venv (py3.14.2, sklearn 1.9.1, typesafe-sdk 0.6.0 pinned) recorded. |
| T2 | NO-SUITE earned | No tests dir, no test config (verified by pane 4); experiment drivers only. Green intact in /tmp copy; plant 1 (body→'') SILENT degradation (uniques 2876→2614) — finding: no row-count self-check; plant 2 (THRESHOLD→'0.5') RED numpy UFuncNoLoopError. THRESHOLD line :52 confirmed by pane 4. |
| T3 | PASS | 7 claims: OOD gaps DEMONSTRATED live (S3 25.4pt, S4 21pt, S5 24pt); in-dist table PARTIAL (S1 0.9780 reproduces seed-42 single exactly); criteria-direction corroborated; caveat DEMONSTRATED-AS-RECORD; OOD table DEMONSTRATED (S5 urgency/names EXACT); repeat-agreement brackets 99.3%; 3-way in-dist LEAD-ONLY. |
| T4 | RAN | 4,878 scored rows, $0.2474, all envelopes jev-1.13.0 (verified by pane 4). S1 n=500 0.9780 [0.9610,0.9890] (recomputed 489/500). S2 n=2893 0.9848 [0.9796,0.9889], tp479 fp42 (recomputed). S4 n=853 share 0.9132 [0.8923,0.9313] (recomputed 779/853). S5 n=632 0.9731 [0.9573,0.9843], tp296 tn319 fp13 fn4 (recomputed via P(not_ham) rule). 1 dropped 403 row (client raises, never coerces). |
| T5 | PASS | Floors same rows: S1 CV 0.9580 (tie p=0.31); S2 CV 0.9855 (tie p=0.91); S3 0.7311 (Jev wins); S4 0.7034 (Jev wins); S5 0.7342 (Jev wins). S3 floor cross-checked by pane 4 against saved predictions file (2099/2876 = 0.7298, same order). Rulings: S1+S2 TIE/REFUSED, S3/S5 Jev-over-floor. |
| T6 | RAN | Adapter @ adffc2e + haiku + grok-4, same states/questions, McNemar paired. S1 ties; S2 haiku ties / grok loses (p=2e-7); S4 BOTH LLMs beat Jev (haiku 0.9461 recomputed 807/853, p=8.4e-06; grok p=5.6e-09) — strongest finding; S5 ties. LLM dollars unpriced. |
| T7 | RAN | Decile bins with counts per split; extremes calibrated; S4 single-class not-observable by construction (stated). |
| T8 | RAN | Repeats ≤0.95%, framing ≤2.58% per split. Pane-4 recompute S1 rep1-rep2: 3/500 vs runner 2/500 — same order, noted. ~$1.24 grand total. |
| T10 | MIXED | S1 TIE/REFUSED; S2 TIE/REFUSED; S3 SEAT-vs-floor (incumbent-neutral); S4 INCUMBENT/REFUSED; S5 SEAT-vs-floor (incumbent-neutral). NOT-RUN: phish 3-way in-dist (routes: live ~9,886 req ≈$0.76; keyless --report lead-grade). Tiers: C5-C6 DEMONSTRATED live; C1-C3/C7 lead-only. |

## Boundary

Single runs per arm; jev-1.13.0 only; public corpora may be in training data; S1 is a 500-sample of 18.5K; S2 incl. 17 exact dups (clone: 2876); no omp seam; nothing certifies Jev in general. No Rust in clone.
