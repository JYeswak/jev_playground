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
