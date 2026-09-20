# SkillRanker PROCESS archaeology — public HEAD `6a74cca` (2026-09-20)

**Pass:** DEEP PASS A for `jev_playground`.  
**Upstream:** [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) (public).  
**Pinned SHA:** `6a74ccad279b5ee4a3973790ec01b47265307a54`  
(`feat(ledger): implement explicit idempotent ledger init and recoverable migration`, 2026-09-20T04:40:21Z).  
**How it was read:** local receipts first, then `gh api` + a read-only shallow clone of the *public* tree at `/tmp/skillranker-public` (not a workspace clone; not committed).  
**License:** `NOASSERTION` on the GitHub repo object; `Cargo.toml:7` says `license-file = "LICENSE"`.  
**Oracle for this receipt:** the public source tree and its frozen JSON contracts. **Not** a live `sr` run, **not** a keyed Jev call, **not** a product promotion.

## Honesty banner — process patterns ≠ product promotion

This document extracts a **designed loop** and the **symbols / schemas / gates** that make it falsifiable. It does **not** promote a skill-ranker into omp, and it does **not** move any gauntlet row. `VERDICT.md` still reads **17 ideas, 0 promotions**. `docs/demos/STATUS.tsv` is untouched. `promoted=0` is the state of record.

What is extracted here is **mentor process**: typed decisions, a cheap-error abstention, a frozen loss table, an always-abstain negative control, and a promotion gate that the *product itself has not pointed at its own cases*. That last fact is the finding, not a footnote.

Wave C already registered the *intent* to mirror three named pieces (skill-router abstention, eval gate ≥0.90, JSONL export) in `docs/demos/upstream-repro/commit-learnings-20260919.md:72-83`. That register is **not evidence**. This pass is the evidence that register was waiting to read.

### Two corpora, two claims — do not conflate them

| Corpus | What it is | Does `src/` read it at `6a74cca`? | Prior receipt |
|---|---|---|---|
| **Session / cass / transcript** | live agent context | **Yes.** `pipeline.rs:586-817` ingests `--context` / `--transcript` / `--session` / `--latest`; `pipeline/cass_source.rs` + `context/cass.rs` parse archives. | `skillranker-origin-main-20260919.md` **refuted** "src never reads the corpus" for *this* corpus. |
| **Eval contract cases** | `tests/eval/synthetic_cases.v1.jsonl` (12 labelled oracles) | **No.** `rg` over `src/` for `synthetic_cases`, `evaluation_policy`, `acceptable_additional_invocations` is empty. | `skillranker-corpus-measured-20260919.md` + `work/skillranker-eval/oracle.mjs` — still true at HEAD. |

The origin/main receipt is right about session context. The eval-contract gap is a **different** file, still unread by the ranker. Status on the policy artifact: `"frozen_contract_not_evidence"` (`tests/eval/evaluation_policy.v1.json:4`).

---

## 0. Local receipts, then the SHA move

Read first, not re-derived:

| Receipt | What it already established | What this pass adds |
|---|---|---|
| `skillranker-20260919.md` | Pin `3fe85c4` had only `sr doctor`; README-ahead-of-code **retracted** once origin/main was 103 commits ahead. | Current public HEAD is **`6a74cca`**, not `4ed4c9b` / `ba5da08`. |
| `skillranker-0bp-native-20260919.md` | Native Mac `sr` blocked (RCH). | Unchanged; this pass did not build or run `sr`. |
| `skillranker-origin-main-20260919.md` | At `ba5da08`, session corpus is read; keyed rank blocked. | Session-read claim still holds. Ledger **schema** has landed; rank still does not write it (below). |
| `skillranker-corpus-measured-20260919.md` | Our oracle, not their binary: mean loss 0.167 vs always-abstain 0.833; top-1 0.800 vs gate 0.90; both misses = false abstention. | Confirmed: their `src/` still does not load those cases. |
| `work/skillranker-eval/oracle.mjs` | Transcribed their 0/1/2 table; first run invented a `helpful` noul gate and produced 11/12 abstentions. | Their product ranks with a bounded Choice + `__none__` and does **not** gate on a second noul (`eligibility.rs:274-289`, `jev/rerank.rs:1-5`). |

**NO-CLAIM for this pass:** no `cargo test`, no `sr demo`, no keyed `sr rank`, no Docker ELF, no private GitHub. Line numbers are from the public tree at `6a74cca`.

---

## 1. The designed loop — session-context → roster → Jev → rank/abstain → hook → feedback

One crate (`skillranker` 0.1.0, edition 2024, `Cargo.toml:1-13`), one binary (`sr` ← `src/main.rs:7-11` → `cli::run`). There is **no workspace of crates**. Ownership is by *module*. The loop is orchestrated in `pipeline::rank_once` (`src/pipeline.rs:542`).

```
  stdin / file / cass / transcript          .claude/skills (+ home)
           │                                        │
           ▼                                        ▼
  [1] config + EffectGate                    [4] roster discover
  [2] source select + ingest                 [5] explicit resolve
  [3] branch + task-anchor                   [6] admit() local filter
           │                                        │
           └────────────┬───────────────────────────┘
                        ▼
              [7] Quill retrieve if K > 254
              [8] wide Jev (Choice + 3 Noul + phase + stuck)
                        │
              needs_skill < gate ──► ABSTAIN "low-need"   (no rerank)
                        │
              [9] rerank Jev (Choice + fits::<id> Noul each)
             [10] after_rerank() ──► ABSTAIN low-fit / no-shortlist-match
             [11] scoring::rank() ──► DECISION ranked
             [12] validate_advisory_publication
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   JSON / table    hookSpecificOutput   ledger.sqlite3
                   (CLI not shipped)    (schema yes; rank write = no)
                        │
                   feedback / observe / eval / calibrate
                   (CLI still planned P5–P8)
```

### Step-by-step with file:line

