# CASS / Agent-Mail alpha approaches — 2026-09-20

**Status:** DESIGN catalog. **Unpromoted.** **`promoted = 0`.** Level: `[pending]`.
**Lane:** offline design. **Class this file may claim:** none — these are mines to
run on Studio, not measurements.
**This file is not a harness, not a live receipt, not a STATUS.tsv row.**

**Mission this unit serves:** validate Jev → build tools from what survives →
**liven omp surfaces with them** → dogfood → share. This packet is stage one
(validate) only: it licenses which *real-store* mines to run next, or it dies.

**Oracle for the process (not a score):** `Dicklesworthstone/skillranker`
`tests/eval/evaluation_policy.v1.json` as mirrored at
`work/skillranker-eval/contract/evaluation_policy.v1.json`
(`frozen_contract_not_evidence`, pulled `@ bb52b8f25`).
**Oracle for cass hit fields:** public
`Dicklesworthstone/coding_agent_session_search` SKILL.md *Response Shapes*
(same pin used by `jev-task-tests-cass-20260920.md`). **Not** a local
`--robot` dump — `command -v cass` is absent on this VM.
**Oracle for mail columns:** `Dicklesworthstone/mcp_agent_mail@ac4966c`
`models.py` + README (same pin as `jev-task-tests-agent-mail-20260920.md`).
**SDK fields:** `docs/demos/SDK-SURFACE.md`. There is no `.distribution`.

---

## Why this exists (and why it is not PR #31 / #32)

PR #31 baked the frozen toolcall scorer (`n=7846`, always-abstain
**0.212210043**, isError-only **1.495284221** LOSE).
PR #32 mined **that same file**: `sess` prefixes, `args` tokens/regex,
`isError` × outcome, `args` length → rule-list + logistic, CV
`mean_loss=0.197426005` BEAT (`toolcall-multi-feature-judge-20260920.md`,
`work/jev-real-corpus-eval/mine_features.py`).

Those numbers are **closed on that corpus**. Re-running `sess` / `args` /
`isError` / `args_len_*` on CASS or mail is not a new mine; it is a
selector≡claim fail (those columns are not in those stores).

This catalog names **≥20 novel mines** against the two stores this cloud VM
**cannot see**:

| Store | Studio path (reported, not opened here) | Scale (reported) |
|---|---|---|
| CASS | `/Volumes/ZestData/cass-data/agent_search.db` | ~59.8k conv / ~5.2M msgs |
| Agent Mail | live `am` / Git-backed `messages/YYYY/MM/*.md` | ~6510 messages |

**Cloud VM fact, measured this pass:** `ls /Volumes/ZestData` → absent;
`command -v cass` → absent; `command -v am` → absent. Every measure sketch
below is a **Studio command**, not a claim that it ran here.

The already-shipped **task-test designs**
(`jev-task-tests-cass-20260920.md`, `jev-task-tests-agent-mail-20260920.md`)
are authored `diagnostic_synthetic` *judge contracts*. This file is the
**dig**: how to extract labelled rows from the real stores so a later judge
has a non-authored Y. A contract is not a mine. A mine that authors its own
Y is R28 / R44 again.

---

## Jeff patterns reused (cite, do not re-derive)

Stolen from skillranker EVAL + this lane's measured copies. Adopt the
mechanism; do **not** assert their 0.167 / 0.800 / 0.833 as ours.

| Pattern | What it binds here | Citation |
|---|---|---|
| **`__none__`** | Every advisory Choice offers a real abstain option. Ties against it abstain. | `jev-juice-surfaces-map-20260920.md:94-95`; `work/skillranker-eval/score.mjs` `NONE` |
| **0/1/2 loss** | False abstention = 1; wrong pick / needless / unavailable = 2. | `evaluation_policy.v1.json:58-72`; rationale `:70-71` |
| **Always-abstain control** | Required. A loss that charges only wrong *emitted* suggestions is invalid. | `always_abstain_counterexample_required: true`; `skillranker-eval/README.md:35` |
| **Planted RED** | Each mine names a plant that must trip (selector hole, empty-success, badge-echo). | CASS-08 / AM-TT-05 plants; `skillranker-eval` `wrong-skill` |
| **`diagnostic_synthetic` cannot promote** | Authored fixtures / this catalog **cannot** move `promoted`. | `evaluation_policy.v1.json:53-56`; R28; R44 |
| **Prevalence gates** | State \(\pi\) beside every score. At 0.016% even a 0.750 separator is ~1:2300. | `math-and-next-level-20260919.md:75-99` |
| **VOI vs cheap baseline** | \(\mathrm{VOI}(Z)=\mathbb{E}[L(a_0,Y)]-\mathbb{E}[L(a(Z),Y)]-c_{\text{call}}\). If \(a(Z)=a_0\), VOI \(\le -c_{\text{call}}\). | same file `:532-556` |
| **Outcome co-presence** | Session co-presence ≠ id-join (10 sessions co-present, 1 id-join). | `INTEGRATIONS.md`; juice map Mode G |
| **Dig-vs-invent** | `__none__` = invent; a hit id = reuse / `cass view`. First-hit always digs. | cass task-tests CASS-04/05; juice map Mode F |
| **Selector ≡ claim** | Score the Choice the product emits. Do not invent a second `helpful` noul gate (0.750→0.167). `requireKey` before any absence. | juice map `:102-103`; `dont-give-up.md` G6 |

