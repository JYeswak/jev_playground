# Oracle design from the Dicklesworthstone corpus

**Corpus:** live FH search over the pinned mirror (`/Volumes/ZestData/dicklesworthstone-mirror`)
with 306 ledger rows, 178 technical sources, 1,433,606 indexed technical chunks, and 102 bead
repositories. FH's own search envelope says ranking is evidence ordering, not proof; the citations
below were then opened from the mirror at the pinned paths.

This is the answer to the lane's failure mode: an oracle that only says NO is a refusal mechanism,
not a decision oracle. Production exemplars pair a predeclared positive boundary with a negative
control, preserve applicability, and make the promotion/hold/reject result mechanically visible.

## Taxonomy

### 1. Threshold promotion gate

**Citation:** `franken_engine/crates/franken-engine/src/promotion_gate_runner.rs:266-328`,
`franken_engine/crates/franken-engine/tests/parser_performance_promotion_gate.rs:1182-1189`.

`evaluate_performance_threshold` fails empty evidence, checks every measurement against declared
minimum throughput and maximum latency, and returns `passed=true` when all measurements are inside
bounds. The test pins the exact boundary: `delta == threshold` produces `"promote"`.

- **Decision:** promote or hold/reject.
- **Fairness:** threshold and denominator are inputs; empty evidence fails; boundary behavior is
  tested explicitly.
- **Failure avoided:** a one-way failure detector that can never authorize a ship, and threshold
  ambiguity at the boundary.

### 2. Monotone per-category ratchet

**Citation:** `franken_ocr/docs/conformance/RATCHET.md:33-51` and
`franken_ocr/src/conformance.rs:780-789`.

A candidate may land only when no category's conservative lower bound falls below its committed
floor. Holding or raising a category is admissible; lowering or dropping a baseline category is
rejected; a new category establishes an initial floor. Small calibration samples trigger a declared
deterministic fallback instead of a fake conformal decision.

- **Decision:** admissible/promote or reject/hold.
- **Fairness:** no-cross-regression is category-wise, not aggregate-only; small-n applicability is
  checked and ledgered.
- **Failure avoided:** aggregate improvement hiding a regression, and a tiny sample laundering a
  meaningless confidence bound.

### 3. Performance ratchet with applicability authority

**Citation:** `frankensearch/crates/frankensearch-quill-gauntlet/src/perf_ratchet.rs:732-740`.

The evaluator first resolves a candidate applicability plan and returns a structured evaluation;
missing exact applicability authority is fatal rather than silently treated as pass. The same module
predeclares a 5% keep floor and 30 measured iterations for a Tier-I decision.

- **Decision:** keep/promote, reject, or refuse to decide when applicability is missing.
- **Fairness:** the candidate cannot choose its own applicability after seeing results; measurement
  count and floor are predeclared.
- **Failure avoided:** changing the denominator or applicability rule after observing a favorable
  result.

### 4. Mixed positive/negative control denominator

**Citation:** `franken_engine/crates/franken-engine/src/differential_oracle_perf.rs:85-118`.

The oracle declares required control cases and exact source hashes before the measurement. The list
contains a mixed positive/negative denominator, so a custom manifest cannot substitute only favorable
programs while retaining the same case names.

- **Decision:** accept/reject the differential result.
- **Fairness:** case identity and bytes are pinned; both sides of the expected behavior are present.
- **Failure avoided:** cherry-picking a denominator or silently swapping fixtures.

### 5. Metamorphic relation plus golden artifact

**Citation:** `franken_tts/crates/ftts-conformance/tests/metamorphic_invariants.rs:315-505`.

The test runs a pinned reference route, loads oracle fixtures, computes a PCM hash, and compares it
to a platform-specific golden. Missing fixtures, incomplete model bundles, or unusable checkpoints
skip explicitly; they do not pass. The comments also separate platform byte identity from
cross-platform content metrics.

- **Decision:** golden/conformance pass, explicit skip, or failure.
- **Fairness:** fixture availability and platform applicability are explicit preconditions; the
  relation is stronger than a manually asserted output.
- **Failure avoided:** treating missing oracle material as green, or demanding impossible
  cross-platform byte identity.

### 6. Metamorphic invariants when golden outputs are hard to enumerate

**Citation:** `frankenlibc/README.md:1242-1253` and
`frankenlibc/crates/frankenlibc-harness/tests/memcpy_strict_conformance_test.rs:452-465`.

The project uses round-trip and invertibility relations—`inet_pton/inet_ntop`, `strto*/snprintf`,
and base64—rather than only fixed expected outputs. A transformation must preserve the invariant
under the relation, even where a complete golden corpus is impractical.

- **Decision:** invariant holds or fails.
- **Fairness:** the oracle is derived from a property of the operation, not a hand-picked answer.
- **Failure avoided:** false confidence from a narrow golden set and no coverage of unseen valid
  inputs.

### 7. Adversarial survival gate

**Citation:** `franken_engine/crates/franken-engine/src/promotion_gate_runner.rs:328-...` and
its promotion-gate integration tests, including
`tests/plas_burn_in_gate_integration.rs:117-146`.

The same promotion machinery evaluates adversarial survival separately from ordinary performance;
known-bad scenarios must remain rejected while ordinary measurements pass.

- **Decision:** promote only if normal and adversarial gates both pass.
- **Fairness:** negative controls are first-class denominator members, not after-the-fact anecdotes.
- **Failure avoided:** a benchmark that passes only on cooperative inputs.

## House rules for this lane

An oracle may rule a candidate only if all of these are present:

1. **Named consumer:** identify the ship, adoption, or decision the oracle controls.
2. **Predeclared positive boundary:** write `promote/adopt/keep if >= X` or an equivalent explicit
   success predicate before measuring.
3. **Symmetric outcome:** the mechanism can return promote/adopt/keep as well as reject/hold/refuse.
4. **Applicability gate:** empty evidence, missing sources, insufficient n, and unsupported shapes
   refuse to decide rather than pass or universally reject.
5. **Pinned denominator:** inputs, fixture identities, source hashes, and exclusions are fixed before
   measurement.
6. **Positive and negative controls:** include a known-good case and a known-bad case; test both
   directions.
7. **Boundary tests:** exact threshold, one-below threshold, and empty/insufficient cases are
   executable tests.
8. **No aggregate laundering:** per-category or per-case regressions cannot hide behind an improved
   aggregate.
9. **Uncertainty or bounded null:** report intervals, disagreement, or an explicit bound on what a
   null result means. Never turn “no evidence here” into “the mechanism never works.”
10. **Promotion receipt:** record what changed when the positive predicate was met, or why the result
    stayed held/rejected.

Our compaction oracle currently violates at least rules 2, 3, and 9: it has no preregistered success
threshold for job usefulness, its measured real-session examples mostly refuse or drop everything,
and byte/token reduction is not a task-success oracle. It must not be used to promote compaction as
useful without a positive continuation-quality control.

## No-claim

- This report does not claim every cited repository is production-correct.
- FH search ranking is not treated as proof; source paths and line ranges are the evidence.
- No clone was edited.
