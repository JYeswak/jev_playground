# Can a free OpenRouter model carry an incumbent arm? SST-5 through system-one-adapter (bead `jev-14qk`)

MaintFixes (background agent of pane 1), 2026-09-24. Live lane, $0: free models only.

## Preregistered (committed before the first call)

**Why.** The Anthropic account cap (`jev-1y19`: "You have reached your specified API usage
limits", until 2026-10-01) removed the Haiku incumbent from every live unit. The direct OpenAI key
returns 401. Pane 1 smoke-tested four free OpenRouter models, one call each. Two came back with
upstream 429, one returned no choices, and `nex-agi/nex-n2.5-pro:free` returned valid JSON in 5.1 s.
Our variance units fail an arm on more than 1% failed rows. Before any free model stands in for an
incumbent, this unit measures whether it can answer every row. It does not measure whether it
answers well.

**How OpenRouter enters the incumbent path.** OpenRouter speaks the OpenAI Chat Completions API. It
enters as the adapter's own `AsyncOpenAIProvider(model, base_url="https://openrouter.ai/api/v1",
api="chat_completions")`, passed as `model=` to `AsyncSystemOneAdapterClient.system_one`, which the
adapter supports as a caller-owned provider. No adapter code is edited or forked.
`work/openrouter/provider.py` builds it and refuses two cases: a model id that does not end in
`:free`, and an unset `OPENROUTER_API_KEY`. The key comes from the lane Infisical project. Only its
length was checked (73). Offline test with no key and no network: `python -m unittest
work/openrouter/test_provider.py`, 4/4. It turns red when the provider is planted with
`api="responses"` or without the `:free` guard.

**What runs.** Everything matches the `jev-zui` Haiku arm: the committed SST-5 Score question
(`work/score-sst5/run.py`, `QUESTION`, imported rather than copied), `structured_outputs=True`,
`llm_answer_mode="probabilities"`, `normalize_probabilities=True` and `RetryPolicy()`. The
RetryPolicy retries 408, 429 and 5xx up to 2 times with backoff, honours Retry-After, and times out
each attempt at 30 s. Only the provider changes. Rows are the first 50 of
`work/score-sst5/sample.jsonl`, public SST-5 test sentences; nothing from this repo's sessions is
sent. The six `:free` models the bead names:

| Model | Listed support on `/api/v1/models` (2026-09-24) |
|---|---|
| `google/gemma-4-31b-it:free` | response_format (not structured_outputs) |
| `qwen/qwen3.8-27b:free` | structured_outputs (not response_format) |
| `nvidia/nemotron-3-super-120b-a12b:free` | both |
| `nex-agi/nex-n2.5-pro:free` | both |
| `dots-studio/dots-3-note-preview:free` | both |
| `google/gemma-4-26b-a4b-it:free` | response_format (not structured_outputs) |

The models run one after another, 2 requests at a time, with 180 s per call including retries.
There is one pass per model; failed rows are not re-run, because a model that needs re-runs to
answer does not meet the bar.

**Recorded per row** (`work/openrouter/rows-sst5-<model>.jsonl`): the answer, or the exception
class and message verbatim; the upstream provider OpenRouter reports (`provider` in the last
attempt's response); the finish reason; the attempt count; the adapter's retry reasons; latency;
tokens; and the adapter's `probability_errors` and `original_probabilities`.

**Scorer, keyless:** `python3 work/openrouter/score_feasibility.py`. It reads only the row files
and `sample.jsonl`, and uses `jev-zui`'s own rounding. It exits 1 while any model's rows are
missing.

**Bar, per model.** A model **can carry a 500-row arm** only if it answers **50/50** here with
**0 zero-mass rows**, where zero-mass means a raw probability map summing to 0 that the adapter
fills in as uniform (`jev-mly`). The 1% bar allows 5 failures in 500. A model that fails even 1
row in 50 is expected, at that rate, to fail about 10 rows in 500, which is over that bar. A model
that misses the bar is reported as NOT FEASIBLE, with its failure classes verbatim. Accuracy and
MAE on 50 rows are printed but decide nothing.

**Stated before running:** 300 calls plus the adapter's retries, all to `:free` ids, so $0.
[INFERENCE] The key is on a paid account, so OpenRouter's free-model daily cap is the higher tier.

**NO-CLAIM.** One pass per model, 50 rows, one evening, one wording. Free endpoints are shared, and
their limits change by the hour. A model that passes here is feasible tonight, not reliable in
general. No quality comparison with Jev or Haiku is made or implied.

## Results

Pending the live run.
