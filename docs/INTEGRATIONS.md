# Integrations — proven vs WIP OMP/Jev seams

This is the user-facing scoreboard for what we have actually wired into OMP, and at which claim level. It is not a roadmap.

**0 promoted.** Re-derive from `docs/demos/STATUS.tsv` (column 4 = `verdict`; rung 5 in the header is `promoted`). No row in that file is `PROMOTED`. The one promotion awarded was retracted the same day when real data arrived (`README.md` Status; `NEGATIVE_EVIDENCE.md` R31). Receipts live under `docs/demos/` and `docs/demos/upstream-repro/`.

Do not read a later rung than the evidence named below. **BUILT ≠ WIRED; WIRED ≠ VALIDATED.**

### How citations work here

If this page mentions `fh`, it is as a *ranker*, not as a citation. `fh doctor` may report STALE
or degraded SCHEDULING (a 1/8 schedule-declaration miss does not retract shipped doctrine).
Corpus citations already in this repo were opened at file:line from the pinned Dicklesworthstone
mirror after `fh` ranked them — `asupersync` `eprocess.rs:224-238`, `franken_ocr`
`RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch`
`perf_ratchet.rs:732-740`. Pattern: **fh ranked, we opened.** A ranking alone is not a citation.

## RULE WINS: four regexes, no Jev call — drop Jev from `tool_call`

We set out to wire Jev into omp and shipped FOUR REGEXES WITH NO JEV CALL IN THEM.
Five surfaces, five cheap wins (cost-benefit, not capability). **Not a Jev promotion.
The ledger stays 0 promoted.**

Receipt: [`toolcall-headtohead-20260919.md`](demos/upstream-repro/toolcall-headtohead-20260919.md) (`f7bcd9d`). Ruling, second axis: [`RULING-authored-vs-real-20260919.md`](demos/upstream-repro/RULING-authored-vs-real-20260919.md) (`268073e`). Claim repro: [`harm-rule-claim-repro-20260919.md`](demos/upstream-repro/harm-rule-claim-repro-20260919.md). Pane 3 scored; pane 2 authored the rule. Held-out split neither scoring pane authored.

**Published rule claim.** Recall **12/12**, FP **0/38** on the committed corpus.
`node work/omp-harm-rule/verify-claim.mjs` exits 0. **Do not cite 0/40 for the rule** —
that denominator is historical and unreproducible (`NEGATIVE_EVIDENCE.md` R34; two
benign cases never committed).

| arm | FP | recall | bar |
|---|---|---|---|
| rule (unmodified, shasum-verified) | **0/38** (committed corpus; `verify-claim.mjs`) | **12/12** | PASS |
| live Jev (`jev-latest` → `jev-1.13.0`) | **0/40** (historical receipt; unreproducible offline) | **11/12** | PASS, strictly dominated |
| dumb keyword list | **0/40** (historical receipt; unreproducible offline) | **5/12** | MISS |
| feasibility (test-path) | — | AUC **1.000** | PASS |

The FP column is **not** a like-for-like comparison. Only recall (12/12 vs 11/12 vs 5/12)
still compares cleanly. Jev's miss is r3 (`git push --force origin main`). **Jev was not
bad** — 11/12 is strong in isolation. This is a cost-benefit kill, not a capability kill.
Ship the classifier; drop Jev from this surface. **Caveat measured 2026-09-20, load-bearing, and updated once the fix landed:** the 12/12 above is a CURATED-CORPUS result and the classifier is **unevidenced in the wild in both directions**. Precision: organic fires were 0-of-28 correct on 80,975 real allow-commands, every one mention-vs-use ([`§17`](demos/upstream-repro/waved-s17-organic-precision-20260920.md), `c20da52`); a positional mention-vs-use stripper cut that to **5 fires on 81,262** and all five are still false, so the defect retreated from shell quoting into program literals rather than dying ([`R44`](../NEGATIVE_EVIDENCE.md), `e33bd5d`). Recall: a sweep of **every** `dcg_block` in this repo's history — 1,338 blocked calls, 843 with text, 75 in scope under a deliberately generous filter — found **no genuinely dangerous in-class command was ever typed here**, and the shipped rule fired on 0 of the 25 sampled ([`jev-m7r`](demos/upstream-repro/m7r-harm-recall-ruling-20260920.md), `4bf1067`). **An empty confusion matrix is not a failing one** — the rule is not shown to be wrong, it is shown to be untested by reality. Any claim about it must name its corpus.

