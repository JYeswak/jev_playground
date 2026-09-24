<!-- Research report by GuidanceScan (task agent spawned by pane 1 AmberWillow, bead jev-jy7t.1), 2026-09-24. Read-only web research; no model API called. Citations are the agent's; pane 1 has not re-checked them. -->

No page has changed since the mirror. All 113 live URLs are byte-identical to `docs-mirror/typesafe/`: the 111 pages in `llms.txt`, plus `sitemap.xml` and `llms-full.txt`. The mirror copy is dated 2026-09-24 16:22 -0600. I made no edits and no model calls; scratch files are only under `/tmp/guidance-scan/`.

## 1. TypeSafe docs: live vs mirror (checked 2026-09-24)

| Check | Result |
|---|---|
| `https://docs.typesafe.ai/llms.txt` | Same SHA-1 as the mirror (`942e6afa...`), 16,019 bytes |
| Pages added or removed | **None.** The sitemap lists 111 pages; every one is in `llms.txt` and in the mirror |
| Pages changed | **None**, all 113 files identical |
| Newest sitemap `lastmod` | `/legal` at 2026-09-24T16:15Z; its content matches the mirror |
| Jaggedness successor | None. `/model-jaggedness.md` returns 307 to `jev-1.13.md`; `jev-1.14.md` and `jev-1.13.1.md` return 404. The page says "Last reviewed 2026-09-17" |
| Blog (typesafe.ai sitemap) | 4 posts: launch (Sep 15, 2026), "Lies, Damned Lies, and Benchmarks" (`/blog/antibenchmaxxing`, Sep 11), "The Bitterest Lesson" (Sep 10), "AI: too good to be true..." (Jun 19; its body came back empty) |
| evals.typesafe.ai | Reachable; read below |

## 2. Official guidance for Jev in a control loop or UI agent

