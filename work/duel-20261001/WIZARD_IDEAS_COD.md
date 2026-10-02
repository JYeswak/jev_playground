# Five improvements worth making to Jev on this machine

**Independent Codex proposal — October 1, 2026.** Thirty candidates considered; five selected below, in priority order. This is a design recommendation, not an implementation or a new result. No provider/model calls were made for this exercise. Daily costs are planning arithmetic at the repository rate of **$0.042 per million input tokens**, not newly measured invoices.

## Recommendation in one sentence

**Make the judgments that already earn their seats fast, correctly applied, bounded across the fleet, and actually retired when withdrawn; then make the existing needs-human page more actionable.** Do not add another general-purpose supervisor, router, skill recommender, or dashboard.

| Rank | Improvement | What Joshua actually notices |
|---|---|---|
| 1 | Fast, occurrence-scoped memory filtering | Useful recall, fewer input tokens, less waiting before work starts, no accidental removal of instructions. |
| 2 | One composable web-result screening path | Predictable withholding, preserved useful results, and less serial screening latency. |
| 3 | Fleet-persistent judgment budgets and refusal holds | Starting another pane does not reset a cap or restart an outage storm. |
| 4 | Effective retirement and version-bound activation | A disabled policy stops interrupting work; configured does not masquerade as running. |
| 5 | Evidence-addressed needs-human pages | The actual decision needed, rather than the first 140 characters of a status preamble. |

### Evidence boundaries

I read the full `AGENTS.md` and `README.md`, `work/jev-inventory/expected.json`, the negative-evidence headings and relevant full entries, the `EVAL.md` tail, and the hooks/extensions/tools under `.omp/`, including memory filtering and kit-guard. I also inspected the shared client, global screen wrappers, dispatch/router/foreman implementations, and the existing needs-human watcher/helper.

- The inventory records memory-filter **ENFORCING**, despite older README/how-text still saying shadow or join-void. Its measured removal is **median 797 / p90 3,408 tokens over 14 turns**, with held-out relevance results **0.978 and 0.985**. That is not fleet-wide dollar savings.
- Global web/injection wrappers are **SHADOW**, not fleet-wide withholding. Project seats enforce. The coding-seat injection result is **0/222 clean false flags and 268/300 planted catches**; the inventory records **zero modern webscreen withholds in 363 real results**. Those are separate cohorts, not a combined precision estimate.
- The gate cascade achieved **94/98 local clears**, establishing paid-call reduction, not useful danger detection. Organic gate cohorts supplied no harmful positives. Historical local timeout pressure matters, but the current source already contains paid fallback: do not propose the missing fallback as a new fix.
- Native find and auto-thinking are already ON. Find measured **404 versus 1,861 tool tokens per successful location** in the controlled comparison; auto-thinking measured **16% lower hard-task cost**. Preserve these paths rather than layering another router over them.
- Needs-human detection passed its small positive/negative check, but has **not** demonstrated faster recovery: the inventory reports **6.9 minutes for paged cases versus 5.4 minutes median unpaged**. That observational comparison is not a causal estimate.
- A read-only October 1 memory-log snapshot contained 751 `scored`, 1,302 `memo`, and 5,080 `daily-cap` rows among 7,149 rows. These are mixed operational/probe records, not 7,149 paid calls or an organic savings denominator. They justify examining coverage/accounting, not projecting a cache hit rate. The web log also contained explicitly fake-offline rows; exclude them from organic benefit claims.

All acceptance bars below are **proposed future bars**, to freeze before outcome labeling. Nothing here claims they already pass. Modify existing paths, not five new services or management systems. No paid comparator is required.

---

## 1. Make memory filtering fast and occurrence-scoped

### Why this is first

The semantic decision already passed held-out checks and actually removes context. The remaining opportunities lie on a blocking path and in applying the verdict, not in inventing a better relevance model.

In `.omp/extensions/jev-memory-filter.ts`, `makeBeforeAgentStartHandler` awaits each item serially. Up to 20 items can be judged; the turn budget is 45 seconds and individual calls can wait 15 seconds. The October 1 metadata snapshot had per-scored-item p50 **137 ms**, p95 **230 ms**. Twenty times 137 ms is approximately **2.74 seconds of serial service time**—an illustration, not a measured turn p50. One fast Jev call does not make a whole filter turn fast.

