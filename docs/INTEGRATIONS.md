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

## THE INTEGRATION RUNS ON REAL WORK — four regexes, no Jev call, one profile

We set out to wire Jev into omp and shipped four regexes with no Jev call in them. The model lost
on five surfaces to cheaper alternatives — never because it was bad, always because something free
was as good or better. The integration that survived contains none of it. **Not a Jev promotion.
The ledger stays 0 promoted.**

**Tip note.** Prefer SHA `6c9c8fc` (`harm-rule-promoted`). That object is **absent from this
checkout and from GitHub** (`git cat-file` fails; GitHub 422). Conformance SHA `bb4fa4f` is
likewise absent. This chapter is cut from `f556b1f`. Cited local receipt paths below; facts
3–5 are **cited, not re-derived**.

### Five-link chain

| # | claim | evidence |
|---|---|---|
| 1 | **earns** | 12/12 recall, FP **0/40** held-out; beat Jev **11/12** and dumb **5/12**. [`toolcall-headtohead-20260919.md`](demos/upstream-repro/toolcall-headtohead-20260919.md) (`f7bcd9d`). |
| 2 | **registered** | `extensions:` list in the profile `agent/config.yml`; loader globs `*.{ts,js}`; **one profile**. Lab register: [`harm-rule-shipped-20260919.md`](demos/upstream-repro/harm-rule-shipped-20260919.md) (`287f4b9`, `jev-lab`). Working-profile register is `codex` only. |
| 3 | **fires** | id-join `toolCallId` to a real `dcg_allow`. Event keys on this tip are `[type, toolName, toolCallId, input]` — no verdict on the event. **Cited, not re-derived:** `work/omp-harm-rule/harm-rule.ts` on this tip does not write `toolCallId` onto its rows. Join the bridge at read-time. |
| 4 | **fires CORRECTLY** | **0/17** unique-command divergence. Cited path `docs/demos/upstream-repro/harm-rule-conformance-20260919.md` (`bb4fa4f`) — **object absent from this checkout and from GitHub**. |
| 5 | **RUNS ON REAL WORK** | Promoted to working omp profile **`codex`** (not `claude`, not all). 5 harm rows (2 decision + 3 diagnostic) + 2 bridge; zero errors; rollback unused. Panes 1/2/3 run on `codex` = this lane's own first real traffic. Cited path `docs/demos/upstream-repro/harm-rule-promoted-20260919.md` (`6c9c8fc`) — **object absent from this checkout and from GitHub**. |

Source on this tree: `work/omp-harm-rule/harm-rule.ts`. Observe-only. Every path returns `undefined`.
dcg remains the only blocker. Zero model calls in the shipped path.

### Also published

- **Five-surface dumb-baseline pattern.** Phishing regex +27 points; flat mid-tier pricing (Jev
  +90.2% more expensive); prompt length (2 of 3); keep-everything on compaction (7× fewer
  mistakes); four regexes on tool-call harm. Ruling, second axis:
  [`RULING-authored-vs-real-20260919.md`](demos/upstream-repro/RULING-authored-vs-real-20260919.md)
  (`268073e`). **Where the harm is expressible, express it.**
- **Silent-register rule.** A module with valid syntax and no `pi.on` registers nothing.
  `node --check` passes it. A hook that fails to register is indistinguishable from a hook that
  sees nothing (`harm-rule-shipped-20260919.md`, `658922f`). Verify against a known-firing
  neighbour, never against silence alone.
- **Co-presence bar.** Observer (or harm-rule) decision rows next to a
  `com.zeststream.omp-dcg-bridge.decision.v1` row in the same session. Session co-presence is
  not id-join.
- **`context.dcgVerdict` was fiction.** The event has no verdict field. Those `unknown`s on the
  Jev observer are defaults, not observations. Join the bridge by `toolCallId` at read-time.

### NO-CLAIM (load-bearing)

- **ONE profile** — `codex`. Not `claude`. Not all profiles.
- **OUR traffic** — panes 1/2/3 on `codex`. Not a stranger's fleet.
- **OBSERVE-ONLY** — `0 block:true`. dcg is still the only thing that blocks.
- **Lab shapes ≠ every profile.** Short prompted lab runs are not every working profile.
- **Observer claim (B) STILL OPEN.** The Jev observer still has no `toolCallId` and still
  defaults `dcgVerdict` to `unknown`. Do not fold that into this win.

