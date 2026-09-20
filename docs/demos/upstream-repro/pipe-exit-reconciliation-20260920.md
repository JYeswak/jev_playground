# pipe-exit: three rulings, three axes, one missing measurement `[receipt]`

MAP.md action-plan item 2. One class (`pipe-exit`), three rulings in the
tree, nothing reconciling them:

| where | ruling | what it actually measured |
|---|---|---|
| `guard-fp-rate-20260920.md` | **KEEP** (FP 0.053) | precision GIVEN a fire |
| `NEGATIVE_EVIDENCE.md` R51 | **DROPPED** (55.2% fire rate) | base rate of fires |
| `NEGATIVE_EVIDENCE.md` R48 | **REFUSED** | enforceability of a *wrapper* |

## Verdict in one line

**Not a contradiction. Three axes, and the decision axis — rate × precision
on the DEFECT population — was never measured by any of them. I measured it:
1.04%, FP 3/20.** R51's DROP of the shipped glob stands and is exactly
reproducible. R51's *reason* stands; R51's "narrowing fails" is overstated —
it tested one narrowing family and missed the one its own trigger names. The
FP receipt's number stands; its `KEEP` disposition is superseded. R48 is
about a different instrument and was never in this fight.

---

## 1. Are they in conflict?

No. They answer three different questions, and each is right about its own.

- **FP receipt — precision.** `P(defect | fired)` = 54/57 = 0.947. Says
  nothing about how often it fires.
- **R51 — base rate.** `P(fired)` = 55.2%. Says nothing about precision.
- **R48 — instrument.** Refuses an opt-in `rcof.sh` *wrapper* that runs the
  command unpiped. That is a sender-side, behavior-altering instrument. The
  guard class is a receiver-side, observe-only string scan. Different object;
  R48 never ruled on it. (R48's own appended correction already concedes the
  string is scannable — it withdrew the "no string to scan" premise and kept
  the fires-on-everything and behavior-altering premises.)

