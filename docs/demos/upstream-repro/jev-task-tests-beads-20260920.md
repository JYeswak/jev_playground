# Jev task tests for the beads DB — unpromoted design

**Date:** 2026-09-20 · **Level:** `[pending]` · **Claim:** DESIGN ONLY.
**Promotion:** `promoted = 0`. This file licenses a later measurement. It is not a measurement.

**Mission this unit serves:** Validate Jev → build tools from what survives → liven omp surfaces → dogfood → publish. This packet is stage-one design of a *tool that has not been built*. A ruling that never runs is not the next stage.

**Pattern:** skillranker’s unused eval contract (frozen 0/1/2 loss, always-abstain control, `__none__` abstain, `diagnostic_synthetic` cannot promote, roster + eligibility, structured JSON decisions), pointed at *our* issue store instead of a skill roster.

**Prior art (read, not copied):**

| artifact | what we steal | what we do not steal |
|---|---|---|
| `work/skillranker-eval/oracle.mjs` | loss table, `__none__`, always-abstain, noul-as-diagnostic-not-gate | their 12-case corpus, their 0.90 number as *ours* until we earn it |
| `docs/demos/upstream-repro/skillranker-corpus-measured-20260919.md` | the invented-noul-gate defect (0.750 → 0.167) | any promotion from `split: diagnostic_synthetic` |
| `docs/demos/BEAD-TEMPLATE.md` | ACCEPTANCE must be a live command + planted RED; P0 inflation is a named anti-pattern | length-as-target (7 KB) — symptom, not juice |
| `docs/demos/tick.md` | panes self-claim from `br ready`; author-exclusion; `QUEUE DRY` is wrong while ready is non-empty | conductor-tick product |
| `work/oracle-kit/index.mjs` | `field()`, `feasibility()`, `auc().constant` | scoring this battery before a feasibility arm exists |
| `docs/demos/SDK-SURFACE.md` | `choice` / `probabilities` / `noul` / `score` — there is no `.probability` or `.distribution` | guessed field names |
| `work/jev-client/src/index.ts` | the only sanctioned `systemOne` body | a new client |
| `work/omp-jev-commit/src/index.ts` | observe-only `tool_call` on bash, fail-open, never a silent pass | blocking `br close` |
| `docs/INTEGRATIONS.md:174` | **no invented STOP-LIVE** | deferred registration / quiet-window-as-science-gate |

**Upstream first (Rule 13):** no cloned repo in this workspace already asks “is this bead’s ACCEPTANCE runnable / is this close honest / which ready bead is next *semantically*.” `bv --robot-triage` asks the *graph* form of “what’s next.” That is the incumbent, not prior art to reimplement. Skillranker asks the same *shape* of question (pick from a roster or abstain) on a different object. We run *their* contract against *our* store.

**Oracle named:** none yet. A later run that scores these cases is `[test]` at best (we authored the snapshots). A run against a week of real `br ready` exports we did not write the questions against is the first `[oracle]`-eligible number. See §8.

---

## 0. Beads on tip — cited, not remembered

Read from disk at design time, branch `cursor/jev-task-tests-beads-6862` off `origin/main` `5dfaba1`:

| path | bytes / rows | role |
|---|---|---|
| `.beads/issues.jsonl` | **48 issues** | JSONL is the truth (`metadata.json` says so) |
| `.beads/config.yaml` | `issue_prefix: jev` | our prefix |
| `.beads/metadata.json` | `database: beads.db`, `jsonl_export: issues.jsonl` | sqlite is disposable; JSONL is reviewable |
| `.beads/.gitignore` | `*.db*` | `beads.db` is never the fixture |

`br` / `bv` are **not on PATH in this environment.** Every `br …` / `bv --robot-*` command below is an ACCEPTANCE command for a later tick, not a number produced today.

Census of `.beads/issues.jsonl` (stdlib parse, 2026-09-20):

