# Jev task tests for cass — design, unpromoted (2026-09-20)

**Status:** DESIGN. **Unpromoted.** Level: `[pending]`.  
**Lane:** offline. **Class target:** C (ground-truth). **Class this file may claim:** none — this is a contract, not a measurement.  
**Consumer:** an omp surface that, before scaffold or ask-user, runs playbook A (`cass`) and then a Jev rank, then exports scores.  
**Oracle for the contract shape:** `Dicklesworthstone/skillranker` eval policy as mirrored at `work/skillranker-eval/contract/evaluation_policy.v1.json` (`frozen_contract_not_evidence`, pulled `@ bb52b8f25`).  
**Oracle for cass hit fields:** public `Dicklesworthstone/coding_agent_session_search` SKILL.md *Response Shapes* (read 2026-09-20 via web; **not** a local `--robot` dump — cass is off `PATH` on this VM).  
**This file is not a product, not a harness, not a live receipt.**

---

## Mission line this unit serves

Validate Jev → build tools from what survives → **liven omp surfaces with them** → dogfood → share.  
This unit is **stage one (validate) only**. It licenses a later harness or it dies. It does not ship a ranker.

---

## Why this exists

`cass` is on-PATH doctrine in this lane and is under-used as a first-party receipt.

- Stage 0 already says search before inventing: `cass search "jev" --robot --limit 10` (`AGENTS.md:890`).
- Research surfaces already name it: `cass search "…" --robot --limit 5` (`AGENTS.md:982`).
- The dedicated section forbids the TUI and pins the worked commands (`AGENTS.md:1403-1418`).

Dont-give-up **playbook A** is the same hole wearing a skill face: the house skill still shows `cass status --json` and `--workspace <project>`, while the lane receipt is `--robot` and a published query (`docs/essays/dont-give-up-gaps.md:1098,1179-1186`). Off `PATH` is not “cass missing” — steal from `AGENTS.md`.

Skillranker already treats cass as **session context**, not as a judged roster (`pipeline/cass_source.rs` + `context/cass.rs`; receipt `skillranker-origin-main-20260919.md`). Their *eval contract* is the pattern this design copies: session context → roster → Choice+`__none__` → local eligibility → JSON decide → frozen 0/1/2 loss (`skillranker-process-mirror-20260919.md:17-23`; `work/skillranker-eval/README.md`).

**The measured gap, stated as a gap:** cass already searches past sessions. Nothing in this tree **grades, ranks, or filters** what cass returns, or **decides dig-vs-invent** before a pane scaffolds or asks the user. `omp-jev-rerank` scores `grep`/`glob` lists and **does not reorder**; it is the wrong surface (code search, not session search) and the right restraint (observe-only until a non-authored corpus exists).

---

## Doctrine cited — `AGENTS.md` cass section, verbatim obligation

```
## cass — Cross-Agent Session Search

cass indexes prior agent conversations (Claude Code, Codex, Cursor, Gemini,
ChatGPT, etc.) so we can reuse solved problems.

Rules: Never run bare cass (TUI). Always use --robot or --json.

cass health
cass search "jev typed questions" --robot --limit 5
cass view /path/to/session.jsonl -n 42 --json
cass capabilities --json

stdout is data-only, stderr is diagnostics; exit code 0 means success.
Treat cass as a way to avoid re-solving problems other agents already
handled — this ecosystem is one week old and the most likely prior
solver is one of our own panes from yesterday.
```

(`AGENTS.md:1403-1418`.)

**Binding corollaries already measured in this repo:**

| Token | Authority | Consequence for this design |
|---|---|---|
| Never invent `--workspace <project>` | `dont-give-up-gaps.md:1098` | Lane queries do **not** take a placeholder workspace flag. Workspace is a **hit field**, judged after the search returns. |
| Off `PATH` ≠ unusable | `dont-give-up-gaps.md:1098`; this VM `command -v cass` → absent | Live cass lane is `NOT_RUN`. Offline fixtures still run. Do not file “cass missing.” |
| `requireKey` before absence | `work/oracle-kit/index.mjs:116-123`; `TESTS.md:28-31` | A claim that a hit “has no `workspace`” must dump the keys present. |
| SDK fields | `docs/demos/SDK-SURFACE.md` | Choice uses `.choice` / `.probabilities` / `.confidence`. Noul uses `.noul` (no confidence). Score uses `.score`. There is no `.probability` or `.distribution`. |
| No second-noul gate | `work/skillranker-eval/README.md:67-68`; `skillranker-corpus-measured-20260919.md:54-65` | A `helpful` noul forced 11/12 abstentions. Abstain is `__none__` only. |

---

## Juice — where Jev earns a seat, and where it does not

Jev is paid. String equality is free. Split the work **before** writing questions.

### Local (do not call Jev)

