# The Oracle Program — proving 22 repos, one tick at a time

**Status:** plan, round 1 · **Owner:** conductor (pane 1) · **Created:** 2026-09-19

> Joshua: *"there is no way that we have a single oracle for all, right? How are we using typed
> rigor backed by asupersync for every one of these?"*

Correct, and the lack of per-repo oracles is why this lane has ruled 21 candidates and promoted
zero. This plan replaces ad-hoc scoring with a **typed oracle algebra**, assigns each repo a
**specific oracle shape with a docs-backed ground truth**, and decomposes the work into units small
enough that a cron tick finishes one — so work stops pausing between sessions.

---

## 1. Why this plan exists (the three observed failures)

Every rule below is a response to something measured in this repo, not a preference.

| Observed failure | Evidence | Rule it forces |
|---|---|---|
| One oracle reused across unlike repos | the compaction "novel token reappears" scorer was applied as if general | **§3 per-repo oracle assignment** |
| Oracles that cannot return YES | an omniscient `perfect` judge scored 27.2%/29.3% at 0% loss and still **failed** the bar | **§2 symmetric outcomes + feasibility arm** |
| Suites blind to judgment | random judge substitution left **254/305 (83%)** tests green; 1 test in 6 repos scores Jev against a label it did not supply | **§2 evidence classes; only class C rules** |
| Verdicts with no adoption path | every rung-4 row is a kill; 21 ruled / 0 promoted | **§5 adoption test is mandatory at rung 3** |
| Work pausing between sessions | units sized per-session, not per-tick | **§6 tick-sized units with resumable state** |

---

## 2. The oracle type algebra

### 2.1 Evidence classes (what a test is allowed to conclude)

Borrowed from `franken_ocr`'s L0–L5 parity ladder — a lower rung failing short-circuits every
higher claim.

| Class | Definition | May conclude |
|---|---|---|
| **A — MOCK-SCRIPTED** | test supplies the judge's answer *and* the expected outcome | plumbing works. **Nothing about judgment.** |
| **B — RECORDED/GOLDEN** | a committed real response replayed and pinned | decoder/wire stability. Not live judge drift. |
| **C — GROUND-TRUTH** | judge scored against a label it did not supply | **judgment quality.** Only class C may rule. |
| **D — OUTCOME** | the downstream task measurably succeeds or fails | **fitness for purpose.** The strongest class. |

A repo's verdict carries its highest achieved class. `CLEARED (class B)` is not `CLEARED (class C)`
and must never be written as if it were.

### 2.2 The seven oracle shapes (from the corpus, with citations)

Mined by pane 2 from the pinned mirror; see `upstream-repro/oracle-design-from-corpus-20260919.md`.

1. **Threshold promotion gate** — `franken_engine/.../promotion_gate_runner.rs:266-328`. Empty
   evidence fails; `delta == threshold` promotes. Use when a single scalar decides adoption.
2. **Monotone per-category ratchet** — `franken_ocr/docs/conformance/RATCHET.md:33-51`. No category
   may fall below its floor; aggregate improvement cannot hide a per-category regression.
3. **Applicability-authority ratchet** — `frankensearch/.../perf_ratchet.rs:732-740`. Missing
   applicability is **fatal, not a pass**. The candidate cannot choose its denominator after seeing
   results.
4. **Mixed positive/negative denominator** — `franken_engine/.../differential_oracle_perf.rs:85-118`.
   Case identity and bytes pinned before measuring, so fixtures cannot be swapped.
5. **Metamorphic + golden artifact** — `franken_tts/.../metamorphic_invariants.rs:315-505`. Missing
   fixtures **skip explicitly**; they never pass.
6. **Metamorphic invariants** (round-trip / invertibility) — `frankenlibc/.../memcpy_strict_conformance_test.rs:452-465`.
   Use where enumerating goldens is impractical.
7. **Adversarial survival gate** — known-bad scenarios must stay rejected while ordinary
   measurements pass. Negative controls are first-class denominator members.

### 2.3 Typed rigor borrowed from asupersync

