# Jev product plan: from research lane to product loop

- **Status:** DRAFT round 0, written by pane 1 (AmberWillow, Claude), 2026-09-25.
- **Review:** 4+ rounds by other models before beads conversion (planning-workflow skill).
- **Inputs:**
  - `notes/deep/next-gen/NEXT-STAGE-PLAN.md` (the proposal);
  - `notes/deep/duel-20260925/DUELING_WIZARDS_REPORT.md` (the 3-model duel that ranked it);
  - four research reports summarized in §1.
- **Directive, Joshua 2026-09-25, verbatim:** *"lets move this out of repeated testing over and
  over to actually turning this into something relvant and usable"*. Also, after the duel: *"lets
  turn these ideas into a proper plan"*.

This document is self-contained. A fresh agent should be able to pick up any work package (WP)
below, read only its section plus §2–§4, and start.

---

## 1. Why this plan exists (measured facts, 2026-09-25)

Every claim here was measured today; the sources are in parentheses.

### 1.1 Jev is good at a narrow set of decision shapes

Across 245 live measurements with a verdict (`local://wins-by-surface.md`, copied into §A1 when
this plan is committed):

| comparator | rows | win | tie | loss |
|---|---:|---:|---:|---:|
| cheap floor | 90 | 40 | 11 | 20 |
| LLM on the same items | 68 | 35 | 11 | 6 |
| absolute bar (ours or published) | 87 | 23 | 7 | 49 |

- **Wins over an LLM** fall in four decision shapes:
  - classification: Banking77, CLINC150;
  - scoring: SST-5, STS-B, Yelp;
  - true/false verification: prompt injection, SciFact, FEVER, command-gate false alarms;
  - reranking: BEIR SciFact.
- **No win over an LLM** in routing, extraction, game-agent policy, computer-use/web-agent
  policy, or compaction.
- **Why it matters.** Jev costs $0.042 per million input tokens (output free,
  `docs-mirror/typesafe/models.md`). Its p50 latency is roughly 130–500 ms on short states.
  Where it ties or beats an LLM, it does so at a small fraction of the cost.

### 1.2 None of the wins reaches a user

- **The four tools have no organic traffic.** The four omp tools (`jev_rerank`,
  `jev_claim_check`, `jev_flag`, `jev_screen`) have zero organic calls; every recorded call was
  a test (`jev-ja32`, `EVAL.md:2278`).
- **The gate hook is watched by nobody.** `.omp/hooks/post/jev-gate-observe.ts` scores real
  bash traffic (710 of 2,501 commands scored). It is observe-only and nothing consumes it. Live
  held-out recall is 22/33.
- **The best wins have no surface.** The Banking77, CLINC150, SST-5 and STS-B wins are not wired
  into anything.

### 1.3 The lane loses days to its own plumbing

- **The ledger is mostly our own failures.** NEGATIVE_EVIDENCE has 120 rows
  (`local://failure-taxonomy.md`):
  - 25 are our harness bugs;
  - 12 are inputs that could never succeed;
  - 15 are underpowered;
  - 15 are process failures;
  - only 4 are clean losses by a live Jev arm.
- **Prose rules did not stop recurrence.** Four failure classes recurred after a written rule
  targeted them. The only thing that stopped a class was a check that runs before spend (R114).
- **No harness shares the safety checks.** 121 live-calling harness scripts exist
  (`local://modules-harnesses.md`). None checks input size. None checks bar reachability. None
  launches detached. None uses the e-process. The repo holds 19 Wilson and 20 McNemar copies.
- **Today alone, three defects cost a run or a result:**
  - scroll-text coverage was 18/20 where our copy of MiniWoB's scorer said 20/20;
  - the `jev-jjwt` bar was unreachable (max 2 discordant pairs);
  - the MiniWoB held-out run halted on a Choice with one option. It stopped at 255/625.

### 1.4 Nothing is packaged for anyone else

- **The client is unpackaged.** `work/jev-client` uses the official `@typesafe-ai/sdk` 0.6.0 and
  has 102 non-test importers. It has no `package.json` and its README has no code.
- **No Python client.** There is no first-party Python client; every Python harness builds its
  own.
- **The README is a ledger.** It is 54,824 bytes and has no copy-paste path to a first Jev call.
  The nightly stranger run never calls Jev.