**Hard rules copied, not optional:**

1. One Choice. Diagnostic Score/Noul may export; they never gate.
2. Always-abstain must be printed on the same split as the candidate.
3. Feasibility arm (perfect judge) must score mean loss 0, else **BLOCKED-HARNESS**.
4. `unavailable` is loss 2 on an attempted case, never a pass.
5. Observe-only. No `{block:true}`. No `send_message`. No `am send`.
6. Off-PATH / missing volume ⇒ `LIVE: NOT_RUN` / `STORE: UNREACHABLE`, not “cass missing.”

---

## How to read an approach card

Every card has the same fields. A card missing a cheap control or a Y source
is not a mine.

| Field | Meaning |
|---|---|
| **Store** | `cass` / `mail` / `both` |
| **Jeff steal** | Which pattern above is load-bearing |
| **Measure** | Studio command / sketch. Introspect schema first. Refuse if keys moved. |
| **Label / Y** | Where the independently judged set comes from. Empty Y = invent / log-only. |
| **Control** | Always-abstain **and** the cheap baseline that might kill VOI |
| **Alpha hypothesis** | What would have to be true for a later Jev judge to earn a paid call |
| **NO-CLAIM** | Exact limit of this card. Catalog ≠ measurement. |

**Identity lock (when a mine runs):** hash the export, print n / class counts /
sha256 **before** any judge. A 10-row authored substitute is **REFUSED** (R44).