There is also a source-level application hazard. Parsing recognizes memory blocks, but `pruneSystemPrompt` removes matching cleaned lines across **all** system-prompt elements. If a recalled bullet duplicates an instruction outside its memory block, a drop can remove both occurrences. I have not observed that collision live; the implementation permits it. Relevance confidence must never authorize rewriting unrelated instructions.

### Decision, seam, and implementation

**Jev decision:** keep the existing Noul question—“Is this memory relevant to the current request?”—and its frozen cut. Do not retune the question, substitute nimble, or extend pruning into conversation history.

**Seam:** the existing `before_agent_start` extension: `parseSystemMemories`, `makeBeforeAgentStartHandler`, and `pruneSystemPrompt`.

1. Carry the source element, exact span, and original-byte hash alongside each memory. Deduplicate the judgment if identical memories recur, but retain every eligible occurrence address. Apply drops only to validated recall spans. Changed source or ambiguous shape means keep.
2. Replace the serial loop with at most **four independent in-flight requests**, preserving the current per-item state/question shape. Initially target a **1.5-second total deadline**. Cancel where supported; otherwise ignore late answers and account for any charge. Unresolved means keep, never irrelevant.
3. Preserve the existing per-instance memo. It already exists; “add caching” is not a discovery. A memo hit must not add historical `inputTokens` to today’s bill. Distinguish newly billed tokens, potential removable bytes, and actual removed bytes.
4. Preserve the context prefix, order, and bytes of kept material. Do not reorder system-prompt elements for concurrency. Combining every memory into one question batch would change the model input and needs a separate quality experiment.

The healthy experience is **silent and faster**. Do not inject a paragraph announcing token savings into the context being reduced. Unknown, timeout, malformed answer, and cap exhaustion retain the memory. Never delete anything from the EE store.

### Metric and bar

Join a filter invocation to the actual omp session/turn and observe the returned system prompt, not merely candidate `drop` rows. Measure total filter wall time; deadline/cap-kept coverage; actual removed input tokens; downstream cached/uncached input usage where available; newly billed Jev tokens; and independently labeled drop precision/task failures attributable to removed recall.

**Proposed bar:** frozen recorded-transport replay preserves every eligible-span decision of the serial incumbent and every non-memory byte. In fresh sessions with 20 eligible uncached items, p95 added latency is at most **1.5 seconds**, median latency falls at least **50%**, and at least **90%** of eligible items resolve within budget. Retain the original held-out quality bar, and require a one-sided 95% lower bound of at least **0.95** on drop precision over at least **200 independently reviewed drops** before widening scope. On a fixed eligible-turn cohort, retain at least **90% of incumbent removal**, not a comparison of unrelated medians. Downstream input-cost reduction must exceed Jev cost after cache effects; otherwise claim context reduction only.

**Cost/day:** no additional judgments are inherently needed. At the existing 200-call process/day cap and an illustrative 1,200 input tokens/call: **$0.01008 per active process-day**; ten fully consuming processes would cost **$0.1008/day**. This is not a machine-wide cap today. Reserve allowance before launching concurrent calls.

**Planted negatives:** derive a case from a recorded prompt with a genuine recall block; duplicate a recall line outside that block and inject a drop verdict. Only the recall occurrence may disappear. Also use a recorded relevant memory and a stalled transport: relevant/unresolved items remain when the turn returns on budget. These are application-safety mutations, not a model-quality benchmark made from invented prose.

### Confidence and stop condition

The benefit mechanism is already live; serial dependency and broad removal scope are visible in our code. No new model capability is needed. Uncertainty remains about bookkeeping overhead, throttling under concurrency, and filtering lost to the shorter deadline. If useful coverage collapses, adjust concurrency/time budget on a development slice—not the relevance quality bar. This extends `jev-9cqw`; it is not a second memory-filter project.

---

## 2. Compose the two web screens around one immutable tool result

### Why this is second

We have two different useful judgments and two hooks that can rewrite the same result. That calls for explicit composition, not a third detector.

