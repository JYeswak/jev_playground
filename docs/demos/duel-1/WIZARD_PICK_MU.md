# Decision memo: build the routing backtest first (duelist B, muse)

**Pick: merged Pair 1 — routing backtest over our own omp logs**
(MU-1 ≡ CC-3, merged spec in `WIZARD_MERGE_MU.md`). One page, as ordered.
Not picked on authorship: it is half mine, and the strongest case against
it is answered at the bottom.

## Why it beats the other five right now

- **vs fact ledger (CC-1):** the ledger question is real but right-sized as
  a *spike*, not a demo — one fixture, three questions, one receipt under
  the existing A/B schema, no install matrix, no WIP slot consumed. The WIP
  limit governs demos; experiments receipt freely. Run the spike in parallel
  (it takes a day); spend the demo slot on the backtest.
- **vs admission screen:** the screen needs a shadow period first — live
  traffic, FP adjudication, unmeasured per-read cost. Slow by construction.
  The backtest needs only disk and finishes in an afternoon.
- **vs claim-checker:** Phase 1 is narrow (commit subjects carry few
  checkable numbers) and a false-positive blocks real commits — fleet
  friction risk on day one. The backtest is read-only; it cannot block
  anyone.
- **vs signals starter:** no lane payoff until a corpus lands (N≥50 gate,
  автор's own condition). Correctly built later.
- **vs foreman-lite:** live bead path + positives-only labels + shared-tree
  concurrency hazards — three unsolved problems, all load-bearing. Build
  after the lane has a cost evidence base, not before.
- **Positive case:** every per-event demo in this duel (screen hook, hook
  L4 validation, any router) needs committed per-decision cost tables to
  argue shippability. The backtest *produces* those tables while paying for
  itself in routed-down dollars. It is prerequisite evidence disguised as a
  demo — build the thing every other ship criterion cites.

## Four ship artifacts

1. **Install:** `npm run backtest -- <transcript.jsonl> [--out
   runs/<ts>.json]` (TS, matches the adapter it reads). Refuses without a
   transcript; idempotent.
2. **Tests + RED arms** (merged set, 7): frontier-needed trigger,
   empty-transcript ERROR, missing-price-model ERROR, all-hard≈0,
   all-trivial≈max, UNPARSED-denominator, determinism-across-runs, plus
   pane 2's negative control (absent price ⇒ no counted savings).
3. **Receipt:** turns N, routed-down k, ledgered $, latency p50–p99,
   threshold, price-table `as_of`, model versions.
4. **EVAL row:** window (≥500 turns, ≥2 panes), Boundary (unreplayed
   traffic named), rung L0+L1 (no live routing exists to validate against).

## Falsifiable ship criterion

Ships iff, on ≥500 real turns across ≥2 panes: ≥25% routable-down at
ledgered prices, determinism check green, per-turn log spot-checkable.
Otherwise it stays a harness with an honest receipt — still useful, not
shipped.

## The kill arm (what abandons it after building)

**Re-escalation audit, one month live:** if turns the backtest routed down
get re-escalated to frontier >30% of the time once a live router exists —
the decisions were wrong, not cheap — abandon router pursuit and keep the
harness as the receipt that killed it. Secondary kill: measured decision
overhead exceeds turn-time savings for two consecutive windows. A demo with
no kill arm is an aspiration; this one has two, dated and counted.

## Strongest argument against this pick, answered

*Cost-first while the correctness question burns is misordered: demo-1's
core claim (pruning beats summary) stands refuted 1–3, and the ledger spike
that could overturn it should own the slot.* Answered twice: (a) slot
economics — the spike does not need the slot, so ordering is parallel, not
serial; block the demo slot and you serialize what could run concurrently.
(b) Evidence dependency runs the other way too — the ledger arm's own
receipt needs per-decision cost lines (2 bounded batches vs summarizer
call) to argue it wins *at comparable price*, and those lines come from
exactly the price-table machinery this demo builds. Backtest first funds
the ledger's argument.

## NO-CLAIM

Recommendation, not measurement. No backtest built, no turn replayed, no
dollar counted. The 25% / 500-turn / 30% numbers are pre-registered bars
for the build to clear, not findings.