A low FP with a high fire rate is not a contradiction; it is a class that is
**right and useless** — right about each fire, useless because the reader
stops reading. The axis that decides an advisory's fate is neither of the
two measured: it is **expected true signals per unit of reader attention**,
i.e. rate × precision on a population where the *defect* (reading a
pipeline's rc as its producer's), not the *precondition* (a pipeline
exists), is what fires. Nobody measured that. So the tree contains two
correct measurements of two non-deciding quantities, and a ruling
(R51's DROP) that got the right answer from the second-best one.

## 2. Independent verification of the fire rate

Corpus A: `work/toolcall-judge-v3/real-allowed.json` (78,242 distinct
`dcg_allow` commands, harvested 2026-09-20T05:22Z) — the file R51 used.
Corpus B: a fresh re-harvest tonight, `work/pipe-exit-reconciliation/measure.mjs`,
611 session files, 222,749 `dcg_allow` rows, 84,174 joined to a command
string, 81,722 distinct. Two corpora, one answer.

```
node work/pipe-exit-reconciliation/measure.mjs
```

| predicate | corpus A (78,242) | corpus B (81,722) |
|---|---:|---:|
| shipped hook glob `*"\| head"*\|*"\| tail"*` | 42,413 = **54.2%** | 44,074 = **53.9%** |
| R51's regex `/\|\s*(head\|tail)\b/` | 43,185 = **55.2%** | 45,342 = **55.5%** |

**R51's 43,185 reproduces to the unit.** CONFIRMED.

One honest wrinkle nobody flagged: R51's number is measured with a **wider
predicate than the code it justified**. The regex also matches no-space
`|head` (772 commands); the shipped glob does not. 54.2% vs 55.2%. Same
verdict, but the receipt and the code are not measuring the same thing, and
the receipt should say which.

Not a tonight artifact. Chronological quartiles of corpus B (R51 regex):

| quartile | window | rate |
|---|---|---:|
| Q1 | 2026-08-30 → 09-07 | 45.0% |
| Q2 | 09-07 → 09-12 | 50.2% |
| Q3 | 09-12 → 09-15 | 64.0% |
| Q4 | 09-15 → 09-20 | 62.7% |

Three weeks, 611 sessions, never below 45%.

R51's collateral claim, "of piped commands ~91% show no rc read":
61,538 piped, 5,894 of them contain `$?` → **90.4% read no rc**. CONFIRMED.

## 3. Reconciling 18.4% with 57%

They do not reconcile. **One of them is wrong, and it is 18.4%.**

- 57/100 (seeded sample) vs p = 0.552 → z = **0.36**. Consistent.
- 57/100 vs p = 0.184 → z = **9.96**. The seeded sample, on its own,
  refutes 18.4% at ten sigma. Both numbers are quoted in the tree as
  mutually corroborating; they are mutually exclusive.

I could not reconstruct any population that yields 18.4%:

| candidate 4,000-subset | rate |
|---|---:|
| top 4,000 by `seen` (what `harvest-allowed.mjs 4000` emits) | 63.7% |
| oldest 4,000 by session mtime | 66.2% |
| newest 4,000 | 58.1% |
| seeded random 4,000 | 53.7% |

Nor any predicate variant: `\| tail` alone 15.3%, `\| head` alone 42.1%,
last-stage head/tail 39.4%, head-with-numeric-arg 33.2%, pipes-and-reads-`$?`
7.5%. Nearest to 18.4% is `| tail` alone at 15.3%, still 3 points off.

**Verdict: 18.4% — UNVERIFIABLE, and refuted by the two measurements that
are reproducible.** Settling command: the table above, `measure.mjs`.

The defect is not the arithmetic, it is the sentence around it. R51 writes
"(conductor measured 18.4% on a 4,000 subset; **same conclusion at both
scales**)". A rate 3× lower is not the same scale and does not carry the
same conclusion with the same force — 1-in-5.4 and 1-in-1.8 are different
arguments about attention cost. A second number from the same lane was
banked as independent corroboration without being re-derived. Same-origin
agreement counted twice — which is the exact failure R48's own correction
block says it avoided.

## 4. The measurement nobody made

R51's trigger says the class may be rebuilt when "a surface where the rc
READ is observable" exists, and names two: harness per-stage metadata, or a
tool_result+isError join. It missed a third that already exists in the
string R51 itself scanned: **the read is frequently in the same command as
the pipe.**

R51 tested one narrowing family — *tighten the pipe pattern* (entire-command
+ last-stage head/tail + no pipefail) — and correctly found it drops the
strong positives, because those all have `; echo …$?` tails. It never tested
the orthogonal family: *require the read*.

Predicate: segment the command on `;`, `&&`, `||`, newline; fire only when a
segment containing `$?` (and not `PIPESTATUS`) is immediately preceded by a
segment whose last stage is `head`/`tail`; skip anything with `pipefail`.

```
812 / 78,242 = 1.04%      (vs 55.2% for the shipped glob)
```

Hand-labelled, seeded random 20 of the 812 — **17 true, 3 false, FP 0.15**:

- `python3 bin/gb-goldens-run.py 2>&1 | tail -5; echo "exit=$?"` — defect.
- `./scripts/quickstart.sh 2>&1 | tail -8; echo "rc_observed=$?"` — defect.
- `./node_modules/.bin/tsc --noEmit 2>&1 | head -30; echo "STRIPE_TSC_EXIT=$?"` — defect.
- …14 more of the same shape, including
  `./scripts/lane-status.sh 2>&1 | tail -16; echo "EXIT=$?"` — **this repo's
  own lane, its own documented trap, in the wild.**

The 3 false fires, each for a different reason:
1. `echo hi | head -0; echo "head -0 rc=$?"` — head's rc is the thing under test.
2. `echo "$digest" | head -2; echo "DIGEST_RC=$?"` — producer is `echo`; it cannot fail, so no misread is possible.
3. `… | head -1; echo "PIPED rc=$? (pipeline status -- inadmissible, shown on purpose)"` — the author annotated the trap in the command itself.

