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