| Check | Input | Fail-safe |
|---|---|---|
| Selector ≡ claim | `requireKey(hit, 'source_path' \| 'line_number' \| 'agent')` | Refuse the hit; do not rank a partial object. Error names the keys present. |
| Empty-success refusal | cass exit 0 **and** `count > 0` **and** zero hits survive eligibility | Decision `abstain` / action `invent`. **Not** “cass found it.” Exit 0 is not a solved hole. |
| Wrong-workspace (literal) | `hit.workspace` present and ≠ live cwd / live project root | Drop from roster (eligibility `wrong-workspace`). |
| Index-stale (literal) | `_meta.index_freshness.stale === true` or `trust.trust_tier === 'stale'` | Drop or flag; do not treat BM25 `score` as freshness. |
| Empty / malformed envelope | missing `hits` array, non-object hit, `count` absent | `unavailable` (loss 2 if the case was attempted). Do not impute `hits: []`. |
| Cass off `PATH` / `cass health` ≠ 0 | live lane only | `LIVE: NOT_RUN`. Offline fixtures still score. |

### Jev (the paid questions — this is the juice)

| Seat | Primitive | Why a regex / first-hit / BM25 cannot do it |
|---|---|---|
| Rank surviving hits for a **live hole** | Choice over `hit_id` ∪ `{__none__}` | Cass `score` is retrieval (lexical/hybrid), not “this session solved *this* hole.” |
| Advice-stale / superseded decision | Noul `advice_stale` (diagnostic, **not a gate**) | A 2026-09-17 receipt can be index-fresh and decision-dead. |
| Residual wrong-workspace | Noul `same_project` when paths are aliases / missing | Literal path compare is blind to moved checkouts and missing `workspace` on `--fields minimal`. |
| Dig vs invent | Choice `__none__` = invent; a hit id = reuse / `cass view` | First-hit always digs. Always-abstain always invents. Both are the controls. |
| Prior-decision extract | Choice among hits whose snippet carries a named VERDICT / decision envelope | Lexical overlap ≠ a reusable decision. |
| Answers-the-question grade | Score `answers_hole` 0–3 **or** Noul `answers_hole` (diagnostic) | BM25 rewards shared tokens (“cass”, “robot”, “TUI”) on docs *about* cass. |

**Hard rule copied from skillranker-eval:** the product decision is **one Choice** with `__none__`. Diagnostic Score/Noul are exported beside the pick. They do **not** override a confident Choice. The 0.750→0.167 swing on their corpus was an invented second gate (`skillranker-corpus-measured-20260919.md:54-65`).

---

## Pipeline — skillranker shape, cass roster

Adopted from `skillranker-process-mirror-20260919.md:17-23` and `work/omp-jev-route/src/process.mjs`. Cass hits replace skills. Quill/254-wide is **not** copied (omp cass `--limit 5` is already a shortlist; `dont-give-up` playbook A uses 5).

```
live hole (task + cwd + constraints)
  → cass health                         # live lane only; offline injects the envelope
  → cass search "<hole>" --robot --limit 5
  → requireKey on envelope (query, count, hits)
  → roster = hits that survive requireKey(source_path, line_number, agent)
           + local eligibility (workspace, index-freshness)
  → Choice+__none__ over roster ids     # one question; no helpful-noul gate
  → local decide: ranked | abstain | unavailable
  → JSON envelope (schema below)
  → export scores (eval JSONL + optional jev-score-register hash)
  → eval contract (Y, loss 0/1/2, always-abstain, planted RED)
```

Decision kinds (same four tokens as skillranker ledger / `omp-jev-route`):

| decision | cass meaning |
|---|---|
| `ranked` | reuse this hit; next command is `cass view <source_path> -n <line_number> --json` |
| `explicit` | the live hole named a session path; resolve locally, no Jev |
| `abstain` | invent — cass returned noise, or nothing answers. **Not** “no hits.” |
| `unavailable` | cannot judge (malformed envelope, off-PATH in a lane that claimed live, asker throw) |

Actions the envelope may carry (cass-specific, *after* the decision kind):

| action | When |
|---|---|
| `reuse` | `ranked` and Y-eligible hit |
| `dig` | `ranked` but the pane must `cass view` / `cass expand` before treating snippet as the answer |
| `invent` | `abstain` — scaffold / write new. Playbook A has been run; it did not pay. |
| `ask-user` | **Forbidden as the first move.** Ask-user is only after cass+Jev abstain *and* invent is blocked by a named human gate. |

---

## Cass envelope — selector ≡ claim

**Authoritative field names** (upstream SKILL.md *Search Response*, 2026-09-20). This is **not** a local `--robot` dump. A later implementer must re-open `cass introspect --json` / `cass robot-docs schemas` on a machine where cass is installed and **refuse to score** if these keys have moved.

