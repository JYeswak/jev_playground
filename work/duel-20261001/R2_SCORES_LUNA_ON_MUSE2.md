# R2 MUSE2 — Luna’s candid evaluation (2026-10-01)

## Scoring basis

Scores are overall decision scores, not confidence percentages: practical benefit to humans/agents, evidence for the problem and expected effect, implementation/correctness risk, and whether the durable value justifies added complexity. A high score means “worth pursuing from the current state,” not merely “interesting.” Already shipped, refuted, low-evidence, or redundant ideas score low even if the original concept was good. I score the proposals against the repository evidence I inspected; MUSE2’s quoted nightly metrics are treated as claims unless independently visible in the cited artifacts.

## At-a-glance

| Idea | Score |
|---|---:|
| 1. Bundle memory judgments into one request | 690 |
| 2. Reuse each memory’s verdict for a whole session | 230 |
| 3. Skip exact prompt echoes deterministically | 610 |
| 4. Deduplicate repeated recall across turns | 180 |
| 5. Skip instruction-prose lines without scoring | 490 |
| 6. Local Nimble for memory Noul | 0 |
| 7. Lower the 200/day cap | 100 |
| 8. Skip filtering when recall is empty | 60 |
| 9. Audit the EE task-context parser branch | 390 |
| 10. Deterministic destructive-command pre-rules | 510 |
| 11. Add curl-pipe-shell and chmod -R 777 pre-rules | 460 |
| 12. Paid rescore of Nimble-cleared destructive commands | 290 |
| 13. Stabilize prompt-cache prefix with order/dedup | 350 |
| 14. Shake tuning | 0 |
| 15. Enforce find-first for locating files | 650 |
| 16. Fleet-wide cache for repeat read-only commands | 160 |
| 17. Serialized commits | 0 |
| 18. Lsof-scoped holder check in watcher | 640 |
| 19. Retire rules through ttsr.disabledRules | 180 |
| 20. Duplicate-work guard before bead claim | 560 |
| 21. Idle-session auto-stop | 90 |
| 22. Kill-switch dashboard for shadows | 70 |
| 23. Session-start cost ledger per pane | 50 |
| 24. Bead-graph auto-claim | 180 |
| 25. Subagent model pinning | 0 |
| 26. Extend effort routing to tool-heavy turns | 250 |
| 27. Local Ollama for memory Noul, conditional on parity | 0 |
| 28. Pre-warm recall at session start | 100 |
| 29. Cap prompt turns per session | 20 |
| 30. Turn off smart-stop | 0 |

## Idea-by-idea evaluation

### Memory / recall

1. **Bundle memory judgments into one request — 690/1000.** Strong latency target and a plausible low-complexity optimization, but the exact pitch (“same Noul, same state per question”) skips the hard part: each current request has a different `{prompt, memory}` state, while the multi-question API evaluates questions against a shared state. The implementation must encode the K distinct pairs into one shared state and construct K correctly indexed questions; that changes question construction and increases request size. Require measured bundled-vs-single decision agreement on recorded pairs, including boundary values and errors, plus actual end-to-end latency. Also, this is not an untouched 20-serial-call baseline: `.omp/extensions/jev-memory-filter.ts` currently runs up to four asks concurrently, and `expected.json` records `jev-11qz` at 1,308 ms, about 60% below the serial 3.3 s. One request could still improve tail latency and request overhead, but “20 calls → 1 RTT” overstates the incremental win. Keep as a focused, reversible latency experiment, not an assumed ≥70% result.

2. **Score each memory once per session — 230/1000.** A memory’s relevance depends on the current request, not a fixed session topic. Session-wide reuse will be stale precisely when the user changes task. A topic-drift detector adds another judgment/heuristic and can fail silently at the transition it is meant to catch. The extension already memoizes the exact `(promptHash, memoryHash)` pair within a process; that preserves reuse only when the inputs match. Better to retain that correctness boundary. A carefully specified cache tied to an exact, immutable task context could be reconsidered, but “session-scoped” is too broad.

3. **Deterministic exact-echo skip — 610/1000.** Cheap, understandable, and likely safe if equality is byte-exact after the same normalization used by the scorer: when memory text equals the current prompt, keep it without asking Jev. It avoids a low-value judgment rather than making a new relevance claim. The estimate of savings is unsupported without the organic frequency of exact echoes; the cited 0.92 is a score, not prevalence. Ensure comparison uses the exact prompt representation sent to Jev (the current prompt is truncated to 2,000 characters), otherwise a truncated-prefix match could wrongly skip a judgment. Simple shadow count first; ship only if nontrivial frequency exists.

