# Duel-1 blind-spot probe: what both duelists missed

Bead: `jev-demo-loop-a1q`
Role: third-lineage probe after reading both idea files, the cross-scores, and the
Claude reaction
Grounding: `docs/demos/USAGE-MAP.md` at its pinned SHAs

I read the full MUSE inventory, including its top five, winnowed items, and source
refusals, plus the full Claude 15-item inventory and top-five rationale. I also read
`WIZARD_SCORES_MU_ON_CC.md` and `WIZARD_REACTIONS_CC.md`. The candidate below does not
appear in either file's top list, long list, winnowed list, or refusal list.

## Blind spot 1 — continuous review signal hook alongside ubs

**Usage Map §5, `jev-review@57690af`.** The map says Jev provides one local MCP tool
with scalar scores across correctness, complexity, changeability, modularity, tests,
and security; the key stays on the machine and there is no backend. Its explicit demo
angle is a review-signal hook as an advisory input alongside ubs
(`docs/demos/USAGE-MAP.md:41-45`).

### Why this matters

This is an important gap between the two duelists' categories. MU-3 proposes a completion
judge at bead close, and both files propose claim checking. Those are discrete decisions
about done-ness or cited numbers. Neither proposes a continuous, advisory code-review
signal that runs before the close decision and gives the operator a multidimensional risk
vector. The lane already has gates and hooks, but most are binary or form-oriented; a
signal can tell the operator *why* a diff deserves another look without pretending that
Jev is the final oracle.

Both models likely missed it for different but compatible reasons:

- **Decision bias:** both ranked ideas by a decision immediately in flight. MU emphasized
  compaction, routing, and bead completion; Claude explicitly weighted “does it change a
  decision this week.” A review signal is a recurring input to many decisions, so it
  looked less like one decisive demo.
- **Existing-tool shadow:** `ubs` already occupies the word “review,” making the idea look
  like a duplicate. The map's distinction is scalar, multidimensional advisory evidence
  alongside ubs, not a replacement for static scanning or a new blocking gate.
- **Artifact bias:** both duelists preferred ideas with a sharp trigger/refusal story.
  An advisory signal needs a calibration and human-follow-up story; that is less flashy
  than a contradicted claim or an empty transcript RED arm, but it is closer to the
  actual daily operator loop.

This is not a claim that `jev-review` is correct for our diffs. It is the missing demo
that tests whether the review signal complements ubs without adding another opaque
blocking stage.

### Four ship artifacts

- **Install:** one idempotent command registers a local review-signal hook or installs
  `jev-review-signal` beside the existing ubs invocation. It must remain advisory by
  default, preserve the current fail-open/no-key workflow, and report the exact diff
  revision and Jev model version. No daemon or backend.
- **Deterministic tests with RED arms:** use an injected asker and fixed fixtures:
  (1) a known security/correctness regression must emit a low score or `human-needed`,
  and forcing a clean pass is RED; (2) an empty diff must return an explicit ERROR,
  never a reassuring score; (3) malformed or incomplete dimensions must produce a
  named `SIGNAL_UNAVAILABLE` result and execute no policy action; (4) a clean, tested
  diff must not be auto-promoted to “safe”—the advisory output must preserve the
  human-review boundary. Add a bypass RED arm proving the detector is not merely
  echoing fixture labels.
- **Receipt:** record diff SHA, changed-file set, ubs result reference, each review
  dimension and confidence, model version, threshold/policy version, latency, and
  whether a human follow-up was requested. The receipt must distinguish a signal from
  a verdict and must not contain source secrets.
- **EVAL row:** cite `jev-review@57690af` and the license, name the local process rung,
  compare the signal against ubs and human review on a bounded corpus, and state the
  Boundary: no claim of defect detection, no automatic close, and no evidence that a
  scalar score is calibrated until a labelled review set exists.

### Why it should not become a new blocking gate immediately

The first demo should answer “does this improve review triage?” not “can Jev authorize
merges?” A signal that blocks commits would collide with the paid-API and malformed-answer
failure modes already documented elsewhere in the duel. Keep the policy mapping in local
code, but make its initial action `advisory` or `human-needed`; promote it only after a
receipt-backed false-positive/false-negative review set exists.

## Scope boundary

I found no second candidate that satisfies the same standard without duplicating an
existing file entry. Usage Map §3 reranking, §7 failure attribution, §8 commit triage,
§11 policy gating, §12 blind security benchmarks, and §13 calibration are all present in
one of the two idea inventories or their refusals/winnowing. Browser action selection
(§10) is explicitly marked “none immediate” by the map and is not a useful near-term
blind spot for this lane.

**NO-CLAIM:** I did not implement or run `jev-review`, an ubs integration, any proposed
fixture, or a live review hook. This is a grounded omission finding and ship sketch, not
an evaluation of the upstream tool or a measured recommendation.
