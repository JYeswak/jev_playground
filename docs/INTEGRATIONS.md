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

## RULE WINS: drop Jev from the `tool_call` surface (cost-benefit kill)

Receipt: [`docs/demos/upstream-repro/toolcall-headtohead-20260919.md`](demos/upstream-repro/toolcall-headtohead-20260919.md) (`f7bcd9d` on `main`). Ruling, second axis: [`docs/demos/upstream-repro/RULING-authored-vs-real-20260919.md`](demos/upstream-repro/RULING-authored-vs-real-20260919.md) (`268073e`). Pane 3 (muse) scored; pane 2 authored the rule. Held-out split neither scoring pane authored. **Not a promotion.**

**Headline.** Ship pane 2's classifier; drop Jev from this surface. Four regexes beat the model on recall at identical false-positive rate, at zero cost and zero latency.

| arm | FP | recall | bar |
|---|---|---|---|
| rule (unmodified, shasum-verified) | **0/40** | **12/12** | PASS |
| live Jev (`jev-latest` → `jev-1.13.0`) | **0/40** | **11/12** | PASS, strictly dominated |
| dumb keyword list | **0/40** | **5/12** | MISS |
| feasibility (test-path) | — | AUC **1.000** | PASS |

Jev's miss is r3 (`git push --force origin main`). **Jev was not bad** — 11/12 with 0 FP on 40 benign commands is strong in isolation. This is a cost-benefit kill (API per tool call), not a capability kill.

**The pattern, which is the headline.** Fifth time a dumb baseline beat the model: phishing regex +27 points; flat mid-tier pricing (Jev +90.2% more expensive); prompt length (2 of 3 sessions); keep-everything on compaction (7× fewer mistakes); four regexes on tool-call harm. **Where the harm is expressible, express it.** A judge earns its place only where a rule cannot be written; five surfaces did not find such a place.

**NO-CLAIM.** Cross-model traffic is unattributed. Recall is on 12 planted harms, not observed incidents. This does not make the live observer working dogfood.

## OPEN: tool_call error prevalence — 3.95% (40× the 0.1% kill line)

Receipt: [`docs/demos/upstream-repro/toolcall-groundtruth-corpus-20260919.md`](demos/upstream-repro/toolcall-groundtruth-corpus-20260919.md) (`33aa633` on `main`). Pane 3 (muse), 2026-09-19. **Zero API.** Harness `work/p3-calibration/mine_decisions.py`; frozen sample `work/p3-calibration/toolcall-corpus-frozen.jsonl`.

**Headline.** 216,507 dcg decisions (11,727 files). On joinable allowed commands (n=78,455): `isError` **3.95%** (3,098). Frozen sample **4.01%** (315/7,846). Frozen split, time-ordered at 2026-09-10T00:00:00Z: **36,955** train (err 4.3%) / **41,500** held-out (err 3.6%). Against the 0.1% kill line the surface is **not killed** — machine-observable badness is ~**40×** above it (`toolcall-groundtruth-corpus-20260919.md:47-55`).

True harm is strictly below 3.95% (benign errors: grep-no-match etc.) and unmeasured without human review. Transcript-derived outcomes are a proxy for harm, not harm.

### JOIN YIELD 36.8% — capture command text at decision time

Of 216,507 decisions, 79,743 resolve to a command AND an outcome (**36.8%**). The 63.2% miss is one mechanistic class, not random loss: 136,718/136,764 miss tids (99.997%) are `js-bash-<uuid>` — a foreign id namespace with no transcript mapping (`toolcall-groundtruth-corpus-20260919.md:27-35`). History recovers barely a third.

**The logger must capture command text at decision time.** That is why `work/dogfood-logger/` exists. Decision rows carry exactly `{kind, toolCallId}` — no command (`dcg-block-rate-prior-20260919.md:46-51`).

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

## WIP: observe-and-log / dogfood logger — fires on jev-lab; session co-presence MET, id-join NOT

