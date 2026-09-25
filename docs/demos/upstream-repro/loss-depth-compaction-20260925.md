# Compaction keep loss-depth autopsy (bead `jev-9gtw.5`; R99, R100)

QuietPrairie (Agent Mail; hub id CompactionAutopsy), Anthropic model, 2026-09-25. **Keyless**: no
TypeSafe call and no model call of any kind. This covers steps 1 and 2 of AGENTS.md's LOSS DEPTH loop
for the two compaction keep studies: `jev-x86y` (R99: at the default 0.5 cut, 0 of 32 needed calls were
kept verbatim) and `jev-jec6` (R100: no rule met the bar). Nothing here changes a bar, a label or a
NEGATIVE_EVIDENCE row.

## Reproduce

```bash
python3 work/loss-depth/compaction/autopsy.py            # every count below, from committed files
python3 work/loss-depth/compaction/autopsy.py --refresh  # first re-derive features.jsonl from the sha-pinned
                                                         # omp session files; refuses unless byte-identical
```

The run reads these files:

- `work/compaction-need/` and `work/compaction-keep/`: `calls.json`, the labels, `decisions.jsonl` and
  `decisions-pass.json`. These are unchanged.
- `work/loss-depth/compaction/autopsy.ts`: rebuilds the exact request `fast-jev-compaction` @ `6e1da50`
  sent for each session: `collectToolCalls`, `fitState` and `batchCalls` with the studies' `OPTIONS`.
  It measures per prefix call what that request showed and what the horizon used, and writes
  `features.jsonl` and `sessions.json`. Those hold numbers, flags and ids, and no session text.
- `work/loss-depth/compaction/codes.jsonl`: one row for each of the 62 needed unpinned calls Jev did not
  keep verbatim. Each row has four judged fields and one decisive fact.
- `autopsy.py` checks the codes against the mechanical features. It refuses when a code claims a stub
  that is not a stub, or claims a re-run returns an output whose file a later prefix call rewrote. It
  then applies a fixed precedence and prints every table in this file.

**Session handling.**
- `/tmp/x86y-packets` is gone. The prefix and horizon were rebuilt from the omp session files named in
  each `sessions.json`, after a sha256 check (all match).
- The rider rule was applied before any text was read. `work/compaction-keep`'s `RIDER_PATH`/`riderHits`
  screen of tool inputs flags `jev-x86y`'s `01a0c530` (1 hit), so it is skipped here.
  - It has 0 needed unpinned calls, so no miss is lost.
  - Its committed ids and scores still count in the AUC reproduction below.
  - `01a0c085` stays excluded (amendment A1) and is never read.

## What the library actually sent

One request per session. Each request had one batch, the state stage `full` in all 8 sessions, and
5.2k–12.6k estimated state tokens. It held three things.

- **State `context`**, verbatim: *"… `history` is the whole conversation so far, oldest first; tool
  outputs are replaced by a short `result` note and long texts may be abridged. … Whatever is not kept
  is deleted permanently, but the assistant can always re-run a tool or re-read a file."*
