# MAP.md stranger check — every number re-derived, both load-bearing claims tested `[receipt]`

I did not write `MAP.md` (`1c2b4f0`) and I did not write any of the six receipts it synthesises.
Scope: re-derive every published number with a command, resolve every link, test the two claims the
action plan rests on, and render the mermaid.

**Result: 7 of the 10 named numbers reproduce exactly. 2 are overturned. 1 has no source anywhere.
Load-bearing claim (a) is confirmed as a command and misleading as a sentence. Load-bearing claim
(b) is confirmed verbatim, its causal attribution is overturned, and its conclusion survives via
three mechanisms MAP.md does not name — one of which is a gate, not a status script.**

Measured 2026-09-20 at HEAD `1c2b4f0`, branch `work/cass-dig-vs-invent`. Exit codes captured
UNPIPED throughout.

---

## 0. Links and receipt mass

```bash
for f in map-hook-ee map-skillranker map-work-packages map-docs map-git-arc map-instruments; do
  p="docs/demos/upstream-repro/${f}-20260920.md"; [ -f "$p" ] && echo "OK $p" || echo "MISS $p"; done
grep -oE '\]\([^)]+\)' MAP.md | sed 's/^](//; s/)$//' | sort -u          # 6 links
wc -l docs/demos/upstream-repro/map-*-20260920.md | tail -1              # 2338 total
```

All 6 links resolve. All bare paths named in prose exist (`docs/demos/PLAN.md`,
`scripts/lane-status.sh`, `foundation/gates.sh`, `README.md`, `docs/demos/STATUS.tsv`).
**"2,338 lines of receipt" — CONFIRMED exactly.**

---

## 1. The ten named numbers

| # | claim | verdict | measured |
|---|---|---|---|
| 1 | 38 wired instruments | **CONFIRMED as a count · sentence OVERTURNED by 5** | 38 rows; but only 33 hang off `gates.sh` |
| 2 | 134 arms | **CONFIRMED** | 90 + 34 + 8 + 2 = 134, all 21 runs rc=0 |
| 3 | 36 instruments with no retirement condition | **CONFIRMED** | 36 |
| 4 | 323,575 rows from `~/.omp/omp-extensions/` | **OVERTURNED** | 381,142 attributable; label is 9,881 *below* two of its own children |
| 5 | 89 observer rows | **CONFIRMED exactly** | 59 + 30 = 89 |
| 6 | 200 guard-rule rows | **OVERTURNED** | 148 (81 + 67) |
| 7 | 40.4% of 1,098 non-merge commits | **CONFIRMED as-of** | 444/1,098 = 40.44%; live 444/1,121 = 39.6% |
| 8 | 9.2% of 206 receipts cited | **CONFIRMED as-of** | 19/206 = 9.22%; live 19/217 = 8.8% |
| 9 | largest source file 469 lines | **CONFIRMED exactly** | `work/skillranker-eval/score.mjs` 469 |
| 10 | `docs/demos/PLAN.md` 5,448 lines | **CONFIRMED exactly** | 5,448 |

### 1.1 — 38 wired: the count is right, the sentence moves 5 instruments to the wrong side