`.omp/hooks/post/jev-webscreen.ts` judges passages and can replace individual fields. `.omp/hooks/post/jev-injection-shadow.ts` judges the whole result in the validated coding-agent persona and can replace it entirely. Both await network work on `tool_result`. Their states/questions are not interchangeable. Depending on host sequencing, a later detector could see an earlier replacement instead of the original evidence: a composition risk, not a measured claim about current host ordering.

A confirmed reporting defect also obstructs rollout: `scoreAndRecord` writes `withheld: flag` before checking enforcement mode. A shadow flag can therefore be logged as withholding even when the original result was delivered. `jev-j0er` needs actual withholds, not flags renamed as actions.

### Decision, seam, and implementation

**Jev decisions:** preserve both Noul policies: which passages instruct the assistant, and whether the whole result is an injection in the coding-agent seat. Freeze thresholds and persona.

**Seam:** one orchestrating `tool_result` handler around the two existing evaluators, shared by project wiring and `work/jev-j0er/*-global.ts` wrappers.

1. Capture original content/hash once. Each evaluator receives its existing view derived from those bytes. Run both requests concurrently when admitted. Do not first merge their questions into a new shared state.
2. Compose deterministically: a valid enforcing whole-result flag withholds everything; otherwise valid enforcing passage flags replace only those passages; otherwise preserve original content exactly. A failed evaluator contributes no flag; a valid flag from the other still applies.
3. Preserve policy caps, secret handling, input eligibility, and fail-open direction. Unsupported/oversize evidence remains explicitly unscored, not summarized into a supposed safety judgment.
4. Produce one operation outcome containing session, tool-call ID, repo, mode, policy versions, input/output hashes, `would_withhold`, and **actual bytes replaced**, alongside separate policy answers/usage. Do not count a shadow result or two flags on one event as two protected interactions.
5. Keep raw evidence out of ordinary logs. The notice may identify the source/tool and withholding, but must not echo attack instructions or exfiltration URLs. Do not automatically re-fetch or execute withheld material to “recover” it.

Healthy output is unchanged, without banners, and avoids serial latency. A flagged event gets one understandable replacement, not independent transformations that obscure what happened.

### Metric and bar

Pair actual omp delivery by **session + tool-call ID**. R128 rules out substituting path mentions or loose hashes for same-event outcomes. Measure result-to-model availability, actual replacements, byte preservation, clean false-withhold rate, planted catch rate, and subsequent abandonment/recovery.

**Proposed bar:** zero shadow-mode replacements, zero duplicate transformations/event, exact preservation of unflagged fields/content blocks on replay. When both evaluators succeed, p95 orchestration overhead is at most **50 ms above the slower evaluator**, rather than serially paying both latencies. Preserve the frozen coding-seat catch bar; require the one-sided 95% upper bound on the **combined path’s** clean false-withhold rate to be at most **2%** before non-Jev enforcement. Include all sampled clean results in the denominator, not only withheld ones. Do not shorten provider deadlines in the same first experiment.

**Cost/day:** approximately the existing two-seat cost, not a claimed halving of input tokens. **20 eligible events/day × two requests × 2,000 input tokens** costs **$0.00336/day**. At existing process limits of 25 webscreen + 100 injection requests and an illustrative 8,000-token average, the envelope is **$0.042/process-day**. These are scenarios, not hard dollar ceilings. Composition and metrics need no extra model call.

**Planted negatives:** replay the recorded benign OWASP/security-research case with its clean Jev verdict: suspicious regex matches alone must not withhold it. A newly obtained false flag on that independently labeled clean case counts as a failure, not an exception. Derive the positive from the recorded markerless injection set. Repeat under `enforce:false`: `would_withhold=true`, original bytes delivered. Add a timeout in one evaluator and a valid flag in the other to test composition.

### Confidence and stop condition

This fixes an actual reporting defect and an avoidable multi-writer architecture while retaining tested questions. Direct dollar upside is small because real web traffic is modest. Reliability and a defensible rollout are the larger benefit. If omp already overlaps the hooks, latency savings may be zero; composition and action-correct reporting still stand. This advances `jev-j0er`; it does not claim fleet enforcement is already complete.

---

## 3. Make judgment limits survive panes, restarts, and concurrent callers

### Why this is third

Several “daily” limits are variables inside handler closures. Memory-filter `calls`, `day`, and `paused`, and the web-screen equivalents, reset when the process is recreated. `kit/src/client.ts` also holds authorization/billing refusal state in a process-local variable for 15 minutes. SDK-client caching already exists; constructing a client cache is not the missing feature.

