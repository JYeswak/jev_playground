<!-- A/B verdict migration (2026-09-18): any literal n=1 relative verdict below is historical/retracted. Current harness withholds verdicts until each arm has >=10 zero-spread samples; see compaction/ab/verdict.ts. -->

# Duel-1 cross-score: COD on MUSE ideas

Bead: `jev-demo-loop-a1q`
Role: non-author, different-lineage grader of `WIZARD_IDEAS_MU.md`
Ground truth: `compaction/runs/replay-big-20260917.json` and
`compaction/runs/ab-20260917.json`

These are judgment scores, not implementation results. I read all five candidates,
`## Winnowed out (10)`, and `## Refused by sources` before scoring. I did not read the
Claude-side ideas file.

## Summary

| Idea | Score | One-line verdict |
|---|---:|---|
| MU-1 routing backtest | **875** | Best next demo: measure our counterfactual savings before adopting a router. |
| MU-2 context-admission screen hook | **470** | Strong injection-screen direction, but the literal credential branch leaks what it claims to protect. |
| MU-3 foreman-lite bead completion judge | **805** | High-value close gate with unusually credible RED arms; concurrency and state-baseline details remain. |
| MU-4 working-point claim-checker | **735** | Directly grounded and shippable, but claim extraction and citation-span semantics are underspecified. |
| MU-5 signal-kit | **640** | Correct meta-lesson and honest N≥50 gate, but greenfield infrastructure with no immediate lane payoff. |

**Strongest: MU-1.** The deciding sentence is: *it measures what routing would have
saved on our own turns before we accept someone else's router numbers.*

**Weakest: MU-2.** The deciding sentence is: *the literal implementation sends incoming
credential material to Jev in order to decide whether credential material may enter context.*

**No merges.** MU-3 and MU-4 are both verification gates but target different evidence
objects (bead completion versus written claims). MU-1 and MU-5 both measure decisions but
have different products (routing counterfactual versus calibrated classifier template).

## MU-1 — omp routing backtest

**Score: 875/1000**

### Truth and citation

Strong, direct citation. MUSE lines 17-20 cite Usage Map §4 and the pinned
`jev-codex-router@8292b51` result: −60% versus full-frontier on 237 real turns, with
cost, latency, fail-open, kill-switch, and local-log details. Usage Map lines 32-39
support the same claim and explicitly call the backtest for our omp logs “Most directly
valuable to us.” The idea correctly treats the upstream number as a hypothesis to test,
not as a result transferable by faith.

The claim is bounded correctly if “estimated $ saved” remains a counterfactual based on
a committed price table. Agreement with the model that actually served the turn is an
oracle proxy, not ground truth; the proposed spot human labels and an explicit EVAL
Boundary are necessary.

### Usefulness and readiness

High immediate value: this lane runs three panes and already emits session transcripts,
and routing can change spend and latency without changing task semantics. The existing
omp adapter and fixture shape make the input seam concrete. No routing implementation or
receipt exists in the inspected tree, so this is a greenfield demo with a good reuse seam,
not a ready feature.

### Four-artifact path

- **Install:** one `npm run backtest -- <transcript> [--out ...]` command is a plausible
  clean-clone surface; refusing without a transcript is the right boundary.
- **Deterministic tests and RED arms:** the proposed frontier-needed trigger, empty
  transcript, and missing-price-model cases are real fail-closed arms. Add a negative
  control proving a down-route is not counted as savings when the price table is absent.
- **Receipt:** turns, routed-down count, committed prices, latency distribution, model
  identity, and threshold make the result reproducible.
- **EVAL row:** the proposed Boundary must distinguish replay evidence, model-serving
  agreement, human labels, and unmeasured counterfactual quality.

### Complexity judgment

Justified. The hard parts are price-table versioning, model-name normalization, and
making “would have routed down” deterministic. Those are bounded data contracts, not a
new daemon or service. Keep the first version replay-only; do not add online routing,
adaptive thresholds, or a dashboard to the backtest.

## MU-2 — context-admission screen hook

**Score: 470/1000**

### Truth and citation

The injection-screen portion is directly grounded: Usage Map lines 11-15 report
`jev_screen` blocking a hidden instruction at injection probability 0.99 and name the
omp context-admission hook as the demo angle. The credential branch is not supported by
that measured source. The MUSE proposal says the hook asks Jev whether an incoming result
“carries credential material” (MUSE lines 65-70), but that creates the central safety
problem.