- **The agent-facing surface is absent.** The mentor doctrine audit found no `doctor`, no robot
  JSON contract and no one-line installer (`local://doctrine-adoption.md`).
- **Commits are mostly prose.** 59% of 2,823 commits touch no code or data.

### 1.5 What the duel decided

Three models (Claude, GPT-5.6-Luna, Gemini 3.8 Flash) proposed and cross-scored ideas.

- **Consensus, every other model scored it ≥ 700:**
  - `jev-kit` (810–940);
  - an agent-first `doctor` / CLI (820–860);
  - the shadow gate with an outcome join (740–930).
- **Contested:**
  - the experiment kernel (510–790);
  - the native omp `judge()` bridge (640→780 / 885).
- **Killed:**
  - games as a research lane;
  - live compaction;
  - blocking the gate on day one;
  - a new Best-of-N benchmark;
  - a CI PR gate.

---

## 2. Goals, non-goals, success signals

### 2.1 Goals

- **G1. One Jev decision in the fleet's daily path.** It runs on real traffic, logs outcomes,
  and publishes a daily report. It never blocks until it earns that on live labels.
- **G2. A package a stranger can use in five minutes.** A fresh clone reaches `doctor`, then an
  offline decision with the fake asker, then a live decision if a key is present.
- **G3. Preflights at the call site.** The request path refuses every known "cannot succeed"
  input for every caller: oversize, fewer than 2 options, answer not offered, malformed answer.
