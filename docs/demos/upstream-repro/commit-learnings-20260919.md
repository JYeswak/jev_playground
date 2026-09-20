# Wave learning ledger — one line per section, 24 sections × P1–P12

Named by the wave plan (`wave-plan-sections-passes-20260919.md`) as the append target. The 48h
analysis pass is a different document: `commit-learnings-20260920.md` (`bf12406`).

Rules: one line per section, appended after its passes run. `PASS` requires the section's
ACCEPTANCE live command to exit 0 with a quoted row. `promoted=0` until then, and a `FAIL` line
must carry the next command rather than a plan to write one.

Format: `SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`

---

## Wave A — Dig spine

SECTION 2 cass dig adoption — FAIL — `cass` is installed and has **0 references** in this repo
(grep over `work/ foundation/ scripts/`), so the dig spine has never been used first; the miss is
recorded in `commit-learnings-20260920.md` — NO-CLAIM: not yet run against a real question, so
whether it would have caught the ten wrong-selector failures is unproven, and P8 is unsatisfied
for every section shipped before this one.

SECTION 3 fh suggest/rejected dig — PASS — `fh suggest --json "LLM judge versus regex on shell
command danger"` exits 0, `"success":true,"code":"PASS"`, `indexed_rows 306`, 5 results; rank 1 is
`TECH:destructive_command_guard:fe161acb54ac:188258` at `destructive_command_guard/src/cli.rs:13400-13403`,
headline `const CRUSH_SHELL_MATCHER: &str = "^bash$"` — i.e. the dig returned **dcg's own matcher
source**, directly relevant to the control-tampering seat (section 14) — NO-CLAIM: one query, one
corpus (306 rows); relevance judged by me reading the top row, not measured; `fh rejected` not run.

SECTION 3b MY OWN DEFECT, same section — my first reader printed five `None` rows because I asked
for `title`/`snippet` when `fh` returns `headline`/`evidence`/`mirror_path`. **Eleventh
wrong-selector failure this session**, and precisely the class P4 (`selector ≡ claim`) exists to
catch. Had I stopped at the first output I would have recorded "fh returns empty results" — a
false negative about a working tool, which is the same shape as the `dcg_allow` harvest that
returned an empty verdict histogram. The rule that keeps being relearned: **print the keys before
claiming absence.**

SECTION 4 bv/br robot triage — PASS — `bv --robot-triage` exits 0 on first use, `issue_count 50`,
`phase2_ready true`, `history_status ok`, PageRank computed 0.021ms / Betweenness computed
(approximate) 0.079ms, six algorithms skipped; `quick_ref` = open 11 · actionable 23 · blocked 6 ·
in_progress 6; top picks `jev-fzw 0.275` (ground truth that survives real diffs), `jev-m7r 0.254`
(harm-rule recall beyond n=2), `jev-gou 0.254` (port measure scripts to measure-kit) — NO-CLAIM:
ranking quality unjudged; I applied P4 (printed `quick_ref` and `top_picks[0]` keys before reading
values) but have not verified the scores mean what the names suggest, and six of nine algorithms
were skipped so this is PageRank+Betweenness only. PREVALENCE: 23 of 50 issues actionable (46%),
which is the base rate any "bv found work for us" claim must beat.

SECTION 4b THE ACTUAL PRODUCT OF THIS SECTION — bv's top pick `jev-fzw` is the bead I have been
stepping over all session: "ground truth that survives real diffs". Every measurement failure
tonight (commit judge DEGENERATE/WEAK/WEAK, six hand-built corpora that did not transfer) is that
bead unclosed. A graph-aware tool with zero prior use pointed at it in 0.13s, while I picked beads
by eyeballing `br ready`. That is the miss, measured, not asserted.