**Latency and throughput**
- Most queries take about 100 ms and are "fast enough for real-time request paths and user interfaces" ([how-to-build](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)).
- The use-case map says 150 ms, "fast... enough to be programmed to play games or embedded into a UI" ([use-case-map](https://docs.typesafe.ai/concepts/use-case-map.md)).
- The launch post gives 70-500 ms end to end, adding that "our published evals are generally run from our laptops on the West Coast" ([launch, Sep 2026](https://typesafe.ai/blog/introducing-system-one-models-and-jev)).
- The self-consistency cookbooks measured 111-114 ms mean round trip on sequential calls ([consistency_choice](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md)).
- The Doom demo runs about 10 queries/s for about $7/hour; its state is structured text, not images. The post admits "a non-AI doom bot could play better" (launch post).

**Rate limits** ([models](https://docs.typesafe.ai/models.md))
- 250,000 tokens/s and 1,200 requests/minute; either limit returns HTTP 429.
- The page warns that limits "are adjusting dynamically... can change without notice."
- [INFERENCE] 1,200/min is 20 requests/s. The ledger measured about 78-85 calls/s at concurrency 16 with no failures. Don't assume either figure; log every 429.

**SDK defaults can stall a loop**
- Timeout is 10 s per attempt, with 2 retries by default (JS [TypeSafeClientConfig](https://docs.typesafe.ai/sdk/javascript/api/interfaces/TypeSafeClientConfig.md) and [RetryPolicy](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RetryPolicy.md); Python [constants](https://docs.typesafe.ai/sdk/python/api/constants.md) and [retries](https://docs.typesafe.ai/sdk/python/api/retries.md)).
- The JS SDK honours `Retry-After` for up to 60,000 ms.
- 429 and 529 should be retried with backoff ([api](https://docs.typesafe.ai/api.md)).

**Batch questions into one request.** Questions over one state run in parallel, so extra questions "usually have little effect on response time" ([fan-out](https://docs.typesafe.ai/patterns/fan-out.md)). The GDPR cookbook measured one batched call as 12.2x cheaper and 10.0x faster than one call per question ([parallel_questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md)).

**State design** ([state](https://docs.typesafe.ai/concepts/state.md), [models](https://docs.typesafe.ai/models.md), how-to-build)
- Input is text only; screens and games must be serialized to text first.
- Context is 64k tokens per request, and 32k for the state plus the single longest question.
- Use JSON objects with named fields. Point questions at a value with a backticked path such as `a.b[0]`.
- Send only the context the question needs, because irrelevant material causes "context rot."

**Large option sets**
- A Choice takes at most 255 options, and each option costs only a few tokens ([choice](https://docs.typesafe.ai/primitives/choice.md)).
- Add an "other" or "none of the above" option.
- Past 255 options, use two stages, or a beam search over Choice probabilities ([hierarchical](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md)). Wikiracing used "scoring independently then making an explicit choice" (launch post).

**Confidence** ([confidence](https://docs.typesafe.ai/confidence.md), [confidence-routing](https://docs.typesafe.ai/patterns/confidence-routing.md))
- Confidence is computed from the probability spread; Noul answers have none.
- Thresholds should scale with the risk of the action.
- "Start with conservative thresholds, test with your own data."
- "Test thresholds by plotting confidence against accuracy on your data" (how-to-build).
- Calibration "does not guarantee that an individual answer is correct" ([system-one](https://docs.typesafe.ai/concepts/system-one.md)).

**Versioning** ([models](https://docs.typesafe.ai/models.md)). `jev-latest` can move. "If you have tuned confidence thresholds... pin that version's ID", and log the `model` field of each response.

**Known weaknesses of jev-1.13** ([jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md))

| # | Weakness | What it means for a game or UI agent |
|---|---|---|
| 1 | Literal reading | It answers the question as written, not as meant |
| 2 | Maths, counting, numbers | Can't judge whether RGB/hex values are near each other; don't interpolate between Score levels |
| 3 | Date and time comparison | Extract the parts, compare in code |
| 4 | Indirection | Reduce hops in the question |
| 5 | Large state full of irrelevant detail | Accuracy drops as unrelated content grows |
| 6 | Adversarial content | Text in the state "can move the answer" |
| 7 | Instructions contradicting criteria | Keep them aligned |
| 8 | Structural invariants | A Noul refund=0.72 plus not_refund=0.47 sums to 1.19; "Don't carry a threshold tuned on a Noul over to a Choice" |
| 9 | Generation | It doesn't write text |

[INFERENCE] Weakness 2 covers pixel coordinates. Convert them to named regions in code.

**How TypeSafe itself treats evals**
- It publishes no standard benchmark table.
- Its evals are "dated snapshots and immediately retired", and it commits to publishing caveats, cherry-picking and bad evidence ([antibenchmaxxing, Sep 11, 2026](https://typesafe.ai/blog/antibenchmaxxing)).
- The launch FAQ says: "Put no weight on public benchmarks... Disclose the nuance... De-emphasizing benchmarks even when you're ahead."
- [evals.typesafe.ai](https://evals.typesafe.ai/) scores against the average of GPT-6 Astra and Fable 5.1 at high thinking. That is agreement with a frontier-model consensus, not ground truth, and the launch post says so.

## 3. Checklist for honest agent-benchmark claims (2025-2026)

- **Run a trivial-agent floor.** On tau-bench, an agent that returns nothing passes 38% of tasks and beats a GPT-4o agent. ABC lists 13 reporting checks (R.1-13), including statistical significance and baseline comparisons ([ABC, Zhu et al., Jul 2025](https://arxiv.org/abs/2507.02825)). Berkeley RDI recommends null, random, prompt-injection and state-tampering agents ([Apr 2026](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/)).
- **Keep answers away from the agent.**
  - OSWorld reached 73% by downloading gold files from public HuggingFace URLs; WebArena reached about 100% via a `file://` read of its task configs (Berkeley RDI).
  - SWE-bench agents used `git log --all` to see future fixes ([SWE-bench #465, Sep 2025](https://github.com/SWE-bench/SWE-bench/issues/465)).
- **Audit the evaluator.**
  - 15.3% of FAIL verdicts on computer-use benchmarks were wrong: 10.7% evaluator false negatives and 4.7% broken tasks ([Dong et al., Jul 2026](https://arxiv.org/abs/2607.28367)).
  - About 10% of OSWorld tasks have serious errors ([Epoch, Oct 2025](https://epoch.ai/blog/what-does-osworld-tell-us-about-ais-ability-to-use-computers)).
  - WebArena's string matching overestimates agents by 5.2% (ABC).
- **Compare the same benchmark version and task set.**
  - About 10% of OSWorld instructions changed after Verified, and 8 Google Drive tasks are usually excluded (Epoch).
  - OSWorld-Verified fixed 300+ issues and asks users to compare against verified results ([XLANG, Jul 28, 2025](https://xlang.ai/blog/osworld-verified)).
  - OSWorld 2.0 was released on 2026-06-26 ([os-world.github.io](https://os-world.github.io/)).
- **Compare the same observation type and step budget.** OSWorld-Verified results are split into Screenshot, A11y tree, Screenshot + A11y tree and Set-of-Mark, grouped by max steps, and kept apart from self-reported results (os-world.github.io).
- **Compare the same timing regime.** Real-time and paused play differ: 0.48% on VideoGameBench vs 1.6% on its paused Lite version ([Zhang et al., May 2025](https://arxiv.org/abs/2505.18134)).
- **Hold the harness constant or report it.** lmgame-Bench finds that dropping LLMs straight into games is unreliable because of perception, prompt sensitivity and contamination ([May 2025](https://arxiv.org/abs/2505.15146)). HAL finds scaffolds "dramatically impact both accuracy and cost" ([Kapoor et al., Oct 2025](https://arxiv.org/abs/2510.11977)).
- **Report variance across runs.**
  - pass^k: GPT-4o's pass^8 is below 25% on tau-bench retail ([Yao et al., 2024, foundational](https://arxiv.org/abs/2406.12045)).
  - The intraclass correlation (ICC) settles after 8-16 trials on structured tasks and 32 or more on complex reasoning ([Mustahsan et al., Dec 2025](https://arxiv.org/abs/2512.06710)).
- **Report cost and latency alongside accuracy.**
  - Joint accuracy/cost optimization and proper holdout sets ([AI Agents That Matter, Jul 2024, foundational](https://arxiv.org/abs/2407.01502)).
  - HAL logs cost per task.
  - The best OSWorld agents take 1.4-2.7x more steps than necessary, and latency runs to tens of minutes ([OSWorld-Human](https://arxiv.org/abs/2506.16042)).
- **Disclose every variant tried.** Meta tested 27 private variants before the Llama-4 release ([Leaderboard Illusion, Apr 2025](https://arxiv.org/abs/2504.20879)).
- **Check whether tasks need the claimed capability.** About 15% of OSWorld tasks need only a terminal, and another 30% can swap scripts for most of the GUI work (Epoch).
- **Count crashes as zeros, and don't grade with an LLM judge.** Judges can be prompt-injected (Berkeley RDI).

## 4. Acting on classifier probabilities

- **Calibrate on the deployment regime.**
  - Rankings of uncertainty methods hold across datasets for a fixed model, but not across model classes or interfaces ([Argus, Jun 2026](https://arxiv.org/abs/2606.25760)).
  - The ledger saw a threshold move from 0.67 to 0.37 across sets, and the dice result shows calibration fails on pure chance.
- **Use conformal sets to decide when to ask.**
  - Ask for help when the conformal prediction set is not a single option ([KnowNo, 2023, foundational](https://arxiv.org/abs/2307.01928)).
  - SafeGround sets GUI-grounding thresholds with a guaranteed false-discovery-rate bound ([Feb 2026](https://arxiv.org/abs/2602.02419)).
- **Closed-loop data is not exchangeable, which standard conformal methods assume.**
  - Adaptive conformal inference updates coverage online; delayed outcomes weaken the bound ([Sep 2026](https://arxiv.org/abs/2609.07251)).
  - Alternatively, freeze the policy and certify it on independent episodes. That work reports recall within one standard deviation of target in all 24 configurations ([Doomed from the Start, Jul 2026](https://arxiv.org/abs/2607.06503)).
- **Context shifts break the guarantee.** Coverage fell from 90% to 74% under unanimous wrong peers ([Conformity Breaks CP, Sep 2026](https://arxiv.org/abs/2609.04445)). On-screen text is the analogous risk (jaggedness #6).
- **Don't trust agent self-report.**
  - 64 of 71 failures (90%) ended with a success claim ([CURA, Aug 2026](https://arxiv.org/abs/2608.27808)).
  - Its certified CUSUM alarm (a running-sum change detector) caught 42.3% of failures at a 0.066 false-alarm rate.
  - Retrospectively, its margin over a token-count baseline was not significant, so run trivial baselines here too.
- **Uncertainty must be modelled over multiple turns.** Agent uncertainty evolves over the interaction, and underspecified tasks need follow-up questions ([Oh et al., Feb 2026](https://arxiv.org/abs/2602.05073); [Kirchhof et al., May 2025](https://arxiv.org/abs/2505.22655)).

## Rules for jev-jy7t.1

1. **Pin and log the model.** Call `jev-1.13.0`, log the `model` field of every response, and freeze all questions before the scored run ([models](https://docs.typesafe.ai/models.md)).
2. **Pre-register the comparison.** Fix the benchmark and version, task list, metric, step budget, observation type and timing regime (real-time or paused). Compare only against a published number in the same setting (os-world.github.io; Epoch Oct 2025; VideoGameBench May 2025).
3. **Compare text-state agents only with text-state agents.** Jev reads text only, so compare against A11y-tree or text-state results. Label any comparison with screenshot agents as a different category ([models](https://docs.typesafe.ai/models.md); OSWorld-Verified columns).
4. **Run four floors in the same harness:** a do-nothing agent, a random agent, an always-the-most-common-action agent, and a scripted bot with no model. A claim fails if Jev doesn't clearly beat all four (ABC Jul 2025; Berkeley RDI Apr 2026; launch post, Doom).
5. **Audit for leaks.** The state builder must never read gold files, evaluator configs, task metadata, git history, or online copies. Log every file and URL touched (Berkeley RDI; SWE-bench #465).
6. **Handle numbers and filtering in code.** Coordinates, colours, counts, dates and randomness are resolved in code. Filter the state, stay under the 32k limit for state plus longest question, and log tokens per call (jaggedness #2, #3, #5; dice result).
7. **Budget latency explicitly.** Measure p50 and p95 from this Mac at the loop's concurrency. Set retries to 0 with a deadline and a fallback action. Count timeouts, 429s and 529s as failed steps, never as dropped tasks ([SDK defaults](https://docs.typesafe.ai/sdk/javascript/api/interfaces/RetryPolicy.md); [api](https://docs.typesafe.ai/api.md); Berkeley RDI).
8. **Run repeated episodes.** Report 95% confidence intervals and pass^k or ICC. Use the same seeds for Jev and baselines, and at least as many runs as the SOTA claim you're comparing against (tau-bench; ICC Dec 2025; ABC R.10).
9. **Report cost and time with success.** Give dollars, tokens, wall-clock time and steps per episode. Claim a win only on the pre-registered metric; otherwise call it a Pareto point (HAL Oct 2025; AI Agents That Matter; OSWorld-Human).
10. **Keep a held-out split and disclose everything.** Tune on a dev split, report on an untouched test split, and list every question wording and threshold tried (AI Agents That Matter; Leaderboard Illusion; [antibenchmaxxing](https://typesafe.ai/blog/antibenchmaxxing)).
11. **Calibrate thresholds per question.** Use held-out episodes from the same regime and plot confidence against accuracy. Never reuse a Noul threshold for a Choice. Claim a guarantee only with conformal sets whose exchangeability or adaptive-update assumption is stated ([confidence](https://docs.typesafe.ai/confidence.md); jaggedness #8; KnowNo; ACI Sep 2026; Argus Jun 2026).
12. **Audit the grader.** Hand-check a random sample of PASS and FAIL verdicts and report the estimated grader error. Use programmatic checkers only, no LLM judge (Dong et al. Jul 2026; Epoch; Berkeley RDI).
13. **Stress-test with injected text.** Put adversarial text in the screen or game state and report the change in score and coverage (jaggedness #6; Conformity Breaks CP Sep 2026).
14. **Don't let Jev grade itself.** Success comes from the environment's checker. Self-report or Jev "done" answers need their own verified evaluation (CURA Aug 2026).
15. **Publish as a dated snapshot.** Include caveats and every losing result ([antibenchmaxxing](https://typesafe.ai/blog/antibenchmaxxing); ABC R.7-R.9).