### Five-link chain (receipts on this tip)

| # | claim | evidence |
|---|---|---|
| 1 | **earns** | 12/12 recall, FP **0/38**, verify-claim exits 0. [`harm-rule-claim-repro-20260919.md`](demos/upstream-repro/harm-rule-claim-repro-20260919.md). |
| 2 | **registered** | `extensions:` list; loader globs `*.{ts,js}`; lab `jev-lab`. [`harm-rule-shipped-20260919.md`](demos/upstream-repro/harm-rule-shipped-20260919.md). |
| 3 | **fires (lab)** | Both directions on luna and sol in lab. [`harm-rule-shipped-20260919.md`](demos/upstream-repro/harm-rule-shipped-20260919.md). On this tip the shipped file writes `toolCallId` (`work/omp-harm-rule/harm-rule.ts`). |
| 4 | **fires correctly (lab)** | **0/17** unique-command divergence vs the frozen scorer. [`harm-rule-conformance-20260919.md`](demos/upstream-repro/harm-rule-conformance-20260919.md) (`bb4fa4f`). Lab shapes ≠ every profile. |
| 5 | **working-profile dogfood — NOT VERIFIABLE / OPEN** | [`harm-rule-promoted-20260919.md`](demos/upstream-repro/harm-rule-promoted-20260919.md) (`6c9c8fc`) **exists on this tip**. It is one driven first-contact probe, not multi-row live logger traffic on a working profile. **Do not publish RUNS ON REAL WORK.** Organic precision now measured: **0/28** over 80,975 real allow commands, every fire mention-vs-use (quoted prompts, test strings, doc prose, loopback bodies) — [`waved-s17-organic-precision-20260920.md`](demos/upstream-repro/waved-s17-organic-precision-20260920.md). The earlier "4/4 driven probes" line is superseded. [`harm-rule-realtraffic-20260919.md`](demos/upstream-repro/harm-rule-realtraffic-20260919.md). |

Source: `work/omp-harm-rule/harm-rule.ts`. Observe-only. Every path returns `undefined`.
dcg remains the only blocker. Zero model calls in the shipped path.

**Silent-register rule.** A module with valid syntax and no `pi.on` registers nothing.
`node --check` passes it. A hook that fails to register is indistinguishable from a hook
that sees nothing (`harm-rule-shipped-20260919.md`). The co-presence bar is observer
decisions next to a bridge row in the same session.

**Observer (B) — mechanism MET at n=1 lab; working-profile dogfood OPEN.**
`a2e2035` stores `toolCallId` and deleted the defaulted `context.dcgVerdict`
from the makeRecord path. Residual: `createObserver` / `installObserver` still
defaults `context.dcgVerdict ?? 'unknown'` on the gate path. The five-link
chain is the harm-rule, not the Jev observer. Do not publish working-dogfood.

**NO-CLAIM.** One profile; our traffic; observe-only; lab shapes ≠ every profile. Recall is
on 12 planted harms, not observed incidents. Cross-model traffic is unattributed.

## OPEN: tool_call error prevalence — 3.95% (40× the 0.1% kill line)

Receipt: [`docs/demos/upstream-repro/toolcall-groundtruth-corpus-20260919.md`](demos/upstream-repro/toolcall-groundtruth-corpus-20260919.md) (`33aa633` on `main`). Pane 3 (muse), 2026-09-19. **Zero API.** Harness `work/p3-calibration/mine_decisions.py`; frozen sample `work/p3-calibration/toolcall-corpus-frozen.jsonl`.

