# Commit learnings pass — what the last 48h actually taught, and what we are not using

Level: `live` where a command was run for this document, `NO-CLAIM` marked inline otherwise.
Scope: `main` since 2026-09-18, plus open PRs #9–#17. Counts re-derived for this pass, not
recalled.

**Headline, and it is against us:** the lane built 21 extension packages, 18 of them installable,
20 with a test file — and **exactly one produces any exported data**. We have been counting
packages as product. A package that scores nothing and exports nothing is a stub with a test.

---

## Cluster 1 — The judge does not generalise; one question out of seven survived

**LEARNED (falsifiable):** Of seven Jev question sets measured against real traffic, six are at or
below their own constant baseline; only `security_control_tampering` fires on danger a rule did
not already express.

Receipts: `judge-seat-ruling-20260920.md` (`6830ce2`, 2,531 real calls),
`commit-judge-31-20260919.md` (`0befea4`), `toolcall-judge-jev-vs-regex-20260920.md` (`c6eb7ab`).

| question set | verdict | control |
|---|---|---|
| tool-call v3 (4 questions) | regex simulator, **no model call at all** | 28 fires / 77,767, 28/28 false positives |
| commit `describes` | DEGENERATE | said yes 31/31, constant 30/31 |
| commit `overstates` | WEAK | 14 false positives / 31, constant 31/31 |
| commit `omits` | WEAK | constant 30/31; missed the one real omission by 0.01 |
| `irreversible_publication` | noise | 12/12 ordinary `git add` / `pull` |
| `secret_staging` | mostly noise | 6 of 8 were `infisical run`, the *correct* pattern |
| `security_control_tampering` | **KEEP, provisional** | 8 rows, six forms sharing no keyable token |

**NEXT STEPS ARE FASTER BECAUSE:** we stop writing question sets speculatively. The gate is now
mechanical and cheap — `work/jev-client/measure-kit.mjs` computes the constant baseline, and any
question that does not clear `best_constant + near_threshold_count` is dead on arrival. That is a
five-minute check that would have saved six question sets.

**WHERE TO APPLY:** omp profile (pre-action surface, the one surviving question, observe-only);
GrokBot and CFS should **not** adopt the other six.

---

## Cluster 2 — Hand-built numbers are ceilings, never estimates

**LEARNED:** Every hand-built corpus this lane produced failed to transfer to real traffic — six
for six, including the `describes 0.11 / omits 0.92` figures that were the entire basis for
shipping the commit judge.

Receipts: `commit-judge-31-20260919.md` (`0befea4`), `1d4e0c8`, `6830ce2`.

**NEXT STEPS ARE FASTER BECAUSE:** `work/toolcall-judge-v3/harvest-allowed.mjs` now regenerates a
real denominator on demand — 1,273 omp session files, 218,759 dcg allow-verdict bridge rows,
**77,767 distinct commands** — so a real control costs one command instead of a day of invention.
No future measurement in this lane needs a hand-made corpus.

**WHERE:** every lane. This is the most portable thing we learned.

---

## Cluster 3 — Mention-vs-use is a defect class, and it fools models too

**LEARNED:** Text *about* a command scores as the command; this broke the regex (28/28 fires) and
Jev independently (6 of 18 exclusive fires were commit-message heredocs).

Receipt: `c6eb7ab`; fix and tests at `work/toolcall-judge-v3/rules-v4.mjs` + `rules-v4.test.mjs`
(10 tests, `6830ce2`).

**NEXT STEPS:** `stripQuotedPayload` is written, tested and importable. Two of its tests failed on
first run and caught a real bug — `"$(...)"` and backticks are quoted but **executed**, so naive
stripping hid genuine token capture (`TOKEN="$(infisical login --plain)"`).

**WHERE:** anything reading agent transcripts — retransmit-killer/compaction especially, where
*everything* is quoted payload. GrokBot skill-shape checks have the same exposure.

---

## Cluster 4 — jevcache: disqualified, removed

**LEARNED:** A field name matching the volatile-identifier rule is deleted *before* hashing, so
`{"command_id": "rm -rf /"}` and `{"command_id": "echo hello"}` produce an identical fingerprint;
decide the benign one first and the destructive one returns the cached benign answer with the real
model's name on it.

Receipts: `work/jevcache-probe/REMOVED.md`, `8fe44b2`, `f717ba3`; upstream
`hyperspaceai/jevcache#1` (filed, open).

Second finding, operational and more portable than the first: **a hub-supervised process cannot be
killed.** Four separate "it is stopped now" claims were made before tracing pid→ppid to
`__omp_worker_daemon_broker`. `restarts=8`. `hub stop` ended it in one call. **A new PID after a
kill is the signature of supervision.**

**NEXT STEPS:** our real cache-hit ceiling is **3.0%** (2,417 re-executions of an identical command
out of 80,184), not the 67.9% headline — so caching was never the leverage. Nothing routes through
a cache; identical answers make drift structurally invisible.

**WHERE:** all lanes — the `hub ps` lesson especially.

---

## Cluster 5 — The dont-give-up skill loop (PRs #9–#15, #16, #17)

**NO-CLAIM.** These are open PRs authored in other panes; I have not re-executed their evidence,
and a pane's report is a claim. Titles carry their own levels (`#16 [test]`, `#17 [pending]`).
Merge track is Joshua's, in flight. Nothing here is graded by me.

---

## Where Jev is actually good — upstream surfaces, cited

**promoted = 0.** Nothing below is promoted; all are observe-only.