**[1] Config + effect gate.** `rank_once` loads `ConfigFiles` and captures a `PolicyReceipt` (`pipeline.rs:566-575`). Thresholds come from config: `top`, `shortlist`, `gate`, `fits` (`:572-575`). `EffectGate` (`src/effects.rs:1-17`) is the single interpretation of `--offline` / `--dry-run` / `--no-ledger` / `--no-persist`. Dry-run can only *add* a restriction (`pipeline.rs:225-237`). Defaults: gate 0.30, fit 0.30, top 5, shortlist 8 (`jev/wide.rs:26-28`, `eligibility.rs:19`).

**[2] Session-context ingest.** `SourceOptions::resolve` (`pipeline.rs:605-635`) picks one of:

| `SourceTarget` | Path | What it is |
|---|---|---|
| `NormalizedFile` / `NormalizedStdin` | `pipeline.rs:670-716` | bounded JSON envelope, `parse_normalized_context` |
| `ClaudeTranscript` | `:717-797` | JSONL tail via `snapshot_jsonl`; latest user `Message` becomes `CurrentRequest` |
| `ClaudeHookStdin` | `:798-804` | **refused**: `"Use sr hook claude for hook protocol stdin mode"` |
| `CassSession` | `:805-816` | `pipeline/cass_source.rs` → `context/cass.rs` |

Without an explicit source, rank discovers Claude sessions under `~/.claude/projects` plus configured `transcript_roots` (`pipeline.rs:591-604`). Recency is disclosed as a warning, not proof of the live pane (`:647-661`).

**[3] Branch + task anchor.** `resolve_active_branch` (`pipeline.rs:819-826`) then `resolve_task_anchor` (`:829-853`). A terse continuation without an antecedent, an uninspectable request, or contradictory require/exclude directives **never reach ranking** (`InsufficientContext` / `OversizedInput` / `UnresolvedExplicit`). `context/overlay.rs:3-16` is the *designed* hook overlay: for `UserPromptSubmit`, stdin `prompt` is authoritative even when the transcript has not yet recorded it. That overlay is **not** on the `sr rank` path today (see [5] Hook).

**[4] Roster.** `roster::Source::load` (`pipeline.rs:933-944`). Claude project-over-personal precedence is used under the explicit provisional label `claude-code-documented-unverified` (`pipeline.rs:80-82, 933-936`). Every result therefore carries `"visibility": "unverified"` unless a different contract is evidenced (`visibility_label`, `:87-96`).

**[5] Explicit resolution (bypasses Jev).** `resolve_explicit_requirements` (`pipeline.rs:976-992`) then `eligibility::route` (`eligibility.rs:100-108`):

- `Route::Explicit` → emit and **call no provider** (`eligibility.rs:91-93`, pipeline `:996-1108`).
- `Route::Unresolved` → `unavailable` / `UnresolvedExplicit` (`:1110-1148`).
- `Route::Advisory` → continue with exclusions (`:1150-1152`).

**[6] Local admission before any Jev call.** `admit` (`eligibility.rs:150-197`) removes restricted / excluded / proven-loaded-reference candidates. An all-excluded or all-loaded roster **abstains with no provider request** (`eligibility.rs:147-149, 174-191`). Empty roster is `unavailable` / `EmptyRoster` (`:155-160`) — operational failure, not a cheap abstention.

**[7] Overflow retrieval.** If admitted count > `MAX_REAL_OPTIONS` (254) (`jev/wide.rs:31`, `pipeline.rs:1276-1298`), `roster::retrieval::retrieve` (Quill / frankensearch) runs. Empty retrieval is exit 5, not an abstention.

**[8] Wide Jev call.** `jev/wide.rs` one request, policy `wide-questions-v1` (`:24`):

| Question key | Type | Instructions (abbrev.) |
|---|---|---|
| `which` | Choice, options = admitted skills + `__none__` | "Which available skill would most help the next step… Choose `__none__` when no listed skill adds useful guidance." (`:36, 43-45`) |
| `gate::specialized_method` | Noul | "Would the next step benefit from a specialized method…?" (`:37, 47-48`) |
| `gate::material_help` | Noul | "Would consulting a relevant skill materially improve…?" (`:38, 49-50`) |
| `gate::context_suffices` | Noul | "Is the existing context sufficient without consulting any additional skill?" (`:39, 51-52`) |
| `phase` | Choice | 8 phases: planning / implementing / debugging / testing / reviewing / releasing / conversing / other (`:40, 56-71`) |
| `stuck` | Noul | "Is there evidence of repeated failure on the current task…?" (`:41, 54-55`) |

`needs_skill = (specialized + material + (1 − context_suffices)) / 3` (`wide.rs:356-358`). If `needs < gate` → `WideDecision::LowNeed` → **abstain / `low-need`, no rerank** (`wide.rs:329-330, 387-388`; `pipeline.rs:1971-2015`). A winning `__none__` on `which` alone does **not** end the pass: "the detailed rerank can rescue a poorly described skill" (`wide.rs:3-6`). Shortlist is the best `M` *real* candidates either way; the sentinel never takes a slot (`wide.rs:332-334`).

**[9] Rerank Jev call.** `jev/rerank.rs` policy `rerank-questions-v1` (`:24`):

| Question key | Type |
|---|---|
| `rerank` | Choice over the shortlist + `__none__` (`:25, 28-31`) |
| `fits::<option>` | one independent Noul per real candidate (`:26, 33-36`) |

Skill text is embedded only as JSON-quoted data after fixed instructions; answers resolve only through the local option map (`rerank.rs:7-11`). `__none__` cannot be a `SkillId` or `OptionId` (`identity.rs:113-115, 136-138`).