| field | count |
|---|---|
| issues | 48 |
| `closed` / `open` / `in_progress` / `blocked` | 26 / 11 / 5 / 6 |
| `issue_type` task / bug | 32+ / rest bugs on older rows; Muse children are tasks |
| priority 0 / 1 / 2 / 3 | **6 / 19 / 20 / 3** |
| description contains `ACCEPTANCE` | **46 / 48** |
| `close_reason == "done"` (no receipt named) | **7 / 26** closed |
| rows with `dependencies` | **12**, all `type: "parent-child"` |
| graph cycles | **0** (tree of parent-child only; `br dep cycles` not run — this is a key scan, not `bv`) |
| `acceptance_criteria` field populated | **1** (`jev-gate-error-decorrelation-ltk`) — everyone else inlines ACCEPTANCE in `description` |
| Muse children | `jev-vbh` + `jev-vbh.1` … `.5` (all `open`; parent P1, children P2) |
| P0 set | all six `jev-publish-*` (hero, playground, hog.1, readme, redteam, scrub) |

Observed issue keys on tip: `id, title, description, status, priority, issue_type, created_at, created_by, updated_at, source_repo, source_repo_path, compaction_level, original_size`, plus optional `closed_at, close_reason, comments[], assignee, labels[], dependencies[], acceptance_criteria`.

Comment object keys (from `jev-0bp`): `id, issue_id, author, text, created_at`.

Dependency object keys (from `jev-vbh.1`): `issue_id, depends_on_id, type, created_at, created_by, metadata, thread_id`.

**Implication for juice:** the graph on tip is a forest of parent-child edges, not a blocked-by DAG. `bv --robot-insights | jq '.Cycles'` is expected empty. A Jev “dep-cycle risk” question on *this* store has prevalence ≈ 0 and is the wrong product. Semantic questions (ACCEPTANCE quality, close honesty, ceremony, ready-queue honesty) have prevalence we can state today. See §1.

---

## 1. What juice Jev can extract from beads (ranked)

Ranked by (ground truth exists today) × (positive-class prevalence) × (cost to measure) × (decision leverage), per the autonomous-loop selection rule. **Graph-complete facts are not juice.** If `br dep cycles` or `status=` already decides it, Jev is a paid echo.

| rank | juice | primitive | why Jev and not `bv` / a regex | prevalence on tip (not a label) | act vs observe |
|---|---|---|---|---|---|
| **1** | **ACCEPTANCE quality** | Score (3-level) + diagnostic Noul | 46/48 rows *contain the word* ACCEPTANCE. A regex “has ACCEPTANCE:” is near-constant. The lane rule is a *live command a stranger can run* (`BEAD-TEMPLATE.md` §4; Joshua: ACCEPTANCE must be live commands). That is semantic. | high mention rate; unknown *quality* rate — that is the thing to label | observe → later, refuse to *file* a bead (not this design) |
| **2** | **claim-vs-close mismatch** | Noul | 7/26 closed rows have `close_reason: "done"` while ACCEPTANCE named a receipt, a labels jsonl, or a command. `jev-0bp` is the sharp one: `close_reason` is `done` and the only comment starts `BLOCKED with receipt 4c19790`. `bv` does not read close text. | **7/26 = 27%** of closed rows are thin-`done` *candidates* (not gold — some may be honestly done) | observe; never auto-reopen |
| **3** | **ceremony-bead detector** | Noul | `jev-kma` title is `Scratch probe bead (delete)`; `jev-vbh` ACCEPTANCE is “this graph exists”; `jev-route-standards-manifest-6yq` is a route-to-foreign-steward process bead, `blocked`, labels `steward:process`. Process beads are how USER 0 / ENABLER 5 / PROCESS 17 recurs. | low-to-medium; enough to label | observe; do not auto-close |
| **4** | **ready-queue honesty** | Noul (or Choice over `{ready, not_ready, __none__}`) | 6 `blocked` rows have **no** `dependencies` — blocked by prose/labels, not by the DAG. `jev-publish-hero-ulo` is `in_progress` P0 whose latest comment is `BLOCKED … GEN failed`. `tick.md` already lost a day to `QUEUE DRY` while P0s sat “ready.” Graph triage cannot see a comment that says BLOCKED. | 6 blocked-without-edge; 1+ in_progress-with-BLOCKED-comment | observe; a later conductor tick may *exclude* |
| **5** | **next-bead triage vs `bv --robot-triage`** | Choice over eligible roster + `__none__` | This is the skillranker question. Incumbent is `bv --robot-next`. Jev’s only wedge is *semantic* priority (P0 hero vs P2 measured recall) and *eligibility the graph cannot see* (author-exclusion is a string; “blocked in the comment” is not). If Jev cannot beat `bv` + a dumb heuristic on a holdout of real ready exports, this row **closes**. | unknown until `br ready --json` is captured | observe first; claim remains a human/`br update` |
| **6** | **priority inflation** | Score | `BEAD-TEMPLATE.md:118` already named it: 6/21 at P0 meant priority carried no information; he uses P1/P2 only. Tip still has **6/48 = 12.5%** at P0, all publish cosmetics. | 6 P0s, all `jev-publish-*` | observe |
| **7** | **eligibility / author-exclusion** | Choice, `__none__` when the only candidates are own-authored | `tick.md`: claim the highest-priority bead *you did not author*. Deterministic given `created_by` + actor. Jev is used only when the roster is mixed and the question is “which of these *I may claim* is actually startable.” A roster of only own-authored beads is a `__none__` case. | depends on actor; constructable | observe |
| **8** | **dep-cycle *semantic* wait** | **abstain** | Graph cycles are `br dep cycles` / `bv --robot-insights`. Tip has zero. A Jev question here fails the prevalence test and the “cheaper deterministic baseline” closure rule. Included as a **planted `__none__` case** so a harness that “finds” cycles on a tree is caught. | ~0 | do not act |

