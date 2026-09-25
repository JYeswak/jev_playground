# Emerald state-blind control receipt

```json
{
  "status": "OK",
  "policy": "state_blind",
  "model_calls": 0,
  "key_status": "NOT_APPLICABLE",
  "runtime_image": "jev-pokeagent-runtime:20260925",
  "runtime_image_id": "sha256:6eb7091484bf328ffa42e643bbeefcd2d0f71998039b40dd7a229d86e5f31ad6",
  "harness_sha": "62bf6f614b66ff76b79954e5a3f04f91c3c6a049",
  "rom_sha1": "f3ae088181bf583e55daf962a92bb46f4f1d07b7",
  "seed_count": 80,
  "seed_start": 0,
  "seed_end": 80,
  "start_macro": 228,
  "macro_cap": 500,
  "goal": {"location_not": "MOVING_VAN"},
  "goals_reached": 80,
  "failures_at_cap": 0,
  "success_rate": 1.0,
  "median_capped_macros": 67.0,
  "p95_capped_macros": 188,
  "max_macros": 338,
  "pooled_source": "work/pokeagent-emerald/live-results.jsonl",
  "pooled_source_sha256": "5294ec9a24319ebc7c528cdb3076c11bc381df3e1abbbb4334a6bf36c97c84fa",
  "pooled_source_rows": 6449,
  "pooled_button_counts": {
    "A": 531,
    "B": 74,
    "DOWN": 628,
    "LEFT": 591,
    "R": 67,
    "RIGHT": 1872,
    "SELECT": 20,
    "START": 293,
    "UP": 1649,
    "WAIT": 724
  },
  "runner_code_sha256": "1026758316e9ba49064599593e00071bc07f8ba014cd8c38eb818a01dbb63af3",
  "results_sha256": "99615e0db9d5148ed360b20782e326b2a39b10ea343df15a252abcbcb730645e",
  "command_shape": "docker run --platform linux/arm64 jev-pokeagent-runtime:20260925 with harness @62bf6f6 mounted in PYTHONPATH; run_baselines.py --fixed-sequence 0 --random 0 --state-blind 80 --cap 500 --seed-offset 0"
}
```

All 80 rows have a final emulator state, `scored: true`, and no `child_error`. Every seed used
the same macro-228 start, 500-macro cap, and `location != MOVING_VAN` goal. Each macro was
sampled with replacement from the 6,449 pooled button entries; emulator state was used only for
goal detection and stopping. This is a keyless emulator control, not a Jev call or an LLM
comparison.
