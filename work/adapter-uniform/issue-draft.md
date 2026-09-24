## What happened

With `system-one-adapter` 0.2.1 (also 0.2.0) in `llm_answer_mode="probabilities"`, a model
output whose Choice probabilities are all `0` comes back as a normal, successful answer: `choice`
is the first criterion, `confidence` is `0.0`, and with `normalize_probabilities=True` every option
reads `1/n`. Nothing is raised and no corrective retry is spent. The Score twin returns the middle
level. The only trace is `response.debug["probability_errors"][<question id>] == 1.0`.

This happens on real inputs. Claude Haiku 4.5 through `provider="anthropic"` with
`structured_outputs=True` returns all-zero maps. One raw `content[0].text` (stop reason
`end_turn`, 10 options):

```json
{"answers":{"intent":{"activate my card":0,"age limit":0,"apple pay or google pay":0,"atm support":0,"automatic top up":0,"balance not updated after bank transfer":0,"balance not updated after cheque or cash deposit":0,"beneficiary not allowed":0,"cancel transfer":0,"card about to expire":0}}}
```

Measured with one 10-option Choice question over Banking77 test messages: 58 of 70 calls came back
all-zero on 14 messages that had come back uniform in an earlier run (5 calls each), against 1 of
70 on 14 other messages with the same labels. All 59 answers were the first option at confidence 0.

## Repro

No key and no model call. `bash`, macOS arm64, Python 3.14 (resolved by `uv` 0.9):

```bash
mkdir -p /tmp/allzero && cd /tmp/allzero
cat > repro.py <<'EOF'
import json

from typesafe_sdk import Choice

from system_one_adapter import SystemOneAdapterClient
from system_one_adapter.providers import ProviderResult

LABELS = ["refund", "shipping", "billing"]


class CannedProvider:
    """A custom provider returning one fixed model output."""

    model_name = "canned"

    def __init__(self, distribution):
        self.text = json.dumps({"answers": {"topic": distribution}})
        self.calls = 0

    def request(self, messages, *, schema, structured):
        self.calls += 1
        return ProviderResult(text=self.text, input_tokens=0, output_tokens=0)

    def translate_error(self, error):
        return error


question = {"topic": Choice(instructions="Ticket topic", criteria=dict.fromkeys(LABELS))}

for label, distribution, normalize in [
    ("model returned all zeros", dict.fromkeys(LABELS, 0.0), True),
    ("model returned all zeros", dict.fromkeys(LABELS, 0.0), False),
    ("model returned 1/3 each", dict.fromkeys(LABELS, 1 / 3), True),
]:
    provider = CannedProvider(distribution)
    with SystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=normalize,
        n_retry_malformed_structure=2,
    ) as client:
        response = client.system_one({"ticket": "x"}, question, model=provider)
    answer = response.answers["topic"]
    print(
        f"{label:26} normalize={normalize!s:5} calls={provider.calls} "
        f"choice={answer.choice!r} confidence={answer.confidence} "
        f"probabilities={ {k: round(v, 3) for k, v in answer.probabilities.items()} } "
        f"probability_errors={response.debug['probability_errors']}"
    )
EOF
uv run --no-project --with system-one-adapter==0.2.1 python repro.py
```

Output (`typesafe-sdk` 0.7.1 resolved):

```text
model returned all zeros   normalize=True  calls=1 choice='refund' confidence=0.0 probabilities={'refund': 0.333, 'shipping': 0.333, 'billing': 0.333} probability_errors={'topic': 1.0}
model returned all zeros   normalize=False calls=1 choice='refund' confidence=0.0 probabilities={'refund': 0.0, 'shipping': 0.0, 'billing': 0.0} probability_errors={'topic': 1.0}
model returned 1/3 each    normalize=True  calls=1 choice='refund' confidence=0.0 probabilities={'refund': 0.333, 'shipping': 0.333, 'billing': 0.333} probability_errors={}
```

## Expected vs observed

