# Can a free OpenRouter model carry an incumbent arm when the harness is paced? (bead `jev-3e2i`, run 2 of `jev-14qk`)

GreenForest (background agent of pane 1, hub id FreeModelScout), 2026-09-24. Live lane, $0: `:free`
model ids only. No Anthropic model, no TypeSafe/Jev call (AGENTS.md, "No Anthropic API spend on
comparisons").

## Preregistered (committed on its own, before the first call)

**Why a second run.** Joshua stopped Anthropic API spend on comparisons on 2026-09-24, so Haiku no
longer serves as the incumbent. `jev-14qk` (`5498c91` bar, `7840279` rows,
`openrouter-free-feasibility-20260924.md`) found no free model that answered 50/50. Its failures
were mostly `429 Rate limit exceeded: free-models-per-min` and `429 Provider returned error` (all
150 failures of the two gemma models and qwen), plus `TimeoutError` (19 nemotron, 9 nex). nex had a
p95 of 151 s against a 180 s whole-call cap. That pattern points at how the harness paced its
requests (2 in flight, the adapter's 30 s retry budget with at most 5 s backoff), not
necessarily at the models. This run changes only the pacing and measures the same thing again.

**Unchanged from `jev-14qk`.** Same question: the committed SST-5 Score question
(`work/score-sst5/run.py`, `QUESTION`, imported). Same rows: the first 50 of
`work/score-sst5/sample.jsonl`. Same adapter settings: `structured_outputs=True`,
`llm_answer_mode="probabilities"`, `normalize_probabilities=True`. Same provider:
the adapter's own `AsyncOpenAIProvider` at `https://openrouter.ai/api/v1`, `chat_completions`, built
by `work/openrouter/provider.py`. Same scorer logic: `work/openrouter/score_feasibility.py`, with
a `--run2` flag that only switches which row files and model list it reads. One pass per model.
Failed rows are not re-run.

**Same bar.**

- A model **can carry a 500-row arm** only if it answers **50/50** with **0 zero-mass rows**.
  Zero-mass means a raw probability map that sums to 0 and that the adapter fills in as uniform
  (`jev-mly`).
- The **`jev-3e2i` comparator gate** is **>=49/50 answered**.
- Accuracy and MAE on 50 rows are printed but decide nothing.

**The only harness changes, and why each one is made.** They sit behind `--paced` in
`work/openrouter/run_sst5.py`. Without the flag the runner behaves exactly as it did in `jev-14qk`.

1. **One model at a time, concurrency 1 (was 2).** With two requests in flight, the per-minute
   request count doubles against the account's free-model per-minute limit. That limit produced
   the dominant failure class.
2. **At most 15 requests per minute from this process.** This is a sliding 60 s window, counted
   at the provider seam, so adapter retries and every other HTTP request count too. Why: OpenRouter
   limits free-model requests per minute per account, and `GET /api/v1/key` does not report that
   limit. [INFERENCE] The published figure is 20/min. 15 leaves headroom, and other panes may share
   the key. The pacer cannot see requests from other processes on the same key.
3. **Per-attempt timeout 120 s.** This is enforced at the provider seam and raised as the SDK's
   `TypeSafeAPITimeoutError`. Why: nex's answered p50 was 64 s and p95 151 s. A slow but valid
   answer is feasibility evidence, not a failure. The whole-call cap rises from 180 s to 420 s
   (pacer wait excluded) so that it can never cut a 120 s attempt that follows an adapter retry.
   The call is still bounded.
4. **429 handling moves from the adapter to the runner.** 429 is removed from the adapter
   `RetryPolicy`'s retried statuses. Everything else in `RetryPolicy()` is unchanged: 408 and 5xx,
   up to 2 retries, the 30 s budget. On a 429 the runner waits the server's `retry-after-ms` or
   `Retry-After`, or **60 s** when neither is sent, then re-sends the row. It waits **at most 3
   times per row**. A 4th 429 fails the row with that 429 recorded verbatim. Why: a per-minute
   limit cannot clear inside the default policy's 30 s budget and 5 s maximum backoff. In
   `jev-14qk` every retry of those rows landed inside the same limited minute.

**Guards (in code, before any request).**

- Every request passes through one wrapper that refuses any model id not ending in `:free`, before
  the HTTP call. This check sits on top of `provider.openrouter_provider`'s construction-time
  refusal.
- There is a process-wide cap of **599 HTTP requests** (under 600). When it is reached, the run
  stops and the remaining models are reported as not run.
- **5 consecutive failed rows of the same class** stop that model. Its remaining rows count as
  failed (not attempted), and the stop is reported.
- `GET /api/v1/key` `usage_daily` is recorded before and after the run. A rise of more than
  $0.001 is reported as a spend incident.
- Keys come only through `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`
  and are never printed.

**Models, in run order.** These are the 8 `:free` ids pane 1 listed with structured output. The
support column is re-read from the public `GET /api/v1/models` before this commit (2026-09-24). All
8 are priced 0/0.

| # | Model | `structured_outputs` / `response_format` listed now |
|---|---|---|
| 1 | `dots-studio/dots-3-note-preview:free` | yes / yes |
| 2 | `nex-agi/nex-n2.5-pro:free` | yes / yes |
| 3 | `nvidia/nemotron-3-super-120b-a12b:free` | yes / yes |
| 4 | `nex-agi/nex-n2.5-mini:free` | yes / yes |
| 5 | `liquid/lfm-2.5-2.6b:free` | yes / yes |
| 6 | `qwen/qwen3.8-27b:free` | yes / no |
| 7 | `google/gemma-4-31b-it:free` | no / yes |
| 8 | `google/gemma-4-26b-a4b-it:free` | no / yes |

The order puts the three models that answered in `jev-14qk` first, so the request cap cannot
starve them.

**Recorded per row** (`work/openrouter/rows-sst5-<model>-run2.jsonl`; the `jev-14qk` row files stay
untouched): the same fields as `jev-14qk`, plus these:

- `rateLimitWaits`, the number of 429 waits;
- `waitMs`, the total 429 wait;
- `pacerWaitMs`, the time held by the 15/min pacer;
- `requests`, the HTTP requests this row made.

`latencyMs` is the duration of the row's last `system_one` call, with the pacer wait subtracted.
Like `jev-14qk`'s, it includes adapter retries.

**Scorer, keyless:** `python3 work/openrouter/score_feasibility.py --run2`.

**Stated before running:** at least 400 requests, and at most 599. All go to `:free` ids, so the
cost is $0. At 15/min and the latencies above, [INFERENCE] the run takes 1-3 hours.

**NO-CLAIM.** One paced pass per model: 50 rows, one day, one wording. Free endpoints are shared
and their limits change by the hour. A model that passes is feasible today under this pacing, not
reliable in general. No quality comparison with Jev or Haiku is made or implied.

## Results

Pending the live run.
