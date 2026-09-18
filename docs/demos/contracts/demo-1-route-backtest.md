# Demo-1 contract — `jev-route-backtest` (SHIPPED, written from measured reality)

Mean 853.8 (4 graders, range 830–875). Source: `PLAN.md` §5.1. Status:
**shipped** — so this contract records what was measured, not what was
intended, including the finding that killed its own follow-on. An
implementer executing from it never opens `PLAN.md`. (Template note: his
beads embed plan sentences verbatim at 98.9% with 5.35 beads per sentence.
This contract follows that shape: every normative sentence here is written
to be copied word for word into the implementation beads, redundantly, not
partitioned.)

## Goal and ownership

Deliver a read-only replay harness that prices a routing counterfactual
over our own omp session logs: point it at recorded transcripts, and it
reports what per-turn routing *would* have spent versus what was actually
spent, with a per-turn decision log for calibration. In product terms: the
evidence gate for live rerouting — backlog item "model router" ships if
and only if this backtest shows savings on OUR turns, because upstream's
−60% was measured on *their* 237 turns and is not transferable by faith.

Explicit file ownership:
- `demos/routing-backtest/` — the demo tree: reader, pricer, decision
  log, install script, test suite. Pane 2 built the reader and pricer
  and owns `demos/routing-backtest/**` outside `fixtures/`.
- `demos/routing-backtest/fixtures/` — the fixture corpus (pane 3):
  real excerpt, known-bad fixtures, manifest with bytes+sha256, per-file
  READMEs, `verify-fixtures.mjs`.
- `demos/routing-backtest/runs/route-backtest-<ISO8601>.json` — receipts.

Explicit non-goals:
- **Not a live router.** Read-only; it never routes anything. Whether a
  router is ever built depends on what the backtest measures — and it
  measured 0.047% (below), so the live router is **not queued**. A demo
  which prevents a build is worth more than one that enables one; that
  prevention is this demo's actual product. Do not re-litigate it here.
- **No adaptive thresholds, no dashboard, no online routing.** The union
  ruling capped scope at replay-only; each addition re-opens the merge.
- **No verdict string.** R11: the A/B harness emitted `"B wins"` from n=1
  and the string propagated into 17 files. This demo reports numbers
  with denominators. Any `verdict` field in a receipt is a defect.

Pane ownership: contract authored pane 3 (muse). Reader/pricer built
pane 2; fixtures pane 3. Stage explicit paths only.

## Product context and guardrails

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Offline lane first. Live calls are budgeted and stated in the receipt.
> The API key lives only in the environment as `TYPESAFE_API_KEY` and its value is never recorded
> in any artifact — names are expected, values are not.
>
> **Evidence rules.** A claim with no re-derivation path is not evidence. An empty scan set is an
> ERROR, never a pass. A one-item scan set is not a demonstration. A timeout is not a verdict.
> Exit code must agree with verdict text. These are implementation requirements, **not statements
> that any code or gate has passed.**
>
> **Shared worktree.** Three agents share this checkout and all commit as the same git identity,
> so `%an` cannot attribute a commit. Stage explicit paths, own files only, never `git add -A`,
> never amend, never rewrite shared history. Preserve peer changes: if a file you need belongs to
> another lane, message its owner with the exact replacement text rather than editing it.
>
> **Blocker protocol.** If a prerequisite is unavailable, report the exact blocker with the command
> and its verbatim output. Never substitute a stub for evidence, never weaken an adversarial
> assertion, and never let a missing capability be reported as passing check.

## Embedded contract

Measured reality (the ship record; every number re-derivable from a
committed receipt):
- Reader over real omp logs: **2 sessions, 1910 + 1183 rows, 30 turns,
  30 classifiable, 0 skipped**, models `gpt-5.6-luna` and
  `muse-spark-1.3-contributor`. A turn is **one `turn_start`→`turn_end`
  marker pair** — defined once, in the reader (`TURN_DEFINITION`),
  after three artifacts asserted three counts (94 rows / 18
  model-bearing rows / manifest "turns 1-6" / reader 1). Three
  artifacts asserting three counts is a missing shared definition, not
  three bugs; the fixture now yields 6/6 under the marker-pair rule.
- Counterfactual, ledgered prices: actual **$7.230350988** vs
  counterfactual **$7.226928188** → savings **$0.0034228 = 0.047%**.
  Upstream measured **−60%** on their turns
  (`jev-codex-router@8292b51`); on ours it is 0.047%. The served model
  is a **baseline, not an oracle** — it is the incumbent policy's
  choice, so agreement-with-served measures status-quo bias, not
  correctness. The price table carries a dated `as_of`; dollar figures
  without one rot silently (pinned-fact stale-risk, measured in our
  own doc review).
- Clean-clone verification, the bar every demo inherits: `git clone` →
  `install.sh` → **10 pass / 0 fail / exit 0**, then the documented
  fixture command → 1 session / 6 turns / 6 classifiable / 0 skipped
  with 5 cheap candidates named. A stranger reproduces this from a
  clean clone or the demo is not shipped.

Mechanism, stage by stage:
1. **Read.** Parse omp session JSONL: session/agent header rows pass
   through for context; `turn_start`→`turn_end` marker pairs delimit
   turns; markerless logs fall back to one user prompt plus following
   assistant/tool rows (the reader's `TURN_DEFINITION` names both
   cases — the fallback exists, is tested, and is counted separately
   in the receipt so markerless traffic never inflates the marker
   denominator). A turn is classifiable iff it carries a served
   assistant model id.