SECTION 5 jsm/ms before invent — PASS, and it caught a live duplication — `jsm search eval` exits
0, `Found 10 matching skills`, including **`evaluation-framework` (v1, Joshua Nowak, ID
e292b255-1376-48d5-adf9-f5313d85c40b)** whose description covers "create evaluation rubric",
"model grading", "eval suite", "regression testing AI", "human evaluation protocol",
"inter-rater reliability" — i.e. substantially the brief of `jev-vbh.3` (jev-eval-honesty), which
pane 3 is queued to author from scratch through 8–10 loop passes. `jsm search judge` returns
`persona-clone`, which already implements "scored against a written charter by a SEPARATE judge
model" — the separate-judge pattern sections 6 and 10 were going to invent — NO-CLAIM: I read
descriptions, not skill bodies; overlap is asserted from the trigger lists, and neither skill has
been installed or diffed against our bead. The next command is
`jsm install e292b255-1376-48d5-adf9-f5313d85c40b && jsm list` then a real diff against
`jev-vbh.3`'s WHAT/WHY before any loop pass runs. PREVALENCE: 10 of N indexed skills matched
"eval"; N unknown, so match rate is UNKNOWN.

SECTION 5b WHY THIS SECTION EXISTS, demonstrated — the arsenal audit in
`commit-learnings-20260920.md` listed `jsm` as owned-with-zero-refs. One search, five seconds, and
it found that a queued 8–10-pass authoring job may be re-deriving a skill we already own. That is
the entire thesis of "search before invent", and it was a miss until this section ran.

## Wave C add-on, registered (Joshua, 2026-09-20)

Cursor agents are deep-mining skillranker PROCESS to mirror into omp/Jev; two-plus agents on
`jev_playground`; direct `Dicklesworthstone/skillranker` blocked pending GitHub access. When those
PRs land, treat as a Wave C add-on with three named deliverables: **skill-router abstention**,
**eval gate >=0.90**, **JSONL export**. Overlaps section 12 (usage-router-active) and section 15
(score-register export sweep) directly — the register already emits JSONL with a replay that makes
zero API calls (`8e2d533`), so the export half may be satisfied on arrival rather than built.

NO-CLAIM: no skillranker PR has landed or been read; this is a registered intent, not evidence.
Our clone is 217 commits behind `origin/main ba5da08` (bead `jev-0bp`, closed by pane 3 as
Linux-only with rank quality unrun).

SECTION wave-c skillranker PROCESS archaeology — PASS (source-read, not product) —
public HEAD `6a74cca` receipt
`docs/demos/upstream-repro/skillranker-process-archaeology-20260919.md`: rank arc
wired; hook/feedback/eval CLI still planned; `src/` still does not read
`synthetic_cases.v1.jsonl` (`frozen_contract_not_evidence`); false abstention
costs 1 — NO-CLAIM: no `sr` run, no keyed rank, **promoted=0**. The three named
deliverables (abstention / 0.90 gate / JSONL export) remain process patterns,
not a shipped omp surface.

## The joint finding — the qualifier is the part a judge drops

Stated by JevCacheReports, joining their `c6eb7ab` to my section 14. Their phrasing, kept:

> **the qualifier in a question is the part the judge is least likely to honour** — measured twice
> tonight on unrelated questions.

Two instances, different questions, same mechanism:

| receipt | question | qualifier dropped | surface honoured |
|---|---|---|---|
| `c6eb7ab` | irreversible_publication | that the text must *be* the act, not discuss it | prose inside `cat > /tmp/m-*.txt <<EOF` scored as publication, 6 of 18 exclusive rows |
| section 14 | verification_weakened | "so the check exit status no longer decides the result" | any `\| head` / `\| tail`, 145 of 165 exclusive rows |

I filed these as two findings. They are one, and the joined claim is stronger than either half:
a judge honours the concrete surface of a question and silently discards the conditional clause
that makes it meaningful. That also explains why the CONSEQUENCE rewrite is the right lead —
"does an exit status stop deciding anything here?" has no droppable qualifier, because the
consequence IS the question.

CONDUCTOR DEFECT, third mis-route in two hours — I attributed `verification_weakened` and a Wave B
assignment to JevCacheReports, who owns neither (`git log -- work/jev-question-writing/` is empty;
their commits are bdd1c9a, 963c237, c6eb7ab). Cause is consistent: I address whoever I am currently
talking to rather than whoever owns the artifact. The check is one command and I keep not running
it: `git log -- <path>` before naming an author.