```diff
- expected: a model output that assigns no probability to any option is not returned as an
-           answer (it is surfaced as an error, or counts against n_retry_malformed_structure)
+ observed: choice='refund' (option #1), confidence=0.0, calls=1, no exception, in both
+           normalize_probabilities modes; answers identical to a model-asserted uniform
```

## Workarounds tried

1. `normalize_probabilities=False`: still `choice='refund'`, `confidence=0.0`, no exception
   (repro line 2); only the probabilities stay `0.0`.
2. `n_retry_malformed_structure=2`: one provider call (`calls=1`). Each value is inside `[0, 1]`,
   so the output validates and no retry happens.
3. Reading `response.answers` only: identical to a model-asserted uniform (repro lines 1 and 3).
   Only `debug["probability_errors"]` or `debug["original_probabilities"]` tell them apart.
4. Score has the same shape: an all-zero map over 3 levels returns `score=1.0` (the middle level)
   at `confidence=0.0` with `normalize_probabilities` `True` or `False`, because the score is
   always computed from a rescaled copy.

## Root cause

All citations at commit `e1d4cc9` (tag v0.2.1), `src/system_one_adapter/`:

- `_utils/probability_normalization.py:100-106`: the model's values are read as-is; a zero total
  gives `error = 1.0`, and with normalization on, `rescale_probabilities` is called.
- `_utils/probability_normalization.py:70-72`: `rescale_probabilities` has a zero-total branch that
  returns `1/len(probabilities)` for every option. Its docstring (`:58`) names this fallback; the
  README describes the option as "Rescale invalid LLM probability distributions to sum to 1",
  and a zero vector has no scale to preserve.
- `_client.py:159`: `max(answers, key=probabilities.__getitem__)` returns the first option on a
  tie, so an all-zero or uniform vector always answers option #1.
- `_utils/confidence_metrics.py:22-24` with `:27-32`: confidence normalizes a zero total to uniform
  and reports `0.0`.
- `_client.py:141-142`: the Score path always rescales (`rescale_probabilities`) before taking the
  expected value, so the substituted uniform becomes the middle level regardless of the option.
- `_schema.py:25`: `Probability = Annotated[float, Field(ge=0, le=1)]` bounds each value but not
  the total, so `_client.py:222-231` (`_decode_or_correct`) accepts the output and the corrective
  retry never triggers.

I see why the uniform fallback exists: it keeps the arithmetic total-free. The trouble is where
it lands: "the model gave no option any probability" becomes "the model picked option #1, weakly".

## Independent confirmation

Live numbers: one model and provider, macOS arm64. The repro is provider-free, on the published
wheel.

## Why this matters

Choice is the routing primitive. A caller reading `choice` routes every such message to whichever
option is listed first, and accuracy computed from `choice` counts it as that option. Score reports
a mid-scale value the model never gave. A `confidence` gate does catch these rows, but cannot tell
them from a model-asserted uniform without reading `debug`.

This is the same shape as #38, where an incomplete provider output was returned as a successful
evaluation and v0.2.1 now rejects it.

## Constructive ask

Make the zero-total case distinguishable outside `debug`. One option that reuses existing
machinery: treat a probability map with no mass as malformed output, so it raises
`TypeSafeAPIResponseValidationError` by default and a caller who sets
`n_retry_malformed_structure` gets a corrective retry. You may prefer a different shape; the
ask is only that `choice` not name an option the model gave zero probability.

## Out of scope

- Rescaling of non-zero invalid totals (e.g. 0.6 to 1.0); that behaviour looks right.
- The model's own tendency to return all zeros; that is provider behaviour and outside this repo.
- `llm_answer_mode="discrete"`; not exercised here.

## Duplicate check

Searched this repo with `gh issue list --repo typesafe-ai/system-one-adapter-python --state all
--search` for `uniform`, `zero probabilities`, `normalize`, `all zero`, `rescale`,
`confidence 0`, and `probability sum`, and read the full issue and PR lists (8 issues, 32 PRs,
2026-09-24). No duplicate found; the nearest is #38 (truncated output accepted as success), a
different mechanism in the provider layer.