**[10] Post-rerank eligibility.** `after_rerank` (`eligibility.rs:225-295`): membership must match the shortlist exactly or `unavailable` / `RosterChanged` (`:238-245`). Then fit ≥ `fits` threshold (default 0.30) or `Abstain(LowFit)` (`:258-272`). Then **each candidate's own rerank probability must strictly beat `__none__`**; ties abstain (`:274-289`, `NoShortlistMatch`).

**[11] Local score.** `scoring::rank` (`scoring.rs:166-196`): softmax over `ln(clip(rerank)) + w_fit·log-odds(fit) + …` (`:134-139`). Defaults `w_fit=1`, `w_prior=0`, `w_phase=0` (`:48-49, 64-68`). A score is "a relative local weight, never a calibrated probability of usefulness" (`scoring.rs:3-5`). Called at `pipeline.rs:2259`.

**[12] Publication revalidation.** `validate_advisory_publication` (`pipeline.rs:2318+`) rechecks policy + roster dependencies on *every* advisory outcome, including a negative recommendation (`:2318-2320`). Cache reuse does not skip this.

### What the loop does *not* close at this SHA

| Designed next step | Source that names it | Wired in this binary? |
|---|---|---|
| `sr hook claude` ingest + `hookSpecificOutput` | README `:350`, `adapter.rs:22-23, 592-614`, `overlay.rs:103-113` | **No.** `IMPLEMENTED_COMMANDS` = `capabilities, demo, doctor, ledger, rank, replay, roster` (`capabilities.rs:17-18`). `ClaudeHookStdin` is refused (`pipeline.rs:798-804`). `OutputDocument` **rejects** `hookSpecificOutput` as inconsistent (`output/mod.rs:229-231, 496-507`). |
| `sr install-hook` / `uninstall-hook` | README `:363-364`; planned P6 (`adapter.rs:510-511`) | **No.** |
| Persist ranking → observe loads → judge useful/harmful/neutral → feedback proposal → calibrate | ledger DDL (`storage/ledger.rs:185-274`) | **Schema yes, write path no.** `record_ranking_event` is called only from `tests/ledger_*.rs`. `pipeline.rs` never mentions it. `Evaluated::persistence` returns `"unavailable"` because "this build has no observation ledger yet" (`pipeline.rs:3152-3180`). CLI `sr ledger` is `init` / `migrate` / `status` only (`cli.rs:303-365, 551-748`). |
| `sr feedback` / `observe` / `stats` / `eval` / `calibrate` | README `:365-373`; planned P5/P8 (`adapter.rs:512-520`) | **No.** `src/evaluation.rs` is a library consumed only by `tests/evaluation_frame_contract.rs`. `cli.rs` has no `evaluation::` import. |

So the **process pattern** is a closed loop. The **product at `6a74cca`** is an open arc: rank can decide; it cannot yet inject advice into a harness or learn from what happened next.

---

## 2. Every module and which loop step it owns

Single package. `src/lib.rs:4-29` is the module list (`storage` is `#[cfg(target_os = "linux")]`).