```bash
awk 'NR>=189 && NR<=241 && /^\| `/' docs/demos/upstream-repro/map-instruments-20260920.md | wc -l
# -> 51 rows = 50 instruments + scripts/README.md (registry doc, not counted)
… | grep -c 'WIRED'      # -> 39
… | grep 'WIRED' | grep -c 'HAND-RUN'   # -> 1  (verify-frozen.sh says "NOT WIRED")
# 39 - 1 = 38 WIRED, and the prose composition 13+10+7+2+1+4+1 = 38
git config --get core.hooksPath   # -> /Users/josh/Developer/jev/githooks
ls githooks | wc -l               # -> 4      ;  ls .omp/hooks/pre/ -> jev-compact.ts
```

The count is internally consistent and reproduces. **The MAP sentence does not:** *"38 wired
instruments hang off `foundation/gates.sh`."* Four githooks (live via `core.hooksPath`) and one omp
pre-compaction hook do **not** hang off `gates.sh`. **33 do.** The 5 it absorbs are precisely the
repo's *only* automatic triggers — the sentence files the counter-evidence to finding 1 inside
finding 1's own number. The source receipt states this correctly at its line 259; the compression
lost it.

### 1.2 — 134 arms, re-derived from 21 independent runs

```bash
for p in scripts/selftest-*.sh; do out=$(bash "$p" 2>&1); echo "$? $(tail -1 <<<"$out")"; done
for p in foundation/gates.d/[0-9]*-*.sh; do case $(basename $p) in 80-*) continue;; esac
  grep -qE '"\$\{1:-\}"[[:space:]]*(==|=)[[:space:]]*.--selftest' "$p" || continue
  bash "$p" --selftest; echo "rc=$?"; done
bash foundation/gates.d/60-staged-deletion-lane.sh                    # rc=0
bash foundation/gates.d/80-lane-instrument-selftests.sh --selftest    # rc=0
```

- 10 suites, run alone: 3, 18, 17, 8, 11, 9, 6, 2, 8, 8 = **90**
- 11 stage selftests (scan set B reproduced with stage 80's own detection regex): 1, 1, 1, 1, 3, 2,
  3, 3, 8, 6, 5 = **34**
- stage 60, live: `2 triggers + 6 satisfying witnesses` = **8** (and `git status --porcelain`
  md5 unchanged before/after — it works in `mktemp -d`)
- stage 80's own: `OK (2 arms: missing REDs as ABSENT, mode-dropped REDs as UNEXEC)` = **2**

90 + 34 + 8 + 2 = **134. CONFIRMED.** Every run rc=0.

**Reproduction trap found, not in any receipt:** `scripts/selftest-other-reasons.sh` and
`scripts/selftest-reason-numerals.sh` are `#!/usr/bin/env python3` files **named `.sh`**. Run them
the way their extension advertises —

```bash
bash scripts/selftest-other-reasons.sh     # rc=2, bash syntax error on a Python line
```

— and a stranger reproducing "10 suites" gets **2 false REDs** and would file a defect against
correct work. They pass rc=0 via their shebang (17 and 9 arms). Stage 80 invokes them correctly, so
the suite is fine and only the manual reproduction path is booby-trapped.

### 1.3 — 36 with no retirement condition