Reasonable one-agent behavior becomes surprising across profiles/RPC sessions: a long-lived worker exhausts its allowance while a new worker gets a fresh one; a new process need not know a peer saw a billing refusal. The repository measured **233 HTTP 402 calls over 4.5 hours** before introducing the existing hold. Extend its lifetime/scope; do not pretend that historical defect remains entirely unfixed.

### Decision, seam, and implementation

**Jev decisions:** unchanged relevance, injection, and risk Noul judgments. Jev does **not** decide budgets, retry permission, credential health, or request equivalence. Those are deterministic responsibilities.

**Seam:** request admission around `kit/src/client.ts` and existing hook factories. Exclude native omp judge traffic unless a supported integration seam is established separately. This cannot claim savings over every native find/auto-thinking call just because those also use TypeSafe.

1. Persist small atomic admission/refusal state by day, surface, and nonsecret provider/account configuration identity. Isolate unrelated test credentials/accounts; never persist a key or expose it as an identity.
2. Reserve before requesting. Distinguish successful completion, failure, and outstanding reservation. Count a crashed reservation conservatively toward spend without holding an in-flight lock forever. Restart is not a budget reset.
3. Share 401/402/403 holds for the same configured account. Do not turn 429/transport/5xx into permanent auth failure. Recovery is explicit credential/billing change or a single bounded designated probe, not independent retries by every waiting worker.
4. Retain separate finite surface allowances. Benefit-producing memory work and enforcing web checks must not lose all allowance to an observe-only gate or unconsumed rerank shadow. Inventory verdicts/operator policy already determine priority; no new classifier needed. Cap skips mean unscored, not safe.
5. Inspect complete exact-request signatures before building persistent verdict reuse. The memory memo already handles local repeats. Add cross-process reuse only if a keyless census finds material eligible repeats; bind it to exact state/question bytes, model, policy revision, repo/trust scope, and expiry. Cache only validated successful answers, never failures or permission grants. No semantic cache.

Keep this daemonless. A new durable component should be narrow safe Rust using an existing tested storage primitive, not a new Python daemon or orchestration framework; keep thin TS adapters at omp seams. First implement atomic allowances/holds. Persistent caching is conditional, not a prerequisite.

### Metric and bar

Join admissions/provider usage to real hook events: requests per account/surface/day, concurrent admissions, attempts after auth refusal, cap-unscored share, admission latency, and downstream benefit per admitted call. Current mixed log counts cannot establish an organic cache hit rate.

**Proposed bar:** ten concurrent workers and a deliberately small cap cannot over-admit across restart/crash/day-boundary tests. After 402, no newly admitted remote request during the shared hold; distinguish previously admitted/in-flight calls. Recovery has one bounded owner. Healthy p95 local admission overhead is at most **5 ms**, without sustained contention. At equal total allowance, preserve successful coverage of enforcing seats; report any tradeoff rather than hiding it behind a cheaper bill. Cross-process caching earns implementation only at **at least 10% exact eligible duplicates** in a properly scoped census, then must cut newly billed input at least 10% without changing replayed applied verdicts.

**Cost/day:** **$0 incremental Jev cost** for local admission/holds. Do not quietly increase allowances. For scale, 2,000 admitted memory requests at 1,200 tokens each cost **$0.1008/day**, regardless of whether one or ten processes consume them. That is a planning example, not a newly authorized increase. Outage/cache savings are unquantified until measured. Do not add this example to ideas 1 and 2: they describe overlapping underlying calls.

**Planted negatives:** inject the recorded billing-incident 402, restart, and attempt from another process: no new request leaves. Inject 503 separately: no durable auth poisoning. Change one state byte or policy revision of an optional cached success: cache miss. Corrupt admission state: refuse optional remote work and preserve original content rather than resetting to unlimited allowance.

### Confidence and stop condition

The scope mismatch is in source and the billing incident supplies a real failure class. This buys predictable operation, not an unproven semantic skill. The danger is a central bottleneck built to save pennies. If coordination cannot stay tiny and below the overhead bar, narrow it to persistent holds and daily reservations; do not add a resident broker. Quality and foreground latency matter more than a maximally “free” call share.

