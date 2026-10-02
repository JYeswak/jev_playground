# jev-28gx BAR (fixed 2026-10-02, before any two-question run; bead jev-28gx)

Source: duel round 2 LUNA idea 2 (MUSE2 820). Keep precision ~0.22 (jev-m959);
single-question rewording exhausted (R137, jev-9tkx). One variable: conjunction
of two independent Noul questions. Frozen question pair, CUT=0.5 each, live
jev-1.13.0 only, pilot spend cap $0.02/day. Nothing wired live until verified.

Q1 (useful): "Memory: `memory`. Current request: `prompt`. Would acting on
this memory change what you do next, or is it background you already have?
Answer usefulness only."

Q2 (current): "Memory: `memory`. Current request: `prompt`. Is this memory
usable for the request as it stands now -- current and applicable, not a stale
dispatch from an earlier turn and not a mere restatement of the request?"

Gate: KEEP iff Q1 >= 0.5 AND Q2 >= 0.5, else DROP.

## Populations (frozen)

- DEV (170): the 9tkx committed slice rebuilt at runtime from
  work/jev-m959/labels.json + sample_organic.json (44 keeps minus bad
  o01,o03,o14,o15,o30,o40) + work/jev-9tkx/s47b-keys.json joined to the local
  sidecar (30 drops) + work/jev-wb7j-lossdepth heldout (96 IRRELEVANT drops).
  expectKeep from committed labels. No new labels by me.
- HELD-OUT (40): fresh sidecar pairs ts >= 2026-10-02T00:00Z, seed-28 sample,
  my blind labels frozen in heldout-labels.json (2 relevant: h08, h23; 38
  irrelevant). Texts joined at runtime by hash prefix; labels predate all runs.
- PLANTED (planted.json): (a) useful-old memory from m959 relevant o01 with a
  prompt it serves -> must KEEP; (b) memory restating the request -> must DROP.

## WIN iff all hold (dev, then held-out)

1. keep precision >= 0.42, 2. drop precision >= 0.90,
3. zero labelled-critical (relevant) memories dropped,
4. irrelevant injected tokens/turn down vs single-question base on the same slice.
5. Spend within $0.02/day cap, stated per run.

FAIL -> NEGATIVE_EVIDENCE with model-limit verdict (R137 lineage).
NO-CLAIM: drop precision beyond labelled sets; usefulness of kept memories.
