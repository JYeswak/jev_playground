# AXIS C — skillranker Jev harness vs R69

Pinned: `skillranker@abf909d` (`abf909d1e0106be8f296805af527711a8fc7d158`).
Lane: offline read of vendored source. **His `cargo test` was not run.**
No live Jev call. No edit inside the clone.

Line counts at this SHA (user's briefing vs disk):

| file | briefing | `wc -l` |
|---|---:|---:|
| `tests/jev_smoke.rs` | 942 | **942** |
| `tests/jev_retry.rs` | 869 | **864** |
| `tests/jev_contract.rs` | 718 | **718** |
| `tests/adapter_contract.rs` | 793 | **793** |
| `tests/p3_gate.rs` | 783 | **783** |
| `tests/p4_gate.rs` | 713 | **712** |
| `tests/p1_gate.rs` | (unmentioned) | **319** |
| `tests/p2_gate.rs` | (unmentioned) | **403** |

~2500 lines of files *named* Jev. What they certify is below.

---

## Verdict (one sentence)

He built a **strict client** around Jev and **assumed the seat**. He never measured whether Jev beats a deterministic baseline. R69 is the stronger *result*. His harness is the stronger *plumbing*. Adopt the plumbing (Rule 12); do not treat the line-count as an accuracy oracle (Rule 13).

His own tree already says this: `docs/reality-check-bridge-plan.md:52` — *"Demonstrated usefulness and operational benefit | UNPROVEN: no accepted relevance, paired harm or representative hook cohorts … fixtures and unit counts cannot pass these gates."*

---

## (1) `jev_contract.rs` — schema and numeric invariants, not accuracy

File header (`tests/jev_contract.rs:1-5`): *"Integration and property tests for TypeSafe Jev distribution, confidence, and usage validation **before scoring**."* Boundary `p1_distribution_validation` / `sr-roadmap-l1i.2.6`.

Every test decodes **hand-built JSON** through `req.decode_response` (`:89-91`, `valid_response_json` at `:63-87`). There is no HTTP, no key, no labelled corpus.

| test | lines | what it asserts |
|---|---|---|
| `distribution_sum_and_confidence` | 98–229 | sum≈1 within 1e-4; live-shaped 0.99 total accepted and **renormalized**; 1.15 / 0.85 / zero-sum rejected; confidence ∈[0,1] |
| `exact_argmax_validation_and_deterministic_tie_breaking` | 235–330 | chosen id ∈ argmax set; ties broken deterministically |
| `unknown_usage_preserved_across_errors` | 336–409 | usage integers; unknown usage kept on terminal error |
| `e2e_case_nonfinite_rejected` | 415–521 | NaN/Inf/missing/type-mismatch → `CodecError` |
| `e2e_case_distribution_sum_tolerance` | 527–585 | 0.99 ok; drift beyond 0.1 rejected; 255-option bound |
| `response_cap_and_depth_limits` | 591–619 | 2 MiB / depth |
| `duplicate_keys_in_response_strictly_rejected` | 625–682 | duplicate JSON keys |
| `error_bodies_sanitized_without_raw_payload_leaks` | 688–718 | canary token never in diagnostics |

**Accuracy:** none. No gold label. No "apple is the fruit" check. The choice in the fixture is whatever the fixture writer put in the JSON (`choice: "skill_alpha"` at `:109`). A model that always returns `__none__` with a valid simplex would pass this file.

P1 gate repeats the same class with canned bytes (`tests/p1_gate.rs:165-183`): a literal `tool_a` 0.70/0.20/0.10 body, decoded locally. Still not a live answer.

---

## (2) `jev_smoke.rs` — injected? no. skip-as-pass? **not anymore.**

Header (`:1-5`): *"A small live success does not qualify provider capacity."*

**Ordinary `cargo test` does not spend money.** Four paid tests are `#[ignore]`:

- `:239-240` `budgeted_live_contract_smoke`
- `:617-618` `budgeted_live_capacity_shapes`
- `:626-627` `budgeted_live_rerank_shape`
- `:841-842` `budgeted_live_distribution_diagnostic`

Ignored tests are **absent from the green suite**, not skipped-inside-and-passed. That is closer to our `NOT_RUN` than to AGENTS.md's broken silent-skip.

**If you force them without consent/key, they fail.** `explicitly_selected_live_test_cannot_pass_without_consent_or_key` (`:129-196`) spawns the test binary with `--ignored --exact <name>`, `env_clear`, and asserts `!output.status.success()` (`:173-175`) plus a static diagnostic. Consent is checked **before** credential lookup (`live_api_key` `:84-103`, `live_consent_precedes_credential_lookup` `:105-127`). Comment at `:84`: *"Never load a repository .env."*

Offline tests in the same file prove fail-closed admission (`admission_gates_fail_closed_without_consent_or_credential` `:382-417`) and request bounds. They are policy tests, not Jev tests.

**What the live smoke would assert if armed** (`budgeted_live_contract_smoke` `:239-380`):

- HTTPS production origin, one admitted attempt, no retry loop (`:360`).
- Exactly 2 answers.
- `food_class` choice ∈ `{apple, carrot, __none__}` (`:306-310`) — **membership, not the fruit**.
- confidence and probabilities in [0,1]; sum within `SUM_TOLERANCE`.
- `fruit_health` noul in [0,1] (`:337-342`) — **0.0 passes**.
- token counts > 0.
- receipt field `"provider_capacity_qualified": false` (`:375`).

The prompt is a toy (`synthetic_contract_request` `:198-237`): *"An apple is a fruit; a carrot is a vegetable"* / *"Which candidate is described as a fruit?"*. A Jev that answers `carrot` or `__none__` still greens. That is not accuracy. It is "the wire returned a well-typed simplex."

**Historical trap, already documented in his tree:** `docs/reality-check-bridge-plan.md:445-449` — an earlier `budgeted_live_contract_smoke` was **not** ignored, defaulted `SKILLRANKER_LIVE_CONSENT` true, and *"With no key, the same test instead verifies refusal and passes. Therefore a green test does not establish a live contract."* Current `@abf909d` closed that class. Cite the current ignore+fail-closed, not the old skip-as-pass.

Transport: live path constructs `JevClient::new(EndpointConfig::production())` (`:253`). Not an injected fake. Recorded fixtures are not used for the live arm.

---

## (3) `jev_retry.rs` — deterministic, loopback TLS, not hammering

Header (`:1-3`): *"Production retry/admission paths over **real local TLS**, plus **deterministic scheduling** tests. All data and trust roots are public synthetic fixtures."*

Server: `tests/fixtures/jev-tls/retry_server.py` plus synthetic CA (`Server::new` `:103-147`). Bearer is canary `synthetic-retry-canary` (`:29`). No TypeSafe money.

**Retryable HTTP statuses** (exhaustive 100..600 scan at `:648-652`):

`429, 500, 502, 503, 504, 529`

**Not retryable:** 401, 403, 400, 422, 501, malformed (`authentication_validation_and_malformed_answers_do_not_retry` `:278-280`). Also Tls/Deadline/Cancelled/Protocol/Redirect (`:654-661`).

**Budget:** `transient_sequence_then_rerank_uses_exactly_four_admissions` (`:187-189`) script `["429:0", "529", "ok", "ok"]`. `four_transient_errors_never_send_a_fifth_attempt` (`:248-250`) script `["503", "502", "500", "504"]`. Four admissions is the cap; no fifth send.

**Backoff:** `retry_delay` is a pure function. With remaining 3s and 50ms unit, delay ∈ **100..=850 ms** for failures 1..=100 and several entropy values (`:603-614`). `Retry-After` HTTP-date parsing is frozen against `UNIX_EPOCH + 784111777` (`:570-590`). Unfittable/ambiguous headers → `RetryStop::DoesNotFitDeadline` / `InvalidRetryAfter` (`:329-332`).

This is the class we should **adopt**: classified retry, deadline-bounded, fail-closed on auth, tested against a local TLS script. It answers nothing about whether Jev's answers are useful.

---

## (4) P3 / P4 and the ladder

Gate files on disk: **only P1–P4**. No `p5_gate.rs` … `p9_gate.rs`.

| phase | gate file | what it actually gates | Jev? |
|---|---|---|---|
| **P0** | (no `p0_gate.rs`) | bootstrap, schemas, **frozen eval policy** (`contract_authority.toml` P0 / `sr-roadmap-l1i.1.8`) | none |
| **P1** | `tests/p1_gate.rs:2-8` | *"Transport and Runtime Readiness"* — clock, origin `https://api.typesafe.ai/v1/systemone` (`:92-107`), codec caps, canned-JSON decode, retryable() classification, WebPKI client construct (`:304-306`). **Does not POST.** | codec/client, not answers |
| **P2** | `tests/p2_gate.rs:2-7` | roster: every eligible option maps to a **currently authorized local file** whose bytes hash. Linux-only (`:!cfg(target_os = "linux")`). | none |
| **P3** | `tests/p3_gate.rs:2-11` | *"Exact-Session Context and Privacy Foundation"* — source selection, JSONL snapshots, Claude overlay, cass adapter, redaction, project signals. One test `all_p3_invariants_verified` (`:75`). | **none** |
| **P4** | `tests/p4_gate.rs:2-10` | *"Useful Core CLI, Pure Ranking, and Exact Cache."* Ranking is driven by `GateMockTransport` (`:44-75`, wired `:459`). Wide gen picks the first non-`__none__` key at confidence 0.85 (`:379-401`); rerank gen assigns 0.60/0.30/0.10 (`:432-443`). | **mocked** |
| **P5** | no gate file | observation ledger / replay / eval accounting (`contract_authority.toml` `:729-755`) | planned |
| **P6** | no gate file | Claude shadow hook (`:765-779`) | planned |
| **P7** | no gate file | advisory opt-in / evidence-backed rollout (`:789-899`) | planned |
| **P8** | no gate file | *"Accept learning only after held-out benefit"* (`:909-911`). Matrix still points at missing `tests/p8_gate.rs` (`contract_matrix.toml:1525`). | **planned, not executed** |
| **P9** | no gate file | later experiments (Quill passages, TUI, other harnesses) | planned |

`adapter_contract.rs` (793 lines) is **Claude/cass hook identity**, not Jev. Tests: capabilities fixture, unknown keys, stdin exclusivity, "fixture pass without smoke cannot authorize installed advice" (`:341-356`). Zero `JevClient`. Counting it in the "2500 lines of Jev testing" is a category error.

P4's word "Useful" is a phase slogan. The mock always returns a well-formed high-confidence winner. The CLI would "rank" even if real Jev were a coin.

---

## (5) Decisive: does he measure Jev vs a deterministic baseline?

**No executed comparison exists in this tree.**

What looks like one, and is not:

1. `tests/eval/evaluation_policy.v1.json:124-131` **names** baselines:
   `quill_only_lexical`, `typesafe_cookbook_style_selection`, `choice_only`, `fit_only`, `proposed_blend`, `always_abstain_negative_control`, `latest_request_only_context`.
2. `tests/eval/README.md:3-6,21` states they are **frozen contract artifacts**, *"not benchmark results"*, and *"do not contain … live Jev responses"*. A passing `scripts/validate_eval_policy.py` *"does not claim that SkillRanker has passed any relevance, harm, operational, live-provider, or release gate."*
3. `expected_values.v1.json:56-73` `always_abstain_counterexample` is a **hand-written 6-row arithmetic check** (always-abstain loss 4 vs candidate 2). Python recomputes the sums. No model is called.
4. `tests/eligibility_contract.rs:157-158` `each_returned_candidate_beats_none_on_its_own_probability` is local inequality on **injected** probabilities.
5. `tests/evaluation_numerics_contract.rs` `log_gamma_and_ln_beta_accuracy` is special-function accuracy, not Jev.

Beads assume the seat: *"Jev is the sole inference engine"* (repeated in `.beads/issues.jsonl`, e.g. `sr-roadmap-l1i.2`). P8 is where held-out benefit would live. P8 has no gate file. Reality-check row 20 (`docs/reality-check-bridge-plan.md:52`) marks usefulness **UNPROVEN**.

So: he **specified** the comparison we actually ran, then did not run it. We ran a weaker, smaller version (semantic n=6, 3/6, Wilson lower never reaches 0.50, McNemar exact p=0.25, arrival 0/week) and retired the seat (`NEGATIVE_EVIDENCE.md` R69). That is a result. His 2500 lines are not a counter-result.

**R69 vs his tree, claimed carefully:**

- R69 does **not** say Jev is useless in general (R69 NO-CLAIM).
- His tree does **not** say Jev is useful. It says the client is strict and usefulness is unproven.
- Therefore R69 is not overturned by line count.
- Public sentence that survives both trees: *skillranker's Jev tests certify the wire; they do not certify the judge. The only executed Jev-vs-baseline measurement we have is our R69 retirement.*

---

## What to adopt anyway (Rule 12, smallest honest form)

Not the seat. The **client discipline**:

1. Live tests `#[ignore]` + a meta-test that forced live without consent/key **cannot pass** (`jev_smoke.rs:129-196`).
2. Consent before key; never load `.env` for paid tests (`:84`).
3. Retry only `{429,500,502,503,504,529}`, four-attempt cap, `Retry-After` that must fit the deadline, loopback TLS fixture (`jev_retry.rs`).
4. Injected `JevTransport` for ranking tests (`p4_gate.rs:59-75`) so P4 cannot spend money and cannot pretend a mock is live.
5. Eval policy that **names** always-abstain / quill-only as required negative controls — we already did the measurement; keep the named controls.

A refusal to adopt those would need a cost, a defect class they would not catch, and a loss. None apply. They are cheaper than another Jev seat.

---

## Boundary

- Did not run `cargo test` in `skillranker/` (vendored; no mutation of the clone).
- Did not re-open R69. Retry condition unchanged: labelled semantic rows we did not author, arrival > 0/week, preregistered p̂ ≥ 0.60.
- Did not count `adapter_contract.rs` as Jev evidence.
- Numbers above are file:line at `abf909d`, not remembered.
