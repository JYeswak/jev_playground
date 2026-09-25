# PokéJev Leaf C r4 code-only supervised battle

**Status: `PREPARED-NOT-MEASURED` until this note is committed.** This is the
new battle authorization after the r4 action-ranking refit. It supersedes the
r3 battle note's optional `code+noul` arm for this run; r4's held-out code-only
and code+Noul reads gave no reason to spend on the Noul leaf arm.

## Frozen inputs

- Pairing: `abyssal`, `k=0..199`, 200 battles, 8 workers.
- Pair seed: `20260925`, the same 200 pairings used by the prior frozen-alpha
  comparison.
- Leaf arm: `--leaf code` only. This uses the frozen code leaf and makes no new
  leaf Noul requests; Jev remains live for the upstream action-prior and
  opponent-model questions already in the Stage B harness.
- Model: `jev-1.13.0`.
- Frozen leaf artifact:
  `work/loss-depth/pokejev-components/leaf-model-v1.json`.
- Frozen leaf artifact SHA256:
  `ad8cd16482eb41e409409c94c968d0b2857f736bd6258b9afd556d785273c49b`.
- Run source is `work/loss-depth/pokejev-components/battle/run.py`; every
  emitted row records its `run_py_sha256`, imported Stage B hashes, `run_id`,
  and UTC timestamps.
- Fresh output stem: `leaf-c-r4-code`. Do not resume, append, or repair any
  r2/r3 partial or prior leaf output.

## Battle bar

The confirmatory bar is the existing 70% Abyssal kill line: the completed arm
must report at least 140 wins of 200, with no harness-error rows and valid row
provenance. Record the Wilson 95% interval, time losses, fallback reasons,
Jev-call count, input tokens, spend at the committed input rate, latency,
model version, source hashes, log path, exit code, and stop reason. A partial
arm is `NOT-SCORED`; never turn it into a 200-battle result by appending rows.

This is one code-only arm, not a code-vs-code+Noul comparison. The held-out
r4 receipt is a model gate, not a battle result.

## Supervised interim gate

The live process MUST be started under a visible `tee` pipeline and MUST append
the actual child exit code. After the first 200 eligible decisions (decisions
where more than one action type was offered), stop the runner at a battle
boundary using the existing stop marker. Run the landed keyless checker against
that partial arm and the committed Stage B reference:

```bash
scripts/arm-sanity.py \
  --arm work/loss-depth/pokejev-components/decisions-abyssal-leaf-code-r4-code.jsonl \
  --reference work/poke-jev/stage-b/decisions-abyssal.jsonl \
  --min-rows 200 --max-diff 0.10
```

The continuation gate is stricter than the checker's default: the absolute
switch-rate difference on the first 200 eligible arm decisions MUST be at most
`0.10` against the Stage B offered-switch reference (`0.41`). Record the arm
and reference eligible counts, switch counts/rates, absolute difference, and
checker exit code. If the difference exceeds `0.10`, or the arm is degenerate,
stop permanently and record `NOT-SCORED`; do not run the remaining battles.
If it is within `0.10`, clear only the persisted stop marker, restart the same
frozen command and `run_id`, and let the runner complete the remaining pairings.
The runner skips completed `k` values and does not alter their rows.

The interim check is a harness guard, not a performance claim. It does not
change the 70% final bar or permit a post-hoc model change.

## Commands

Commit this note before any live command. Then run one supervised process:

```bash
set -o pipefail
log='work/loss-depth/pokejev-components/battle/leaf-c-r4-code.log'
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/battle/run.py \
  battles abyssal 200 --workers 8 --leaf code --run-id leaf-c-r4-code \
  2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
printf 'exit_code=%s\n' "$rc" | tee -a "$log"
exit "$rc"
```

The supervisor must observe the live process, stop it only after the interim
row gate, and inspect the persisted footer before continuing. No unattended
watcher or retry loop is allowed. No `code+noul` arm follows this note.

## Boundary

This note authorizes only the r4 code-only arm against the frozen 200 pairings.
It does not authorize changing the model, pair seed, workers, clock, action
prior, opponent model, or final bar after seeing rows. It does not authorize
new leaf Noul calls. A failed interim gate or any unobserved child exit leaves
the arm `NOT-SCORED` and requires a new preregistered decision before another
battle attempt.
