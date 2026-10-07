# Time-window replication receipt

**Verdict: PASS**

Frozen window: 2026-10-02T22:00:00Z to 2026-10-04T22:00:00Z (end exclusive).

Primary bar: Jev must have the same held referenced-drop count as the held-matched baseline and strictly greater savings on held unreferenced rows.

Secondary original bar is reported separately. Weekly tokens are scaled from the 48-hour labelable-result rate; this is an estimate, not a deployment claim.

No claim beyond the preregistered temporal population. The report contains no result text.

```json
{
  "calls_with_usage": 200,
  "corpus_sha256": "706754624f46db70bb92fc1ced3aea8491911d945a631bb07b989a5974930a33",
  "dev_rows": 100,
  "fallback_keeps": 0,
  "held_matched": {
    "miss_rate_held_rows": 0.11,
    "miss_rate_referenced": 0.25,
    "reference_drops": 11,
    "savings_chars": 429328,
    "savings_row_units": 6.0,
    "wilson_95_held_rows": [
      0.06254196357064568,
      0.18631296503080313
    ],
    "wilson_95_referenced": [
      0.14574213828964888,
      0.3944056635895915
    ]
  },
  "held_matched_miss_count_equal": true,
  "held_matched_savings_ratio": 1.752878917750531,
  "held_matched_threshold_chars": 50955,
  "held_referenced": 44,
  "held_rows": 100,
  "held_unreferenced": 56,
  "input_tokens": 148990,
  "jev": {
    "miss_rate_held_rows": 0.11,
    "miss_rate_referenced": 0.25,
    "reference_drops": 11,
    "savings_chars": 752560,
    "savings_row_units": 29.64014478429976,
    "wilson_95_held_rows": [
      0.06254196357064568,
      0.18631296503080313
    ],
    "wilson_95_referenced": [
      0.14574213828964888,
      0.3944056635895915
    ]
  },
  "median_latency_ms": 187.0,
  "model": "jev-1.13.0",
  "observed_spend_usd": 0.006258,
  "original_bar_pass": false,
  "primary_advantage": true,
  "rows_sha256": "86a6d02ab9f2965df57f7039c07ee64fbf0ed4f2fa20bac307c7565ccc66d3c7",
  "scored_calls": 200,
  "spend_complete": true,
  "total_calls": 200,
  "verdict": "PASS",
  "weekly_tokens_saved_held_matched": 2384917,
  "weekly_tokens_saved_jev": 4180471,
  "weekly_tokens_saved_youden": 4419858,
  "weekly_volume_estimate": 2222,
  "youden_baseline": {
    "miss_rate_held_rows": 0.13,
    "miss_rate_referenced": 0.29545454545454547,
    "reference_drops": 13,
    "savings_chars": 795654,
    "savings_row_units": 15.0,
    "wilson_95_held_rows": [
      0.07757167427240512,
      0.20980351440076428
    ],
    "wilson_95_referenced": [
      0.1815552911850489,
      0.44220200126160236
    ]
  },
  "youden_threshold_chars": 34175
}
```