4. **Recall-side dedup across turns — 180/1000.** The core duplicate problem is already addressed within a prompt: the filter deduplicates identical memory text before scoring, and its memo reuses verdicts for identical prompt+memory pairs. Deduplicating repeated recall across *different* prompts is not generally sound because relevance changes with the request. Persistent recall dedup may instead hide source identity, ordering, or prompt-specific context. No new value without an observed duplicate class that is semantically interchangeable and a measured safe reuse condition.

5. **Drop instruction-prose lines without scoring — 490/1000.** Potentially useful if parser captures confirm static instruction text is being mistaken for memory and consuming scarce calls. The code explicitly identifies `<memories>` and an EE tail, and a prior live parser issue was fixed by parsing prompt elements separately; do not assume the branch still misclassifies. A deterministic parser boundary is preferable to spending Noul calls, but it must preserve actual EE memories and avoid changing prompt bytes. First label captured parser candidates and quantify wasted calls; then fix classification only for a demonstrated false-positive shape. Medium score because the likely savings are small and a parser false negative can change what gets retained.

6. **Local Nimble for memory Noul — 0/1000.** The proposal itself says this is refuted by `yl60`: 250 pairs, 84.4% agreement against Jev versus a 95% bar, and 3 of 11 Jev-kept relevant memories incorrectly dropped. The matching R138 row in `NEGATIVE_EVIDENCE.md` is dated 2026-10-02, later than the 2026-10-01 evaluation date, so I do not treat that row as contemporaneous evidence; the same numbers and refutation are explicitly supplied in the proposal. Its stated retry condition is ≥95% agreement and zero critical drops on the same population, keylessly. No passing evidence is offered. Do not spend calls or wire it in.

7. **Lower the 200/day cap — 100/1000.** “Arbitrary” is not evidence that the cap is causing a problem, and the cap is a safety/cost bound. Lowering it could make the filter skip useful judgments; raising or changing it also needs rate/volume evidence. Inspect cap-hit rates and effects first. The empty-recall case already avoids calls, so the stated adjacent motivation does not justify changing the cap.

8. **Skip filter when recall is empty — 60/1000.** Correct optimization in theory, but already naturally free: no memory candidates means no per-item ask loop. An explicit early return might save parsing/logging work, but that is not a user-visible latency lever absent a measured cost. Avoid code for a zero-call path unless profiling identifies meaningful overhead.

9. **Audit the EE task-context parser branch — 390/1000.** The proposed measurement is more valuable than immediately deleting or “fixing” code. Zero relevant hits in captures does not establish dead code: the captured workload may not exercise the intended feature. Determine whether EE blocks exist in live prompts and whether parsing produces candidates; then remove dead behavior only if the input population rules it out. A narrow, keyless reachability audit has low risk, but deletion/fix is premature and its practical impact is likely small.

### Safety gates

10. **Deterministic destructive-command pre-rules — 510/1000.** Deterministic checks are attractive for known dangerous shell forms, especially when a model has a measured false-clear. But “`rm -r/R` outside `/tmp` → instant flag” is a broad policy, not a mere optimization: it would block ordinary repository cleanup and legitimate deletion, while `/tmp` is not inherently safe. Shell syntax, quoting, variables, symlinks, and command composition defeat naïve regexes. The existing cascade evidence in `expected.json` is strong overall (950 Nimble-cleared commands, 0 harmful blind-labeled; 9/10 planted commands held, with an `rm -rf` nonexistent-path miss), but that supports a targeted analysis of the missed command class, not an unconditional blanket rule. Score rises only for a narrowly defined, parsed high-risk condition with benign corpus coverage, explicit fail-safe behavior, and no claim that the `/tmp` carve-out is universally safe.

11. **Add curl-pipe-shell and chmod -R 777 pre-rules — 460/1000.** Both command shapes can be dangerous, but simplistic string matches flag quoted examples and miss shell indirection/format variants. `curl | sh` can also be a documented installer; `chmod -R 777` may be intentional in a disposable fixture, though usually risky. Treat each as a separately measured rule with a command grammar, policy rationale, and recorded benign controls. Bundling two rules obscures which one creates false positives. More practical as deterministic checks in a proper command parser/policy layer than ad hoc regexes in the Jev gate hook.

12. **Paid-Jev rescore of Nimble-cleared destructives — 290/1000.** It could estimate a selected disagreement/error rate, but paid Jev is not ground truth for harm, and the existing seven-day blind-label result is already 0/950 harmful among Nimble-cleared commands; a paid rescore reportedly flags none. This proposal risks paying for another noisy label instead of investigating the known `rm -rf nonexistent` miss with independent command/context labels. If new evidence shows a specific unlabeled high-risk stratum, use a bounded blinded audit with human ground truth and a preregistered sampling plan; otherwise not a priority.

