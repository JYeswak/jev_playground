# Planning review round 1 — pane 6 QuietHarbor (W2.1 seat)

Reviewing `docs/PLAN-DEEP-KIT-20260922.md` whole, with wave-1 measurement in
hand (`notes/deep/honesty-census.md` commit `62355af`, census TSV at `83300a1`).
Sibling rounds R1-1..R1-12 (p5/p2/p3) read first; nothing below re-proposes
them. Every change cites evidence or is labelled `[Inference]`.

## R1-13 (SHRINK): W2.2 must type its evidence before repairing — most "evidence" is mention, not proof

Analysis: W2.2 says "repair every REPAIRABLE close through `br` with the
evidence W2.1 named". My census names evidence for 30 rows, but all 30 lack
machine-checkable evidence IN the reason, and resolving the named items
shows why that matters: 12 of the 30 cite
`work/nev-routing/tool-select-labelled.jsonl` — the measurement corpus those
beads produced, not proof their closes were correct. A commit that merely
names an id (`git log --grep` hits like `0d36407`, cited for 0bp/0c6/eww/gou)
is provenance, not completion proof. The g3i/g8p overturn proved the
complementary gap: the real evidence lived in comments and cited files the
arms never opened. Repairing all 30 "with the evidence named" would therefore
either rubber-stamp mentions or silently redo the evidence pass. The 11 bare-
`done` shorts are the crisp set; the rest need typed evidence first
(fix-commit vs mention vs comment/cited-file), then repair of the fix-type
rows only.

```diff
 **W2.2 False-close repair (wave 3).** Repair every REPAIRABLE close through `br` with the evidence
-W2.1 named; reopen every NO-EVIDENCE close with a comment. The three existing repair beads fold in.
+W2.1 named, typed first: re-run the evidence pass distinguishing fix-type evidence (a commit that
+IS the fix, a receipt that IS the proof, a resolving file:line) from mention-type (an id string in
+a corpus, a commit message, a dispatch doc). Repair the 11 bare-`done` shorts and the fix-type rows
+through `br`; mention-only rows go back through comment-reading arms before anyone touches their
+status. There are no NO-EVIDENCE rows at 83300a1; if the rerun produces any, reopen with a comment.
+The three existing repair beads are closed (83300a1); drop the fold-in clause.
```

## R1-14 (CHANGE): W2.3 must pin the unitizer — the floor moves with the splitter

Analysis: my (b) rule yields 35 candidates line-based, 32 block-based, 37 on
the pre-rewrite tree — numerator 0 every time, denominator ±3 by splitter
choice (`notes/deep/honesty-census.md` §(b)). W2.3's floor ("whatever W2.1
measured") is therefore undefined until the unitizer is pinned, and its
selftest ("plants an unregistered numeric README sentence and requires RED")
can plant a sentence the splitter drops — the registered pattern itself
(`Call the official SDK.`) is invisible to the rule — making RED
unachievable or vacuous depending on the plant. A ratchet on an unpinned
denominator ratchets noise.

```diff
 **W2.3 Claim-coverage ratchet (wave 3).** Stage `foundation/gates.d/18-claim-coverage.sh`: coverage
-fraction from W2.1(b) as a floor that may only rise; `--selftest` plants an unregistered numeric
-README sentence and requires RED naming it.
+fraction from W2.1(b) as a floor that may only rise, computed by the SAME unitizer the census used
+(shared script, not a reimplementation); the stage refuses to run if the unitizer differs by hash.
+`--selftest` plants an unregistered numeric README sentence, asserts the plant counts as a
+candidate FIRST, then requires RED naming it.
```

## R1-15 (CHANGE): W2.4 must cover the predicate classes that actually fire