**Not ranked as juice (rejected here, retry in §9):** rewriting priority, auto-closing, fail-closed `pre` hook on `br close`, “STOP-LIVE until a quiet window,” treating `bv` as broken because we have not installed it.

---

## 2. Skillranker contract, transplanted

Transcribed from `work/skillranker-eval/oracle.mjs` (their `tests/eval/evaluation_policy.v1.json` as that file recorded it). **Do not retune after seeing scores.**

### 2.1 Frozen loss (Choice / roster questions)

| outcome | loss |
|---|---|
| `correct_recommendation_on_positive` | **0** |
| `correct_no_match_abstention` | **0** |
| `false_abstention_on_positive` | **1** |
| `incorrect_recommendation_on_positive` | **2** |
| `needless_recommendation_on_no_match` | **2** |

Abstain is the model picking `__none__`. A second Noul (“would any bead help?”) is **diagnostic only** — never a gate. Their first run here taught that (`helpful` 0.07–0.48 on all 12 while `topP` was 0.74–1.00).

### 2.2 Frozen loss (Noul)

Polarity is fixed per case in the fixture (`y_side: "yes"|"no"`). Threshold 0.5. Abstain if `noul ∈ (0.40, 0.60)` (band named now, not after a run).

| outcome | loss |
|---|---|
| correct side of 0.5 | **0** |
| abstain when a side is labelled | **1** |
| wrong side | **2** |

`noul` has **no** `confidence` field (`SDK-SURFACE.md`). Do not invent one.

### 2.3 Frozen loss (Score)

Three-level rubric, `score` is the SDK expected value (may fall between levels). Map to nearest level `{0,1,2}`. Abstain if `confidence < 0.55` (choice/score have confidence; named now).

| outcome | loss |
|---|---|
| exact level | **0** |
| off-by-one | **1** |
| off-by-two or abstain-when-labelled | **2** / **1** |

### 2.4 Always-abstain control

For this 10-case battery the control is computed from the labels in `work/jev-beads-eval/cases.v1.jsonl`, not from a later run:

- Choice positives (C1): abstain costs 1
- Choice no-match (C2, C10): abstain costs 0
- Noul labelled (C5, C6, C8, C9): abstain costs 1 each
- Score labelled (C3, C4, C7): abstain costs 1 each

**always-abstain mean loss = 8/10 = 0.800.**

A coin-flip Choice on C1 (4 roster ids + `__none__`) is not computed here — n=1 Choice case cannot carry a 5,000-trial baseline. When the holdout grows, compute it the way `oracle.mjs` did, *from the corpus alone*, before the first live call.

