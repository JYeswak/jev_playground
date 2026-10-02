# BREADTH — Rules / Guardrails / Review (OrangeFrog, 2026-10-02)

Lineage: V10 (bash-pipe-exit applicability Choice, feasibility GO, prereg posted, bead
jev-dr4p). Prior art in this lane tested ONE design per vein (single Noul/Choice at a cut).
Sources read: `docs-mirror/typesafe/cookbooks/{llm_guardrails,consistency_choice_cookbook,
consistency_noul_cookbook,sde_cascade,citation_check,hierarchical_classification,
rerank_typesafe}.md`, `docs-mirror/typesafe/patterns/{composite-scoring,confidence-routing,
fan-out}.md`, `awesome-jev/README.md` community index (jev-secret-detection, commit-miner,
Jev Review, Jev Logs, pi-warden, Bicameral). No community code cloned; mechanisms below are
our experiments, not ports.

Shared label assets (keyless, frozen): 5,903 ttsr_injection rows (4,895 active-rule / 48
rules); V10 held-out 118 blind-labeled bash-pipe-exit rows (19 clear / 43 printonly-borderline
/ 56 inapplicable); 223 honesty-gate pipe-exit blindings (positive mine, unharvested).

## D1. Applicability battery + policy routing (guardrails pattern on TTSR)
- Decision: fire / suppress / (review) for an already-triggered rule.
- State: trigger command + next agent action (same as V10).
- Questions (one request): Nouls {pattern-present, hazard-real, already-correct}
  + Score {interruption-worthiness}. Code-owned thresholds per rule (strict/permissive policies).
- Action: suppress only when all Nouls low and score low; review band routes to log, never blocks.
- Labels: V10 blind applicability (118 rows exist).
- Baseline: V10 single-Choice + deterministic regex (62 interruptions, 0 clear-misses).
- Why beat: decomposes "already correct" (PIPESTATUS/pipefail, which fooled V1-Choice raw
  0.648) from "hazard real"; thresholds tunable per rule without re-asking.

## D2. Screen cascade (SDE cascade: cheap -> verify -> reasoning)
- Decision: which tier handles this firing (regex / Jev-battery / human log).
- State: tier 1 sees trigger text only; tier 2 sees full event + action.
- Questions: tier-1 Noul (certainly-inapplicable?) at high cut; tier-2 D1 battery on survivors.
- Action: suppress at tier 1 only above 0.9; else escalate; never block.
- Labels: tier-1 precision on V10 118 + cost/call accounting.
- Baseline: Jev-on-everything.
- Why beat: same safety as D1 at a fraction of spend (most firings die at tier 1); spend is
  the binding constraint at 1,447 injections/7d.

## D3. Composite rule score (composite-scoring pattern)
- Decision: suppress iff weighted atomic scores < cut.
- State: trigger + the rule's own past precision (from census) + event.
- Questions: Scores {pattern-strength, hazard-severity, usage-correctness, print-only-likelihood}.
- Action: weights in code, per rule; auditable arithmetic.
- Labels: V10 118 (fit weights on dev sessions only, test on held-out).
- Baseline: single Choice.
- Why beat: calibrated per-rule weights; a print-only discount weight directly targets the 32
  printonly rows the regex keeps.

## D4. Rank-then-verify over co-firing rules (rerank pattern)
- Decision: when >1 rule fires on one event, inject at most one.
- State: event + candidate rule texts.
- Questions: Choice top-1 most-applicable + Noul verify ("does the winner address this event?").
- Action: inject winner only iff verify passes; else suppress all.
- Labels: blind most-applicable on multi-rule rows (need count first).
- Baseline: inject-all (current).
- Why beat: kills stacked interruptions; verify step bounds the harm of picking wrong.

## D5. Commit-diff policy classifier (commit-miner pattern)
- Decision: route commit to pass / review / block lanes.
- State: diff + message.
- Questions: Choice {bugfix, feature, security, chore} + Nouls {evidence-present, tests-touched,
  claim-matches-diff}.
- Action: risky (security/unverified-claim) -> review; rest pass.
- Labels: revert history + gate verdicts + verifier overturns.
- Baseline: pre-commit grep gates.
- Why beat: semantic policy (e.g. "done without evidence") that regex cannot state.