- **State `goal`**: the last three user prompts, each clipped to 500 characters.
- **State `history`**: each message's text verbatim, and each call as `{id, tool, input ≤1,000 chars,
  result: "ok, N chars (omitted)"}`.

It asked two Nouls per candidate call:

- `call_tN`: *"… should stay in the history: knowing this call was made, with its input, still matters for
  what the assistant does next"*.
- `result_tN`: *"The full output of tool call tN (tool, N chars) should stay in the history verbatim: the
  assistant still needs its contents **and re-running the tool would not do**"*.

The measured facts about those requests:

- **The request held none of the outputs.** No output's first 40 characters appear in its request
  state (0 of 317 calls with a 40+ character output).
- **The rebuild matches the live run.** `jev-jec6`'s 8 rebuilt requests estimate 82,901 input tokens.
  The live run recorded 72,649, so the estimate is 14.1% high, inside the estimator's documented 2–18%.
  `jev-x86y` cannot be checked the same way because `01a0c530` is not rebuilt.
- **The published scores reproduce from committed rows.** They are the AUCs of needed vs not-needed:

  | study | keepCall | keepResult | C2 `need` |
  |---|---:|---:|---:|
  | x86y | 0.689 | 0.691 | — |
  | jec6 | 0.714 | 0.633 | 0.654 |

- **Only the first of two prompts was in `01a0d288`'s goal.** Its latest prompt (a pane-1 interrupt)
  has a tool result attached by the adapter, so `goalFromMessages` skips it. The full text stays in
  the history.
- **The goal was a pointer in all 8 sessions.** In `01a0c086`, `01a0d0f2`, `01a0d11c`, `01a0d161` and
  `01a0d269` it says "read <dispatch file> in full and do it". The task body is therefore itself an
  omitted output. In `01a0d151`, `01a0d241` and `01a0d288` it names a bead to `br show`. Where the
  prefix fetched that bead (`01a0d151` t8, `01a0d241` t8), its body is likewise an omitted output.
- **The goal was clipped in 5 of 8 sessions** (latest prompt over 500 characters).

## How each miss was classified

**The four judged fields** come from reading each call's prefix and the horizon message the labels name:

- `used`: whether the later step used the output (`result`) or the call's own `input`.
- `reobtain`: whether re-running the call (`rerun`) or a plain read (`reread`) returns what was used,
  or nothing does (`no`).
- `trigger`: whether the use continues work already planned in the prefix, or answers a horizon prompt
  the prefix did not anticipate (`new-prompt`).
- `visible`: whether the goal names the call's file or command as the task.

**Precedence.** The first rule that matches assigns the cause:

1. `harness_shaken`: the transcript already held omp's shake stub (mechanical).
2. `unforeseeable`: `trigger = new-prompt`.
3. `call_not_result`: the use is the call's input.
4. `rerun_premise`: the output is re-obtainable, which the state tells Jev is always possible and the
   result question rules out.
5. `model_miss`: an irreplaceable output whose need the state shows.
6. `evidence_absent`: an irreplaceable output whose need the state does not show.

## Result: causes of the 62 needed calls not kept verbatim

| cause | x86y | jec6 | both | mean keepCall / keepResult |
|---|---:|---:|---:|---|
| `harness_shaken`: output already an omp shake stub | 0 | 12 | 12 | 0.369 / 0.163 |
| `unforeseeable` from the prefix | 0 | 0 | **0** | — |
| `call_not_result`: the use was the call's input | 3 | 3 | 6 | 0.473 / 0.177 |
| `rerun_premise`: re-obtainable, and the question asks for irreplaceable | 29 | 14 | **43** | 0.418 / 0.175 |
| `model_miss` with the evidence visible | 0 | 0 | **0** | — |
| `evidence_absent`: irreplaceable, need not shown | 0 | 1 | 1 | 0.360 / 0.150 |
| total | 32 | 30 | 62 | |

The contract's other causes, measured on the same misses:

- **State lacked the current task or latest prompt.** In 7 of 8 sessions the task body is an omitted
  output (5 dispatch-file reads and 2 bead fetches). In `01a0d288` the latest prompt is missing from
  the goal (see above).
  - 9 of the 50 non-stub misses are goal-named reads: the dispatch file or bead the goal points at,
    or a file the goal names (to edit, or as the correction's subject).
  - The mechanical path match finds 7 of those 9. The other two are the bead fetches.
- **Output truncated before the part later used.** The request showed 0 characters of every output.
  - Of the 42 non-stub misses whose used tokens can be located in the output, 33 have the earliest
    used token inside the first 500 characters.
  - For 18 of them, every used token is inside that head.
  - The library's own fallback (`drop_result`, which keeps a 500-character head) fired on 7 of the 62
    misses. On 2 of those the head held every used token: `01a0d161` t24's edit tag `#5A73` at offset 1,
    and `01a0d11c` t31. The verbatim metric still counts both as lost.
- **Unforeseeable later need.** 11 misses were used after a new horizon prompt. In each, the use
  continued work the prefix had already planned: the rule receipt and callback in `01a0c086` after
  pane-1 challenges, the `jev-fmy` edit in `01a0d161`, and the runner in `01a0d241` after the 402
  blocker. None was coded `new-prompt`.