---

## 4. Make retirement effective and activation refer to running code

### Why this is fourth

R132 supplies a direct failure witness: an already-retired claim rule was still recorded firing **125 times** because sessions had not reloaded. The key-source reminder fired **491 times** in its seven-day census and had **0/26** relevant observable cases in blind review. Moving a file into `disabled/` does not remove already-loaded instructions.

Do not resurrect either rule. Stop paying their attention/context cost after withdrawal, and stop mistaking a changed hardlink/config for adoption. Strengthen `jev-6pjh` and the existing installer/global wrappers; do not build another fleet dashboard.

### Decision, seam, and implementation

**Jev decision:** existing Noul relevance/injection questions, or the qualified typed question belonging to another enabled policy, only while that exact version is active. Retirement/install/reload/version selection is deterministic and operator-controlled, never a new Jev vote about whether Jev should run.

**Seam:** owned hook/extension registration and result application, `kit/src/install.ts`, profile entrypoints, and the conductor’s verified worker-restart boundary.

1. Bind a policy revision to actual loaded code/question bytes. From inside the running session, record that revision, session/process identity, scope, and mode on the first real handler invocation. Configuration discovery is insufficient.
2. Have owned hooks consume a minimal activation/retirement record, reusing the local state machinery in idea 3 where appropriate. Check eligibility before a paid call and before applying its answer. A revoked version preserves context/content and emits no stale advisory; late answers cannot resurrect it. Deterministic DCG/kit-guard protections are outside this mechanism.
3. Do not hot-import arbitrary changed code into an in-flight session. New implementations still require fresh-session positive/negative proof. Healthy operation is silent; only a mismatch or failed handoff reaches the existing conductor.
4. Native TTSR is a different lifecycle. An owned post-hook cannot promise to unload rules already resident in omp. Establish whether the installed host supports reload; otherwise checkpoint/restart at a confirmed task boundary. Use the worker’s own session binding/callback and process identity, not a title, new RPC session, or spinner. Without a safe boundary, keep that worker explicitly stale; do not kill it or claim completion.
5. Preserve unrelated extension arrays and guards. Outside Jev, a fresh session proves the global wrapper fires once; inside Jev, prove it is not registered twice alongside the project hook.

The state record directly controls runtime behavior; it is not a certificate someone must remember to read. Existing sessions predate the new retirement check, so the initial installation itself still requires a verified reload/restart. Do not claim the new check retroactively controls them.

### Metric and bar

Read actual session/hook events by loaded revision: paid calls, semantic injections after retirement, duplicate firings, and time to verified adoption. Count actual retired-policy context tokens separately; 125 firings is not a token estimate.

**Proposed bar:** instrumented retired versions make **zero new admissions and zero applications after observing retirement**, including delayed answers. Every designated worker has fresh-session both-direction proof before rollout completion. Native TTSR retirement requires **zero post-reload firings in those workers**; unsupported/no-safe-restart cases remain incomplete. Healthy checking adds no model-visible tokens or Jev calls. Never hide stale/unobserved workers in a green aggregate.

**Cost/day:** **$0 added Jev input** for retirement/version checks. Potential savings are unwanted queries and unwanted model-visible context. R132 reported **$0.0131 over seven days for all measured TTSR usage**, with no per-rule attribution: do not claim these retirements save that entire amount. Measure removed context and its cached/uncached cost.

**Planted negatives:** load an owned policy, pause its mocked answer, retire it, release the answer: no injection/withholding. Freshly load the replacement and replay recorded positive/benign inputs to prove action and silence. Repeat the recorded retired-rule trigger after native TTSR reload/restart. An old worker still running remains unresolved even if a new RPC probe passes.

### Confidence and stop condition

This addresses a demonstrated interruption, not an abstract reliability goal. Uncertainty concerns native host lifecycle support. The owned-hook retirement path is useful independently, but the native-rule leg stays open until truly unloaded. A design that can only print “stale” forever fails this recommendation. This is fourth because lifecycle integration is harder than fixing a handler and cannot be hand-waved into completion.

---

## 5. Put the exact human decision into the existing needs-human page

### Why this survives, but ranks last

