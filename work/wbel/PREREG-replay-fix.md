# PREREG — wbel replay fix, ONE variable: preceding work in state (bead jev-wbel)

Frozen 2026-10-02 before any fix live call. Parent replay (PREREG-replay.md):
veto rate 0.790, precision 0.335, miss 0.881 at cut 0.40 — STAY-SHADOW.
Failure mode: undescribable-load veto + low separation on organic stream.

## Variable (exactly one)

State gains the turn's PRECEDING task tool calls (deployable: known at load
time; post-load `following` trails are NOT used — leakage). Question, cut
(0.40), description resolution, fail-open direction all unchanged:

- state: { request, recent_work: ["bash <cmd>", "read <path>", ...] } (<=6,
  same capture shape as the corpus `following` field, but from BEFORE the load)
- question: identical fitsQuestion wording.

## Dev rescore (exploratory)

Rescore the SAME 200 labeled rows with enriched state (200 calls). Advance to
fresh confirm iff dev precision >= 0.60 (worth confirming) — else report FAIL,
no fresh spend.

## Fresh confirm (preregistered)

New seed sample N=150 from loads NOT in the dev 200. Blind-label all 150
before scoring. Confirm PASS iff fresh precision >= 0.60 AND vetoes >= 20
(else NO-DECISION). Enforcement bar unchanged (0.80/0.10 on a full sample) —
this confirm tests the FIX, not enforcement.

## Caps

<= 200 dev + <= 150 fresh = <= 350 calls, $0.015 cap (~$0.012 expected), stop
401/402/403, 20 s timeout, checkpointed. Runner `work/wbel/run_refix.mjs
--phase dev|fresh`; context `work/wbel/replay-devctx.json` (keyless,
`work/wbel/extract-ctx.py`); receipts `replay-dev2.jsonl`,
`replay-fresh-{corpus,labels,rows}`.