2. **Ask (policy, ours).** Per classifiable turn, one Jev Choice (pinned
   model, recorded version): route to frontier or to the cheap tier,
   with the threshold in our policy file — never upstream's. Canned
   asker with recorded real answers for the offline lane (hermetic CI);
   live lane re-asks and records the model version per receipt, and
   **never re-certifies fixtures**: a moved `jev-latest` that changes
   recorded answers is drift to price, not a fixture failure
   (golden-regeneration reflex, refused by design).
3. **Price.** Join each decision against the committed per-model price
   table (`prices.json` with `as_of` date): actual spend from the
   served model, counterfactual from the decision. A turn naming a
   model absent from the table ⇒ ERROR, never a `$0` row (a missing
   price presented as savings is the failure the table exists to
   prevent). Down-routes under absent prices are not counted, period
   (pane 2's negative control, adopted).
4. **Report.** Per-turn decision log (turn id, served model, decision,
   both prices) for human spot-checks plus aggregates: turns N,
   routed-down k, saved $, latency p50–p99, model versions, threshold,
   price-table `as_of`. No verdict string anywhere in the output.

Cost and budget, in provider units: the backtest itself spends one Jev
request per classifiable turn when live (input-sized, output free);
the committed numbers above came from recorded answers ($0 marginal).
Every live run states calls, model version, and wall time. The fixture
command (1 session / 6 turns) is the $0 smoke any pane runs first.

API contract if Jev is called: endpoint
`POST https://api.typesafe.ai/v1/systemone`, Bearer `TYPESAFE_API_KEY`
from environment only, model pinned with version recorded per receipt;
one Choice per turn as worded in the policy file; malformed answers
⇒ turn counted `asker_malformed`, excluded from both savings legs
(never assigned to the cheaper one — that would manufacture savings).

## Focused verification

Third-party commands (demo tree):
- `./install.sh` from a clean clone, then the suite: **10 pass /
  0 fail / exit 0** (the shipped bar, re-run don't trust).
- Documented fixture command → `1 session / 6 turns / 6 classifiable /
  0 skipped`, 5 cheap candidates named in the receipt.
- `node --test test/` — reader, pricer, decision-log, and RED arms
  below against the committed fixtures.

RED arms (all passing at ship; each names its plant):
- **Empty classifiable set ⇒ `ERROR EMPTY_CLASSIFIABLE_SET`.**
  `fixtures/zero-classifiable-turns.jsonl` (3 spans, zero served-model
  rows, verified 0 by `verify-fixtures.mjs`) must exit nonzero with
  the error naming the fixture — never "saved $0.00". (Integration
  note: the reader first proved this arm with an in-memory string;
  the committed file now exists and is verified on disk. The next
  reader change consumes the file — an arm proved on a string the
  repo also holds as a file is proved twice, billed once.)
- **Model absent from price table ⇒ ERROR.** Fixture with all 18
  model fields rewritten to `frontier-unlisted-9x` (differs from the
  real excerpt ONLY in those fields, proven byte-wise) must exit
  nonzero — never a `$0` row, never counted savings.
- **Classifiable count below floor ⇒ WARN then ERROR.** A run whose
  classifiable turns fall below the policy floor must not emit a
  receipt that reads like a successful backtest: warn naming the
  floor, and ERROR if zero. The receipt carries the denominator
  (turns, classifiable, skipped with reasons) so "n=1 success" is
  structurally unstatable.
- **Manifest integrity.** `verify-fixtures.mjs` recomputes bytes +
  sha256 per fixture file against `manifest.json`; any drift fails.
  Two runs on different corpora are two experiments (R11) — the
  manifest is what makes that checkable.

Denominator per run: sessions, rows, turns, classifiable, skipped
(with reasons: unparseable, model-less, below-floor), wall time. Exit
code agrees with verdict text. Who verifies: a non-author pane; the
fixture corpus (pane 3) and the reader (pane 2) were built by
different panes precisely so neither grades its own input.

## Evidence and logging

- Receipt path: `demos/routing-backtest/runs/route-backtest-<ISO8601>.json`.
  Schema: `inputs` (transcript shas, price table `as_of`, model
  version, threshold, policy version), `turns` (per-turn: served
  model, decision, actual $, counterfactual $), `aggregates` (N, k,
  saved $, latency p50/p99), `denominator` (counts above),
  `failures: []` (verbatim errors). No `verdict` field — by design,
  permanently.
- Commit subject level: `[test]` (suite green, recorded answers);
  `[live]` only with calls, model version, latency, budget. Never
  bare "verified".
- Boundary for `EVAL.md`: replays recorded traffic against ledgered
  prices. Does not prove live-routing savings (unbuilt, unqueued),
  does not validate the price table (dated, re-derive), does not
  cover traffic shapes absent from the corpus (markerless logs get
  the fallback path and its separate count).
- Never retro-edit a receipt. Supersede by re-running.
- No secret values, no operator home paths, no machine names. Fixture
  scrub verified zero hits (`thinkingSignature`, `/Users/`, `/home/`).

## Open risks with concrete resolution

- **Price-table rot.** Dollars date faster than code. Resolution: the
  `as_of` field plus a quarterly re-derivation bead —
  `npm run prices:check` diffs table entries against provider pages
  and opens the bead on any move; receipts pin the table sha so a
  stale table is detectable, not silent.
- **Corpus narrowness.** Two sessions, one lane's traffic. Resolution:
  the receipt's Boundary names the corpus; each new session type
  appended re-runs the full suite plus a fresh spot-check of ten
  decisions (`npm run spotcheck -- --n 10`), recorded in the run's
  receipt, before its turns join any savings claim.
- **Agreement-with-served misread as accuracy.** Resolution: the
  receipt labels the column `served_model_baseline` (never oracle),
  and any downstream consumer quoting "agreement" without the
  status-quo-bias caveat fails review — the caveat is in the schema
  (`baseline_caveat` string, required), not in tribal memory.
