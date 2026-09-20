# Dig-vs-invent named-subset breakdown — pre-registered falsifier `[pending]`

Committed BEFORE scoring (rule 3, `docs/RULES.md`). Corpus is the LOCKED
export `work/cass-mail-mines/exports/cass-dig-rows.jsonl` (n=138, sqlite
recent-120k window, standing aggregate: always-invent 0.159420290 vs
dig-iff-count>0 0.057971014 BEAT). Scorer
`work/cass-mail-mines/scripts/score_dig_subsets.py` does not exist yet at
this commit. Loss frozen: invent-on-y1=1, dig-on-y0=2, else 0
(`cass_dig_y.py` mechanical Y).

## Named subsets (frozen regexes on query text, counts derived at run)

- **S_wrong_selector** (A08 slice):
  `/no such|missing field|does not exist|undefined|requireKey|distribution|customType|keys present|wrong selector/i`
- **S_lexical_trap** (A24 slice): `/cass|robot|\bTUI\b|noul|AGENTS\.md/i`
- **S_control**: `/zzzz_cannot_exist|negative control/i`
- **S_pass_probes**: `/ pass \d+$/` (the 30 repeated pass-N probes, lines 109-138)
- **S_topical**: everything else

A query may sit in two slices (e.g. lexical + pass-probe); per-slice
denominators are reported separately, no double-counting within a slice.

## What kills it

- **F1:** dig-iff-count>0 fails to beat always-invent on ANY named slice
  (S_wrong_selector, S_lexical_trap, S_control, S_pass_probes, S_topical)
  → **HELD**, even though the pooled aggregate BEATs. Pooled numbers have
  overturned 3/3 in this lane; a subset failure is the finding.
- **F2:** S_control shows any hit with y=1, or `zzzz` returns count>0 →
  harness RED (BLOCKED-HARNESS): the negative control fired.
- **F3:** empty-success rows (count>0 & y=0, standing count 4) — if
  always-pick-top-hit mean loss ≤ always-abstain on exactly those rows →
  note as RED against top-hit, not against dig-iff (dig-iff abstains only
  when count=0; it digs these and eats loss 2 — report the slice loss
  honestly).

## Outcome words

DONE = dig beats always-invent on ALL five slices (CLEARED on this window
only). HELD = F1 fires on any slice. BLOCKED-HARNESS = F2 fires. No
aggregate-only claim; the slice table IS the result.

## NO-CLAIM

Mechanical Y proxy, not human edit-delta. Sqlite recent-window, not
full-index cass search (index-busy, no rebuild started). n=138 with 30
near-duplicate pass probes — S_pass_probes measures stability, not breadth.