## Examples (session, call, `tool_use_id`, decisive fact)

**`harness_shaken` (12, all in `01a0d0f2`, where 40 of 41 prefix outputs are stubs):**
- `01a0d0f2` t8 `call-5af772f4-…-7|fc_0782d2b9-…_0`. It reads the Canny receipt, but the transcript
  holds only `[shaken ~4224 tokens — recover: artifact://80 (region 7)]`, 57 characters. Keeping it
  verbatim keeps the stub, and the labellers inferred need from the path.
- `01a0d0f2` t26 `call-9790993b-…-25|fc_dcdb3ce7-…_4`. The labelled-rows read is a stub (4,909 tokens
  shaken). C2 scored it 0.51.
- `01a0d0f2` t18 `call-39c15c16-…-17|fc_c5a61187-…_1`. The Score-contract doc read is a stub, and h1's
  corrected probe relies on it.

**`rerun_premise` (43):**
- `01a0c086` t1 `call_01a0c092960774838b55fa5b7117b65f|…`. This is the dispatch pack the goal says to
  "read … IN FULL, then work it". keepResult was 0.20. The file is unchanged, so under the question's
  own clause ("re-running the tool would not do") no is the literal answer.
- `01a0c086` t25 `call_01a0c097501476d7b60ab78300221dff|…`. A deterministic count printed
  `callsite-exclusion hits= 64 rate=0.082%`, and h4's rule file cites `64/78,242 (0.08%)`. Re-running
  gives the same number. keepResult was 0.16.
- `01a0d161` t24 `toolu_01UYKkLE3RsP9Fepz8RhVcyB`. The edit echo carries the new tag `#5A73`, which the
  h22 edit anchors on. `drop_result` kept the call and a 500-character head that contains the tag.

**`call_not_result` (6):**
- `01a0d151` t27 `call-4ea2f8dc-…-26|fc_47050cb4-…_0`. h8 repeats the same `am file_reservations
  reserve` form for another path. keepCall was 0.51, so `drop_result` kept exactly what was used.
- `01a0d11c` t34 `call_01a0d11fb3157154a85472750235b0d8|…`. h6 rewrites `.omp/kit-guard.json` from the
  content in the write call's own input.
- `01a0d241` t1 `call-ad28f134-…-0|fc_bf512382-…_0`. h11 marks todo items done by the names in the
  call's input.

**`evidence_absent` (1):**
- `01a0d11c` t33 `call_01a0d11f9d1870caa24efb4f6d2808ad|…`. An Agent Mail reserve failed on a stale
  lock (pid, age), piped through `head`, so the state note says `ok, 615 chars`. h26's commit message
  cites the lock. A later run would not reproduce it.

**`unforeseeable` and `model_miss`: none.** The closest candidates to a model miss are the 9 goal-named
reads above: keepResult mean 0.189, max 0.23. They are coded `rerun_premise` because each file was
unchanged and re-readable.

All 62 rows, with their facts, are table 6 of the script's output.

## What this says

The loss is mostly about the question and the state, not about Jev's ability to foresee need.

- None of the 62 misses needed foresight the prefix lacked.
- 43 were outputs that re-running or re-reading returns. The library asks Jev whether an output must
  stay because "re-running the tool would not do", and its state tells Jev "the assistant can always
  re-run a tool or re-read a file". The labels ask something else: whether a later turn used the
  output.
- For a re-readable file, the question's literal answer is no. That holds even for the dispatch file
  the goal says to read and follow.
- Jev also never saw any output. Every call reached it as `ok, N chars (omitted)`.
- 12 of `jev-jec6`'s 30 needed calls had no output to keep: omp had already shaken that session.

The live TypeSafe docs (`docs-mirror/typesafe/primitives/noul.md:382`) say: *"Ask one yes/no question per
Noul. If a question has two conditions … the model has to judge both at once and the value means less.
Ask two Nouls and combine them in code."* The library's result Noul has two conditions: still needed,
and not reproducible. C2 in `jev-jec6` also had two: will use it, and no later call restates it. C2
also kept the state's re-run sentence. So neither studied design asked the single question the labels
answer.