`skill://asupersync-mega-skill` contributes four mechanisms, adopted verbatim in spirit:

- **Proof-lane manifest** (`artifacts/proof_lane_manifest_v1.json`) → our
  `docs/demos/ORACLE-MANIFEST.tsv`: every repo's oracle, class, and lane declared **before** any
  green claim. "Classify every proof through the manifest before making any green claim."
- **Refuse-to-decide as a first-class verdict** — a lane whose manifest requires remote proof may
  not be greened by a local fallback. Our equivalent: `REFUSE (applicability)` outranks a guess.
- **Live-doc refresh before any claim** — the SDK/API surface must be re-read at planning time, not
  recalled. Already paid for: `client.systemOne.evaluate` does not exist; the Python SDK is not on
  PyPI; `NoulAnswer` exposes `.noul` not `.probability`.
- **e-process for anytime-valid stopping** (`asupersync/src/lab/oracle/eprocess.rs:224-238`):
  `e_t = e_{t-1}·max(1e-15, 1+λ(x−p0))`, reject at `e ≥ 1/α`. Use wherever we sample sequentially,
  so stopping when the number looks good is not p-hacking.

### 2.4 The five mandatory properties (any oracle in this lane)

1. **Named consumer** — the ship/adoption decision it controls.
2. **Predeclared positive boundary** — `promote if ≥ X`, written in the file before running.
3. **Symmetric outcomes** — can return promote/adopt as well as reject/hold/refuse.
4. **Feasibility arm** — an arm that *ought* to pass (perfect judge, or known-good candidate). **If
   nothing can pass, the instrument is broken, not the candidate.** This is the rule that caught the
   rigged compaction bar in one run.
5. **Both controls** — a positive control proving the harness detects signal (ours scored AUC
   **0.941**) and a negative control proving it rejects noise (**0/200**).

Benefit is counted in the unit the product delivers — bytes, dollars, seconds — never in incidents.
A per-incident benefit and a per-byte cost cannot be summed; that incommensurability is exactly what
made keep-everything unbeatable.

---

## 3. Per-repo oracle assignment

**There is no single oracle.** Each repo gets a shape, a ground truth, and its own win condition.
Ground truth must be **docs-backed**: derived from the repo's own README/spec/benchmark definition,
read at assignment time, not inferred.

### 3.1 Products (decisions we might adopt)

| repo | decision it makes | oracle shape | ground truth source | target class |
|---|---|---|---|---|
| `devanshbatham/commit-miner` | is this diff a security fix / which CWE | 4 mixed pos/neg denominator | real commits from our history + benign controls | **C→D** |
| `thruwire/foreman` | is a worker stuck / off-track / done | 7 adversarial survival | constructed observations at *their* thresholds + trap pairs | **C** |
| `NiazMorshed2007/jev-review` | code quality 1–10 | 6 metamorphic (ordering invariant) | good/bad pairs; ordering is the invariant, absolute score is not | **C** |
| `Dicklesworthstone/skillranker` | which skill to load | 1 threshold gate | its own `synthetic_cases.v1.jsonl` + frozen 0/1/2 loss table | **C** |
| `AbdelStark/bicameral` | allow / confirm / block a tool call | 7 adversarial survival | injection & destructive-command corpus; benign reads as negatives | **C** |
| `browser-use/jev-ultrafast` | next browser action | 5 metamorphic + golden | its `verify(page)` end-state checker, rewired behind a fixture | **D** |
| `*/jev-router`, `jev-codex-router` | which model for this turn | 3 applicability ratchet | **completion**, not price: did the downgraded turn finish | **D** |
| `tamaratran/fast-jev-compaction` | what to delete from history | 2 per-category ratchet | substantive-reuse + byte ceiling (**RULED OUT**, ceiling ~27–29%) | **C ✓done** |

### 3.2 Benchmarks (evidence about Jev, not products)

`jev-sec-bench`, `jev-spam-eval`, `jev-rerank-bench`, `jev-phishing-bench`,
`jev-agent-failure-benchmark`, `typesafe-ai-benchmark`. All are **shape 4** (their committed
per-item data is the pinned denominator) and top out at **class C**. Rule: recompute from per-item
data with our own scorer; never quote a headline. This caught two flattering framings already.

