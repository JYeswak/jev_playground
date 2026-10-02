# PREREG — zezf H3/H4 (bead jev-pslq)

Frozen 2026-10-02 before any H3/H4 live call. Live jev-1.13.0 only.
Parent: long-runner Noul-question + cut 0.50 FAIL (rec 0.200 vs 0.40 bar, prec 0.478;
table on same rows prec 0.42 rec 0.18). H2 cue backfired. Conductor order: H3/H4
with positive-only wording and dev-fitted cuts.

## H3 — Noul positive statement + dev-fitted cut

Same state as parent (`{command, cwd}`), one Noul per request. Wording is a
positive assertion (Noul judges truth; no question form, no negation):

> "This shell command runs for longer than 120 seconds, judging by its full
> command text including all arguments, not just the tool name."

Predict LONG iff noul >= cut_h3. Fail-safe (timeout/error/invalid/refused) -> SHORT.

## H4 — Choice bands + dev-fitted probability cut (new primitive)

`askJevChoice`, same state. Positive options only:

- instructions: "How long will this shell command run, judging by its full
  command text including all arguments, not just the tool name."
- classes: { long: "runs for longer than 120 seconds",
              short: "finishes in 120 seconds or less" }

Score = P(long). Predict LONG iff P(long) >= cut_h4. Validator-refused/invalid ->
SHORT (fail-safe direction: foreground).

## Cut fitting (dev, frozen before held)

`var/agent-tmp/zezf/devset.json`: 120 rows, 60 pos / 60 neg, all non-held
(disjoint from held pool; scored before only with parent/H2 wordings, never H3/H4).
Score all 120 per design (240 calls), pick the cut maximizing Youden J
(sens + spec − 1, prevalence-free); tie-break: lowest cut (favors recall, the
parent's miss). Cuts recorded in the receipt before the held phase starts.

## Held evaluation (fresh negatives, disclosed positive reuse)

`work/zezf/sample_h3h4.json`: ALL 55 held positives (the pool holds no more;
shared with the parent sample — recall denominators identical, disclosed) +
245 FRESH held negatives (seed 20261003, old-sample row_ids excluded).
300 calls per design. Same frozen train table + cut 0.01 as parent, applied to
the same rows (paired baseline).

## Bar (per design, fixed pre-call)

PASS iff recall >= 0.40 AND precision >= 0.20 on the 300 fresh-held rows.
Report: paired 2x2 design-vs-table disagreement, Wilson 95% CIs, per-call
model/row-hash/status/tokens/latency/spend, exclusion count, miss analysis by
first-token. FAIL -> NEGATIVE_EVIDENCE with rows; area stays open per LOSS DEPTH.

## Caps and harm limits

<= 240 dev + <= 600 held = <= 840 calls, spend cap $0.025 (~$0.015 expected),
stop on 401/402/403 or cap, 20 s timeout, checkpointed resume by row id.
Note: the zezf 300/vein cap is already breached (540 disclosed); H3/H4 are new
designs with their own budgets above. NO-CLAIM on causality and beyond
session-bash generalization.
Runner: `work/zezf/run_h3h4.mjs --phase dev|held`; receipts
`work/zezf/h3h4dev.jsonl`, `work/zezf/h3h4held.jsonl` (ids, hashes, scores,
preds, status, tokens, latency; no raw text).