Envelope keys: `query`, `limit`, `count`, `total_matches`, `hits`.  
Optional `_meta`: `elapsed_ms`, `cache_hit`, `wildcard_fallback`, `next_cursor`, `index_freshness.{stale,age_seconds}`.

Per-hit keys:

| field | `--fields minimal` | `--fields summary` | full / default |
|---|---|---|---|
| `source_path` | yes | yes | yes |
| `line_number` | yes | yes | yes |
| `agent` | yes | yes | yes |
| `title` | no | yes | yes |
| `score` | no | yes | yes |
| `workspace` | no | no | yes |
| `snippet` | no | no | yes |
| `match_type` | no | no | yes |
| `created_at` | no | no | yes |
| `trust.*` | no | no | `--robot-meta` only |

**Rejected design:** judging stale / wrong-workspace / answers-the-question on `--fields minimal`. Those questions are blind without `workspace`, `created_at` / `trust`, and `snippet`. The lane search command stays the AGENTS.md shape (`--robot --limit 5`), which is the default/full payload, **not** `--fields minimal` and **not** `--workspace <project>`.

`requireKey` on every hit before it enters the roster. A scorer that reads `hit.score` when the key is absent fabricates BM25-0 and looks like a real null (the `.distribution` / 0.500 defect, `SDK-SURFACE.md:17-23`).

Planted RED for the selector (CASS-08 below): a hit object with `title`+`snippet`+`score` and **no** `source_path`. The harness must throw / mark `unavailable` and **name the plant keys**. A pick of that row is a harness fail, not a Jev fail.

---

## Eval contract — adopted, not invented

Copy `work/skillranker-eval/score.mjs` `LOSS` and `NONE`. Do not fork a second table. Assert the frozen values against `evaluation_policy.v1.json` the same way `assertFrozenLoss` does.

| class | loss |
|---|---:|
| correct recommendation on positive | 0 |
| correct no-match abstention | 0 |
| false abstention on positive | 1 |
| incorrect recommendation on positive | 2 |
| needless recommendation on no-match | 2 |
| operationally unavailable on attempted case | 2 |

Their rationale, kept: *a loss that charges only wrong emitted suggestions is invalid because always abstaining would minimize it without helping positive cases* (`evaluation_policy.v1.json:70-71`).

**Y** = `acceptable_hit_ids_y`: the independently judged set of cass `hit_id`s that actually answer the live hole under current constraints. Empty Y means invent (`__none__`). Already-viewed sessions can make Y empty (loaded-reference analogue). A repeatable workflow (same hole, new tree) can keep Y nonempty.

**`hit_id`** is `source_path` + `#` + `line_number`. Not `title`. Titles collide.

**Split:** every case in this file is `diagnostic_synthetic`.  
`forbidden_use` (copied): *No promotion, calibration, or statistical quality claim.*  
A later class-C run requires cass `--robot` dumps this pane did **not** author, labelled before questions freeze (R28).

**Always-abstain is required.** A policy that only punishes wrong picks is invalid.

---

## Preregistered bars — written before any run

These are **diagnostic bars** on an authored set. Clearing them is **not** promotion. `diagnostic_synthetic` cannot promote even at precision 1.0 (`evaluation_policy.v1.json:53-56`; `work/skillranker-eval/README.md:39-41`).

| bar | value | what failure means |
|---|---|---|
| always-abstain mean loss on the 9 judged cases | **6/9 = 0.667** | 6 positives × 1 + 3 no-match × 0. If a scorer reports a different always-abstain, the denominator drifted. |
| first-hit mean loss (preregistered, not sampled) | **14/9 ≈ 1.556** | first-hit is wrong on CASS-02,03,04,05,06,07,09 (loss 2) and right on CASS-01,10 (loss 0). |
| BM25-only (cass `score` argmax) | **same as first-hit on these fixtures** | every planted noise hit is also the highest `score`. If a later corpus breaks that, recompute; do not keep 1.556. |
| random / coin-flip | report exact E[loss] over roster ∪ `{__none__}` per case, then the mean | overflow-empty-roster trap from skillranker-eval: if eligibility empties the roster, the action space is `{__none__}` only. |
| empty-success refusal | **3/3** on CASS-05,06,07 | any `ranked` pick is loss 2 (needless). |
| selector plant | CASS-08 → `unavailable` or throw naming `source_path` | a pick is a harness RED, not a Jev score. |
| always-pick-top-hit (planted RED) | mean loss **worse than always-abstain** on {CASS-02,03,04,09} | if it is not, the plants are not plants. |
| Jev / candidate judge | mean loss **< 0.667** and **< first-hit** | necessary, not sufficient. |
| top-1 on positives | print it; **do not promote at 0.90** | skillranker’s 0.90 is *their* skill-router gate on *their* split. Applying it here as a ship gate is spec-editing. |
| feasibility arm | a perfect judge (pick first Y id, else `__none__`) must score **mean loss 0** on the 9 judged cases | if it cannot, the labels are contradictory. **BLOCKED-HARNESS**, not a Jev verdict. |
| class | A until a non-authored cass dump exists | authored n=10 is the third time this week we would inflate (R28). |