**Not these features (PR #32 closed set):** `sess_repo_*`, `sess_exact_*`,
`args_len_lt_100`, `args_len_eq_200`, `cmd_*` token regexes, `isError`-only,
logistic / rule-list on `toolcall-corpus-frozen.jsonl`. Do not port them.

---

## Approaches (n=24)

### A01 — Thread supersession vs `reply_to`

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Selector ≡ claim (`reply_to` is a parent edge, not a cancel — `models.py` `#188`); planted RED; `__none__` |
| **Measure** | On Studio: export threads with ≥2 messages. `jq` group by `thread_id`. Flag rows whose body matches `/supersede\|ignore previous\|IGNORE \d+/i` **and** rows whose only link is `reply_to`. Score a Choice `{keep_as_current, duplicate_ignore, conflict_unresolved, __none__}`. |
| **Label / Y** | Human (or later-pane) reservation that actually landed: which message's `path_pattern` was reserved. If neither, Y empty. |
| **Control** | Always-abstain. Cheap: `reply_to != null ⇒ keep_as_current` (must RED on a duplicate that only replies). Cheap-2: `importance==high ⇒ keep_as_current`. |
| **Alpha hypothesis** | Real threads contain “ignore 4104” without a `supersedes` column. A `reply_to`-only rule will systematically mis-label duplicates as current. Jev earns a seat only if that residual survives both cheap rules **and** \(\pi\) of true supersession is high enough that false abstention is cheaper than needless keep. |
| **NO-CLAIM** | AM-TT-04 is an authored plant, not this mine. No `supersedes` column exists at `ac4966c`; do not invent one. |

### A02 — Human-overseer high-badge echo cost

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | VOI vs cheap baseline; prevalence gates; R42.3 (re-asking Jev for a forced-high column loses cost-benefit) |
| **Measure** | `am inbox` / frontmatter dump. Contingency: `from == HumanOverseer` × `importance` × (`ack_required` / body-has-new-instruction). Print \(\pi(\text{high})\), \(\pi(\text{high} \mid \text{overseer})\), \(\pi(\text{new work} \mid \text{high})\). |
| **Label / Y** | `{urgent_work, overseer_noise, __none__}` judged from whether a later message in-thread names a new reservation / bead, **not** from the badge. |
| **Control** | Always-abstain. Cheap B1: `resource://views/urgent-unread`. Cheap B0: `from==HumanOverseer && !ack_required ⇒ overseer_noise`. |
| **Alpha hypothesis** | Overseer force-high makes `importance` a near-constant on the human path. If B0 matches Y on both the cadence pair and the “STOP, rotate the key” pair, \(\mathrm{VOI}\le -c_{\text{call}}\) and the family is a cost-benefit kill **before** any Jev call. |
| **NO-CLAIM** | Do not treat `importance` as Y. Do not page a human on every high. First number is prevalence, not a judge score. **Run this first on Studio** (columns exist today). |

### A03 — Cross-session skill-reuse hit rank

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | `__none__`; dig-vs-invent; selector ≡ claim (`hit_id` = `source_path#line_number`, not `title`) |
| **Measure** | For each later session whose first user turn names a *skill* (`jsm`, `dont-give-up`, `skillranker`, house skill), `cass search "<skill> <hole>" --robot --limit 5`. Rank hits. Join to whether the pane ran `cass view` on a Y hit before scaffolding. |
| **Label / Y** | Hits whose `source_path` is the session that *first shipped* that skill's worked command (lane receipt, not a marketing snippet). Empty Y if the hole is new. |
| **Control** | Always-abstain (always invent). First-hit / BM25-argmax. Recency-in-same-workspace. |
| **Alpha hypothesis** | Cass `score` rewards shared tokens (“skill”, “robot”, “TUI”) on docs *about* cass. A later Jev Choice can beat first-hit the way CASS-04 is built — **only** on a non-authored dump. If first-hit already beats always-abstain, the seat shrinks to empty-success plants. |
| **NO-CLAIM** | Not skillranker's 0.167 on *their* 12-case skill roster. Not `omp-jev-rerank` (grep/glob, does not reorder). |

### A04 — Dig-vs-invent on cass snippets

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Dig-vs-invent; 0/1/2; always-abstain; empty-success refusal |
| **Measure** | Sample live holes from later user turns (first 200 chars). Run the **lane** command `cass search "<hole>" --robot --limit 5` (never `--workspace <project>`, never `--fields minimal` as the judge payload). Decision `{dig, invent}` via Choice over hit ids ∪ `{__none__}`. |
| **Label / Y** | Did the pane's *next* non-search edit copy a byte span from a viewed hit (reuse) or create a new path (invent)? Outcome is the edit, not the snippet. |
| **Control** | Always-`__none__` (invent-everything). Always-first-hit (dig-everything). Token-overlap ≥ k. |
| **Alpha hypothesis** | Rule 13 failure mode (nineteen clones untouched) is a **false invent**. If \(\pi(\text{nonempty Y})\) on real cass traffic is ≪ the authored 6/9, always-abstain wins and the paid ranker is ceremony. State \(\pi\) first. |
| **NO-CLAIM** | CASS-04/05 are plants. Opening a hit is not Y; **using** it is. Ground-truth “changed the next edit” is post-hoc and must be labelled by a non-author. |

### A05 — Ack SLA breach

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Outcome co-presence; 0/1/2; planted RED (reply exists ≠ ack) |
| **Measure** | For each `ack_required==true`, compute \(\Delta t = \mathrm{ack\_ts} - \mathrm{created\_ts}\) (or null). Bucket: acked-in-SLA / acked-late / never-acked. Join `thread_index` for any later message from the recipient (co-presence). |
| **Label / Y** | `{stuck_wait, handshake_complete, ack_without_send, __none__}`. Structural SLA (null `ack_ts` past threshold) is a **feature**. Y is whether the *sender's next message* is a chase vs a new bead. |
| **Control** | Always-abstain. Cheap: `ack_required && ack_ts==null ⇒ stuck_wait`. Plant: any-reply-exists ⇒ complete (must RED — INTEGRATIONS 10-vs-1). |
| **Alpha hypothesis** | The boolean `ack_required ∧ ¬ack_ts` is free and probably dominates (VOI kill). Jev is only in the running on “is this reply an ACK or a status ping.” If that residual's \(\pi\) is tiny, observe-and-log, do not call. |
| **NO-CLAIM** | SLA hours are not in the schema; pick a preregistered threshold **before** looking at the histogram, or the threshold is the judge. **Run this second on Studio.** |

### A06 — Phishing-in-band on the agent bus

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Planted RED; fail-safe `__none__`; 0/1/2 under-prices a miss (R42.2) — keep the table, forbid promotion |
| **Measure** | Scan bodies/subjects for `/Joshua said\|paste.{0,40}key\|TYPESAFE_API_KEY\|BYPASS_JEV\|ignore (the )?(rules\|AGENTS)/i` **and** a matched set of ordinary bead handoffs. Choice `{escalate_human_observe, actionable_work, coordination_chatter, __none__}`. |
| **Label / Y** | Independently: impersonation / secret-ask / safety-disable ⇒ `escalate_human_observe`. Real handoff with “Joshua said ship X” and **no** secret-ask ⇒ `actionable_work`. |
| **Control** | Always-abstain (under-prices the miss — record it). Cheap: `/Joshua said/` regex (must FP the plant). Cheap-2: `from==HumanOverseer` allowlist (overseer is a web composer, not a From: spoof). |
| **Alpha hypothesis** | Sibling-pane spoof is in-band; the bus authenticates registration, not intent. If real \(\pi\) is ~0, the family is a nag and gets uninstalled (healthy-path-silent rule). If \(\pi\) is measurable and the regex FPs ordinary “Joshua said,” Jev *may* earn a probe **after** both baselines. |
| **NO-CLAIM** | Not `jev-spam-eval` 0.9857 / 91.3% OOD (human SMTP ≠ agent bus). Do not copy those numbers. Do not put a key in a fixture. Do not send. |

### A07 — Reservation conflict co-presence

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Outcome co-presence; selector ≡ claim; show-human vs nag |
| **Measure** | Join `am file_reservations conflicts` rows to in-thread mail that *mentions* the same `path_pattern` within ±T. Print: conflict-only, mail-only, id-join, session-co-present-but-different-path. |
| **Label / Y** | `{show_human, wait_and_retry, agents_only, __none__}`. Y = `show_human` only when exclusive + unreleased + two writers name the same path **and** one of them is `EVAL.md` / paid-surface / irreversible. |
| **Control** | Always-abstain. Cheap: `/conflict\|EVAL.md/i` on subject (must RED when subject is stale and body is heartbeat — AM-TT-07 plant shape). Cheap-2: any exclusive reservation ⇒ show_human (nag). |
| **Alpha hypothesis** | The conflict **column** is free. Jev is only for “show a human vs wait.” If join yield is ~0 (dead `am` / unused reservations), the mine is `UNMEASURED`, not “no conflicts.” |
| **NO-CLAIM** | Co-presence of a reservation row and a mail row is not a conflict. Do not invent `context.dcgVerdict`. |

### A08 — Prevalence of wrong-selector language

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Selector ≡ claim; prevalence gates; G6 (8–10× wrong-selector in one day) |
| **Measure** | `cass search "no such field" --robot --limit 50` and sibling queries (`"keys present"`, `"requireKey"`, `".distribution"`, `"customType.data"`). Count sessions whose snippet claims absence **without** dumping `keys()`. |
| **Label / Y** | `{wrong_selector, true_absence, __none__}`. Y = `wrong_selector` when a later message in the **same** `source_path` finds the field (the eighth / ninth pattern). |
| **Control** | Always-abstain. Cheap: snippet matches `/no (such )?(field\|key)/i ⇒ wrong_selector` (will FP true absence). |
| **Alpha hypothesis** | If \(\pi(\text{wrong_selector})\) among absence-claims is high, a pre-scaffold cass+Jev ranker that prefers `requireKey` receipts beats invent-a-missing-field. If most absences are real, the cheap regex is a nag. |
| **NO-CLAIM** | Searching this tree for `noul` matches docs *about* noul. Use the high-entropy control `zzzz_cannot_exist_9c42` and expect 0 hits. Cass `score` is not `probabilities`. |

### A09 — Retransmit / token waste across cass sessions

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | VOI vs cheap baseline; dig-vs-invent; cost is part of validation |
| **Measure** | Cluster sessions by normalised first-user-turn (simhash / token set). For each cluster size ≥2, measure later-session prompt tokens spent *before* a `cass search` / `cass view`. Compare to clusters that searched first. |
| **Label / Y** | `{should_have_dug, fresh_hole, __none__}`. Y = `should_have_dug` when a prior session in-cluster contains a named VERDICT / decision envelope the later pane re-derived. |
| **Control** | Always-abstain (never flag retransmit). Cheap: cluster-size ≥2 ⇒ should_have_dug (will FP “same hole, new tree” repeatable workflows). |
| **Alpha hypothesis** | Retransmit is the Rule 13 cost in tokens, not in clones. If cheap clustering already flags the waste, Jev's only seat is “is this the *same* hole or a repeatable workflow that should keep Y nonempty.” |
| **NO-CLAIM** | Not the toolcall `args` length feature. Not `jev-retransmit-killer` unless that tree is re-read and its Y is this Y. Token counts from cass payloads are index-shaped, not billed-API-shaped. |

### A10 — Question-shape that precedes GOOD vs BAD

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Selector ≡ claim; prevalence; criteria-inversion (short question won; elaborated lost) |
| **Measure** | From cass user/assistant first turns, extract question shape: imperative vs interrogative vs “please advise” vs pasted stack-trace vs numbered plan. **Do not** use toolcall `sess` / `args` / `isError`. Join *within cass* to a later same-session verdict line (`VERDICT`, `offline-verified`, `NOT_RUN`, `promoted: false`). |
| **Label / Y** | `{leads_to_named_receipt, leads_to_retraction, __none__}` from *cass text*, not from the frozen toolcall GOOD/BAD. |
| **Control** | Always-abstain. Cheap: has-stack-trace ⇒ receipt (likely wrong). Cheap-2: message-length buckets (the PR #32 `args_len_*` analogue — **only** as a control we expect to lose or to be a VOI kill). |
| **Alpha hypothesis** | The lane already measured that elaborating a Jev *question* costs accuracy. The mine asks whether *human/agent ask-shape* in prior sessions predicts whether the session produced a citable receipt. If length-only matches the Choice, do not call Jev. |
| **NO-CLAIM** | This is **not** a second GOOD/BAD on `toolcall-corpus-frozen.jsonl`. Joining cass text to that file's `isError` is a PR #32 remix and is rejected (see § Rejected). |

### A11 — Mail → cass join on project path

| | |
|---|---|
| **Store** | both |
| **Jeff steal** | Outcome co-presence; selector ≡ claim; join yield is the first number |
| **Measure** | Join key candidates, in order: `mail.project_key` / `project_slug` ↔ cass `workspace`; `thread_id` (bead id) ↔ cass snippet / title tokens; `path_pattern` ↔ `source_path`. Print yield for each key: id-join / co-present / miss. Secret-scan the export before it touches git. |
| **Label / Y** | A pair is Y-positive only on **id-join** (same project + overlapping time window + shared bead id or reserved path). Co-presence alone is not Y. |
| **Control** | Always-abstain (no join). Cheap: string-equal `workspace == project_slug`. Plant: two panes in one tmux session, different project paths (must not join). |
| **Alpha hypothesis** | Without this yield number, every `both` mine is fiction. If id-join is much smaller than session co-presence (the observer↔bridge lesson), later both-store judges must fail closed, not impute. |
| **NO-CLAIM** | Cloud VM cannot compute this. Dead `am inbox` count:0 is `UNMEASURED`, not yield 0. **Run this third on Studio** — it gates A18. |

### A12 — Empty-success: `count>0` is not “already solved”

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Dig-vs-invent; planted RED (CASS-07); always-abstain *succeeds* on empty Y |
| **Measure** | Take cass envelopes with `count>0`, `exit 0`, `_meta.index_freshness.stale != true`. Grade whether any hit's snippet answers the *live hole that was queried*, not whether hits exist. |
| **Label / Y** | Empty when no hit is a first-party receipt for that hole (the invoice-number-cited-but-not-reproduced shape). Nonempty only when `cass view` would change the next edit. |
| **Control** | Always-pick-top-hit (must be loss 2 on empty-Y). `count>0 ⇒ ranked` (named RED). Always-abstain (loss 0 on these). |
| **Alpha hypothesis** | Playbook A will over-claim “cass found it.” If empty-success \(\pi\) is high, the cheapest ship is a **local** refusal (`count>0` ∧ zero Y-eligible), and Jev is optional. |
| **NO-CLAIM** | Authored 3/9 empty-Y is a property of plants, not of real cass traffic. |

### A13 — Advice-stale vs index-fresh

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Local eligibility before pay; diagnostic noul is **not** a gate |
| **Measure** | Hits with `_meta.index_freshness.stale==false` / `trust.stale` absent, whose `created_at` predates a *later first-party receipt* in the same workspace (e.g. skillranker `@3fe85c4` clone advice vs `work/skillranker-eval/`). |
| **Label / Y** | Gold = the later receipt's hit_id. Stale-top-hit is a near-miss and **must not** count as correct. |
| **Control** | Always-abstain. BM25-argmax. Local drop of `trust_tier=stale` (record which path ran). |
| **Alpha hypothesis** | Index-fresh ≠ decision-fresh. If local eligibility already drops `trust_tier=stale`, Jev never sees the trap and VOI is on the residual (aliases, missing `trust` on `--fields minimal`). |
| **NO-CLAIM** | Do not judge stale on `--fields minimal`. A second `cass view` may fill fields; until it does, the question is blind. |

### A14 — Workspace alias / moved-checkout residual

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Local eligibility first; residual Noul `same_project` only when the literal compare is blind |
| **Measure** | Collect `workspace` values; cluster by basename / inode-unaware path (`/Users/…/jev` vs `/projects/jev_playground` vs `/workspace`). Literal drop of `workspace ≠ cwd`. Remainder: missing `workspace` or alias. |
| **Label / Y** | Same git remote + overlapping bead ids ⇒ same project. Different remote ⇒ drop. |
| **Control** | Always-abstain. Cheap: string-equal workspace. Cheap-2: basename-equal (will join unrelated `jev` checkouts). |
| **Alpha hypothesis** | Literal compare is free and should run first. Jev `same_project` is only for the residual. If `--fields` omitted `workspace`, **refuse** to rank (selector plant), do not impute. |
| **NO-CLAIM** | Never add `--workspace <project>` to the lane search command (`dont-give-up-gaps.md:1098`). Workspace is a hit field. |

### A15 — CC-as-owner after steward-map residual

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Explicit resolution is local; Jev only when the steward is not machine-readable |
| **Measure** | Join `to[]` / `cc[]` to roster `task_description` and to Beads `steward:*` labels. Score routing Choice over roster ∪ `{__none__}`. |
| **Label / Y** | Who actually reserved the path named in the body (reservation table), not who is on `to[0]`. |
| **Control** | Always-abstain. Cheap: `to[0]`. Cheap-2: steward-map / `thread_id` → steward (if this matches Y on both the case and the body-dropped plant, Jev loses the family). |
| **Alpha hypothesis** | AM-TT-02 is the authored shape. On real mail, exact-id routing is common; the residual is “To: is the docs pane, body names the observer tree.” Measure residual \(\pi\) before budgeting a call. |
| **NO-CLAIM** | `to[]` is sender-asserted. A wrong To is not a schema error. |

### A16 — `thread_id` ≠ bead-id convention breach

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Selector ≡ claim; prevalence; Beads owns status, Mail owns the thread |
| **Measure** | Compare `thread_id` to subject `[<id>]` and to `.beads/issues.jsonl` ids. Rates: match / subject-only / thread-only / neither. |
| **Label / Y** | `{convention_ok, recoverable_from_subject, orphan_chatter, __none__}`. Orphan with actionable body is still actionable — do not empty Y because the join key is dirty. |
| **Control** | Always-abstain. Cheap: `thread_id == subject-capture`. Plant: heartbeat with a well-formed `[jev-x]` and empty work (Y empty). |
| **Alpha hypothesis** | If convention-breach \(\pi\) is high, a Jev join-fixer is tempting and probably wrong — a local parser on `[<id>]` is cheaper. Jev only if the body names a bead the headers do not. |
| **NO-CLAIM** | This lane's tip census of beads is not mail ground truth. Do not run `br` from a judge. |

### A17 — Same-query Y-flip across days

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Golden-regeneration reflex (forbidden); advice-stale; diagnostic ≠ promote |
| **Measure** | Repeat the same cass query string on two index snapshots (or `created_at` split). Align `hit_id`s. Flag rank-1 flips and Y-set flips. |
| **Label / Y** | Freeze Y **before** seeing the second snapshot (questions freeze first). A flip is a fact about the index, not a license to retune the question. |
| **Control** | Always-abstain. Cheap: “latest `created_at` wins.” |
| **Alpha hypothesis** | A moving cass index is the same shape as a moving `jev-latest`: a stale gold is *telling you something*. If Y flips often, do not promote a ranker trained on day-1 gold. |
| **NO-CLAIM** | Two snapshots authored by the scorer are not two days. Need Studio index history we did not write. |

### A18 — Mail ACK exists in cass but not in `ack_ts`

| | |
|---|---|
| **Store** | both |
| **Jeff steal** | Outcome co-presence; handshake completeness |
| **Measure** | After A11 yield > 0: find `ack_required && ack_ts==null` mail whose joined cass session contains an assistant/user line `ACK` / `reserved <path>` in-window. |
| **Label / Y** | `{stuck_wait, handshake_complete_off_bus, cass_ack_is_chatter, __none__}`. Off-bus complete is a **mail product hole**, not a Jev win by itself. |
| **Control** | Always-abstain. Cheap: mail columns only (A05). Cheap-2: any cass “ACK” token ⇒ complete (must RED on heartbeat). |
| **Alpha hypothesis** | Agents ack in-session and forget `acknowledge_message`. If this \(\pi\) is high, the cheap ship is an observe-only reminder, not a paid Choice. Jev only to separate “ACK. File reserved.” from “ACK. Standing by.” |
| **NO-CLAIM** | Requires A11. Until join yield is printed, this card is `PREPARED-NOT-MEASURED`. |

### A19 — Cass snippet reuse vs later edit delta (not isError)

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Dig-vs-invent; adoption ≠ usefulness; selector ≡ claim |
| **Measure** | After a `cass view` in session S, diff the next file write in S against the viewed snippet (longest common substring / token Jaccard). Threshold preregistered. |
| **Label / Y** | `{reused_verbatim, reused_structure, ignored_hit, __none__}`. `ignored_hit` after a high BM25 rank is the false-dig cost (loss 2 if we recommended it). |
| **Control** | Always-abstain. Cheap: Jaccard ≥ θ ⇒ reused. Plant: shared tokens “cass”/“robot” with no byte reuse. |
| **Alpha hypothesis** | This is the *usefulness* ledger skillranker still lacks (`src/` never reads `synthetic_cases`). A ranker that is adopted (viewed) but unused (no edit delta) is not juice. |
| **NO-CLAIM** | **Not** `isError` and **not** the frozen toolcall GOOD/BAD. Edit delta is not harm. Do not join this to PR #32 features. |

### A20 — Attachment / path selector plant in real mail

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Selector ≡ claim; planted RED (CASS-08 shape on mail) |
| **Measure** | Count messages with `attachments[]` missing `path`, or `body_md` that claims `local://` / `file:` without a resolvable path. `requireKey` on `{id, thread_id, from, subject}` before any grade. |
| **Label / Y** | Operational: `unavailable` if required keys missing. Relevance Y is **excluded** (unjudged), same as CASS-08. |
| **Control** | A harness that picks a row with no `id` **fails the plant**. Always-abstain is not the required control here — throw / `unavailable` is. |
| **Alpha hypothesis** | Real traffic may already contain the plant. If it does, the first ship is `requireKey`, not Jev. |
| **NO-CLAIM** | Do not fetch attachment bytes. Paths only. No secrets in the export. |

### A21 — Multi-pane reservation ping-pong

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Prevalence; healthy-path-silent; VOI |
| **Measure** | Threads where exclusive reservation of the same path flips ≥N times in Δt (release → reserve → conflict → release). |
| **Label / Y** | `{show_human, agents_only, __none__}`. Y = `show_human` only past a preregistered flip count **or** when the path is `EVAL.md` / `AGENTS.md`. |
| **Control** | Always-abstain. Cheap: flip-count ≥ N (no Jev). |
| **Alpha hypothesis** | If flip-count already separates, Jev is ceremony. If most ping-pong is polite ACK-and-yield, showing every flip is a nag that gets the seam uninstalled. |
| **NO-CLAIM** | Three agents share this tree; ping-pong is normal (`AGENTS.md` tail note). Do not treat “I did not touch that file” as a defect. |

### A22 — Same-agent vs other-agent cass reuse

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Dig-vs-invent; RULE 13 (“most likely solver is yesterday's pane”) |
| **Measure** | On A04's roster, split hits by `agent == live agent` vs other. Score whether Y concentrates in same-agent, other-agent-same-workspace, or other-workspace. |
| **Label / Y** | Same as A04 (edit-delta reuse), stratified. |
| **Control** | Always-abstain. Cheap: prefer same-agent. Cheap-2: prefer other-agent (the “don't trust your own prior wrong number” rule). |
| **Alpha hypothesis** | Cass indexes our own wrong numbers. Same-agent top-hits may be *our* inflated receipts (R28). If other-agent-same-workspace Y-rate is higher, the cheap ranker is “not me,” and Jev is residual. |
| **NO-CLAIM** | RULE 13's “yesterday's pane” is doctrine until this \(\pi\) is printed. |

### A23 — Draft-quality vs send-authority confusion rate

| | |
|---|---|
| **Store** | mail |
| **Jeff steal** | Binding is `log-only`; grade ≠ send (R42.1) |
| **Measure** | Observe `send_message` inputs (pre, observe-only) vs a rubric: bead prefix, path, ask, no secret-ask. Compare to whether the *human* would have sent (only if a later human edit of the same draft exists — rare). |
| **Label / Y** | `{needs_rewrite, ready_to_recommend_send, must_not_send, __none__}`. **Even on `ready_*` the action stays `draft_note`.** |
| **Control** | Always-abstain. Cheap: `ack_required==true ⇒ ready`. Cheap-2: length>0. Both must fail the plants. |
| **Alpha hypothesis** | If agents already send well-formed `[id]` mail, the grade is a nag. If they send `"update" / "working on it"` at high prevalence, a **local** rubric wins; Jev only for `must_not_send` residual (A06 overlap — do not double-count). |
| **NO-CLAIM** | A test that calls `send_message` on `ready_*` is a product bug, not a judge score. Zero send authority in this catalog. |

### A24 — Hits *about* cass, not solutions (lexical-trap prevalence)

| | |
|---|---|
| **Store** | cass |
| **Jeff steal** | Dig-vs-invent; BM25 ≠ judgment; planted top-hit RED |
| **Measure** | Queries that contain `cass` / `robot` / `TUI`. Fraction of top-1 hits that are AGENTS.md quotes or dont-give-up playbook text vs a worked `cass view` of a *solved hole*. |
| **Label / Y** | Gold = a session that *used* cass to solve a different hole. Docs-about-cass = near-miss, not correct. |
| **Control** | Always-abstain. First-hit / BM25 (must lose if the trap is real). |
| **Alpha hypothesis** | The authored CASS-04/07 traps are not evidence. If real top-1 for query `cass` is almost always doctrine, playbook A needs a **local** filter (“drop hits whose snippet is the AGENTS.md cass section”) before any Jev call. |
| **NO-CLAIM** | Negative control `zzzz_cannot_exist_9c42` must return 0. A hit about noul is not a noul answer. |

---

## Census

| id | name | store | first-on-Studio? |
|---|---|---|---|
| A01 | Thread supersession vs `reply_to` | mail | |
| A02 | Human-overseer high-badge echo cost | mail | **yes (1)** |
| A03 | Cross-session skill-reuse hit rank | cass | |
| A04 | Dig-vs-invent on cass snippets | cass | |
| A05 | Ack SLA breach | mail | **yes (2)** |
| A06 | Phishing-in-band | mail | |
| A07 | Reservation conflict co-presence | mail | |
| A08 | Wrong-selector language prevalence | cass | cass-fallback |
| A09 | Retransmit / token waste | cass | |
| A10 | Question-shape → receipt vs retraction | cass | |
| A11 | Mail→cass join on project path | both | **yes (3)** |
| A12 | Empty-success `count>0` | cass | cass-fallback |
| A13 | Advice-stale vs index-fresh | cass | |
| A14 | Workspace alias residual | cass | |
| A15 | CC-as-owner after steward-map | mail | |
| A16 | `thread_id` ≠ bead-id breach | mail | |
| A17 | Same-query Y-flip across days | cass | |
| A18 | Cass ACK vs missing `ack_ts` | both | after A11 |
| A19 | Snippet reuse vs edit delta | cass | |
| A20 | Attachment/path selector plant | mail | |
| A21 | Reservation ping-pong | mail | |
| A22 | Same-agent vs other-agent reuse | cass | |
| A23 | Draft-quality vs send-authority | mail | |
| A24 | Hits about cass, not solutions | cass | cass-fallback |

**24 cards. 0 measurements. 0 promoted.**

---

## First mines on Studio (selection, not taste)

Ranked by the autonomous-loop rules: ground truth today → prevalence → cost →
leverage. Full commands live in
[`work/cass-mail-mines/README.md`](../../../work/cass-mail-mines/README.md).

1. **A02** — `importance` / `from` are columns. VOI vs B0/B1 can kill a family
   with zero Jev calls (R42.3).
2. **A05** — `ack_required` / `ack_ts` / `created_ts` are columns. Co-presence
   plant is free.
3. **A11** — join yield gates every `both` card. Print it or fail closed.

If mail export is dead (`count: 0` / no `messages/` tree): do **not** report
“no chatter.” Fall through to cass-only **A12 / A08 / A24** on
`/Volumes/ZestData/cass-data/agent_search.db`.

This cloud VM **cannot** run any of those.

---

## Rejected designs (this pass)

| Rejected | Why | Retry when |
|---|---|---|
| Port PR #32 `sess` / `args` / `isError` / `args_len_*` onto cass or mail | Those columns are not in those stores. Selector ≠ claim. | Never as a port. A *new* labelled export with its own columns is a different mine. |
| Treat this 24-card catalog as a promotion denominator | `diagnostic_synthetic` / unrun sketches cannot promote (policy `:53-56`; R28; R44). | A Studio export this pane did not author, identity-locked, labelled after questions freeze, prevalence stated, non-author confirms. |
| Author another 10-case cass/mail battery and score it | R44: n=10 is not n=7846. | Never as a substitute for the real stores. |
| Join cass question-shape to frozen-toolcall `isError` | That is a PR #32 remix, not a cass mine. | Never on that join key. |
| `reply_to` as `supersedes` | `#188` is a parent pointer. | A later mail SHA adds a real `supersedes` column — then A01's cheap control changes, the mine does not go away. |
| Second `helpful` noul gate on any of these Choices | Measured 11/12 abstentions. | Never as a gate. |
| `send_message` / auto-ack from a grade | R42.1. Irreversible fleet side-effect. | Joshua names the seam and the human confirmation in the same message. |
| Silent skip when cass/am/ZestData are absent | “Never ran” must not read like passed. | Never. Print `STORE: UNREACHABLE` / `LIVE: NOT_RUN`. |
| STATUS.tsv / gauntlet row from this file | No verdict landed. | After a Studio mine prints always-abstain **and** a cheap baseline on a locked export. |

**Refuted hypothesis this catalog is willing to hold (unmeasured):**
*“first-hit / BM25 / `importance==high` / `reply_to` / `count>0` are sufficient
policies on the real stores.”* The authored plants are built so those policies
lose to always-abstain. **Confirm on Studio.** If a cheap rule beats
always-abstain *and* matches Y on the plant pair, that family is a VOI kill
and Jev is not budgeted.

---

## NO-CLAIM

- **`promoted = 0`.** Ledger stays 0 promoted. `docs/demos/STATUS.tsv` is
  untouched. No gauntlet row.
- **Nothing ran against CASS or mail.** This VM: no `/Volumes/ZestData`, no
  `cass`, no `am`, no `/tmp/.tskey`. No Jev call. No omp seam. No `sr`.
- **Not PR #31 / #32.** Those scores stay on `toolcall-corpus-frozen.jsonl`.
  This file does not reprint 0.212 / 1.495 / 0.197 as cass or mail numbers.
- **Not the cass/mail task-test always-abstain arithmetic** (0.667 / 0.800).
  Those are authored Y. R28 applies.
- **Not skillranker's 0.167 / 0.800 / 0.833 live/contract numbers.**
- **Not `jev-spam-eval`.** Human SMTP ≠ agent bus.
- **Hit / message schema is from upstream docs**, not from a local introspect.
  Field drift is a retry, not a silent coerce. Do not invent SQLite table
  names for `agent_search.db`.
- **n=24 authored cards.** Prevalence figures in the task-test files are
  properties of plants. Real prior-art / heartbeat base rates are unknown.
- **No secret** in this file. Phishing copy talks about a key path, not a key.
- **`ubs` on a doc-only change exits 3** — that is **not** a pass (R6).
- This document is `[pending]`: catalog, **nothing executed**.

---

## Next lever (not this PR)

1. On Studio, follow `work/cass-mail-mines/README.md` — A02 → A05 → A11
   (or cass-fallback A12/A08/A24 if mail is dead).
2. Identity-lock the export (n, class counts, sha256). Refuse a 10-row
   substitute.
3. Print always-abstain + cheap baseline **before** any Jev question freezes.
4. Only then: freeze questions, label Y (non-author), score VOI.
5. Wire observe-only only for a family that beats always-abstain **and** the
   cheap rule on that locked export.

Until step 1, the honest state is **EXPLORED** (this file) — not `PROBED`.