**Headline.** 216,507 dcg decisions (11,727 files). On joinable allowed commands (n=78,455): `isError` **3.95%** (3,098). Frozen sample **4.01%** (315/7,846). Frozen split, time-ordered at 2026-09-10T00:00:00Z: **36,955** train (err 4.3%) / **41,500** held-out (err 3.6%). Against the 0.1% kill line the surface is **not killed** — machine-observable badness is ~**40×** above it (`toolcall-groundtruth-corpus-20260919.md:47-55`). *As-of 2026-09-19 receipt; live corpus re-derived 2026-09-20 at n=221,873 decisions / GOOD+BAD 82,278 at 3.89% — conclusion unchanged. Regen: `python3 work/p3-calibration/mine_decisions.py` (minutes, read-only; writes gitignored `decisions_full.jsonl`, delete after).*

True harm is strictly below 3.95% (benign errors: grep-no-match etc.) and unmeasured without human review. Transcript-derived outcomes are a proxy for harm, not harm.

### JOIN YIELD 36.8% — capture command text at decision time

Of 216,507 decisions, 79,743 resolve to a command AND an outcome (**36.8%**). The 63.2% miss is one mechanistic class, not random loss: 136,718/136,764 miss tids (99.997%) are `js-bash-<uuid>` — a foreign id namespace with no transcript mapping (`toolcall-groundtruth-corpus-20260919.md:27-35`). History recovers barely a third.

**The logger must capture command text at decision time.** That is why `work/dogfood-logger/` exists. Decision rows carry exactly `{kind, toolCallId}` — no command (`dcg-block-rate-prior-20260919.md:46-51`). The shipped harm rule does capture `command` at decision time; see `NEGATIVE_EVIDENCE.md` R33 and its correction.

### Pane 3 withdrew the revert-predicate (INVALIDATED)

BAD was `isError` **or** a revert-signal regex on the next three user messages. A laxer revert predicate (bare failed/wrong/stop) put 59k of 62k BAD through coordination chatter ("revision, not revert", "repair the gate-runner FAIL") — demonstrated with verbatim examples, **WITHDRAWN**, not reported (`toolcall-groundtruth-corpus-20260919.md:37-45`). Revert-signal prevalence is not reported (predicate invalid on coordination traffic). **`isError` survived.**

### fail-open verified at `dcg-guard.ts:599-610`

Infrastructure failure + non-block classification returns `undefined` (= allow): fail-open CONFIRMED. Exit 1 without a blocking decision still blocks (`:615-617`). Source for that claim: the corpus check at `toolcall-groundtruth-corpus-20260919.md:9-12`, which opened `dcg-guard.ts:599-610`. Do not inherit a proposed certification file.

## Proven: `jev-compact` — L3 measurement instrument

| | |
|---|---|
| **What it is** | A `session_before_compact` hook that asks Jev keep/drop questions about the prefix omp has already decided to summarize, then **logs the verdict**. |
| **What it is not** | A pruner. It does not shrink the session. omp's own summarizer keeps the job. |
| **Claim level** | **L3** — the seam fires in a real omp session, and a known-bad envelope makes it refuse. **L4 is not reached and is not reachable on this seam** as Jev-pruning. |
| **Install** | `compaction/install-jev-compact.sh` |
| **Skill** | `.omp/skills/jev-compact/SKILL.md` |

### The load-bearing facts, with file:line