**Prevalence (state it beside every score):** 6/9 judged cases have nonempty Y (66.7%). CASS-08 is operational / unjudged for relevance.

---

## ≥10 synthetic cases — cass hit lists as state

`split: diagnostic_synthetic` for all. Schema stamp: `jev.cass-task-test.case.v1`.  
Paths are synthetic (`/projects/jev_playground`, `/projects/other-app`). No operator home paths. No secrets. No captured live session bodies.

Live hole text is **this lane’s already-published holes**, not invented product work.

### Shared roster field note

Each `hits[]` item is a cass-shaped object. `hit_id` is derived, not stored by cass. The harness derives it. Cases that omit a required field are plants.

### CASS-01 — `positive_reuse`

**Kind:** `positive_advisory`. **Y:** `["/projects/jev_playground/sessions/dont-give-up.jsonl#1182"]`.  
**Always-abstain loss:** 1. **Wrong pick loss:** 2. **Correct pick loss:** 0.

Live hole: *“the house skill shows `cass --workspace <project>`; what is this lane’s worked command?”*

| rank | hit_id | workspace | score | snippet (abridged) | role |
|---|---|---|---:|---|---|
| 1 | `…/dont-give-up.jsonl#1182` | `/projects/jev_playground` | 0.91 | `cass health` then `cass search "jev typed questions" --robot --limit 5` (`AGENTS.md:1410-1411`) | **gold** |
| 2 | `…/other-app/tui-notes.jsonl#4` | `/projects/other-app` | 0.74 | “run `cass` and pick from the TUI” | wrong-workspace + wrong command |
| 3 | `…/jev_playground/readme-draft.jsonl#20` | `/projects/jev_playground` | 0.40 | “cass indexes sessions” | same workspace, does not answer |

First-hit = gold (the one case first-hit is allowed to win). Feasibility arm must pick the gold.

### CASS-02 — `stale_top_hit`

**Kind:** `near_miss_advisory`. **Y:** `["/projects/jev_playground/sessions/skillranker-eval-20260920.jsonl#12"]`.  
**Near-miss must not count as correct:** the rank-1 hit.

Live hole: *“what is the skillranker eval contract we actually run in this tree?”*

| rank | hit_id | created_at | trust_tier | score | snippet | role |
|---|---|---|---|---:|---|---|
| 1 | `…/skillranker-20260919.jsonl#3` | 2026-09-19T08:00:00Z | `stale` | 0.88 | “clone `@3fe85c4`; `src/` never reads `synthetic_cases`” | **stale advice** (true then, superseded by `work/skillranker-eval/`) |
| 2 | `…/skillranker-eval-20260920.jsonl#12` | 2026-09-20T04:00:00Z | `trusted` | 0.61 | `node work/skillranker-eval/run.mjs` — frozen 0/1/2, always-abstain 0.833 | **gold** |
| 3 | `…/compaction.jsonl#1` | 2026-09-18T12:00:00Z | `unverified` | 0.22 | keep/drop compaction | off-hole |

First-hit and BM25 pick the stale receipt → loss 2. Always-abstain → loss 1. Jev must pick rank 2 or abstain (cheap). Local eligibility **may** drop `trust_tier=stale` before Jev; if it does, the roster is `{gold, compaction}` and the case still has a nonempty Y. The case remains valid either way — record which eligibility path ran.

### CASS-03 — `wrong_workspace`

**Kind:** `near_miss_advisory`. **Y:** `["/projects/jev_playground/sessions/infisical.jsonl#15"]`.

Live hole: *“Infisical says run init — is the secret missing?”*

| rank | workspace | score | snippet | role |
|---|---|---:|---|---|
| 1 | `/projects/other-app` | 0.86 | “run `infisical init` then `infisical run --projectId=<id>`” | **wrong workspace + leftover `<id>`** |
| 2 | `/projects/jev_playground` | 0.55 | `42b194c3-89d7-4ebb-895f-dd77ddf005ba`; unlinked directory ≠ missing secret | **gold** |
| 3 | `/projects/jev_playground` | 0.19 | “TYPESAFE_API_KEY lives in `/tmp/.tskey`” | related, does not answer init-vs-unlinked |

Literal `workspace` compare drops rank 1 before Jev. Residual case for Jev: if `--fields minimal` omitted `workspace`, Jev must still refuse the `<id>` snippet as the answer. **Both paths are in the case:** `workspace_present: true` in this fixture so the local filter is testable; CASS-08 is the missing-field plant.