| surface | evidence | honest status |
|---|---|---|
| control-tampering detection on shell traffic | `6830ce2`, 8 rows, 6 distinct forms | best result we have; **provisional**, retirement test in flight (panes %71/%73) |
| harm gating | `omp-harm-rule`, 94 real rows, 0 FN / 0 FP; 1/814 recall vs real dcg blocks, 0/500 FP | **the rule won** — 4 regexes beat Jev 12/12 vs 11/12 at zero cost; contains no model call |
| commit message vs diff | `0befea4` | **REFUTED** on real commits |
| dispatch routing | published as a negative result, 7/15 vs coin-flip 7.5 | REFUTED, published anyway |
| GEPA / jev-align optimisation | zero question changes across ~800 metric calls; two upstream defects reproduced | REFUTED as a lever |

The defensible one-line ruling: **Jev earns a seat where no rule can be written and the form space
is open. It loses wherever a regex can be written, which is most places we tried.**

---

## PRODUCT HOLE: installable != exportable

Re-derived for this document (`ls`/`package.json` inspection, not recall):

```
total 21 | omp.extensions entry 18 | with a test file 20 | WITH EXPORTED DATA 1
```

**Three claims I have repeated this session are false and are corrected here:**

1. "Nine extensions" — there are **21** packages.
2. "All installable" — **3 are not**: `omp-jev-observer` has a `package.json` with **no
   `omp.extensions` entry**, and `omp-jev-dispatch` and `omp-harm-rule` have **no `package.json`
   at all**. `omp-harm-rule` is our single best-performing component.
3. "Extensions produce Jev-derived scores we can export" — only
   `work/omp-jev-commit/labels-31.json` exists, and it is **hand-written truth labels, not Jev
   scores**. **Zero packages export a Jev-derived score.**

### The hole, named

**`installable != exportable`.** The lane optimised the wrong property. "Installable" was the bar
we tracked and hit 18 times; "produces a score someone can read" was never a bar at all, and we
hit it zero times.

```
installable (omp.extensions entry)   18 / 21
has a test file                      20 / 21
exports ANY data                      1 / 21
exports a JEV-DERIVED SCORE           0 / 21
```

The single export, `work/omp-jev-commit/labels-31.json`, is **hand-written truth labels** — the
opposite of a Jev-derived score. So the observability we built is a closed loop: 21 packages
observe, and nothing downstream can read what they saw.

**The fix is a contract, not another package.** Every observe-only extension should append a row
carrying, at minimum: the Jev score, the question key, the model version, and the input's
identity. `omp-jev-commit` already proves the shape works (`commit_error` on failure, never a
silent pass); it just writes nothing durable.

**Consumer, gate, defect, retirement — the creation gate, answered:**

1. *Consumer:* the measurement harness, and any future calibration run — both currently have to
   re-derive scores from scratch because no package retains them.
2. *Gate:* an extension cannot be called shipped while it exports nothing; "observe-only" describes
   its blast radius, not its output.
3. *Observed defect:* 2,531 Jev calls were made tonight and **every score was discarded** after the
   run that produced it. The commit-judge measurement had to re-score 31 commits that extensions
   had already seen.
4. *Retirement:* when ≥1 package exports Jev-derived scores that a second measurement reads
   without re-calling the API.

This is the highest-value unclaimed work in the lane, and it is product, not process: it makes the
next measurement cheaper instead of measuring the last one.

---

## Owned dicklesworthstone tooling we are NOT applying

Installed on this machine; references inside this repo counted by grep.

| tool | refs | the miss |
|---|---|---|
| `cass` | 0 | Session mining would have surfaced the ten wrong-selector failures as one pattern instead of ten separate rediscoveries. |
| `fh` | 0 | The harvest corpus is exactly what `fh search`/`suggest` is for; we hand-rolled a JSON scan instead. |
| `bv` | 0 | Graph-aware triage; we picked beads by eyeballing `br ready` and twice dispatched work already assigned. |
| `rch` | 0 | Appears 3,282 times in *our own traffic* as the fleet's build path, and zero times in this repo — every local build here is unoffloaded. |
| `ee` | 0 | Procedural memory would carry the `readRow`/`requireKey` selector rules across sessions instead of re-deriving them. |
| `pt` | 0 | Process triage would have found the hub-supervised jevcache in one command instead of four wrong "it's stopped" claims. |
| `caut` | 0 | We had no idea whether Jev calls were rate-limited; Joshua had to tell us the API was free to use. |
| `jsm` | 0 | Skill quality grading, directly relevant to the five skills Muse is authoring now. |
| `ubs` | 1 | Referenced once, never run on any extension. |
| `am` | 1 | `am inbox` returned `count: 0` on 20 consecutive checks — dead transport, still nominally in the contract. |

Applied and load-bearing: `dcg` (6), `br` (6), `ntm` (1). `dcg` blocked four destructive commands
during the jevcache removal tonight and was right each time.

**Sharpest miss: `pt`.** It exists to answer the exact question that cost this session four false
claims.

---

## NO-CLAIM

- 657 commits touched `main` in 48h across all panes; this pass reads clusters and receipts, not
  every commit. Clusters 1–4 are ones I executed or re-derived; cluster 5 is not graded.
- The extension census is structural (`package.json` + file presence). It does **not** prove the 18
  installable packages install cleanly — no `omp` install was run for this document.
- The tooling table counts grep references in this repo only. A tool with 0 refs may be used
  elsewhere on this machine; the claim is "not applied *here*".
- `security_control_tampering` rests on 8 rows. The retirement test (panes %71/%73) has not
  reported.