### 2.5 Promotion (stolen, then bounded)

Their gate: top-1 precision on positives ≥ 0.90 **and** mean loss < always-abstain.

Ours, preregistered, **stricter on one axis**:

1. mean loss < 0.800 (always-abstain)
2. mean loss < dumb heuristic (defined in §5)
3. on the Choice subset: top-1 precision on positives ≥ 0.90
4. feasibility arm (`oracle-kit` `feasibility`) passes on the planted RED pair (C4, C9)
5. **`split: diagnostic_synthetic` cannot promote.** This battery is that split.

Clearing (1)–(4) on this file is `CLEARED (class C, diagnostic)` — enough to *build the observe-only scorer*, not enough to *wire it into a working profile as advice the model must honor*.

---

## 3. State snapshot shape

Jev `state` is one JSON object. Question IDs are never sent to the model (`typesafe-ai/skills`); meaning lives in `instructions`. The snapshot must be complete enough to answer without the rest of the repo.

```json
{
  "schema": "jev-beads-state/v1",
  "source": {
    "jsonl": ".beads/issues.jsonl",
    "exported_at": "2026-09-20T00:00:00Z",
    "head": "5dfaba1"
  },
  "actor": {
    "id": "omp-muse_1",
    "may_claim": true,
    "authored_ids": ["jev-vbh", "jev-vbh.1"]
  },
  "graph": {
    "ready_ids": ["jev-m7r", "jev-vbh.1"],
    "blocked_ids": ["jev-route-standards-manifest-6yq"],
    "cycle_ids": [],
    "note": "ready_ids come from `br ready --json` when the binary exists; fixtures plant them."
  },
  "roster": [
    {
      "id": "jev-m7r",
      "title": "…",
      "status": "open",
      "priority": 2,
      "issue_type": "task",
      "labels": [],
      "assignee": null,
      "created_by": "josh",
      "created_at": "2026-09-19T00:00:00Z",
      "close_reason": null,
      "acceptance_excerpt": "ACCEPTANCE: either a corpus … or a written ruling …",
      "comment_tail": [],
      "dep_ids": [],
      "dep_types": []
    }
  ],
  "focus": { "id": "jev-cz0", "…": "same fields plus close_reason and last comment" },
  "eligibility": {
    "claimable_ids": ["jev-m7r"],
    "excluded": [{ "id": "jev-vbh.1", "reason": "authored_by_actor" }]
  }
}
```

**Roster construction (product path, when built):**

1. `br ready --json` → candidate ids (graph eligibility).
2. Drop ids in `actor.authored_ids` (tick eligibility).
3. Cap roster at 8 + `__none__`. Overflow is a `__none__` / “ask `bv --robot-plan`” problem, not a Jev problem.
4. Each roster row carries `acceptance_excerpt` (slice from first `ACCEPTANCE` through 400 chars) and `comment_tail` (last ≤2 comments, 300 chars each). No home paths, no keys.

**Focus construction (ACCEPTANCE / close / ceremony questions):** one issue, same fields, plus `description_head` (first 800 chars) — not the full 7 KB. Skillranker overflow_retrieval was a false abstention; we accept that risk and do not dump whole bodies into state on a design that has not been paid for.

Fixtures live at `work/jev-beads-eval/cases.v1.jsonl` (schema in `work/jev-beads-eval/policy.v1.json`).

---

## 4. Task-test battery (10 cases)

Every case has: `case_id`, `split`, `question_type`, `y` / `acceptable_*`, loss table (by type), always-abstain cost, planted RED. Structured decision out:

```json
{
  "decision": "act | abstain",
  "choice": "<id>|__none__|null",
  "score": 0.0,
  "noul": 0.0,
  "confidence": 0.0,
  "reason_code": "ready|thin_close|ceremony|inflated|unrunnable|__none__"
}
```

`reason_code` is *our* post-score label, not a Jev field. Do not ask Jev to emit it.

### C1 — `bt-next-ready-measured` · Choice · `diagnostic_synthetic`

**Question:** “Which listed bead should this actor claim next, if any?”
**Criteria:** one short line per roster id + `__none__` = “No listed bead is claimable and startable; do not invent work.”

