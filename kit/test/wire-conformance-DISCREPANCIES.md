# Wire conformance: divergences and fixture provenance (jev-745g, 2026-10-02)

## Divergences

None known. All clients (askJev, askJevChoice, askJevBundle, rerankTop1, and the
four validators) accept the same recorded-valid responses and refuse the same
hostile mutations (kit/test/wire-conformance.test.mjs 16/16).

## Fixture provenance

Valid rows are recorded jev-1.13.0 responses already in the tree (never typed
for this harness):
- kit/test/fixtures/recorded-answer-rows.json (Choice; consumed via the
  existing RecordedFakeAsker pattern)
- kit/test/fixtures/banking77-answer.json (Choice, 77-class)
- kit/test/fixtures/scifact-answer.json (Noul)
- kit/test/fixtures/sst5-answer.json (Score + legend)
- kit/test/fixtures/rerank-fiqa-answer.json (Choice, 7 candidates)

Hostile rows are derived boundary mutations of those recordings (choice moved
outside ids, probabilities rescaled off 1.0, chosen-below-max, NaN/Infinity/
out-of-range/type-swapped scalars, dropped keys, missing answers). Synthetic
data stands in only for the hostile path, never for the valid path.

## Out of scope (not a divergence)

- work/jev-client is a cutover stub (all callers import kit directly).
- .omp hook askers (webscreen, skill-hint) call kit entry points with the live
  key and offer no injection seam; their validation is kit's, covered here.
