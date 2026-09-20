# pipe-exit v2, mined from dcg: 1.03% fire rate, 0–1 FP of 10 `[live]`

One item, dogfooded to a solution, on the corpus we already had and were not using.

## The mining substrate nobody reads

`dcg` holds **223,945 `dcg_allow` decision rows** — every bash command this fleet has run, with
a verdict. `work/toolcall-judge-v3/real-allowed.json` is a **78,242-command** harvest of it.

**Zero `ee` extensions read any of it**: `rg -l 'dcg' ~/.omp/omp-extensions/ee-*.ts` → **0**, and
`ee journal list` in this workspace is `entryCount 0` against **14,196** `bash_failure` rows. The
richest corpus we own and the memory system that needs it are not connected. That is the mine.

## Predicate reconciliation — my number was 5× wrong

R51 dropped `pipe-exit` on a **55.2%** fire rate. Reproduced **to the unit**: 43,185 / 78,242.

Then the narrowing. Three predicates, same corpus:

| predicate | hits | % of all commands |
|---|---:|---:|
| `\| head\|tail` (v1, shipped then dropped) | 43,185 | **55.2%** |
| `$?` anywhere in a piped command (mine) | 3,956 | 5.06% |
| **rc read AFTER the pipe** (agent's) | 818 | **1.05%** |
| v2 = that, minus `set -o pipefail` | **807** | **1.03%** |

**My predicate was 5× too loose** — it counted `$?` appearing *before* the pipe, or belonging to
a redirect. The defect is specifically *the read that follows the pipe*, and the agent's
predicate says so. `pipefail` turned out to be a rounding error: 11 of 818.

## Hand-labelled, seeded, full matched span

Ten of the 807, seed 1. **All ten are the defect shape.**

```
1  bin/gb mcp tools transcript-mcp 2>&1 | head -5; echo "rc=$?"
3  ...crates/ack-spine/src/ack.rs 2>&1 | head -6; echo "rustc exit=$?"
4  ...src/resident.rs 2>&1 | head -n 12; echo RC=$?
7  ...--msg-file=/tmp/r24/pane1-report.md 2>&1 | tail -20; echo "rc=$?"
10 ...| grep -v "WARN rch" | tail -20; echo "BUILD_RC=$?"
```

Every one reports head/tail's status as the command's. **The most interesting row is #2** —
`| head -1; echo "PIPED rc=$? (pipeline status -- inadmissible)"` — an author who already knew,
annotating the trap inline. Count it a false positive and the rate is **1/10**; count it a true
match with an informed author and it is **0/10**.

## The result

```
v1  55.2% fire rate   ->  wallpaper, dropped under R51
v2   1.03% fire rate  ->  53x quieter, same defect class, 0-1 FP of 10
```

**A 53× reduction in noise for the same defect.** This is what R51's own reopen trigger asked
for: it recorded that narrowing had been tried and failed, but it had only tested
*tighten-the-pipe*, never *require-the-read*.

## What I am NOT doing

**Not re-adding the class.** `ReconcilePipeExit` owns that ruling and is mid-flight; this is
evidence handed to the owner, not a unilateral revert of R51. The agent declined to re-add on
n=20 and was right to; this is n=807 with a labelled sample, which is the denominator that
decision deserves.

## NO-CLAIM

One corpus (78,242 harvested `dcg_allow` commands, one machine, one fleet), one labeller, ten
labels. The FP estimate is 0–1 of 10 and the interval on that is wide. The v2 predicate is
regex over a command string: it cannot see whether the agent actually *read* the printed rc, so
it still detects a strong precondition rather than the mistake itself — R51's core objection is
narrowed by 53×, not eliminated.

## The instance that settles it: our own gate, 223 times

`ReconcilePipeExit` caught this in the wild and I reproduced it:

```
cd /Users/josh/Developer/jev && ./scripts/lane-status.sh 2>&1 | tail -16; echo "EXIT=$?"
```

**`lane-status.sh` exits 3 when a verdict cites a receipt that does not exist.** That is the
lane's one automated honesty gate. Read through `| tail`, it reports `EXIT=0` **whether or not
the gate failed**. Harvested count of piped `lane-status` invocations: **223**.

Live confirmation of the mechanism, this session:

```
bash -c 'exit 3' | head -1; echo "rc=$?"   ->   rc=0
```

The tick protocol instructs the conductor to run that script every 20 minutes. For 223 of those
runs the failure signal could not have reached the reader.

## Convergence, and the contamination in it

The owning agent measured **812 / 1.04%, FP 3/20**; I measured **807 / 1.03%, FP 0–1/10**. Two
predicates (their segment-splitter, my regex), same answer.

**This is not two independent confirmations.** I read their 1.04% in an IRC message *before*
running my decomposition, so my derivation was anchored, not blind. Same-origin evidence counts
once — the rule this lane already wrote down. Their labelling is also the better of the two:
n=20 against my n=10, and they identified the FP driver I could not see from my sample —
**author intent, which no string scan detects** — making **0.15 an FP floor, not an estimate.**
Where we differ, their number governs.