### 3.3 Infrastructure

`typesafe-sdk-js`, `typesafe-sdk-python`, `jev-mcp`, `typesafe-ai/skills`,
`system-one-adapter-python`, `awesome-jev`. Shape 5 (golden/replay), class **B** — and **B is the
honest ceiling**; they carry no judgment. `system-one-adapter-python` is the exception and the
template: labeled probe + VCR cassette + `>0.9` assertion, class C in CI with no key.

---

## 4. The manifest (state of record, resumable)

`docs/demos/ORACLE-MANIFEST.tsv` — one row per repo, written **before** measurement:

```
repo  shape  ground_truth_source  win_condition  class_target  class_achieved  stage  receipt  digest
```

`stage` ∈ `UNASSIGNED → SPEC → BUILT → RUN → RULED`. A tick reads the manifest, picks the oldest
row not at `RULED`, advances it **one stage**, and writes it back. This is what makes the work
resumable: no session needs to remember anything.

Gate: a row may not reach `RUN` unless its `win_condition` is non-empty and its oracle file contains
a feasibility arm. Enforced by a new stage in `foundation/gates.sh` (creation-gate justification in
§7).

---

## 5. Phases

Phases are strictly ordered; each is a dependency edge in the bead graph.

- **P0 — Substrate.** Manifest schema + `oracle-kit` (shared scorer: AUC/Mann-Whitney, e-process,
  positive/negative control runners, feasibility-arm assertion). *Unblocks everything.*
- **P1 — Spec.** For each repo: read its docs, name the shape, source the ground truth, write the
  win condition into the manifest. **No code.** One repo per unit.
- **P2 — Build.** Implement that repo's oracle against `oracle-kit`, including both controls and the
  feasibility arm. One repo per unit.
- **P3 — Run.** Execute, record class achieved, emit receipt. One repo per unit.
- **P4 — Rule.** Non-author verdict: PROMOTE / HELD / RULED_OUT / REFUSE(applicability). A rung-3
  CLEARED row **must** get an adoption test dispatched.
- **P5 — Ratchet.** Promoted items get a floor in the manifest; regressions fail closed.

**Critical path:** P0 → (P1→P2→P3→P4 per repo, parallel across panes) → P5.

---

## 6. Tick-sized units (the cron rotation)

The unit of work is **one repo × one phase**, sized to finish inside a 20-minute tick. A tick:

1. `./scripts/lane-status.sh` (state) and read `ORACLE-MANIFEST.tsv`.
2. Pick the oldest row not at `RULED`; if a pane is idle, dispatch its next stage to a **non-author**.
3. Advance exactly one stage; commit manifest + receipt in the **same** commit.
4. Fire the callback with the next unit already named.

With 22 repos × 4 stages ≈ **88 units**, 3 panes, ~1 unit/pane/tick → roughly 30 ticks of runway.
Nothing pauses, because the next unit is always computable from the manifest without context.

---

## 7. SCOPE CUT — this plan failed its own process-porn worksheet

Filled `process-porn-worksheet.md` against this document before committing it. Part 1: running code
does not branch on the manifest, so it is **process**. Part 2 Q3 is real (21 ruled / 0 promoted;
three measured harness defects). But the worksheet's last red flag fired:

> *"This is your second-or-later process artifact this session while the capability count has not
> moved. That is the meta-trap; stop entirely."*

**That is an accurate description of me this session.** An 88-unit program with a manifest, a gate
stage and a shared kit is exactly the apparatus the skill warns is "infinitely extensible,
especially when the assignment is about process quality."

**Cuts, effective immediately:**

- **`oracle-kit` is deferred**, not built. Three repos get hand-rolled oracles first. If the same
  scorer is copied a third time, *then* extract it. Premature extraction is the ceremony.
- **The manifest gate stage is deferred.** The manifest starts as a plain TSV that a human reads.
  No new `foundation/gates.sh` stage until a row actually reaches `RUN` without a win condition —
  i.e. until the defect is observed here, not imagined.