Error discipline (optional): a selector near-miss counted decisions only and missed diagnostics.

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
- **(C) Working profile — NOT claimed for the Jev observer.** Everything in the table above is
  `jev-lab`, a disposable profile. The **harm-rule** (four regexes, no Jev call) was promoted to
  **one** working profile (`codex`); that is a different extension and does not close this
  observer claim. See THE INTEGRATION RUNS ON REAL WORK above.

An earlier version of this section reported *0 observer rows against 1 bridge row*. That was true
when written and is now stale; the zero-row cause was a module with valid syntax whose `pi.on`
registration line was absent — reproduced deliberately and repaired
(`harm-rule-shipped-20260919.md`, `658922f`). **A hook that fails to register is indistinguishable
from a hook that sees nothing.** The loader globs `*.{ts,js}`; the config is an `extensions:` list
in the profile `agent/config.yml`.

Live omp was never taken off the table. There is **no standing ban** on registering into working omp profiles. The fleet invented "STOP-LIVE" / deferred registration as reasons not to work. This row is not an indefinite deferral and not quiet-window gated. The Jev observer registered and wrote rows; **id-join capture did not**. The harm-rule's `codex` promotion is a different extension and does not close claim (B).

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

Session co-presence has now been observed (6 sessions, lab only), so that condition is met. The remaining condition for calling the **Jev observer** working is the **id-level join** (currently 0: no `toolCallId` on observer rows, all verdicts defaulted to `unknown`). That claim **(B) is still open**. Do not fold the harm-rule's `codex` promotion into it. There is no dogfood or observer file under `.omp/hooks/` on this tip. The only pre-hook in this tree is `jev-compact`.

**Where a probabilistic judge belongs.** Only on what regex cannot express. The dcg prior is now on this tip: [`docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md`](demos/upstream-repro/dcg-block-rate-prior-20260919.md) — 49,661 allow / 488 block = **0.97%**.

## Scoreboard

| Surface | State | Claim | Promoted? |
|---|---|---|---|
| harm-rule (four regexes, no Jev call) | observe-only on **`codex`** (one profile); 5+2 row counts **cited, not re-derived** (`6c9c8fc` absent) | five-link chain above; **not** a Jev product promotion | **no** |
| tool_call head-to-head | RULE WINS; ship classifier, drop Jev | rule 12/12 vs Jev 11/12 vs dumb 5/12, both FP 0/40; cost-benefit kill | no |
| tool_call ground-truth corpus | OPEN; 216k decisions, zero API | 3.95% isError on allowed (frozen 4.01%); 40× the 0.1% kill line; join yield 36.8% | no |
| `jev-compact` / `install-jev-compact.sh` | ships; fires in real `/compact` | L3 measurement; does **not** prune | no |
| dogfood / observe-and-log | `jev-lab`: observer **14** decision / **33** diagnostic rows; bridge **13**; **6** sessions co-present | **partial** — session co-presence MET, id-join **0** (no `toolCallId`, all `dcgVerdict` defaulted `unknown`); lab only. Claim **(B) STILL OPEN** | no |
| STATUS ledger (`docs/demos/STATUS.tsv`) | 0 `PROMOTED` rows | rulings, not products | **0** |

Further receipts: `docs/demos/omp-seam-live-20260918.md`, `docs/demos/omp-seam-fqo-20260919.md`, `docs/demos/upstream-repro/dogfood-logger-20260919.md`, `docs/demos/upstream-repro/omp-jev-observer-20260919.md` (offline-only; do not read as live-working), `docs/demos/upstream-repro/toolcall-headtohead-20260919.md`, `docs/demos/upstream-repro/harm-rule-shipped-20260919.md`, `docs/demos/STATUS.tsv`, `NEGATIVE_EVIDENCE.md` R21 / R31. Conformance and promoted receipts are cited by local path; those SHAs are **absent from this checkout and from GitHub**.
