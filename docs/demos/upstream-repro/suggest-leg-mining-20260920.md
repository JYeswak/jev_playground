# The SUGGEST leg: four classes mined, two shipped, two refused `[live]`

Stage 3 of the hardening loop. DETECT is live (188 rows, 10 installs), RECALL is refused on
ee 0.15.2 and rerouted, WRITE-BACK has fired **once**. This is the missing leg: turn the
78,242-command `dcg_allow` harvest into predicates narrow enough to be worth firing.

The bar, set before measuring: **a class firing above ~5% is wallpaper and does not ship.**

## Results

| class | predicate | hits | rate | verdict |
|---|---|---:|---:|---|
| pipe-exit v2 | rc read AFTER the pipe, no `pipefail` | 807 | **1.03%** | shipped (prior receipt) |
| **glob-silenced** | `grep` over an unquoted PATH glob **with `2>/dev/null`** | **820** | **1.05%** | **SHIP** |
| count-as-verdict | `grep -c` whose count is the last thing printed | 1,486 | 1.90% | ship, unlabelled |
| live-file digest | `shasum` under `sessions\|logs\|.omp` | 14 | 0.02% | **REFUSE — too rare** |
| digest-truncation | `shasum … \| cut/awk/head` | 827 | 1.06% | **REFUSE — not a defect** |

Two refusals matter as much as the two ships. **14 hits does not justify a rule** — a rule that
fires twice a year is a rule nobody remembers the meaning of. And `shasum | cut` is ordinary
digest truncation, not a mistake; firing on it would teach readers to ignore the guard.

## The predicate I got wrong, and how

First attempt at the glob class matched **any `*`** after `grep`. Labelled sample of 12:
**8 were a `*` inside a REGEX**, not a path — `'fn .*resume'`, `'^\+.*(#\[test\])'`. **FP ≈ 67%.**

Re-narrowed to a token containing both `/` and `*`, unquoted: **8/8 genuine paths.** Then the
real narrowing — the glob is not the defect, the **silenced stderr** is:

```
grep -rl 'asupersync' crates/*/Cargo.toml 2>/dev/null
```

If the glob matches no path, `grep` prints nothing, exits 1, and the reader sees **"no matches"**
when the truth is **"no such path."** That is this repo's dominant defect class, and the harvest
says we do it **820 times**.

**Only hand-labelling caught the 67% FP.** A fire-rate number alone would have shipped it: the
broken predicate fired at 3.53%, inside the bar.

## Labelled sample

Seed `20260920`, n=20, segment-scoped. **17 true shape, 3 ambiguous** (the glob sits in a
neighbouring command in the same line). **FP floor ≈ 0.15** — identical to pipe-exit v2's floor,
and for the identical reason.

## NO-CLAIM

**The FP driver is author intent, which no string scan can see.** Many authors write
`2>/dev/null` on a glob *deliberately*, probing an optional path. The defect only exists when
the empty result is then read as "checked, none" — and the command string cannot show that. So
this detects a **precondition**, never the mistake, exactly as R51 objected. 0.15 is a floor.

One corpus, one machine, one labeller. `count-as-verdict` is shipped on its **rate only** — it
has no labelled sample yet, and its FP is unknown. Saying so is the point: the number that
exists is the rate, and the number that does not exist is the precision.
