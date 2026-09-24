**Version:** `jev-curate` 0.1.0: the crates.io release and `main` at commit `f4c675b` (`src/presets.rs` is the same in both).

**Observed:** with a valid key, `filter` rejects every row under the default preset (`reasoning-math`) and under `code-correctness`. Each rejection reason is an HTTP 422 from `POST /v1/systemone`: the Score question's `criteria` is sent as an object keyed `"1"`..`"5"`, and the API wants a list. The summary reads like a strict filter (`Pass Rate: 0.00%`), so nothing says the requests failed. `anti-sycophancy`, which has only Noul questions, keeps the same row.

**Expected:** Score `criteria` is "an ordered array of level descriptions" ([API reference, Score](https://docs.typesafe.ai/api)). The Python SDK made the same move in v0.6.0 on 2026-09-15: "accept `Score.criteria` as an ordered sequence instead of a dictionary keyed by integers" ([changelog](https://github.com/typesafe-ai/typesafe-sdk-python/blob/main/docs/changelog.md)).

**Why this matters:** the README's own example (`jev-curate filter train.parquet --preset reasoning-math`) and the no-flag default both return an empty clean set, silently, after spending a request per row. A user tuning thresholds or swapping datasets would see the same 0% and could reasonably conclude the data is bad.

**Repro** — fresh clone, one row. Run on Linux x86_64 (`rustc 1.100.0-nightly`):

```bash
git clone https://github.com/AkashPriyadarshii/jev-curate && cd jev-curate
export TYPESAFE_API_KEY=...   # any valid key
printf '%s\n' '{"text":"def square(x):\n    return x * x\n"}' > rows.jsonl

cargo run -q --release -- filter rows.jsonl --preset code-correctness --out out-code
cat out-code/rejected.jsonl
# → Clean Output:    out-code/clean.jsonl (0 rows)
# → {"record":..., "rejection_reasons":["Jev evaluation failed: TypeSafe AI API error: HTTP 422 Unprocessable Entity -
#    {\"detail\":[{\"type\":\"list_type\",\"loc\":[\"body\",\"questions\",\"code_quality\",\"score\",\"criteria\"],
#    \"msg\":\"Input should be a valid list\", ...

cargo run -q --release -- filter rows.jsonl --out out-default      # default preset: reasoning-math
cat out-default/rejected.jsonl
# → Clean Output:    out-default/clean.jsonl (0 rows)
# → the same 422, with loc [..., "reasoning_depth", "score", "criteria"]

cargo run -q --release -- filter rows.jsonl --preset anti-sycophancy --out out-noul
wc -l < out-noul/clean.jsonl
# → 1
```

The same request with curl, where only the shape of `criteria` changes:

```bash
for criteria in '{"1":"Broken","2":"Partial","3":"Working","4":"Clean","5":"Production-grade"}' \
                '["Broken","Partial","Working","Clean","Production-grade"]'; do
  curl -s https://api.typesafe.ai/v1/systemone \
    -H "Authorization: Bearer $TYPESAFE_API_KEY" -H 'Content-Type: application/json' \
    -d '{"model":"jev-latest","state":"def square(x):\n    return x * x\n",
         "questions":{"code_quality":{"type":"score",
           "instructions":"Rate the completeness, idiomacy, and correctness of this code snippet.",
           "criteria":'"$criteria"'}}}'
  echo
done
# → {"detail":[{"type":"list_type","loc":["body","questions","code_quality","score","criteria"],...}]}
# → {..., "answers":{"code_quality":{"type":"score","score":2.83,"confidence":0.86,
#    "legend":{"0":"Broken","1":"Partial","2":"Working","3":"Clean","4":"Production-grade"},...}},...}
```

**Where it comes from:**
- `src/presets.rs:55-61` (`reasoning_depth`) and `src/presets.rs:141-147` (`code_quality`) build `criteria` with `json!({"1": ..., "5": ...})`.
- `src/client.rs:77-81` puts the preset's questions into the request body unchanged.
- `src/filter.rs:89-99` turns the API error into a rejection. Failing closed is the right call for a curation filter; it is also why this surfaces as a 0% pass rate instead of an error.

**What I tried:**
1. `--preset anti-sycophancy` — works, but it has no Score question, so it can't stand in for the code or math presets.
2. The same five descriptions sent as a list (curl above) — HTTP 200.
3. Supplying a corrected rubric — not possible without rebuilding: `--preset` takes a name only (`src/main.rs:32-34`), and the presets are compiled in.

**One more thing to check when fixing the shape:** list positions are 0-based; the 200 response's `legend` runs `"0"`..`"4"`. Both `min_scores` floors are `3.0` (`src/presets.rs:66`, `src/presets.rs:152`), which reads as the key-`"3"` level in the current object ("Sound derivation with standard detail", "Working implementation with minimal edge case handling"). On the returned scale, 3.0 is the fourth description, one level stricter. The README's "`Score` 1–5" (`README.md:39`, `README.md:98`) has the same off-by-one.

**Ask:** send Score `criteria` as an ordered list, and re-read the two 3.0 floors on the 0-based scale the API returns.

**Out of scope:** the fail-closed rejection on an API error. That behaviour is right; this is only about the request shape and the thresholds that depend on it.

**Duplicate check:** `gh issue list --repo AkashPriyadarshii/jev-curate --state all --search "criteria list 422"` and `--search "score criteria"`: no duplicate among the open or closed issues.
