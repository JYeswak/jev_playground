# Duel-2 rung 2 — MU-H1 TODO-judge JEV shape

Status: non-author rung-2 assessment.
Candidate: MU-H1 stale-TODO truth judge from `docs/demos/duel-2/DEMAND_HUNT_MU.md` (`6c101d5`).
Non-author demand score: **820** in `HUNT_SCORES_COD_ON_MU.md` (`98a74d8`); author score 900;
gap 80.
Question: whether the candidate requires typed calibrated judgment rather than ordinary chat
review.
Recusal: COD-H1…H5 and Demo-9 are not assessed here.

## Verdict

**RUNG 2: CLEARED on structure, with the exact mechanism below required.**

MU-H1 has a real judgment-shaped core: given one deterministically located TODO marker plus a
bounded evidence envelope, Noul judges whether the marker's proposition remains true in the current
codebase. The model does not find markers, rewrite comments, summarize the repository, or invent a
work item. A fixed local policy maps the typed judgment probability to `active`, `stale`, or
`uncertain`, and a receipt records the input hashes, model version, probability, evidence references,
and action.

The hunt's one-sentence mechanism was directionally correct but under-specified. This document
closes the questions that must be pinned before thin proof: exact question, finite output semantics,
deterministic candidate extraction, malformed/withhold behavior, and the precise reason an ordinary
chat call is a weaker control. If implementation deviates by asking a model to discover markers or
extract arbitrary TODO meaning, this clearance is void and the candidate returns to HELD.

## 1. What Noul judges; what Choice chooses

### Deterministic candidate record

The scanner first enumerates only explicit marker tokens from the repository: `TODO`, `FIXME`,
`HACK`, `XXX`, `BUG`, and a configured project marker set. A marker record contains:

```json
{
  "marker_id": "sha256(repo_sha + file + byte_start + byte_end + raw_marker)",
  "file": "src/cache.ts",
  "symbol": "loadCache",
  "line": 88,
  "byte_start": 2410,
  "byte_end": 2467,
  "raw_text": "TODO: remove workaround once v2 endpoint ships",
  "blame": {"commit": "...", "author": "...", "introduced_at": "..."},
  "evidence": [
    {"kind": "code_context", "sha256": "...", "path": "src/cache.ts", "range": "80:102"},
    {"kind": "related_symbol", "sha256": "...", "path": "src/api.ts", "symbol": "v2"},
    {"kind": "test_or_config", "sha256": "...", "path": "package.json", "range": "..."}
  ]
}
```

The raw marker is data, not an instruction. The evidence list is assembled deterministically from
configured rules: surrounding source range, symbol references, recent diff/blame metadata, explicit
issue references, tests, configuration, and dependency declarations. A missing or unavailable
evidence source is represented as `unavailable`; it is never silently replaced by a generated
summary.

### Exact Noul question

For each supplied marker record, Noul receives the raw marker and the bounded evidence envelope. The
question text is:

> You are judging one source-code marker, not writing code. The marker is `<raw_marker>` at
> `<file>:<line>` inside `<symbol>`. The supplied evidence is `<evidence records>`. Does the marker's
> stated unfinished condition remain true in the current repository state? Return true only when the
> evidence supports that the marker still accurately describes unresolved work at this location.
> Return false when the evidence shows the condition is fulfilled, obsolete, or contradicted. Withhold
> when the evidence is insufficient, ambiguous, unavailable, or requires guessing beyond the supplied
> records. Do not propose a replacement TODO, delete code, summarize the repository, or infer an
> action not stated by the marker.

Typed criteria:

- `true`: the marker's stated condition is still supported as unresolved by the supplied evidence;
- `false`: the condition is fulfilled, obsolete, or contradicted by the supplied evidence;
- `withhold`: insufficient or ambiguous evidence; never coerce to true or false.

The response schema is a typed verdict plus probability and model metadata, for example:

```json
{
  "verdict": "true | false | withhold",
  "probability": 0.0,
  "reason_code": "active | fulfilled | obsolete | contradicted | insufficient_context",
  "evidence_refs": ["record-id/range"],
  "model": "jev-<pinned-version>"
}
```

The exact field names must follow the Jev API's typed schema at implementation time; the semantic
invariant is non-negotiable: finite verdict, calibrated probability, explicit withhold, and no
free-form task generation. A missing answer, malformed probability, unknown evidence reference, or
out-of-range value is an error/withhold, never an active or stale approval.

### Local mapping to report labels

Noul does not need to invent a third class. The local policy maps its typed result:

- `true` with probability at or above the predeclared threshold → `active`;
- `false` with probability at or above the threshold → `stale`;
- `withhold`, insufficient probability, malformed output, or threshold disagreement → `uncertain`;
- any detector/evidence assembly error → `error`, excluded from precision/recall denominators.

The threshold is a policy parameter, not an unmeasured claim. Its value and calibration set belong in
the receipt and later rung-4 measurement. A threshold may not turn every low-confidence answer into
`stale`; uncertain is a first-class outcome.

### Choice role

The current MU-H1 mechanism does **not require a Choice call**. Noul judges each already-supplied
marker record, and a deterministic sorter orders the resulting worklist by confidence, age, or a
predeclared risk key. Adding a Choice merely to select a truth label would duplicate Noul and make
the semantics less clear.

If the product later adds an operator action selector, Choice may select only from caller-supplied
finite actions:

```text
keep / inspect / promote-to-issue / remove-after-human-approval
```

The action candidates must be provided by local policy and are not truth labels. Choice cannot
invent `delete`, choose a new priority, or turn `uncertain` into `remove`. The current candidate's
rung-2 proof therefore rests on Noul; “what Choice chooses” is either no Choice in the minimal
shape or the explicit finite operator-action set above in an extended shape.

## 2. Why ordinary chat is measurably worse

The author's sentence is substantially right about the desired control but too absolute about chat.
A fixed prompt, pinned model, structured-output schema, deterministic evidence envelope, and receipt
can recover **syntactic comparability** for ordinary chat calls. Per-marker prompting is not
inherently incomparable if the caller pins the prompt, input shape, model, temperature policy, and
parser.

The residual measurable disadvantage is that an ordinary chat completion does not by itself provide
a calibrated typed probability and a mandatory withhold semantics. It may return a parseable label,
but the number in `{"confidence": 0.91}` is not a calibrated probability until a representative
labelled set establishes reliability; it may produce prose, an off-list label, or a confident answer
when evidence is insufficient. Noul's value is the contract for cheap, repeated, probability-bearing
judgments and an explicit refusal path—not the word “LLM” or a claim that chat models cannot classify.

The head-to-head properties are measurable:

| Property | Fixed chat prompt | MU-H1 Jev shape |
|---|---|---|
| Candidate discovery | Must be deterministic outside the chat call | Deterministic outside the Noul call |
| Output | May be schema-constrained, but parser failures vary by integration | Typed verdict and probability required |
| Confidence | Self-reported unless separately calibrated | Calibration procedure and version recorded |
| Unknown evidence | Must be prompted and audited; often becomes a guess | `withhold` is a required outcome |
| Batch comparability | Recoverable with pinned inputs and receipts | Native target: same typed shape per marker |
| Audit trail | Caller must build it | Marker/evidence hashes and model metadata are required |
| Cost/latency | Depends on provider and output verbosity | One short Noul per marker; output is bounded |

Therefore the honest one-sentence answer is:

> A fixed chat rubric can recover parseability and some comparability, but it is measurably weaker
> unless an external layer supplies the calibrated probability, explicit withhold behavior, and
> batch receipt that MU-H1 treats as the product.

