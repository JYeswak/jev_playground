# Should you dig into past work before inventing an answer? `[pending]`

We tested this on 138 real questions asked against CASS, our archive of
~59,800 past agent conversations (~5.2M messages). The question: when the
archive returns hits, should the agent reuse them ("dig") or write from
scratch ("invent")?

## The honest arc

Digging wins **in aggregate**: average loss 0.058 digging whenever any hit
exists, vs 0.159 always inventing (n=138 locked questions)
([receipt](./dig-subset-breakdown-20260920.md)).

That aggregate **inverts on the slice that matters**. On the 16 questions
that claim something is missing ("no such field", "undefined", …),
digging scores 0.500 vs 0.250 inventing — twice as bad **if you price a wrong
dig at twice a wrong invention, which is our assumption, not a measurement**.
Price them equally and the slice is a tie. What survives either pricing is the
direction: on these questions digging never beats inventing. The hits exist and
answer nothing. The pooled win was carried by the other 122 questions, where
digging was nearly perfect.

The obvious fix was built and **refused**: a rule that skips digging on
suspicious questions caught 2 of the 4 empty hits but killed 2 good digs
— a coin, not a policy. Worse, it keyed on the *wording* of the failing
slice rather than on *whether any hit actually answers*; a rule fitted to
16 rows will not generalize
([receipt](./a12-refusal-result-20260920.md)).

Separately, joining agent-mail threads to archive sessions works at the
project level (20 exact path matches, e.g. 465 mail messages ↔ 107 archive
sessions for one project) — but every match is captured by plain
string-equality, so there is no job here for a paid model
([receipt](./a11-join-yield-20260920.md)).

## What is unmeasurable, and why

We could not test whether agents acknowledge requests off-channel: all 20
project matches are **time-disjoint** — e.g. the richest pair's mail runs
2026-08-31→09-01 while its archive sessions run 2026-06-17→07-27, 35 days
apart. Say `UNMEASURED`, never `0`
([receipt](./a18-offbus-result-20260920.md)).

## Takeaway

**Dig by default, but never dig an absence-claim on hit-count alone —
demand evidence in the hit that it answers, or invent.**

## Caveats a reader needs

- `Y` (which digs were "right") was a **mechanical proxy**. It has now been
  **human-calibrated on the 16 rows that decide the finding**
  ([calibration](./c1-calibration-result-20260920.md), labels in
  `c1-human-y.jsonl`; [review that demanded it](./mines-nonauthor-review-20260920.md)).
  A reader read every top snippet and judged whether it answered the question.
  **Two labels changed, both from "the dig was right" to "it was not"** — a hit that
  was a metrics-ledger dump, and one where `undefined` appeared only as a `session_id`
  string value. Both are mention-vs-use: the word was present, the answer was not.
  Recomputed with human labels, the slice gets **worse for digging, not better**:

  | cost of a wrong dig | inventing | digging | |
  |---|---:|---:|---|
  | 1× (equal) | 0.125 | 0.375 | digging loses |
  | 2× (our assumption) | 0.125 | **0.750** | digging loses badly |

  So the earlier caveat is **retired, not softened**: at equal cost the slice is no
  longer a tie, it breaks toward inventing, and the direction now holds without
  depending on our chosen constant. What remains is the honest limit — **one adjacent
  reader, n=16, and two labels either way** would still move it.
- Practical warning, reproduced: the mail DB timestamps are in
  **microseconds**, the archive DB's in **milliseconds**. Compare them raw
  and every time-window join silently returns zero — the same zero a real
  disjointness finding produces. Normalize first.
- **Replicated on a representative sample, and it got stronger.** The numbers above
  came from an id-window of 120k messages that we later measured as
  **unrepresentative** ([sampling frame](./cass-sampling-frame-20260920.md)): 1.5% of
  conversations, workspaces whose top-3 do not overlap the corpus's, messages ~4.7×
  longer than average, and — despite us calling it "recent" — a span covering the
  **entire** corpus era, because message ids are not chronological.

  So the whole protocol was re-run on a seeded random draw of 1,000 conversations
  (seed 421337, `sample_sha f68bccdc`, [receipt](./repsample-result-20260920.md)),
  changing nothing else:

  | | representative | id-window |
  |---|---|---|
  | always-invent | 0.587 | 0.159 |
  | dig-iff-hit | **0.101** | 0.058 |
  | absence-claim slice (1:2) | **0.875 loses** | 0.500 loses |
  | absence-claim slice (1:1) | **1.188 loses** | 0.250 tie |

  **Both halves hold and the warning is sharper**: digging still beats inventing
  overall, and on absence-claims it is now far worse, not marginally so. The
  conductor predicted the opposite — that the inversion was an artefact of long
  receipt-shaped messages — and was wrong: a representative corpus raises the base
  rate of useful hits (0.159 → 0.587), which makes "hits exist but answer nothing"
  a **worse** bet, not a better one.
- Nothing here cleared; no promotion. n=138 with 30 near-duplicate probe rows; no
  full-index search (the index was rebuilding at measurement time).