The page has a real consumer and small-sample detection evidence, but no demonstrated recovery-time saving. `check_idle_needs_human` emits the **first 140 characters** of the assistant message. That may be status preamble rather than the question Joshua must answer.

Improve the page rather than adding idle checks, another monitor, or a generic stuck classifier. The hypothesis is cheap to falsify and user-facing, but confidence in benefit is lower: human availability may dominate response time.

### Decision, seam, and implementation

**Jev decision:** after the existing `needs_human` Noul qualifies a page, use a bounded **Choice over source-span IDs plus `none`**: which span states the concrete unresolved human decision? Select evidence, never generate a summary, invent an owner, grant approval, or choose a destructive remedy.

**Seam:** `scripts/fleet-needs-human.mjs` and existing `check_idle_needs_human`/page formatting in `scripts/fleet-idle-watch.py`. No new monitor or polling cadence.

1. Deterministically split the same bounded, secret-screened message into paragraph/sentence spans with stable IDs and a small maximum count. Validate the returned choice/distribution. Ensure a terminal question can be represented; unsupported shapes retain the incumbent page.
2. Quote the selected original decision-bearing span with the existing pane ID and exact session/message pointer. Include a bead only when bound by trustworthy state, not semantic similarity.
3. On `none`, uncertainty, invalid answer, timeout, or extra-call cap exhaustion, deliver the existing page. Enrichment failure must never suppress a qualified alert. A span identical to the old excerpt is not an improvement.
4. Leave importance and delivery deterministic. Agent Mail already exposes `importance`; R42 rules out paying to rediscover it. Do not mark mail read, auto-acknowledge, add recipients, or treat an approval sentence as actual approval. Retain duplicate suppression.

Healthy workers remain silent. The intended gain is fewer trips through scrollback to understand a decision—not more pages or longer prose.

### Metric and bar

Join existing page time/mark to the exact session and subsequent substantive resumed work, retaining never-resumed/censored cases. Measure correct action-bearing selection, omission by the old prefix, page-to-resume time, clarification requests, page count, and incremental context/page bytes.

**First bar, keyless:** blind-review **30 historical qualified pages** and find at least **10** whose delivered prefix omitted the decision. If that opportunity is absent, stop. If deterministic selection of the last explicit question fixes the same cases, ship that and give Jev no seat.

**Jev bar if the seat remains:** at least **95% correct selections** on a held-out set, no lost qualified pages, no duplicate-page increase, and improvement over that deterministic selector. Then interleave at least **30 comparable decision-required operational pages**, targeting at least **25% lower median page-to-resume time**. Report the distribution, censoring, and human availability; do not turn the historical 6.9-versus-5.4-minute observation into a causal claim. Never deliberately delay/suppress an urgent incumbent page to create a comparison.

**Cost/day:** at most **20 added Choice calls/day**, matching the current finite helper scale. At 2,000 input tokens each: **$0.00168/day incremental**, plus the unchanged Noul cost. A formatting-only winner costs **$0** and is preferable. Give enrichment a short deadline so a better page does not arrive substantially later.

**Planted negatives:** use a recorded completion/status message as the non-paging control; a quoted old question must not become a new approval request. The positive is an actual decision-required message with a long status prefix. Include an actual spend/destruction approval request: quote without executing, approving, or preselecting the answer. Failed Choice still delivers the qualified incumbent page.

### Confidence and stop condition

This is the right place to test usefulness: an existing page whose classifier works but whose time-saving claim does not. A speedup is not promised. If pages already expose the decision, or human availability explains the delay, retain the present system. That is better than declaring success from how many spans Jev classified.

---

## The 30-candidate winnow

These are selection outcomes, not thirty implementation commitments. The five recommendations contain the full decision/seam/metric/bar/cost/negative contracts. Related candidates were folded together rather than inflated into separate projects.