| Module | Path | Loop step it owns | Key symbols |
|---|---|---|---|
| `main` | `src/main.rs` | entry clock before parse/I/O | `EntryClock::capture`, `cli::run` |
| `cli` | `src/cli.rs` | command surface | `Command::new("rank"\|"doctor"\|"roster"\|"capabilities"\|"demo"\|"replay"\|"ledger")`; **no** `hook` / `feedback` / `eval` |
| `runtime` | `src/runtime.rs` | deadline + publication gate | `EntryClock`, `admit_publication`, `ProcessInvocation` |
| `config` | `src/config.rs` | knobs | `HookMode::{Shadow,Advisory}` (`:279-298`), `SettingKey::HookMode` (`:91`), default shadow (`:872`) |
| `effects` | `src/effects.rs` | one policy → every restriction | `EffectGate`, `Scope::{Rank,LocalInspection}`, `History` |
| `adapter` | `src/adapter.rs` | hook *contract*, not hook *runtime* | `USER_PROMPT_SUBMIT` (`:22`), `USER_PROMPT_EXPANSION` (`:23`, unsupported), `ClaudeHookEvent`, `ClaudeUserPromptSubmit`, `AdviceDisposition`, `foundation_capabilities` planned CLI (`:503-523`) |
| `context` | `src/context/mod.rs` | session-context | `PrivateText`, `NormalizedContext`, `CurrentRequest`, `Role` |
| `context::source` | `source.rs` | source selection | `SourceOptions.claude_hook`, `SourceTarget` |
| `context::jsonl` | `jsonl.rs` | transcript tail | `snapshot_jsonl`, `CursorKind::Ranking` |
| `context::cass` | `cass.rs` (unix) | archive sessions | (paired with `pipeline/cass_source.rs`) |
| `context::discovery` | `discovery.rs` (unix) | Claude session inventory | `discover_claude_sessions`, `transcript_session` |
| `context::overlay` | `overlay.rs` | hook prompt overlay | `apply_claude_prompt_overlay`, `ClaudeOverlayRequest` |
| `context::anchor` | `anchor.rs` | task identity | `resolve_task_anchor`, `AnchorResolution`, `is_terse_continuation` |
| `context::branch` | `branch.rs` | active leaf + loaded skills | `resolve_active_branch`, `evaluate_loaded_skill_eligibility` |
| `context::render` | `render.rs` | provider-facing reduction | `render_context_and_receipt`, `strip_advisory_from_non_user` |
| `context::signals` | `signals.rs` | project signals | `collect` (trusted PATH `/usr/local/bin|/usr/bin|/bin`, `pipeline.rs:100`) |
| `context::tool` | `tool.rs` | tool↔skill association | `associate_tool_events`, `extract_load_observations` |
| `pipeline` | `src/pipeline.rs` | **the loop** | `execute_pipeline`, `rank_once`, `build_abstain_document`, `build_ranked_document`, `build_explicit_document` |
| `pipeline::roster` | `pipeline/roster.rs` | discovery adapter for rank | `Source::load`, `capture_dependencies` |
| `pipeline::cass_source` | `pipeline/cass_source.rs` | cass ingest | `read` |
| `roster` | `src/roster/mod.rs` | skill identity | `InvocationName`, `UsageKind`, `Visibility` |
| `roster::discovery` | `discovery.rs` | roots | `claude_code_plan` |
| `roster::resolution` | `resolution.rs` | bindings + option map | `AdvisorySkill`, `ResolvedRoster`, `OptionMap` |
| `roster::explicit` | `explicit.rs` | require/exclude | `resolve_explicit_requirements`, `parse_prompt_directives` |
| `roster::frontmatter` | `frontmatter.rs` | SKILL.md | `parse_skill_metadata`, description caps |
| `roster::retrieval` | `retrieval.rs` | Quill prefilter | `retrieve`, `QueryInput`, `RetrievalBudget` |
| `roster::revalidation` | `revalidation.rs` | publication fence | `revalidate_claude` |
| `roster::snapshot` / `inspect` / `import` / `evidence` | matching files | inspect/diff/import | `sr roster --snapshot\|--diff` |
| `eligibility` | `src/eligibility.rs` | admit / after_rerank | `AbstainReason`, `UnavailableReason`, `Verdict`, `admit`, `after_rerank` |
| `jev` | `src/jev/mod.rs` | Jev surface | re-exports codec / endpoint / admission |
| `jev::wide` | `wide.rs` | stage-1 questions + gate | `NONE_OPTION`, `WHICH`, `GATE_*`, `PHASE`, `STUCK`, `needs_skill`, `WideDecision` |
| `jev::rerank` | `rerank.rs` | stage-2 questions | `RERANK`, `FIT_PREFIX`, `RerankOutcome` |
| `jev::codec` | `codec.rs` | wire schema | `Request{model,state,questions}`, `Response`, `Question::{Choice,Noul}`, `SUM_TOLERANCE=0.1` |
| `jev::client` | `client.rs` | one HTTPS attempt | `JevTransport`, `JevClient`, no internal retry |
| `jev::retry` | `retry.rs` | caller-owned retry | `RetrySession`, `RetryAfter` |
| `jev::endpoint` | `endpoint.rs` | origin + `/v1/systemone` | `DEFAULT_TYPESAFE_ENDPOINT`, `SKILLRANKER_USER_AGENT` |
| `jev::admission` | `admission.rs` | attempt budget | `AttemptBudget`, `RankingStage::{Wide,Rerank}` |
| `scoring` | `src/scoring.rs` | local order | `Weights`, `Input`, `rank`, `utility` |
| `output` | `src/output/mod.rs` | public envelope | `Decision::{Ranked,Explicit,Abstain,Unavailable}`, `SCHEMA_VERSION=1` |
| `output::table` | `table.rs` | TTY | `render_abstain_view` → `DECISION: ABSTAIN` |
| `output::trace` | `trace.rs` | `--explain` | `StageTrace`, `TraceStage` |
| `demo` | `src/demo.rs` | offline fixtures | `DemoCase::{Useful,None,Explicit,Unavailable}` |
| `replay` | `src/replay.rs` | offline recompute | `ReplayCase`, `make_recomputed_abstain`; `__none__` cannot be a candidate (`:298-300`) |
| `evaluation` | `src/evaluation.rs` | P5 frame joiner (library only) | `RelevanceClass::{TrueAbstain,FalseAbstain,…}`, `compute_metrics` — **does not read `synthetic_cases.v1.jsonl`** |
| `storage` / `storage::ledger` | `src/storage/ledger.rs` (Linux) | observation store *schema* | tables below; `record_ranking_event` / `record_observation` / `record_judgment` / `record_feedback_proposal` |
| `cache` | `src/cache/` | exact response cache + leases | `RequestStage::{Wide,Rerank}`, `compute_request_fingerprint` |
| `privacy` | `src/privacy/` | redaction + consent | `admit_provider_attempt`, `NetworkConsent`, `Redactor` |
| `readiness` | `src/readiness.rs` | `sr doctor` | hook mode + ledger + credential *presence* (not auth) |
| `capabilities` | `src/capabilities.rs` | `sr capabilities --json` | `IMPLEMENTED_COMMANDS`, schema registry (`:98-108`) |
| `identity` | `src/identity.rs` | IDs | `SkillId` rejects `__none__` |
| `authorized_read` | `src/authorized_read.rs` | bounded file reads | `AuthorizedRoots` |
| `blocking` | `src/blocking.rs` | blocking-leaf pool | `run_blocking_leaf` |
| `limits` | `src/limits.rs` | caps | `HOOK_ADDITIONAL_CONTEXT_SCALARS`, `HOOK_STDIN_BYTES` |
| `subprocess` | `src/subprocess.rs` | child boundary | (signals / git inspect) |
| `transport.rs` | `src/transport.rs` | **not** in `lib.rs` | leftover origin notes; live path is `jev::endpoint` |

Dependencies that are *other people's crates*, not loop steps: `asupersync` (runtime + TLS), `frankensearch-core` / `frankensearch-quill` (retrieval), `rusqlite` (ledger), `clap`, `serde`.

---

## 3. Eval contract — and the gap that `src/` never reads the cases

### 3.1 Artifacts

| File | Schema | Status field |
|---|---|---|
| `tests/eval/evaluation_policy.v1.json` | `skillranker.evaluation_policy.v1` | `"frozen_contract_not_evidence"` (`:2-4`) |
| `tests/eval/synthetic_cases.v1.jsonl` | `skillranker.synthetic_case.v1` | 12 lines, one of each `case_kind` |
| `tests/eval/expected_values.v1.json` | `skillranker.expected_values.v1` | `"deterministic_contract_examples_not_measured_results"` (`:4`) |
| `tests/eval/README.md` | — | "They are not benchmark results." (`:5`) |
| `scripts/validate_eval_policy.py` | stdlib checker | requires `status == "frozen_contract_not_evidence"` (`:195`) |
| `scripts/test_eval_policy.py` | stdlib tests | `test_synthetic_cases_cannot_be_relabelled_as_holdout_evidence` (`:94-97`) |

