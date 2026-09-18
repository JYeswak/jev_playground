# Duel 1 — merged-implementation rulings, duelist B (muse)

Four ideas converged across lineages; the backlog needs implementations,
not winners. For each pair I rule per dimension — scope, mechanism, RED
arms, install, failure mode — naming which file's version survives and why,
with my bias declared per pair (I authored the MU side of all four).
"Neither" was considered every time; the honest result is that no pair
needs a fifth implementation — the unions are coherent. (The duel's actual
fifth implementation already exists: B1 sanitize-before-send, which is
neither file's version but MU-2's ashes plus CC-5's scope. It is referenced,
not re-ruled.)

---

## Pair 1 — routing backtest (MU-1 ≡ CC-3): union, MU installs, CC arms lead

**Bias:** authored MU-1. Ruling splits against and for authorship as noted.

- **Scope:** merged. CC-3's session glob (`~/.omp/profiles/<p>/agent/
  sessions/*.jsonl`) with MU-1's framing (backtest-first gate: backlog #9
  ships iff savings show on OUR turns). CC-3's live-confirm arm dies here —
  re-validating recorded answers against a moved `jev-latest` is the
  golden-regeneration reflex (my reply concession); the live lane instead
  records model version per receipt and prices drift, never re-certifies
  fixtures.
- **Mechanism:** recorded real answers primary (CC-3 — real distributions
  beat canned ones), canned minimal asker retained solely for hermetic CI.
  Threshold policy ours; "served model" demoted to baseline (conceded).
  Price table carries `as_of` + re-derivation path (CC's hit, adopted).
- **RED arms:** union — MU's frontier-needed trigger, empty-transcript
  ERROR, missing-price-model ERROR; CC's all-hard≈0, all-trivial≈max,
  UNPARSED-denominator, determinism-across-runs; plus pane 2's negative
  control (down-route with absent price must not count as savings). No
  cuts: MU's arms test policy-correctness, CC's test estimator-honesty.
- **Install:** MU's survives (TS `npm run backtest` — the transcript
  adapter it reads is TS, so TS minimizes impedance), CC's `uvx`/`npx`
  fork dies for the same ambiguity COD killed in my MU-4.
- **Failure mode:** carries both files' named risks — status-quo bias via
  the baseline (MU), silent dollar-rot via stale prices (CC).

## Pair 2 — admission screen (MU-2 ≡ CC-5): CC-5's scope, MU-2's rigor

**Bias:** authored MU-2, the flawed half. This ruling goes against
authorship on scope — necessarily, since my scope shipped a leak.

- **Scope:** CC-5's injection-only + shadow-then-enforce, in full. The
  credential question is deleted (duel-settled law), reborn only as B1's
  local prefilter with its own receipt. MU-2's universal read/fetch/paste
  coverage survives inside that scope.
- **Mechanism:** Jev injection Noul over inbound bytes behind a local
  secret-pattern scan that runs FIRST on every screened result: on hit,
  redact-and-log, Jev sees surrogate-or-nothing, receipt records which
  bytes Jev saw (pane 2's receipt requirement, adopted). This is my
  reactions' CC-5 prefilter line, now load-bearing in the merged spec.
- **RED arms:** union — CC's blind held-out slice, both-directions trigger
  (flag injection AND classify real page), FP-rate report; MU's silent-
  healthy, empty-scan ERROR, undiscoverable-hook-dir install check. The
  blind arm is the only genuinely external one in the duel; it anchors.
- **Install:** MU-2's rigor (idempotent, refuses on undiscoverable dir —
  the `.omp/hooks/`-without-`pre/` silent miss) around CC-5's hook + CLI.
  CC-5 lacked the install check; MU-2 lacked the scope discipline. Each
  file supplies what the other missed.
- **Failure mode:** the MU-2 leak (named, with the production-vs-tests
  boundary), per-read cost unmeasured until shadow (CC's sequencing
  note stands), FP-nag route-around (silent-healthy-path rule is the
  guard).

## Pair 3 — claim-checker (MU-4 ≡ CC-2): CC-2 first, MU-4 second — one demo, two phases

**Bias:** authored MU-4. Ruling ships the rival scope first; reasoning below.

- **Scope:** one demo, phased. Phase 1 = CC-2's pre-commit lane (narrowest
  contract in the duel: message + cited artifacts, mechanism installed
  twice). Phase 2 = MU-4's working-file scope (explicit claim blocks only)
  unlocks after Phase 1's FP-rate EVAL row clears a pre-registered bar.
  Two scopes, one core, ordered by blast radius — not two demos.
- **Mechanism:** shared core both files described identically
  (extract triples → load artifacts → Jev verify → refuse/silent/skip).
  MU-4 contributes withhold-never-approve (CC already ruled it the better
  specification); CC-2 contributes `CLAIM_CHECK_SKIPPED` on API outage.
  Extraction v1 = explicit blocks + structured citations (both files now
  agree; arbitrary prose stays refused).
- **RED arms:** union — 7-vs-8 refuse naming both numbers, missing artifact,
  span-mismatch (CC's addition, adopted), empty evidence, unlabeled
  citation, skip path. Seven arms is a lot; every one maps to a distinct
  failure observed in-lane this month.
- **Install:** CC-2's `githooks/` + `core.hooksPath` path (no new
  mechanism); single canonical runtime, killing my `uvx`/`npx` fork.
- **Failure mode:** FP-blocked commits (mitigated by skip path + FP-rate
  row) and scope creep into a document system (capped: explicit blocks
  only, Phase 2 gated on Phase 1 numbers).

## Pair 4 — signals starter (MU-5 ≡ CC-4): CC-4's template, MU-5's refusal doctrine

**Bias:** authored MU-5. Ruling takes the rival's install and thesis arm,
keeps my refusal gate and offline completeness.

- **Scope:** CC-4's bring-a-CSV template. MU-5's synthetic-offline loop
  survives as the template's day-zero proof (renders + runs with zero
  edits), and the N≥50-gated local resume application stays a documented
  retry condition, not a feature.
- **Mechanism:** K-signal Nouls + tiny LR + calibration report + fixed-rule
  floor. Fit implementation named here since neither file did: `uv` +
  `scikit-learn` (lane toolchain allows it; hand-rolled IRLS would be a
  numeric footgun wearing determinism as a costume).
- **RED arms:** union — CC-4's self-falsifying thesis arm (verdict must
  lose or refuse to report), my fit-refusal WITH the conceded fixes (fixed
  seed, pre-registered threshold, small-sample refusal), min-rows ERROR,
  ECE gate, empty corpus. License citations in README (CC's criterion,
  kept — attribution is not optional).
- **Install:** CC-4's `uvx jev-signals init`; my ambiguous fork dies.
- **Failure mode:** verdict-baseline-wins (thesis dead → refuse, the arm
  that makes this template honest), premature local fitting (N≥50 gate),
  shift collapse between fit and field (flip-rate reporting is the tripwire).

---

## NO-CLAIM

Paper merges. No union implemented, no arm run, no conflict with either
file's frozen scored text — where a merge contradicts a scored version
(Pair 2 scope, Pair 3 phasing), the scored versions stand as history and
these rulings stand as the plan.