So the deciding axis, finally measured: the shipped glob delivers ~0.95
precision at a 55% rate (one warning every 1.8 commands); the read-required
predicate delivers ~0.85 precision at a 1.04% rate (one warning every 96
commands), and it **contains** all four of the FP receipt's strong
positives by construction, since it requires exactly the `; echo …$?` tail
they share. That is a 53× reduction in attention cost for a 0.10 loss in
precision.

I am **not** re-adding the class on this measurement. n=20 is one reader
and the labels are mine; three of my twenty "false" calls turned on author
intent, which a string scan cannot see, and intent-sensitivity is a warning
that the FP will be worse on a bigger sample. What this measurement does
establish is narrower and sufficient: **R51's "narrowing fails measured" is
true of the family it tested and false as a general claim**, and R51's
trigger is closer to satisfied than R51 believed.

## 5. Corroboration of the FP receipt's strongest claim, live

The FP receipt argues the class earns its place because "every bare
`cmd | head` in a bash tool call also reports head's rc to the harness as
the tool result (isError observed)". Probed directly tonight:

```
bash -c 'exit 3' | head -1; echo "shell-reported rc=$?"
→ shell-reported rc=0        # and the tool call itself returned success
```

Producer exited 3; the shell and the harness both saw 0. **CONFIRMED live.**
This is the one claim in the three documents that raises the class's value,
and it survives.

---

## 6. Rulings

| ruling | status | why |
|---|---|---|
| R51 DROP of the shipped `pipe-exit` glob | **STANDS** | 55.2% reproduced exactly; 90.4% of piped commands never read an rc; precondition-not-defect is correct |
| R51's "18.4% on a 4,000 subset" | **OVERTURNED** | unreproducible on any slice or predicate; refuted at z≈10 by the seeded sample quoted two lines above it |
| R51's "narrowing fails measured" | **NARROWED** | true for the tighten-the-pipe family; untested and false for the require-the-read family (1.04%, FP 3/20) |
| FP receipt's `FP = 0.053` for pipe-exit | **STANDS** | measures precision, honestly, and is not what decides |
| FP receipt's `KEEP` disposition | **SUPERSEDED** | disposition needs rate × precision; the receipt measured only precision, and its own frozen threshold ("DROP if FP > 0.50") cannot see a rate |
| FP receipt's harness-isError claim | **CONFIRMED** | live probe, §5 |
| R48's refusal of the `rcof.sh` wrapper | **STANDS, NOT IN CONFLICT** | different instrument (sender-side, behavior-altering, opt-in); says nothing about a receiver-side observe-only scan |

## 7. Annotations each receipt should carry (append, never rewrite)

**`guard-fp-rate-20260920.md`** — append (done, this commit):
disposition column superseded for `pipe-exit`; 0.053 stands; the frozen
threshold was precision-only and structurally could not see the 55% rate;
the isError claim confirmed live.

**`guard-dogfood-20260920.md`** — append (done, this commit): see §8.

**`NEGATIVE_EVIDENCE.md` R51** — append (done, this commit). The file was
uncommitted and owned by another lane when I drafted this; it was committed
at `e26b10f` before I touched it. Text appended:

