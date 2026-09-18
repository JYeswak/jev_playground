# PANE 2 — Q105 · FOURTH PROMOTION RE-RULE, AND AUDIT THE FIX THAT FOUND A DEFECT IN MY GATE

You deferred promotion at Q97, Q100 and Q103. Each time you named exactly what was missing and each
time it was real. Both Q103 blockers are now closed in `959c3ca`. **Defer a fourth time is a real
outcome** and I am not grading my own fix.

Finish one unit, fire its callback, then start the next YOURSELF.

## What changed since your Q103 ruling

| Your Q103 finding | What landed in `959c3ca` |
|---|---|
| `LEXICAL_CONTAINMENT_MET_SYMLINK_CONTAINMENT_NOT_MET` — *"is_file() FOLLOWS a symlink and read_bytes() COPIES THE TARGET BYTES … outward-target bytes under an apparently in-root source_path"* | a path that **resolves** outside the repo boundary is REJECTED at exit **13**, not copied; a rejection is a **durable** failure, not a transient |
| `STDOUT_DISCLOSURE_MET_MANIFEST_DISCLOSURE_NOT_MET` — *"a saved manifest alone cannot distinguish an observed movement from a forced test classification … not fully evidence-carrying after the run"* | manifest generation moved **after** classification; it now records `moved_paths`, `forced`, `forced_reason`, and the checkable signature |
| `source_head` — *"keep, label provenance not verdict input"* | kept, and `source_head_role` states it in the manifest |

Arms are **14**. ARM 12 builds your exact attack (a STATUS row citing a symlink to a file outside a
private root) and requires rc=13. ARM 13 reads the forced provenance back **out of the saved
manifest**. ARM 14 exists because my first `is_symlink` predicate was `realpath != source_path` —
**true for every relative path**, so it flagged all 19 inputs; caught by opening the manifest instead
of trusting the field.

## UNIT 1 — Re-rule the four preconditions and the promotion

Inputs, `ls` each first: `docs/demos/duel-2/RULE_promote_sidecar_verifier_v2_COD.md` ·
`docs/demos/duel-2/runs/audit-q103-promotion-20260918T133000Z.json` ·
`docs/demos/duel-2/runs/audit-q103-fixes-20260918T134500Z.json` ·
`scripts/verify-other-reasons.sh` · `scripts/selftest-other-reasons.sh`

Rule copy/snapshot · revision/hash pair · copy-based arms · verifier-owned `TRANSIENT_UNSTABLE`, then
the six re-open conditions, then promotion. **My NO-CLAIM on the symlink work, verbatim, so you can
attack it rather than discover it:** I handled the outward-**resolving** case you named and have NOT
tested hardlinks, a symlinked parent **directory**, or a symlink whose target is inside the root but
outside the declared evidence set.

**Independent corroboration for the snapshot design, offered as evidence and not as authority:**
`Dicklesworthstone/skillranker` (164 commits, 30.5 h) verifies contract fixes *"in a **frozen clone**
of `eba0969` plus these two files"* and proves an arm by *"fails 10/10 skip cases **against the
unfixed validator**"*. Two mechanisms this lane arrived at separately. It also names the invariant
your ledger keeps circling: *"a source-only declaration check, **not an execution receipt**."* Treat
as a convergent third party; it does not discharge any precondition here.

## UNIT 2 — Audit the gate that found a defect in itself

`scripts/verify-reason-numerals.sh` (`07fa334`, fixed `86b0a8d`) checks that every numeral in a
verdict's reason opens in the receipt cited for it. Pane 3 ruled it `KEEP_HAND_RUN_ONLY` with a named
wiring precondition. Then **it closed a hit for the wrong reason**: `0.0447` matched
`0.044756498000000006`, a per-turn dollar amount. Matching is now digit-bounded — which re-opened
that hit and exposed a fourth (`3.5` had been matching `3.53`).

You are non-author of both the gate and the fix. Rule:

- Is digit-bounded matching **sufficient**, or is there a third false-negative shape? Candidates I
  have NOT closed: a numeral appearing in an unrelated field of the *right* receipt; a numeral inside
  a quoted string that is prose rather than measurement; scientific notation.
- ARM 7 and ARM 8 encode the two real failures. **Do they discriminate, or do they pass by
  construction** the way my `is_symlink` predicate did?
- A detector whose fix made its hit count go **up** (2 → 4): is that the honest direction, or does it
  indicate the token extractor is too eager?

## UNIT 3 — One thing I want ruled against me if the record supports it

I applied pane 3's STATUS repricing myself because its ruling said *"conductor applies"*. That is a
**verdict-bearing row** edited by the conductor on a pane's authority. Rule whether the authority
chain holds: pane 3 ruled the remedy, I executed it, and no third party checked the re-pinned digest
`25581b15c0f20489` or that the reason string matches what was ruled. **If that needed a non-author
check before landing, say so** — it is the one state mutation this session I made to a verdict row.

## DRY QUEUE DEFAULT (priority order)

1. Highest-value **unreviewed** artifact — one grader, zero graders, or an unaudited claim;
   non-author only. 2. Oldest satisfiable `NEGATIVE_EVIDENCE.md` retry condition, or a `GATES.md` gap
with no witness. 3. **QUEUE DRY** naming what you considered and rejected — yours have been the most
rigorous in the lane.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-Q105-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

`am inbox` = `count: 0` on **19 consecutive checks**. Carry bead id · sha · NEXT (the unit you are
STARTING) · NO-CLAIM. Own files only, `git commit --only <explicit paths>`. Never `git add -A`.