**Roster (planted, ids are real):**

| id | status | P | why it is in the roster |
|---|---|---|---|
| `jev-publish-hero-ulo` | in_progress | **0** | comment_tail starts `BLOCKED … GEN failed` — heuristic bait |
| `jev-vbh` | open | 1 | ACCEPTANCE is “this graph exists” — ceremony parent |
| `jev-vbh.1` | open | 2 | ACCEPTANCE is a live `infisical run … node --experimental-strip-types <compaction-score-script>` |
| `jev-m7r` | open | 2 | ACCEPTANCE is a corpus *or* a written ruling — live, measured |
| `__none__` | — | — | abstain |

**Y / acceptable:** `["jev-vbh.1", "jev-m7r"]` — both have a stranger-runnable ACCEPTANCE and are `open`. Hero is not acceptable (blocked in the comment). Parent `jev-vbh` is not acceptable (ceremony; work is the children).

**Always-abstain cost:** 1 (false abstention).
**Planted RED:** a judge that returns `jev-publish-hero-ulo` because P=0. Dumb heuristic does this by construction (§5).
**Actor:** `authored_ids: []` so author-exclusion is off (that is C10).

### C2 — `bt-next-no-match` · Choice · `diagnostic_synthetic`

**Roster:** `jev-cz0` (closed), `jev-kma` (closed scratch), `jev-route-standards-manifest-6yq` (blocked, labels `blocked` + `steward:process`), `__none__`.

**Y:** `["__none__"]`
**Always-abstain cost:** 0
**Planted RED:** any id other than `__none__` (needless recommendation, loss 2).

### C3 — `bt-accept-live-cmd` · Score · derived from tip `jev-vbh.1`

**Rubric:** `0` = no stranger-runnable command (or “looks right”); `1` = names an artifact but not a command; `2` = copy-pasteable command + named observable.

**Focus:** `jev-vbh.1` ACCEPTANCE excerpt as on tip (live `infisical run … node --experimental-strip-types …`, success observable: quoted payload lines score ~0).

**Y:** `2`
**Always-abstain cost:** 1
**Planted RED:** none in this row — the pair is C4.

### C4 — `bt-accept-looks-right` · Score · `diagnostic_synthetic` · **feasibility RED**

**Focus:** C3’s issue with ACCEPTANCE replaced by `ACCEPTANCE: looks right; the pane will know.` Everything else identical (status open, P2, real id suffix `-plant`).

**Y:** `0`
**Always-abstain cost:** 1
**Planted RED (this *is* the plant):** a scorer that still emits 2 has failed the feasibility arm. `oracle-kit` `feasibility` on `{C3→high, C4→low}` must clear `bar=0.8` and `constant=false`. If it does not, **no verdict** — harness is blind.

### C5 — `bt-claim-close-thin` · Noul · derived from tip `jev-cz0`

**Question:** “Does `close_reason` name evidence that could satisfy the stated ACCEPTANCE?”
**Y side:** `no` (we want noul < 0.5)

**Focus:** `jev-cz0` — ACCEPTANCE demanded “a committed labels jsonl per extension … precision/recall … every FP/FN quoted”; `close_reason: "done"`; `comments: []`.

**Always-abstain cost:** 1
**Planted RED:** answering yes. (We do **not** gold-label that the work was undone — only that the close text does not name the evidence. See §8.)

### C6 — `bt-claim-close-named` · Noul · derived from tip `jev-4uy`

**Same question as C5.** **Y side:** `yes`

**Focus:** `jev-4uy` `close_reason` on tip begins `docs/demos/phi-second-pair-20260919.md [oracle]: …` — a path + level + number.

**Always-abstain cost:** 1
**Control for C5:** if C5 and C6 collapse to the same side, the Noul is a constant (`oracle-kit` `auc().constant`).

### C7 — `bt-priority-inflation` · Score · derived from tip P0 cluster

**Rubric:** `0` = P matches described blast radius; `1` = one notch off; `2` = P0/P1 for cosmetics or a blocked publish while measured-open work sits at P2.

