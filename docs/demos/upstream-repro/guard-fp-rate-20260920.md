# Guard FP-rate: seeded 100-command sample `[receipt]`

Sample: 100 real `dcg_allow` commands from 78,242 harvest records, seed
20260920 (`sample sha c05a027cf8e77102`). Threshold frozen before any
fire seen: DROP if class FP > 0.50 with ≥10 fired; UNDERPOWERED if <10.
67 fires hand-labeled one by one; 5 ambiguous matches verified against
full command text (heredoc containment checked, not assumed).

## Per-class FP table

| class | fired | correct | false | FP rate | disposition |
|---|---:|---:|---:|---:|:--|
| pipe-exit | 57 | 54 | 3 | 0.053 | KEEP |
| grep-as-proof | 10 | 10 | 0 | 0.000 | KEEP |
| stage-all | 0 | — | — | — | UNDERPOWERED (no fires to judge) |
| commit-backtick | 0 | — | — | — | UNDERPOWERED (no fires to judge) |

## The 3 false fires (all pipe-exit)

- `OUT=$(...); RC=$?` with verdict parsed from JSON content (row 11):
  rc reported-but-unused; content decides.
- `set -o pipefail` + `|| echo` fallback (rows 27, 31): rc explicitly
  handled at both layers.

No heredoc-contained match among the 5 checked (rows 0, 3, 77 all fire
on real pipelines outside the quoted span) — the mention-vs-use check
that motivated the verification.

## The strong positives (why the class earns its place)

`echo exit=$?` / `SELF_RC=$?` / `gates_rc=$?` capturing a PIPELINE rc
(rows 63, 88, 90, 96) — the last is the lane's own documented trap,
firing in the wild. Every bare `cmd | head` in a bash tool call also
reports head's rc to the harness as the tool result (isError observed),
so display-only truncation is warn-worthy here, not noise.

## NO-CLAIM

One reader, n=100, two classes unjudged for lack of fires (their day-one
verdict is the unit tests, not this sample). Advisory severities only —
no blocking claim follows from any rate here. `[receipt]` used.

---

## CORRECTION appended 2026-09-20 (reconciliation lane, non-author)

Re-derived in `pipe-exit-reconciliation-20260920.md`. Nothing above is
rewritten; two of its cells are superseded.

**`pipe-exit` disposition `KEEP` → SUPERSEDED. The `FP 0.053` stands.**
The measurement is precision GIVEN a fire, and it is sound. Disposition is
not decidable from precision alone: the same class fires on **55.2%** of
78,242 real `dcg_allow` commands (43,185; re-derived to the unit,
`work/pipe-exit-reconciliation/measure.mjs`), so it is right about each
fire and useless as a warning. Dropped under `NEGATIVE_EVIDENCE.md` R51
and removed from the shipped classifier at `e26b10f`.

The frozen threshold ("DROP if class FP > 0.50 with ≥10 fired") could not
have caught this: it has no rate term. Freezing it before any fire was
correct practice and is not what failed — the threshold was measuring the
wrong quantity, honestly. A rate arm belongs in the next one.

One predicate note. This receipt's 57 fires come from the shipped glob
(`*"| head"*|*"| tail"*`). R51's 55.2% comes from `/\|\s*(head|tail)\b/`,
which also matches no-space `|head` — 772 extra commands. The glob's own
rate is 42,413/78,242 = 54.2%. Same verdict either way, but the two
documents are not measuring the same predicate.

**The sample is not re-derivable from this tree.** No sampler was
committed, so `sample sha c05a027cf8e77102` cannot be regenerated and the
57 fires cannot be re-counted. They are corroborated statistically
instead: 57/100 against p = 0.552 is z = 0.36 — consistent. (Against the
18.4% also quoted in R51, z = 9.96; this sample is what refutes that
number. See the reconciliation, §3.)

**The strongest claim here survives, and was probed live.** "Every bare
`cmd | head` in a bash tool call also reports head's rc to the harness":
`bash -c 'exit 3' | head -1; echo "rc=$?"` → `rc=0`, and the tool call
returned success. CONFIRMED.

`grep-as-proof` (0/10 FP) is unaffected and remains shipped. The two
UNDERPOWERED rows are unaffected.
