# A18 off-bus ACK probe (precise K1 pair) — pre-registered falsifier `[pending]`

Committed BEFORE scoring (rule 3, `docs/RULES.md`). Prototype script
`work/cass-mail-mines/scripts/score_a18_offbus.py` does not exist yet at
this commit. Pair: mail project 66 (`/Users/josh/Developer/
clutterfreespaces.ios`, 287 ack_required=1 msgs, ALL unacked) ↔ cass
workspace 617 (107 conversations). Window frozen: ±24h.

## Measure (frozen)

For each of the 287 unacked ack-required msgs: cass conversations in
workspace 617 overlapping ±24h; content match (case-insensitive)
`%ACK%` OR `%reserv%` → off-bus candidate, else `stuck_wait`. Controls:
always-abstain (all stuck_wait); cheap-2 any-ACK-token ⇒ complete (must
RED on heartbeat — top-5 match sample read live, counts only into git).

## What kills it

- **F1:** 0 of 287 have ANY in-window cass conversation → REFUSE
  (UNMEASURED on this pair; no co-presence to judge, not yield-0).
- **F2:** candidate π ≈ 0 (<2% of 287) → HELD (no off-bus hole here; A18
  stays PREPARED elsewhere).
- **F3:** candidates exist but top-5 sample reads heartbeat-only →
  HELD (cheap-2 RED; needs a real reservation-vs-chatter grader, unbuilt).

DONE = π printed with exact denominator (287) + in-window coverage count.
No DONE past a count: Y-grading the candidates is a later unit.

## NO-CLAIM

Mechanical token co-presence, not handshake judgment. Live DBs, monotonic.
Content read live, never exported (ids/counts only — secret-scan before
git). Locked dig export untouched. No rebuild started.