### Tokens / cache

13. **Stable prompt-cache prefix via order and dedup — 350/1000.** Fixed ordering can help only if the provider’s caching contract keys the relevant prefix and the varying content is placed after it. Reordering system elements or deduplicating prompt content can change precedence/meaning; “billed retransmit bulk” does not prove wasted billable tokens or that the cache is missing. The 98.878% figure is a config/comment anchor in the proposal, not enough evidence of a cacheable prefix or an opportunity to reduce spend. First inspect actual serialized provider payloads and documented cache semantics, then establish per-session billed-token baseline. Avoid changing instruction/memory order based on a cache hypothesis.

14. **Shake tuning — 0/1000.** Already on and explicitly excluded by the proposal itself. No change to make; any tuning requires a new measured defect.

15. **Find-first enforcement — 650/1000.** Strong, measured agent-ergonomics value: the project records 576 versus 5,293 tokens per located file, and a controlled A/B of 404 versus 1,861 at equal success. The rule is already in `AGENTS.md`; the incremental proposal is a lint/enforcement mechanism. A lightweight, accurate locator check could make the behavior durable across agents, but a brittle lint that rejects legitimate content searches or forces `find` for symbol/literal searches would add friction and teach the wrong distinction. Build only if observed violations remain despite the rule, and scope the check to file-location operations. High upside, modest implementation, but not a new idea in this tree.

16. **Fleet read-cache for repeat read-only commands — 160/1000.** A cache keyed by cwd/command/HEAD/mtime is not correct for `git status`, branch/index state, environment-dependent commands, external bead DB changes, and files modified without the expected timestamp behavior. A command result may also depend on unkeyed environment variables or concurrent writes. Building a generic bash wrapper adds stale-evidence risk to an agent workflow. A read-only cache is viable only for a tightly enumerated deterministic command with a complete invalidation key and observed duplicate rate; the proposal lists broad commands, so reject the generic cache.

### Fleet / process

17. **Serialized commits — 0/1000.** The proposal says this is already shipped. No additional implementation or benefit follows from re-proposing it.

18. **Lsof-scoped holder check in watcher — 640/1000.** A concrete reported bug with a plausible narrow fix: a machine-wide `pgrep` veto can confuse unrelated processes with actual holders. Scoping to the relevant open-file/process relationship is materially safer than weakening the veto. This is a good engineering fix if the observed false veto is reproduced from the watcher’s recorded process state. Keep it narrow; do not fold in unrelated commit-wrapper changes. Need a test covering both a genuine holder (must veto) and an unrelated same-name process (must not veto), plus a real watcher smoke.

19. **Retire rules through `ttsr.disabledRules` — 180/1000.** The cited `jev-pn7b` evidence says retired rules fire only in sessions started before retirement; fresh sessions are clean. That refutes the proposed loader defect and weakens the case for runtime disable plumbing. Mutating a live configuration surface may add risk without addressing the residual: revocation in already-running sessions. Use the established session-bound activation semantics, and reopen only for a demonstrated requirement to revoke a rule inside an existing session. Do not assume `ttsr.disabledRules` is a supported mechanism absent API evidence.

20. **Duplicate-work guard before bead claim — 560/1000.** Avoiding double claims has practical fleet value and the cited 8qu6 incident is a concrete defect. But a read-only assignee check alone is a check-then-act race: two agents can observe unassigned and both claim. The useful fix is an atomic claim/update with a single winner, or a reservation/lease mechanism already supported by the tracker—not a convention-only guard. Keep recovery for abandoned leases explicit. Medium-high value; implementation correctness is the deciding issue.

21. **Idle-session auto-stop — 90/1000.** High risk of equating quiet with safe-to-stop: a worker may be waiting for a slow tool, human input, or a continuation. Requiring a needs-human signal reduces but does not remove risk; that signal means page/wait, not necessarily terminate. Savings are unquantified and destructive cleanup of sessions can lose useful state. Prefer notification or a human-approved stop until an independently measured state machine proves stop-safe transitions.

22. **Kill-switch dashboard for shadows — 70/1000.** A dashboard is not itself a kill switch and creates a maintenance/attention surface. Existing shadow controls should remain simple and operable; add a dashboard only if operators have demonstrably failed to find or activate an existing control and a named consumer needs it. No defect or measurable benefit supplied.

23. **Session-start cost ledger per pane — 50/1000.** Observability without an action path is not a useful feature by itself. The repo already has call-level sidecars and session usage information; another ledger duplicates evidence unless it changes a concrete budget/dispatch decision. No such decision or defect is named. Prefer querying existing records.

