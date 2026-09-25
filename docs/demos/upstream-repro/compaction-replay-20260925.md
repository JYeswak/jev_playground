# Compaction keep replay loop: dev arms, then a blind held-out (bead `jev-9gtw.6`)

QuietPrairie (Agent Mail; hub id CompactionAutopsy), Anthropic model, 2026-09-25. LOSS DEPTH steps 3–4
for R99/R100, from the autopsy `docs/demos/upstream-repro/loss-depth-compaction-20260925.md`
(`801f812`). **PREPARED-NOT-MEASURED.** This section is committed before the first live call. The
requirements are these:

- Jev only (`jev-1.13.0`, pinned), through TypeSafe.
- No comparator model and no Laya.
- Every request is built in our wrapper, `work/loss-depth/compaction/replay.ts`. The vendored
  `fast-jev-compaction` clone (`6e1da50`) is imported and never edited.

## Dev preregistration

**Slice.** These are the 7 stub-free sessions of the autopsy, all development data:
- `jev-x86y`: `01a0c086`, `01a0d151`, `01a0d161` and `01a0d269`;
- `jev-jec6`: `01a0d11c`, `01a0d241` and `01a0d288`.

Among their unpinned prefix calls, the final labels are 50 needed, 165 not-needed and 4 undecidable.
Each session file is sha256-checked before it is read. `01a0c085` (A1), `01a0c530` (rider screen) and
the stub session `01a0d0f2` are not in the slice. `01a0d0f2` is read once, only for the token check
below; `jev-jec6` already sent it to Jev.

**Arms.** One variable each, and one request per session per arm: every arm fits in one batch, 6.8k–
23.1k estimated request tokens against the library's 30k cap.
- **A0, the baseline.** It is the library's own request.
  - `replay.ts check`, keyless, compares every session's A0 body with the body `compactMessages`
    sends through a recording `fetch`. They are byte-identical in all 8 readable sessions.
  - `replay.ts tokens --live` resends A0 plus `jev-jec6`'s C2 question for its 4 sessions. The summed
    `usage.input_tokens` must equal the 72,649 that `jev-jec6` recorded.
- **H1, the re-run premise.** H1 makes two changes, which together are one variable:
  - `STATE_CONTEXT` loses *"but the assistant can always re-run a tool or re-read a file"*. It keeps
    *"Whatever is not kept is deleted permanently."*
  - One single-condition Noul replaces the library's two: *"A later step of the assistant will read,
    cite or act on a value, line, path, error or finding that appears in the output of tool call {id}
    ({tool}, {n} chars)."*

  Everything else is A0's, including the history with every output omitted.