**Focus:** `jev-publish-hero-ulo` P0, ACCEPTANCE is `visual/hero.jpg` + grade JSON; comment_tail is BLOCKED on gen. Compared in-state to a one-line note that `jev-m7r` (real-danger recall) is P2 open.

**Y:** `2`
**Always-abstain cost:** 1
**Planted RED:** same focus with `priority` mutated to 2 should score 0 — if both score 2, the question is “is this a publish bead?” not “is priority inflated?”

### C8 — `bt-ceremony-route` · Noul · derived from tip `jev-route-standards-manifest-6yq`

**Question:** “Is this a ceremony / route / process bead with no consumer-visible product change in-repo?”
**Y side:** `yes`

**Focus:** title `Route: add jev to fh's authoritative target manifest…`, status `blocked`, labels `blocked, jev, routed, steward:process`, comment routes to franken-harvest steward.

**Always-abstain cost:** 1
**Negative control (same question, not a separate case id):** `jev-32z` (FP on production commands, ACCEPTANCE is `FP count/30 … or HARNESS BLIND`) must land `no`. If both are yes, ceremony is a constant. Recorded as C8’s planted RED *pair* in the fixture (`controls.must_flip_id`).

### C9 — `bt-ready-honesty-open-blocked` · Noul · `diagnostic_synthetic` · **feasibility RED**

**Question:** “Should this bead appear in `br ready` for a stranger pane?”
**Y side:** `no`

**Focus:** `jev-route-standards-manifest-6yq` with **only** `status` mutated `blocked → open`. Labels still include `blocked`; comment still says BLOCKED; no `dependencies`.

**Always-abstain cost:** 1
**Planted RED:** a status-only heuristic (`status==open ⇒ ready`) says yes. That is the dumb baseline. Jev must use the comment/labels.

### C10 — `bt-eligibility-author` · Choice · `diagnostic_synthetic`

**Roster:** only `jev-vbh`, `jev-vbh.1` … `jev-vbh.5` (Muse children). **Actor** `authored_ids` contains every one of them.

**Y:** `["__none__"]` — tick.md author-exclusion. Graph may call them ready; this actor may not claim them.

**Always-abstain cost:** 0
**Planted RED:** picking `jev-vbh.1` because it has the best ACCEPTANCE (correct for C1, wrong here). Eligibility is part of the state; ignoring it is a harness defect.

---

## 5. Head-to-head — preregistered bar

Three arms, same 10 cases, same loss tables. **No arm may be dropped after seeing scores.**

| arm | how it decides | what it cannot see |
|---|---|---|
| **Jev** | `work/jev-client` `askJev` / `askJevChoice` via injected transport; questions frozen in the fixture | nothing we put in `state` |
| **`bv --robot-triage` / `bv --robot-next`** | parse `--robot-*` JSON; pick `quick_ref` / next id if it is in the roster, else `__none__` | comment text, ACCEPTANCE quality, close_reason honesty. On C3–C9 it **is** the always-abstain arm (no opinion → abstain) |
| **dumb heuristic** | Choice: lowest `priority` number among `status ∈ {open, in_progress}`, then oldest `created_at`; if none, `__none__`. Score/Noul: `status==open ⇒ ready/yes`; `close_reason` non-empty ⇒ close-ok; `description` contains `ACCEPTANCE` ⇒ score 2; `priority<=1 ⇒` not inflated | semantic blockers, thin `done`, ceremony, author-exclusion |

**Preregistered verdict rule** (write it on the receipt *before* the first keyed call):

```
CLEARED-diagnostic  iff  mean_jev < 0.800
                    and  mean_jev < mean_heuristic
                    and  feasibility(C4,C9).ok
                    and  (Choice positives == 0 or top1 >= 0.90)

BEATS-BV-wedge      iff  on {C3,C4,C5,C6,C7,C8,C9}
                         mean_jev < mean_bv
                         (bv is always-abstain on these by construction)

SHIP-OBSERVE-CLI    iff  CLEARED-diagnostic
                         (the CLI in §6, still observe-only)

SHIP-OMP-ADVICE     never on this split.
                    Retry: a holdout of real `br ready --json` exports
                    from days the question-author did not label.

RULED_OUT-triage    iff  on {C1,C2,C10} mean_jev >= min(mean_bv, mean_heuristic)
                    Retry: new fact — a week of ready-queue exports
                    where bv and the heuristic disagree with a human claim log.
```