`src/` never names any of those paths. `src/evaluation.rs` is a *different* schema (`schema_version: u64`, `CaseKey`, `JudgedLabel`) used only by `tests/evaluation_frame_contract.rs`. The Python validators are the only readers of the frozen cases.

### 3.2 Loss table (0 / 1 / 2)

From `evaluation_policy.v1.json:58-72` and the hand-checkable examples in `expected_values.v1.json:6-55`:

| Outcome | `y` nonempty? | Decision | Loss | Normalized `y = loss/2` |
|---|---|---|---|---|
| correct recommendation | yes | ranked ∈ Y | **0** | 0.0 |
| correct no-match abstention | no | abstain | **0** | 0.0 |
| **false abstention on positive** | yes | abstain | **1** | 0.5 |
| incorrect recommendation | yes | ranked ∉ Y | **2** | 1.0 |
| needless recommendation on no-match | no | any skill | **2** | 1.0 |
| operationally unavailable on attempted case | — | unavailable | **2** | 1.0 |

Rationale, quoted from the policy (`:71`): *"A loss that charges only wrong emitted suggestions is invalid because always abstaining would minimize it without helping positive cases."*

`always_abstain_counterexample_required: true` (`:70`). The toy counterexample (`expected_values.v1.json:56-74`) is 6 cases (4 positive / 2 no-match): always-abstain total loss 4, mean 0.667; a candidate policy total 2, mean 0.333. Conclusion: `always_abstain_fails_positive_case_value`.

That 0.667 is **not** the 0.833 in our oracle. 0.833 is `10 × 1 / 12` on the *12-case* file (10 positives, always abstain). Both numbers are internally consistent; they are different cohorts. Cite the cohort.

### 3.3 Promotion gate ≥ 0.90 (and the rest of the bar)

`evaluation_policy.v1.json:133-173`:

| Gate | Number | Notes |
|---|---|---|
| `top_one_precision.minimum_rate` | **0.90** | plus Wilson lower endpoint ≥ 0.80 |
| `positive_case_suggestion_rate.minimum_rate` | 0.80 | **`abstention_counts_as_miss: true`** |
| `needless_suggestion_rate.maximum_rate` | 0.05 | Wilson upper ≤ 0.10 |
| overflow coverage @ 254 | 0.98 | min 50 overflow positives |
| shortlist coverage @ M | 0.95 | |
| relevance cohort | 300 primary / 150 positive / 100 no-match / 50 near-miss | *not* the 12 synthetic cases |
| controlled harm | 150 families, one-sided 95% UB ≤ 0.02 | separate cohort |
| operational fallback | 500 hook invocations, fallback ≤ 0.05 | separate cohort |

Split `diagnostic_synthetic` (`:53-56`): allowed use = "Contract and validator oracles only." Forbidden = "No promotion, calibration, or statistical quality claim." The 12 cases are all `split: diagnostic_synthetic`. Relabelling one as holdout is a validator hard-fail (`test_eval_policy.py:94-97`).

### 3.4 The 12 cases (kinds, not scores)

One line each, `case_kind` unique (`synthetic_cases.v1.jsonl`, 12 records):

`positive_advisory`, `no_match_advisory`, `near_miss_advisory`, `multiple_valid_advisory`, `explicit_request`, `planning_or_explanation`, `loaded_reference_empty_y`, `repeatable_workflow_nonempty_y`, `overflow_retrieval`, `compacted_or_terse_context`, `roster_change`, `operational_failure_semantics`.

Y is `acceptable_additional_invocations_y`. Already-available references can empty Y; repeatable workflows can remain in Y (`evaluation_policy.v1.json:36`). Explicit requests are scored separately so exact-name cases do not inflate model quality (`:37`).

### 3.5 What `src/evaluation.rs` *would* compute if pointed at a frame

`RelevanceClass` (`evaluation.rs:201-211`): `ExplicitMatch|ExplicitMismatch|TruePositive|FalsePositive|NeedlessSuggestion|TrueAbstain|FalseAbstain|OperationalFailure|Unjudged`.

Classification (`:674-686`): empty Y + suggestion → `NeedlessSuggestion`; empty Y + no top-1 → `TrueAbstain`; top-1 ∈ Y → `TruePositive`; else if `decision == "abstain"` or `relevance_abstention` → `FalseAbstain`; else `FalsePositive`.

`compute_metrics` (`:697-825`) exposes `false_abstention_rate` over positive advisory cases (`:805-808`) and `top1_precision` over *emitted* advisory suggestions (`:787-790`) — i.e. abstentions drop out of the precision denominator, which is why the policy also requires `positive_case_suggestion_rate` with `abstention_counts_as_miss: true`.

**It is still not a reader of `synthetic_cases.v1.jsonl`.** No CLI `sr eval`. Planned earliest phase P5 (`adapter.rs:518`).

---

## 4. Abstention semantics — false abstention is the cheap error

### 4.1 Product decisions (what `sr rank` can emit)

`output::Decision` (`output/mod.rs:34-39`): `ranked` | `explicit` | `abstain` | `unavailable`.

Exit 0 covers ranked, explicit, and **valid abstention** (README `:589`; `validate_decision` returns `CliExit::Success` unless `unavailable`, `output/mod.rs:508-515`).

Abstain *reasons* (product, not eval):

