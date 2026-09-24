# Draft — do not file

Title: Score `criteria` is sent as a `"1"`..`"5"` object; the API requires an ordered list

Repo: `AkashPriyadarshii/jev-curate` @ `d1a3a0505700da10341fa37d79a61151179a892e`

## What happens

`code-correctness` and `reasoning-math` send Score `criteria` as a JSON object keyed `"1"`..`"5"` (`src/presets.rs:141-147`, `src/presets.rs:55-61`). `POST /v1/systemone` with `model: jev-1.13.0` returns HTTP 422:

```
{"detail":[{"type":"list_type","loc":["body","questions","code_quality","score","criteria"],"msg":"Input should be a valid list"}]}
```

The same error names `reasoning_depth.score.criteria` for the reasoning preset. Noul `criteria` as `{true, false}` is not the failure.

On 2026-09-23 a binary run of `--preset code-correctness` over 30 QuixBugs rows rejected all 30 with that 422. Zero scores reached `src/filter.rs`.

## Whose shape is wrong

The clone's. Current contract:

- https://docs.typesafe.ai/primitives/score — `criteria` is an ordered array. A level's number is its position, starting at 0.
- TypeSafe Python SDK `Score.criteria` is a `Sequence`, "one per score from zero". Changelog v0.6.0: accept an ordered sequence instead of a dictionary keyed by integers.

Sending the same five strings as a list, through `typesafe-sdk` `Score`, model `jev-1.13.0`, on those same 30 rows: 30/30 HTTP 200. Response legend keys were `[0, 1, 2, 3, 4]`. Scores were 0.98–2.03, an expected index on that 0-based scale, not an integer 1–5.

## Second bug, visible only after the 422 is fixed

`src/presets.rs:152` sets `code_quality` minimum to `3.0`. `src/filter.rs:132` rejects when `score < 3.0`. On the 30 scored rows every raw score was below 3.0, so the filter would still reject 30/30. The 3.0 floor assumes the `"1"`..`"5"` keys are the number Jev returns. They are not. Level 0 is the first description.

A post-hoc `score + 1` reading is not a fix to ship without a new labelled check. It is only evidence that the threshold and the wire scale disagree.

## Suggested change

Serialize Score `criteria` as a list, low end first. Keep Noul `criteria` as `{true, false}`. Re-read `min_scores` against the 0-based expected index, and say so in the README. Do not treat a 422 as a low score.

Not filed from the jev lane. The vendored clone is read-only.