```bash
awk 'NR>=189 && NR<=241 && /^\| `/' …/map-instruments-20260920.md | grep -c '\*\*NONE\*\*'   # 36
```

36 table rows, and the prose enumeration sums independently to 36 (1 driver + 8 stages + 10 suites
+ 12 named + 4 githooks + 1 omp hook). 50 − 36 = 14 matches the stated 14. **CONFIRMED.**

### 1.4 — 323,575: OVERTURNED twice over

```bash
for p in ~/.omp/profiles/*/agent/sessions ~/.omp/agent/sessions; do [ -d "$p" ] || continue
  rg -oIN '"customType"\s*:\s*"(com\.zeststream\.[a-zA-Z0-9._-]+)"' -r '$1' "$p"
done | sort | uniq -c | sort -rn
cd ~/.omp/omp-extensions && for f in *.ts; do case $f in *test*) continue;; esac
  echo "$f $(rg -oIN 'com\.zeststream\.[a-zA-Z0-9._-]+' "$f" | sort -u | tr '\n' ' ')"; done
```

**(i) The published figure is internally inconsistent.** MAP.md's mermaid prints
`DCG 223,945` and `RCH 109,511` **inside** a subgraph labelled `323,575 rows`.
223,945 + 109,511 = **333,456** — the box total is **9,881 lower than the sum of two of its own
children**. Tracing it: 323,575 is exactly the source receipt's older by-file pair
(219,108 + 104,467, `map-hook-ee:168-169`), while the children are a later snapshot. Two
measurement times in one box, with the older one as the total.

**(ii) It is under-scoped by a whole extension.** `adapter.ts` and `observational-tool-result.ts`
live in the same directory and emit `omp-observational-hook.{capture,failure}.v1` = 33,000 + 14,205
= **47,205 rows** the figure omits. Attributable to `~/.omp/omp-extensions/` right now:

| identifier | rows |
|---|---:|
| `omp-dcg-bridge.decision.v1` | 224,188 |
| `omp-rch-lane-bind-bridge.decision.v1` | 109,749 |
| `omp-observational-hook.capture.v1` | 33,000 |
| `omp-observational-hook.failure.v1` | 14,205 |
| **total** | **381,142** |

Grand total across all identifiers: **385,368**. The "~328k rows" system-wide figure is also stale.
`11 extensions + 11 tests = 22 files` **CONFIRMED exactly.**

### 1.5 / 1.6 — the mermaid mixes two counting methods, and only one node uses the bad one

Canonical (`customType`) counts, all CONFIRMED exactly:

| mermaid node | published | measured | verdict |
|---|---:|---:|---|
| `omp-harm-rule` | 1,247 | 1,151 + 96 = **1,247** | CONFIRMED |
| `omp-jev-preaction` | 1,121 | 1,071 + 50 = **1,121** | CONFIRMED |
| `omp-jev-route` | 149 | 147 + 2 = **149** | CONFIRMED |
| `omp-jev-observer` | 89 | 59 + 30 = **89** | CONFIRMED |
| `guard-rule.ts` | **200** | 81 + 67 = **148** | **OVERTURNED** |

The 200 is not a measurement error, it is a **method** error, and its provenance is recoverable.
`map-hook-ee` counted with a bare identifier grep:

```bash
grep -rho "com\.zeststream\.[a-z0-9.-]*\.\(decision\|diagnostic\|event\)\.v1" \
  ~/.omp/agent/sessions ~/.omp/profiles/*/agent/sessions --exclude-dir='--private-tmp--' | …
# -> omp-guard-rule 214 · omp-jev-observer 1178 · omp-harm-rule 756
```

That is the exact method `map-work-packages:88-92` documented as **overstating ~40x** because it
counts the agent *talking about* an identifier across 11 GB of transcripts. Reproduced today it
returns **214** for guard-rule (vs 148 canonical) and **1,178** for observer (vs 89 — 13.2x).

So on 2026-09-20 two sibling receipts published the same number for the same package by different
methods — `map-hook-ee` 200, `map-work-packages` 136 — a 47% disagreement. **MAP.md took the higher
one, which is the one its own sibling receipt disqualified**, and placed it in a diagram where every
other row is canonical. 136 → 148 is consistent with monotonic growth; 200 → 148 is not possible.

### 1.7 — 40.4%: confirmed, and the definition matters more than the number

```bash
git log --no-merges --format='%s' > /tmp/subj.txt
for t in duel-2 queue instrument gauntlet duel duel-1 compaction plan route-backtest method \
         rung4 tick negative-evidence redteam lane hero gate oracle installer ensemble omp \
         verdict rung3 contracts; do grep -cE "\($t\)" /tmp/subj.txt; done   # sums to 444
grep -cE '\(duel-2\)|\(queue\)|…' /tmp/subj.txt          # union = 444  (no double-counting)
git rev-list --count --no-merges HEAD                    # 1121   (was 1098)
```

444/1,098 = **40.44% CONFIRMED as-of**. Live: the abandoned set is **unchanged at 444** while the
denominator grew to 1,121 → **39.6%**. The numerator is frozen and the denominator is growing: the
share is *falling*. A researcher reading 40.4% as a decay rate would have the sign wrong.

**Definitional gap worth acting on.** "Scope token" means *the subject contains `(token)`* — three
different denominators exist for `duel-2` and MAP.md names none of them:

| definition | command | count |
|---|---|---:|
| subject contains `(duel-2)` | `grep -cE '\(duel-2\)'` | **207** ← the published figure |
| conventional scope at subject start | `grep -cE '^[a-z]+\(duel-2\)'` | 99 |
| commits touching the directory | `git log --no-merges -- docs/demos/duel-2/` | 221 |

Action-plan row 5 says *"archive 207 commits of scope."* The archivable unit is the directory, and
that is **221**.

### 1.8 — 9.2%: confirmed, and the gap is widening

```bash
git ls-files docs/demos/upstream-repro | grep -c '\.md$'                              # 217 (was 206)
awk -F'\t' '!/^#/ && $1!="candidate" {print $6}' docs/demos/STATUS.tsv \
  | grep 'upstream-repro' | sort -u | wc -l                                           # 19
