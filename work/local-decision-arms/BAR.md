# Local decision models vs jev-1.13.0 on Banking77 (bead jev-576e)

Committed before the first scored local call (one warm-up probe on row i=0 is excluded from scoring).

- Data: `work/choice-banking77/full.jsonl` (PolyAI Banking77 test split, 3,080 rows, not ours).
- Sample: 600 rows, `random.Random(7).sample(range(3080), 600)`; same rows for every arm.
- Incumbent: committed `work/choice-banking77/rows-full-jev.jsonl` (jev-1.13.0, recorded answers).
- Arms: Kev-4B (jaredpalmer/kev-4b @ c4bfa11, kev rev 5f78968, local MPS, `127.0.0.1:8009`);
  Clef-flash (Cloudflare/clef-flash, local) when it serves.
- Request: identical to `run.py`: state `{"customer_message": text}`, one Choice `intent`,
  instructions "The primary intent of this customer banking message", 77 humanized labels.
- Metrics: top-1 accuracy, ECE (10 equal-width bins on chosen-option probability), median latency.
- Bar (per arm): PASS if accuracy >= jev accuracy on the same 600 rows minus 0.02 AND ECE <= jev ECE.
  Otherwise FAIL. A paired McNemar p-value is reported, not used as the bar.
- Errors: more than 6 failed rows (1%) = run FAILED, not scored.
- Spend: $0 (local); no TypeSafe call is made (jev answers are the committed rows).