> **CORRECTION appended 2026-09-20 (reconciliation lane, non-author).**
> Verdict stands; two numbers do not. (1) The 55.2% reproduces exactly
> (43,185/78,242) but with regex `/\|\s*(head|tail)\b/`, which is WIDER than
> the shipped glob it justified — the glob's own rate is 42,413 = 54.2%.
> (2) "conductor measured 18.4% on a 4,000 subset; same conclusion at both
> scales" is withdrawn: no slice (top-by-seen 63.7%, oldest 66.2%, newest
> 58.1%, random 53.7%) and no predicate variant reproduces 18.4%, and the
> seeded-100 sample quoted in the same paragraph refutes it at z≈10. Delete
> the parenthetical or replace it with corpus B (81,722 distinct, 55.5%).
> (3) "Narrowing fails measured" holds for the tighten-the-pipe family only.
> The orthogonal family — require the rc READ adjacent to the pipeline —
> fires 812/78,242 = 1.04% with FP 3/20 hand-labelled and CONTAINS all four
> strong positives. R51's trigger is therefore partly satisfied already:
> the read is observable in-string, not only in harness metadata. See
> `docs/demos/upstream-repro/pipe-exit-reconciliation-20260920.md`.

**`NEGATIVE_EVIDENCE.md` R48** — no correction needed. Add one cross-ref
line so the next reader does not re-litigate: R48 refuses the *wrapper*;
the receiver-side observe-only scan is R51's object, not R48's.

## 8. What `guard-dogfood-20260920.md` should now say

Its proof row quotes `class: "pipe-exit"` from session
`2026-09-20T17-49-12-422Z_01a0bfef`. That build is gone: all 10 installed
copies now hash `f10f7e16`, which has no `pipe-exit` branch.

Verified by running the *installed* classifier on the receipt's own witness:

```
cp ~/.omp/profiles/jev-lab/agent/hooks/pre/guard-rule.ts /tmp/gr-installed.mjs
node -e 'import("/tmp/gr-installed.mjs").then(m=>console.log(m.classify("echo probe-ok | head -1").cls))'
→ null
```

So:

- The receipt's **claim** ("LOADING PROVEN") **still stands**. A decision row
  proves the handler ran; which class it carried is incidental to loading.
  The claim does not depend on the dropped branch.
- The receipt's **witness is superseded and no longer replayable**. Under
  `f10f7e16` the same command produces `guard_pass`, not `guard_fire`.
- The replay recipe must change. A fresh loading proof needs a probe that
  still classifies: `grep -c …` → `grep-as-proof`, or a `git add -A`-shaped
  string → `stage-all`. Failing that, `guard_pass` plus the
  `diagnostic.v1` row (which fires on every `tool_call` regardless of tool)
  is sufficient evidence of load.
- Append, do not edit the quoted JSON. It is a true record of a build that
  existed; deleting it would destroy the only evidence that the drop
  actually changed installed behavior.

## 9. Does a code change follow?

**Not to `guard-rule.ts`. Yes to the git tree — and that one is now closed.**

`classify()` as installed is correct and I did not touch it. But while
verifying the three rulings I found the reason "nothing in the tree
reconciles them": at `1c2b4f0` the reconciling artifacts did not exist in
git at all.

| artifact | worktree, as measured | HEAD `1c2b4f0`, as measured |
|---|---|---|
| `work/omp-guard-rule/guard-rule.ts` | `f10f7e16` — pipe-exit dropped | `d26727a0` — **pipe-exit live** |
| `NEGATIVE_EVIDENCE.md` R51 | present | **absent** (`grep -c '^## R51'` → 0) |
| 10 installed hook copies | `f10f7e16` | n/a |

The drop ruling and the drop code were **both uncommitted**. A fresh clone
got a guard that classifies `pipe-exit`, a receipt saying KEEP, and no R51
— a tree with no conflict and the wrong answer. Installed code ahead of
committed code is the inverse of ordinary drift, and nothing here checks
for it: every gate in this repo compares the worktree against itself, so
the one direction that can regress a shipped ruling is the one direction
unguarded.

