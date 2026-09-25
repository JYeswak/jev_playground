# PokéJev Leaf C r3 supervised battle arms

**Status: `PREPARED-NOT-MEASURED`.** This note is authorized only after the
keyless parity tests, dev refit, and held-out score in
`loss-depth-pokejev-leaf-c-r3-refit-receipt-20250925.md` were committed.

## Frozen inputs

- Model: `jev-1.13.0` for the optional `code+noul` arm.
- Frozen leaf artifact:
  `work/loss-depth/pokejev-components/leaf-model-v1.json`.
- Model SHA256:
  `05e4ac31457665e478237be51741869cb7005b5911da17cfd33ae77b8cd3525f`.
- Feature contract: full known team HP, integer post-move HP parsing, as defined
  in `loss-depth-pokejev-leaf-c-r3-prereg-20250925.md`.
- Pairing: `abyssal`, 200 battles, 8 workers, `k=0..199`, fresh output stems.
  The r2 partial is never resumed or appended to.

## Arms

1. `code`, no live leaf Noul calls.
2. `code+noul`, one Jev Noul request per eligible leaf turn using the existing
   three questions and the frozen model's Noul coefficients.

No threshold, feature, model, pair seed, or arm order may change after this note.

## Supervision and stop rule

Run one arm at a time. Capture combined stdout/stderr beside the result files
with `tee`, append the actual child exit code, and do not start the next arm until
the first arm's receipt is inspected. HTTP 401, HTTP 402, key rejection, or the
existing stop marker ends that arm immediately. If the wrapper is cancelled, the
exit code is `EXIT_CODE_UNOBSERVED` unless the footer was persisted; report the
stop timestamp and final persisted log lines before any further spend.

Commands:

```bash
set -o pipefail
log='work/loss-depth/pokejev-components/battle/leaf-r3-code.log'
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/battle/run.py battles abyssal 200 \
  --workers 8 --leaf code --run-id leaf-c-r3-code 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}; printf 'exit_code=%s\n' "$rc" | tee -a "$log"; exit "$rc"
```

If and only if the code arm completes its receipt gate, run the same command with
`leaf-r3-code-noul.log`, `--leaf code+noul`, and `--run-id leaf-c-r3-code-noul`.

## Receipt gate

Each completed arm must have exactly 200 completed rows, no harness-error rows,
the pinned model SHA, the expected `run_id`, and valid `run_py_sha256`,
`row_started_at_utc`, and `row_recorded_at_utc` on every row. Record wins/losses,
Wilson interval, time losses, decision count, Jev call count, input tokens, spend,
latency, fallback reasons, model version, log path, exit code, and stop reason.
A partial arm is `NOT-SCORED`; do not repair, append, or silently merge it.

The comparison reports code-only and code+Noul separately, with the paired
win-difference only if both arms pass the gate. This is not a general Jev
benchmark and does not revive the invalid r2 code result.

## Boundary

The r3 battle arms test the corrected harness on the frozen pair set only. The
held-out AUC receipt is a model gate, not a battle prediction. No arm is started
without a supervised log and an explicit persisted exit code or an explicit
`EXIT_CODE_UNOBSERVED` stop record.
