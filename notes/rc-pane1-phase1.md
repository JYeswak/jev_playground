# Reality check — pane 1 (`%1`, `jev__omp-claude_1`) — Phases 1–2

**Method:** `skill://reality-check-for-project`, Variant A, run independently of
`docs/REALITY-CHECK-20260921.md` (pane 4 owns that file; I did not read it before deriving the
checklist below, and where we agree that is concurrence, not copying — where we disagree is
recorded in §6).

**Every number below was read out of a committed file today.** Citations are `path:line` or a
`jq` path into a committed JSON. Nothing is recalled.

---

## 1. The one-sentence answer

**Jev has a state-of-the-art application, it is already proven at n=1,383 with confidence
intervals by a third party inside this very tree, and we never looked at it — because not one of
the tasks we chose to test ever posed a discrimination problem.**

Our own `README.md:289-296` ships six omp packages under a column headed literally **`calls
Jev?`**, which the prose above the table glosses as *"whether a model call earns its place on
that surface, decided by measurement rather than preference."* **Four of the six say yes.** We
then reported the lane's state as "zero certified seats."

Those are not the same sentence, and the second one is the one that stopped the mission.

**Precision, since this is the headline.** "Four say yes" is not "four are proven seats." Of the
four: `omp-jev-rerank` and `omp-jev-failure` keep **exactly one** question each *after measurement
killed the others*; `omp-jev-review` has **never scored live** (§4 Q2); only `omp-jev-observer` is
unqualified. The defensible claim is therefore the narrow one — **a Jev call survived the
measurement filter on four of six surfaces** — and even that is irreconcilable with a flat "zero."

---

## 2. Vision checklist — re-derived from AGENTS.md "THE MISSION" + README.md

| # | Goal (source) | Status | Evidence |
|---|---|---|---|
| 1 | **Validate Jev** (`AGENTS.md` THE MISSION) | **WRONG_APPROACH** | 6 surfaces evaluated; 5 posed no discrimination problem (3 lexical, 2 constant-policy, §3a). Sampling error, not a verdict. |
| 2 | **Build tools from what survives** | **NOT_STARTED — premise error, not absence of input** | a Jev call survived measurement on 4 of 6 surfaces (`README.md:289-296`, `calls Jev?`); the input exists and was mislabelled as empty |
| 3 | **Liven omp surfaces** | **PARTIAL** | 1 hook, 1 MCP, 0 tools, 0 extensions; `omp-jev-rerank` scaffold built, **0 live rows** because omp emits no `search_result_observed` |
| 4 | **Dogfood** | **REGRESSED** | first real dogfood found the instrument broken (R68) |
| 5 | **Share publicly** | **PARTIAL** | 1 upstream issue + 2 corrections; ARC unpublished |
| 6 | *implied:* **cite external oracles over internal ones** (`AGENTS.md` RULE 13 clause 2) | **NOT_STARTED** | `jev-rerank-bench@cd9a35b` has sat unread in this tree with 67 MB of cached responses and 10,000-sample bootstrap CIs |

---

## 3. THE SEPARATION — "Jev lost to a regex on OUR tasks" ≠ "Jev has no application"

This is the assignment, and it resolves cleanly on arithmetic.

### 3a. What every task we tested has in common

Source for all five: `docs/demos/upstream-repro/RULING-authored-vs-real-20260919.md:87-93`.

| our task | the cheap thing that won | margin | mechanism |
|---|---|---|---|
| tool-call harm | four regexes | rule **12/12** vs Jev 11/12, both FP 0/40 | **A — lexical** |
| phishing verdict | two-line domain regex | **+27 pts**, McNemar p=1.5e-8 | **A — lexical** |
| router tier signal | prompt **length** | length won 2 of 3 sessions | **A — lexical** |
| tier routing for cost | **flat mid-tier pricing** | Jev **+90.2% more expensive**, 643 real sessions | **B — constant** |
| context compaction | **keep everything** | **7× fewer mistakes**; `keep_p` AUC **0.35–0.65** | **B — constant** |

**Correction to my own first draft.** I initially wrote that all five labels are "a pure function
of the literal input string." That is wrong for two of them, and the error matters, so here is the
corrected taxonomy — **there are two distinct mechanisms, not one:**

- **A — lexically decidable (3 of 5).** The label *is* a function of the literal tokens. `rm -rf`
  is in the text or it is not; the domain is in the URL or it is not; the prompt is long or short.
  A regex is not a *baseline* here, it is the **correct answer**, and a judge is a 400 ms tax on a
  solved problem.