**Closed at `e26b10f`** ("installed code was AHEAD of HEAD, so a fresh
clone regressed") by the conductor, who adopted the unstaged edits, landed
`guard-rule.ts` at `f10f7e16`, its tests, R51, and a TESTS.md registry row
naming `pipe-exit` as ABSENT — so re-adding the class now breaks a
documented claim instead of silently reverting a ruling. Re-verified after
the fact: `HEAD:work/omp-guard-rule/guard-rule.ts` → `f10f7e16`, R51 in
HEAD → 1. The reconciliation above now describes the committed tree, not
just this machine.

The residual gap is not this instance, it is the missing check: no gate
compares an installed artifact's hash against its committed source. Left
unbuilt deliberately — that is a Creation-Gate question for the guard lane,
not something to bolt on inside a reconciliation.

Adjacent count corrections found while verifying, not part of the ruling:

- ~~**"10 installs" is 9.**~~ **RETRACTED within the hour — 10 is correct,
  and my correction was the defect.** Published first, then overturned by
  `DogfoodMap`, then re-verified by me rather than taken on their word:

  ```
  find ~/.omp -name guard-rule.ts -not -path '*/sessions/*' | wc -l   → 10
  # 1 global  ~/.omp/agent/hooks/pre/guard-rule.ts
  # 9 profile ~/.omp/profiles/{claude,codex,glm,grok,jev-lab,muse,omp-1,omp-2,omp-3}/...
  # all 10 hash f10f7e16
  ```

  I counted with `ls ~/.omp/profiles/*/agent/hooks/pre/guard-rule.ts`,
  which cannot see the **global** install surface — a real one, which
  `map-hook-ee` lists separately and credits with 61 `guard_pass` + 1
  `guard_fire`. Counting it twice did not help: both counts used the same
  blind glob, so repetition bought precision and zero accuracy. My
  speculation that the export clone at
  `~/Developer/jev_playground-export/work/omp-guard-rule/guard-rule.ts`
  (real, still `d26727a0`) was "what was counted" was invention on top of
  a bad census. `map-hook-ee`'s 10 and the conductor's "all ten" were both
  right.

  Left standing rather than deleted because it is this receipt's own
  instance of the defect it rules on: a narrow probe read as a complete
  census, published as a correction of someone else's correct number. The
  guard class I just declined to re-add exists to catch the same shape one
  layer down.

  `cba7e8b`'s commit subject-body carries the wrong count ("9 installs, not
  10") and is not amendable. This bullet is the correction of record; a
  reader mining commit messages for counts will find a number the tree
  contradicts, which is itself worth knowing about commit-message mining.
- `DogfoodMap` reports guard-rule row counts of 148 by the canonical
  `customType` key vs 200 published in MAP.md (bare-identifier grep). None
  of my numbers inherit that count — my denominators are command corpora
  (78,242 / 81,722), measured from `dcg_allow` bridge rows, not from
  guard-rule decision rows.

One unrelated live finding, recorded because it is the same defect class
this guard exists to catch: **dcg denied a `bash` call of mine because the
literal string `git add -A` appeared as DATA** — an element of a JS array of
test strings passed to the classifier, never executed. Mention-vs-use, in
the blocker, tonight. Worked around by writing `"git "+"add -A"`.

## NO-CLAIM

One reader. The 20-row hand label in §4 is mine alone and three of its
three false calls turn on author intent, which no string scan can observe —
treat FP 0.15 as a floor, not an estimate. Segmentation in §4 splits on
`;`/`&&`/`||`/newline without a shell parser, so quoted or heredoc-contained
separators mis-segment; I did not quantify that (the FP receipt did check
heredoc containment for its own sample and found none). R51's "narrowing
still fires 6.0%" is **UNVERIFIABLE as written** — the prose does not pin
the predicate; my two nearest readings bracket it at 1.9% (whole-command
pipeline, head/tail last, no pipefail) and 39.0% (last-stage head/tail, no
pipefail), and I make no claim about which R51 meant. The seeded-100
sample's own sha (`c05a027cf8e77102`) is not reproducible from this tree —
no sampler was committed — so its 57 fires are corroborated statistically
(z = 0.36 against 55.2%) and not re-derived. No blocking claim follows from
any rate here; every instrument discussed is observe-only. `[receipt]` used.
