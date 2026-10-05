# Fleet decision schema: where our agents decide, how often, and what is labelled (14 days, 2026-09-20 → 2026-10-04)

Read-only mining of live omp session logs and jev decision logs. No model calls. Every count below comes
from a command in **Reproduce** and is keyed in `decision-points.jsonl` (`count_source` names the exact keys
in `census.json`, `pass2..5.json`, `declogs.json`). INFERENCE marks anything not directly counted.

## Corpus

| Item | Value | Source |
|---|---|---|
| Session files (mtime < 14 d) | 3,024 files, 6.31 GB, 2,205,580 lines, **all parsed (no sampling)** | `find … -mtime -14` → `filelist.txt`; `census.json` meta |
| Session start dates | 2026-09-20 … 2026-10-04 (1 file from 09-15 still appended) | `session` row timestamps |
| Profiles (files) | default 1,621 · claude 611 · codex 555 · muse 171 · grok 48 · nv-deepseek-flash/nv-glm/nv-glm-flash/nv-kimi 4 each · agy 1 · omp-test 1 | census meta |
| Repos (files, by session cwd) | jev 1,685 · control-plane 330 · clutterfreespaces.ios 270 · omp-test 250 · uds 210 · localbench 190 · tmp 86 · ~/.local 3. **grokbot: 0 sessions in window** | census meta |
| Subagent session files | 1,468 (nested under a parent session dir) | `c:subagent_session_file` |
| jev decision logs | 26 files in `~/.local/state/jev/`, row counts per file in `declogs.json` | `declogs.py` |
| cass | `cass health` = `rebuilding`, index stale, lexical-only (semantic needs consent). One probe `cass search "that's wrong" --robot --limit 5` returned `total_matches` 40,982 in 37.7 s: lexical OR-matching, not a label count. **cass contributed no counts** | commands below |

Caveat: sessions are live; passes ran minutes apart, so a few counts drift by ≤ 3 between passes (e.g. todo nudges 2,106 vs 2,107). Row shapes are read with the two-shape `readRow` logic of `kit/src/client.ts:639-663` (`census.py:read_row`).

## Layers, derived from row and tool types actually present

17 row types, 15 custom types, 24 custom-message types, 36 tool names, 369,876 tool calls, 19,717 tool errors (`census.json`).

| Layer | Evidence in the logs (14 d) |
|---|---|
| L01 prompt intake | `role:user` 19,052 (human/other 14,939 · conductor dispatch 2,510 · subagent assignment 1,460 · system-wrapped 143); auto-thinking judge calls 7,610; `thinking_level_change` 4,201; `model_change` 3,146 |
| L02 planning | `todo` 14,744 calls (init 1,895 · done 9,157 · block 1,647); `mode_change` 2,178 (goal 2,164); `mid-run-todo-nudge` 2,106; `todo-error-reminder` 392 |
| L03 skill/rule load | `read skill://` 7,795; `jev-skill-hint` 954; `ttsr_injection` 6,588 + `ttsr-injection` msg 1,366; developer `rule_violation` 683; TTSR judge calls 7,349; `kit-guard` 501 |
| L04 tool selection | bash 117,642 · read 81,305 · eval 71,995 · write 23,275 · edit 23,030 · grep 16,309 · todo 14,744 · hub 8,389 · wait 4,807 · find 2,379 · glob 2,320 · yield 1,883 · web_search 833 · task 569 · ask 286 |
| L05 tool call (pre-exec gates) | guard-rule decisions 146,873 · dcg 87,608 · rch-lane 86,227 · harm-rule 35,072 (codex only); `gate-observe.jsonl` 39,279 |
| L06 tool result | toolResult 369,870; spilled 26,592; shaken 73,088 (jev only); `read artifact://` 4,329; `find` judge calls 41,002; `lsp-late-diagnostic` 699; `injection-shadow.jsonl` 19,250 |
| L07 memory | `ee-task-context` 1,126; `xd://recall` 187; `xd://retain` 101; `read memory://` 117; `memory-filter.jsonl` 39,179 |
| L08 compaction | 1,665 (remote 1,074 · snapcompact 583 · handoff 7 · soft 1) |
| L09 delegation | `task` 569 calls → 1,051 agents (task 802 · scout 144 · reviewer 59 · zeststream-reviewer 21); 1,468 subagent files |
| L10 stop/continue | stopReason stop 16,202 · aborted 5,212 · error 969 · length 17; smart-stop judge calls 8,009; `session-stop-continuation` 2,829 (jev only); `session_exit` 3,212 |
| L11 review/verification | `git diff` 7,169; test runs 3,310; builds 3,962; jev-review decisions 3,334; reviewer subagents 80 |
| L12 close/commit/push | `git commit` 4,425 · `git push` 2,617 · `br close` 677 · `br create` 714 · `br update` 1,605 · revert 7 · reset --hard 6 · restore 165 · deploy 71 |
| L13 fleet coordination | Agent Mail send 2,146 · fetch_inbox 1,472 · reservations 1,897 · conflict checks 1,668; `irc:incoming` 2,096; `write agent://` 1,047; `ntm` 6,132; `launch-completion` 1,052; `fleet-jev-shadow.jsonl` 4,248 |

