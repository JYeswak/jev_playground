# Labelled replay of the keep-question fixes, as a comment on tamaratran/fast-jev-compaction#52

**Status:** filed on 2026-09-25 as
https://github.com/tamaratran/fast-jev-compaction/issues/52#issuecomment-5827141624 (JYeswak), after
pane 1 approved it and Joshua authorized upstream comments (bead `jev-9gtw.6`). The body posted is
the quoted section below, unwrapped, and the read-back matches it byte for byte apart from the
trailing newline.
**Target:** `tamaratran/fast-jev-compaction` at `6e1da50`. The pinned clone is untouched, and no fork
exists yet, because nothing here measured an improvement.

## Dedupe (2026-09-25, `gh issue list --state all`, 34 issues)

The design observations are already reported, so this is **not a new issue**:
- **#26:** results are shown as `ok, N chars (omitted)`, and the state's "can always re-run a tool or
  re-read a file" pushes toward no. It proposes putting a head and tail of each output in the state.
- **#52:** the result Noul asks "still needs its contents **and** re-running the tool would not do".
  This measures irrecoverability, not usefulness. It proposes rewording.
  - Comments add MaxSar51's replay: proxy labels, rewording AUC 0.656–0.718, and visibility adds
    nothing.
  - Austin666k's comment says deleting the re-run clause alone lifts a load-bearing `Read` from
    0.24 to 0.85.
- **#25:** non-reproducible results need protection that relevance alone cannot give.

What none of those has is **blind labels from two independent model labellers (not humans),
adjudicated**. The draft below is a comment on #52, linking
#26. It adds that measurement and states what we can and cannot prove.

## Draft comment

> Adding a labelled replay to this thread. It confirms the design observations and reports that, on
> our data, the proposed fixes did not produce a usable keep signal.
>
> **Setup.**
> - Library at `6e1da50`, `jev-1.13.0`, the replay options `keepThreshold 0.5`, `maxStateTokens
>   20000`, `truncateHeadChars 500`, `preserveRecentMessages 6`.
> - 7 real coding-agent sessions (omp harness). Each was compacted at the result of its 40th tool
>   call.
> - Every prefix call was labelled needed / not-needed against the next 40 messages by two
>   independent model labellers (Anthropic models, not humans, blind to Jev's scores and to each
>   other), with disagreements adjudicated: 50 needed and 165 not-needed unpinned calls.
> - Requests were built outside the library. Our baseline body is byte-identical to what `compact()`
>   sends, and it re-measured the exact input tokens of an earlier live run (72,649).
>
> **The design, as the code states it.**
> - Outputs never reach Jev. `state.ts:106` renders every call's result as `ok, N chars (omitted)`.
>   In a replay of the library's own requests (8 sessions), 0 of 317 outputs appear in any request state.
> - `STATE_CONTEXT` (`state.ts:12`) ends "the assistant can always re-run a tool or re-read a file".
> - The result Noul (`compact.ts:64`) has two conditions: "the assistant still needs its contents and
>   re-running the tool would not do".
> - An error analysis covered all 62 needed calls the library did not keep in two earlier labelled
>   runs (8 sessions: these 7 plus one whose outputs had already been cleared by the harness). 43
>   were outputs that a re-run or re-read would return, so under this wording "no" is the literal
>   answer. 12 had no output left to keep. 0 were needs that the prefix could not foresee.
>
> **Arms.** One variable each; AUC is needed vs not-needed:
>
> | arm | AUC | needed kept / not-needed dropped at 0.5 |
> |---|---:|---|
> | library request | 0.648–0.661 (4 runs) | 0/50 / 165/165 |
> | re-run sentence removed + one "a later step will read, cite or act on … the output" Noul | 0.514 | 36/50 / 47/165 |
> | first 500 chars of each output in `result` (#26's proposal) | 0.663 | 0/50 / 165/165 |
> | unclipped task + the dispatch file it names in `goal` | 0.662 | 0/50 / 165/165 |
> | output head visible **and** re-run sentence removed **and** one use Noul | 0.524–0.537 (3 runs) | 42/50 / 31–37 of 165 |
>
> **What we see.**
> - While the re-run sentence and the two-condition question are in place, every `keepResult` sits
>   in 0.07–0.29, whatever the state shows. Adding the output head moved AUC by 0.015, within the
>   0.013 spread of identical repeats.
> - Removing the premise (with or without the output) spreads the scores to 0.22–0.91, but they no
>   longer rank need.
> - So on labelled data we could not confirm that rewording alone, or rewording plus visibility,
>   fixes selection. MaxSar51's and Austin666k's results use proxy labels or a two-call probe. Ours
>   use blind labels from two independent model labellers (not humans), adjudicated, over 215 calls.
> - None of our arms reached a usable operating point: at any cut dropping half the not-needed
>   results, needed-kept had a Wilson lower bound of 0.65 or less.
>
> **What we can say, and what we cannot.**
> - The three design points above are real: outputs hidden, the premise sentence, and the
>   two-condition Noul.
> - We did not find a Noul wording that fixes them. The output-size and feature baselines MaxSar51
>   reports (AUC 0.84–0.85) are the next thing we would try.
> - We cannot share the transcripts. Per-call scores and labels exist as ids and numbers only.

## Evidence in this repo

- Autopsy: `docs/demos/upstream-repro/loss-depth-compaction-20260925.md` (`801f812`).
- Replay: `docs/demos/upstream-repro/compaction-replay-20260925.md`.
  - Prereg `948b479`, dev results `73a16c4`, A1 prereg `7f12e9f`.
  - Scripts `work/loss-depth/compaction/replay.ts` and `replay.py`.
- Source lines at `6e1da50`: `fast-jev-compaction/src/state.ts:12` (the re-run sentence),
  `state.ts:106` (`(omitted)`) and `compact.ts:64` (the two-condition result Noul).
