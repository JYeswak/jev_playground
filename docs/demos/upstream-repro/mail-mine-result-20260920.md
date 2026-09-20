# Full mail-corpus mine — 2026-09-20 `[receipt]`

**Outcome: HELD for a seat; DONE as census.** Falsifier F1 fires
mechanically (99.5% ≥ 10%) and is then discounted by its own key audit:
the linkage is ambient co-presence, not action.

Falsifier pre-registered (`mail-mine-falsifier-20260920.md`). Miner
`work/cass-mail-mines/scripts/mine_mail.py`, read-only, 6,510/6,510 rows
(as-of: mail grows). No `body_md`, no subject text anywhere — ids,
counts, enums, paths only.

## Census (as-of mine run)

| | |
|---|---:|
| messages | 6,510 |
| threads | 4,509 (1,630 msgs, 25%, threadless orphans) |
| projects | 153 |
| reservations | 7,316 |
| ack_required=1 / acked msgs | 3,135 / 58 |
| threads with ≥1 acked msg | 7 |
| threads bead-linked | 3 |

## Linkage audit (the finding)

| key | threads |
|---|---:|
| reservation ±24h same project | 4,485 |
| ack acted-on | 7 |
| bead id | 3 |
| any (F1 test) | 4,485 / 4,509 = 99.5% |

The 99.5% is vacuous: reservations are dense (7,316 over active
projects), so any message in an active project sits within ±24h of one —
co-presence, the observer↔bridge lesson in a new place. The two
non-ambient keys total 10 threads: far too thin for a judge, and the
bead key is near-dead (numeric thread_ids vs `jev-*` bead ids never meet).
F2 does not fire (reservation key alive), but F1's pass carries no seat
information. Seat question HELD pending a non-ambient linkage definition;
nothing here clears a Jev call.

## NO-CLAIM

Structural features only; linkage is temporal co-presence unless stated.
Live-monotonic counts as-of run. One window, one machine. `[receipt]`
used throughout — the word exists and fits.