Analysis: my (c) found zero SHA-move predicates in the real ledger; all four
satisfied triggers were other classes — new-corpus-date (R16), git-log
recency (R37), grep-count (R38), script-run (R68)
(`notes/deep/honesty-census.md` §(c)). W2.4 as specified
(`scripts/ledger-resurrect.sh`: "lists rows whose SHA/version predicate is
now satisfied", selftest "plants a row whose pinned SHA moved") automates
the empty class and leaves the four live ones manual. The script should check
all observable classes with one worked selftest each; minimum viable is the
R38 class, since it is pure grep and already fired twice (the ledger's own
history plus my recount).

```diff
 **W2.4 Ledger resurrection (wave 3).** `scripts/ledger-resurrect.sh`: lists NEGATIVE_EVIDENCE rows
-whose SHA/version predicate is now satisfied; cadence = every `foundation/gates.sh` run, advisory
+whose SHA/version/doc-sentence/count/file predicate is now satisfied (the four classes W2.1(c) found
+live: corpus-date, git-log, grep-count, script-run); cadence = every `foundation/gates.sh` run, advisory
 (non-blocking) until one resurrection has been acted on. While non-blocking it cannot fail, so it
 lands `PREPARED-NOT-MEASURED`: each run appends its candidate count to a census line the next
 honesty census reconciles, so silence is visible rather than green. `--selftest` plants a row whose
-pinned SHA moved in a fixture manifest.
+pinned SHA moved in a fixture manifest AND a fourth `?? 'unknown'` instance that must list R38.
```

## R1-16 (CHANGE): census pinning rule — counts must carry their pin

Analysis: during one Part A pass my bead denominator moved 105 → 106 → 107
(peer commits plus one uncommitted row) and the README rewrite moved the B12
denominator 37 → 35, both mid-measurement (`notes/deep/honesty-census.md`
header, §(b)). Any reconciliation of two censuses that compares bare numbers
is comparing different populations. The fix is already demonstrated: my (a)
counts cite the `83300a1` blob, reproducible by
`git show 83300a1:.beads/issues.jsonl`.

```diff
 No phase exit may cite a result whose dependency closure contains an unresolved item from an
 earlier phase.
+
+Census rule (all waves): every census number cites the blob or file revision it counted
+(commit SHA for tracked files, mtime + HEAD for live-tree reads). A rerun that cannot name
+its pin is not a rerun. Reconciliation compares pins first, numbers second.
```
Placement: end of §10 (Phase exit criteria), since that is where cross-phase
citation discipline lives. `[Inference]`: placement only; the rule itself is
measured above.

## R1-17 (CHANGE): W2.1's fixed numbers are already stale — restate as pin-at-count

Analysis: §4 W2.1 still says "all 68 closed beads" and "the 13 in_progress
and 14 blocked rows". Measured at `83300a1`: 70 closed, 18 in_progress, 14
blocked (`notes/deep/false-close-census.tsv`). The packet text will rot on
every bead commit; the numbers belong in the census artifact, with the packet
naming the pin rule.

```diff
-**W2.1 Honesty census (wave 1).** Goal: the three GAP rows (B11, B12, B13) as numbers, not prose.
-Target: `notes/deep/honesty-census.md` + `notes/deep/false-close-census.tsv`. Measure: (a) B13 —
-all 68 closed beads: `close_reason` length, whether it names a command, a commit that
-`git cat-file -e` resolves, or a receipt path that exists; classify REPAIRABLE (evidence exists
-elsewhere, name it) / NO-EVIDENCE / OK; also the 13 in_progress and 14 blocked rows with their last
-update age. (b) B12 — README.md claim sentences (numerals, "verified", "passes", "beats") vs rows in
+Target: `notes/deep/honesty-census.md` + `notes/deep/false-close-census.tsv`. Measure: (a) B13 —
+all closed beads AT THE PINNED COMMIT (70 at 83300a1 and moving): `close_reason` length, whether
+it names a command, a commit that `git cat-file -e` resolves, or a receipt path that exists;
+classify REPAIRABLE (evidence exists elsewhere, name it) / NO-EVIDENCE / OK; also the in_progress
+and blocked rows at the same pin (18 + 14 at 83300a1) with their last-update age. (b) B12 —
+README.md claim sentences (numerals, "verified", "passes", "beats") vs rows in
 `foundation/kit/claims.tsv`: coverage fraction with the sentence list.
```

## R1-18 (CHANGE): pin-liveness selftest must plant synthetic heat, not recency

Analysis: my addendum diagnosis (`notes/deep/honesty-census.md` Addendum):
the RED arm pins a row to the real `NEGATIVE_EVIDENCE.md` at threshold 1
while `pin-liveness.sh:57` counts trailing-24h commits; 27.4h of quiet turned
the demonstration green, and the selftest comment claiming immunity ("cannot
silently stop testing anything") is false. Any gate that depends on this
instrument — including W2.4's future pin automation — inherits a
weekend-shaped hole. A synthetic hot file (fixture with faked recent history
in /tmp, or a threshold-0 arm) holds still.

```diff
 **W2.4 Ledger resurrection (wave 3).** `scripts/ledger-resurrect.sh`: lists NEGATIVE_EVIDENCE rows
 whose SHA/version predicate is now satisfied
```
(no text change proposed to W2.4 here beyond R1-15; this change targets the
instrument both depend on)
```diff
 scripts/selftest-pin-liveness.sh arm 1 (wave 3, owner: whoever clears stage 80): repoint the
 "row pinned to a hot file" arm at a synthetic hot file whose heat does not decay (fixture STATUS
 with a planted digest over a path with faked trailing-24h commits, or threshold 0), and correct
 the comment claiming threshold 1 is rate-independent. Do not touch the instrument's threshold
 semantics in the same commit (gate-thrift: one change, one RED proof).
```
`[Inference]`: the synthetic-heat design; the flake it fixes is measured.

## R1-19 (PERF): W2.4 census reconciliation must be incremental

Analysis: my full (a) run took ≈6s (6.09s on the committed-blob run), dominated by one `rg` over the tree per
closed row × 70 (`notes/deep/honesty-census.md` Preregistered (a)). A
per-`gates.sh`-run resurrection cadence that re-scans all rows each time
scales with the ledger, not with change. `git log` on `.beads/issues.jsonl`
already gives the changed-row set; only those rows need re-evidence per run,
with a full pass on the honesty-census cadence.

```diff
 **W2.4 Ledger resurrection (wave 3).** `scripts/ledger-resurrect.sh`: lists NEGATIVE_EVIDENCE rows
 whose SHA/version predicate is now satisfied; cadence = every `foundation/gates.sh` run, advisory
+(non-blocking) until one resurrection has been acted on. Each run re-evidences only bead rows
+touched since the last run (`git log` on `.beads/issues.jsonl`); the full 70-row pass runs on the
+honesty-census cadence, not per gate run.
```
(Append; rest of W2.4 unchanged apart from R1-15.)

## Packets reviewed without changes proposed

W1.1–W1.3 (p2's R1-5/R1-6 and env-failure rules cover the load/proxy/shared-env
gaps; nothing in my seat adds to them), W1.4–W1.8 (untouched by my evidence),
W3.1 (capacity objection already resolved by the depth directive; row-level
review belongs to its owner), W4.1–W4.2, W5.1–W5.2, W6.1–W6.2 (p3's R1-7..R1-12
cover ledger/ranking/cold-read/receipt issues; the B12 denominator finding is
filed above as R1-14 against W2.3, not W6.2), W7.0–W7.4 (no wave-1 evidence
from my seat; the T4-bar and class profiles are pane 1's design), W0.

## FLAG: acceptances that cannot fail

Reviewed every §4 acceptance for unfalsifiability. The only
cannot-fail-by-construction text is W2.4's advisory mode (concur with R1-3,
with new evidence: my (c) found 4 presently-actionable candidates that an
advisory run would list and ignore — the mode's first live test is already
waiting). All other acceptances fail cleanly: W2.2's oracle (11 bare-`done`
rows guarantee a non-vacuous rerun), W2.3's RED selftest (as amended by
R1-14), W2.5's canary (RED-or-refuse), W2.6's run URL, W1.4's 0-mismatch
target, W1.6–W1.8 staged gates, W3.1's row count, W5.1's QA boxes, W7.2's
per-clone receipts.