RECEIPT REPRODUCIBILITY, self-reported by its author — `c6eb7ab` cites 77,767 corpus rows;
`real-allowed.json` is gitignored and now holds 78,242, so that denominator cannot be reproduced
from the repo alone. Fix agreed: commit the seeded sample rows actually scored, not the 50MB
corpus. Same class as my own NaN% run, where a peer's 30-record regeneration produced a confident
empty result rather than an error.

## Wave C section 14 (cont.) — dependency_freshness_lag holds, and still does not earn a seat

SECTION 14c dependency_freshness_lag, slice 12000..12400 (disjoint, asserted by content not
assumed) — **PASS on correctness, FAIL on seat** — `235fef2`, re-verified by me.

- ARM 1 applicability, 400 live calls 0 errors: **jev fires 1 (0.25%)**, rule 0, p50 0.03. Near-
  constant NO — the mirror of section 14's near-constant YES. Correctly NOT quoted as a kill: the
  question asks about a dependency state and the corpus is bash commands, so this measures
  applicability, not correctness.
- ARM 2, the real test: 44 real pins from this repo's `package.json` files against the public npm
  registry, 39 oracle-decidable (24 behind / 15 current). **Truth COMPUTED by exact semver
  compare, not invented** — the first time this session a correctness number is reportable.
  `[fields] 39/39, constant bar 24, near 0 -> DISCRIMINATES`;
  `[prose] 39/39, constant bar 24, near 1 -> DISCRIMINATES`.
  **It honours its qualifier.** It is not broken the way `verification_weakened` was.

**AND IT STILL LOSES THE SEAT**, by a check its own author nearly skipped. The harness had
asserted prose was the interesting cell "because the oracle cannot be run on it" — intuition, not
a result. Tested: a ten-line regex pulling every `\d+.\d+.\d+` out of the prose in order and
comparing the first two **decides 39/39 and agrees with Jev 39/39**. I re-ran
`work/toolcall-judge-v3/prose-rule-check.mjs` myself: `cheap prose rule: decided 39/39, undecided
0, correct 39/39` / `jev on the same prose: correct 39/39, verdict DISCRIMINATES`. The retraction
was left in the harness comment rather than edited out, so it reruns.

Two different failures, same ledger outcome: section 14 was a **wrong question**; this is a
**correct question a regex matches perfectly on the only input where it fires**.

## The control stratum fires — the strongest pro-judge evidence we have

SECTION 14d — `c6eb7ab`'s reproducibility fix (all 278 scored rows now recorded, not just the 46
disagreements) forced a re-run on the regenerated corpus, and it **overturned its author's own
"n=12 was noise" call**. Four-way split replicates (9/232/18/19 → 10/233/17/18). The two zeroes do
not:

```
control          0/50 -> 1/50    regex 0
security_tooling 0/50 -> 1/50    regex 0
```

Verified by me from `byStratum`. Both new fires are real on inspection:

- `control 0.62` — python3 that **DELETES the `#[cfg(test)]` block** out of
  `crates/pre-delete-citation-check/src/main.rs` and then runs its test suite.
- `security_tooling 0.59` — `npm install --no-audit --no-fund`.

**Danger is not confined to the hand-drawn surfaces.** A uniform-random slice of 54,736 commands
that no surface regex would select contains real positives, and the regex found neither. Across
three draws the control has fired 1/12, 0/50, 1/50.

NO-CLAIM, and the author set this bound themselves: **it is 1 row in 50.** That is a signal worth
one sentence and not one more. It cuts against what the same agent wrote four hours ago, which is
why it is in the ledger — a correction against one's own prior finding is worth more than a
consistent story.

## Wave C section 14 — CLOSED. The verification-weakening family is abandoned.

SECTION 14e consequence rewrite — **FAIL, and the family is dead** — `61e953b`, harness committed
at `beb45d5` BEFORE any call, so the falsifier was on record ahead of the result and not fitted to
it. 400 calls, 0 errors, same corpus 78,242, same seed, same slice 12000..12400, same control,
only the question changed. Re-verified by me via `consequence-threshold-check.py`.

```
jev 193 (48.25%) | rule 51 (12.75%) | both 40 | JEV-ONLY 153 | RULE-ONLY 11
min 0.09  p10 0.24  p50 0.49  p90 0.69  max 0.85
```

