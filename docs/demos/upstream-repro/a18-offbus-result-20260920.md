# A18 off-bus ACK probe (precise K1 pair) — 2026-09-20 `[pending]`

**Verdict: REFUSE** (F1: 0 of 287 unacked ack-required msgs have ANY
in-window cass conversation). UNMEASURED on this pair — not yield-0. And it
generalizes: all 20 K1 pairs are time-disjoint (table below), so A18's
in-window join is unmeasurable on every K1 pair tonight.

Falsifier pre-registered at `555c005`
(`a18-offbus-falsifier-20260920.md`) before `score_a18_offbus.py` existed.
Pair: mail project 66 (`/Users/josh/Developer/clutterfreespaces.ios`, 287
ack_required=1, all unacked) ↔ cass workspace 617 (107 conversations, 99
with ACK/reserv tokens somewhere in history). Window ±24h frozen.

## Result

| | |
|---|---:|
| denominator (unacked ack-required, proj 66) | 287 |
| in-window coverage | 0 |
| off-bus candidates | 0 |
| π(candidate) | 0.0 |

## Why: eras disjoint

- mail proj 66: 2026-08-31 → 2026-09-01.
- cass ws 617: 2026-06-17 → 2026-07-27.
- Five weeks apart; no ±24h window bridges it.

All-20-pair range check (mail min/max vs cass min/max, ±24h): every pair
`disjoint`. Path-join without time-join is exactly the observer↔bridge
lesson — co-presence ≠ id-join, and here even co-presence is absent.

## Method note (caught, not shipped)

First run compared raw timestamps: mail `created_ts` is MICROseconds, cass
`started_at/ended_at` MILLIseconds. The scorer normalizes to seconds
(`score_a18_offbus.py` header). An unnormalized comparison also yields
zero — same number, wrong reason. The era table above is the real reason.

## NO-CLAIM

Token co-presence design, unexecuted beyond coverage (no candidates to
grade). Content read live only as counts, never exported (ids/counts
only). Live DBs, monotonic. Locked dig export untouched. No rebuild
started. Not a promotion (`promoted = 0`).
