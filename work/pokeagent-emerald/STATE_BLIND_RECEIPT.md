# Emerald state-blind control receipt

```json
{
  "policy": "state_blind",
  "model_calls": 0,
  "key_status": "NOT_APPLICABLE",
  "seed_count": 80,
  "seed_start": 0,
  "seed_end": 80,
  "start_macro": 228,
  "macro_cap": 500,
  "goal": {"location_not": "MOVING_VAN"},
  "goals_reached": 0,
  "failures_at_cap": 80,
  "success_rate": 0.0,
  "median_capped_macros": 500.0,
  "p95_capped_macros": 500,
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
  "runner_code_sha256": "ee7cfd6a64ac6cb16bcee148838a69a0c631482535d2034500626584f081ad47",
  "harness_sha": "62bf6f614b66ff76b79954e5a3f04f91c3c6a049",
  "rom_sha1": "f3ae088181bf583e55daf962a92bb46f4f1d07b7",
  "results_sha256": "3ce1e107a0a351e221840ff7271f15581966fc606722c07b473dc68de4ee0b8f",
  "rom_path": "/Users/josh/Library/Application Support/jev-roms/pokeemerald.gba",
  "command": "uv run python work/pokeagent-emerald/run_baselines.py --rom /Users/josh/Library/Application Support/jev-roms/pokeemerald.gba --output work/pokeagent-emerald/state-blind-results.jsonl --fixed-sequence 0 --random 0 --state-blind 80 --pooled-rows work/pokeagent-emerald/live-results.jsonl --cap 500 --harness-sha 62bf6f614b66ff76b79954e5a3f04f91c3c6a049 --rom-sha1 f3ae088181bf583e55daf962a92bb46f4f1d07b7"
}
```

The 80 emulator runs used seeds `0..79`, the fixed macro-228 start, a 500-macro cap, and
only the goal predicate above. Each macro was sampled with replacement from the 6,449 pooled
button entries; emulator state was not used for selection. This is a keyless control, not a
Jev call or an LLM comparison. All 80 runs stopped at the cap without leaving the truck.