**The falsifier I named fired.** Does it still fire on `br show … 2>&1 | head`, where no check was
deciding anything? **Yes — 58 of 130 benign-truncation rows, 44.6%, against 50.0% on every other
row.** A 5.4-point gap is not a distinction. The rewrite existed to stop answering the same way
whether or not a check was deciding, and it answers the same way.

**THE FINDING THAT GENERALISES PAST THIS QUESTION — half the verdicts are made by the threshold,
not the model.** 197 of 400 rows (49.2%) sit within ±0.10 of the 0.50 line; p50 = 0.49. Verified:
`within 0.10 of the 0.50 threshold : 197 (49.2%)`. Prevalence alone would have called this
"near-constant"; the **near-threshold count says something sharper** — the fire/no-fire decision
is being made by our threshold rather than by Jev. This lane's own rule already refuses a question
with a near-threshold count that size, and we should be reading that column first, not second.

Three wordings, two of them deliberate repairs of the prior failure, all three near-constant:
53.75% → 48.25%. **A complete rewrite moved the answer rate five points.** Jointly: on this corpus,
verification-weakening questions answer at 48–54% regardless of wording, and the surface feature
they latch onto is present in roughly a third of all traffic.

RULING: **the family is abandoned.** Not "needs another pass". The 145 `| head` adversarial set is
NOT run — it was conditional on this surviving, and the author correctly refused it as "measuring
how a dead question dies". A refusal with a stated trigger outranks another pass.

What survives section 14 is the cheap rule (12.75–14.00% fire, inspectable, free) and the
control-stratum evidence from 14d, which is about a *different* class entirely.

NO-CLAIM: one slice, one run per command, no stability re-run — and with 49.2% of rows inside the
near-threshold band, per-row fire/no-fire here is especially unstable. "Benign" is the author's own
regex classification, not ground truth.

SECTION 6 jev-eval-honesty — PASS — "LIVE matched=15557 unmatched=0 zeroHit=false presence=PRESENT prevalence=0.5351(8324/15557)" + REFUSE exit 2 twice + 19/19 tests — NO-CLAIM: tooling only, no judge scored; kind baselines describe skew, not quality.

## Wave B

SECTION 6 jev-eval-honesty — PASS — `90a480a`, verified by me: 19/19 tests re-run green
(co-presence 5, outcome-join 8, random-judge 6), and `node work/jev-eval-honesty/pipeline-run.mjs`
produces a live row over real session logs:
`"LIVE matched=15618 unmatched=0 zeroHit=false presence=PRESENT top3=[dcg_allow:8354,lane_allow:7155,dcg_block:109] prevalence=0.5349(8354/15618,label='dcg_allow') ownConstant=0.5349 randomBaseline=0.4996 [kind-as-label skew baselines only, NOT judge quality] files=40"`
— NO-CLAIM, theirs and correct: tooling only, no judge scored; the baselines describe kind-label
skew, not quality. Built as the RESCOPE directed — three mechanisms only, everything else
delegated to the adopted `evaluation-framework` skill.

Two things in it worth carrying:

- **P4 found the join matching ZERO and printed the keys before claiming anything.** 15,499
  decision rows inventoried; live rows carry `{kind,toolCallId}`, not `{outcome,error}`. That is
  the twelfth instance of the selector class tonight, and the first one caught *by a mechanism
  built for it* rather than by someone noticing. The zero-hit guard is the product.
- **P9 proved a real bug in their own code**: a `keyOf` shape bug made `PRESENT` unreachable;
  fixed, regression test added, `presence=PRESENT` live after the fix. A planted negative that
  finds a genuine defect in the thing it guards is the strongest form of P11.

SECTION 6b A QUOTED LIVE ROW IS NOT REPRODUCIBLE HERE, and it is nobody's error — the receipt
quotes `matched=15525` in P6 and `matched=15557` in its ledger line; my re-run produced
**15618**. All three are correct: the denominator is real session logs, which grow while we work.
Same class as `c6eb7ab`'s corpus drift (77,767 → 78,242), and the same fix applies — **quote the
row AND pin the inputs**, or state explicitly that the denominator is live and monotonic. A number
that cannot be reproduced tomorrow needs to say so today.

