# README claim sweep, part 2: scope, receipts, reader paths (2026-09-20)

Level: `test` (every runnable below ran, exits unpiped; no Jev calls).

## STALE fixed (1)

- compaction/README "npm test 32/32" → 38/38 (ran: 38/38 exit 0; no conflicts, reserved).

## CONFIRMED, weighted per dispatch (scope / self-contradiction / reader paths)

- Compaction hook scope ("install into any repo, omp asks before compacting"):
  installer writes `.omp/hooks/pre/jev-compact.ts` (+lib+skill+receipt); entry
  present in this repo; live-seam receipt `docs/demos/omp-seam-live-20260918.md`
  exists. No overclaim found.
- Mutated-rule detection (777→778): recall 10/12, verifier exits 2; file
  restored byte-identical (`git status` clean) and re-verified exit 0.
- Foreign-shape scope: `shape.mjs` on non-session JSONL → exit 3
  `ERROR EMPTY_SCAN_SET` — visible, not silent zero. The "reports zero turns"
  sentence understates slightly (it errors rather than reporting 0) but the
  load-bearing half — never a silent zero — holds.
- Installer honesty (backup/rollback/never-overwrite): all three in
  `install-harm-rule.sh` (lines ~108-111, 145, 151) with the measured defect
  that motivated them cited in comments.
- Census models: 408,265 / 49,842 / 15,658 + six others, 4,619/488,724/4,626/0
  — all in `census-20260918.json` denominator/by_model.
- 30-turn 0.0447%: backtest README names the input ("our own 30 turns, 2
  sessions") and receipt carries counts; probe-state-closure recomputed it.
  Nuance: the root README's printed command runs a 6-turn fixture (harness
  demo), not the 30-turn figure — same code, smaller denominator. Not a
  contradiction, but a reader re-running the command gets 6 turns, not 30.
- whatif residual: `unreconciled tokens 0` on clean fixture, exit 0;
  assumptions + notModeled in receipt. Hostile dir exits 1 on the malformed
  fixture — honest failure, and the README never claims otherwise.
- jev-probe: no key → exit 2 with the infisical line (troubleshooting row
  exact); `--replay` exit 0, model jev-1.13.0, live lane NOT_RUN.
- node>=20 declared in all three tools' package.json. All essay/doc links
  (dont-give-up ×3, INTEGRATIONS, SDK-SURFACE) + `.env.example` (projectId
  matches README's infisical line) exist.
- R20 exists (NEGATIVE_EVIDENCE.md:814). Ablate harness receipt exists
  (ablate-rerun-classD-20260919.md). Ensemble missing-clone path prints the
  exact `git clone` (run_all.py:76-80) — reader path intact.
- 20,000-token default: `DEFAULT_POLICY.maxPromptTokens = 20_000`
  (counterfactual.mjs:5) — the "demo's policy" sentence is exact.

## UNVERIFIABLE, kept as UNVERIFIABLE (2 new)

- Six-session compaction table (155,837→104,443 etc.): session names appear
  ONLY in root README; committed replay receipts lack per-session char counts.
  A reader cannot re-derive a single row. Not contradicted — unsourced.
- "Three of those were real holes found under a green suite": no source in
  routing docs/runs/receipts. Current 7/7 proven live; the history is not.

## Prior five stay UNVERIFIABLE (no command found; not upgraded).

## Verification: stage 97 exit 0 (root README untouched in part 2).

## Ledger line

SWEEP readme-part2 — 1 STALE-fixed (compaction 32→38), scope/receipt/paths all CONFIRMED except 2 new UNVERIFIABLEs — NO-CLAIM: six-session rows and three-holes history unsourced, left as written.
