# Baseline design — claim-check v0.6.0 versus a Jev claim checker

Status: rung-2 comparison design, not implementation or benchmark result.
Incumbent: `bhumik154/claim-check` v0.6.0, tag SHA
`f3a020b5684f3854352197af5f4fb7d5e506972b`.
Candidate: a Jev-backed numeric-claim checker derived from Demo-3's contract, with deterministic
triple extraction and Noul evidence judgment.
Purpose: baseline and obliterate the incumbent only if the measured delta is large enough to change
a stranger's choice.

## Correction to the incumbent argument

The maintained incumbent is not a reason to skip the experiment. `claim-check` is the strongest
possible control arm because it is pinned, installable, deterministic, offline-capable, and already
trusted by its users. The right question is not “can Jev do something different?” It is:

> On one labelled corpus containing the incumbent's supported test-count claims and a strict set of
> claims it documents as unsupported, does the Jev checker create enough additional correct,
> actionable coverage to justify model cost and latency?

If the answer is no, the honest result is “use claim-check.” If the answer is “use claim-check for
test counts and the Jev checker for the rest,” that is a composition seam and a useful result, not a
failure. The candidate ships only when the delta is operationally material rather than statistically
interesting but negligible.

## What claim-check v0.6.0 provably does

Pinned source:

- Repository: [bhumik154/claim-check](https://github.com/bhumik154/claim-check)
- Release: [v0.6.0](https://github.com/bhumik154/claim-check/releases/tag/v0.6.0)
- Pinned README: [raw README at v0.6.0](https://raw.githubusercontent.com/bhumik154/claim-check/v0.6.0/README.md)
- Tag SHA: `f3a020b5684f3854352197af5f4fb7d5e506972b`
- Release title: “report unverified claims,” published 2026-08-19.

The README states that the tool checks whether the **test count in a commit message is true**,
using pytest, Vitest, or Jest. Documented examples include:

```text
22 passed
22/22 tests pass
all tests pass
```

Its documented commit-msg flow is:

1. Parse a test-count claim in the commit message.
2. Run or reuse the relevant test-run evidence.
3. Compare the claimed count with the runner's observed result.
4. Block the commit when the claim mismatches.
5. Report “could not verify” when no usable whole-suite run exists rather than silently asserting
   support.

The README also documents scope limitations: a run narrowed by `-k`, `-m`, an explicit path, `-x`,
`--lf`, a shard, Vitest `-t`, or Jest `--onlyChanged` cannot confirm a whole-suite claim; a runner
or environment failure can produce a fail-open “could not verify” path; and the tool does not infer
whether a run's scope matches the author's intended claim beyond observable runner signals.

That is a substantial baseline. It is not a straw man and must win its supported subset unless the
measurement says otherwise.

## What it does not document as supported

The candidate corpus must explicitly test the boundary rather than assume it. At v0.6.0's documented
scope, the Jev checker must treat these as out-of-scope for the incumbent, not as incumbent bugs:

1. Non-count numerics such as `latency: 37 ms`, `processed: 10,000 rows`, or `formats: 12`.
2. Percentages and ratios such as `accuracy 94.2%`, `37% faster`, or `nDCG 0.692`.
3. Claims whose evidence is an arbitrary JSON, CSV, log, Markdown, or TypeScript receipt rather than
   a pytest/Vitest/Jest result.
4. Same-number/wrong-denominator claims, such as `7/8` asserted against a receipt containing 7
   passed out of 9 total.
5. Unit mismatch claims, such as `0.47%` versus `0.47` or dollars versus cents.
6. Claims whose cited evidence is prose or a source-span statement rather than test-run output.
7. Claims that were true at revision R but are stale after the cited artifact or repository changes.
8. Multiple numeric triples in one message when the evidence paths are different artifact classes.
9. A true claim with no usable current evidence: the incumbent may report unverified, while the Jev
   candidate must preserve an explicit `unknown`/withhold result.
10. Claims where “all tests pass” depends on the repository's hidden `testpaths`, ignore list, or
    discovery configuration and the output cannot establish the intended scope.

These are the candidate's opportunity classes, not assumed wins. For each class the receipt must
record `incumbent_unsupported` or `incumbent_unverified` based on the actual pinned tool output;
never infer a pass/fail from a missing line.

## Shared corpus

### Source material

The first corpus is built from the existing claim-audit receipt:

- Receipt: `docs/demos/duel-1/runs/claim-audit-20260918T003836Z.json`.
- Schema: `jev.duel.claim-audit.v1`.
- Four source documents.
- Five cited source artifacts.
- 60 labelled claims: **19 EXACT, 4 WRONG, 37 UNVERIFIABLE**.
- Two WRONG rows are residual instances of an already-corrected error, which must remain labelled as
  observed historical claims rather than silently repaired.

The receipt is evidence about the corpus, not a ready-made claim-check input. The comparison harness
must materialize each row into a fixture containing:

```text
cases/<id>/message.txt       # one commit message or claim-bearing message
cases/<id>/evidence/         # cited artifact copies, if present
cases/<id>/manifest.json     # claim, type, unit, citation, expected status, provenance
cases/<id>/runner/           # pytest/Vitest/Jest output where applicable
```

Every fixture receives a case SHA, source receipt path/row, expected semantic status, and a
classification of whether v0.6.0 documents it as supported. Existing artifacts are copied by bytes;
the harness never rewrites the source receipt or quietly corrects a claim.

### Strict-subset rule

The corpus must contain a strict incumbent-supported subset, not two unrelated test sets. Build the
manifest in two stages:

1. **Core historical set:** all 60 claim-audit rows, preserving their original text and expected
   `exact`, `wrong`, or `unverifiable` label.
2. **Runner control set:** a small stratified set of test-count messages and matching
   pytest/Vitest/Jest outputs sufficient to exercise the incumbent's documented path, including
   correct count, wrong count, all-tests phrase, narrowed run, missing run, runner failure, and
   multiple claims.

The manifest must compute, not assume, the subset fields:

```json
{
  "case_id": "claim-017",
  "expected": "supported | contradicted | unknown",
  "claim_class": "test_count | percent | ratio | arbitrary_json | prose | stale | unit_mismatch",
  "incumbent_scope": "supported | unsupported | unverified",
  "evidence_kind": "pytest_output | vitest_output | json | csv | log | markdown | none",
  "source_row": "claim-audit:17"
}
```

The incumbent-supported rows remain in the full corpus and are a strict subset of all rows. The Jev
checker runs against every row, but its supported/unsupported results are scored by class. A Jev
checker that wins only because the corpus omits test-count claims has failed the design.

### Label policy

Ground truth is determined before either tool runs, using deterministic artifact re-derivation and a
human-reviewed manifest. The labels are:

- `supported`: claimed number, unit, denominator, and cited artifact meaning agree;
- `contradicted`: evidence exists and disagrees in value, unit, denominator, or stated meaning;
- `unknown`: evidence is absent, stale, ambiguous, unavailable, or insufficient to decide.

`unknown` is not a negative class that a checker may convert into `contradicted`; it is a third
outcome. The two residual WRONG rows and all UNVERIFIABLE rows retain their audit provenance so the
comparison can test stale/correction behavior rather than erase the lane's history.

## The two arms

### Arm A — claim-check v0.6.0

Run the pinned release through its documented `commit-msg`/CLI path against the shared fixture. For
runner-supported cases, provide the exact runner command and output it expects. For unsupported
classes, record the documented `could not verify`/no-op result as `unsupported` or `unverified`,
not as a tool failure.

Required capture per case:

- pinned release/tag SHA;
- command and runner version;
- commit-message bytes/hash;
- test output bytes/hash, if used;
- exit code and stdout/stderr;
- parsed status (`blocked`, `allowed`, `could_not_verify`, or no claim);
- wall time and process count;
- whether the runner was whole-suite or narrowed.

Arm A is allowed to win. In particular, a Jev arm must not replace a deterministic test-count check
with a slower probabilistic answer when the incumbent is correct and cheaper.

### Arm B — Jev claim checker

The candidate follows Demo-3's structural boundary but must expose the incumbent comparison:

1. Deterministically parse number/unit/cited-artifact triples from the same message bytes.
2. Resolve and hash the cited artifact or runner receipt.
3. Perform deterministic exact checks for numeric identity, units, denominator fields, and missing
   paths before using Jev.
4. For unresolved semantic relation, call one pinned Noul with the artifact content and exact claim
   question; output `supported`, `contradicted`, or `withhold` with probability.
5. Refuse or withhold on malformed evidence, timeout, unsupported parser shape, or stale revision.
6. Emit a receipt with per-case status, evidence references, hashes, model/version, probability,
   latency, cost, and denominator counts.

The Noul must not re-derive deterministic arithmetic that local code can prove. If a JSON field equals
`0.942`, code should compare it; Jev is reserved for same-meaning, prose, ambiguous, or semantically
linked evidence. The candidate must therefore report where it yields to the incumbent's deterministic
path.

## Shared commands and artifacts

The design's commands are exact placeholders for the eventual package; no command was run in this
unit:

```sh
# Build the immutable shared corpus and manifest.
node tools/claim-bench/build-corpus.mjs \
  --audit docs/demos/duel-1/runs/claim-audit-20260918T003836Z.json \
  --out runs/claim-bench/corpus.json

# Incumbent arm, pinned v0.6.0.
claim-check verify-tests runs/claim-bench/cases/claim-msg.txt \
  --pytest-output runs/claim-bench/cases/runner/pytest.txt

# Jev arm, offline injected asker first, live only after budget approval.
node bin/jev-claim-check.mjs \
  --manifest runs/claim-bench/corpus.json \
  --out runs/claim-bench/jev-receipt.json

# Common scorer; it must score every case and split by incumbent scope.
node tools/claim-bench/score.mjs \
  --manifest runs/claim-bench/corpus.json \
  --incumbent runs/claim-bench/incumbent-receipt.json \
  --jev runs/claim-bench/jev-receipt.json \
  --out runs/claim-bench/comparison.json
```

The final receipt must include full denominators, not only headline percentages:

```json
{
  "cases": 72,
  "classes": {"test_count": 12, "non_count_numeric": 12, "percent": 10, "arbitrary_artifact": 16, "prose": 8, "stale": 8, "unit_mismatch": 6},
  "arm_a": {"supported": 12, "unsupported": 42, "unknown": 18},
  "arm_b": {"supported": 0, "contradicted": 0, "unknown": 0},
  "metrics_by_class": {},
  "cost_latency": {},
  "failures": []
}
```

The numbers in this illustrative schema are not results and must not be copied into EVAL. The builder
must fill them from the fixture; a zero or one-item denominator is an error for a claimed class.

## Head-to-head metrics

Report per-class and aggregate:

1. **Supported precision:** among `supported`, proportion whose ground truth is supported.
2. **Contradiction recall:** among ground-truth contradicted cases, proportion refused/flagged.
3. **Unknown discipline:** ground-truth unknown cases not falsely approved.
4. **Coverage:** fraction of the full corpus with a non-unknown, evidence-backed status.
5. **Scope lift:** coverage on classes documented outside claim-check's supported subset.
6. **False support rate:** unknown or contradicted claims emitted as supported.
7. **Revision/staleness recall:** stale true-at-revision-R claims correctly withheld at revision-S.
8. **Latency, provider cost, and local CPU:** per case and per resolved claim.
9. **Receipt completeness:** input/evidence hashes, command exit status, scope, model/version, and
   re-derivation path.

Do not collapse `unsupported` into an error for Arm A or into a win for Arm B. The comparison must
show where the incumbent has deliberately chosen not to answer and where the Jev checker adds useful
coverage.

## Ship criterion and incumbent wins

The Jev checker may ship as a demo only if an independent held-out corpus meets all of these
operational thresholds:

- On the incumbent-supported test-count subset, Jev has no more than a 2 percentage-point loss in
  supported precision or contradiction recall, and its cost/latency is reported rather than hidden.
- On the documented out-of-scope classes, Jev adds at least **30 absolute percentage points of
  actionable coverage** over Arm A, including at least five correctly resolved
  contradicted/unknown cases that Arm A reports unsupported/unverified.
- False support stays at or below **5%** overall and at or below **5%** on each class with at least
  ten cases.
- The added coverage is not confined to a lane-specific artifact type; at least two external-style
  artifact classes (for example benchmark JSON plus prose/log receipt) must show the lift.
- A reviewer can re-run both arms from the same manifest and reproduce the per-case statuses and
  cost/latency denominators.

The 30-point coverage lift is intentionally large. A 0.047% operational improvement would repeat
Demo-1's death: real, reproducible, and not worth a stranger switching. If the Jev checker only
adds one or two rare non-test claims, the result is **composition** (`claim-check` for test counts,
Jev for a separately justified artifact class), not a standalone demo. If the incumbent wins test
counts and Jev wins broader claims, the receipt must say both plainly.

## Failure modes that sink the candidate

1. **Out-of-scope classes are rare.** If non-test/percent/arbitrary-artifact claims are less than
   20% of a representative corpus, the coverage lift cannot change behavior; report the base rate
   and do not ship a general claim checker.
2. **Our own documents are a biased corpus.** The 60-row claim audit is valuable but lane-generated;
   add a held-out corpus from unrelated repositories or withdraw the market claim.
3. **Jev is merely a slower parser.** If deterministic code resolves all cases, remove the Jev call
   and keep the incumbent-style tool; a model call without semantic lift fails rung 2/4.
4. **Noul hallucinates support for unknown evidence.** Any false-support rate above 5% is a fail,
   regardless of mean accuracy.
5. **Runner scope is not controlled.** A Jev claim checker that declares whole-suite support from a
   narrowed test run repeats the incumbent's documented caution in worse form.
6. **No one reads receipts.** If pilot operators do not use the per-class report to change whether
   they trust a commit claim, the receipt is not product value; measure review/action change.
7. **Cost dominates the delta.** If Jev adds meaningful coverage but costs more than the operational
   risk/review time it saves, keep it as an offline research tool rather than a commit gate.

## NO-CLAIM

This is a comparison design only. No claim-check package was installed or executed, no Jev request was
made, no corpus was generated, and no precision/recall delta exists yet. The 19/4/37 counts come from
the committed claim-audit receipt; all proposed class counts, thresholds, and JSON values above are
acceptance design, not measurements. The incumbent is treated as a serious baseline, including cases
where it should win.