I disagree with the title-level implication that “secrets never enter context” (MUSE
line 57) as written. A Jev question must receive the incoming result before the hook can
classify it. A real secret therefore crosses the paid external boundary before the hook
can block or redact it. The lane secrets rule forbids leaking key-derived material into
logs, fixtures, and messages; it does not authorize sending it to the classifier. A
local deterministic secret detector must run first, and the Jev branch must refuse or
operate only on a proven redacted surrogate. Without that redesign, this is a security
regression disguised as admission control.

### Usefulness and readiness

Injection admission is valuable at the context boundary, and the clean-page silent
healthy path is a good operational requirement. The proposed universal read/fetch/paste
hook would also add paid latency and an availability dependency to every incoming result.
The specified evidence contains no working omp `tool_result` hook or live receipt, so
readiness is greenfield. The claimed L3 live proof is a ship requirement, not evidence
already present.

### Four-artifact path

- **Install:** the profile-aware `<repo>/.omp/hooks/pre/` installer and refusal on an
  undiscoverable hook directory are concrete.
- **Deterministic tests and RED arms:** hidden injection, clean documentation, runtime-built
  fake credential plants, admitted injection, commented-on clean content, and empty scan
  set are good arms. They do not prove that real credentials never leave the process.
- **Receipt:** screened/blocked counts and latency are necessary but must include detector
  ordering, redaction status, and whether Jev saw original or surrogate bytes.
- **EVAL row:** L3 transcript/frame evidence is plausible only after the real seam fires;
  the Boundary must explicitly exclude real-secret testing.

### Complexity judgment

As written, complexity is not the main problem; trust-boundary ordering is. A safe
version needs a local prefilter, explicit redaction, fail-closed behavior on detector
failure, and a separate injection-only Jev question. Those changes reduce the claim from
“secrets never enter context” to a defensible layered gate. Until then, the citation is
partial and the credential feature is not shippable.

## MU-3 — foreman-lite bead completion judge

**Score: 805/1000**

### Truth and citation

Direct citation. Usage Map lines 47-50 describe `foreman@2c43982` having Codex workers
build while Foreman+Jev independently assess completion, requirements, tests, verify
needed, and human needed. MUSE lines 103-105 accurately carry that dimension set into a
`jev-bead-check` wrapper.

The proposal correctly rejects a bare chat-model “looks good” answer and makes the
verdict typed, thresholded, and evidence-linked. The independent judge is not itself an
oracle: it is a pre-close signal. The command must retain a human-needed outcome and
never turn Jev confidence into permission to bypass a real gate.

### Usefulness and readiness

High lane fit. The lane closes beads frequently, and the exact failure mode—self-certified
close with no evidence checklist—is real. The proposal is greenfield: no working
`jev-bead-check` implementation or receipt was part of the inspected ground truth. The
one-script/no-daemon shape keeps adoption cost reasonable.

### Four-artifact path

- **Install:** one command is plausible, but the workflow must pin the `br` version and
  define how a bead start revision is recorded.
- **Deterministic tests and RED arms:** empty diff → human-needed, deleted acceptance file
  → verify-needed, satisfying diff → complete, and title-only body → ERROR are strong
  fires-on-known-bad cases (MUSE lines 115-119).
- **Receipt:** bead id, start/end revisions, verdict, per-dimension scores, model version,
  and evidence checklist are enough to audit a decision.
- **EVAL row:** record whether the judge was run before the close and what it did not
  inspect. A later follow-up bug is calibration data, not proof that the original close
  was invalid.

### Complexity judgment

Mostly justified, with two required safeguards: snapshot the diff and bead body at the
start of the check, and fail closed if the bead changes while the check runs. Shared
worktrees make a moving HEAD and a closed bead especially dangerous. Do not add a daemon,
automatic close, or a second review service in the first cut.

## MU-4 — working-point claim-checker

**Score: 735/1000**

### Truth and citation

Direct citation. Usage Map lines 17-21 report `jev_verify@6ec5efc` catching a contradicted
claim at confidence 1.0 against a city ordinance and name the working-point claim-check
as the demo angle. MUSE lines 138-145 use that source accurately and preserve the key
insufficient-context → withhold behavior.

