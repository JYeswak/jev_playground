# A12 local refusal prototype — pre-registered falsifier `[pending]`

Committed BEFORE scoring (rule 3, `docs/RULES.md`). Prototype script
`work/cass-mail-mines/scripts/score_a12_refusal.py` does not exist yet at
this commit. Corpus: locked `exports/cass-dig-rows.jsonl` +
`exports/cass-dig-hits.jsonl` (n=138; 4 known empty-success rows).

## Candidate rule R (frozen)

Refuse dig (invent instead) iff ALL hold:

1. `hit_count > 0` (there is something to refuse; count=0 already invents),
2. query matches absence-claim shape
   `/no such|missing|does not exist|undefined|requireKey|no .* field|absent/i`,
3. top-hit snippet is NOT answer-eligible: no query token (len≥4, alnum,
   lowercased, stopwords excluded: {such,field,does,exist,what,where}) appears
   inside backticks OR within 40 chars of an error literal
   (`error|traceback|no such|undefined|is not|null|missing|column`).

Otherwise dig iff `hit_count > 0` (standing policy).

## What kills it

- **F1:** refused-Y1 count ≥ refused-empty count → REFUSE (kills more good
  digs than bad ones).
- **F2:** refused-empty count = 0 → REFUSE (toothless; the 4 known empties
  survive it).
- **F3:** R loss on S_wrong_selector ≥ dig-iff loss (0.500) → REFUSE (adds
  nothing where it matters).

Passing F1–F3 does NOT clear R: the predicate was authored after eyeballing
snippet heads (post-hoc), so the best passing outcome is HELD pending
fresh-data confirmation — and fresh confirmation needs `cass search`,
which is index-busy. DONE is not on the table tonight.

## Outcome words

REFUSE = F1/F2/F3 fires, with the counts. HELD = passes F1–F3 but post-hoc
authorship undisclosed nowhere — confirmation blocked. No DONE.

## NO-CLAIM

Mechanical snippet-literal proxy, not a judgment that the hit answers the
hole. Snippets truncated at 800 chars in the export. Locked export,
unregenerated. No rebuild started.