This distinction prevents a false rung-2 claim. If Jev is called with an unpinned prompt, the result
is not automatically a candidate merely because the response is called a verdict. If a conventional
chat model is wrapped with the same calibration, threshold, parser, evidence hashes, and receipt,
it may become a comparable control arm; that is the correct baseline, not an a priori rhetorical
victory for Jev.

## 3. Extraction, generation, and summarization audit

### Allowed deterministic extraction

Locating TODO markers is extraction, but it is permitted and must be explicit. The scanner may use:

- anchored lexical scanning for marker tokens;
- Tree-sitter/AST traversal to associate a marker with its enclosing symbol;
- `git blame` and commit metadata for age/context;
- deterministic reference lookup for issue IDs, tests, configs, and symbols;
- fixed byte/range slicing for the evidence envelope.

This is analogous to enumerating acceptance lines before Demo-4's Noul calls or enumerating quote
spans before Demo-5's Choice. The extractor discovers candidate records; it does not decide whether
the TODO is true. Its output is hashed and visible in the receipt.

### Forbidden hidden model stages

The following would break the candidate's rung-2 shape:

1. Asking a model to find all TODOs in a repository instead of scanning deterministically.
2. Asking a model to rewrite “remove workaround once v2 ships” into a latent structured proposition
   without recording the raw marker and extracted fields.
3. Asking a model to summarize the relevant repository and then judging only the summary.
4. Asking a model to generate suggested code, a replacement TODO, or an issue body as part of the
   truth verdict.
5. Treating a missing code range, failed blame lookup, or unavailable issue as evidence that the
   TODO is stale.
6. Sorting or deleting markers based on a generated narrative rather than typed verdict plus local
   policy.

The correct pipeline is:

```text
raw repository
  -> deterministic marker enumeration
  -> deterministic bounded evidence collection
  -> Noul true/false/withhold + probability
  -> local threshold / uncertain mapping
  -> deterministic receipt and worklist
```

No summarization is needed. The evidence envelope may contain multiple bounded source snippets, but
it must preserve their paths, ranges, hashes, and unavailable states. If a later design adds
semantic proposition extraction, it must either make that extraction deterministic and inspectable or
return to HELD for a new rung-2 review. The original Demo-5 defect was not “extraction exists”; it
was an unspecified extraction claim with no source-range mechanism. MU-H1 can avoid that defect by
making the stage explicit.

## 4. Structural verdict

**CLEARED.** MU-H1 requires a judgment model for the central question—whether a supplied TODO
marker remains true—and the value improves when the same typed probability/withhold contract is
repeated over a deterministic batch. The candidate does not fail because marker discovery is
extraction; it fails only if discovery or proposition interpretation is delegated to hidden model
generation.

The clearance is conditional on the contract-level repairs in this file:

- deterministic marker enumeration;
- bounded, hashed evidence records;
- exact Noul question and finite verdict semantics;
- mandatory withhold/error path;
- threshold and calibration metadata in the receipt;
- no model-generated marker discovery, summary, or action;
- no deletion without human approval.

The clearance does not claim the demand score exceeds 820, that stale markers are common enough to
matter, that Noul probability is calibrated, that labels are obtainable, or that the tool clears
thin proof or measured lift. Those are later gates. It also does not claim a fixed chat model cannot
be a strong baseline; the calibration and operational delta must be measured.

## Cheapest next structural/proof boundary

Before building a broad product, implement only deterministic marker enumeration plus an injected
Noul over a fixture containing active, fulfilled, obsolete, ambiguous, and unavailable-evidence
markers. The receipt should prove malformed and withhold paths before any live call. A later
falsification design should measure whether the stale/active distribution creates enough operational
lift to justify the repeated judgment cost; that is separate from this rung-2 clearance.

## NO-CLAIM

No MU-H1 implementation or Jev call was run. This file does not prove calibration, semantic truth,
label quality, prevalence of stale markers, installability, cost, or measured lift. It only determines
that the candidate has a valid judgment-model shape if it follows the explicit deterministic
extraction → Noul → local-policy pipeline above.