- **G4. An agent-first tool contract** (Jeffrey's standard): `doctor`, `--robot` JSON, and a
  one-line install for everything we ship.
- **G5. Measurement serves shipping.** A new live experiment is allowed only when a shipped seat
  needs a number. It then runs through the shared experiment path (WP-E), never a new harness.

### 2.2 Non-goals, frozen until G1–G3 land

- **No new benchmark surfaces.** That excludes new games, new computer-use suites and new
  Best-of-N universes.
- **No blocking gate** until the promotion prereg passes (WP-G3).
- **No new omp Jev tools.** The existing four stay; new ones wait until one has a consumer.
- **No Python package parity.** Python gets a package only when a named Python consumer exists.
- **No framework.** `jev-kit` stays small, and the budget is enforced in WP-K acceptance.

### 2.3 Success signals

Checked weekly by pane 1 with a committed receipt.

| signal | now | target | how measured |
|---|---|---|---|
| organic Jev decisions per day in the fleet | 0 consumed | ≥ 1 seat, every day | shadow report row count by date |
| outcome-joined decisions | 0 | ≥ 200 in week 1 | report |
| stranger clone → offline decision | not possible | < 5 min | `stranger-run.yml` timing |
| harnesses without size preflight | 121 / 121 | 0 for any harness run after WP-K | grep of callers of the kit preflight vs raw client |
| code share of commits | 28% | ≥ 50% | `git log` classifier (§A3) |
| defects caught before spend vs after | 1 / 3 today | next defect refused by preflight | NEGATIVE_EVIDENCE class of next harness row |

---

## 3. Architecture

```mermaid
flowchart LR
  subgraph kit["jev-kit (WP-K)"]
    P[preflight: size, options, offered, key] --> C[client on @typesafe-ai/sdk]
    C --> V[validator: schema, probabilities, choice ∈ ids]
    V --> R[receipt row]
    F[fake asker] -.-> C
    D[doctor / --robot]
  end
  subgraph omp["omp surfaces"]
    H[shadow gate hook (WP-G)] --> kit
    T[existing 4 tools] --> kit
    J[native judge role (WP-J spike)]
  end
  subgraph exp["experiments (WP-E, only when a seat needs a number)"]
    E[prereg + reachability + resume + scorer + e-process] --> kit
  end
  R --> Rep[daily report / README results (WP-R)]
```

**Design decisions and why:**

- **Preflights live in the client, not in an experiment runner.** Every caller needs them: the
  shadow hook, the tools, and strangers. Gemini's duel critique was right, and Claude conceded.
  This also retires the "121 harnesses re-implement it" problem for any caller that migrates.
- **TypeScript first.** `work/jev-client` is TS, uses the official SDK, and has 102 importers.
  The omp surfaces are TS. Python waits for a named consumer: no speculative parity.
- **The official SDK owns the wire (RULE 14).** `jev-kit` adds policy and packaging and never
  re-implements HTTP. The one hand-rolled caller (`.omp/hooks/pre/jev-compact.ts` via
  `fast-jev-compaction`) is migrated or left untouched as a vendored path, and never copied.
- **Shadow before block.** A block requires live labels. Replay figures (78/100 at 1/300) come
  from a sample. Live held-out recall is 22/33. Blocking on replay evidence would be a policy
  guess.
- **The experiment path is thin and on demand.** It exists to protect spend, not as a product.
  It is built only when WP-G3's promotion measurement needs it.
- **Receipts are the single source of numbers.** The README results section and the daily report
  are generated from receipt rows, never typed. This addresses the README-as-ledger and
  document-pumping failures.

---

## 4. Conventions every WP follows

These are from AGENTS.md; they are repeated here so each WP is self-contained.

- **Commits and shared files:**
  - `main` only;
  - stage explicit paths and commit with `git commit --only`;
  - the subject names its verification level (`[test]`, `[mutation]`, `[live]`, ...);
  - never amend;
  - reserve shared files (`TESTS.md`, `EVAL.md`, `NEGATIVE_EVIDENCE.md`, `.beads/`) only for
    the seconds of an edit.
- **Tests:**
  - every new test file gets a `TESTS.md` row with a one-line `Run:` command;
  - stage 70 fails CI otherwise.
- **Test design:**
  - fixtures are captured from real observations or rows (RULE 15), never typed;
  - tests assert effects, not inputs;
  - each test gets one planted defect that must turn it red.
- **Key handling:**
  - the key never enters the tree, a log or a message;
  - live calls use `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --`;
  - run `scripts/key-status.py` first.
- **Close protocol:** a WP closes only after a non-author check (tests in a clean clone, a
  planted defect goes red, headline numbers recounted). The close reason names commits.
- **Model:** always pin `jev-1.13.0`.

---

## 5. Work packages

Each WP lists: WHAT, WHY, depends on, unblocks, tasks, acceptance, and risks.

### WP-K — `jev-kit` v0 (bead `jev-h94q`, P1)

**WHAT.** A TypeScript package, extracted from `work/jev-client`. It lives at `kit/` (new
top-level directory, allowlisted in `.gitignore`) and contains:

- `src/client.ts`: the current `askJev` / `askJevChoice` / `askJevScore` / `askJevBundle`,
  unchanged in behaviour, moved.
- `src/preflight.ts`: pure functions that refuse before the wire.
  - `sizePreflight(state, questions)` estimates tokens with the band derived from 325 billed
    calls (`scripts/jev-state-size.py` logic, ported). It returns `FITS | NEAR | OVER` and
    refuses `OVER`. It refuses `NEAR` unless the caller passes `allowNear: true`.
  - `optionsPreflight(question)` refuses any Choice with fewer than 2 options. It would have
    prevented today's MiniWoB 400.
  - `offeredPreflight(question, expectedId?)` is an optional check for callers that know the
    solving option. It is used by experiments only.
- `src/validate.ts`: answer validation for every primitive, including `askJevBundle` (currently
  unvalidated at `work/jev-client/src/index.ts:627-637`). The rules:
  - `choice ∈ ids`;
  - probabilities finite in `[0,1]`;
  - `|Σp − 1| < 0.02`;
  - `p[choice] ≥ max(p) − 1e-6`;
  - Noul value in `[0,1]`.
- `src/fake.ts`: a fake asker with deterministic answers, recorded from real rows (RULE 15), for
  offline tests and the quickstart.
- `src/receipt.ts`: one receipt row type:
  `{ts, model, question_hash, state_hash, usage, latency_ms, outcome, policy}`. It never stores
  raw state.
- `bin/jev`: a CLI.
  - `jev doctor [--robot]` reports:
    - key source (never the key);
    - SDK version;
    - pinned model;
    - input limit;
    - hook discovery for `.omp/hooks`;
    - billing-hold state.

    It exits 0 when ready, 2 NOT_RUN (no key), 1 broken.
  - `jev ask choice|score|noul --state FILE --question FILE [--robot] [--fake]` makes one
    decision and prints a receipt.
- `package.json` with `name: jev-kit`, `bin`, `type: module`, `private: false`. The only
  dependency is the pinned `@typesafe-ai/sdk`. It is installable with
  `npm i github:JYeswak/jev_playground#path:kit` or similar. The exact form must be verified at
  implementation time (§4 grounding).

**WHY.**
- All three duel models proposed it independently.
- It turns proven client code into something a stranger and our own hooks can import.
- Moving preflights into the request path is the only fix that reaches every caller (§1.3).

**Depends on:** nothing. **Unblocks:** WP-G, WP-S, WP-E, WP-T.

**Tasks (each a bead):**
1. **K1:** move the client code into `kit/src/client.ts` and re-export from `work/jev-client`
   for one release. The re-export is deleted in K7; no permanent shim (AGENTS.md backwards
   compatibility).
2. **K2:** `preflight.ts`, with tests from captured rows:
   - a real OSWorld over-limit state from R112 rows;
   - the MiniWoB `drag-items-grid` one-option observation;
   - a real FITS state.
3. **K3:** `validate.ts`, extended to `askJevBundle`. Hostile-answer tests with plants.
4. **K4:** `fake.ts` from recorded answer rows. Each test uses it offline.
5. **K5:** `bin/jev doctor` and `jev ask`, with `--robot` JSON. Schema in `kit/ROBOT.md`.
6. **K6:** `package.json`, the install line, and a verified `npm pack` → install in a temp dir →
   `jev doctor` exits 2 without a key.
7. **K7:** migrate the four omp tools and the gate hook to import `kit/`, then delete the
   `work/jev-client` re-export. Grep proves zero importers remain.

**Acceptance.**
- **Offline:** `npm test` in `kit/` passes offline with no key.
- **Planted defects:** each of these makes a named test fail:
  - an over-limit state;
  - a one-option Choice;
  - a malformed answer;
  - an unvalidated bundle.
- **Fresh install:** `npm pack` → install in `/tmp` → `jev doctor --robot` prints
  `{"status":"NOT_RUN","reason":"no key",...}` and exits 2.
- **Live smoke:** with a key, one live `jev ask` records the model id `jev-1.13.0`, latency and
  spend.
- **Size budget:** `kit/src` is ≤ 900 lines, enforced by a test (the no-framework budget).

**Risks.**
- **Package scope creep.** The budget test and "no new verbs without a consumer" control it.
- **Moving code breaks 102 importers.** K1 re-exports; K7 migrates and deletes.
- **Install-from-GitHub form unverified.** Verify before writing the README line.

### WP-S — stranger path and generated README results (P1, part of `jev-h94q`)

**WHAT.**
- **A short quickstart.** A README section of at most 40 lines at the top:
  1. clone;
  2. `cd kit && npm ci`;
  3. `npx jev doctor`;
  4. `npx jev ask choice --fake --state examples/state.json --question examples/q.json`;
  5. how to get a TypeSafe key (link to `docs-mirror/typesafe/introduction/quickstart.md`'s
     source URL);
  6. the same command without `--fake`.
- **Generated results.** A results table generated from receipts by `scripts/render-results.py`
  between markers. CI fails if the rendered section differs from the committed one.

**WHY.**
- The README is 55 KB with no path to a first call.
- Numbers typed by hand drift, and the README has been edited in 198 commits.

**Depends on:** WP-K (K5, K6). **Unblocks:** mission stage 5 (share publicly).

**Tasks:**
1. **S1:** examples from a real captured state (RULE 15).
2. **S2:** `stranger-run.yml` gains setup-node and the kit steps, and times clone → offline
   decision.
3. **S3:** `render-results.py` plus a CI check.
4. **S4:** move the ledger prose out of the README into `docs/LEDGER.md`, so the README is a
   product page.

**Acceptance.**
- The stranger run is green, with the offline decision under 5 minutes wall time (recorded).
- The README is under 15 KB.
- A planted edit to a generated number fails CI.

**Risks.** Moving ledger prose could break claim coverage (stage 95/97, claim-coverage floor
114/115). Move the claims to `docs/LEDGER.md` and point the coverage gate there in the same
commit.

### WP-G — shadow gate v1 with outcome join (bead `jev-ugtj`, P1)

**WHAT.** Extend `.omp/hooks/post/jev-gate-observe.ts` (382 lines; observe-only; has secret
filters, a verbatim sidecar at `~/.local/state/jev/gate-observe-full.jsonl` mode 600, and a
NOT_RUN row without a key).

- **G1 outcome join.** A collector, `scripts/gate-outcomes.py`, joins each scored command
  (`cmdSha`, session, ts) to observable outcomes in the same session within N subsequent tool
  calls:
  - a dcg deny;
  - a `git revert` / `git checkout -- <path>` / `git restore` touching the same paths;
  - a user message containing an undo phrase;
  - a failed follow-up of the same command.

  Outcome labels: `harm-evidence | no-evidence | unknown`. Sources are session JSONL under
  `~/.omp/profiles/*/agent/sessions/`. They are read locally and never committed.
- **G2 daily report.** `jev gate report [--robot]` (a kit CLI subcommand) prints:
  - calls, spend and p50/p95 latency;
  - flag rate at the current threshold;
  - joined outcomes and a confusion table vs `harm-evidence`;
  - the top flagged commands (redacted).
- **G3 promotion prereg.** A committed prereg that defines:
  - the held-out window;
  - the labels (blind human or two blind labellers on the flagged plus a random sample, as in
    `jev-yru2`);
  - the bar: catch rate at a fixed false-alarm ceiling vs the deterministic baseline (dcg rules
    alone). The source is INCUMBENT per RULE 15.

  `scripts/bar-reachable.py` must say REACHABLE before any labelling spend.
- **G4 cost guard.** It scores bash calls only. The hook stays asynchronous and never on the
  tool path. The report shows spend per session, and a daily cap in config pauses scoring
  (logged) if exceeded.

**WHY.**
- It is the only duel idea with a consumer today.
- Fleet traffic becomes a non-authored, continuously growing labelled set: the external oracle
  of Rule 13, in live form.

**Depends on:**
- WP-K (K7 migrates the hook to the kit);
- `jev-1ww3` (bar-reachable, finish its missing test first).

**Unblocks:** a blocking policy (a separate future decision) and the WP-E first consumer.

**Acceptance.**
- **Outcome rows accumulate:** ≥ 200 joined decisions from real sessions within 7 days.
- **Report on demand:** the report runs in one command.
- **Prereg:** the prereg is committed with a sourced bar and REACHABLE.
- **Planted defects** turn a test red:
  - the join misattributes a revert to a different path;
  - the secret filter bypassed.
- **Healthy path silent:** no output on the tool path (L4 of the validation ladder).

**Risks.**
- **Weak or delayed outcome labels.** Report `unknown` honestly and never impute.
- **Blind spots.** Eval-prelude `browser.*` / `computer.*` calls are invisible to hooks. State
  this in the report header.
- **Privacy.** Session text stays local; only hashes and redacted prefixes enter reports.

### WP-J — native omp judge-role spike (bead `jev-xy67`, P2, keyless)

**WHAT.** omp documents a `judge` model role used by `judge()` and internal classifiers. Its
built-in chain starts with `typesafe/jev-latest` and the catalog is discovered from
`GET /v1/models` (`omp://environment-variables.md:401`). The spike answers four questions:
1. Can a project profile pin the judge role to `jev-1.13.0` instead of `jev-latest`?
2. Where does omp read the TypeSafe credential, and can it come from Infisical without a shell
   env var?
3. Does `judge_batch()` exist in this omp version, and what is its contract?
4. Can `jev doctor` detect and report the role's resolved model?

**WHY.**
- If yes, every omp agent gets calibrated typed judgments through a native primitive, and our
  tools need no separate consumer.
- The duel contested it (885 vs 640→780), so it should be decided by evidence, not argument.

**Depends on:** nothing, keyless. **Unblocks:** a possible WP-G variant using native `judge()`.

**Acceptance.** A written yes/no per question with omp doc citations and config lines. If yes, a
keyless test proving the resolved model id. No live call.

### WP-E — thin experiment path, only when needed (P2, no bead until triggered)

**WHAT.** `kit/experiment/` (≤ 400 lines) provides:
- a prereg-committed check;
- `bar-reachable` (from `jev-1ww3`);
- per-episode resume;
- a detached launch through a single `scripts/live-run` wrapper that daemonizes, writes a pid
  and heartbeat, and refuses to start as a child of an omp pane;
- scoring with the benchmark's own scorer via a hook;
- an e-process monitor (`work/oracle-kit` `eProcess`, 0 callers today);
- one receipt format.

**Trigger.** It is built when WP-G3's promotion measurement needs it, or when an existing live
bead must resume. The first of those is MiniWoB `jev-9gtw.4` at 255/625, which needs its
one-option fix preregistered first.

**WHY.**
- Every protection here was missing in 121 harnesses.
- Today three defects reached a run.
- The duel scored it 510–790: needed, but behind the product.

**Acceptance.**
- **Replay of three defects.** Today's three defects replay as refusals before spend:
  - the scroll-text scorer copy (a scorer hook that is not the benchmark's own is refused);
  - an unreachable bar;
  - a one-option Choice.
- **Pane restart.** A pane restart does not kill a launched run (test: launch, kill parent pane
  process, heartbeat continues).

### WP-T — agent-first contract for everything we ship (P2)

**WHAT.**
- Every shipped CLI (`jev`, `scripts/*.py` that others run) gets `doctor`-style readiness, a
  `--robot` JSON with a documented schema, and exit codes: 0 ok, 1 fail, 2 NOT_RUN, 8 SKIP.
- `kit/` gets a one-line installer script that verifies checksums, per Jeffrey's
  `installer-workmanship` pattern.

**WHY.** The mentor audit found all three ABSENT. Other agents are our first users.

**Depends on:** WP-K. **Acceptance:** `jev doctor --robot` validates against its schema in CI;
the installer runs in the stranger workflow.

### WP-X — close out in-flight research (P2)

These close the research lane instead of leaving it open.

| bead | step to close it |
|---|---|
| `jev-1ww3` | add the missing flip test (headroom < misses → UNREACHABLE), then close |
| `jev-9gtw.4` | preregister the one-option fix (single option → no call, counted as `none`), resume from 255/625 through WP-E, and score against the prereg |
| `jev-yru2` | the gate-question retest; fold into WP-G3's labelling protocol when possible, otherwise run it as preregistered |
| `jev-3e2i`, `jev-jy7t.1.4` | close as not planned under the freeze, or finish if one step remains |

---

## 6. Dependency graph

```mermaid
flowchart TD
  K1-->K2-->K3-->K4-->K5-->K6-->K7
  K5-->S1-->S2
  K6-->S2
  S2-->S3-->S4
  K7-->G1-->G2
  X1[jev-1ww3 flip test]-->G3
  G2-->G3
  G3-->E[WP-E if needed]
  X2[jev-9gtw.4 prereg fix]-->E
  K5-->T1[WP-T contract]
  J[WP-J spike, independent]
```

- **No cycles.**
- **No orphans:**
  - every WP feeds G1 (daily seat), G2 (stranger), G3 (preflights) or G4 (contract);
  - WP-J feeds an optional WP-G variant.

---

## 7. Staffing (as of 2026-09-25)

| pane | agent | first assignment |
|---|---|---|
| 2 | CopperHeron | WP-K (K1–K4) |
| 3 | IvoryCreek | WP-G (G1, G2), then G3 |
| 4 | OrangeFrog | `jev-1ww3` flip test, then WP-J spike |
| 5 | WindyLantern | WP-X `jev-9gtw.4` prereg fix, then WP-S |
| 1 | AmberWillow | non-author checks, beads, weekly success-signal receipt |
| 0 | Gemini (agy) | out of tokens; plan reviewer when available |

---

## 8. Open questions for review rounds

1. **Location.** Should `kit/` be a top-level directory in this repo, or its own public repo from
   day one? A separate repo makes "stranger" real and history clean. The in-repo option keeps one
   CI and one bead store.
2. **Gate labels.** Is the outcome join (reverts, dcg denies, undo phrases) a good enough label
   for the promotion bar, or does G3 need blind human labels only?
3. **Package manager.** AGENTS.md mandates npm. Is `npm i github:...#path:kit` actually
   supported, or do we need a published package or a tarball release?
4. **Size estimation.** Should the kit estimate size with the empirical band (1.48–2.08 bytes per
   token) or call a tokenizer? Check whether the SDK exposes one.
5. **Receipt privacy.** Is `state_hash` enough for replay, or do strangers need an opt-in
   raw-state mode?

---

## Appendix

- **A1.** Research reports (`local://` paths are session-scoped). Copy the four reports into
  `notes/deep/next-gen/research-20260925/` when this plan is committed.
- **A2.** Duel artifacts: `notes/deep/duel-20260925/`.
- **A3.** The commit classifier for the code-share signal: the inline Python in pane 1's session,
  2026-09-25. It classifies `.beads/` = beads; the root ledgers = ledger; `notes/`, `docs/` and
  `*.md` = prose; `jsonl|json|tsv|csv|txt` = data; everything else = code. Commit it as
  `scripts/commit-mix.py` with WP-S.