### CASS-04 — `dig_vs_invent_dig` (buried gold)

**Kind:** `overflow_retrieval` analogue (shortlist of 5, gold at rank 4). **Y:** `["/projects/jev_playground/sessions/requirekey.jsonl#116"]`.

Live hole: *“I grepped `"role": "toolResult"` and got zero files — does omp persist tool results?”*

| rank | score | snippet | role |
|---|---:|---|---|
| 1 | 0.93 | docs *about* noul / tool results in AGENTS.md | lexical trap |
| 2 | 0.81 | `omp-jev-rerank` README “scores. It does not reorder.” | same tokens, wrong product |
| 3 | 0.70 | “empty scan set is an ERROR” | related doctrine, not the spacing bug |
| 4 | 0.44 | file has **no space**; spaced form matches 0 files (`SDK-SURFACE.md:19`) | **gold** |
| 5 | 0.21 | cass TUI warning | noise |

First-hit / BM25 → loss 2. Always-abstain → 1. Jev should pick rank 4 (`dig` then `cass view`). `__none__` is the cheap miss.

### CASS-05 — `dig_vs_invent_invent`

**Kind:** `no_match_advisory`. **Y:** `[]`. Correct decision: `__none__` / action `invent`.

Live hole: *“wire a typed Jev asker into a **new** omp `session_before_compact` judged keep-set that this lane has not built.”*

Hits are all *about* compaction or cass, none a keep-set implementation:

| rank | score | snippet | role |
|---|---:|---|---|
| 1 | 0.90 | `fast-jev-compaction` keep/drop | prior art, **not this hole** |
| 2 | 0.80 | AGENTS.md compaction seam table | doctrine, not a landed keep-set |
| 3 | 0.70 | cass search for “compact” in other-app | wrong workspace |

Empty-success refusal: `count=3` must **not** read as “cass already solved it.” Needless pick → loss 2.

### CASS-06 — `answers_question_false_positive`

**Kind:** `no_match_advisory`. **Y:** `[]`.

Live hole: *“what is Jev’s **invoice-processing** accuracy on TypeSafe’s dashboard?”*

| rank | score | snippet | role |
|---|---:|---|---|
| 1 | 0.95 | “Jev aggregate **67.8%** vs 74.1% best comparator” (`AGENTS.md` RULE 13) | **right number, wrong question** (aggregate, not invoice) |
| 2 | 0.88 | “61.8% against 79.1% on invoice processing” — same paragraph | **gold-looking trap:** this *is* the invoice number, but the snippet is our *citation of the gap*, not a reproduced dashboard row with date/model/N |
| 3 | 0.30 | cass health help | noise |

**Label rule for this case (preregistered):** Y is empty because neither hit is a first-party reproduction (`evals.typesafe.ai` not run here; no N/date/model). Picking rank 2 as if we had reproduced the dashboard is **needless recommendation** (loss 2): it launders a cited gap into a measured result. Correct = `__none__` / invent a budgeted live check or write `NOT_RUN`.

This is the “grade whether a hit actually answers” seat. BM25 cannot make this distinction.

### CASS-07 — `empty_success_noise`

**Kind:** `no_match_advisory`. **Y:** `[]`.  
**Planted empty-success:** envelope `count: 5`, `total_matches: 42`, `_meta.index_freshness.stale: false`, conceptually exit 0.

Live hole: *“did another pane already land `jev-task-tests-cass`?”*

All five hits are older cass *mentions* (AGENTS.md quotes, dont-give-up playbook A, skillranker cass_source). None is this design. `count>0` + fresh index + exit 0 is the lie. Decision must be `abstain` / `invent`. A `ranked` pick is loss 2 and a **named RED** for empty-success.

### CASS-08 — `selector_claim_missing_field` (harness RED)

**Kind:** `operational_failure_semantics`. **Relevance denominator:** **excluded** (unjudged).  
**Y:** n/a. **Expected:** `unavailable` or throw.

Envelope contains one hit:

```json
{
  "title": "Authentication debugging",
  "snippet": "The error occurs when...",
  "score": 0.85,
  "match_type": "exact"
}
```

Keys present: `title`, `snippet`, `score`, `match_type`.  
`requireKey(..., 'source_path')` must throw `no 'source_path'. Keys present: [match_type, score, snippet, title]`.  
A harness that picks this row, or that reports “no workspace” without the key dump, **fails the plant**. This is the planted negative for selector ≡ claim.

### CASS-09 — `always_pick_top_RED`

**Kind:** `positive_advisory`. **Y:** `["/projects/jev_playground/sessions/ubs-r6.jsonl#99"]`.  
**Planted baseline:** `always-pick-top-hit` **must** score loss 2 on this case. If it does not, the plant is broken.

