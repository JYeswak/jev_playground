# Planning review round 2 — pane 2

Plan pin: `e106eb7`. Prompt: `notes/deep/dispatch/p2-wave1.md` Part B, applied to the integrated plan. Focus: W7.0, W7.3/W7.4, Phase C. The plan is not edited.

## Removal: drop the blanket T4 on tool/integration clones

`pi-subagents` was routed as tool/integration, so the profile required T4. The receipt at `docs/demos/upstream-repro/pi-subagents-w70-20260922.md` marks T4 `NOT-APPLICABLE`: the clone does not call Jev. A second pane can mark that `FAIL` for a missing live call. Both readings fit the plan.

```diff
- **tool/integration** clones (MCP servers, hooks, routers, compaction) run T1–T4 + T9 + T10
+ **tool/integration** clones run T1–T3 + T9 + T10.
+ T4 is added only when the clone's own source contains a Jev client.
+ If it does not, T4 is NOT-APPLICABLE and the file:line is the proof.
```

Why: a required live call on a clone with no client cannot be performed, so two panes will not record the same row. Evidence: `pi-subagents-w70-20260922.md` T4; class profile at plan line 441.

## Change: T4 must not demand p50/p95 below N=5

T4 says N, prevalence, cost, and p50/p95 are stated. `jev-router-w70-20260922.md` recorded N=1, latency 1152 ms, and correctly called it a smoke. A second pane can invent a p50 from that one number and call T4 passed. The bar committed at `da2a785` already says p50/p95 are not observable below N=5. The plan does not.

```diff
- N, positive-class prevalence, cost and p50/p95 latency stated
+ N and cost stated. Prevalence is stated or NOT-APPLICABLE with the reason
+ there is no labelled positive class. p50 and p95 are stated only when N>=5;
+ below that the cell is "not observable", and writing a percentile from one call fails T4.
```

Why: otherwise T4 cannot fail a one-call smoke that prints a fake percentile. Evidence: router receipt T4; `w70-t4-bar-20260922.md` at `da2a785`.

## Flag: T2's plant arm cannot be observed when the suite is already red

T2 says plant a defect in `/tmp` and the suite must go RED, or record the suite as unable to fail. `pi-subagents` was already exit 1 before any plant (this re-run: 3262 pass, 24 fail, 23 cancelled, 12 skipped, of 3321). A plant on a red suite does not show that the suite can fail. The row cannot distinguish "unable to fail" from "already failing".

```diff
- then one defect planted in a `/tmp` copy must turn it RED, or the suite is recorded as unable to fail
+ if the unmodified suite exits 0, a planted defect must turn it RED, or it is unable to fail.
+ If the unmodified suite already exits non-zero, record that exit and the fail count.
+ The plant arm is NOT-APPLICABLE until a clean run exits 0.
```

Why: the current sentence treats a pre-existing red as the same outcome as a successful plant. Evidence: `pi-subagents-w70-20260922.md` non-author re-run footer.

## Flag: W7.3 acceptance cannot fail

W7.3 says every sentence traces to a ledger row, and the ledger's `run_status` is a lead, not evidence, until a W7.0 receipt exists. Tool clones do not run T6. If no seat/benchmark T6 receipt exists, a writer can ship an empty section and meet "every sentence traces" vacuously. Two panes will not produce the same page: one will cite leads, one will write nothing.

```diff
- From W7.1, a short README section
+ From W7.0 receipts only. A lead in the ledger is not a sentence.
+ Acceptance fails if the section is empty while zero T6 receipts exist:
+ the packet stays blocked, it does not publish a blank "what we learned".
```

Why: an empty page is not a finding, and a page built from leads repeats the failure Joshua named. Evidence: plan lines 417–419 and 474–477; this wave's tool receipts have no T6 row.

## Change: W7.4 cannot become a Phase C bead as written

Phase C exit: every §4 packet is a bead with WHAT/WHY/ACCEPTANCE. W7.4 says "candidates are chosen by the ranking, not assumed here." There is no scoring function. Prevalence may be `unknown`. Cost is a word. Decision leverage is not a column. Two panes ranking the 14 `apply` rows will not emit the same top three.

```diff
- Rank W7.1's application_in_our_systems rows by AGENTS.md's selection rule
+ Rank only rows whose W7.0 receipt exists. Score is lexicographic and written
+ in the bead body before the sort: ground_truth 1 if the receipt names a
+ labelled corpus, else 0; prevalence is a fraction or 0 if unknown;
+ cost is 2 keyless, 1 live-key, 0 rch-worker; leverage is 1 if the row names
+ an omp surface that can block or rewrite a tool call, else 0.
+ Phase C creates the W7.4 bead only after that table exists.
+ A bead titled "apply the top three" with the three unnamed is not a bead.
```

Why: Phase C cannot emit WHAT for an unnamed target. Evidence: plan lines 479–483 and 560–561.

## What cannot become a bead as written

- **W7.0** is a standard, not a deliverable. Making it a bead duplicates W7.2's acceptance. It should stay a gate on W7.2, not a bead of its own. `[Inference]` only in the sense that the plan does not say "W7.0 is a bead"; Phase C says every §4 packet is one, and W7.0 is a packet.
- **W1.4** acceptance requires a human-launched `KIT_GATE_EDIT=1` session. An agent cannot close it. Phase C may create it only as blocked on that session, not as `br ready`.
- **W0** is the conductor's loop. It has no oracle a fresh agent can run.

NO-CLAIM: this review does not rank the 14 apply rows and does not edit the plan.
