# Emerald state-blind control receipt — NOT SCORED

**This artifact is an infrastructure-failure receipt, not a baseline result.** It supersedes the
prior `STATE_BLIND_RECEIPT.md` claim in commit `8fd7628d`. The native `uv` invocation could not
import the PokeAgent harness (`ModuleNotFoundError: No module named 'pokemon_env'`) in any child.
No row reached the emulator, and no row may be treated as a capped failure.

```json
{
  "status": "NOT_SCORED",
  "policy": "state_blind",
  "model_calls": 0,
  "key_status": "NOT_APPLICABLE",
  "seed_count": 80,
  "seed_start": 0,
  "seed_end": 80,
  "start_macro": 228,
  "macro_cap": 500,
  "goal": {"location_not": "MOVING_VAN"},
  "rows": 80,
  "scored_rows": 0,
  "not_scored": 80,
  "final_state_rows": 0,
  "child_error": "exit_1",
  "child_stderr": "ModuleNotFoundError: No module named 'pokemon_env'",
  "runtime": "native uv; not the pinned PokeAgent Docker runtime",
  "pooled_source": "work/pokeagent-emerald/live-results.jsonl",
  "pooled_source_sha256": "5294ec9a24319ebc7c528cdb3076c11bc381df3e1abbbb4334a6bf36c97c84fa",
  "pooled_source_rows": 6449,
  "runner_code_sha256": "ee7cfd6a64ac6cb16bcee148838a69a0c631482535d2034500626584f081ad47",
  "harness_sha": "62bf6f614b66ff76b79954e5a3f04f91c3c6a049",
  "rom_sha1": "f3ae088181bf583e55daf962a92bb46f4f1d07b7",
  "results_sha256": "1f70d5e41e039309e9ab866e45df305033816088e9049f9d9dd9a049f85d39e2"
}
```

The result is **NOT_RUN/NOT_SCORED** for the experiment question. Re-run only inside the pinned
linux/arm64 PokeAgent runtime, and commit a scored receipt only after all 80 rows contain a final
emulator state and no `child_error`.
