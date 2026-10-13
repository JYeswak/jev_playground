# Cohort-C tail split manifest — lane jev-b35c.32.5 (CobaltCoyote, 2026-10-13)

DB-only work pending Beige flush. If an import runs first, re-apply from this record.

## Snapshots (canonical compact-JSON SHA-256, Cyan-compatible)
- jev-n6-outcome-logging-vfnv: d536b7021485cf4e4ec3a36489f1354c367288049b2615523833146322032be8 (611+3540 chars)
- jev-np5k: dcd43f9ab6b2b5f30d8d434159e1dd09527ae20b23915fbd2796023c30b13b9c (2342+1690 chars)
- Cyan-preserved (skipped, no duplicate): pifg/6b60eaec (C2926), q3q8/fe58391e (C2927), s0ve/9910f9c4 (C2928), x2/67b03f03 (C2931), x3su/acc863de (C2932), x6/ad5f6ec2 (C2933), x8/0589e881 (C2934)

## Units (all open, parent-child to original, no parent->child blocks anywhere)
- jev-n6-outcome-logging-vfnv.1 (1256 chars): persistence + PREREG floor. No blocks edges.
- jev-n6-outcome-logging-vfnv.2 (1539 chars): join/measure/fixtures/gates. No blocks edges.
- jev-np5k.1 (1410 chars): wiring + contract. Blocks: umcw, b35c.29, b35c.17.
- jev-np5k.2 (1147 chars): L3/value/SHIP. Blocks: grzn, mvvh.

## Lane edges this session (all metadata shard, actor CobaltCoyote, --no-auto-flush)
32.2 mapping: grzn.3->wbel, b35c.4.2->oy76, b35c.4.3->k3yw.
32.2 slots: brxq->b35c, s49q->b35c, xky7->b35c, z66l->b35c (all parent-child).
32.5 splits: 4× parent-child above + 5× unit blocks above.
Pre-existing edges relied on (not mine, do not remove): n6->n0-sclo (blocked), np5k->{b35c.29, acs2, umcw, grzn, b35c.17, mvvh}.

## Roll-ups (open, slimmed, history in snapshot comments)
- n6: 4151 -> 751 chars. np5k: 4032 -> ~590 chars.