- **No phase may run ahead of a shipped verdict.** P1 specs are capped at **3 repos** until at
  least one repo completes P4. A spec backlog is not progress.
- **Benchmarks (§3.2) are demoted out of the program.** They are evidence, not products; ruling
  them is the survey habit reasserting itself (open question 2, now answered NO).

Remaining scope: **8 product repos × 4 stages = 32 units**, not 88.

## 8. Creation gate for the one surviving instrument

Per lane doctrine, all four must be named or it does not get built.

**`ORACLE-MANIFEST.tsv`** (the only artifact built now).
- **Consumer:** the cron tick — it reads the oldest row not at `RULED` and dispatches that unit.
  Not "the record", not "future maintainers".
- **Gate:** a repo cannot be ruled without a row carrying a preregistered win condition.
- **Observed defect:** 21 rulings landed this session with **zero** preregistered thresholds, and
  one bar was later proven impossible — a perfect judge failed it.
- **Retirement:** delete when the 8 product repos are at `RULED` and P5's ratchet holds their
  floors. It is a work queue, not a permanent register.

`oracle-kit` and the gate stage are **parked** per §7; this section is deliberately one artifact
long.

---

## 8. Beads structure

Jeff-standard: every bead carries **WHAT / WHY / ACCEPTANCE**, and the graph is dependency-complete
before work starts.

```
jev-oracle-p0-kit          (no deps)
jev-oracle-p0-manifest     (no deps)
jev-oracle-p1-<repo>       blocked-by: p0-manifest
jev-oracle-p2-<repo>       blocked-by: p1-<repo>, p0-kit
jev-oracle-p3-<repo>       blocked-by: p2-<repo>
jev-oracle-p4-<repo>       blocked-by: p3-<repo>   [non-author only]
jev-oracle-p5-ratchet      blocked-by: all p4-*
```

Every bead's ACCEPTANCE names a positive observable, a planted negative, and a NO-CLAIM.
`REFUSE(applicability)` is an acceptable terminal outcome and must be listed as such, so a pane is
never forced to manufacture a verdict.

---

## 9. Binding rules (from `just-say-no-to-process-porn-and-ceremony`)

These bind every unit dispatched under this plan and must be pasted into each subagent packet:

- **Never dispatch "make the tests pass."** Acceptance = positive observable + planted negative +
  NO-CLAIM. A subagent told only to go green will weaken tests or special-case fixtures.
- **A pane's report is a claim, not evidence.** Re-execute cited commands; diff specifically for
  touched test/gate code, new fixtures standing in for live proof, and regenerated goldens.
- **No self-certification.** A P4 ruling is invalid from the pane that authored P2/P3. Non-author
  only — this is the clause whose absence produced 21–0.
- **A typed refusal beats a fabricated result.** `REFUSE(applicability)` is a terminal outcome, so
  no pane is ever forced to manufacture a verdict. But refusal-only work never closes a
  positive-capability item.
- **Benefit in the product's own unit** — bytes, dollars, seconds. Never incidents.
- **Every claimed metric predeclares its denominator and a countermetric.** Agreement between
  panes raises confidence, never authority class; same-origin evidence counts once.
- **Honesty pass every third tick**, reported in the tick line, not filed as an artifact.

## 10. Open questions for review round 2

1. Is class **D (outcome)** reachable for the routers without unaffordable live spend? The
   ablate-and-rerun experiment is named but uncosted.
2. Should benchmark repos (§3.2) be ruled at all, or only mined for evidence? They are not products;
   ruling them may be the survey habit reasserting itself.
3. Does `oracle-kit` belong in this repo or in `foundry/loop-kit` for reuse by other lanes?

## 11. NO-CLAIM

This is a plan, round 1 of the ≥4 the planning workflow requires. No repo has been assigned its
oracle yet beyond the eight sketched in §3.1; those assignments are hypotheses until each P1 unit
reads that repo's docs and confirms the ground truth exists. The 88-unit estimate assumes four
stages per repo with no rework and is therefore a floor, not a forecast.
