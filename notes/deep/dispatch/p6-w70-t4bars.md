# W7.0 T4 bars — pane 6 group (jev-align, commit-miner, skillranker, bicameral, jev-ultrafast)

Committed BEFORE any live call in this group. Bars are decision criteria, not
numbers to beat: each states the corpus, N, prevalence reporting, metric,
pass/refuse rule, and call cap. Model `jev-1.13.0` pinned everywhere. Every
receipt states N, positive-class prevalence, cost, p50/p95 latency, and a
paired test where comparative. Prior receipts are leads, never passes.
Worker state at prereg time: `/dev/null` is `character special file 666` on
contabo-1/2/3/4 (measured 2026-09-23 via the rch skill command; pane-1 repair
not yet reported, so Rust negative-test verdicts still get second-worker
confirmation per the skill).

## jev-align (seat) — cap 120 Jev calls, GEPA comparison OFF

Corpus: N≥40 labelled rows — the clone's own bundled data if labels exist,
else ONE named public labelled set recorded in the receipt. Never authored.
Metric: multiclass accuracy vs always-majority + ambiguity-error check (error
rate in top-ambiguity quartile ≥2× base rate).
APPLICATION (acquisition-sampler port) proceeds iff Jev beats majority by
≥0.10 AND the ambiguity check holds. GEPA itself is not adopted (ledger);
no reflection-LLM spend without a second prereg.

## commit-miner (seat) — cap 60 Jev calls

Corpus: N≥20 commits with known bug/security labels from a named public repo
history (record repo + SHAs). Bars (both must hold): validity 0 FP on the
set AND cost ≤ $0.0128 per 20 commits (prior rung-4 bar stands).
Verdict class per T10 regardless; cost refuses independently of accuracy.
T2 note: `tests.rs:799` c3/c4 failure re-runs NOW (workers healthy by direct
measure); any negative-test verdict gets a second worker before it counts.

## skillranker (benchmark) — cap 40 Jev calls

Corpus: N=12 labelled skill-fit cases from existing labelled data only
(record source). Arms on the same rows: Jev wide-Choice top-1 (+ loss),
always-abstain floor, BM25-only ranking (Quill prefilter as ranker — the
comparison the ledger says was never measured).
Router-hook application proceeds iff Jev beats BOTH floors by ≥0.10 accuracy
or ≥0.05 mean loss. Suite via RCH (any healthy worker); negative-test
verdicts confirmed on a second worker.

## bicameral (tool; T4+T9) — cap 100 Jev calls

Corpus: N=40 authored cases (DISCLOSED authored → result class SELF at best).
Floor: regex high-risk list (`high-risk.ts`) head-to-head with McNemar on
the same rows. No seat-pass bar: the transferable mechanism is the
degrade-to-pattern fallback, so T4 characterizes failure — report per-class
precision/recall, T8 flip rate, and the exact conditions where regex beats
Jev. T9: timeout/429/malformed/key-absent against its client; must refuse,
host survives.

## jev-ultrafast (seat; T4+T9) — cap 25 Jev calls

Corpus: N=10 states from the existing synthetic set (disclosed authored).
Bars: ≥8/10 correct targets AND 0 invalid executions; random-target floor on
the same states. T6 small-LLM arm (N=10) attempted via infisical-found keys;
only if keys absent may T6 go NOT-RUN with the four earned-label fields.
T9 on its httpx client (timeout/malformed/key-absent must refuse).

## T5/T7/T8 for all five

T5: always-majority (or random-target where ranking) + cheapest lexical rule
on the same rows; a floor tying Jev refuses the seat (class A/B).
T7: reliability bins WITH counts; single-bin tables reported as
"calibration not observable at this N".
T8: N=10 subset asked 3× plus once reworded-state-identical; report flip
rates; >20% flip flagged, no seat on flagged rows.
