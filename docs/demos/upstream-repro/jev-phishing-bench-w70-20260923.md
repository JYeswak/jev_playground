# jev-phishing-bench W7.0 fresh run (2026-09-23, pane 4 MistyTurtle)

- jev HEAD at bar commit: `9e8199b`; run 2026-09-23T03:38Z.
- Clone: `upstream/anisselbd/jev-phishing-bench @ 1d56e8c` (anisselbd, NO
  LICENSE). `git status` empty before and after (verified by pane 4).
- Corpus: `data/emails.jsonl` 2000 rows on disk (recounted by pane 4).
- Prior receipts are LEADS, never passes (phishing-20260918.md, EVAL.md:279).

## T4 BAR (preregistered — predates the first live call)

Pinned `jev-1.13.0`; full corpus (affordable); verdict-choice accuracy + CI;
floor = clone regex+eTLD rule same rows. Seat iff Jev lower-CI > floor;
lead predicted REFUSED class A.

## Results

| id | status | evidence |
|---|---|---|
| T1 | PASS | SHA/license-absence/status clean; Python 3.14.2 via uv; host/version recorded. |
| T2 | PASS | No committed suite (no tests/, no `def test`). Keyless floor exits 0; plant (`registered_domain`→'' in /tmp copy) drops floor 0.9165→0.6055, restored + re-verified. Floor computation can fail both directions. |
| T3 | PASS | 5/5: Jev 62.6% vs Haiku 81.3% (committed metrics.json exact; live rerun 0.6298 consistent); floor 91.6%/83.5%/0.2% recomputed exact just now; split-B McNemar p=0.003156 from artifact; regression tie p=0.06297 from artifact; costs $0.0385/1k Jev vs $0.9295/1k haiku-arm fresh. |
| T4 | RAN, seat REFUSED | 2000 calls (1999 ok, 1 transient Cloudflare 520 recovered pass 2), model jev-1.13.0 in envelopes. Verdict 0.6298 CI [0.6084, 0.6507], recall 0.4334, FPR 0.1740. p50 195ms p95 368ms. $0.0769. Tallied by pane 4 from raw rows (1259/2000, 1257/2000). |
| T5 | FLOOR WINS | Floor same 1999 rows recomputed by pane 4 via analyzer: 0.9165 CI [0.9035, 0.9278]. Bar: 0.6084 ≤ 0.9165 → REFUSED class A. |
| T6 | PASS | Adapter @ adffc2e + haiku-4-5, same email state + verdict wording, 400 shared rows (seed 20260923): Haiku 0.7475 CI [0.7027, 0.7876] (tallied by pane 4: 299/400); discordants 72/28, McNemar p=1.3e-5 → incumbent better. $0.3718, p50 0.87s. |
| T7 | PASS | 10 bins n=1999, ECE 0.1611, largest bin 22.2% — observable. |
| T8 | PASS | Repeats flip 48/1999 (2.4%), 2-3/200; reword agree 0.799/0.796. |
| T10 | REFUSED, class FLOOR | Regex (91.65%) and incumbent (paired p=1.3e-5) both beat Jev verdict (62.98%). What Jev keeps is decomposition price (~1/25 cost), not re-measured here. |

## Boundary

One dropped row (transient 520). Public corpus may leak into training. No Rust in clone.