The claim/evidence decision is well grounded. The weak point is the phrase “extracts
verifiable working points” (MUSE line 143): extracting claims and citation spans from
arbitrary Markdown is a separate parsing and scope problem, not demonstrated by
`jev_verify`. The first version should require explicit claim blocks or structured
citations rather than pretend arbitrary prose extraction is solved.

### Usefulness and readiness

Broad lane value: EVAL rows, duel files, receipts, and close-out reports all contain
claims that should be checked before publication. The contradicted and insufficient
outcomes are more useful than a binary “looks supported.” No implementation or measured
receipt exists in the evidence set, so readiness is greenfield. Choose one canonical
runtime (`npm` or `uv`) instead of shipping an ambiguous `uvx`/`npx` fork.

### Four-artifact path

- **Install:** a single command can ship after the input contract is narrowed to explicit
  working-point blocks and citation paths.
- **Deterministic tests and RED arms:** supported pair, contradicted pair, insufficient
  pair, empty evidence directory, and unlabeled citation are good RED arms. Add a
  citation-span mismatch arm so a claim cannot pass merely because some other evidence
  file contains the same words.
- **Receipt:** claim ids, evidence paths and hashes, verdict, confidence, model version,
  and withheld reasons make the result auditable.
- **EVAL row:** record the parser contract, evidence corpus, and the boundary between
  claim checking and legal/source authority.

### Complexity judgment

Worthwhile, but only as a constrained writer-facing gate. Generic extraction, citation
resolution, and evidence directory semantics can grow into a document system. Keep the
first release to explicit claim records and deterministic evidence selection; let the
Jev call judge the pair rather than generate or rewrite prose.

## MU-5 — signal-kit

**Score: 640/1000**

### Truth and citation

Direct citation. Usage Map lines 63-72 report the zero-label lesson: a verdict alone
loses, five signal questions plus a logistic regression reaches 95.1% accuracy, AUROC
0.988, ECE 0.027, and a fixed strong rule reaches 89.5%. The MUSE proposal accurately
turns that into a template and explicitly refuses to apply it to our resume-quality data
until N≥50 (MUSE lines 199-202). That honesty is a material strength.

The local A/B is not a 50-sample training corpus: it is one transcript, three questions,
and four live calls. The compaction receipt says summarization won 3–1 on the measured
resume questions, but that is not enough to fit or validate a signal model. The proposal
correctly treats the local application as future work rather than laundering this result
into evidence.

### Usefulness and readiness

The general pattern is useful for future classifier decisions and could prevent another
verdict-only mistake. Immediate lane value is low because the required labels do not yet
exist. No working template or receipt exists in the inspected tree; this is greenfield
research infrastructure, not a ready demo.

### Four-artifact path

- **Install:** `uv run` can provide a clean synthetic end-to-end command.
- **Deterministic tests and RED arms:** empty corpus and committed synthetic golden report
  are solid. “Shuffled labels → no signal” needs a fixed seed, a pre-registered statistical
  threshold, and a small-sample refusal test; otherwise it is probabilistic theater.
- **Receipt:** dataset hash, label count, split policy, fit seed, coefficients, calibration
  bins, AUROC/ECE, fixed-rule baseline, and model versions are required.
- **EVAL row:** the synthetic-only Boundary must remain prominent until a user-labelled
  corpus reaches the declared N≥50 retry condition.

### Complexity judgment

Justified only as a small template. Logistic regression, calibration, and a fixed-rule
floor are manageable; a generalized “starter” for every classifier is not. Defer local
resume-quality fitting until the N≥50 gate is actually met.

## Cross-score conclusion

The MUSE set is intentionally mixed: one high-leverage measurement harness, two useful
verification gates, one eventually useful calibration template, and one security idea
that is unsafe without a trust-boundary redesign. The highest-confidence next candidate
is MU-1. MU-3 is the best operational gate after it. MU-2 should not advance in its
current credential-screening form.

**NO-CLAIM:** I did not implement or run any proposed harness, hook, CLI, classifier, or
live validation. These are independent judgments grounded in the cited map, the two
receipts, and the AGENTS.md acceptance bar; they are not measurements of the five ideas.