| # | Candidate considered | Disposition and reason |
|---|---|---|
| 1 | Bounded parallel memory judgments | **Selected: 1.** Existing quality evidence and a serial foreground path. |
| 2 | Occurrence-addressed recall pruning | **Folded into 1.** Correct application belongs with that filter. |
| 3 | One giant multi-memory question batch | Not first: changes state/interactions; independent concurrency preserves the validated shape. |
| 4 | Cross-process exact verdict cache | Conditional component of **3**; current memo exists, but fleet duplicate demand is unproven. |
| 5 | Durable surface allowances/shared refusal hold | **Selected: 3.** Process lifetime currently changes effective policy. |
| 6 | Batch unrelated hooks into one request | Reject: incompatible state/trust scopes and coupled deadlines; not a free optimization. |
| 7 | Compose whole-result and passage screening | **Selected: 2.** Existing consumers and an actual action-reporting defect. |
| 8 | Automatically re-fetch/unwrap withheld results | Reject: can undo protection; no measured recovery benefit. |
| 9 | Preserve benign security research/source structure | **Folded into 2.** The recorded OWASP false positive supplies a control. |
| 10 | Another DONE/numeric claim judge | Reject: R130/R83; no new evidence overturns their limits. |
| 11 | Effective policy retirement across workers | **Selected: 4.** R132 documents retirement that did not stop firing. |
| 12 | Hot-reload hook code every turn | Reject: imports do not solve state migration, delayed answers, or native TTSR lifecycle. |
| 13 | Another surface-status dashboard | Reject: reporting is not a runtime improvement; use existing consumers. |
| 14 | Source-span selection for needs-human pages | **Selected: 5**, conditional on the cheap opportunity/heuristic check. |
| 15 | Jev urgency reclassification for Agent Mail | Reject: R42; server importance and urgent-mail paging already exist. |
| 16 | Cheap/default/strong subagent routing | Reject now: `jev-t5jk` reports zero cheap routes in 60 replay calls and no actually-cheap cohort; verifier also disputes denominators/row availability. |
| 17 | Enable auto-thinking everywhere | Keep existing rollout, not a new idea: already ON in named profiles with a measured win. |
| 18 | Per-turn model switching by hardness | Reject: existing route extension explicitly gives advice only and records prior savings inversion. Advice is not execution. |
| 19 | More aggressive smart-stop continuation | Reject: zero observed promise-stops is IDLE-BY-DESIGN, not a reason to lower the bar or substitute nimble. |
| 20 | Jev task priority over beads | Reject: R43; no new human-disagreement dataset justifies replacing bv/br facts. |
| 21 | Jev validates DAGs/close prerequisites | Reject: deterministic graph/contract checks already own this. |
| 22 | Another find-versus-grep semantic router | Defer: preserve the proven rule; no demonstrated increment over native find/guidance. |
| 23 | A second native-find rerank pass | Reject: find already uses Jev; extra ranking needs a marginal result, not the same saving counted twice. |
| 24 | Withhold arbitrary local reads by relevance | Reject: R19 and no validated future-use policy; memory success is not transferable automatically. |
| 25 | Revive skill hints with another lexical shortlist | Reject: R131/R133 exhausted this family; no new semantic retrieval evidence here. |
| 26 | Add Jev to cass/EE search ranking by default | Reject now: R116 found no high-frequency independent seat; actual memory filtering has the consumer. |
| 27 | General stuck/retry foreman | Reject now: R28 prevalence remains a problem. A metadata census of 80 recent canonical Jev session files found only one exact repeated error, on `wait`; tests were not excluded and this is not confirmed waste. |
| 28 | Select a root-cause block for every CI failure | Defer: no measured daily consumer/avoidable-debug-time cohort here. First consume structured failing-step facts. |
| 29 | Load-aware local gate-cascade scheduling | Defer: inspect timeouts, but this observer is asynchronous and has no demonstrated organic safety benefit. Service time is not foreground delay, and local is not resource-free. |
| 30 | Semantic transcript/compaction pruning | Reject: R99/R100 future-need losses are not overturned by memory-filter success. Preserve recoverable history. |

## Practical order and stop conditions

Start with **1**, then **2**: working paths, existing model questions, immediate observable effects. Implement **3** narrowly alongside fleet rollout, not as a prerequisite framework. Use **4** to make those rollouts/retirements true in running workers. Run **5’s keyless check** before engineering its Choice question.

Use existing tests, hook logs, session files, and a named verifier—not a new dashboard, ledger, or paid comparator. Fresh-session positives and planted negatives remain necessary. If latency savings are zero, a cache has no hits, or an enriched page does not shorten work, report that and stop the branch. The objective is fewer expensive agent tokens, less foreground waiting, and fewer interruptions on this machine—not more Jev calls.
