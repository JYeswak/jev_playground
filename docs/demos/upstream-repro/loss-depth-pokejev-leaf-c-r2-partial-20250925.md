# Leaf C r2 code arm: partial receipt

**Status: `NOT-SCORED` — harness-bug.** This is an interrupted partial, not a
battle result for the frozen Leaf C model. It is committed only to preserve the
failure evidence and the exact stop boundary.

## Run and stop

- Run id: `leaf-c-r2-code`; model: `jev-1.13.0`.
- Command: `run.py battles abyssal 200 --workers 8 --leaf code --run-id leaf-c-r2-code`,
  launched through the canonical Infisical wrapper and supervised by the caller.
- Process cancellation: `2026-09-25T02:43:29-06:00`; no battle workers remained
  when checked immediately afterward.
- No numeric child exit code was emitted: cancellation interrupted the tee shell
  before its `exit_code=` footer. This is recorded as `CANCELLED/EXIT_CODE_UNOBSERVED`,
  never inferred as success.
- Captured log: `work/loss-depth/pokejev-components/battle/leaf-r2-code.log`.
  The persisted log stopped at `02:35:50-0600`; its last lines are the normal
  `abyssalbot54`/`abyssalbot57` trainer-art warnings. The row files persisted until
  `02:43:11-0600`.
- No `code+noul` arm was started.

## Persisted partial

The path-limited artifacts are:

- `work/loss-depth/pokejev-components/results-abyssal-leaf-code-leaf-c-r2-code.jsonl`:
  123 finished battles, `k=0..153`, 38 wins and 85 losses.
- `work/loss-depth/pokejev-components/decisions-abyssal-leaf-code-leaf-c-r2-code.jsonl`:
  4,385 decision rows; 3,712 rows have leaf values; 3,681 of those value maps are
  exactly one-hot; 2,360 chosen actions are switches.
- Input tokens: 11,122,642; output tokens recorded: 0; model rows identify
  `jev-1.13.0`. At the documented $0.042 per million input tokens this is
  approximately $0.467151 Jev spend.

These rows and the supervised log are retained as evidence, but no win rate,
AUC, or comparison is reported from them.

## Root cause: three independent harness defects

1. `work/loss-depth/pokejev-components/battle/run.py:439` uses
   `re.findall(r"(\\d+)%", ...)`. Because the raw pattern contains a doubled
   backslash, it searches for a literal backslash and never matches the HP
   percentages in candidate summaries. Candidate HP therefore falls back to one
   shared base value.
2. With HP absent, status, hazards, and speed are also shared across candidates;
   the only candidate-varying code feature is `ko_threat`: `0` for switches and
   `1` for moves. The frozen coefficient is `-0.124`, so every switch scores above
   every move. This is a deterministic choice-policy defect, not evidence about
   Jev or the leaf model.
3. Independently, training's `leaf_c.snapshot_features` sums replay-seen Pokémon
   HP fractions and divides by 6, while live `_base_features` sums the whole
   known `battle.team` and divides by 6. Training mean `hp_weighted_remaining`
   is about `0.268` (scale about `0.135`); live values are near `1.0` (about
   `z=+5`). This train/serve skew invalidates the live feature distribution even
   after the regex is corrected.

The partial arm is therefore `NOT-SCORED` for harness-bug, with all three causes
required to be fixed or explicitly resolved before a new battle arm.

## Boundary and next gate

No code+noul battle was run. No result from this partial may be compared with the
frozen-alpha arm or the zero-call control. Before any new live call, keyless tests
must show: (a) two move candidates with different post-move HP receive different
leaf scores; (b) live and replay feature vectors agree within `1e-6` on at least
three recorded Stage B turns, using the same explicitly chosen HP denominator;
(c) on 100 recorded dev states, switch selection when a switch is offered is within
10 percentage points of the Stage B arm's 41% sanity rate. If matching replay
features requires changing the training definition, the model must be refit on dev
and re-scored on held-out under a new committed preregistration before any battle.
