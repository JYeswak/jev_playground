# Application plan — 2026-09-21

Revises `docs/REALITY-CHECK-20260921.md` in place of its conclusion. That document's
numbers stand. Its inference does not.

## Phase 1 — where we actually are

Stage 1 did not find that Jev has no application. It found that five seats we tested
are the wrong class of task. Pane 1's correction, checked against
`docs/demos/upstream-repro/RULING-authored-vs-real-20260919.md`:

| class | seats | what won | what it says |
|---|---|---|---|
| A lexical | tool-call harm, phishing, router tier | a regex / a length | the label is in the tokens; a regex is the answer, not a baseline |
| B constant | cost routing, compaction | flat mid-tier; keep-everything | no discriminative signal, for Jev or anyone |
| C discriminate | **not sampled** | — | the only class a judgment model is for |

R69 already said this and the summaries dropped it (`NEGATIVE_EVIDENCE.md` NO-CLAIM:
"says nothing about Jev in general"). The ruling at that receipt said the same thing
on day one: Jev was not bad; it was never better than the cheap thing already on
*that surface*. Two documents, one overclaim in the summaries. That is the defect.

**Two-bit admissibility, asked before measuring:**

1. Is the label a function of the literal input tokens?
2. Does a constant policy (always-keep, always-mid-tier) score well?

A judge has a seat only when both are NO.

## Phase 2 — the application that passes both bits

**Semantic rerank.** Proof already in the tree, read from `git show HEAD` of
`jev-rerank-bench` @ `cd9a35b`, not from the dirty working tree (pane 1: values
bit-identical, JSON re-serialised, zero fresh spend on the sibling replay).

NevIR negation, n=1383, 0 failures (`results/nevir.json` at HEAD):

| arm | paired accuracy | ms | $/1k |
|---|---:|---:|---:|
| jev-score-batch | 0.7115 | 275 | 0.035 |
| jev-noul-pair | 0.7086 | 547 | 0.044 |
| cohere-pro | 0.6696 | 828 | 2.50 |
| bm25 | 0.0224 | ~0 | 0 |

Bit 1 is NO: BM25 is the literal-token policy and it scores 0.0224. Bit 2 is NO:
there is no constant policy for "which of these passages answers the query."

8-dataset headline is a **tie** (+0.0009 vs Cohere). Do not sell the tie as a win.
The win is negation. Evidence level of the table: **[oracle]** committed JSON at
HEAD `cd9a35b`, read via `git show`, not the dirty working tree. Date of the
upstream run is in that file; this lane did not re-execute the scorer.

### What shipped this pass

| piece | command | claim level |
|---|---|---|
| score-batch policy | `node --experimental-strip-types --test work/nev-rerank/test/rank.test.mjs` | **[test]** 7/7. Lexical order picks the trap; scores pick the answer; a failed asker does not invent a ranking. |
| HEAD replay | `node --experimental-strip-types work/nev-rerank/rank.mjs` | **[oracle]** prints HEAD NevIR cells and the fixture contrast. Exit 0. |
| live smoke | `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/nev-rerank/live-once.mjs` | **[live] N=1, 2026-09-21, model `jev-1.13.0`, 1 request / 2 scores.** Lexical picked TRAP. Jev ordered ANSWER 0.953 over TRAP 0.510. Direction only. |
| omp tool | `.omp/tools/jev-rerank.ts` | written. No key returns input order + `NOT_RUN`. **L2/L3 not proven** — discovery not exercised. |
| citation fold | `work/citation-check` tests | **[test]** 6/6. Official cookbook policy, offline. Not the headline. |

The existing `work/omp-jev-rerank` hook still only logs grep hits and reorders nothing.
That is not this tool.

### What this does not claim

- That n=1 replicates n=1383. It does not. The trap scored 0.510, not ~0. Order was right on one planted pair.
- That negation occurs at a useful rate in *our* retrieval traffic. Unmeasured. That can still kill deployment.
- That the 8-dataset tie is a win.
- That the omp tool has fired in a session.
- That citation-check is live-verified.
- That "four of six surfaces call Jev" means four certified seats. README column is `calls Jev?`. Pane 1 retracted the wider paraphrase. Defensible line: a Jev call survived the measurement filter on four of six surfaces. `omp-jev-review` never scored live (HTTP 400, 0 `review_scored`).

