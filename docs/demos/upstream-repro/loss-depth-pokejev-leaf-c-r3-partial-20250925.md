# Leaf C r3 code arm: partial receipt

**Status: `NOT-SCORED` — unresolved harness-bug.** The full-team replay/live
parity tests passed, but the live candidate policy remained degenerate: switches
were selected on 977 of 982 turns where a switch was offered (99.5%). The arm was
stopped before any Noul arm; these rows are evidence for the next keyless audit,
not a model or battle result.

## Stop boundary

- Run id: `leaf-c-r3-code`; command was the committed r3 supervised battle note,
  200 battles, 8 workers, `--leaf code`.
- Cancellation: `2026-09-25T03:12:12-0600` via the supervised job cancellation.
  `pgrep` immediately afterward found no battle or worker process.
- Results persisted through `03:11:52-0600`: 89 battles, `k=0..106`, 28 wins and
  61 losses.
- Decisions persisted through `03:11:52-0600`: 2,836 rows; 982 switch-offered
  turns; 977 switch choices; 2,161 one-hot leaf value maps.
- Captured log:
  `work/loss-depth/pokejev-components/battle/leaf-r3-code.log`.
  Its final persisted lines are trainer-art PM warnings from abyssalbot55,
  abyssalbot54, abyssalbot57, and abyssalbot53. The tee shell was cancelled before
  its `exit_code=` footer, so the numeric exit code is
  `CANCELLED/EXIT_CODE_UNOBSERVED`, not a guessed success code.

Path-limited evidence committed with this receipt:

- `work/loss-depth/pokejev-components/results-abyssal-leaf-code-leaf-c-r3-code.jsonl`
- `work/loss-depth/pokejev-components/decisions-abyssal-leaf-code-leaf-c-r3-code.jsonl`
- `work/loss-depth/pokejev-components/battle/leaf-r3-code.log`

## What is and is not established

The keyless tests proved the corrected HP regex and full-team replay/live feature
contract on three recorded first turns. They did **not** prove that the candidate
summaries supplied by the live battle path carry the same feature values as the
replay snapshots. The r3 live arm therefore remains invalid despite those tests.

No `code+noul` arm was started. No r3 win rate, AUC, or code-vs-Noul comparison may
be reported from this partial.

## Required next diagnostic

Before any further paid call, take five recorded r3 decision turns and print for
one switch plus two moves per turn: the candidate summary, the four base feature
values, `ko_threat`, standardized feature vector, and frozen code leaf score.
Identify the feature whose live candidate values force the switch ordering. The
100-row sanity arm in the r3 receipt used the recorded `leaf-code-v1` decisions,
not live-path feature reconstruction; it is not evidence against this failure.
Add a keyless regression test for the identified live candidate-feature contract,
then write and commit a new preregistration before any resume.