`bv` is **PREPARED-NOT-MEASURED** in this environment (binary absent). The first measurement tick installs or wraps it; it does not invent a `quick_ref` shape. If `bv --robot-next` JSON does not contain a single next id, the arm records `UNAVAILABLE` and the BEATS-BV-wedge clause is skipped — it is **not** scored as a pass.

---

## 6. How it plugs into omp — observe-only first

**Do not block `br`. Do not rewrite priority. Do not close beads.**

Phased, each phase has a kill switch (`JEV_BEADS_EVAL=0`, matching `work/jev-usage-router`).

### Phase A — CLI over a snapshot (no omp, default)

```text
node --experimental-strip-types work/jev-beads-eval/score.mjs \
  --cases work/jev-beads-eval/cases.v1.jsonl \
  --asker fake|live
```

- `fake`: injected asker, offline, the only lane this design authorizes now.
- `live`: budgeted, N=10, model pinned `jev-1.13.0`, key from `/tmp/.tskey` never printed. State in the session *before* the call: which tree (`work/jev-beads-eval`), lane `live`, 10 calls, why offline was insufficient (it wasn’t, until the fake asker is green).
- Export: `work/jev-beads-eval/logs/scores-<ISO8601>.jsonl` — one row per case: `case_id, arm, decision, choice, score, noul, confidence, loss, why`. Gitignore the logs if they ever contain live state that is not already public in `.beads/issues.jsonl`.

This phase does not exist as code in this PR. The fixture + this file *are* the design.

### Phase B — omp custom tool, model-callable, observe-only

Land later in **project** scope, not `~/.omp/`:

`.omp/tools/jev-beads-observe.ts`

- Params: `{ mode: "ready"|"focus", id?: string }` (`pi.zod`).
- Reads `.beads/issues.jsonl` (truth) and, if present, shells `br ready --json` / `br show <id> --json` as *hints*, never as the only source.
- Asks the frozen questions. Appends one JSONL score row. Returns the structured decision to the model as **advice**.
- Fail-open: tool errors return a `beads_error` row (`NEGATIVE_EVIDENCE.md` R40 — never a silent pass) and `undefined` / a visible error string, never a fake score.

L2 proof: `get_state.dumpTools` lists it. L3 proof: a known-bad focus id (C4 / C9) produces `decision: act` with the RED label, and a healthy `br ready` of an empty claimable roster produces `__none__` without commenting. Healthy path **silent** except the JSONL.

### Phase C — optional `tool_call` observer on bash (still fail-open)

Copy the `work/omp-jev-commit` shape: listen for `bash`, match `^\s*br\s+(ready|show|close|update)\b`, build a snapshot, score, append. **Return `undefined` on every path.** Never `{block:true}`.

This is the dogfood path. Register on **pane 0 or `omp --profile=jev-lab`**, not by taking down mid-flight panes. **No STOP-LIVE, no “registration requires human review,” no quiet-window science gate** (`docs/INTEGRATIONS.md:174`, `EVAL.md:448`). Fleet blast radius is a human gate only for *working* profiles, and even then the first install is observe-only fail-open.

### What we will not plug

| seam | why not |
|---|---|
| `.omp/hooks/pre/*` fail-closed on `br close` | acting on an unpromoted diagnostic split |
| `session_before_compact` | wrong object (messages, not issues) |
| MCP `jev-mcp` verify/screen/find as a beads ranker | those tools are not this question; wrapping them is dependency smuggling |
| Host-owned `jev://bead/next` | host-key ownership is a later L4; not this design |

---

## 7. Surfaces this would consume, if it ever ships

Named consumers, so this is BUILD-shaped rather than an unconsumed instrument (Rule 12 phase boundary):