| Reason string | Source | When |
|---|---|---|
| `low-fit` | `AbstainReason::LowFit` (`eligibility.rs:24, 36`) | last candidates failed `fit ≥ threshold` |
| `already-loaded` | `:26, 37` | every survivor is a proven-present reusable reference |
| `excluded` | `:28, 38` | restrictions / explicit exclusions removed everyone |
| `no-shortlist-match` | `:30, 39` | no candidate's rerank p beat `__none__` (ties included) |
| `low-need` | `WideDecision::LowNeed` (`wide.rs:329-330`; `pipeline.rs:1972-1974`) | `needs_skill < gate` after wide; **no rerank** |
| `local-exclusion` | fixture `output-abstain.v1.json:5` | documented envelope example |

`unavailable` is a different class: `explicit-resolution`, `empty-roster`, `roster-changed` (`eligibility.rs:45-60`). Operational unavailability costs **2** in the eval table, not 1.

### 4.2 Why "false abstention = 1" is the process to steal

The loss table makes always-abstain *visible* and *worse* on positives, but still cheaper than a wrong pick. Our live oracle on their 12 cases (`skillranker-corpus-measured-20260919.md`) observed exactly that shape: 8/10 positives correct, both no-match cases correctly abstained, both failures = **false abstention** (overflow paraphrase; operational-failure wording). Mean loss 0.167 vs always-abstain 0.833. Gate 0.90 missed by one case.

That is a **process** result about Jev-on-their-labels, not a skillranker-product result. Their ranker adds roster validation, retrieval, two-stage questions, and `__none__` ties. Those could move the number either way. The contract forbids treating n=12 `diagnostic_synthetic` as holdout evidence.

### 4.3 `__none__` is a sentinel, not a skill

- Wide / rerank option id: `NONE_OPTION = "__none__"` (`wide.rs:35`).
- `SkillId::new` / `OptionId::new` reject it (`identity.rs:113-115, 136-138`).
- Replay refuses a candidate whose `skill_id == "__none__"` (`replay.rs:298-300`).
- Demo case `none`: "An abstain decision where the sentinel none option wins" (`demo.rs:7`).

### 4.4 Hook-mode quiet failure (designed, not shipped)

README `:622-623`: "The dedicated hook maps recommendation failures to quiet exit-zero behavior so it never blocks the agent." `HookMode::Shadow < Advisory` (`config.rs:277-281`). Default is shadow (`:872`). `additional_context_allowed` caps hook text at `HOOK_ADDITIONAL_CONTEXT_SCALARS` and at most one suggested invocation name (`adapter.rs:754-770`, `MAX_SUGGESTED_INVOCATION_NAMES = 1` at `:21`). None of this is reachable: `sr hook` is planned P6, and the output contract currently **forbids** `hookSpecificOutput` on a decision document.

---

## 5. JSON schemas (the ones the loop actually speaks)

### 5.1 Jev wire (`jev/codec.rs`)

Request (`:149-153`):

```json
{ "model": "jev-latest", "state": <any JSON>, "questions": { "<id>": Question } }
```

`Question` tagged `type` (`:73-83`):

```json
{ "type": "choice", "instructions": <Value>, "criteria": { "<option>": "<description>" } }
{ "type": "noul",   "instructions": <Value>, "criteria": { "true": "...", "false": "..." } }
```

Response decode (`:216-273`) requires: answer keys == request keys; Choice keys == criteria keys; every p finite in range; `|Σp − 1| ≤ 0.1` (`SUM_TOLERANCE`, `:20`); `p[choice] == max(p)` else `InvalidChoice`. Missing `answers` / type mismatch → error, never a partial act.

Capabilities lists the question-set versions (`capabilities.rs:106-107`): `wide_questions: "wide-questions-v1"`, `rerank_questions: "rerank-questions-v1"`.

### 5.2 Rank decision envelope (`output/mod.rs`, fixtures `tests/fixtures/output-*.v1.json`)

Required on a full decision (not a pre-input failure): `schema_version` (1), `event_id`, `decision`, `reason`, `harness`, `context_quality`, `quality{prompt_complete,task_anchor_known,history_windowed,attachments_omitted,source_gaps}`, `roster{total,eligible,wide_candidates,shortlist,partial,retrieval,provenance{snapshot_id,policy_version,wide_set_id,rerank_set_id}}`, `needs_skill`, `choice_confidence`, `none_probability`, `phase`, `skills[]`, `omitted_rank_mass`, `cache`, `model`, `usage`, `persistence`, `warnings`, `warnings_omitted`, `elapsed_ms`. `unavailable` adds `error{code,kind,message,hint,retryable}`.

Forbidden on a decision: `kind`, `actionable`, `run_status`, `gate_status`, **`hookSpecificOutput`** (`output/mod.rs:496-507`).

`skills[]` item shape (ranked fixture): `rank`, `skill_id`, `name`, `invocation_name`, `rank_score`, `rerank_probability`, `wide_probability`, `fits`, `path`, `content_hash`.

`persistence` ∈ {`disabled`, `unavailable`} at this SHA (`pipeline.rs:3175-3180`). Not `recorded`.

### 5.3 Hook stdin (designed)

`ClaudeUserPromptSubmit::from_value` (`adapter.rs:659-697`) requires:

```json
{
  "hook_event_name": "UserPromptSubmit",
  "prompt": "<string>",
  "prompt_id": "<optional EventId>",
  "session_id": "<optional>",
  "transcript_path": "<optional>",
  "cwd": "<optional>"
}
```

`UserPromptExpansion` parses as `UnsupportedEvent` (`adapter.rs:601, 609-611`). Any other name is `UnknownEvent`. Additive unknown fields: `RejectUnknown` or `RetainAdditive` (`:690-695`). Byte-capped by `HOOK_STDIN_BYTES`.

### 5.4 Ledger (Linux schema, not yet written by rank)

`sr-ledger-v1`, application id `0x53524C47` ("SRLG"), file `$XDG_DATA_HOME/sr/ledger.sqlite3` (`ledger.rs:31-32, 4-6`). Tables (`:276-288`):

