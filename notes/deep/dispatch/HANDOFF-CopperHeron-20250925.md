# CopperHeron quiet handoff — 2026-09-25

## Beads

- `jev-yru2`: **in_progress**, assigned to CopperHeron. This is the current unit.
- `jev-pvdp`: closed after non-author verification; no remaining action in that bead.

## Last commits

- Last CopperHeron unit commit: `5b368355db7c448572eddb7a3df65cf47f3b3b9c`, `fix(gate-question-gap): [test] make public row IDs unique`.
- It supersedes the first extract commit `bfc19b43ae95ba4966cc276634da38315c0ee24a`; the first extract had duplicate command hashes across repeated run scalars and was corrected before any labels were written or committed.
- The shared-tree HEAD observed during handoff is `c971f34301133aee6bc177f215f9d3587da543d1`, a pane-1/shared-tree commit, not authored by CopperHeron. Do not stage or revert sibling changes.

## Completed yru2 work

- Preregistration and transport correction committed before the successful extract: `20f99ed366688b6f2e08fee9ccca3ab70a2dc58c` and the follow-up corrections carried into the shared history.
- Frozen source rule: GitHub search query `topic:github-actions archived:false is:public`, sorted by stars descending, top ten frozen at `2026-09-25T17:01:59Z`; no workflow-driven replacements.
- Successful public archive extract: seven retained MIT repositories, three license exclusions, 214 candidate run scalars, 10 target-shape rows, 100 fixed-seed non-target rows, 110 selected rows, 110 unique row IDs.
- Extract SHA-256: `0e76d6bc679fb3ad6fd40c1bf0c49e3400fbe16febb0d914a1749975b13fb5af`.
- State SHA-256: `2700c1d9cb5bd69b15e824ed8539dc9925884d3a369deb26d75baf41199d8e17`.
- State-size check: `python3 scripts/jev-state-size.py work/jev-yru2-public/states.jsonl --question-bytes 1886` → `FITS 110, NEAR 0, OVER 0`.
- No Jev/API call was made.
- `ubs work/jev-yru2-public/extract_public.py` completed with zero critical and zero warning findings (one informational subprocess-related item).

## Exact stop point

The next step was the two blind labelers. `work/jev-yru2-public/label_prompt.md` contains the recorded prompt, frozen five harm clauses, input projection, deterministic batch size (20), and model aliases: Labeller A `completion model=smol`; Labeller B `completion model=slow`.

- First whole-array attempt launched both completions but failed validation because the pre-fix extract used duplicate command hashes. No label files were written or committed. The extract was then fixed and recommitted at `5b368355`.
- Second attempt started Labeller A in deterministic 20-row batches with `completion model=smol`; the eval cell was interrupted by the quiet-restart order before any output was written. Labeller B was not completed. No `labels-*` files exist under `work/jev-yru2-public/`.
- Labeller A was started at approximately `2026-09-25T17:20Z` and stopped unfinished on the quiet-restart order; its partial response remained only in the interrupted eval kernel, no partial label file was written, and no label output is available for commit.
- No completion/process matching `jev-yru2`, `completion`, or `work/jev-yru2-public` was running at handoff (`NO_MATCHING_PROCESS`).

## Uncommitted state

- Complete but uncommitted: `work/jev-yru2-public/label_prompt.md`.
- No label output exists.
- The shared working tree has many unrelated pane changes. Do not stage, revert, stash, or overwrite them. Stage only `work/jev-yru2-public/label_prompt.md` and this handoff file in the quiet handoff commit.

## Next concrete step

After restart, commit the already-written prompt and this handoff with `git commit --only`, then run the two blind labelers independently against committed extract `5b368355`; validate exactly 110 labels per file and commit each label file with explicit paths. Compute disagreements only after both label files are committed, send the disagreement rows to AmberWillow for adjudication, and do not make a live Jev call. Because there are exactly 10 target-shape rows, one `no-harm` target-shape label leaves fewer than 10 target-harm rows and must be reported `UNDERPOWERED`.

## Waiting on pane 1 / Joshua

- Pane 1 must adjudicate all disagreements after both blind label files are committed.
- No paid/live action is pending or authorized in this unit.