The append-only decision/outcome logger lives at `work/dogfood-logger/`. Its schema, join, concurrent appends, and rotation are tested locally (`work/dogfood-logger/test/logger.test.mjs`; receipt `docs/demos/upstream-repro/dogfood-logger-20260919.md`). The observer library is at `work/omp-jev-observer/` (offline: 5 tests; receipt `docs/demos/upstream-repro/omp-jev-observer-20260919.md`).

**Measured on the `jev-lab` profile's session JSONL (counts re-derived, not quoted):**

| row type | count |
|---|---|
| `com.zeststream.omp-jev-observer.decision.v1` | **14** |
| `com.zeststream.omp-jev-observer.diagnostic.v1` | **33** |
| `com.zeststream.omp-dcg-bridge.decision.v1` | **13** (all `kind=dcg_allow`) |
| sessions containing observer decision **and** bridge rows | **6** |

Three separate claims, and only the first is met:

- **(A) Session co-presence — MET.** Six lab sessions carry observer decision rows alongside
  `com.zeststream.omp-dcg-bridge.decision.v1` rows with a real verdict.
- **(B) Id-join — NOT met.** All **14** observer decisions carry `dcgVerdict: "unknown"`, and the
  observer rows carry no `toolCallId`, so the id-level join to bridge rows is **0**. The event
  exposes `[type, toolName, toolCallId, input]` and **no verdict**, so the original
  `context.dcgVerdict` read a field that does not exist: those `unknown`s are defaults, not
  observations. The non-duplication filter is therefore **corrected, not working-as-designed**.
- **(C) Working profile — NOT claimed.** Everything above is `jev-lab`, a disposable profile.
  None of it is evidence about a working profile under real user traffic. This is not
  continuous or production dogfood.

**NO-CLAIM (join seam).** On the private tip, the harm-rule extension now emits `toolCallId`
(`daf3e93`); the Jev observer still does not. That is the remaining id-join seam, not a
co-presence failure.

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

Session co-presence has now been observed (6 sessions, lab only), so that condition is met. The remaining conditions for calling the observer working are the **id-level join** (currently 0: no `toolCallId` on observer rows, all verdicts defaulted to `unknown`) and a **working profile under real traffic**, which has not been attempted. There is no dogfood or observer file under `.omp/hooks/` on this tip. The only pre-hook in this tree is `jev-compact`.

**Where a probabilistic judge belongs.** Only on what regex cannot express. Measured on this surface: the classifier wins and Jev is dropped ([`toolcall-headtohead-20260919.md`](demos/upstream-repro/toolcall-headtohead-20260919.md)). The dcg prior is on this tip: [`docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md`](demos/upstream-repro/dcg-block-rate-prior-20260919.md) — 49,661 allow / 488 block = **0.97%**.

## Scoreboard

| Surface | State | Claim | Promoted? |
|---|---|---|---|
| tool_call head-to-head | RULE WINS; ship classifier, drop Jev | rule 12/12 vs Jev 11/12 vs dumb 5/12, both FP 0/40; cost-benefit kill | no |
| tool_call ground-truth corpus | OPEN; 216k decisions, zero API | 3.95% isError on allowed (frozen 4.01%); 40× the 0.1% kill line; join yield 36.8% | no |
| `jev-compact` / `install-jev-compact.sh` | ships; fires in real `/compact` | L3 measurement; does **not** prune | no |
| dogfood / observe-and-log | `jev-lab`: observer **14** decision / **33** diagnostic rows; bridge **13**; **6** sessions co-present | **partial** — session co-presence MET, id-join **0** (no `toolCallId`, all `dcgVerdict` defaulted `unknown`); lab only; not working/production dogfood | no |
| STATUS ledger (`docs/demos/STATUS.tsv`) | 0 `PROMOTED` rows | rulings, not products | **0** |

Further receipts: `docs/demos/omp-seam-live-20260918.md`, `docs/demos/omp-seam-fqo-20260919.md`, `docs/demos/upstream-repro/dogfood-logger-20260919.md`, `docs/demos/upstream-repro/omp-jev-observer-20260919.md` (do not read as working/production dogfood), `docs/demos/upstream-repro/toolcall-headtohead-20260919.md`, `docs/demos/STATUS.tsv`, `NEGATIVE_EVIDENCE.md` R21 / R31.
