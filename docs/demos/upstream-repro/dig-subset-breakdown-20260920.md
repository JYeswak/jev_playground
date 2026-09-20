# Dig-vs-invent named-subset breakdown — 2026-09-20 `[pending]`

**Verdict: HELD** (F1 fires on S_wrong_selector: dig-iff 0.500 LOSES to
always-invent 0.250). The pooled aggregate BEAT (0.058 vs 0.159) does not
survive the slice table — the fourth pooled number in this lane to fall to
named subsets.

Falsifier pre-registered at `ffef6d7`
(`dig-subset-falsifier-20260920.md`) before `score_dig_subsets.py` existed.
Corpus: locked `exports/cass-dig-rows.jsonl`, n=138, sqlite recent-120k.
Loss frozen: invent-on-y1=1, dig-on-y0=2. Mechanical Y, not human labels.

## Slice table (mean loss; lower wins)

| slice | n | y_dig | always-invent | dig-iff-count>0 | beats? |
|---|---:|---:|---:|---:|:--|
| S_wrong_selector (A08) | 16 | 4 | 0.250 | **0.500 LOSE** | no |
| S_lexical_trap (A24) | 20 | 3 | 0.150 | **0.000** | yes |
| S_control | 2 | 0 | 0.000 | 0.000 tie | UNDERPOWERED (n=2, cannot separate) |
| S_pass_probes | 30 | 0 | 0.000 | 0.000 tie | UNDERPOWERED (zero positives — policies identical by construction) |
| S_topical | 82 | 15 | 0.183 | **0.000** | yes |

Control check clean: `zzzz` count=0, y=0; no control-slice y=1 anywhere —
no BLOCKED-HARNESS (F2 silent).

## Reading

- The aggregate win was carried by S_topical (82 rows, dig perfect 0.000)
  and S_lexical_trap (dig perfect). On wrong-selector queries — the A08
  slice, the exact failure mode G6 names — digging doubles the loss versus
  inventing (0.500 vs 0.250): hits exist (`count>0`) but answer nothing
  (Y=0), and each costs loss 2. Empty-success rows: 4, all in losing slices.
- S_control (n=2) and S_pass_probes (zero positives) are UNDERPOWERED:
  no direction reported. The HELD rests on S_wrong_selector alone (n=16,
  outright loss 0.500 vs 0.250), so the verdict does not depend on ties.
- Implication for playbook A: a blanket dig-iff-count>0 policy is wrong on
  exactly the queries where a pane most wants to dig (absence-claims). The
  cheap local refusal (`count>0` ∧ zero Y-eligible, A12) is the load-bearing
  ship for that slice, not a louder dig rule.

## NO-CLAIM

Mechanical receipt-shaped/wrong-selector Y, not human edit-delta. Sqlite
recent-120k window, not full-index search (index-busy, no rebuild started).
30 of 138 rows are near-duplicate pass probes — S_topical breadth is
thinner than n=138 suggests. Not a promotion (`promoted = 0`).
