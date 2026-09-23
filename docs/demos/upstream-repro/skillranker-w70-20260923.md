# W7.2 skillranker (ROOT clone @a6f1ff0) — fresh run receipt

## T-row table

| id | verdict | one-line |
|---|---|---|
| T1 | PASS | a6f1ff0 2026-09-21, MIT+Rider, tracked-clean, contabo-1+3, jev-1.13.0 |
| T2 | FAIL (build-red, grounded) + PARTIAL-green | full suite exit 101 on 2/2 workers (missing synced fixtures); fixture-free 8 targets 78 pass/0 fail/4 ignored; plant NOT-RUN |
| T3 | PASS | 6 claims w/ file:line: 2 demonstrated, 4 partial |
| T4 | PASS (rate) + gate-FAIL | N=12, prev 83.3%, top-1 0.800, mean loss 0.167; beats both floors; 0.800 < 0.90 gate |
| T5 | PASS | always-abstain 0.833/0.000 + lexical 0.583/0.600 on same rows; Jev beats both |
| T6 | PASS per brief (BM25 arm) | lexical arm doubles as incumbent per brief; LLM-adapter arm NOT-RUN (brief) |
| T7 | PASS | 5 bins WITH counts + unasked row; N=11 caution |
| T8 | PASS | repeat 0/10, reword 0/10 flips |
| T9 | PASS | codec 15/15+8/8; key-absent/malformed/timeout all refuse, host survives |
| T10 | SELF, gate-FAIL, NO-CLAIM | bar rate-PASS, promotion FAIL; tiers unassigned (no rubric in lane) |

## T1 pin/env
- Clone: /Users/josh/Developer/jev/skillranker @ a6f1ff02cab274df287098cf205247cc67d7d1ef (2026-09-21, `fix(privacy): redact tool labels before context windowing`). Upstream copy pinned 3fe85c4 (upstream/MANIFEST.tsv:22). Neither touched: no commits, no pushes; final `git status --porcelain` shows ONLY pre-existing untracked scratch-ho/ + sr-linux-amd64 (both pre-date this run per skillranker-origin-main-20260919.md); `git diff --stat` empty; HEAD still a6f1ff0.
- License: MIT + OpenAI/Anthropic Rider (LICENSE:1; rider names OpenAI/Anthropic + affiliates, voids grants to Restricted Parties).
- Model jev-1.13.0 pinned. Bar commit 070efe6 (2026-09-22 21:38:26 -0600) predates first W7.2 live call (2026-09-22 21:42:52 -0600). Key only via infisical run (never printed).
- Workers used: contabo-1, contabo-3 (Selected-worker lines in T2).

