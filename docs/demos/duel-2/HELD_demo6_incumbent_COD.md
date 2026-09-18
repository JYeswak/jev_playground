# Held resolution — Demo-6 notes-surface incumbent search

Status: **HELD, not ruled out.**
Candidate: Demo-6 claim-check notes form, pane-3 authored, reconciled demand 330.
Surface: explicit claim blocks in a writer-facing Markdown file checked against a local evidence
directory.
Search question: does a maintained tool already provide this whole capability, or do existing tools
supply only a deterministic baseline or a different document/RAG evaluation surface?

## Scope of the candidate

The authoritative contract defines:

```text
jev-claims <notes.md> --evidence <dir>
```

The writer supplies explicit blocks:

```text
CLAIM(<id>): <verifiable sentence>  EVIDENCE: <relative path> [<relative path> ...]
```

The command deterministically parses those blocks, loads the cited local files, uses Choice only
when multiple evidence spans are possible, and uses one Noul per claim-evidence pair. It must emit
`supported`, `contradicted`, or `insufficient` with probability and receipt fields, and it must
withhold rather than approve insufficient evidence. It is not Demo-3's commit-msg trigger, does not
extract arbitrary prose, does not run a server, and does not rewrite the notes.

The incumbent search therefore needs to test all of these dimensions, not merely find a tool that
mentions “fact checking”:

1. writer-facing Markdown/document input;
2. local or supplied evidence directory with path-level provenance;
3. claim-to-evidence support or contradiction decision;
4. explicit uncertainty/withhold behavior;
5. per-claim receipt and nonzero failure boundary;
6. a calibrated per-decision probability with an auditable threshold, if it claims to be a Jev
   substitute.

A tool matching only one or two is a baseline or adjacent comparator, not an owner. §3i's corrected
rule matters here: deterministic overlap is useful control data; it is not a kill. A model that emits
prose or an uncalibrated confidence number is also not a calibrated judgment owner.

## Search method: problem first

I searched the problem using combinations of:

- `claims evidence directory Markdown verifier CLI`;
- `document citations local evidence files supported contradicted insufficient`;
- `claim grounding evidence folder command line`;
- `notes claims cited artifacts report JSON`;
- `citation faithfulness retrieved context per claim`;
- `stale evidence fingerprint claim ledger`.

I then followed the strongest results into their own documentation and separated four categories:

- structured claim/evidence ledgers;
- deterministic citation and byte-grounding tools;
- model-assisted document fact-checkers;
- RAG evaluation metrics that accept context arrays but are not writer-facing file tools.

This produced several real adjacent baselines. It did not produce one documented maintained tool that
matches every Demo-6 field and the calibrated Noul/Choice boundary.

## Closest baseline: Open Knowledge (`okn`)

Sources:

- [Open Knowledge claims commands](https://openknowledge.sh/wiki/features/commands/claims.html)
- [Open Knowledge evidence commands](https://openknowledge.sh/wiki/features/commands/evidence.html)
- [Open Knowledge eval claims](https://openknowledge.sh/wiki/features/commands/eval.html)
- [Open Knowledge CLI changelog](https://openknowledge.sh/wiki/changelog/cli.html)

Open Knowledge is the strongest deterministic workflow match found. Its documented commands manage
structured typed claims, evidence references, lifecycle status, verification records, stale claims,
reconciliation, and JSON/Markdown validation. `okn evidence pin` creates content-addressed evidence
with SHA-256 and rejects changed bytes. `okn eval claims` replays claims across immutable Git
checkpoints and distinguishes `supported`, `refuted`, and `unverified`, with stale/hallucinated
states.

That is valuable and should be a serious control arm. It does **not** document a Noul-like calibrated
per-decision probability or a model judging semantic claim support. The docs explicitly describe
confidence as extraction confidence rather than truth confidence, and `eval claims` replays recorded
evidence-backed history rather than asking a model to determine truth. It also has a broader
repository/knowledge-base lifecycle than Demo-6's one notes file plus evidence directory.

**Disposition:** strong deterministic baseline, not a Jev judgment owner. Demo-6 must beat it only on
a measured semantic/uncertainty surface, not on hashes or path validation that Open Knowledge already
handles.

## Closest local citation verifier: Ethos

Source: [docushell/ethos](https://github.com/docushell/ethos).

The public description positions Ethos as an open-source local verifier for document citations,
source evidence, RAG, and agents. Its documented outcomes include `Grounded`, `Ungrounded`, `Stale`,
and `Capability-limited`, with commands shaped around a document plus citations/evidence artifacts.
This is close to Demo-6's path-level evidence and stale-fingerprint concern.

The documented boundary is equally important: Ethos verifies that cited evidence exists and matches;
it does not independently determine whether a claim is true, relevant, or complete. That makes it a
deterministic grounding/citation baseline. It can expose missing files, changed evidence, and
citation mismatch, but it does not supply the calibrated semantic support probability that Demo-6's
Noul contract requires.

**Disposition:** baseline for evidence existence, provenance, and staleness; not an owner of the
calibrated claim-meaning question.

## Closest model-assisted document reviewer: ClaimLint

Source: [klittle32/claimlint](https://github.com/klittle32/claimlint).

ClaimLint is the closest model-assisted document workflow found. Its documented artifacts include
`claims.json`, findings, questions, reviewer provenance, `evidence.json`, and `report.html`. It
organizes claims, evidence, investigation state, and verdicts such as `Supported`, `Overstated`,
and `Unsupported`.

Its own limitations prevent treating it as a complete owner:

- the README warns that “unsupported” means available evidence does not establish the claim; it does
  not automatically mean false;
- it warns that ClaimLint is not an authority on truth and does not guarantee factual correctness or
  exhaustive research;
- the model/harness performs investigation and judgment, while ClaimLint preserves the evidence
  trail;
- the public description does not establish a calibrated per-claim probability, a fixed threshold,
  or Demo-6's exact local `--evidence <dir>` exit-code contract;
- it is more general document review than an explicit structured-block writer gate.

ClaimLint is therefore a meaningful non-Jev model comparator if it can be pinned and run on a shared
corpus. It is not enough to say that Demo-6 is owned because both emit a support label: Demo-6's
measured wedge must be calibrated typed uncertainty, deterministic citation loading, and a receipt
that refuses insufficient evidence.

**Disposition:** closest model-assisted baseline; not a demonstrated calibrated judgment owner.

## Scholarly-citation tools: paper-verify and citeguard

Search found [paper-verify](https://github.com/nolainjin/paper-verify), which is designed for Markdown
and text documents, extracts scholarly identifiers/URLs, evaluates citation support, and writes a
report with `Match`, `Partial`, `Mismatch`, `Uncertain`, and `Inaccessible` outcomes. It documents an
`--evidence-dir` workflow. This is a closer file/evidence surface than generic RAG metrics, but its
scope is bibliography/source retrieval and scholarly citations rather than arbitrary local evidence
files referenced by explicit claim blocks. Its evaluation/confidence semantics also require a pinned
run before any claim of calibration.

[Citeguard](https://github.com/xiaweiyi713/citeguard) is another structured citation review/triage
candidate with JSON states such as unresolved sources, source changes, metadata issues, and
`review_required`. It appears closer to citation management and publication pipelines than to a
writer-facing local claim block with a Noul threshold.

**Disposition:** adjacent citation baselines. They may be included in a future corpus if their pinned
versions and input formats can represent Demo-6 cases, but they do not establish that the exact notes
surface is owned.

## RAG evaluation frameworks: Ragas and DeepEval

### Ragas

Official [Ragas faithfulness documentation](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/faithfulness/)
defines a score over claims extracted from a generated response and supplied `retrieved_contexts`.
It checks whether response claims can be inferred from context and computes supported claims divided
by total claims. This is a useful semantic baseline, but it expects an evaluation test case with
context strings, not a writer-facing Markdown file and path-resolved evidence directory. It returns a
metric score, not Demo-6's per-claim exit-code contract, and its model-based score is not automatically
calibrated as a probability.

### DeepEval

Official [DeepEval faithfulness](https://deepeval.com/docs/metrics-faithfulness) and
[CitationFaithfulnessMetric](https://deepeval.com/docs/metrics-citation-faithfulness) distinguish
whether an answer is supported by retrieved context from whether each citation marker points to the
specific supporting passage. Required test-case fields include `actual_output` and
`retrieval_context`, with optional expected output. This is an excellent evaluation comparator for
claim-level support, but it is a test harness, not a notes-file/evidence-directory writer gate. Its
thresholded metric is not documented as a calibrated per-decision probability with a first-class
`insufficient` refusal.

**Disposition:** reusable semantic evaluation baselines, not direct incumbents for Demo-6's CLI
surface. They can supply a control arm in a later shared corpus if their model and threshold are
pinned.

## Scope matrix

| Capability | Open Knowledge | Ethos | ClaimLint | paper-verify/citeguard | Ragas/DeepEval | Demo-6 target |
|---|---|---|---|---|---|---|
| Explicit local evidence files | Strong | Strong | Partial/depends on workflow | Partial/source-oriented | Context strings | Required |
| Writer Markdown input | Structured bundle | Supported docs/citations | Strong | Strong | No direct file gate | Required |
| Claim-to-evidence support | Recorded/replayed | Grounding/match | Model-assisted review | Citation support | Context support | Required |
| Contradicted outcome | Refuted | Ungrounded/capability-limited | Overstated/Unsupported | Mismatch/Partial | Low score | Required |
| Insufficient/withhold | Unverified/stale | Capability-limited | Human-review limitation | Uncertain/Inaccessible | Metric/threshold | Required |
| Per-claim calibrated probability | Not documented | No | Not documented | Not established | Not established | **Required Jev wedge** |
| Deterministic citation receipt | Strong | Strong | Evidence trail | Strong | Test-case receipt | Required |
| Exit nonzero on contradiction | Gate/check modes | Verify modes | Workflow-dependent | Report/CI-dependent | Harness-dependent | Required |
| Choice over spans | Not the documented core | Not the documented core | Not the documented core | Not the documented core | Not the documented core | Required only when ambiguous |

No single row is an exact owner. Open Knowledge and Ethos are the strongest deterministic controls;
ClaimLint and paper-verify are the closest model-assisted/document reviewers; Ragas and DeepEval are
semantic metric baselines. The remaining question is not whether Demo-6 can produce a support label;
it is whether Jev supplies a calibrated per-claim probability, explicit withhold, and auditable
threshold that changes writer decisions on a shared notes/evidence corpus.

## Adjudication

**Demo-6 remains HELD at 330; no score change and no kill.** The problem search found real baselines
and adjacent tools, including tools that are closer than the original incumbent list. It did not find
a pinned maintained tool that simultaneously provides:

1. explicit claim blocks in a writer-facing Markdown file;
2. arbitrary local evidence-directory paths;
3. deterministic path/hash provenance;
4. typed support/contradicted/insufficient outputs;
5. calibrated per-decision probability with a tunable threshold and audit trail; and
6. a writer-time exit-code boundary that withholds insufficient evidence.

The corrected baseline plan is therefore:

- baseline deterministic path/hash/stale checks against Open Knowledge and Ethos;
- baseline model-assisted claim review against ClaimLint or paper-verify if a pinned run is possible;
- optionally baseline a Ragas/DeepEval claim-context metric on the same claim/evidence pairs;
- measure Demo-6's Jev probability calibration, withhold coverage, false-approval rate, cost, and
  writer action lift.

If a future pinned tool satisfies all six simultaneously, Demo-6 must re-open the incumbent question.
If the new tool uses a judgment model but has no calibration/withhold/audit trail, it remains a
baseline rather than a structural kill under §3i.

## Retry condition

The hold resolves only with a pinned shared-corpus comparison showing either:

- a maintained tool fully covers the six-part Demo-6 contract, including calibrated per-claim
  probability and refusal; or
- Demo-6 materially outperforms the deterministic and model-assisted baselines on a held-out corpus
  with false approval ≤5%, ECE ≤0.10, and at least 20% writer-review/action lift.

A deterministic incumbent winning path validation is expected and is not a kill. A semantic tool
winning a support label without calibrated probability is an adjacent baseline, not ownership.

## NO-CLAIM

No incumbent was installed, no notes/evidence corpus was run, no model was called, and no adoption or
performance result was measured. The search is public-document research with bounded source quality;
repository freshness and exact version compatibility remain open until a pinned local baseline run.