```

19/206 = **9.22% CONFIRMED as-of**. Live: **19/217 = 8.8%** — 11 receipts added, **zero** citations
added. This is the mirror image of §1.7: here the numerator is frozen and the denominator grows, so
the citation gap is *widening*. That strengthens action-plan item 4 rather than dating it.

### 1.9 / 1.10 — the two file-size numbers are exact

```bash
git ls-files | grep -E '\.(ts|mjs|js|py|sh|rs)$' | xargs wc -l | sort -rn | head -3
# 469 work/skillranker-eval/score.mjs   |  452 scripts/verify-other-reasons.sh
wc -l docs/demos/PLAN.md    # 5448
```

Both **CONFIRMED exactly**, including the 11.6x prose-to-code ratio the section is built on.

---

## 2. The one number with no source: "57 files use appendEntry"

The mermaid's `SESS` node publishes *"session JSONL — 57 files use appendEntry."* **UNVERIFIABLE —
and no definition reproduces it.**

```bash
grep -rn '\b57\b' docs/demos/upstream-repro/map-*-20260920.md
# the ONLY 57 in all six receipts: map-docs:258 "distinct entries (^## headings) | 57"
#   -> the heading count of commit-learnings-20260919.md. Nothing to do with appendEntry.
git ls-files | xargs rg -lN 'appendEntry' | wc -l                                  # 73
git ls-files | grep -E '\.(ts|mjs|js|py|sh)$' | xargs rg -lN 'appendEntry' | wc -l  # 54
git ls-files | grep -E '\.(ts|mjs|js)$' | xargs rg -lN 'pi\.appendEntry\(' | wc -l  # 21
```

73 / 54 / 32 (non-test) / 21 (real call sites) / 17 (markdown). Nothing lands on 57, and since the
tree only grows, an *earlier* code-extension count would be **≤ 54** — so 57 cannot be that either.
Best reading: a number was carried over from an unrelated measurement. The honest node value is
**21** (files with an actual `pi.appendEntry(` call) or **54** (files containing the token).

Also in the same diagram: subgraph `S1` is labelled *"5 of 22 installed"* — **CONFIRMED**
(`omp-harm-rule`, `omp-jev-observer`, `omp-jev-preaction`, `omp-jev-review`, `omp-jev-route`) — but
it **draws only 4 of the 5**. `omp-jev-review` is installed and emitting (3 + 3 = 6 rows) and is
absent from the picture.

---

## 3. LOAD-BEARING CLAIM (a) — "nothing automatically runs the gate driver"

```bash
crontab -l > /tmp/ct.txt; echo $?                              # 0, 18 lines
grep -cE 'gates\.sh|lane-status' /tmp/ct.txt; echo $?           # 0, rc=1
grep -rlE 'gates\.sh|lane-status' ~/Library/LaunchAgents/       # no match (95 plists)
grep -rlE 'gates\.sh|lane-status' .git/hooks/                   # no match
grep -nE 'gates\.sh' docs/demos/tick.md                         # rc=1, no match
```

**CONFIRMED for the driver.** `foundation/gates.sh` appears in no crontab line, no launchd plist,
and no git hook. The 134-arm suite fires when a human types the command.

**The grep's second alternative is misleading, and it is this repo's own dominant defect class.**

```bash
grep -nE 'gates\.sh|lane-status' docs/demos/tick.md
# 30:./scripts/lane-status.sh          # exits 3 if any verdict cites a receipt that does not exist
```

The crontab contains:

```
*/20 * * * * ntm --robot-send=jev --panes=1 --msg-file=/Users/josh/Developer/jev/docs/demos/tick.md
8,18,28,38,48,58 * * * * cd /Users/josh/Developer/jev && … fleet-idle-monitor --report-only
```

`lane-status.sh` **is** reached automatically every 20 minutes: the scheduler names a *file*, and
the invocation lives *inside* the file. `grep` over the crontab text cannot see it and returns 0.
**A zero-hit grep read as a clean result — the exact failure `scripts/vgrep.sh` was built to stop,
published in the headline finding of the document that describes it.** `map-instruments:224` gets
this right (*"cron sends the tick to pane 1, it does not run the script"*); the compression into a
single `-c` → **0** loses the distinction, and a stranger will read it as "no automation touches
this repo."

Compounding it: per §1.1, **5 of the 38 "wired" instruments are automatically triggered** (4
githooks + 1 omp hook), and the finding-1 sentence puts them on `gates.sh`'s side of the ledger.

**Net: the ruling stands — give `gates.sh` a trigger or say it is hand-run (item 3) — but the
evidence sentence must be rewritten, because "0" is the answer to a narrower question than the one
it is printed under.**

---

## 4. LOAD-BEARING CLAIM (b) — `lane-status.sh:87` and the 207 undeletable commits

This is the claim that decides whether the largest cleanup in the plan is blocked. It splits three
ways.

### 4a. The text: CONFIRMED verbatim

```bash
sed -n '87p' scripts/lane-status.sh
# SIDECAR_PATH="${JEV_SIDECAR:-docs/demos/duel-2/runs/receipt-other-reasons.json}"
```

### 4b. The causal attribution: **OVERTURNED — that read is FAIL-OPEN**

`SIDECAR_PATH` has exactly one consumer in the whole script, and it is guarded:

```bash
grep -n 'SIDECAR' scripts/lane-status.sh     # 85 (comment), 87 (assign), 92 (only use)
sed -n '92,95p' scripts/lane-status.sh
#   printf '%s\n' "$STATUS" "$SIDECAR_PATH"
#   … | sort -u | while read -r f; do
#     [ -n "$f" ] && [ -f "$f" ] || continue        <-- missing file is SKIPPED
```

Proof:

```bash
./scripts/lane-status.sh                                        # rc=0
JEV_SIDECAR=/tmp/definitely-not-here.json ./scripts/lane-status.sh   # rc=0
diff /tmp/ls-base.txt /tmp/ls-nosidecar.txt
# 1c1 — the timestamp line, and nothing else
```

**Deleting that JSON changes one line of `lane-status.sh` output: the clock.** It does not fail, it
does not warn, it silently drops a digest input. `lane-status.sh:87` does not make 207 commits
undeletable, and it does not make even *one file* undeletable.

### 4c. The conclusion: **CONFIRMED, and stronger — via three mechanisms MAP.md does not name**

**(1) The same default path is read by a FAIL-CLOSED consumer that IS a gate.**

```bash
sed -n '41p' scripts/verify-other-reasons.sh
# SIDECAR = Path(os.environ.get("JEV_SIDECAR", "docs/demos/duel-2/runs/receipt-other-reasons.json"))
sed -n '212,215p' scripts/verify-other-reasons.sh      # missing -> return 2

bash foundation/gates.d/90-sidecar-verifier-wrapper.sh                  # rc=0  PASS
JEV_SIDECAR=/tmp/definitely-not-here.json \
  bash foundation/gates.d/90-sidecar-verifier-wrapper.sh                # rc=1
# FAIL  stage 90 sidecar verifier   rc=2 usage/environment — STATUS or sidecar missing
```

The sidecar **is** load-bearing. Not for the status script MAP.md cites — for **stage 90 of the gate
ladder**, which goes RED without it. MAP.md cited the fail-open reader and missed the fail-closed
one that shares the same default string.

**(2) Fifteen *other* duel-2 receipts are hard-required by `lane-status.sh` — at a different line.**

```bash
awk -F'\t' '!/^#/ && $1!="candidate" {print $6}' docs/demos/STATUS.tsv | grep duel-2 | sort -u | wc -l
# 15   (all exist; and the line-87 sidecar is NOT one of them: grep -c -> 0, rc=1)
sed -n '367p' scripts/lane-status.sh          # elif [ "$missing" -gt 0 ]; then rc=3
```

Proof by mutation — repoint one cited receipt and the script fails closed:

```bash
sed 's#duel-2/runs/demo7-weights-20260918T041352Z.json#duel-2/runs/ARCHIVED-AWAY.json#' \
  docs/demos/STATUS.tsv > /tmp/s2.tsv
JEV_STATUS=/tmp/s2.tsv ./scripts/lane-status.sh          # rc=3
# FAIL: 1 of 40 STATUS rows cite a receipt that does not exist.
```

**(3) MAP.md's own refusal rests on an uncited duel-2 artifact.** The *"routing saved 0.0447%"*
ruling in "What NOT to do" has exactly one in-repo source:
`docs/demos/duel-2/FALSIFY_COD-H2_MU.md` — under `duel-2/`, and **not** among the 15
machine-checked citations. An archive that preserved only what `STATUS.tsv` cites would delete the
evidence for one of MAP.md's three "do not build" rulings, and no gate would notice.

### 4d. Consequence for the action plan

Row 5's blocker reads *"move the sidecar JSON first."* **Wrong consumer, and insufficient.** Moving
that one file satisfies nothing (`lane-status.sh` never cared), while the real prerequisites are:

1. retarget `verify-other-reasons.sh:41`'s default — or set `JEV_SIDECAR` at stage 90 — **or stage
   90 goes RED**;
2. relocate-and-re-cite **15** `STATUS.tsv` column-6 receipts, or `lane-status.sh` exits 3;
3. preserve at least one **uncited** prose artifact (`FALSIFY_COD-H2_MU.md`) that MAP.md's own
   conclusions depend on and no gate protects.

The cleanup is **not** unblocked. It is larger than the plan says, and the single blocker the plan
names is the one file that blocks nothing.

---

## 5. The mermaid block — UNVERIFIABLE as a parse

**I could not render it. I am not claiming it parses.**

```bash
which mmdc                                  # rc=1
npx --no-install mmdc --version             # npm error: could not determine executable to run
npm ls -g --depth=0 | grep -i mermaid       # rc=1
ls node_modules/.bin/                       # empty
```

A *different* mermaid implementation exists on this machine
(`/Users/josh/Developer/frankentui/crates/ftui-extras/src/mermaid.rs`, with `.mmd` fixtures), but it
is not mermaid.js and has no prebuilt binary (`target/release` empty). Substituting it would produce
a verdict about the wrong parser, so I declined.

Two defects proved from the text alone (block extracted = 39 lines):

```bash
awk '/^```mermaid/{f=1;next} /^```$/{if(f){f=0}} f' MAP.md > /tmp/map.mmd
grep -nE '\bTR\b' /tmp/map.mmd                      # exactly 1 hit: its own declaration, line 4
grep -cE ':::dead|class .*dead' /tmp/map.mmd        # 0, rc=1
```

- **`TR["tool_result (post-exec)"]` is a dangling node.** Declared, zero edges, referenced nowhere
  else. It renders as an orphan box — the post-exec leg the `LOOP` subgraph exists to show is drawn
  disconnected, while `TC` fans out to all seven emitters.
- **`classDef dead` is declared and never applied.** Only `gap` is used (`class HUMAN gap`). The
  diagram defines a style for dead surfaces and then marks nothing dead, though findings 3 and 5
  are entirely about abandoned surfaces.

---

## 6. Live-monotonic drift observed during this check

| corpus | receipt | now | direction |
|---|---:|---:|---|
| non-merge commits | 1,098 | 1,121 | +23 |
| abandoned-scope commits | 444 | **444** | unchanged → share falling |
| tracked receipts in `upstream-repro` | 206 | 217 | +11 |
| receipts cited by `STATUS.tsv` | 19 | **19** | unchanged → gap widening |
| `work/` directories | 53 | 54 | +1 |

The 54th `work/` dir is `work/pipe-exit-reconciliation/`, untracked, created **by a sibling agent
while I was measuring**. MAP.md's NO-CLAIM anticipates exactly this, and it held.

Confirmed exactly and not otherwise listed: 13 gate stages · 10 `guard-rule.ts` installs, 10
distinct inodes, all `f10f7e16` (1 global `~/.omp/agent/hooks/pre/` + 9 profiles) · 22 files in
`~/.omp/omp-extensions/` · 53 work dirs scoring KEEP 39 / ALIGN 12 / DISCARD 2 (= 53).

---

## 7. Can a researcher trust MAP.md as the entry point to this repo?

**Yes for the shape of the system and 7 of 10 headline numbers, but not yet for action: rewrite
finding 1's evidence sentence (the crontab grep answers a narrower question than it is printed
under), replace `guard-rule 200` with 148 and `323,575` with 381,142, delete the unsourced 57, and
re-aim action-plan row 5 at `verify-other-reasons.sh:41` plus 15 `STATUS.tsv` citations — because
the file it currently names as the blocker is the one file whose deletion changes nothing.**

---

## NO-CLAIM

- **I did not run `foundation/gates.sh`.** I ran individual stages (60, 80 `--selftest`, 90, and the
  11 scan-set-B selftests) and the 10 instrument suites. A full-driver green is not claimed, and
  stage-in-isolation PASS is not evidence about stage ordering or shared state between stages.
- **I did not render the mermaid block.** §5 is a text audit and two proved defects, not a parse
  verdict. If `mmdc` is installed later, §5's parse line must be re-answered, not inherited.
- **Row counts are `customType` counts over `~/.omp/profiles/*/agent/sessions` and
  `~/.omp/agent/sessions` only.** An extension writing to an external store (both `ee` legs) emits
  zero rows there by design and is invisible to this method — `map-hook-ee` names this blind spot and
  it applies to my numbers too. "381,142 attributable to `~/.omp/omp-extensions/`" means *these four
  identifiers are emitted by source files in that directory*; I did not prove no other file anywhere
  emits them.
- **The 444 abandoned-scope figure inherits the receipt's `(token)` definition.** I verified the
  union does not double-count and that the arithmetic holds; I did **not** independently audit
  whether those 24 tokens are the right 24, nor re-derive the ≥5-commits / >24h-silent cutoffs.
- **My 15-receipt duel-2 dependency count is `STATUS.tsv` column 6 only.** Other consumers may cite
  `duel-2` paths from prose, and §4c(3) shows at least one does. A complete pre-archive dependency
  sweep is not in this receipt.
- **I did not verify `ee` health, `EE-E040`, the `remember → preflight` link, or the skillranker
  `11m17s`.** Those belong to concurrent siblings; every claim about them here is quoted from the
  receipts, not measured by me.
- **The 148 guard-rule figure is a point measurement on a growing corpus.** It overturns 200 because
  200 is method-incompatible (a bare-identifier count, reproducible as 214 today), not because 148 is
  a ceiling.
- **`git status --porcelain` showed 8 pre-existing modified paths and 8 stashes before I started.**
  I wrote exactly one file and committed only it; the two `JEV_STATUS`/`JEV_SIDECAR` mutations were
  temp copies under `/tmp`, and stage 60 was confirmed tree-neutral by md5 of
  `git status --porcelain` before and after.