Live hole: *“`ubs` on a markdown-only change exited 3 — is that a pass?”*

| rank | score | snippet | role |
|---|---:|---|---|
| 1 | 0.99 | “`ubs --staged` until exit 0” (generic skill line) | **top-hit trap** |
| 2 | 0.41 | exit 3 = nothing checked, **not a pass** (`NEGATIVE_EVIDENCE.md` R6) | **gold** |

Always-pick-top-hit → 2. Always-abstain → 1. Jev should pick rank 2. This is the named RED the user asked for (`always-pick-top-hit`).

### CASS-10 — `prior_decision_extract`

**Kind:** `repeatable_workflow_nonempty_y`. **Y:** `["/projects/jev_playground/sessions/route-process.jsonl#74"]`.

Live hole: *“we need a typed abstain cheaper than a wrong pick for a cass ranker — do we already have the decision envelope?”*

| rank | score | snippet | role |
|---|---:|---|---|
| 1 | 0.77 | “Never run bare cass (TUI)” | doctrine, not a decision envelope |
| 2 | 0.48 | `decision TEXT CHECK(decision IN ('ranked','explicit','abstain','unavailable'))` + 0/1/2 loss copied into `omp-jev-route` | **gold — reusable prior decision** |
| 3 | 0.33 | skillranker README marketing | not our landing |

Correct pick = rank 2, action `reuse`. Prior load of the archaeology receipt must **not** empty Y (repeatable workflow: new surface, same envelope). Loaded-reference analogue would empty Y only if this exact cass ranker already shipped — it has not.

---

## Always-abstain, first-hit, BM25, random — worked on these labels

Judged set = CASS-01..07,09,10 (n=9). CASS-08 excluded.

| case | Y empty? | always-abstain | first-hit / BM25 | perfect judge |
|---|---|---:|---:|---:|
| 01 positive_reuse | no | 1 | 0 | 0 |
| 02 stale_top_hit | no | 1 | 2 | 0 |
| 03 wrong_workspace | no | 1 | 2 | 0 |
| 04 buried gold | no | 1 | 2 | 0 |
| 05 invent | yes | 0 | 2 | 0 |
| 06 answers-false | yes | 0 | 2 | 0 |
| 07 empty-success | yes | 0 | 2 | 0 |
| 09 top-hit RED | no | 1 | 2 | 0 |
| 10 prior decision | no | 1 | 2 | 0 |
| **mean** | 3/9 empty (33.3% no-match) | **0.667** | **1.556** | **0.000** |

Coin-flip: per case, uniform over `{hit_1..hit_k, __none__}`. Eligibility may drop hits; the implementer must compute E[loss] from the **post-eligibility** roster, not from raw `count`. Report the exact fraction, not a 5,000-trial sample, unless a sample is labelled as a sample (skillranker-eval already made this distinction: exact 1.035 vs sampled 1.036).

---

## Question text (preregistered — do not retune after seeing scores)

One Choice. Criteria map is roster `hit_id` → one-line `agent` / `workspace` / `title` / first 160 chars of `snippet`. Plus `__none__`.

```
instructions: "Which listed prior session hit should the agent open next
for this live hole, if any?"

__none__: "No listed hit actually answers this hole. Invent rather than
reuse. Cass returning hits is not evidence they help."
```

Diagnostic only (export, never gate):

| name | type | text |
|---|---|---|
| `answers_hole` | noul | “Does this hit answer the live hole, not merely share tokens with it?” |
| `advice_stale` | noul | “Is the reusable decision in this hit superseded by a later first-party receipt in the same workspace?” |
| `same_project` | noul | “Is this hit from the same project as the live hole, given the workspace field or the path?” |

Python Noul requires `instructions` or `criteria` (`SDK-SURFACE.md:52-54`). JS `noul()` supplies it. Use the sanctioned `work/jev-client` caller; do not invent `client.systemOne.evaluate`.

**Rejected:** gating the Choice on `answers_hole ≥ 0.5` (the skillranker `helpful` defect). **Rejected:** treating cass `score` as `probabilities`.

---

## JSON decide envelope

Reuse `jev.omp-jev-route.process.v1` kinds. Cass-specific schema stamp: `jev.cass-rank.decision.v1`.

```json
{
  "schema_version": 1,
  "schema": "jev.cass-rank.decision.v1",
  "decision": "ranked",
  "reason": "choice-above-none",
  "action": "dig",
  "hit_id": "/projects/jev_playground/sessions/requirekey.jsonl#116",
  "source_path": "/projects/jev_playground/sessions/requirekey.jsonl",
  "line_number": 116,
  "none_probability": 0.08,
  "diagnostics": {
    "answers_hole": null,
    "advice_stale": null,
    "same_project": null
  },
  "cass": {
    "query": "spaced toolResult grep zero files",
    "count": 5,
    "total_matches": 5,
    "eligibility_dropped": ["wrong-workspace:2"]
  },
  "persistence": "recorded",
  "binding": "log-only"
}
```