## The schema: 65 decision points over 13 layers

Class: **a** ALREADY-CLASSIFIED (a jev surface or omp native judge/rule decides it today) · **b** CLASSIFIABLE-WITH-LABELS
(an outcome label exists in the logs and was counted) · **c** CLASSIFIABLE-NEEDS-LABELS · **d** NOT-CLASSIFIABLE.
"Labels" counts only **outcomes** (what happened after the decision), never the decision records themselves
(e.g. 1,096 dcg blocks and 4,178 guard fires are decisions, so their label count is 0).
Totals: a 23 · b 10 · c 16 · d 16.

| Layer | Decision | Type | Occ. 14 d | Outcome labels | Class | Existing surface |
|---|---|---|---|---|---|---|
| L01 | effort/thinking level for this prompt | choice | 7,610 | 0 | a | omp native judge auto-thinking (Jev), 5 profiles |
| L01 | prompt source: human vs conductor dispatch vs subagent assignment vs system-wrapped | rule | 19,052 | 0 | d | none (structural) |
| L01 | prompt stage/intent (plan, build, review, ops, question) | choice | 17,449 | 0 | c | none live |
| L01 | model/profile for this session | choice | 3,146 | 0 | c | none (jev-t5jk deferred covers subagent tier only) |
| L01 | did the user accept the last final answer (correction after answer) | noul | 7,536 | 31 | c | none |
| L02 | plan first (todo init) or act | noul | 1,895 | 0 | c | none |
| L02 | nudge: are open todos stale | rule | 2,106 | 453 | b | omp native mid-run-todo-nudge (rule) |
| L03 | which skill fits this prompt (hint) | choice | 3,492 | 225 | a | jev-skill-hint extension (declared PARKED/OFF, still firing: jev-35sg) |
| L03 | veto this skill load | noul | 433 | 0 | a | skill-veto shadow (jev-wbel) |
| L03 | which skill to read (agent-initiated skill:// read) | choice | 7,795 | 0 | c | none |
| L03 | does a TTSR rule apply to this stream (judged rules) | noul | 7,954 | 722 | a | omp TTSR + Jev judge (7,349 judge calls) |
| L03 | AGENTS.md changed on disk: reload | rule | 501 | 335 | d | kit-guard (rule) |
| L04 | locate with find vs grep vs glob | choice | 21,008 | 1,250 | b | rule text only (jev-kvcc deferred) |
| L04 | shell used where a specialized tool exists | rule | 117,642 | 0 | a | TTSR rules (regex) |
| L04 | poll (sleep loop) vs async/wait | rule | 17,125 | 0 | d | system-prompt rule only |
| L04 | ask the human vs answer from tools | noul | 286 | 42 | c | none |
| L04 | go to the web vs stay local | noul | 3,448 | 0 | c | none |
| L05 | block this bash command (dcg) | rule | 87,608 | 0 | a | dcg bridge (deterministic, blocking) |
| L05 | is this command risky (observe cascade) | noul | 39,279 | 0 | a | gate cascade nimble→Jev (observe only) |
| L05 | guard rule fires (grep-as-proof, stage-all, commit-backtick) | rule | 146,873 | 0 | a | omp-guard-rule extension |
| L05 | harm rule (codex profile) | noul | 35,072 | 0 | a | omp-harm-rule (codex profile only) |
| L05 | rch lane bind allow/deny | rule | 86,227 | 0 | a | rch-lane-bind bridge (rule) |
| L05 | will this edit apply (tag fresh, lines displayed) | rule | 23,030 | 3,022 | d | omp edit tool (structural) |
| L05 | will this bash command fail | noul | 117,642 | 8,932 | d | none (forecast) |
| L06 | is this tool result an injection | noul | 19,250 | 0 | a | Jev injection screen, annotate-only |
| L06 | is this web result unsafe to show | noul | 585 | 0 | a | web screen (withhold external only) |
| L06 | which web result to open first (rerank) | choice | 57 | 0 | a | websearch rerank (OFF) |
| L06 | rank find candidates (top passage/file) | choice | 41,002 | 421 | a | omp native judge on find (Jev) |
| L06 | long result: keep inline, spill/summarize, or drop (shake) | choice | 99,680 | 4,329 | b | omp spill/shake (size rule); jev-dau5 lever in progress |
| L06 | repeat read of an unchanged file (dedup) | noul | 36,827 | 20,388 | b | read-dedup shadow (566 rows: would-skip 216) |
| L06 | after a bash error: identical retry vs change vs move on | choice | 8,948 | 5,144 | b | none |
| L06 | after an edit error: re-read first vs re-edit | choice | 3,022 | 1,500 | b | none |
| L06 | is this late LSP diagnostic actionable | noul | 699 | 133 | b | omp lsp-late-diagnostic (always injects) |
| L06 | is the agent in a tool-call / thinking loop | rule | 16 | 0 | a | omp native loop redirect (rule) |
| L07 | is this recalled memory relevant now | noul | 39,179 | 0 | a | memory filter (Jev drop; enforce switch absent: jev-08hr) |
| L07 | inject task memories at prompt (ee-task-context) | noul | 1,126 | 0 | c | ee hook (rule) |
| L07 | recall now (agent-initiated recall / cass / memory read) | noul | 720 | 0 | c | none |
| L07 | what to retain | noul | 101 | 0 | d | none (generation) |
| L08 | when to compact | rule | 1,665 | 0 | d | omp compaction (rule) |
| L08 | what summary text to keep | noul | 1,665 | 0 | d | none (generation) |
| L08 | which previously read files to keep pinned through compaction | choice | 1,577 | 1,385 | b | none |
| L09 | delegate to subagents or do inline | noul | 569 | 0 | c | none |
| L09 | which agent type per subtask | choice | 1,051 | 7 | c | none |
| L09 | which model tier per subtask | choice | 1,051 | 0 | c | none (jev-t5jk deferred) |
| L09 | accept the subagent's result | noul | 1,691 | 32 | c | none |
| L10 | promise-then-stop: should the turn continue | noul | 8,009 | 0 | a | omp native smart stop (Jev) |
| L10 | continue after stop (mission/goal continuation) | rule | 2,906 | 0 | a | session-stop-continuation (jev) / goal mode |
| L10 | user interrupt / abort | rule | 5,385 | 0 | d | none |
| L11 | is this diff reviewable | rule | 3,334 | 0 | a | omp-jev-review gate |
| L11 | diff review verdict (behaviour/boundary) | noul | 25 | 0 | a | omp-jev-review Jev score |
| L11 | claim/close without evidence | noul | 1,364 | 69 | a | TTSR kit rules (claim-without-evidence retired R130) |
| L11 | which tests to run / will this diff break a test | noul | 7,272 | 1,214 | d | none (forecast; V8 deferred) |
| L11 | is this review finding new or a repeat | choice | 195 | 0 | c | conductor judgement |
| L12 | commit now / is the staged set right | noul | 4,425 | 466 | b | guard-rule stage-all/commit-backtick |
| L12 | push now | rule | 2,617 | 234 | d | none |
| L12 | close this bead | noul | 677 | 117 | b | br policy + TTSR kit-close rules |
| L12 | is this new bead a duplicate | choice | 714 | 0 | d | none |
| L12 | undo: revert / reset / restore | rule | 178 | 0 | d | dcg blocks destructive forms |
| L12 | deploy | rule | 71 | 0 | d | none |
| L13 | pane state: idle / working / no-agent | choice | 4,248 | 0 | a | fleet watcher (STOPPED since 2026-10-04) |
| L13 | idle worker needs a human: page pane 1 | noul | 60 | 0 | a | fleet watcher |
| L13 | dispatch: which bead to which agent | choice | 4,667 | 0 | c | fleet-router (11 rows); omp-kit owns idle dispatch |
| L13 | incoming peer/IRC message: act or ignore | choice | 3,568 | 0 | d | none |
| L13 | file reservation conflict | rule | 3,565 | 0 | d | agent mail |
| L13 | background job: keep, cancel, restart | choice | 901 | 0 | c | none |

### What the outcome labels are (deterministic, all counted)

| Label | Definition | Count |
|---|---|---|
| spill/shake read-back | `read artifact://…` calls; spilled artifact ids later read in the same session | 4,329 reads; 354 of 1,518 ids |
| redundant repeat read | repeat `read` of a path with no edit/write/bash/eval naming the file since the prior read | 20,388 of 36,844 (16,456 after a write). INFERENCE: ranged reads of different windows count as repeats |
| bash-error recovery outcome | isError of the next bash call after a failed one | identical retry ok 245 / err 76; changed ok 4,142 / err 681; no bash next 3,592 |
| edit-error recovery outcome | within 2 calls: re-read 1,407 vs re-edit 1,529; re-edit outcome ok 1,281 / err 219 | as stated |
| locate follow | next call after `find` is `read` 1,250 of 2,128; `find-rank.jsonl` next calls touched a returned hit 421 / 786 | pass3; one-liner below |
| compaction re-read | a `details.readFiles` file read again within 30 calls after compaction | 1,385 of 1,577. INFERENCE: some are routine |
| TTSR re-fire | same rule fires twice+ in one session (non-compliance proxy) | 722 of 1,568 (session, rule) pairs |
| skill hint followed | hinted skill later read via `skill://` | 225 of 954 in-session hints |
| todo nudge followed | `todo` call within 3 calls | 453 of 2,106 |
| LSP late acted on | same file edited within 3 calls | 133 of 699 |
| commit outcome | commit isError 436; hook reject 23; revert 7 | census |
| bead close outcome | `br close` refused/error text 69; isError 48 | census |
| user correction | regex on the next human turn after a final answer | 31 of 7,536 (floor; recall unchecked) |

## Top 10 by occurrences × label availability

Rule: `score = occurrences_14d × avail`, `avail = 1.0` if outcome labels ≥ 100, `0.5` if 30–99, `0.25` if 1–29, else 0 (`gen.py`).

Strict ranking (all classes):

| # | Layer | Decision | Occ. | Labels | Class |
|---|---|---|---|---|---|
| 1 | L05 | will this bash command fail | 117,642 | 8,932 | d (forecast) |
| 2 | L06 | long result: keep inline, spill/summarize, or drop | 99,680 | 4,329 | b |
| 3 | L06 | rank find candidates | 41,002 | 421 | a |
| 4 | L06 | repeat read of an unchanged file (dedup) | 36,827 | 20,388 | b |
| 5 | L05 | will this edit apply | 23,030 | 3,022 | d (structural) |
| 6 | L04 | locate with find vs grep vs glob | 21,008 | 1,250 | b |
| 7 | L06 | after a bash error: identical retry vs change | 8,948 | 5,144 | b |
| 8 | L03 | does a judged TTSR rule apply | 7,954 | 722 | a |
| 9 | L11 | which tests to run / will this diff break a test | 7,272 | 1,214 | d (forecast) |
| 10 | L12 | commit now / is the staged set right | 4,425 | 466 | b |

Classifier-actionable ranking (excluding NOT-CLASSIFIABLE), the list that should drive work:

| # | Layer | Decision | Occ. | Labels | Class | Cheapest baseline to beat |
|---|---|---|---|---|---|---|
| 1 | L06 | long result keep / spill / drop | 99,680 | 4,329 | b | size + tool-name threshold |
| 2 | L06 | rank find candidates | 41,002 | 421 | a | BM25 / grep order |
| 3 | L06 | repeat-read dedup | 36,827 | 20,388 | b | path + no-intervening-write rule |
| 4 | L04 | locate tool choice (find vs grep) | 21,008 | 1,250 | b | "find first" rule text |
| 5 | L06 | bash-error recovery (retry vs change) | 8,948 | 5,144 | b | block identical retry (but 245 / 321 identical retries succeeded) |
| 6 | L03 | judged TTSR rule fires | 7,954 | 722 | a | the rule's regex trigger alone |
| 7 | L12 | commit readiness | 4,425 | 466 | b | guard stage-all + hook result |
| 8 | L01 | user accepted last answer | 7,536 | 31 | c | the correction regex |
| 9 | L03 | skill hint for this prompt | 3,492 | 225 | a | silence |
| 10 | L06 | edit-error recovery (re-read vs re-edit) | 3,022 | 1,500 | b | always re-read on stale tag |

Next: todo-nudge actionability (2,106 / 453), compaction file pinning (1,577 / 1,385), LSP late actionability (699 / 133), bead close readiness (677 / 117).

**Biggest volume with zero outcome labels** (decision volume is not label availability): gate observe 39,279; memory relevance 39,179; injection screen 19,250; prompt stage 17,449; smart stop 8,009 (decisions not even persisted); skill read 7,795; auto-thinking 7,610; dispatch 4,667; pane state 4,248.

## NOT-CLASSIFIABLE (16) and why

| Why | Decision points |
|---|---|
| Structural: code already decides exactly | prompt source (prefix); AGENTS.md reload (mtime); poll vs wait (`\bsleep\s+\d`); edit apply (tool's tag check: 3,022 errors are the tool working); when to compact (token threshold); file reservation conflict (glob overlap); push (git decides; 65 rejects) |
| Forecast, label not in the input tokens | bash failure (8,932 errors, but ECOSYSTEM sec 3: retry .444 vs majority .556); diff breaks a test (1,214 failed test/build runs; diff-risk AUC .377) |
| Human decision | user interrupt/abort (5,385: a label *source* for other rows); undo (178); deploy (71) |
| Generation | compaction summary text (keep 0/32); what to retain |
| State outside the text | incoming peer message act-vs-ignore (.704 vs .75 bar); duplicate bead at create (abstain .678 beats Jev .370) |

## What jev's bead graph is missing compared with this schema

Open graph: 99 non-closed beads (48 open, 34 deferred, 13 in_progress, 2 blocked, 2 in_review) from `.beads/issues.jsonl`; keyword map in Reproduce.

1. **The `classifier` families do not cover the layer with the most labelled decisions (L06 result handling).** `jev-b35c.16/.17` cover route, rank, verify, score, gate, screen, diff, memory, watch, effort. There is no family for result-size (keep/spill/drop), dedup, recovery, or pinning, the four L06/L08 rows with 4,329 / 20,388 / 6,644 / 1,385 outcome labels. Only `jev-dau5` (lever, in progress) touches one of them, and it uses its own 3-probe "referenced-later" label, not the direct `artifact://` read-back (4,329) counted here.
2. **No bead for repeat-read dedup.** `read-dedup-shadow.jsonl` runs (566 rows), but the open graph has 0 beads matching "dedup"; 20,388 redundant repeat reads are already labelled.
3. **No bead for error recovery.** Bash: 337 identical retries, 245 succeeded, so a "block identical retry" rule would be wrong 76% of the time. Edit: 219 / 1,500 re-edits without a re-read failed again. 0 open beads.
4. **Locate-tool choice is deferred while the fleet ignores the rule.** `find` is 2,379 of 18,688 find+grep calls (12.7%) against `jev-kvcc`'s own ≥ 40% bar; `jev-kvcc` is deferred.
5. **"route has no organic traffic" (ECOSYSTEM row 1) is contradicted by routing-shaped decisions** with organic volume: prompt stage 17,449, locate tool 21,008, subagent type 1,051, session model 3,146. Only `jev-t5jk` (P3, deferred) touches routing.
6. **Delegation (L09) is unplanned.** 1,051 spawned agents, 1,468 subagent sessions, no outcome label beyond 32 error yields and 7 task errors. Only `jev-t5jk`.
7. **Commit/close readiness (L12) has labels and no bead.** 436 failed commits, 23 hook rejects, 69 refused closes, 191 stage-all fires; 0 open beads match. INFERENCE: "git writers" may be omp-kit's ground (ROADMAP "Not in the mission"), so this may belong to omp-kit, not jev.
8. **omp-native injections have no value receipt.** `mid-run-todo-nudge` is followed 453 / 2,106 times and `lsp-late-diagnostic` acted on 133 / 699; `jev-mvvh` (economic ledger) covers jev surfaces only.
9. **Judged TTSR rules carry an unused compliance label.** 722 / 1,568 (session, rule) pairs re-fire; `jev-pn7b` only covers retired rules still firing.
10. **Compaction file pinning is a separate, labelled decision.** Only `jev-g2uv` (turn keep/drop, deferred, a refuted family) exists. File pinning has 1,385 / 1,577 labels.
11. **Label persistence, not models, blocks the high-volume a-rows.** Smart stop's 8,009 calls persist no decisions (`jev-nwo1` in progress). Auto-thinking's 7,610 have no outcome (`jev-5ai4`, `jev-2fz6` deferred). The 5,212 aborts and 7,536 post-answer human turns go unused as outcome sources.
12. **Rollout skew.** These surfaces fire in one repo or one profile only: skill hint (jev), jev-review (jev, tmp), session-stop-continuation (jev), harm-rule (codex profile), shaken results (jev). The fleet watcher (4,248 rows, 09-25/26 only) is STOPPED, and no open bead restarts it (`jev-06wt` is heartbeat/observability).

## Reproduce (commands run, in order)

```
cd ~/.omp && find agent/sessions profiles/*/agent/sessions -name '*.jsonl' -mtime -14 -type f | sed "s|^|$HOME/.omp/|" > filelist.txt   # 3,024
nice -n 10 python3 census.py filelist.txt census.json      # 22 s, 8 workers: row/tool/custom/kind counts + per-repo/profile
nice -n 10 python3 declogs.py declogs.json                  # 26 jev decision logs
nice -n 10 python3 pass2.py filelist.txt pass2.json        # field detail: dcg reasons, hub ops, yields, edit/bash error classes
nice -n 10 python3 pass3.py filelist.txt pass3.json        # guard_fire classes, exit codes, next call after find
nice -n 10 python3 pass4.py filelist.txt pass4.json        # follow/outcome labels after triggers
nice -n 10 python3 pass5.py filelist.txt pass5.json        # repeat reads with/without intervening write
python3 -c '...find-rank.jsonl: hits ∩ nextToolCalls[].touched' # 421/786 touched a hit
python3 -c '...open beads keyword map over .beads/issues.jsonl'  # 99 non-closed beads
cass health --robot; cass search "that's wrong" --robot --limit 5
python3 gen.py > ranked.txt                                  # writes decision-points.jsonl (65 rows) + ranking
```

All scripts and their JSON outputs are in this folder. No raw transcript text is copied into any output.
