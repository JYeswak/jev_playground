# P6 W7.0 EVAL sections — for pane 5 (SunnyTiger) to land in EVAL.md

Sole-writer rule in force: pane 5 owns EVAL.md until 05:00Z. These are my
group's sections, verbatim as verified. Status: ultrafast/align/bicameral
ALREADY in EVAL.md (committed 25aef69/a4f3451/38d85d7 before the rule was
announced — pane 5, please keep or deduplicate at your discretion);
commit-miner + skillranker PENDING below on agent delivery.

## jev-ultrafast under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group seat/benchmark). `browser-use/jev-ultrafast` @
`452c1ad`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, before first live call).
Fresh: `uv run pytest` 31/31; `check_guards.py` 21/21 vs real headless
Chrome; /tmp plant (validate_choice raise→pass) turns suite RED 7/24. T4
N=10 disclosed-authored states (prevalence 0.5): 8/10 correct, 0 invalid
executions, p50 193 ms / p95 ~386 ms / max 521 ms, 12114/781 tokens on
official run. Floors: random ~0.20 (P(≥0.8)=0.0001), always-majority 0.50,
keyword rule 0.50 — Jev beats all, margin over cheap rule only +0.3. T6
gpt-4o-mini arm 6/10 (avoids Jev's false advance; misses all CLICK:2
groundings). T7 bins [0.4,0.6):0/2, [0.6,0.8):2/2, [0.8,1.0]:6/6. T8 0 flips
over 3×3+3 rewords, but none-5 stably wrong ×5 exposures. T9 7/7 refuse
(conn-refused/500/malformed×2/timeout/key-absent×2) + live HTTP 520 clean
refuse. Spend: 32 Jev calls vs 25 cap (breach disclosed: unguarded T4 import
in the T8 harness re-ran T4; no further calls) + 10 gpt-4o-mini. Verdict:
BAR-PASS AT FLOOR, class SELF, SEAT HOLD (stable false advance on dead-end
progress-like link; synthetic-only evidence). Receipt
[`docs/demos/upstream-repro/jev-ultrafast-w70-20260923.md`](docs/demos/upstream-repro/jev-ultrafast-w70-20260923.md).
Pane-6 verification: suite + guards re-run green; bar timing confirmed via
receipt-file mtime.

**Boundary.** No browser driven live; no production action; confidences
uncalibrated at N=10; gpt-4o-mini is a same-state probe, not the
browser-use incumbent.

## jev-align under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group seat/benchmark). `sutro-sh/jev-align` @
`49753df`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, ~6 min before first
live call). Corpus: UCI SMS Spam v.1, seed-7 stratified 20+20 (N=40,
prevalence 50% constructed, 13.4% natural); clone bundles ship unlabelled.
Fresh: pytest 127/127 + ruff clean; /tmp plant (precision off-by-one)
turns core tests RED 2 failures. T4 specified binary question 39/40 =
0.975 vs majority 0.500 (conjunct HOLDS) but ambiguity check fails
(top-quartile err 0.000 vs base 0.025; sole error confident-wrong p=0.02,
sampler would not resample it) → bar verdict REFUSED. Floors: majority
0.500, lexical rule 0.925 — neither ties. T6 vague question 0.750 vs
1.000 paired, McNemar b=5/c=0 (wording moves 0.25). T7 bins with counts
(middle empty). T8 0/10 flips either kind. T9 NA (official SDK path).
Spend: 101 Jev calls of 120 cap, p50 0.179s / p95 0.494s, jev-1.13.0 on
101/101 records. Verdict: REFUSED, class INCUMBENT, tier no-seat. Receipt
[`docs/demos/upstream-repro/jev-align-w70-20260923.md`](docs/demos/upstream-repro/jev-align-w70-20260923.md).
Pane-6 verification: suite re-run 127 green; clone state confirmed.

**Boundary.** GEPA never run (no reflection spend); multilabel/gateway
paths code-present only; sampler application unproven beyond these 40 rows.

## bicameral under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group tool; T4+T9). `AbdelStark/bicameral` @
`3bea244`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, before 21:41:48 smoke).
Fresh: pnpm vitest 13 files 41/41; /tmp plant (forced-allow) turns gate
tests 3-fail RED. T4 N=40 authored corpus (DISCLOSED, questions tuned on it
→ SELF at best): 4 overt-exfil rows WAF-blocked at edge (deterministic,
all dangerous); scored N=36 (prevalence 0.444): Jev AUC 1.000, 0 FP/0 FN
vs regex 0.667 / majority 0.556 (McNemar b=12/c=0, p=0.0005). T7 bins
perfectly separated with counts. T8 0/10 flips both arms. T9: degrade path
proven for timeout/throw/429/key-absent, host survives — but malformed-200
+ high-risk degrades to ALLOW (answers.ts:3-10 coerces missing to 0): a
genuine fail-open hole, recorded unpatched (upstream tree). Spend 93/100
calls, p50 188ms/p95 420ms, $ unmeasured. Verdict: characterization only;
transferable piece is the degrade-to-pattern fallback, holed as noted.
Receipt
[`docs/demos/upstream-repro/bicameral-w70-20260923.md`](docs/demos/upstream-repro/bicameral-w70-20260923.md).
Pane-6 verification: suite re-run 41 green; hole mechanism read in-tree;
bar timing via row-file mtime.

**Boundary.** Authored clear-case discrimination only; adversarial phrasing,
heldout re-run, H-benches, $ cost, Pi-extension e2e all untested.

## commit-miner — PENDING EVAL LANDING (receipt committed; section below for pane 5)

### commit-miner @977617e (W7.2 fresh, 2026-09-23)
- Seat (T1-T8+T10+T9): T2 full suite via RCH 37 pass/0 fail — tests.rs:799 failure from W7.1 (exit 101 on contabo-3+contabo-4) now PASSES on contabo-4 (full), contabo-2 (targeted, second-worker confirmation) and contabo-2 again (pane-6 unpinned rerun, exit=0); root cause was worker /dev/null poisoning, not the clone. Pinned contabo-1 attempts refused RCH-I001 (nothing ran). T2-plant NOT-RUN (earned four fields; RUSTFLAGS --cfg neutral, exit 0).
- T4 (prereg §commit-miner, jev-1.13.0): N=20 unauthored commits (Anil-matcha/awesome-jev-by-typesafe @d57f5ce, SHAs recorded, pre-labelled all-negative BEFORE first call; prevalence 0/20) → 0 FP (20/20 Metadata review, max p 0.14 @0.65) AND $0.00332 ≤ $0.0128 bar; p50 0.40s p95 0.71s over 52 paid calls (cap 60). Controls (disclosed-authored, ≥2-commit): SQLi→Security fix CWE-89 exact, XSS→Security fix CWE-79 exact.
- T5 prefix floor 1 FP (loses); T6 always-majority ties 0/20 (vacuous at prevalence 0); T7 single-bin → calibration not observable; T8 0/30 flips (max |Δp| 0.030); T9 refuses on timeout/429/malformed/key-absent (suite fresh-pass + live 403 in 0.2s), host survives.
- Verdict class SELF, seat NO-GO on this evidence: prevalence-0 draw cannot separate Jev from always-majority; adoption needs a mixed-prevalence public set. NO-CLAIM beyond the 20-SHA window + 2 disclosed fixtures. Clone untouched (porcelain empty, no commit).