`binding: log-only`. Observe-only. Never `{block:true}`. A throwing sink still returns `undefined` (same as `omp-jev-rerank` / `omp-jev-route`). Adoption ≠ usefulness.

Export row (installable ≠ exportable; copy the skillranker-eval export columns, cass-flavoured):

`schema, case_id, pick, y, loss, why, class, roster_ids, y_in_roster, judge, lane, measured_product`

`measured_product` is false unless a real `cass search --robot` produced the envelope. These fixtures keep it false.

---

## omp wiring — before scaffold / ask-user

**Co-presence with dont-give-up playbook A.** Playbook A is the cass dig. This unit is the **Jev-rank after cass** that playbook A lacks. They must fire in the **same session**, same profile. Silence next to a firing neighbour is “not loaded,” not “no prior art” (`dont-give-up-skill-patches.md` playbook E neighbour rule).

### When it runs

1. Agent is about to **scaffold** a new instrument, demo, or benchmark.
2. Agent is about to **ask-user** “has this been solved?”
3. Stage 0 research (`AGENTS.md:890`) — cass is already listed; this adds the rank.

Not on every tool call. A per-tool-call Jev question multiplies by session tool count (`AGENTS.md` cost rule). Cass+Jev is a **turn-start / pre-scaffold** cost, recorded as calls-per-decision.

### Live commands (lane, not skill generics)

```bash
cass health
cass search "jev typed questions" --robot --limit 5
# then, only on a ranked hit:
cass view /path/to/session.jsonl -n 42 --json
```

Hole string is the live task, not the example query. The example query is the **worked lane shape**. Never `--workspace <project>`. Never bare `cass`.

If `command -v cass` fails: steal the commands from `AGENTS.md:1410-1413`, run the **offline** fixtures, print `LIVE: NOT_RUN`. Do not report “cass missing.”

### Where it lands (when someone builds this — not this PR)

| piece | path | rung it can reach |
|---|---|---|
| Playbook A paste (already written) | house skill / `dont-give-up-skill-patches.md` | doctrine |
| Observe-only tool | `<repo>/.omp/tools/cass-rank.ts` (project scope) | L2 loaded / L3 if a known-bad list makes it abstain |
| Optional skill | `.omp/skills/cass-dig/SKILL.md` pointing at AGENTS.md commands + this contract | not a measurement |
| Score export | `work/jev-score-register/` hash + eval JSONL (pick/Y/loss) | same split as skillranker-eval |

**Not a blocking hook.** A cass miss must not block `bash`. Fail-open. Skillranker hook is fail-open / shadow (`skillranker-process-mirror-20260919.md:72-74`); copy that, not a `{block:true}` safety gate.

**Not MCP in v0.** An MCP server is the isolating option (`AGENTS.md` seam 5) and is the right later home for the paid key. Design v0 is the in-process observe-only tool so the eval contract can be dogfooded without a second process. Revisit if the key must leave the agent.

### Neighbour co-presence (playbook A)

Same session, same profile:

1. Playbook A runs `cass health` (or the offline fixture loader when cass is off `PATH`).
2. This tool writes a `jev.cass-rank.decision.v1` row.
3. A known-firing neighbour (dcg-tool-bridge / harm-rule) writes a row.

0 cass-rank rows next to a firing neighbour means not loaded — missing `pi.on`, glob miss, or not on `extensions:`. Silence alone is not a finding.

### Healthy path is silent

`ranked`/`abstain` on ordinary holes must not nag. Export the row. Do not inject a lecture. Skillranker: ordinary abstention is silent. Copy that or the seam gets uninstalled.

---

## What a later harness must implement (acceptance for a *build* PR — not this one)

Positive observable:

- `node --test` (or `node work/…/run.mjs`) scores the 10 cases offline with an injected asker. No key. No network.
- always-abstain mean loss prints **0.667** on the 9 judged cases.
- planted CASS-08 names `source_path` in the error / `unavailable` reason.
- planted CASS-09: always-pick-top-hit loss **2**.
- CASS-05/06/07: a first-hit policy loss **2**; `__none__` loss **0**.
- `--live` without a key prints `LIVE: NOT_RUN` (exit 0). That is not a pass.
- Feasibility (perfect judge) mean loss **0**.

Planted negatives: CASS-08 (selector), CASS-09 (always-pick-top-hit), CASS-07 (empty-success).

NO-CLAIM the build PR must repeat: authored split; cannot promote; cass off-PATH → live NOT_RUN.

---

## Rejected designs (retry conditions)