| Table | Discriminants |
|---|---|
| `ranking_events` | `decision IN ('ranked','explicit','abstain','unavailable')`; `mode_channel`; `exposure_state IN ('generated','prepared','emitted','acknowledged','unknown')` |
| `ranking_candidates` | `stage IN ('wide','rerank')` |
| `provider_attempts` | `stage IN ('wide','rerank')`; `status IN ('admitted','sent','completed','failed','unknown')` |
| `observations` | `evidence_state IN ('attempted','loaded','censored')` |
| `judgments` | `label IN ('useful','harmful','neutral')` |
| `feedback_proposals` | `status IN ('unresolved','historically_absent','rejected','adopted')` |
| `calibrations` | `split IN ('train','validation','holdout')` |
| `session_cursors` | `cursor_kind IN ('ranking','observation')` |
| `roster_snapshots` | `membership_coverage IN ('complete','unknown','partial')` |

This is the **feedback loop as a schema**. Rank does not insert into it. `sr feedback EVENT_ID --skill SKILL_ID --verdict useful` is README prose (`README.md:367`), not a `Command::new`.

### 5.5 Capabilities document

`sr.capabilities.v1` (`capabilities.rs:15`). Implemented: help, version, + `IMPLEMENTED_COMMANDS`. Planned (still): `hook`, `install-hook`, `uninstall-hook`, `stats`, `observe`, `feedback`, `snooze`, `budget`, `eval`, `calibrate`, `tui`, `gaps` (`adapter.rs:505-522`). Adapter kinds: `normalized_context` (implemented), `claude_hook` (unverified, `on_default_hook_path: true`), `cass_session` (unverified). Conformance dimensions (`adapter.rs:67-77`): `prompt_timing`, `branch_identity`, `visibility`, `restrictions`, `compaction`, `load_evidence`, `hook_output`, `deadline`, `delivery` — all `not_evaluated` in the shipped fixture.

### 5.6 Replay case (`--save-case`)

`ReplayCase` (`replay.rs` + `pipeline.rs:347-356`): `schema_version`, `case_id`, `created_at_unix_ms`, `manifest`, `captured_request`, `recorded_responses{wide,rerank}`, `local_evidence`, `historical_decision`. Forbidden in hook mode (`pipeline.rs:246-251`). This is how a *single* live rank becomes an offline artifact — it is **not** a dump of `synthetic_cases.v1.jsonl`.

---

## 6. Hook event names and advice gate (designed surface)

| Symbol | Value | Disposition |
|---|---|---|
| `USER_PROMPT_SUBMIT` | `"UserPromptSubmit"` | `AdviceDisposition::Eligible` (`adapter.rs:22, 608`) |
| `USER_PROMPT_EXPANSION` | `"UserPromptExpansion"` | `Disabled(UnsupportedEvent)` (`:23, 609-611`) |
| any other `hook_event_name` | — | `UnknownEvent` |

`AdviceDisposition` (`:216-218`): `Eligible` | `Disabled(AdviceBlockReason)`. Native advice additionally requires real-harness smoke evidence on every `NATIVE_ADVICE_DIMENSIONS` cell (`:79-88, 343-396`). The Claude adapter is shipped `SupportClass::Unverified` (`:538-549`), so `native_advice` is disabled until those cells pass. That is the honest "we have a hook contract, we have not proven the harness" state.

`install.sh:46`: installer "does not … install hooks". Preview/apply is the documented `--apply` pattern (README `:381`) — also unshipped.

---

## 7. What `omp-jev-route` / `jev-usage-router` / `omp-jev-preaction` are missing vs this loop

This is a **gap list**, not a build order, and not a promotion.

### 7.1 Side-by-side

| Loop piece (skillranker) | `omp-jev-route` | `jev-usage-router` | `omp-jev-preaction` |
|---|---|---|---|
| Session-context ingest (transcript / cass / overlay) | latest user string from `context.messages[]` (`work/omp-jev-route/src/index.ts:45-68`). `turn_start` is content-free (measured). | `goal` + optional `completedWork` string. No session. | `tool_call.input.command` only. |
| Roster (visible, versioned, exclusions, already-loaded) | **none** | **none** (fixed 4 actions) | **none** |
| Explicit require/exclude before the model | **none** | **none** | **none** |
| Local admit that can abstain *without* a paid call | **none** | kill-switch bypass (env/config), not an abstention | regex miss → `preaction_pass` |
| Two-stage Jev (wide gate + rerank + `__none__`) | two Nouls, no Choice, no sentinel (`QUESTIONS` `:29-34`) | one Choice, no `__none__`; low confidence → `bypass` (`router.mjs:109-110`) | **no Jev** (by ruling) |
| Rank / abstain as a first-class decision | `suggested_tier` ∈ {heavy, light, default}; never abstains from advising | `action` ∈ {local, research, browser, bypass} | fire / pass |
| Fail-safe direction named | **silent** (`return undefined` every path, `:106-109`) | fail → `bypass` (safe-ish for spend; not a labelled abstain) | fail → `undefined` (observe-only) |
| Hook injection (`hookSpecificOutput` / block) | observe-only; never routes (`README.md:5-8`) | no hook; caller must honor in `active` | observe-only; dcg remains the blocker |
| Feedback loop (observe → judge → proposal → calibrate) | `appendEntry` decision rows; no join to outcome | daily JSONL log; no judgment labels | decision rows; no labels |
| Eval contract (Y, 0/1/2, always-abstain, ≥0.90) | **none**. Live labels are 10 turns / 24 repeats of 1 turn. | 7-step smoke, not a loss table | 6 tests, regex RED arms |
| Cheap-error abstention (loss 1 vs 2) | no abstain class | `bypass` conflates "unclear", "irreversible", and "unconfigured" | no abstain class |
| `__none__` / "answer directly" option | absent (the two questions always fire when a prompt exists) | `bypass` is the nearest analogue, but it is also the kill-switch and the error path | N/A |
| Persistence honesty (`recorded` vs `unavailable`) | rows exist or they don't; no `persistence` field | log write is best-effort | same |
| Shadow vs advisory | always shadow (cannot act) | `mode: shadow\|active` (`config.json`) | always shadow |

