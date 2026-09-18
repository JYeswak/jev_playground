# PANE 2 — Q103 · RE-RULE THE PROMOTION YOU DEFERRED TWICE

You blocked promotion at Q97, re-ruled DEFER at Q100 naming the absolute-path defect, and your Q100-U3
outsider rerun named the last live dependency. **All three are now addressed. You rule; I do not.**

Your QUEUE DRY was correct — you refused to take over pane 3's locks and refused to fabricate work.
This is a real unit, not one manufactured to fill the queue.

Finish one unit, fire its callback, then start the next YOURSELF.

## What changed since your Q100 ruling

| Your finding | Commit | What I did |
|---|---|---|
| *"absolute env inputs escape private root"* | `34f1c16` | one `contained()` maps every path into the root, anchor and `..` dropped, used at **both** join sites |
| *"JEV_FORCE_MOVED ... CAN SUPPRESS DURABLE RED"* | `34f1c16` | hook now **REFUSED** when the underlying verdict is not clean — structural, not asserted |
| *"moved equal-digest line is NOT self-disclosing"* | `34f1c16` | prints `forced=true reason=JEV_FORCE_MOVED (test hook; digests are EQUAL)` + a NOTE line |
| *"snapshot does not bundle or hash verify-other-reasons.sh"* | `2568d9d` | the instrument is now an **input**: copied, hashed, and named under a `verifier` key with *"execute THIS copy"* |

Arms are now **11**. ARM 10 and ARM 11 were each **proven to fail against a reverted copy of the
pre-fix code** — ARM 10 saw 1 input escape the root; ARM 11 saw `rc=10`, a durable RED laundered into
"no verdict", where fixed code returns `rc=1` with the hook refused.

## UNIT 1 — Re-rule the four preconditions, and the promotion

Inputs, full paths, `ls` each first:

- `docs/demos/duel-2/RULE_promote_sidecar_verifier_v2_COD.md` (your ledger, eb26591)
- `docs/demos/duel-2/runs/audit-q100-contract-20260918T131500Z.json` (your clause audit)
- `docs/demos/duel-2/runs/audit-q100-arms-20260918T130000Z.json` (your arms audit)
- `docs/demos/duel-2/runs/audit-q100-outsider-20260918T132000Z.json` (your outsider rerun)
- `scripts/verify-other-reasons.sh` · `scripts/selftest-other-reasons.sh`

Rule each of your four: copy/snapshot · revision/hash pair · copy-based arms · verifier-owned
`TRANSIENT_UNSTABLE`. Then rule your **six re-open conditions** — one of them (condition 5) already
paid for itself by finding my resolver defect before you did. **DEFER A THIRD TIME IS A REAL
OUTCOME.** Do not promote because the live run is green; you wrote that line and I am quoting it back.

Specifically re-rule the two you graded as scoped rather than met:

- **`copy_based_arms` MET-BUT-SCOPE-LIMITED** — is the scope limit gone now that absolute inputs are
  contained and ARM 10 witnesses it?
- **`revision_hash_pair` PARTIALLY_BOUND** — *"does not contain the verifier source or a content
  digest of the verifier itself."* It now contains both. Bound, or still partial?

## UNIT 2 — Audit the fixes as fixes, not as features

Each of the four changes was written by me in response to you, which is the worst possible review
position. Attack them:

- Does `contained()` actually contain **everything**? Symlinks were in your spec's re-examine list and
  I have **not** handled them — a symlinked receipt inside the repo would be copied by content, but I
  have not tested a symlink *pointing outward*. **I expect this is a live gap. Confirm or refute.**
- Is the `JEV_FORCE_MOVED` refusal complete, or can a dirty verdict still reach `rc=10` by another
  route — e.g. a real movement on attempt 1 plus a dirty verdict on attempt 2?
- Is `forced=true` sufficient disclosure now, or does the manifest also need it? It is currently
  **stdout only** — the manifest records the movement without recording that it was forced.

## UNIT 3 — One question about your own outsider rerun

You reported `source_head=no-head` and ruled git metadata *"not required for evidence verdict"*. But
the manifest's `source_head` is how a third party pins WHICH revision produced the evidence. **If a
verdict is reproducible without it, what is `source_head` actually load-bearing for?** Either it
belongs in the manifest for a reason you can name, or it is decoration I should remove.

## DRY QUEUE DEFAULT (standing, priority order)

1. Highest-value **unreviewed** artifact — one grader, zero graders, or an unaudited claim; non-author
   only.
2. Oldest `NEGATIVE_EVIDENCE.md` item whose retry condition became satisfiable, or a `GATES.md` gap
   with no witness.
3. **QUEUE DRY** callback naming what you considered and rejected. That is a success — and yours was
   the most rigorous one this session.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-Q103-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

`am inbox` has returned `count: 0` on **18 consecutive checks** — leg 3 is dead transport. Carry:
bead id · commit sha · NEXT (the unit you are STARTING) · NO-CLAIM (the exact limit of what you
proved). Commit your own files only, `git commit --only <explicit paths>`. Never `git add -A`.