- The handler **only ever returns `undefined`**. A compact verdict is logged as `would-compact` and yielded; omp's summarizer does the actual compact. See `compaction/src/omp-hook.ts:217-222` and `compaction/src/omp-binding.ts:173-182`.
- The installer itself says what it verifies and what it never claims: placement plus dependency resolution, **not** firing (`compaction/install-jev-compact.sh:16-17`).
- The deployed entry is the same three-line wrapper: `compaction/deploy/hook-entry.ts:7-9`.
- Fail-open / fail-safe direction: every path yields. A missing key registers **nothing** (`compaction/src/omp-binding.ts:226-231`). A Jev outage, a malformed envelope, or a below-minimum reduction costs a missed optimisation, never context (`compaction/src/omp-hook.ts:93-97`).
- **Never claim a session was shrunk by this hook.** Stated in the skill (`.omp/skills/jev-compact/SKILL.md:19-21`) and in the live receipt (`docs/demos/omp-seam-live-20260918.md:104-108`). Replay-harness reductions (library over a transcript) are a different claim from a live `/compact`.
- Why L4-as-Jev-pruning is refused: omp consumes a fromHook result as `{summary, firstKeptEntryId, ...}`, not a pruned-message list. Jev judges; it does not write the required `summary` string. `NEGATIVE_EVIDENCE.md` R21 (`:780-783`) and `docs/demos/omp-seam-fqo-20260919.md:42-43`.

### How to see that it fired

```bash
./compaction/install-jev-compact.sh /path/to/your/repo
# restart that repo's omp session WITH TYPESAFE_API_KEY
# run /compact, then:
tail ~/.jev-compact.log
```

`refused` / `passthrough` / `would-compact` are decisions. No new line means the hook did not run — not a silent success.

## WIP: observe-and-log / dogfood logger — fires on jev-lab; co-presence MET, id-join proven at n=1, working profile OPEN

The append-only decision/outcome logger lives at `work/dogfood-logger/`. Its schema, join, concurrent appends, and rotation are tested locally (`work/dogfood-logger/test/logger.test.mjs`; receipt `docs/demos/upstream-repro/dogfood-logger-20260919.md`). The observer library is at `work/omp-jev-observer/` (offline: 5 tests; receipt `docs/demos/upstream-repro/omp-jev-observer-20260919.md`).

**Measured on the `jev-lab` profile's session JSONL (counts re-derived by the conductor at
2026-09-19T21:50Z, not quoted from a callback):**

| row type | count |
|---|---|
| `com.zeststream.omp-jev-observer.decision.v1` | **28** |
| ├ with a nonempty `toolCallId` | **1** |
| ├ `dcgVerdict: "unknown"` (defaulted, legacy) | **27** |
| └ `dcgVerdict` absent (correct, post-`a2e2035`) | **1** |
| `com.zeststream.omp-jev-observer.diagnostic.v1` | **55** |
| `com.zeststream.omp-dcg-bridge.decision.v1` | **27** (all `kind=dcg_allow`) |
| joins by `toolCallId` to a same-session bridge row | **1** |
| sessions containing observer decision **and** bridge rows | **10** |

Three separate claims. The first is met, the second is met **as a mechanism at n=1 in a lab
profile only**, and the third is open:

- **(A) Session co-presence — MET.** **Ten** lab sessions carry observer decision rows alongside
  `com.zeststream.omp-dcg-bridge.decision.v1` rows with a real verdict.
- **(B) Id-join — MECHANISM MET, n=1, lab only.** `a2e2035` wired `event.toolCallId` into
  decision records and **deleted** the fictional `context.dcgVerdict ?? 'unknown'` default.
  Re-derived live: **28** observer decisions, **1** with a nonempty `toolCallId`, **27** bridge
  rows, **1 join by id**. `dcgVerdict` is `unknown` on the **27** legacy rows and **absent** on
  the **1** new row — absent is the correct state; the event exposes
  `[type, toolName, toolCallId, input]` and **no verdict**, so every `unknown` was a default,
  never an observation. Receipt `docs/demos/upstream-repro/omp-jev-observer-id-join-20260919.md`;
  gate note `GATES.md` (`0b21798`).
  **One join is a mechanism, not a rate.** It proves the wiring; it says nothing about how often
  joins succeed, and it is not working-profile dogfood.
  **Residual:** `installObserver` / `createObserver` still defaults
  `dcg: ... context.dcgVerdict ?? 'unknown'` on the gate path
  (`work/omp-jev-observer/src/observer.mjs`). That fiction is not fully removed.
  **The cross-namespace seam is untouched.** Observer↔bridge joins because both are `js-bash-*`;
  observer↔`tool_execution_start` (`call_…|fc_…`) remains refused at overlap **0**
  (`GATES.md:152-158`).