## D6. Secret-span verdicts (secret-detection pattern)
- Decision: flag / ignore a secret-shaped span in a diff.
- State: span + entropy + path + surrounding lines.
- Questions: Nouls {secret-shaped, test/fake, already-redacted}, pinned low-temp for repeatability.
- Action: flag only on shaped & real & unredacted.
- Labels: planted secrets + our fake-key fixtures + FP corpus from secret-scan gate logs.
- Baseline: rg regex shapes.
- Why beat (narrow): regex already near-perfect on recall; the bar must be FP-rate at equal
  recall, and the honest prior is BASELINE WINS until a paired FP difference is measured.

## D7. Gate-verdict consistency (consistency cookbooks)
- Decision: final gate verdict on borderline claim checks.
- State: claim + cited evidence.
- Questions: N parallel Choice/Noul repeats; agreement decides, disagreement routes to human
  with raw values published.
- Action: review-band, never auto-fail.
- Labels: verifier overturns of gate verdicts.
- Baseline: single call.
- Why beat: measured overturn-rate drop; uncertainty made visible instead of averaged away.

## D8. Hierarchical rule routing (hierarchical classification + beam)
- Decision: which rule family (then leaf rule) owns this event, if any.
- State: event (command + tool + cwd).
- Questions: Choice over families {shell, python, git, beads, ...} -> beam top-2 -> leaf Nouls
  only within survivors.
- Action: run only surviving leaves' checks; applicability built in.
- Labels: which rule (if any) applied, from V10-style blind review across rules.
- Baseline: all-36-regex scan every event.
- Why beat: sublinear cost as rules grow; inapplicable families never evaluated.

## D9. Pre-trigger scrutiny screen (inversion of V10)
- Decision: does this command need the rule engine at all?
- State: command + cwd (no rule text).
- Questions: Noul "could any rule plausibly apply to this command?"
- Action: skip all rule evaluation when Noul < low cut; else run engine normally.
- Labels: rule-fired-&-applicable (positives) vs clean commands (negatives, abundant).
- Baseline: rules-always-run.
- Why beat: saves 100% of rule cost on clean commands (the majority); harm-bound is explicit
  (missed-hazard rate with rule-of-three bound). High risk, high value.

## D10. Review-then-inject with session dedupe (Jev Review staged + Jev Logs triage)
- Decision: inject this reminder now, or suppress as repeat/low-value?
- State: reminder text + event + same-rule firings already injected this session.
- Questions: Noul {correct} + Noul {useful-now} + Score {marginal-value-given-repeats}.
- Action: inject only high-confidence useful; repeats decay by count.
- Labels: same-session repeat chains (keyless countable) + V10 applicability.
- Baseline: inject-all (491 firings of one rule!).
- Why beat: attacks the largest measured waste directly (repeat volume, not correctness);
  even a crude repeat-decay wins before any model judgment.

## Feasibility (keyless, 2026-10-02) and prereg choice

Top 3 probed on frozen assets in `var/agent-tmp/dr4p-feas.34880/`:

- D10 repeat-suppression: 628 same-rule chains, 4,864 repeat-rows = 82% of all 5,903
  injection rows (`d10` counts). Blind labels on 30 repeat pairs (`d10_labels.json`):
  21 new-info / 7 redundant / 2 censored. Verdict MIXED: repeats are mostly DISTINCT
  events, so naive repeat-suppression is UNSAFE; viable redesign is adaptation-gated
  (suppress iff agent saw this reminder and pattern persists). Not preregistered yet.
- D4 rank-then-verify: 297 multi-rule rows (5.0%). Verdict GO (small but adequate);
  queued behind D1.
- D1 applicability battery: 118 V10 blind labels + frozen regex baseline (62 interruptions,
  0 clear-misses) already exist. Verdict GO, most ready.

PREREG D1 (committed here pre-live; live on conductor KEY OK): same 118 held-out rows and
labels as V10 (`held_labels.json`); one request per row with Nouls
{pattern-present, hazard-real, already-correct} + Score {interruption-worthiness}, same
state as V10; fail-safe KEEP on invalid/conf<0.6/error; per-rule strict policy from the
guardrails cookbook. Baselines on identical rows: regex (62/0) + V10-Choice result when run.
PASS iff interruptions <= 57 AND clear-misses = 0 AND interruptions < V10-Choice (paired
McNemar on disagreements). Caps: <=130 calls; spend stated; stop on 401/402/403; key-fetch
failure = NOT_RUN.