These are design refusals. They are **not** yet `NEGATIVE_EVIDENCE.md` rows — no measurement landed this pass. Promote a row there only when a run exists.

| Rejected | Why | Retry when |
|---|---|---|
| Treat cass exit 0 + `count>0` as “already solved” | Empty-success; playbook A hole class | Never. CASS-07 is the permanent plant. |
| Invent `--workspace <project>` on the lane command | Measured skill defect (`dont-give-up-gaps.md:1098`) | Never for the *command*. Workspace remains a hit field. |
| `--fields minimal` as the judge payload | Drops `workspace` / `snippet` / `created_at`; stale and answers-the-question go blind | A measured token-budget forces minimal **and** a second `cass view` fills the missing fields before Jev. |
| Use cass `score` as Jev `probabilities` | Selector ≠ claim; retrieval ≠ judgment | Never. |
| Gate Choice on a second noul | 11/12 abstentions on skillranker’s corpus | Never as a gate. Diagnostics stay diagnostics. |
| Per-tool-call cass+Jev | Cost multiplies by tool count | A held-out session log shows calls-per-session and money, and the healthy path is silent. |
| Blocking hook | Wrong seam; cass miss is not a destroy-data command | Never for this surface. |
| Promote on these 10 authored cases | R28: authored corpora inflated three results in one day | A cass `--robot` dump this pane did not write, labelled before questions freeze, prevalence stated, non-author confirms. |
| Apply skillranker 0.90 top-1 as a *ship* gate here | Different product, diagnostic split, forbidden_use | Their gate may be printed as a **rate FAIL** on a future harness (skillranker-eval’s exit 2) so a miss cannot hide; it still cannot promote this split. |
| Silent skip when cass is off `PATH` | “Never ran” must not read like passed | Live lane prints `NOT_RUN`. Offline still runs. |
| Ask-user before cass+Jev | The user asked for pre-scaffold / pre-ask-user | Never as the first move. |

**Refuted hypothesis this pass is willing to hold (unmeasured):** *“first-hit / BM25-only is a sufficient cass reuse policy.”* The fixtures are built so that policy’s mean loss is 1.556 vs always-abstain 0.667 — first-hit is **worse than doing nothing**, the same shape as skillranker’s coin-flip (1.035) vs always-abstain (0.833). **Retry / confirm:** score first-hit on a non-authored cass dump. If first-hit beats always-abstain there, this seat shrinks to empty-success + selector plants only.

---

## NO-CLAIM

- **Unpromoted.** Ledger stays **0 promoted**. `docs/demos/STATUS.tsv` is untouched. No gauntlet row.
- **Nothing ran.** No `cass` binary on this VM (`command -v cass` absent). No `cass health`, no `--robot` dump, no `cass view`. No live Jev. No `sr` binary. No omp session. No skill paste applied.
- **Class A at best** if someone later scripts these fixtures against a fake asker. Class C requires labels this author did not write, on envelopes cass actually emitted.
- **Hit schema is from upstream SKILL.md**, not from a local introspect. Field drift is a retry, not a silent coerce.
- **n=10 authored cases.** R28 applies. Prevalence 6/9 nonempty Y is a property of the plants, not of real cass traffic. Real prior-art prevalence in this week-old ecosystem is unmeasured; RULE 13 still says the most likely solver is yesterday’s pane — that is doctrine, not a base rate.
- **Skillranker 0.167 / 0.800** is Jev-on-*their*-skill corpus (`skillranker-corpus-measured-20260919.md`). It is not a cass-rank number and is not re-run here.
- **`omp-jev-rerank`** is not this product. It observes grep/glob and does not reorder.
- **Playbook A is not merged** as a JSM skill edit on this tip (dont-give-up essays cite open PRs). This design does not paste it.
- **No secret** in any fixture. No captured customer state. No `/Users/josh` paths.
- This document is `[pending]`: code-first contract, **nothing executed**.

---

## Next lever (not this PR)

1. On a machine with cass: `cass health` && `cass capabilities --json` && `cass introspect --json`; pin the schema or refuse.  
2. Harvest a **non-authored** `--robot` dump (other panes’ sessions; secret-scan; gitignore the raw file if credential-shaped). Label Y **after** freezing the question text above.  
3. Build the offline harness against `work/skillranker-eval/score.mjs` (`LOSS`, `NONE`, `--export`, planted RED). Do not fork the loss table.  
4. Wire observe-only `.omp/tools/cass-rank.ts` next to playbook A; prove CASS-07 abstain and CASS-08 throw in a disposable `jev-lab` profile. L3 needs both directions.  
5. Then, and only then, a budgeted live Jev pass (state N, model pin, why offline was insufficient).

Until step 2, the honest state is **EXPLORED** (this file) — not `PROBED`.