## Hypotheses for the dev replay loop, ranked (one variable each)

**Dev slice.** The 7 sessions with no stub outputs: `01a0c086`, `01a0d11c`, `01a0d151`, `01a0d161`,
`01a0d241`, `01a0d269` and `01a0d288`. Unpinned calls: 50 needed, 165 not-needed, 4 undecidable. These are
development data (the two studies' labelled sessions). A winning design still needs a fresh,
preregistered held-out set.

**H1. The re-run premise.**
- **Variable:** remove the premise and change nothing else. Delete "but the assistant can always re-run a
  tool or re-read a file" from `STATE_CONTEXT`. Ask one single-condition Noul per call: *"a later step
  will read, cite or act on a value, line, path or finding in this output"*. Re-runnability, if wanted,
  moves to code (tool class, and whether a later call rewrites the file).
- **Prediction:** the 9 goal-named reads reach ≥ 0.5, and slice AUC rises from C2's 0.654 to ≥ 0.75.
- **Supporting keyless sign:** under C2, which dropped the question's re-run clause but kept the
  state's, the 3 goal-named reads in `jev-jec6` averaged 0.520. The other 11 `rerun_premise` misses
  there averaged 0.347.
- **Falsified if** the 9 stay below 0.5. Then the premise is not what holds scores down, and H2 is next.

**H2. Output evidence in the state.**
- **Variable:** replace `result: "ok, N chars (omitted)"` with the output's first 500 characters (the
  head `drop_result` already keeps). The question stays fixed.
- **Prediction:** slice AUC rises by ≥ 0.10. The rise concentrates on the 33 misses whose earliest used
  token sits inside that head. It does not reach the 9 whose earliest token lies beyond the head, or
  the 8 with no locatable token.
- **Cost:** about 40 × 150 tokens per request, which fits the 30k request cap over 5–12.6k states.
- **Falsified if** AUC moves less than 0.05.

**H3. The goal holds the task, not a pointer to it.**
- **Variable:** the goal becomes the latest prompt, unclipped, plus the body of the file or bead it
  names. That body is an omitted output in 7 of 8 sessions (5 dispatch-file reads and 2 bead
  fetches). The eighth, `01a0d288`, names a bead that this autopsy did not trace to a prefix call.
- **Prediction:** calls whose input path appears in that body gain more than calls whose path does not.
  Per call, the 9 goal-named reads gain the most.
- **Falsified if** the two groups gain equally.

**H4. Stub handling, a prerequisite and not a fix.**
- **Variable:** skip sessions whose outputs are omp shake stubs, or resolve `artifact://` before asking.
- **Keyless check, already run:** dropping the stubs from `jev-jec6` still meets no bar.
  - C1: 15/18, Wilson lower bound 0.608, not-needed dropped 27/75.
  - C2: 5/18.
  - AUC 0.663–0.665.
- **Consequence:** a replay that includes `01a0d0f2` measures the stubs, not the design.

**H5. A different cut on the existing scores. Closed, keyless.** No cut meets `jev-jec6`'s bar in either
study, for any recorded score. The scores tried were keepCall, keepResult, `need`, and the max of
those present. Threshold or rank tuning on these scores cannot reach the bar, so none of it should be
retried.

## NO-CLAIM and disclosures

- **One coder, not blind.** The four judged fields were coded by one reader (this pane, an Anthropic
  model) from the rebuilt prefix and horizon, with Jev's scores visible in the working dossier. The
  fields describe the transcript, not the scores. Precedence and every count are code.
- **The dossier was never committed.** It lived at `/tmp/loss-depth-compaction/` and held session
  text. The committed codes carry only short quotes: paths, tags and printed numbers.
- **"Used tokens" is a proxy.** It means token overlap between an output and the horizon message the
  labels name. It locates the part used, and it is not a parse.
- **Scope.** 8 sessions of one project and one model pin, with the two studies' cut point and horizon.
  The causes explain these 62 misses. Whether any hypothesis works is for the replay loop.