- **(C) Working profile — STILL OPEN, not claimed.** Everything above is `jev-lab`, a disposable
  profile. No multi-row live logger exists on a working profile. This is not continuous or
  production dogfood. **Promoted: 0.** The harm-rule's `codex` registration is a
  different extension and does not close observer claim **(B)** or this
  working-dogfood claim.

An earlier version of this section reported *0 observer rows against 1 bridge row*. That was true
when written and is now stale; the zero-row cause was a module with valid syntax whose `pi.on`
registration line was absent — reproduced deliberately and repaired
(`harm-rule-shipped-20260919.md`, `658922f`). **A hook that fails to register is indistinguishable
from a hook that sees nothing.** The loader globs `*.{ts,js}`; the config is an `extensions:` list
in the profile `agent/config.yml`.

Live omp was never taken off the table. There is **no standing ban** on registering into working omp profiles. The fleet invented "STOP-LIVE" / deferred registration as reasons not to work. This row is not an indefinite deferral and not quiet-window gated.

### How to iterate on live omp

**Live test surface = pane 0** in the jev NTM session, or **added test panes** in that same session. That is not a separate agent farm. OMP is the common harness across many model/agent types. Do not take down mid-flight panes to dogfood.

- **Register / dogfood on pane 0 or an added test pane.** Leave mid-flight panes untouched. Promote only after receipts.
- **RUN-CLONE.** Local clones and disposable lab profiles (`omp --profile jev-lab`) are free for atomic mutation, planted known-bad, and improvement loops. Quiet-window is not a science gate for that work. `jev-lab` is where the 0-row defect was seen — that is a finding, not a working install.
- **The improvement loop** — carve the cases regex cannot express, tighten criteria, re-measure against the 0.97% dcg prior (`docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md`) and the 3.95% allowed-command error rate — is how a later fire on pane 0 / an added test pane is earned. Then promote.

### Engineering checks before the act

A `tool_call` observer on `bash` would fire on every bash in every session, so the act has preconditions. They are the gate. They are not a quiet-window gate and not a reason to DEFER the loop:

1. **Offline proof first** — writer tests green; a synthetic `tool_call` proves the handler returns `undefined` on success, error, and timeout.
2. **Fail-open** — logger/observer failures return `false` / `undefined` and never throw into the host (`work/dogfood-logger/src/logger.mjs`; `compaction/src/omp-binding.ts:226-231`). Guard fail-open is verified at `dcg-guard.ts:599-610` (corpus `toolcall-groundtruth-corpus-20260919.md:9-12`).
3. **`0 block:true`** — observe only. Never return omp's `{block: true, reason}` shape.
4. **jsm preconditions** — the installed file must be self-contained. `9e6c88d` imported `../../dogfood-logger/src/logger.mjs`, a parent path that does not exist after a copy into `~/.omp`. `348894e` inlined the record builder so the extension no longer depends on a repo-relative parent.
5. **The loader must actually load it.** Globs `*.{ts,js}`. Config is `extensions:` in the profile `agent/config.yml`. A register that writes 0 rows while another extension writes rows is not loaded — verify against a known-firing neighbour, never against silence alone.