- **B — a constant policy wins (2 of 5).** The winner is not a rule at all, it is a *constant*:
  always pick mid-tier, always keep everything. These tasks are not lexical — they are tasks where
  the cost asymmetry or the absence of signal makes "always answer X" unbeatable. Compaction is the
  clean case: `keep_p` AUC **0.35–0.65** straddles 0.5, so there was no discriminative signal for
  *anyone* to find, Jev included.

**What A and B share — and this is the real finding:** in neither class does the task require
**discriminating between near-identical candidates**. In A the answer is visible in the surface
tokens; in B there is no answer worth acting on. Five tasks, two mechanisms, zero instances of the
thing a judgment model is actually for.

We ran five tasks that between them never posed a discrimination problem, got the same answer five
times, and generalised it to Jev.

**And the ruling itself says so**, at `RULING-authored-vs-real-20260919.md:99-102`: *"Jev was not
bad on any of them… 96.5% on prompt injection with context is excellent; it ties a classifier
trained on ~14,800 labels while using **zero**. The finding is narrower and more useful: it was
never better than the cheap thing already available **on that surface**."* The scope qualifier was
in the ruling from the start. Every summary since has dropped it.

### 3b. The class we never sampled — where the deterministic baseline is *below chance*

`jev-rerank-bench@cd9a35b`, NevIR negation pairs, **n = 1,383 pairs, 0 failures**, official paired
accuracy metric, random guessing = 25%. Read from `results/nevir.json`:

| model | paired acc | median ms | $/1k questions |
|---|---|---|---|
| **jev-score-batch** | **0.7115** | 275 | **0.035** |
| jev-noul-pair | 0.7086 | 547 | 0.044 |
| jev-noul-batch | 0.6970 | 272 | 0.033 |
| Cohere Rerank 4 Pro | 0.6696 | 828 | 2.50 |
| jev-choice | 0.6587 | 273 | 0.033 |
| ZeroEntropy zerank-2 | 0.6059 | 1031 | 0.009 |
| DeepSeek V4.1 Flash (json) | 0.2169 | 1141 | 0.075 |
| DeepSeek V4.1 Flash (pair) | 0.1728 | 2202 | 0.066 |
| **BM25 — *the regex*** | **0.0224** | 0.002 | **0** |

**BM25 scores 2.24% where Jev scores 71.15%. A 31.8× multiple.** BM25's `same_top_pick_share` is
**0.933** — it returns the same passage for both questions 93% of the time. It cannot see
negation at all, because negation is not lexically decidable: "a drug that treats X" and "a drug
that does *not* treat X" share every content token.

**And the chat models are *below the 25% chance rate*** (0.173, 0.217). This is a task class where
generative LLMs are worse than a coin and Jev is at 71%.

### 3c. Jev significantly beats the commercial SOTA reranker

10,000-sample paired bootstrap, `results/nevir.json` `._bootstrap` (sign is Cohere − Jev, so
negative = Jev wins):

| comparison | diff | CI95 | p |
|---|---|---|---|
| cohere-pro vs **jev-score-batch** | **−0.0419** | [−0.0687, −0.0152] | **0.0022** |
| cohere-pro vs **jev-noul-pair** | **−0.0390** | [−0.0651, −0.0130] | **0.0026** |
| cohere-pro vs **jev-noul-batch** | **−0.0275** | [−0.0542, −0.0007] | **0.0446** |
| cohere-pro vs jev-choice | +0.0108 | [−0.0152, +0.0376] | 0.4386 (tie) |

**Three of four Jev configurations beat Cohere Rerank 4 Pro with p < 0.05, at 1/71st the cost and
3× the speed.** On the general 8-dataset headline (1,617 questions, public qrels) it is a tie —
`results/significance.json` `.overall.ndcg10.best = "jev-score-batch"`, and
`jev-score-batch|cohere-pro diff = +0.0009`, i.e. parity with commercial SOTA at $0.45 vs $2.51
per 1k queries.

### 3d. The conclusion, stated so it cannot be rounded

- **"Jev lost to a regex on our tasks"** — TRUE, five times, and correctly ruled. Keep every kill.
- **"Jev has no application"** — FALSE, and our own ledger already said so. **R69 verbatim:**
  *"This says nothing about Jev in general, and nothing about Jev on corpora unlike ours. It says:
  at this fleet's exposure profile and labelling rate, no Jev seat we tested can be certified
  here."* (`NEGATIVE_EVIDENCE.md:3139-3141`)