### Thinking / models

24. **Bead-graph auto-claim — 180/1000.** Auto-claim can reduce dispatch friction but risks assigning blocked, stale, sensitive, or wrongly scoped work. The bead graph helps rank work; it does not establish an agent’s capability, file reservation, or authorization. Use the existing ready/claim workflow and atomic ownership. Automate only a narrow dispatcher with explicit ownership/eligibility rules and measured conductor overhead.

25. **Subagent model pinning — 0/1000.** Already done per the proposal. No incremental value unless a regression shows an active call path using an unintended model.

26. **Extend effort routing to tool-heavy turns — 250/1000.** Potentially useful if tool-heavy prompts are systematically under- or over-budgeted, but there is no baseline or demonstrated miss. Tool count is not the same as reasoning difficulty; routing on it can increase cost while harming success. First measure effort choice, task outcome, and cost on a representative held-out set. A new policy without that evidence is speculation.

27. **Local Ollama for memory Noul if parity passes — 0/1000.** This is conditional, but the proposal says the condition already failed: `yl60` reports 84.4% agreement on the 250-pair set and 3/11 critical relevant memories dropped, below its 95% and zero-critical-drop bar. The matching R138 entry is dated 2026-10-02, after the stated evaluation date; I rely here on the proposal’s own description, not on treating that later-dated row as contemporaneous. No new fact is offered that meets the retry condition. Do not run or wire this experiment unless the keyless parity gate passes on the specified population.

28. **Pre-warm recall asynchronously at session start — 100/1000.** The assumption that recall is not already asynchronous is unverified, and session-start precomputation can add latency/network work before the agent knows which memories matter. Results may be stale or unused. Measure current recall timing and cache behavior first; only prefetch if the existing critical path is demonstrated and an exact invalidation key exists.

29. **Cap prompt turns per session — 20/1000.** Arbitrary turn caps truncate real work and shift the failure to a confusing user-facing boundary. No budget or quality threshold is supplied. If runaway sessions are a real cost problem, bound by explicit spend/time with a resumable state and a measured stop policy, not a fixed turn count.

30. **Turn off smart-stop — 0/1000.** No case for changing it. The project rules say the feature is on and tested both ways; the inventory labels the surface idle-by-design because there were no promise-stops to catch. Those facts support keeping the feature as-is, not turning it off. Reconsider only if a measured false continuation or cost exists.

## Verdict on the proposed top five

The ordering is not persuasive as written. **#1 (bundling)** is a reasonable experiment, but its one-request state construction and existing 4-wide concurrency must be included in the design and baseline. **#2 (cache-prefix stability)** is the weakest of these five: cache behavior and billed-token savings are asserted, not demonstrated, and reordering prompt content can change behavior. **#3 (session verdict reuse)** is unsafe across changing prompts; the existing exact-pair memo is the sound boundary. **#4 (destructive pre-rules)** targets a real class of risk but the `/tmp` carve-out and broad path test are unsound as stated. **#5 (fleet read-cache)** is too broad and creates stale-output risk.

My practical next bets from this 30 are: (a) prove or reject the correctly designed batch request against single-call recorded pairs; (b) reproduce and fix the narrowly evidenced watcher holder-scope bug; (c) close any observed find-first violations with a narrow locator-only check; and (d) test exact-echo and instruction-prose prevalence keylessly before coding. None should be called a win until the behavior and benefit are observed on their intended surface.

## Evidence boundary

I read `AGENTS.md`, `README.md`, `work/jev-inventory/expected.json`, `work/duel-20261001/DUELING_WIZARDS_REPORT.md`, `work/duel-20261001/WIZARD_IDEAS_MUSE.md`, `.omp/extensions/jev-memory-filter.ts`, and `NEGATIVE_EVIDENCE.md` R134–R138. Particularly relevant: the memory filter already uses four concurrent asks and exact-pair memoization; expected inventory records the 1.3 s concurrency result, the 0/950 gate-cascade blind audit, and memory-filter receipts; R135 refutes the cited semantic-shortlist direction; R136 discloses the tiny n for needs-human enrichment; and `jev-pn7b` in the prior duel report narrows the retired-rule issue. **Date boundary:** repository R138 is timestamped 2026-10-02, one day after the system date supplied for this evaluation, so I do not independently treat it as contemporaneous; the MUSE2 proposal itself labels `yl60` refuted and supplies its 84.4%/3-of-11 result, which is the basis of the local-Nimble scores. I did not independently replay the nightly logs, run bead queries, or reproduce the watcher claim; those claims remain attributed to the supplied proposal where noted. No implementation or live call was performed.