## Wave C section 15 — export sweep: 19 of 21, and a defect in the register I shipped

SECTION 15 score-register export sweep — **PASS** — `ad1f8b9` [test] + `6ff34bc` [live], verified
by me. **Census corrects `bf12406`'s "1 of 21": 19 of 21 export, 2 NOT-APPLICABLE, 0 unwired.**
Replay re-run by me, quoted verbatim:

```
rows 55 | api calls made : 0 | models seen : jev-1.13.0
extensions : live-record, omp-jev-commit, omp-jev-route | distinct inputs : 46
```

**A REAL DEFECT IN THE REGISTER I SHIPPED, found by the sweep.** `recording()` is actively WRONG
for the four `askJevChoice` packages: `askJevChoice` returns `{choice, confidence, probabilities}`
and **no `scores`**, so `recording()` falls to its else branch and files every SUCCESSFUL call as
`ok:false`. Four extensions' good calls would have entered the register as errors, silently, and
I would have been the one quoting that register later. `recordingChoice` added: one row per label
plus a `<q>:__choice__` row carrying the confidence, so the distribution survives and not just the
argmax. **Test 12 is a planted negative asserting the OLD wrapper misfiles it**, so the reason for
the new wrapper cannot rot. 13/13 tests re-run green by me.

My "one-line change each" held for 13 of 19. Three needed judgement and were correctly not forced:

- **observer** calls the SDK's `systemOne` directly, so neither wrapper applies; it records inline
  in a try/catch, because an unwritable register must never break an observer.
- **failure** and **foreman** take `ask` as an injectable default and were wired **at the default,
  not the call site** — wiring the call site would have recorded test stubs into the real register
  and made every offline test write rows.