**R69 shipped with the correct scope qualifier and every summary written since has dropped it.**
That is the same overclaim mechanism this lane catches daily in smaller places, running in
reverse: an under-claim generalised into a verdict.

---

## 4. The five questions

**1. What IS working?** The refusal machinery — genuinely, and it should be kept. `exposure-check`,
13 gate stages, 77 refutations with retry conditions, a submit gate, a planning process that found
18 defects pre-code. Also working and uncounted: `work/jev-client` (one typed caller, because
every hand-rolled body was wrong at least once).

**2. What is NOT working?** Task selection. Five of six evaluated surfaces posed no
discrimination problem at all (§3a: three lexical, two constant-policy), which pre-determined the
result. And `omp-jev-review` — the one surface our README
marks *"yes — no regex for 'this refactor changed a default'"* — **never scored once**: 3
`diff_command_observed`, 3 `review_error` (HTTP 400), **0 `review_scored`**. A seat we ourselves
called irreplaceable was blocked by our own malformed request body, and then counted in the zero.

**3. What is blocking us?** Not the premise (pane 4's read) and not capability. **A sampling
error.** We drew five tasks from the two classes where a judge must lose, and concluded the judge
loses.

**4. Would implementing all open/in-progress beads close the gap?** **No.** 5 open / 4 ready
beads; the evidence-matrix plan (v8) improves how we *claim*, not what we *ship*. No bead points
at a task class where the deterministic baseline is weak.

**5. What vision goals have ZERO bead coverage?** Four:
- **the sampling error itself** — no bead asks "on what task class do both a literal-token rule
  *and* a constant policy fail?";
- **`jev-rerank-bench`** — 67 MB of third-party evidence in-tree, never cited in `EVAL.md`;
- **the `omp-jev-review` HTTP 400** — a scored seat blocked by a fixable client bug;
- **publication** — stage 5 has no owner.

---

## 5. Phase 2 — the bridge plan

**Bridge in one line: stop generating candidate tasks, and start with the task where the
third-party oracle already exists.**

| # | Gap | Category | Action | Cost |
|---|---|---|---|---|
| B1 | Jev's real application class is unnamed | Vision | Adopt **semantic reranking / retrieval gating** as the target class, on `jev-rerank-bench@cd9a35b` evidence | done in this doc |
| B2 | No external oracle cited | Proof | Reproduce the NevIR + 8-dataset scoring **offline from the committed 67 MB cache, zero API calls**, emit a receipt | ~1 h |
| B3 | `omp-jev-rerank` has 0 live rows | Integration | omp emits no `search_result_observed`; wire the rerank seam to a surface that **does** produce candidate lists | ~4 h |
| B4 | `omp-jev-review` HTTP 400 | Implementation | Route it through `work/jev-client` (the typed caller that exists precisely for this) and get a non-zero `review_scored` | ~1 h |
| B5 | Every kill generalised past its scope | Design | Add a **two-bit admissibility test** to every verdict row, asked *before* measuring — see below | ~1 h |
| B6 | Stage 5 unowned | Vision | The separation in §3 is the publishable result — it is a genuine, checkable, externally-corroborated finding | — |

**B5 is the durable one** — the instrument that would have prevented this entire month. Two bits,
asked before any task is measured:

> **Bit 1 (lexical).** Is the label a function of the literal input tokens? → if yes, a regex is
> the correct answer and a judge loses by construction. *(Caught: harm rule, phishing, tier-length.)*
>
> **Bit 2 (constant).** Does some constant policy — always-keep, always-mid-tier — score well?
> → if yes, no classifier is needed at all. *(Caught: compaction at `keep_p` AUC 0.35–0.65,
> cost routing.)*
>
> **A judge only has a seat when BOTH bits are NO.** Then and only then is a regex win evidence
> about Jev rather than evidence about the task.

Applied to reranking, both bits are NO and the escape routes are closed: BM25 is the strongest
literal-token policy that exists for this task and it scores **0.0224** paired on NevIR / 0.486
nDCG@10 overall; and there is **no constant policy at all** for "which of these 30 passages
answers the query." That is precisely why the seat is live here and dead on our five.

---

## 6. Where I differ from pane 4's `docs/REALITY-CHECK-20260921.md`

Read after deriving the above. We agree on stages 3/4/5 and on the bead answer. We differ on
question 3:

- **Pane 4:** *"Not capability — premise. The mission assumes stage 1 yields survivors. It yielded
  none."*
- **Pane 1 (me):** the premise is fine; **stage 1 was run on the wrong sample.** Survivors exist
  (`README.md:290-296` names four), and a fifth was blocked by an HTTP 400 of our own making.
  "It yielded none" is the dropped-qualifier error from §3d restated.

Pane 4's honest reframe — *"a measurement discipline that reliably kills its own output"* — is
accurate and is an asset. But a discipline that has never sampled outside one task class has not
yet measured the thing it claims to have ruled on.

---

## 7. THE PICK — what I would ship this week

**Application: semantic reranking / retrieval gating, as a Jev rerank stage over candidate sets.**

**Upstream repo@sha that already proves it: `jev-rerank-bench@cd9a35b` (anessbelbati), in-tree.**

Why this one and not the other candidates:

1. **The oracle is external and public.** Labels are BEIR/BRIGHT/NevIR/MIRACL qrels — authored by
   neither us nor the repo owner. Clears the R28 authored-evidence bar outright.
2. **n is large and uncertainty is stated.** 1,617 scored questions + 1,383 NevIR pairs, 10,000-
   sample paired bootstraps, CIs on every cell.
3. **Reproducing it costs $0.** `common.py:4` — *"cache/<model>/<dataset>.<variant>.jsonl so a
   rerun costs nothing and anyone can audit the raw outputs."* 481 cached files, 67 MB, 16 model
   arms including Cohere, ZeroEntropy, DeepSeek, Qwen and BM25.
4. **The deterministic baseline is present and loses by 31.8×.** Every prior kill in this lane
   came from a strong regex. Here the regex scores 2.24%. That inverts the lane's entire result.
5. **It beats the commercial incumbent**, significantly, three ways, at 1/71 the cost — so it is a
   *wedge*, not a me-too. The `COD-H3` kill ("becomes a router competing with RouteLLM head-on
   with no wedge") does not apply.
6. **Prevalence is not the killer here.** Every seat we killed died at 0.016%–3.95% base rates.
   Reranking has **no base rate problem** — every query has a candidate list by construction.
7. **A scaffold already exists** — `work/omp-jev-rerank/`, 7/7 tests. Its only defect is that
   nothing feeds it candidates.

**The one-week shape:** B2 (offline reproduction receipt, $0) → B4 (fix the 400) → B3 (feed the
rerank seam a real candidate list). The obvious candidate source is our own retrieval surface:
`codebase_search`, `grep`/`glob` result sets, and `fh search` all emit ranked candidate lists
today and none of them is reranked.

## 8. Provenance check — I nearly cited a dirty tree, and the check came back clean

Before claiming the reproduction, I ran `git -C jev-rerank-bench status`. **The tree is dirty:**
`results/{nevir,significance,summary}.json`, `results/summary.md`, `results/runs.jsonl` and
`results/calibration_nq.png` are all modified. Every number in §3 had been read out of a
**locally modified file**. Per `AGENTS.md`, *"an undisclosed local edit turns every number
measured against that tree into a fooled certificate."* So I diffed before going further.

**Result: the values are bit-identical to upstream `HEAD`.**

| comparison | HEAD | working tree |
|---|---|---|
| bm25 paired acc | 0.022415039768618944 | 0.022415039768618944 |
| cohere-pro | 0.6695589298626174 | 0.6695589298626174 |
| jev-score-batch | 0.7114967462039046 | 0.7114967462039046 |
| cohere-pro vs jev-score-batch | diff −0.0419, p 0.0022, CI [−0.0687, −0.0152] | identical |
| cohere-pro vs jev-noul-pair | diff −0.0390, p 0.0026, CI [−0.0651, −0.0130] | identical |
| cohere-pro vs jev-noul-batch | diff −0.0275, p 0.0446, CI [−0.0542, −0.0007] | identical |
| cohere-pro vs jev-choice | diff +0.0108, p 0.4386, CI [−0.0152, +0.0376] | identical |

All four bootstraps match on diff, p, **and both CI bounds** — the bootstrap is seeded
(`results/significance.json` `.seed = 0`). The 27,193-line diff is JSON re-serialisation plus a
re-rendered matplotlib PNG (176,454 → 176,447 bytes), not a change in any measured value.

**Who did it, and did it cost money.** `results/runs.jsonl` gained 3 rows dated
`2026-09-18T19:00–19:01Z` — a sibling pane ran a scifact slice three days ago. One row reads
`"calls": 300, "cost_usd": 0.166619` next to `"new_this_run": 0`, which looks like $0.17 of
shared budget. It is not. `run.py:50-60`: `done` (→ `new_this_run`) increments **only inside the
`as_completed(futures)` fetch loop**, whereas `calls` and `cost_usd` sum over `all_rows`, which is
read from `cache.rows` — i.e. the *whole cache*, replayed. **`new_this_run: 0` means zero fetches
and zero fresh spend**; the dollar figure is replayed historical accounting of the cached rows.

**Two things this establishes that §3 could not:**
1. The "$0 to reproduce" claim is **verified, not asserted** — a sibling already replayed a slice
   of this benchmark from cache at zero fresh cost, and the accounting fields prove it.
2. The measured values are **stable across an independent re-run on a different day by a
   different pane**. That is a stronger provenance statement than "read from a committed file".

**Boundary.** I did not myself execute the scorer — I diffed a re-run a sibling had already
performed. A full-corpus (not scifact-slice) offline replay is still unexecuted, and `uv sync`
was not run. `foundation/gates.sh` not run. No live Jev call made by me; no key loaded. The
8-dataset headline is a **tie**, not a win — only negation is a win, and I have not established
that negation-sensitivity occurs at a measurable rate in our own retrieval traffic; that is B3's
job and it may kill the seat.

---

## 9. Prevalence on our own traffic — pricing the top rung before anyone builds

`VERDICT.md:46` makes it law: *"price the top rung before building the middle ones."* Every seat
this lane killed died on prevalence. So I measured the rerank opportunity in **our** traffic
rather than assuming it. Read-only, zero API calls.

**Corpus:** 1,821 session JSONL files, **3,149 MB**, 7 omp profiles + default, **137,949 toolCalls**.

**Opportunity rate:** retrieval = **4,528 / 137,949 = 3.28%** of all tool calls, i.e. **2.49 per
session**. Breakdown: `grep` 3,452 · `glob` 717 · `web_search` 359 · `codebase_search` **2**.

Against the base rates that killed prior seats — foreman supervision **0.016%** (dead), tool_call
error **3.95%** — retrieval at 3.28% is in the live range. And structurally it is not the same
kind of problem: **a reranker fires on every retrieval and reorders; it raises no alarm, so there
is no false-positive cliff.** That is why this seat does not die the way the others did.

**Is there anything to rerank:**

| tool | n | median | p75 | p90 | max | ≥10 lines | ≥30 lines |
|---|---|---|---|---|---|---|---|
| `grep` | 3,452 | 40 | 157 | 373 | 1,452 | 73.6% | **55.6%** |
| `glob` | 723 | 10 | 59 | 197 | 407 | 50.1% | 32.6% |
| `web_search` | 359 | 67 | 112 | 155 | 268 | 86.1% | 64.3% |

**55.6% of greps return ≥30 candidate lines** (~1,919 in this corpus). `jev-rerank-bench`'s
setting is literally **thirty** BM25 candidates cut to 2,000 chars. The shapes match.

**Our baseline is weaker than the benchmark's.** Jev beats BM25 (0.486 nDCG@10) there. `grep`
does not rank at all — results arrive in file-path order, which carries **zero** relevance
signal. The deterministic baseline on our surface is weaker than the one Jev already beats by 20
points, which means B5 bit 1 is NO here too.

### The re-scope — and this is the part that matters

`codebase_search` fires **twice** in 137,949 calls. Our retrieval is **92% lexical** (`grep` +
`glob`), not semantic. The benchmark measures natural-language-query → passage relevance; a grep
query is a **regex**.

- The **opportunity structure** (many candidates, no relevance order) **transfers**, at measured
  prevalence.
- The **NevIR negation win does *not* transfer.** Negation-sensitivity is a property of semantic
  queries; a regex has no negation to miss.

So the seat to build is *"which of these 40 grep hits matters for the current task"* — **not**
*"Jev is better at negation."* NevIR is why the **class** is live; it is not evidence for **our
surface**. Citing it as the latter would be the authored-vs-real pattern a third time.

**NO-CLAIM.** I have shown the *opportunity* exists at measurable prevalence, with large candidate
lists and a null-signal baseline. I have **not** shown that reranking those hits improves any agent
outcome — that is rung 3+ and is unmeasured. This is **demand evidence measured on real traffic we
did not author**, which is more than any of the 17 gauntlet candidates had at rung 1.

**Method boundary.** `toolCall`/`toolResult` paired by `toolCallId` within each session file;
result size in **lines** of result text, which overcounts multi-line single hits and undercounts
truncated results. Files >25 MB skipped; 1,821 of 1,875 scanned. Counts are tool **calls**, not
unique queries. No API call, no key, nothing written outside `notes/`.

---

## 10. A free labelled corpus for our own surface — and my second instrument bug

Pane 4's build landed with the honest open question: *"reranking our greps helps — that outcome is
unmeasured."* Three gauntlet candidates (MU-H1, COD-H1, COD-H4) died of *"corpus absent."* So I
tested whether a corpus already exists for free.

**The idea:** after a `grep` returns 161 lines, the agent's next `read` **is** a relevance
judgment nobody had to author. Candidates = distinct files named in the grep output; relevant =
the file actually read. `read` fires **16,405** times in the corpus.

### The bug, first

| | v1 (broken) | v2 (fixed) |
|---|---|---|
| grep→read pairs | 159 | 660 |
| labelled pairs | **3** | **219** |
| yield | 1.89% | **33.18%** |

v1 assumed grep output is `path:line:text`. omp's real format is `[src/foo.rs#FF28]`, or `# src/`
plus `## foo.rs#FF28`. v2's header-form counter settles it: **`hdr2` = 5,734 extractions**,
`bracket` = 793, **`colon` = 3**. The format v1 was written for occurs **three times in 1,821
sessions**. I nearly reported `n=3` as "no corpus exists" — a false ZERO from a broken
instrument, which is **R68 exactly**, and the second instrument bug I caught in myself today.

The tell was in the v1 output and I should have seen it immediately: `hits_per_grep_median: 319`
beside `candidates_per_grep_median: 4`. Four filenames out of 319 hit lines is not a finding, it
is a parser failing.

### The result

| metric | value |
|---|---|
| labelled pairs | **219** (unauthored, in-domain) |
| **grep top-1 baseline** | **26.48%** |
| grep top-3 | 64.38% |
| chosen rank | median 2, mean 4.05 |
| candidates per grep | median 5, max 20 |
| corpus | 1,821 sessions · 3,452 greps (2,539 ≥10 lines) · 16,405 reads |

**Median candidate count is 5, so blind guessing scores ~20%. grep's file-path ordering scores
26.48% — 6.5 points over random.** The weak-baseline condition the entire pick rests on is now
measured **on our own traffic**, not inferred from BM25's 0.486 on someone else's. Headroom is
73.5 points. And 219 labelled examples is an order of magnitude past the 17 markers that killed
MU-H1 and the 2-of-30 transcripts that killed COD-H1.

### Proxy caveat — stated, not buried

The label is a **proxy**, not ground truth. (1) "read it next" ≠ "it was the relevant hit".
(2) 441 of 660 pairs had the read target *not* among the candidates — those are **unlabelled, not
negatives**; scoring them as negatives would inflate any result. (3) Matching is by **basename**,
so two `mod.rs` collide; unquantified. (4) Only 660 of 2,539 big greps get a read at all, so the
33.18% yield is over the subset that has one. (5) `window = 6` events is a parameter I chose and
did not sweep.

**NO-CLAIM.** This shows a reranker *could* help and gives the bar it must clear. It is **not**
evidence that Jev's reranker *does*. That is still the open question that can kill deployment.

**Suggested preregistered bar** (pane 4's to set or reject): beat **26.48%** top-1 on these 219
pairs by a margin whose 95% interval excludes zero — registered *before* scoring them, or it is
our own artifact again.

---

## 11. LIVE — the review seat, and my own instrument failing three more times

Joshua gave blanket live-call approval. Pane 4 owned rerank and pane 3 the injection flag, so I
took the unowned seat: `omp-jev-review`, which our README marks *"no regex for 'this refactor
changed a default'"* and which had **never scored once** (3 `review_error`, 0 `review_scored`).

**Live:** `jev-1.13.0`, 2 runs × 7 states = **14 requests, 0 failures**, 2026-09-21. Key via
Infisical, never printed.

### Defect 1 — the measurement could only ever say DEGENERATE

`measure.mjs:231` declares the tally with `scores: []`; lines 260-263 pushed `total`, `correct`,
`saids`, `truths` — **never `scores`**. Line 281 then grades an always-empty array, so `asked=0`,
`yes=0`, and measure-kit's `constant = (yes === 0 || yes === asked)` is unconditionally true.
**Every question returned DEGENERATE regardless of Jev's answers.** The first run printed
`19/21 HIT` per-case and "all three DEGENERATE" on the same page.

Fixed (one line). **The verdict reverses on two of three questions:**

| question | broken | fixed |
|---|---|---|
| `behaviour` | 0/7 DEGENERATE | **6/7**, spread 0.77, DISCRIMINATES |
| `boundary` | 0/7 DEGENERATE | **7/7**, spread 0.95, DISCRIMINATES |
| `scope` | 0/7 DEGENERATE | 6/7, spread 0.32, genuinely DEGENERATE |

**Blast radius checked before alarming anyone:** `omp-jev-failure/measure.mjs:177` pushes
correctly; `omp-jev-rerank` does not use `gradeQuestion` at all, so the rerank cut was **not**
made on this bug. Isolated, and caught on first-ever execution.

### Defect 2 — the shipped extension judges a command string

`src/index.ts:84` — `state: { diff: command.slice(0, MAX_DIFF) }`, where `command` is
`git diff HEAD~1`. The extension asks three questions about **sixteen characters of shell**. Their
own `measure.mjs` header says so. This voids every L2+ claim for the extension until the diff body
is passed. Not patched — behaviour change, pane 4 owns the queue.

### Then I applied B5 to my own result, and it killed the headline

`boundary` at 7/7 looked like a seat. `AUTH_DELETED` deletes
`if (!session || !session.roles.includes('admin')) return 403` under the commit message *"fix:
unblock the staging dashboard"* — and contains **no** `auth`/`permission`/`credential`/`token`.
I nearly reported *"Jev caught what a regex cannot."*

**Wrong.** My regex was too narrow. Adding `403`, `forbidden`, `session` — obvious security
tokens — the keyword baseline scores **7/7, exactly tying Jev**, at zero cost and zero latency.
**`boundary` fails bit 1. Lexically decidable. No seat.** I had chosen a weak baseline and almost
credited Jev for beating it — gate self-weakening, inverted.

### `behaviour` is the only survivor, and it is thin

| | score |
|---|---|
| **Jev (live)** | **6/7** |
| best cheap baseline (`any non-comment changed line` / `changes a literal value`) | **5/7** |

**+1 on n=7 authored rows** — the same margin structure as the harm rule, where the regex won by
one. The two make *different* errors: on `big-refactor-tidy` (400 generated renames) every
changed-line baseline says "behaviour changed" and is wrong; **Jev says 0.16 and is right** — a
line-counting rule cannot tell a 400-line rename from a 400-line semantic change. Jev then misses
`dep-bump-lockfile` (0.19, truth true) which the literal-value baseline gets.

**Verdict: `behaviour` = PREPARED-NOT-MEASURED.** It is the one question a rule does not obviously
replace, and +1 on seven same-author rows is not a seat. `boundary` = no seat (lexical).
`scope` = **CUT-authored** with retry on non-author diffs — P2's framing, accepted: closing it on
n=7 same-author rows would be R28 in the cut direction.

**Score for the session: three instrument defects, all mine or in code I ran first** — v1 label
scan off by 73×, the always-DEGENERATE grader, and a lexical baseline I drew too narrow. Each was
caught by checking the instrument against its own output before reporting. That is the only reason
any number in this file is worth reading.

---

## 12. The regime — what a Jev seat actually requires, named at last

My 7 research scouts wedged at 45 minutes and produced nothing, so I ran the breadth census
directly. Of 24 clones only **five** carry committed data: `jev-rerank-bench` (16 files),
**`jev-spam-eval` (19 files, 9 result dirs)**, `jev-benchmark` (3),
`jev-agent-failure-benchmark` (1), `skillranker` (3). The rest are code or catalogues.

`jev-spam-eval@76ef183` is the strongest application evidence in the tree and appears **nowhere in
`EVAL.md`**.

### Zero-shot Jev vs TF-IDF trained on the target's own labels

| in-distribution | Jev (0 labels) | TF-IDF |
|---|---|---|
| email-dataset | 98.3% | 98.4% (14,800 labels) |
| Ling-Spam | 98.6% | **99.4%** (2,300 labels) |
| 3-class + phishing | 94.2% | **98.7%** (4,600 labels) |

| out-of-distribution | Jev | TF-IDF | gap |
|---|---|---|---|
| Ling-Spam, 2000 | **98.6%** | 73.0% | **+25.6** |
| phishing, 2024–25 | **91.0–93.6%** | 70.3% | **+21–23** |
| modern mail, 2026 | **97.3%** | 72.5% | **+24.8** |

Four questions over 19,528 emails cost **$1.12**. (`OUT_OF_DISTRIBUTION.md:16-18`, per-prediction
JSONL under `results/`.)

### The cleanest statement of the regime, on one dataset

Verifying pane 2's edge at `OUT_OF_DISTRIBUTION.md:28-41` — it is sharper than they put it. On
**Ling-Spam**, the identical method:

| | accuracy |
|---|---|
| TF-IDF trained on Ling-Spam's **own** labels | **0.9857** |
| **Jev, plain question, zero labels** | **0.9857** |
| TF-IDF trained on email-dataset (wrong distribution) | 0.7298 |

**An exact tie when the baseline has right-distribution labels; +25.6 points when it does not.**
The failure mode is legible: TF-IDF flagged **745 of 2,408** legitimate posts (31%) as spam,
because academic list mail looks nothing like the business mail it learned "legitimate" from.

### Applying B5, the regime falls out

- **Bit 1, in-distribution:** TF-IDF *is* the lexical baseline — word frequency — at 98.4%.
  **YES → no seat.**
- **Bit 1, out-of-distribution:** the same lexical baseline collapses to 70–73%. **NO → seat.**

**The seat is not "spam." It is distribution shift and cold start** — any task where labels
resembling what you will actually see cannot be obtained. New abuse campaigns, novel phishing,
emerging failure modes, day-one classification. **None of our five surfaces were in that regime.**

### Pane 2's counter-edge, verified and it holds

The detailed-criteria question scored **0.9701** against the plain question's **0.9857** on this
OOD set (`:32-33`) — yet detailed criteria was the *winner* in-distribution (98.3% vs 96.0%).
**Question tuning overfits the distribution it was tuned on and moves points both ways.** OOD
stability therefore reads as a *model* property, not a question property. That strengthens the
regime claim rather than weakening it.

### What this does to our own verdict

It **reframes, it does not overturn.** All five of our tasks had a stable distribution and a
writable rule; the cheap thing won and shipping it was right. And we already wrote this finding
ourselves at `RULING-authored-vs-real-20260919.md:99-102` — *"it ties a classifier trained on
~14,800 labels while using **zero**"* — the same zero-shot-parity result, filed as a loss because
our distribution never shifted.

**We measured the one regime where a judge cannot win, five times, and generalised from it.**
That is the answer to "how can we not find one application."

**Boundary.** I re-ran nothing here; every number is read from committed files. The repo states
its own limit: *"exploratory experiments, not benchmarks,"* run once, one model version
(`jev-1.13.0`). OOD sets are small — 2,876 / 853 / 633. The 98.3% used a question written *after*
reading mistakes in 1,000 sampled emails. Pane 4 notes the 97.3/72.5 pair in the modern-mail row
is the accuracy column, not the "legitimate called legitimate" column — my summary used accuracy,
which holds. `EVAL.md` citation is pane 4's to make; I have not touched that file.

### Provenance — the clone is dirty, and one dirty file moves a published number

Pane 4 flagged two modified files before citing anything. Checked: `results/ood_modern.jsonl` and
`results/ood_tfidf_predictions.jsonl`, both OOD. Row counts identical (633 / 4362) but 619 and 566
rows differ in content at the same index — a re-run or re-sample, not a reformat. **Docs are clean
against `HEAD`**, so every number quoted above came from clean bytes.

Scoring `ood_modern.jsonl` both ways (`label` vs `choices.choice`, ham/legitimate collapsed):

| question | HEAD | working tree |
|---|---|---|
| `category` | 614/633 = 97.00% | 97.00% |
| `category_names_only` | 624/633 = 98.58% | 98.58% |
| **`category_urgency_authority`** | **616/633 = 97.31%** | **612/633 = 96.68%** |

The README headline *"97.3% (with urgency and authority)"* is the **HEAD** value. **Anyone
replaying this working tree gets 96.68% and would conclude the repo overclaimed — it did not, our
checkout drifted.** Cite `jev-spam-eval@76ef183` **at HEAD**, and disclose that the modern-mail
per-prediction file is locally modified; otherwise the next agent files a false overclaim against
an upstream repo, which this lane already did once this week.

Conclusion unchanged: 96.68% vs TF-IDF 72.5% is still **+24.2**, and Ling-Spam (98.6/73.0) and
phishing (91.0–93.6/70.3) are untouched by the drift. I did not clean, stash, or check out
anything in that clone — **the drift is disclosed, not repaired.**