Session co-presence is met (**10** sessions, lab only). The id-level join is now proven as a
**mechanism at n=1** — `a2e2035` stores `event.toolCallId` and drops the defaulted verdict, and
**1** of **28** observer decisions joins a same-session bridge row by id. That is wiring, not a
rate. The remaining condition for calling the observer **working** is a **working profile under
real traffic**, which has not been attempted: no multi-row live logger exists outside `jev-lab`,
and **promoted is 0**. There is no dogfood or observer file under `.omp/hooks/` on this tip; the
only pre-hook in this tree is `jev-compact`. A residual `context.dcgVerdict` default still exists
on the `createObserver` gate path.

**Where a probabilistic judge belongs.** Only on what regex cannot express. Measured on this surface: the classifier wins and Jev is dropped ([`toolcall-headtohead-20260919.md`](demos/upstream-repro/toolcall-headtohead-20260919.md)). The dcg prior is on this tip: [`docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md`](demos/upstream-repro/dcg-block-rate-prior-20260919.md) — 49,661 allow / 488 block = **0.97%**.

## WIP / UNPROMOTED: taste-loop packages — observe-only scaffold

Eleven `work/omp-jev-*` product-taste packages landed in
[#16](https://github.com/JYeswak/jev_playground/pull/16). Shared kit:
[`work/taste-loop/README.md`](../work/taste-loop/README.md). The binding contract is
[`work/taste-loop/CONTRACT.md`](../work/taste-loop/CONTRACT.md).

**Claim level: observe-only scaffold.** Not wired to working profiles. Not validated
on live traffic. Not working-dogfood. **Not promoted.** Do not copy into `~/.omp` —
imports are repo-relative (`work/jev-client`, `work/taste-loop`).

Names from the tree: `omp-jev-default`, `omp-jev-field`, `omp-jev-firstlook`,
`omp-jev-fork`, `omp-jev-heat`, `omp-jev-heckle`, `omp-jev-jargon`,
`omp-jev-promise`, `omp-jev-skip`, `omp-jev-uncanny`, `omp-jev-undo`. Heat is
attention leftover, not taste.

**NO-CLAIM.** Offline tests and frozen questions only. `measure.mjs` is a harness,
not a result. No live accuracy. Ledger stays **0 promoted**.

## WIP / UNPROMOTED: skillranker process mirror — route slice

Process copied from `Dicklesworthstone/skillranker@6a74cca` into
[`work/omp-jev-route`](../work/omp-jev-route/): abstention (`__none__` / local
eligibility), structured JSON decision log, preregistered 0/1/2 eval gate.
Receipt: [`demos/upstream-repro/skillranker-process-mirror-20260919.md`](demos/upstream-repro/skillranker-process-mirror-20260919.md).

**Claim level: offline process slice.** Not registered on a working profile. Not
a re-score of their corpus. Not working-dogfood. **Not promoted.**
`diagnostic_synthetic` cannot promote.

ACCEPTANCE (no key, no network):

```bash
node work/omp-jev-route/src/cli.mjs decide --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
node work/omp-jev-route/src/cli.mjs gate --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs
```

## WIP / UNPROMOTED: skill-router eval-contract mirror

Harness at [`work/skillranker-eval/`](../work/skillranker-eval/README.md). Mirrors
`Dicklesworthstone/skillranker` `tests/eval/` @ `bb52b8f25` (pulled via `gh`,
provenance in `contract/PROVENANCE.md`): frozen 0/1/2 loss, always-abstain and
coin-flip as first-class runners, ≥0.90 top-1 as an **explicit FAIL**, planted
wrong-pick that must score 2, JSONL eval-row export.

This is the Wave C add-on named in
[`commit-learnings-20260919.md`](demos/upstream-repro/commit-learnings-20260919.md)
(abstention + eval gate ≥0.90 + JSONL export). The register at
`work/jev-score-register/` already persists numeric Jev scores; this harness
exports the **eval** row (pick / Y / loss) the register's `score` field cannot
carry.

**Claim level: unpromoted process mirror.** Offline controls and planted RED
only. Live lane is `NOT_RUN` without a key. **Not a SkillRanker product
measurement** — no `sr` binary path is invoked. n=12 is `diagnostic_synthetic`;
their contract forbids promotion on it. A prior live Jev-on-corpus receipt
(mean loss 0.167, top-1 0.800) lives at
[`skillranker-corpus-measured-20260919.md`](demos/upstream-repro/skillranker-corpus-measured-20260919.md)
and is not re-run here.

**NO-CLAIM.** Unpromoted. Ledger stays **0 promoted**.

## Scoreboard

| Surface | State | Claim | Promoted? |
|---|---|---|---|
| tool_call / harm-rule | RULE WINS; four regexes, **no Jev call**; links 1–4 lab/corpus; link 5 **NOT VERIFIABLE** as working-dogfood | rule 12/12, FP **0/38** committed corpus; Jev 11/12 / dumb 5/12, historical FP 0/40 unreproducible (R34); first-contact `6c9c8fc` ≠ multi-row live logger; cost-benefit kill | no |
| tool_call ground-truth corpus | OPEN; 216k decisions, zero API | 3.95% isError on allowed (frozen 4.01%); 40× the 0.1% kill line; join yield 36.8% | no |
| `jev-compact` / `install-jev-compact.sh` | ships; fires in real `/compact` | L3 measurement; does **not** prune | no |
| dogfood / observe-and-log | `jev-lab`: observer **28** decision / **55** diagnostic rows; bridge **27**; **10** sessions co-present; **1** join by `toolCallId` — ALL from the deployed variant, which differs from the shipped tree | **partial, qualified** — co-presence MET on the deployed copy; the shipped `work/omp-jev-observer/src/observer.mjs` **cannot fire** (calls undefined `safeAppend`, deterministic silence — [`waved-s16-observer-dogfood-20260920.md`](demos/upstream-repro/waved-s16-observer-dogfood-20260920.md)). Do not read this row as "the tree works." Working-profile dogfood **OPEN** | no |
| taste-loop (`omp-jev-{default,field,firstlook,fork,heat,heckle,jargon,promise,skip,uncanny,undo}`) | WIP / UNPROMOTED; observe-only scaffold | not wired to working profiles; not validated on live traffic; see `work/taste-loop/CONTRACT.md` | no |
| skillranker process mirror (`omp-jev-route` slice) | WIP / UNPROMOTED; offline decide/gate CLI | abstain + JSON log + copied 0/1/2 gate; not working-dogfood; not their corpus | no |

| skill-router eval-contract mirror (`work/skillranker-eval/`) | WIP / UNPROMOTED; process mirror of skillranker `tests/eval` @ `bb52b8f25` | offline controls + planted RED; ≥0.90 is a hard FAIL; JSONL eval export; **not** an `sr` product measurement | no |
| score exports (Jev-derived) | **19 of 21** packages export scores; NOT-APPLICABLE: `preaction`, `harm-rule` (rows without model calls) | supersedes the "1 of 21" in `commit-learnings-20260920.md` | n/a |
| `jevcache` | **REMOVED and disqualified** | `8fe44b2` removal + `f717ba3` correction; nothing routes through a cache (identical answers make drift invisible) | n/a |
| score register replay | pinned fixture `c4e0e7c4…`, 55 rows | replays with **`api calls made: 0`** (`work/jev-score-register/replay.mjs` does not import the client) | n/a |
| STATUS ledger (`docs/demos/STATUS.tsv`) | 0 `PROMOTED` rows | rulings, not products | **0** |

Further receipts: `docs/demos/omp-seam-live-20260918.md`, `docs/demos/omp-seam-fqo-20260919.md`, `docs/demos/upstream-repro/dogfood-logger-20260919.md`, `docs/demos/upstream-repro/omp-jev-observer-20260919.md` (do not read as working/production dogfood), `docs/demos/upstream-repro/toolcall-headtohead-20260919.md`, `docs/demos/STATUS.tsv`, `NEGATIVE_EVIDENCE.md` R21 / R31.