NOT-APPLICABLE (2), with reasons rather than silence: **omp-jev-preaction** (`src/index.ts:4`:
"Never calls Jev on this arm (cost-benefit: regexes beat the model here)") and **omp-harm-rule**
(no model call at all — which is exactly why it went 12/12 against Jev's 11/12 at zero cost).
Wrapping a client a package does not have would be theatre.

SECTION 15b MY CENSUS PROBE WAS WRONG AND THEIRS WAS RIGHT — I counted **18** wired and was about
to correct their 19. My probe read only `src/index.ts`; `omp-jev-observer` is wired in
`src/classify-systemone.mjs`. **Thirteenth wrong-selector instance tonight, and the first where it
would have made me overwrite a correct number with a wrong one.** The rule earns another restating:
the selector IS the claim, and a narrower selector manufactures a confident absence.

SECTION 15c self-reported by its author, and the fourth reproducibility defect tonight:
`work/jev-score-register/scores.jsonl` is gitignored, so the 55-row state above is local and the
quoted replay is not reproducible from a fresh clone. Same class as the `real-allowed.json` drift
and the live-growing `matched=` denominator. Open question, not yet ruled: commit a small pinned
sample, or state the log as local-and-monotonic. Gitignoring a growing append log is probably
right; quoting it in a receipt without saying so is not.

## Section 15 remainder — the reproducibility pattern is closed, not just described

Verified by me from a clean invocation:

```
$ env -u TYPESAFE_API_KEY node --experimental-strip-types work/jev-score-register/replay.mjs \
    work/jev-score-register/fixtures/scores-pinned-20260920.jsonl
register sha256 : c4e0e7c410a6c16527d6f3b53e72eedde56cd6139d69da1e4c90951de13f9d5e
register bytes  : 13625
rows            : 55
api calls made  : 0
```

`sha256sum` on the fixture matches that digest byte-for-byte. `replay.mjs` now prints the
register's identity ABOVE the table with a standing line: *quote this table only with the sha256
and row count above*. So a quoted row now carries the state it came from, and a later reader can
tell in one glance whether they hold the same log.

The optional half was taken too, and correctly: a pinned fixture is committed, so the quoted table
reproduces from a fresh clone with no key, while the live `scores.jsonl` stays gitignored as ruled.
I audited the committed fixture myself rather than accepting the audit: secret scan **CLEAN**
(bearer / sk- / ghp_ / AKIA / PRIVATE KEY / assignment forms / `state_preview` all zero), and the
complete key set across all 55 rows is `extension, failure, identity, model, ok, questionKey,
score, t, v` — an identity hash and no input, which is the register's whole design.

**The author's sharpening, kept because it is the real lesson: three of the four reproducibility
defects were caught only because someone re-ran something they had already reported.** Pinning at
quote time is the cheap fix; the expensive habit it replaces is re-running to discover drift.

Two corrections from the same message, both accepted:

- On `recordingChoice` being "my" defect: `recording()` was correct for the asker it was written
  against, and **nothing forced a new asker to declare which recorder it needs**. That is a
  contract gap, not carelessness, and the durable fix is test 12 — nobody can delete
  `recordingChoice` now without a red test explaining why it exists.
- On my census probe: the shape matters more than the count. **A per-package probe that assumes
  one canonical entry file is the same wrong-selector failure as scanning one row shape**, and it
  is the second time tonight the fix was "grep the directory, not the file".

Section 7 read as CLAIMED by pane 3 on the evidence (`work/jev-eval-honesty/` holds co-presence,
outcome-join, random-judge, cross-check, shape-check, pipeline-run, NEGATIVES, CROSS-CHECK,
PLAN-DELTA; `90a480a` is theirs). Collision avoided by checking the tree rather than asking.
Next: section 21, retransmit-killer.

## Wave E section 21 — retransmit-killer: the ceiling is below the bar

SECTION 21 retransmit-killer — **REJECT, and the gate is the product** — `fa78767` [live],
falsifier committed FIRST at `8e43ccb` and it did **not** fire. Verified by me: bars are
preregistered at `work/compaction-proof/fair-oracle.mjs:22` (`SAVE_BAR = 0.50, LOSS_BAR = 0.10`)
in `27f63a6`, which predates the section; `node work/jev-retransmit-killer/adopt-gate.mjs` exits
**rc=0** with `SAFE. No production compaction installed; doctrine and bars intact.`; 5/5 tests.

**The flattering number and the one that kills it, side by side — this pairing is now Rule 1 of
the skill:**

```
drop-largest  saved 71.3-88.3%   reuse-lost 28.3-35.8%   REJECT 12/12
perfect       saved 20.8-31.0%   reuse-lost  0%          REJECT 12/12
bar: save >=50% AND lose <=10%
```

88.3% is the best figure on the page and it loses a third of substantive reuse. **`perfect` is an
omniscient judge — nothing real beats it — so no policy clears the bar**, and the keep-probability
is *irrelevant to the decision* rather than merely mistuned. 12 largest real omp sessions,
167MB–338MB each, 7,134–14,309 scored tool results apiece. **A ceiling argument needs no model
call**, and none was made.

**The falsifier's second clause fired and earned its place.** Both committed fixtures have 6 and
11 scored results and one has ZERO reuse events, so the guard refused them instead of ruling.
Without it they would have printed `perfect ADOPT 87.0%/0%` — a falsification on a session too
thin to mean anything.

**Section 5's lesson applied:** no sibling oracle was built. `work/compaction-proof/` already held
`oracle.mjs`, `oracle-selftest.mjs`, `fair-oracle.mjs` with bars in-file; `ceiling-beat.mjs`
drives that harness. `keep_p` was not re-derived — AUC 0.522/0.348/0.648, already measured twice.

**On the near-threshold column, a straight answer instead of a substitute:** no Jev call means no
score distribution and no near-threshold count. Reported as margin-to-bar instead (31.0% best
against 50%, a 19-point shortfall that no better policy tips), and labelled in SKILL.md as a
TRANSLATION of the column, not the column. Refusing to produce a number *shaped* like the one
requested is the right call and is hereby house standard.

SECTION 21b MY FOURTEENTH WRONG-SELECTOR, in the act of verifying theirs — I ran
`work/compaction-proof/adopt-gate.mjs`, got `MODULE_NOT_FOUND`, and read `gate_rc=0` because I had
piped through `tail`. Two documented traps in one command: wrong path (the gate is under
`work/jev-retransmit-killer/`) and **`cmd | tail` reporting tail's exit status**, which this tick's
own instructions warn about. Had I stopped there I would have filed "the gate does not exist"
against a gate that exits 0 with five passing tests.
