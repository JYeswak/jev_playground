# X2 Clef-Flash vs Jev receipt

```json
{
  "prereg_sha256": "8e81c8e2246eef7b4915828691c6d9df49dab150ed8d1c3208b57dd38ea5de16",
  "split_sha256": "1c047b20eb31eebb0f1b39e5e7b0a5f406eff35805e66dc6118a69d4d33f3dfe",
  "suites": [
    {
      "assumed_discordance": 0.2,
      "clef_calls": 0,
      "dev_n": 449,
      "held_n": 898,
      "margin": 0.05,
      "minimum_metric_power": 0.9559512094428566,
      "planned_n": 1347,
      "status": "POWERED",
      "suite": "injection"
    },
    {
      "assumed_discordance": 0.2,
      "clef_calls": 0,
      "dev_n": 149,
      "gate_sample_context": {
        "jev_command_projection": "commandViewChars prefix; historical Jev input differs from full original on 296/396 rows",
        "random_unflagged_stratum": {
          "label_provenance": "two local LLM labelers; not independently human-verified",
          "labelled_harms": 0,
          "n": 200,
          "one_sided_95_upper_harm_rate": 0.014867,
          "weighted_recall_lower_bound": 0.679956
        },
        "recorded_jev_catches": "47/47 conditional on the Jev-flagged stratum; not gate-wide recall",
        "sample_scope": "Jev-flag-stratified, 396-row command projection",
        "source": "work/x7-gate-rules/RECEIPT.md"
      },
      "held_n": 247,
      "margin": 0.05,
      "minimum_metric_power": 0.5446972040964657,
      "planned_n": 396,
      "status": "DESCRIPTIVE",
      "suite": "gate"
    }
  ]
}
```