| consumer | what it would read |
|---|---|
| `docs/demos/tick.md` self-claim rule | JSONL `choice` when a pane’s queue drains — advice, still `br update` to claim |
| Muse children `jev-vbh.1`–`.5` | ACCEPTANCE-quality Score on the skill loop beads themselves |
| `work/jev-usage-router` | not a route target; do not stuff bead triage into usage routing |
| `work/skillranker-eval/oracle.mjs` | loss-table + scorer helpers, not the skill corpus |
| `work/oracle-kit` | `field` / `feasibility` / `auc` on every published number |

If those consumers are not wired in the same PR that first *runs* the battery, the instrument is HOLD.

---

## 8. NO-CLAIM / what not to test

- **This is not a product.** No CLI, no omp tool, no hook shipped in this change. Fixtures are a sketch.
- **`diagnostic_synthetic` cannot promote.** The 10 cases were authored by the same pass that wrote the questions (`NEGATIVE_EVIDENCE.md` R28). Clearing the bar here licenses an observe-only CLI, nothing else.
- **`close_reason: "done"` is not gold-wrong.** C5 tests whether the *text names evidence*, not whether `jev-cz0`’s labels jsonl exists in the tree. Do not reopen beads from a score.
- **`bv` was not run.** Do not invent `--robot-triage` output. Do not declare `bv` worse than Jev.
- **No dep-cycle product.** Tip has 12 parent-child edges and 0 cycles. `br dep cycles` is the oracle. A Jev cycle score would be a ceremony metric.
- **No STOP-LIVE.** Live omp registration of an observe-only tool is allowed on pane 0 / `jev-lab` when a later tick has a fake-asker green suite. Quiet-window is timing, not a science gate.
- **No live Jev call in this PR.** Offline-first. The key does not enter the tree, the fixtures, or this file.
- **No invented field names.** Read `docs/demos/SDK-SURFACE.md`. `field()` throws.
- **Do not gate Choice on a helper Noul.** Already measured as a 0.750→0.167 swing.
- **Do not test “should we stop using beads.”** Out of scope.
- **Do not treat Muse `jev-vbh` ACCEPTANCE (“this graph exists”) as a product ship.** It is in the battery *as* a ceremony parent.
- **Home paths in tip JSONL** (`source_repo_path: /Users/josh/Developer/jev`) stay in the beads store; fixtures here strip them.
- **`promoted = 0` after this file lands.** A design receipt is not a rung.

---

## 9. Rejected designs (retry conditions)

Recorded here and as `NEGATIVE_EVIDENCE.md` R43.

1. **Replace `bv --robot-triage` with Jev over the whole DAG.** Cost: a new ranker plus a paid call per tick, against an incumbent that already emits `--robot-*` JSON. Defect class it would not catch: graph reachability, which is already exact. Loss: we would stop running `bv` and lose the only non-authored comparator. **Retry:** a holdout of ready-queue days where a human claim log disagrees with `bv --robot-next` on ≥10 rows and Jev agrees with the human at mean loss < both baselines.
2. **Fail-closed pre-hook on `br close`.** Acting on diagnostic labels. **Retry:** SHIP-OMP-ADVICE conditions in §5, plus L3 on both a bad close (C5) *and* a named-receipt close (C6) in a real omp session, fail-open first.
3. **Invent STOP-LIVE / defer registration / quiet-window-as-science-gate.** Already retracted at `docs/INTEGRATIONS.md:174`. **Retry:** none — Joshua’s word.
4. **Jev dep-cycle detector.** Prevalence ~0 on tip; deterministic baseline exists. **Retry:** `br dep cycles` non-empty on a store we own, and a cheaper script cannot name the cycle.

---

## 10. Next lever (not a plan to make a plan)

One command, offline, when a later tick *builds* the scorer that this file specifies:

```text
node --experimental-strip-types work/jev-beads-eval/score.mjs --asker fake
```

ACCEPTANCE for that tick (not this one): fake asker + planted RED C4 and C9 fail by name; always-abstain mean prints `0.800`; live lane prints `NOT_RUN` when the key is absent; `ubs` on the new TS/JS exits 0; this file’s bar text is unchanged.

**Boundary of *this* file:** no scorer was run, `br`/`bv` were not executed, no Jev call was made, no omp tool was registered. 48 issues were counted from `.beads/issues.jsonl` on `5dfaba1`.