Pane 1 measured retrieval demand on our logs (this pane did not re-run that census). Reported: 4,528 / 137,949 tool calls are retrieval (3.28%), grep median 40 lines, 55.6% of greps at least 30 lines, `codebase_search` fired twice. **Re-scope:** the opportunity transfers. The NevIR negation win does not — a regex has no negation to miss. Cite NevIR as class evidence only.

### Preregistered bar — grep top-1 on our traffic

Receipt `notes/rerank-label-scan.json`, generated 2026-09-21T18:51:58Z, `parser_version` 2. Measured by pane 1. This pane read the file and did not re-execute the scan. Evidence level: **[oracle]** over session logs, zero API calls. The label is a proxy.

v1 of that scan reported 3 labelled pairs and was an instrument bug: it assumed `path:line:text`. omp's grep format is a header (`hdr2` = 5,734 extractions; bracket = 793; colon = 3). v2 is the number below.

| quantity | value |
|---|---:|
| grep-then-read pairs | 660 |
| labelled pairs | 219 |
| label yield | 33.18% |
| grep file-path top-1 | **26.48%** |
| grep top-3 | 64.38% |
| chosen rank | median 2, mean 4.05 |
| candidates per labelled grep | median 5, max 20 |

**Live result, after the bar, on a re-extracted corpus that reconciled.** `work/nev-rerank/pairs.jsonl` matched v2: 219 labelled, grep top-1 26.48% (58/219), header forms 793/5734/3. Query field was `intent` on all 219, not the regex. 219 requests, 0 failures, model `jev-1.13.0`, 2026-09-21. Receipt `work/nev-rerank/live-receipt.json`.

| set | n | Jev top-1 | grep top-1 | paired diff | 95% bootstrap CI | excludes 0 |
|---|---:|---:|---:|---:|---|---|
| all rows | 219 | 35.62% | 26.48% | +9.13 pp | [0.46, 17.81] pp | yes, barely |
| snippet present | 155 | 36.13% | 20.00% | +16.13 pp | [5.81, 26.45] pp | yes |
| filename only | 64 | 34.38% | 42.19% | -7.81 pp | [-25.0, 9.38] pp | no |

Random floor on the actual per-row candidate counts is 24.79%, not 1/median. Grep order is +1.69 pp over that floor. Exact McNemar on the 100 discordant pairs (Jev-only 60, grep-only 40) is two-sided p=0.057. The preregistered interval bar is met by a hair. The conventional exact test is not. Both stand.

Challenges accepted, 2026-09-21. The snippet split was looked at after the calls. It is not a second seat and it gets no family correction because it was not a preregistered family. It is also not nothing: pooling 35.62 against 26.48 averages a win on passage text with a loss on filenames. Report the split as an observation that needs a fresh sample, not as the result and not as silence. The label is the next file read, not relevance. Cost of the 219 was not recorded. An 8-call sample on the same path, not a rescore: median 137 ms (115–313), 8,954 input tokens, $0.000376 at $0.042/MTok, $0.047 per 1,000 requests. That sample does not price the 219.

## Ambition — what makes this more than a fixture

The fixture proves the policy. The application is the tool returning an order a caller acts on. Next measurements, in order, each able to kill the seat:

1. Live smoke on the planted negation. **Done, N=1, direction only.** See the table.
2. Replay the committed NevIR cache through `expectedLevel` and confirm our reduction matches `jev.py` on a recorded answer, not just a synthetic distribution. (Done for the synthetic; not yet on a cached response body.)
3. Grep's own top-1 on our traffic. **Scored.** Jev 35.62% vs grep 26.48% on 219, interval excludes 0 by 0.46 pp, McNemar p=0.057. Not a certified seat.
4. A `tool_result` path that offers the order. Not started. Not a silent reorder.

Review boundary seat, retracted by pane 1 and re-run here: `python3 notes/boundary-lexical-baseline.py` exits 0. Keyword regex 7/7, Jev 7/7, on the same diff bytes. Bit 1 fails. No seat. Behaviour remains their PREPARED-NOT-MEASURED, n=7 same-author, not adopted as a build.

Citation check stays the second build. It passes bit 1 as NO for the entailment step
(the quote is present; the claim can still be false) and bit 2 as NO (always-verified
is the failure the cookbook plants). It does not have a public n=1383. Rerank does.

## Bead coverage

`jev-k9z` and children already exist (pane 2, before the split). This plan does not
open a sixth advisory logger. It points `jev-k9z.1` at `work/nev-rerank` and adds the
two-bit admissibility check as a gate on the next candidate, not as another ruling.