## T2 own suite (RCH only, never local cargo, never --target)
- Full: `RCH_VISIBILITY=verbose rch exec -- cargo test -j 2` → exit 101 on contabo-1 AND identically on contabo-3. Same 5 errors: tests/transport_failures.rs:84,163,167,209,213 `couldn't read tests/fixtures/jev-tls/{ca.pem,server.pem,server.key}`. Counts: 0 pass / 0 fail / 0 skip — no test executed. Verdict FAIL (build-red). DEVIATION: ran without `--locked` (AGENTS.md:558 prescribes `--locked`); Cargo.toml pins are mostly exact (`=`), drift surface small, disclosed.
- Cause grounded (not a code defect): files are tracked at HEAD (`git ls-files` lists all 6; `git cat-file -e HEAD:.../ca.pem` OK) and present locally, but absent in the RCH-synced remote tree on 2/2 workers → RCH sync/transfer gap for *.pem/*.key (consistent with .rchignore header `Remote compilation needs source, never local credentials`). No trybuild/should_panic surface in repo (`grep -rln` empty) → no such negative verdicts exist; the build-failure verdict itself IS second-worker-confirmed.
- Fixture-free subset on contabo-3, exit 0: eligibility 11, endpoint 11, jev_admission 6, jev_codec 15, jev_contract 8, jev_rerank 7, jev_smoke 9, jev_wide 11 = **78 pass / 0 fail / 4 ignored**. Ignored with reasons (jev_smoke.rs:240,620,629,849): 4 live-paid consent-gated probes. jev_retry + jev_transport fixture-blocked too — same cause, not separate defects.
- T2 plant NOT-RUN. (1) `mkdir -p /tmp/w70plant/...` + RCH exec with cwd /tmp/w70plant → `Working directory does not exist: /tmp/w70plant`. (2) verbatim as shown. (3) cause: no-touch constraint + RCH executes in synced project trees only. (4) routes: human-approved temporary in-clone plant + revert; or lane-approved RCH scratch path; or upstream vendoring fixtures so the suite compiles remotely.

## T3 claim inventory (≥5, with file:line)
1. Wide Choice + typed `__none__` sentinel; winning sentinel never ends the pass (src/jev/wide.rs:1-6, :35 NONE_OPTION, :222 criteria push; README.md:91) — DEMONSTRATED: live 2/2 no-match abstentions (topP 1.00/0.99), 8/10 positives picked, 0 wrong picks.
2. Gate mean 0.30 decides rerank (src/jev/wide.rs:26 DEFAULT_GATE; src/config.rs:880-881 gate/fits 0.30; src/eligibility.rs:19) — PARTIAL: constants present; harness asks one Choice with no second gate; rerank never executed live.
3. Quill BM25 prefilter ONLY if >254 candidates (src/pipeline.rs:1714-1717; src/jev/wide.rs:31 MAX_REAL_OPTIONS; src/roster/retrieval.rs; README.md:91) — PARTIAL: code present; N=12 never triggers it; now measured vs lexical floor in T5/T6.
4. 96 KiB serialized cap + fixed trim order, sentinel+candidates never dropped (src/jev/wide.rs:8-12; src/jev/codec.rs:13 MAX_REQUEST_BYTES; src/limits.rs:334-335) — PARTIAL: constants + passing trim unit tests (jev_wide 11/11); no live over-budget request observed.
5. Budget 2 logical / 4 HTTP attempts, single admission seam (src/jev/admission.rs:5-8; src/limits.rs:15-16) — PARTIAL: constants + jev_admission 6/6; live spent 1 call/case, budget never pressured.
6. Hand-rolled wire codec, no TypeSafe SDK (src/jev/codec.rs:1-3; Cargo.toml has NO typesafe dep; src/jev/endpoint.rs:26,29) — DEMONSTRATED: jev_codec 15/15 + jev_contract 8/8 pass; T9 refuses behave as documented.

## T4 live (per prereg bar)
- Corpus: skillranker/tests/eval/synthetic_cases.v1.jsonl, N=12 existing labelled cases (DISCLOSED diagnostic_synthetic; tests/eval/README.md: `not benchmark results`). Used as-shipped, no authoring.
- Arms on same rows: Jev wide-Choice top-1 via work/skillranker-eval judgeSkillPick + askJevChoice (one Choice + `__none__`, no second gate) | always-abstain floor | lexical BM25-approximation floor (exact token overlap, no stemming, zero-overlap→abstain, tie→first; Quill itself never triggers at N=12 — disclosed).
- Jev: positives 10/12, prevalence 83.3%; top-1 8/10 = 0.800; mean loss 0.167 (total 2); abstains 4 (2 correct + 2 false); wrong picks 0. Both errors are cheap false abstentions, never wrong picks.
- Spend: 39 Jev calls vs cap 40. Latency p50 212ms / p95 366ms (38 measurement calls). Token/$ unreported by harness — calls are the cost metric. No key or customer data printed.
- Router-hook bar: vs always-abstain Δacc +0.800 / Δloss −0.666; vs lexical Δacc +0.200 / Δloss −0.416 → beats BOTH floors beyond thresholds → rate-PASS. Promotion gate: 0.800 < 0.90 → FAIL (0.90 gate sourced: lane receipts skillranker-corpus-measured-20260919.md:10,26 — prior lane bar applied unchanged; NOT in the W7 prereg, which governs rate only).

## T5 floors (same 12 rows)
- always-abstain (offline, deterministic): mean 0.833, top-1 0.000, abstains 12, holes 1.
- lexical (exact-overlap rule): mean 0.583, top-1 6/10 = 0.600. Reference: coin-flip exact E[loss] 1.035.
- A floor tying Jev would refuse the seat — neither ties: Jev clears both by ≥0.10 acc and ≥0.05 loss.

## T6 incumbent
- Per brief, T6 is satisfied by the BM25 arm: the §T5 lexical arm (BM25-approximation: token-overlap ranker, 0.583/0.600) IS the T6 incumbent arm; no separate LLM arm. Paired gap on same rows: Jev − lexical = −0.416 mean loss, +0.200 top-1 (n=12, descriptive only, no significance claimed).
- system-one-adapter-python LLM arm NOT-RUN per brief, with the four fields stated in the agent report (brief-directed skip; future route named).

## T7 calibration (bins WITH counts; asked n=11)
- topP [0.00,0.50): n=1, correct 1. [0.50,0.70): n=0. [0.70,0.85): n=3, correct 2. [0.85,0.95): n=1, correct 1. [0.95,1.01]: n=6, correct 6. Unasked (local abstain, no call): overflow loss 1. Not single-bin, but N=11 asked — no calibration claim made beyond the counts.

## T8 stability (10-subset = first 10 case_ids; reword `Restated with identical meaning: ` prefix, roster/constraints/Y identical)
- 3× same-state: round2 and round3 picks identical to round1 on all 10 → repeat flips 0/10. Reword: picks identical on all 10 → framing flips 0/10. No seat-flagged rows (>20% flip): none.

## T9 fault behaviour (codec path src/jev/codec.rs + client)
- Rust: jev_codec 15/15 + jev_contract 8/8 + jev_smoke consent tests — contabo-3, exit 0.
- Live-client refuses, host survives: key-absent → unconfigured (0 calls); malformed classes-list + single-label → no-answers (0 calls); timeoutMs=1 → transport refuse, host survives (1 call, counted in spend).
- Codec errors carry no input/keys/bodies by construction (src/jev/codec.rs:22-23, :40-65).

## T10 verdict + Boundary + spend
- Class: SELF (clone-authored disclosed synthetic corpus; split forbids promotion; measures Jev-via-harness, NOT the sr product — no sr binary invoked). Floors: FLOOR-beating (both). Incumbent: BM25-approximation-beating (descriptive). Tiers: unassigned — no RULEBOOK tier rubric in this lane; recorded as unassigned rather than invented.
- Router-hook application: BAR rate-PASS numerically, promotion FAIL (0.800<0.90 sourced gate; synthetic split; n=10 positives). NO-CLAIM: n=12 diagnostic_synthetic; second run reproducing the 2026-09-19 0.167/0.800 shape (lead confirmed as lead); not a SkillRanker product measurement; not a promotion; full-suite RCH RED is a sync gap, not a code verdict.
- Boundary: measured = Jev Choice-via-harness on clone corpus + fixture-free Rust targets via RCH. Not measured = sr binary rank quality, rerank stage, Quill>254 path, over-budget trim, LLM incumbent, full-suite green. Clones untouched (root HEAD a6f1ff0, tracked-clean; upstream 3fe85c4 untouched). Spend: 39/40 Jev calls, model jev-1.13.0, p50/p95 212/366ms; RCH contabo-1 (exit 101) + contabo-3 (exit 101 confirm, exit 0 subset).

## Pane-6 verification (2026-09-23, before landing)

- `git -C skillranker status --porcelain` → only pre-existing untracked scratch-ho/ + sr-linux-amd64 (both pre-date this run); `git diff --stat` empty; HEAD `a6f1ff02cab274df287098cf205247cc67d7d1ef`.
- `git -C skillranker ls-files tests/fixtures/jev-tls/` lists all 6 incl. pem/key → tracked at HEAD, consistent with the transfer-gap cause (present locally, absent on workers).
- 0.90 promotion gate sourced in-lane (skillranker-corpus-measured-20260919.md:10,26 — prior bar, applied unchanged); it is NOT in the W7 prereg, which governs rate only. Both verdicts stand without contradiction: rate-PASS (prereg) + promotion FAIL (standing gate).
- Worker RCH lines quoted verbatim with IPs/exits; full-suite rerun not repeated (two-worker identical exit-101 with identical missing-file errors is the confirmation the skill requires).