### 7.2 The three missing pieces that actually matter

1. **A roster.** Skillranker's interesting question is "which of *these* skills, or none." Route asks "is this turn hard." Usage-router asks "local / research / browser / bypass." Preaction asks "does this bash line match a wipe regex." None of ours binds a live, versioned, excludable candidate set, so none of ours can have a false-abstention-on-positive.

2. **A typed abstain that is cheaper than a wrong pick, and an always-abstain control that makes that claim checkable.** Usage-router's `bypass` is the closest we have, and it is overloaded (kill switch + low confidence + transport failure + genuine "don't"). Skillranker separates `abstain` (relevance) from `unavailable` (operational) from `explicit` (user already named it). Our oracle already showed what happens when you invent a second gate: 11/12 abstentions, a number that measured the question wording.

3. **The closed loop.** Rank without observe/judge/feedback is a smoke call that cannot improve. Skillranker has the *schema* for that loop and has not wired the writers. We have JSONL append and have not defined Y. Copying their schema without a writer would repeat their own `frozen_contract_not_evidence` gap. Copying a writer without Y would be a log, not a loop.

### 7.3 What we should *not* copy from the README

`README.md` documents `sr hook claude`, `sr install-hook`, `sr feedback`, `sr eval`, `sr calibrate` as if they were the binary. `capabilities.rs:17-18` and `cli.rs:18-365` say they are not. We already burned a session blaming upstream for a stale pin (`skillranker-20260919.md` retraction). The control is `IMPLEMENTED_COMMANDS` + `rg Command::new src/cli.rs`, not the README table.

---

## 8. Implemented vs planned — machine-readable

`sr capabilities --json` is the authority (`capabilities.rs:52-72`): a foundation `planned_cli` entry is marked `implemented` only if its name is in `IMPLEMENTED_COMMANDS`.

| Command | Phase (planned) | At `6a74cca` |
|---|---|---|
| `rank`, `doctor`, `roster`, `capabilities`, `demo` | P2–P4 | **implemented** |
| `replay` | P5 | **implemented** |
| `ledger` (`init`/`migrate`/`status`) | P5 | **implemented** (admin only; no rank writer) |
| `hook`, `install-hook`, `uninstall-hook` | P6 | planned |
| `stats`, `observe`, `feedback`, `eval` | P5 | planned |
| `snooze`, `budget` | P6 | planned |
| `calibrate` | P8 | planned |
| `tui`, `gaps` | P9 | planned (`tui` feature flag reserved, `Cargo.toml:17-18`) |

`src/adapter.rs:4`: "These types freeze first-supported source boundaries and the advice gate. They do not read transcripts, start cass, install hooks, or emit advice." That sentence is still accurate for the adapter module. The pipeline now reads transcripts and cass. It still does not install hooks or emit advice.

---

## 9. Claim level and boundary

| Claim | Level | Evidence |
|---|---|---|
| Public HEAD is `6a74cca` | `[oracle]` (GitHub) | `gh api repos/Dicklesworthstone/skillranker/commits/main` |
| `src/` does not read `synthetic_cases.v1.jsonl` | `[test]` (search) | `rg` over `src/` empty; Python validators are the only readers |
| Rank pipeline implements context → roster → Jev → rank/abstain | `[test]` (source read) | `pipeline.rs:542-2316` |
| Hook / feedback / eval CLI are unimplemented | `[test]` (source read) | `capabilities.rs:17-18`, `cli.rs` subcommands |
| Ledger rank-write is unimplemented | `[test]` (source read) | `record_ranking_event` only in tests; `persistence() == "unavailable"` |
| False abstention costs 1, wrong pick costs 2 | `[oracle]` (their contract) | `evaluation_policy.v1.json:58-65` |
| Jev-on-their-12-cases mean loss 0.167 / top-1 0.800 | `[live]` (ours, prior) | `skillranker-corpus-measured-20260919.md` — **not re-run this pass** |
| Skillranker the product clears 0.90 | **NOT_RUN** | requires their binary + keyed rank + a cohort the contract itself says n=12 cannot be |
| Anything promoted | **no** | `VERDICT.md` / `STATUS.tsv` untouched |

**Boundary:** public GitHub only. No private repo access. No `sr` binary executed. No TypeSafe call. No file in the vendored clone (if any) was edited. `/tmp/skillranker-public` is disposable local scratch.

**Retry condition for "the loop is closed":** `IMPLEMENTED_COMMANDS` contains `hook` and `feedback`; `pipeline.rs` calls `record_ranking_event` on a successful decision; `rg synthetic_cases src/` is nonempty *or* `sr eval --dataset tests/eval/synthetic_cases.v1.jsonl` exists and the policy status field is no longer the only reader. Until then, steal the *process* (typed abstain, 0/1/2, always-abstain control, gate that abstention-counts-as-miss), not the product.

---

## 10. What a later pane should do with this (selection, not a plan-to-plan)

Per the autonomous loop: this pass **closes the archaeology**. It does not license a skill-ranker port.

If a later unit wants to *use* the process:

- The cheapest adoption that has a consumer today is **naming abstain vs unavailable vs wrong-pick** on an existing observe-only surface (`omp-jev-route` or `jev-usage-router` logs), with an always-abstain control computed on a corpus we did **not** author. That is a policy + a receipt, not a new tool.
- Building `sr hook` ourselves, or a roster-backed ranker, is a new product. Rule 12 says adopt the *mechanism*; the mechanism that is missing on their side is the writer that points `src/` at the cases they already froze. We do not owe them that writer, and we do not promote on a contract they marked `frozen_contract_not_evidence`.

`promoted=0`. Left that way on purpose.
