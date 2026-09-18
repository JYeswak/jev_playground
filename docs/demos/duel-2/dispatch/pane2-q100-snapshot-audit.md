# PANE 2 — Q100 · AUDIT THE SNAPSHOT IMPLEMENTATION AGAINST YOUR OWN Q99 SPEC

You wrote the spec. I wrote the implementation. **You are the non-author of the code and the author of
the contract**, which is the only pairing that can rule on whether the contract was met.

Finish one unit, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them. A BLOCKED callback is a SUCCESS.

## Inputs (full repo-relative paths; `ls` each before you depend on it)

- Your spec:            `docs/demos/duel-2/SPEC_snapshot_manifest_COD.md`  (44feaf2)
- Your promotion ledger:`docs/demos/duel-2/audit-sidecar-promotion-*.json`  (eb26591, Q97)
- Implementation:       `scripts/verify-other-reasons.sh`
- Arms:                 `scripts/selftest-other-reasons.sh`  (now 9)

Present ⇒ proceed. Absent ⇒ fire a BLOCKED callback naming the exact path, then take the dry-queue
default. Never wait on "when X lands".

## UNIT 1 — Did the implementation MEET your spec, clause by clause?

Your spec named these. Rule **MET / PARTIAL / NOT MET** on each, with the file:line you read:

1. Original STATUS/sidecar bytes and receipt paths **preserved** (evidence not rewritten).
2. Copies under a private snapshot root.
3. **Resolver** maps original relative paths to snapshot paths.
4. Manifest records: source HEAD · capture attempts · per-file source_pre / source_post / copy raw
   sha · normalized sha where defined · bytes · source and snapshot paths.
5. Manifest **self-digest over the canonical payload excluding the digest field**.
6. A third party can recompute the hashes and the manifest, and rerun the copied verifier.

Then rule the **four Q97 preconditions** you yourself blocked promotion on — copy/snapshot,
revision/hash pair, copy-based arms, verifier-owned `TRANSIENT_UNSTABLE`. You wrote *"lane-status rc10
does not transfer"*; the verifier now owns its own rc10 with its own bounded two-capture. **Does it
transfer now, and is the promotion you deferred now decidable?** You may rule DEFER AGAIN — that is a
real outcome, and naming what is still unmet is worth more than a promotion.

## UNIT 2 — Attack the arms, not the feature

Three things I want you to try to break, because each is a defect class this lane has already caught
inside its own instruments:

- **ARM 9 re-hashes copies off disk** rather than trusting `copy_raw`. Is that actually independent,
  or does it share a computation with the thing it checks?
- **`JEV_FORCE_MOVED`** is a deterministic hook because racing a mid-run mutation proved nothing three
  times. I claim it is **fail-safe by construction: it can only manufacture a false TRANSIENT, never a
  false pass.** Try to falsify that. If it can suppress a real FAIL, say so — that is a live defect.
- **The `moved:` line printed `c16061aa… -> c16061aa…`**, identical digests, because the hook forced
  the classification. I claim that self-discloses a forced transient. **Does it, or is it just
  confusing output that a reader would mistake for a real movement?**

Also: does the withheld report actually withhold? I claim no verdict text escapes an unstable capture.

## UNIT 3 — The question I cannot ask myself

The snapshot exists so a third party can re-derive a verdict. **Can they?** Take the emitted snapshot
dir and manifest, and try to reach the verdict *as an outsider* — recompute digests, rerun the copied
verifier against the copies, and see whether anything forces you back to the live repo. If it does,
the snapshot is cosmetic in exactly the way your spec set out to prevent, and I want that named.

## DRY QUEUE DEFAULT (standing, in priority order)

1. Review the highest-value **unreviewed** artifact in the lane (one grader, zero graders, or an
   unaudited claim) — non-author only.
2. The oldest `NEGATIVE_EVIDENCE.md` item whose retry condition has become satisfiable, or a
   `GATES.md` gap with no witness.
3. Fire a **QUEUE DRY** callback naming what you considered and rejected. That is a success.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are all PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-Q100-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

Measured 17 consecutive times this session: `am inbox` returns `count: 0`. **Leg 3 is dead
transport** — do not rely on it, and if you do send mail, report what the send returned. Carry: bead
id · commit sha · NEXT (the unit you are STARTING, never what you are waiting for) · NO-CLAIM (the
exact limit of what you proved).

Commit your own files only, `git commit --only <explicit paths>`, verification level in the subject.
Never `git add -A`.

---

## CORRECTION 1 (appended 2026-09-18T12:50Z — do not insert, this is a live-pointer file)

**The ledger path above is wrong, and pane 2's BLOCKED callback was correct.** There is no
`docs/demos/duel-2/audit-sidecar-promotion-*.json`; I invented that glob from memory rather than
deriving it from the commit I cited. The real artifact is:

    docs/demos/duel-2/RULE_promote_sidecar_verifier_v2_COD.md   (eb26591, 54 lines)

This is the un-re-derived-citation defect — committed inside a packet that asks a pane to audit
citations. It is the same class as the bare filename that produced two correct BLOCKED callbacks
earlier in the session: **a packet that names a path the pane cannot resolve is a defective packet.**

**Two additions to UNIT 1, both of which I want ruled AGAINST me if the record supports it:**

- The ledger's **six re-open conditions** were not read against my implementation before I shipped
  it. Doing so immediately found a live defect: condition 5, *"no live shared path is read after the
  snapshot is declared complete"*, caught the resolver falling back to the **live** path for anything
  `snapshot()` skipped — so a receipt absent at capture but appearing mid-run would have been read
  live and verified. Fixed in `0e024ee`. **Read all six adversarially; one of them already paid.**
- I **still** read live files after verification to compute `source_post`. That is literally a live
  read after the snapshot. I claim the bounded-capture contract requires it. **Rule whether that
  violates condition 5 or is exempt** — if it violates, promotion stays deferred.
- Condition 6 requires foundation execution stay **explicitly non-commit-wired**, and you earlier
  warned foundation *"would collapse rc10 to RED if wired"*. **Is stage 80 still safe now that the
  verifier owns an rc10?**
