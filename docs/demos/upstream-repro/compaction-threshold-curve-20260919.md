# Threshold calibration: keep-probs don't discriminate retention-need, so no threshold spends better

Pane 3 (muse), 2026-09-19, Python arm (zero shared lineage with pane 1's JS arm).
Oracle: `jev-latest` -> `jev-1.13.0`. Harness: `work/p3-calibration/` (sample.py,
fetch_probs.py, sweep.py, probs.jsonl committed; cand-*.jsonl uncommitted —
regenerable via sample.py, bulk transcript text stays out of the tree).

## Design (and its disclosed deviation)

Per sampled call, the library's two noul questions verbatim
(`fast-jev-compaction/src/compact.ts:56-67`), keep rule `p >= t`, result-only
retention (call text out of scope; result bytes dominate). State per call is
CALL-LOCAL (task = preceding user text, tool + input + truncated result) — NOT
the library's 25k-token transcript window. One request per call (150 requests,
no cross-talk), plus 6 pilot + 30 small-batch + 1 failed = 187 total this pass.

Corpus (n per session): grokbot/muse 50, franken-harvest/codex 50,
omp-orchestrator/claude 50. Uniform timeline sample, seeds 1/2/3.

Needed-later oracle (PROXY, not ground truth): novel tokens (lowercase alnum,
len>=5) in the result, absent from earlier assistant text, reappearing in later
assistant text. Lax by construction: base rate 111/150 = 74%.

## The curve

```
t kept dropped mistakes mist_rate bytes_saved mist_per_10KB
0.0  150    0    0 0.000         0 0.000
0.1  150    0    0 0.000         0 0.000
0.2  149    1    1 1.000     20438 0.501
0.3  122   28   22 0.786    128954 1.747
0.4   51   99   73 0.737    388159 1.926
0.5    3  147  108 0.735    584763 1.891
0.6+   ~0  ~150 ~110 0.74   ~585k  ~1.93
```

Per session at t=0.5: grokbot 50 dropped/32 mistakes, harvest 49/39, orch 48/37.

## Findings

1. **The score carries no signal about the oracle.** Mean keep_p | needed = 0.361
   vs unneeded = 0.369 — identical. Mistake rate per dropped item is ~0.74 FLAT
   across t=0.3..1.0, and mistakes-per-10KB is flat 1.7–2.1. Threshold tuning
   cannot work here: every cut is the same fixed exchange rate.
2. **Flatness (as ordered): the efficiency curve is flat.** Mistakes-vs-bytes is
   monotone (more drops = more of both), but no threshold spends better per byte.
   There is no knee, no operating point on efficiency grounds.
3. **Planted extremes behave:** t=0.0 keeps everything (0 mistakes, 0 saved —
   degenerate pass); t=1.0 drops everything (111 mistakes — oracle catches it).
4. **P3-2 verdict: nothing beats keep-everything on mistakes.** Keep-all has 0
   mistakes; every dropping threshold has >0. On mistakes-per-byte keep-all is
   0/0 (undefined) — plainly: dropping buys bytes at a fixed ~1.9 mistakes/10KB
   with no threshold that spends better. If a byte budget forces drops, say which
   budget; the threshold is then arithmetic, not calibration.
5. **State caveat (bounds the claim):** call-local states systematically undervalue
   results (only 3/150 >= 0.5; calls spread 0.29–0.84 with 133/150 kept). The
   library's transcript-window states kept 8/13 live. The non-discrimination
   finding is about THESE judgments; full-state probs might discriminate — that
   is pane 1's JS arm to confirm or refute, running the same sweep against
   library-built states.

NO-CLAIM: the oracle is a token proxy for "needed", not ground truth (74% base
rate proves its laxity); bytes≈chars; n=150 across 3 sessions, one model, one day.

## Convergence with the JS arm (2c330e9, read after writing)

The sibling arm (native JS SDK, library-built states, n=96×3, oracle with planted
negatives: noise→0/200, end-of-transcript→0/200, real→~90%) lands the same
verdict from the strong side: Jev@0.5 drops 98-99% (≈ drop-everything,
indistinguishable from random/recency), keep-everything wins 7-23x. This arm
agrees at every comparable point (my t=0.5 dropped 147/150 = 98%; keep-all has 0
mistakes here by construction). Two differences bound the claims: (1) their
oracle is control-validated, mine is not — my 74% base rate vs their ~90% is a
threshold-definition gap (len>=5/hit>=1 vs their linear first/last-occurrence
rule), and my non-discrimination result (0.361 vs 0.369) is robust to that gap
but should be re-run under their oracle; (2) their states are library-faithful
(transcript window), mine call-local — the fact that BOTH produce drop-rates
near 98% suggests the threshold is wrong in more than one state regime, but only
their arm proves it where the product actually runs. Joint reading: do not run
this compactor on omp sessions; threshold tuning is futile in both regimes.
