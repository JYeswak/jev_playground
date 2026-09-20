# NEGATIVES — where the three mechanisms say nothing

Boundaries, not failures. Each entry names a concrete input shape on which
the mechanism stays silent or refuses, and states what the mechanism CANNOT
establish there. No Jev calls; all shapes below are offline and reproducible
from the cited sources.

Provenance: Pass-6 live scan `node work/jev-eval-honesty/pipeline-run.mjs`
(2026-09-19), first run:

```
"LIVE matched=15529 unmatched=0 zeroHit=false presence=ABSENT-NEXT-TO-FIRING
top3=[dcg_allow:8310,lane_allow:7111,dcg_block:108]
ownConstant=0.5351(8310/15529,label='dcg_allow') randomBaseline=0.4954
[kind-as-label skew baselines only, NOT judge quality] files=40"
```

Counts move between runs (live session logs append while agents work);
shapes do not. Real row shape from the scan (session
`2026-09-16T15-52-23-093Z_01a0aaeb`, `com.zeststream.omp-dcg-bridge.decision.v1`):
`data:{kind:"dcg_allow",toolCallId:"call_…|fc_…"}` — two keys only, no
`outcome`/`error`, no bare `id`.

## 1. outcome-join (`joinOutcomes`, outcome-join.mjs)

- **B1 — rows with none of the verdict keys → `unmatched: "no-verdict-key"`.**
  Input shape: parsed rows whose `data` carries none of
  `["kind","outcome","error","verdict"]`. Real example: the Pass-5 scan —
  with an outcome/error-only key list the join matched **0/15499** live
  dcg-bridge rows (every row `no-verdict-key` under that list; the Pass-5
  fix widened the default to include `kind`). Reproduced offline: a row
  `data:{note,toolCallId}` with `expectKey:["kind"]` lands in
  `selectorReport`, and with no verdict key at all lands in `unmatched`.
  CANNOT establish: that no decisions fired — only that no row carried one
  of the named keys. A zero-match join is evidence about the key list, not
  about the world.
- **B2 — wrong join key → `unmatched: "missing-id:<idKey>"`, possibly `zeroHit`.**
  Input shape: rows keyed `toolCallId` joined with `idKey:"id"`. Real
  example, recorded in pipeline-run.mjs: `idKey "id"` joins **0/15523** —
  every live row `missing-id:id` — while `idKey "toolCallId"` joins all of
  them. CANNOT establish: that the decisions are unjoinable or absent, only
  that none carried that particular join-key field. Downstream, this is the
  shape that arms the zero-hit refusal rather than a finding.
- **B3 — rows failing the selector → `selectorReport`, never joined.**
  Input shape: parsed rows missing ≥1 `expectKey` field (Pass-6:
  `expectKey:["kind"]`). Reproduced offline: two rows missing `kind` yield
  `matched=0, selectorReport=[…missing:["kind"]…], zeroHit=true`. In the
  Pass-6 scan this branch stayed silent (all 15529 decision rows carried
  `kind`). CANNOT establish: anything about the outcomes of selector-failed
  rows — they are counted, not graded, and a full-selector-miss scan reports
  a refusal, not a clean bill.

## 2. co-presence (`checkPresence`, co-presence.mjs)

- **B1 — `REFUSE` on `zeroHit`, whatever the neighbours say.**
  Input shape: any `joinResult` with `zeroHit:true`, even alongside ten
  thousand firing neighbour rows. Exact refusal string (asserted verbatim
  by co-presence.test.mjs):
  `zero-hit: selector matched nothing; refusing to report absence as finding`.
  CANNOT establish: anything about the subject — present, absent,
  loaded, or unloaded. The refusal is the whole output; there is no absence
  claim to quote past it.
- **B2 — `PRESENT` unreachable under the Pass-6 wiring (key-shape mismatch).**
  Input shape: `idKey:"toolCallId"` over `joinOutcomes` matched entries.
  Matched entries store the key as `{id, …, record}`; `keyOf` looks up
  `record["toolCallId"]` then `record.data[…]` — neither exists on that
  shape — so `hits` is identically 0. Proved offline: the subject row
  **literally inside** the neighbour set still returns
  `ABSENT-NEXT-TO-FIRING`. The Pass-6 `presence=ABSENT-NEXT-TO-FIRING` on
  15529 matched rows is this artifact, not evidence of anything about the
  subject. Contrast: flat `{id}` records with `idKey:"id"` do reach
  `PRESENT`. CANNOT establish: that the subject is not-loaded (the detail
  string's "missing pi.on / glob miss" reading is unwarranted under this
  wiring) — only that the matched-entry shape and the lookup shape disagree.
  Fix direction, not taken here: teach `keyOf` the `{id, record}` shape or
  compare against `record[idKey]`.
- **B3 — `ABSENT-NO-NEIGHBOUR` on an empty neighbour set.**
  Input shape: subject key missing from `matched` AND `rows:[]`. The
  mechanism says this one about itself in its own detail string: "no
  co-presence evidence; cannot distinguish not-loaded from no-traffic."
  The Pass-6 scan never took this branch (dcg-bridge neighbour rows were
  present), so it stayed silent there. CANNOT establish: which of
  not-loaded vs no-traffic holds — by design, this verdict is the absence
  of evidence, not evidence of absence.

## 3. random-judge (`randomBaseline` + `ownConstant`, random-judge.mjs)

- **B1 — unanimous label set: both baselines are 1.0 and vacuous.**
  Input shape: every case carries the same truth label. The seeded shuffle
  is then the identity permutation, so `randomBaseline.accuracy` is
  identically 1.0, and `ownConstant` is 1.0 on the majority label. A real
  judge scoring 1.0 on such a set has beaten nothing. The Pass-6 kind
  distribution was three-class (top3 above), so this branch did not bite
  there — it is the boundary the next unanimous-looking slice must check
  first. CANNOT establish: any judge skill whatsoever; "beats chance" is
  meaningless where chance is 1.0.
- **B2 — kind-as-label baselines calibrate skew, not judges.**
  Input shape: the Pass-6 wiring, where `truthKey:"kind"` feeds
  record-kind labels (not judge verdicts) into both baselines:
  `ownConstant=0.5351 (label='dcg_allow')`, `randomBaseline=0.4954`.
  These numbers describe the label distribution of the scan — 8310/15529
  `dcg_allow` — exactly as the LIVE line's own bracket warns ("skew
  baselines only, NOT judge quality"). CANNOT establish: judge quality, or
  a bar a grading judge must beat. Quoting 0.5351 as "the baseline" is
  valid only for hypothetical judges answering kind-labels.
- **B3 — degenerate n: empty and singleton case sets.**
  Input shape: `cases:[]` → `randomBaseline.accuracy=0`,
  `ownConstant={label:undefined,count:0,accuracy:0}`; a single case →
  `randomBaseline.accuracy` identically 1.0 (a one-element shuffle cannot
  move). Structural from random-judge.mjs; the Pass-6 scan (n≈15k) never
  took this branch. CANNOT establish: a chance floor where the permutation
  has no room to vary — below n=2 there is no "chance" to measure, only
  arithmetic.
