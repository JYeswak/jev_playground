# Lesson-class Clef-Flash bake-off preregistration

Bead: `jev-dadu` · frozen before first Clef request.

## Data and labels

Use exactly the 622 reviewer-labelled rows in
`/Users/josh/Developer/omp-test/var/agent-tmp/planning-retro/findings-{omp-kit,localbench,cfsios,uds}.jsonl`.
Exclude `findings-jev.jsonl` because its labels were heuristic. Collapse every
`OTHER:<slug>` label to `OTHER`. The offered set is, in this fixed order:
`SCOPE_GAP`, `FALSE_CLAIM`, `MISSING_EDGE`, `PRIORITY`,
`PINNED_LIVE_VALUE`, `UNDEFINED_TERM`, `STALE_TEXT`, `CYCLE`, `DUPLICATE`,
`OVERSCOPE`, `OTHER`.

## Split

Seed `20261005`. Stable row id is SHA-256 of `source_filename + ":" + line_number`.
Within each source repo, shuffle sorted row ids with Python `random.Random(seed)`;
assign alternating rows to dev and held-out. This yields a deterministic,
source-stratified near-50/50 split. All incumbents and any rule vocabulary use
dev labels only. Clef sees finding text only; held-out labels are not in the
request state.

## Arms

- **Majority:** most frequent dev class; ties break by offered-class order.
- **Keyword rule:** on dev only, count normalized whitespace tokens by class.
  At prediction, sum each token's dev counts per class and select the largest;
  ties break by offered-class order; no seen tokens selects dev majority.
- **Clef-Flash:** one Choice request per held-out finding to local
  `http://127.0.0.1:8010/v1/systemone`, model `clef-flash`, with the ordered
  offered set above. `state` contains only the finding; instructions ask for
  the single best canonical process-finding class. No remote service or paid
  model.

## Frozen bar

On held-out rows, Clef must have both accuracy and macro-F1 strictly greater
than the dev-fitted keyword rule, and two-sided exact McNemar p < 0.05 on
paired accuracy disagreements. Otherwise verdict `LOSES`. No post-hoc changes.
Majority is a separately reported incumbent, not a substitute threshold.

## Bounds, privacy, and refusal

Maximum 700 calls, one per held-out row; no retries; stop at the first
connection or HTTP error. Before running, `scripts/local-model-guard.sh` must
pass and execution is `nice -n 10`. Validate the response class is offered,
probabilities are finite in [0,1] and sum to 1 within 0.02, and chosen class
is a maximum-probability option; invalid answers count `NOT_SCORED` and never
become a guess. Log row id, class options, answer, probabilities, latency,
model, and status. Never log finding text; include only its SHA-256. Local
Clef spend is $0.

No claim beyond this pool and split. Any result is shadow evaluation only;
not a deployed second pass and not proof on future fleet findings.