- **H2, output evidence.** Each call's `result` becomes `ok|error, N chars: <the output's first 500
  characters> …[k more chars]` instead of `(omitted)`.
  - `STATE_CONTEXT`'s *"tool outputs are replaced by a short `result` note"* becomes *"each tool
    output is cut to its first 500 characters in `result`"*.
  - The questions are A0's.
- **H3, the task in the goal.** The library's own `goal` option carries the last three user prompts,
  unclipped. A prompt that carries a tool result counts. The goal then adds the full output of each
  prefix call that fetched what those prompts name:
  - a `read` of a file they name as a whole path;
  - a bead they name, fetched by `br show` or read back as its JSON;
  - with br's `INFO` log lines stripped, the longest fetch per target, and each body capped at 10,000
    characters.

  `fitState` fits the state as the library does. The questions are A0's.

**Scores.** Each arm's primary score is the Noul that keeps a result verbatim: `keepResult` for A0,
H2 and H3, and `use` for H1. `keepCall` is reported for A0, H2 and H3, as description only.

**Metrics.** Computed by `python3 work/loss-depth/compaction/replay.py`, keyless, over the slice's
unpinned calls with final labels:
1. AUC of needed vs not-needed.
2. At the library's cut, 0.5: needed kept, with a Wilson 95% interval, and not-needed dropped.
3. At the dev cut: needed kept, with its Wilson lower bound, and not-needed dropped. The dev cut is
   the smallest observed score at which at least 50% of not-needed results drop. The jec6 bar is also
   evaluated there (lower bound ≥ 0.80 and ≥ 50% dropped). This is a dev indication, not a result.
4. The autopsy's subgroups:
   - the 9 goal-named reads: mean score, and how many reach ≥ 0.5;
   - needed calls whose earliest used token lies inside the first 500 characters (33) vs the other
     needed calls.
5. A0 against the recorded studies: how many nouls equal the recorded ones, and the largest
   difference. This is a determinism check on the pin.

**Predictions, from the autopsy.** Each is falsified as stated.
- **H1:** the 9 goal-named reads reach ≥ 0.5 and AUC reaches ≥ 0.75. Falsified if the 9 stay below
  0.5.
- **H2:** AUC rises by ≥ 0.10 over A0, and the rise is larger on the 33 head-located needed calls than
  on the other needed calls. Falsified if AUC moves less than 0.05.
- **H3:** the 9 goal-named reads gain more than the other needed calls. Falsified if they gain
  equally.

**What goes to held-out.** The dev pass decides nothing about Jev. It selects the design and the cut,
and then:
- The arm with the highest dev-cut Wilson lower bound is the candidate.
- If two or more arms each raise AUC by ≥ 0.05 over A0, their combination runs once on the same slice
  first, and it becomes the candidate if its dev-cut lower bound is higher.
- The candidate's design and cut are frozen in the held-out preregistration before any held-out Jev
  call.
- The per-arm table goes to pane 1 before any held-out work.

**Budget.** Dev: 28 requests (4 arms × 7 sessions) plus 8 for the token check, about $0.02 at
$0.042 per million input tokens. The held-out stays under $1.

**Rows.** `dev-answers.jsonl` holds per arm and call: session, `tool_use_id`, pinned and scores.
`dev-requests.jsonl` holds per request: arm, session, input tokens and a body sha256 prefix.
`dev-pass.json` and `tokens-check.json` hold the spend and the token check. No session text is
written.

**NO-CLAIM.** 7 development sessions of one project and one model pin, with the two studies' cut
point and 40-message horizon. The arms were written after the autopsy read these sessions, so a dev
gain is a hypothesis for the held-out, not a result.

## Dev results (live, 2026-09-25, `jev-1.13.0`)

**Order.** `948b479` is the prereg above. The token check and the dev pass then ran once each, at
05:01:30Z and 05:01:42Z, under `infisical run`, with `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` unset.
Re-score, keyless: `python3 work/loss-depth/compaction/replay.py`.

**The baseline is the library's request.**
- **Token check:** A0 plus C2 on `jev-jec6`'s 4 sessions, 8 requests, measured **72,649 input
  tokens**. `jev-jec6` recorded exactly 72,649 (`tokens-check.json`, $0.0031).
- **Nouls:** 159 of A0's 438 nouls equal the recorded ones. The largest difference is 0.07, so the pin
  repeats a request exactly but its answers vary by a few hundredths.

**Spend.** 28 dev requests, 337,717 input tokens, **$0.0142**. By arm: A0 70,630, H1 62,704,
H2 115,387, H3 88,996. With the token check, the total is $0.0172.

**Per arm.** Unpinned calls on the slice: 50 needed, 165 not-needed.

| arm | score | AUC | needed kept at 0.5 | not-needed dropped at 0.5 | dev cut | needed kept at dev cut | not-needed dropped there |
|---|---|---:|---|---:|---:|---|---:|
| A0 library | keepResult | 0.648 | 0/50 (0.000–0.071) | 165/165 | 0.16 | 32/50 (0.501–0.759) | 87/165 |
| H1 no re-run premise, one use Noul | use | **0.514** | 36/50 (0.583–0.825) | 47/165 | 0.59 | 28/50 (0.423–0.688) | 83/165 |
| H2 output head in the state | keepResult | 0.663 | 0/50 (0.000–0.071) | 165/165 | 0.17 | **39/50 (0.648–0.872)** | 84/165 |
| H3 task body in the goal | keepResult | 0.662 | 0/50 (0.000–0.071) | 165/165 | 0.16 | 36/50 (0.583–0.825) | 92/165 |

No arm meets the jec6 bar on dev: no dev-cut Wilson lower bound reaches 0.80. The descriptive
`keepCall` AUCs are A0 0.689, H2 0.641 and H3 0.701.

**Score ranges** (unpinned calls, min–median–max):

| arm | min | median | max |
|---|---:|---:|---:|
| A0 | 0.08 | 0.16 | 0.28 |
| H2 | 0.07 | 0.17 | 0.29 |
| H3 | 0.08 | 0.16 | 0.29 |
| H1 | 0.22 | 0.60 | 0.91 |

**Subgroups.**

| arm | 9 goal-named reads: mean | ≥ 0.5 | 33 head-located needed: mean | 17 other needed: mean |
|---|---:|---:|---:|---:|
| A0 | 0.184 | 0 | 0.175 | 0.167 |
| H1 | **0.727** | **7** | 0.608 | 0.583 |
| H2 | 0.211 | 0 | 0.193 | 0.188 |
| H3 | 0.210 | 0 | 0.178 | 0.171 |

**Predictions.**
- **H1:** the goal-named half held (7 of 9 reach ≥ 0.5, mean 0.727). The AUC half is **falsified**:
  AUC fell to 0.514, below A0. Without the premise Jev scores almost every call as likely to be
  used, and with no output to look at it cannot tell needed from not-needed.
- **H2: falsified** (+0.015 AUC, under the 0.05 floor). The 33 head-located calls rose by 0.018 and
  the other needed calls by 0.021, so there was no concentration either.
- **H3: falsified as a design.** AUC rose by only 0.014. The goal-named reads gained 0.026 and the
  other needed calls about 0.004. That difference exists but is small.

**What the dev pass shows.**
- While the re-run sentence and the two-condition question stand (A0, H2, H3), every `keepResult`
  sits in 0.07–0.29. Showing Jev the output (H2) or the task (H3) moves it by about 0.01.
- Removing the premise without showing the output (H1) spreads the scores to 0.22–0.91 but loses the
  ranking.
- Each studied variable alone is either suppressed by the premise or blind without evidence. The
  combination of evidence with no premise has not been run.

**Held-out selection, as preregistered.**
- No arm raised AUC by ≥ 0.05 over A0, so the preregistered combination rule does not fire.
- The candidate by dev-cut lower bound is H2 at cut 0.17: 39/50 kept, lower bound 0.648, with 84/165
  dropped. It does not meet the bar on dev.
- This table goes to pane 1 before any held-out work.

**NO-CLAIM.** 7 development sessions, one pass per arm, one model pin. The pin's answers vary by up
to 0.07 between identical requests, so dev differences under about 0.02 in a mean are within repeat
noise.

## Amendment A1: the combined arm, with repeats (pane 1's GO; committed before any A1 call)

**Why.** H1 and H2 each failed alone. The premise flattens every `keepResult` to 0.07–0.29 whatever
the state shows. Without the premise and without the outputs, Jev is blind. Their combination is one
variable away from H2 (the question and premise) and one from H1 (the evidence), and it was never
run.

One correction to the note above. The 0.07 is the largest difference between single A0 **nouls**
across identical requests, not an AUC spread. The AUC spread across repeats has not been measured,
and this amendment measures it.

**Arm C.**
- **State:** H2's, meaning each call's `result` is `ok|error, N chars: <first 500 characters> …[k more
  chars]`. Its context is H2's with the re-run clause removed: *"…each tool output is cut to its first
  500 characters in `result` … Whatever is not kept is deleted permanently."*
- **Question:** H1's single-condition `use_tN` Noul, verbatim.
- **Code:** `replay.ts` arm `C`. The keyless `check` gives 8.3k–21.2k estimated request tokens per
  session, one batch each.

**Run.** `replay.ts a1 --live` runs A0 and C, 3 repeats each, on the same 7-session dev slice: 42
requests, about $0.03. The rows go to `a1-answers.jsonl` / `a1-requests.jsonl` / `a1-pass.json`, with
a `repeat` field.

**Report** (`replay.py`, keyless), per arm and repeat:
- AUC;
- needed kept and not-needed dropped at 0.5;
- the dev cut (the smallest observed score that drops ≥ 50% of not-needed), needed kept there with
  Wilson 95%, and the dev bar;
- per arm, the AUC mean and range over the 3 repeats.

**Gate.** The held-out goes ahead only if C meets the dev bar (needed kept with Wilson lower bound ≥ 0.80
at ≥ 50% of not-needed dropped) in **all 3** repeats. Otherwise the loop stops here. The result is
then recorded against NEGATIVE_EVIDENCE R99/R100 as their retry condition being tested, and the
held-out set is not labelled.

## A1 results (live, 2026-09-25, `jev-1.13.0`): STOP

`7f12e9f` committed A1 before the run. The run was one `replay.ts a1 --live` at 05:05:24Z: 42
requests, 534,273 input tokens, **$0.0224**. Re-score, keyless: `python3
work/loss-depth/compaction/replay.py`.

| arm | repeat | AUC | needed kept at 0.5 | not-needed dropped at 0.5 | dev cut | needed kept at dev cut | not-needed dropped there |
|---|---:|---:|---|---:|---:|---|---:|
| A0 | 1 | 0.652 | 0/50 | 165/165 | 0.16 | 33/50 (0.522–0.776) | 89/165 |
| A0 | 2 | 0.661 | 0/50 | 165/165 | 0.16 | 34/50 (0.542–0.792) | 96/165 |
| A0 | 3 | 0.650 | 0/50 | 165/165 | 0.16 | 34/50 (0.542–0.792) | 87/165 |
| C | 1 | 0.524 | 42/50 (0.715–0.917) | 34/165 | 0.68 | 28/50 (0.423–0.688) | 84/165 |
| C | 2 | 0.537 | 42/50 (0.715–0.917) | 37/165 | 0.68 | 27/50 (0.404–0.670) | 85/165 |
| C | 3 | 0.527 | 42/50 (0.715–0.917) | 31/165 | 0.68 | 28/50 (0.423–0.688) | 84/165 |

**Repeat noise.** A0 over 4 runs (the dev pass plus 3 repeats) spans AUC 0.648–0.661, and C over 3
spans 0.524–0.537. The arm differences in the dev pass (+0.015 for H2, +0.014 for H3) are the same
size as that spread, so neither is a measured gain.

**Gate: C meets the dev bar in 0 of 3 repeats, so the held-out is not run.** The `e7304e4` sample
stays unlabelled. The result is recorded under NEGATIVE_EVIDENCE R100 as its retry condition tested
and not met.

**What the loop found.** The two library design choices the autopsy named are real, but fixing them
did not produce a working keep signal on labelled data.
- **The premise and the two-condition question suppress the scores.** With them in place (A0, H2,
  H3), every `keepResult` sits in 0.07–0.29, whatever the state shows.
- **Removing them lets the scores spread (0.22–0.91) but does not rank need**, with or without the
  output: AUC 0.514 (H1) and 0.524–0.537 (C).
- **The best operating point on dev** is still near the library's own `keepResult` ranking: H2 at
  0.17, 39/50 kept (lower bound 0.648) with 84/165 dropped, below the bar.

**Total spend** for jev-9gtw.6: $0.0031 (token check) + $0.0142 (dev) + $0.0224 (A1) = **$0.0397**.

**NO-CLAIM.** 7 development sessions of one project and one model pin, with the studies' cut point
and 40-message horizon. This rules out these five designs on this curve. It says nothing about keep
signals outside Jev Nouls, such as the output-size and feature baselines in upstream
`tamaratran/fast-jev-compaction#52` (proxy labels, AUC 0.84–0.85), or about other models.
