# Does Jev-driven compaction drop a tool call a later turn needed? (bead `jev-x86y`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. **PREPARED-NOT-MEASURED** until the live
replay. Jev only (`jev-1.13.0`, pinned). No Anthropic API.

## Preregistered (committed before any session is sampled, labelled or replayed)

**Why.** `jev-0c6`'s live replay (`6fc95d1`) on a current claude-profile session dropped all 63
unpinned tool calls and kept none. Its six invariants only prove that nothing was invented and no
text vanished silently. Dropping everything is correct if the calls were old exploration and a
silent context loss if they were not. Nothing measured tells those apart. This readout labels, blind
to Jev, whether each tool call was needed later, and then compares Jev's keep decision to that label.

**Sessions** (`work/compaction-need/need.ts select`, run once after this commit, writing
`sessions.json`):
- **Eligible:**
  - omp session files of the jev project, top level only, under `~/.omp/agent/sessions/-Developer-jev/`
    and `~/.omp/profiles/*/agent/sessions/-Developer-jev/`;
  - last written before `CUTOFF = 2026-09-24T17:00:00Z`, so a still-open session is not eligible;
  - 200 KB to 3 MB;
  - at least 50 paired tool calls after `adaptOmpTranscript`.
- **Excluded:**
  - `01a0d3a7`, `jev-0c6`'s file B, whose outcome the author has seen;
  - `01a0b735`, file A, also seen and too small anyway.
- **Why not B.** Its keep/drop outcome is known, so it cannot be labelled blind by anyone who reads
  that receipt.
- **Sample:** 6 sessions, drawn with a seeded generator (mulberry32, seed 20260924) from the eligible
  list in path order. Each file's sha256 is recorded, and a file that changes after sampling makes
  every later step refuse.
- **Tuning:** none of the eligible sessions was used to write the compaction questions. Those come
  from `fast-jev-compaction` at `6e1da50`, written upstream, and `compaction/test/` holds no session
  id.

**The compaction point, fixed now.** For each session, the omp file goes through `adaptOmpTranscript`
into the library's messages.
- **Prefix:** everything through the message that holds the result of the **40th** paired tool call.
- **Horizon:** the next **40 messages** after it, or fewer if the session ends.
- The replay compacts the prefix only, which is what compaction would see at that moment. The
  horizon is what the session did next.
- The library pins calls in the last 6 prefix messages. Pinned calls are always kept, labelled like
  the others, and reported apart, in no rate.

**The need label**, one per prefix tool call, judged against the horizon:
- **`needed`:** a message in the horizon reads, cites, or depends on information whose source in the
  context is this call's result (or input). For example:
  - a later turn quotes or uses a value, line, path, error or finding that appeared in this result;
  - an edit whose old text was obtained by this read;
  - an answer or decision that rests on what this call returned.
- **`not-needed`:** no horizon message uses information whose source is this call.
- **`undecidable`:** the packet cannot tell, for example because the result was cut in the packet
  at the point that matters.
- A call whose result a later call simply re-obtains (the same file read again) is `not-needed`,
  unless a horizon turn uses the earlier result before re-obtaining it.

**Labellers.** Two fresh subagents, not the author, who has seen `jev-0c6`'s outcome. They are
spawned by pane 1 or by the author with this receipt and nothing else as the brief. Each is blind to
the other and to any Jev decision. None exists yet, since the replay refuses until labels are
committed.
- **Input:** the packets `need.ts packets` writes to `/tmp/x86y-packets/`, one per session. Each
  holds every prefix call's tool, input (up to 1,500 characters) and result (up to 3,000), and the
  horizon's messages (text up to 2,000, tool inputs up to 800, results up to 1,500).
- **Files:** `labels-1.jsonl` and `labels-2.jsonl`, one
  `{"session", "tool_use_id", "label", "horizon": <index or null>}` per call.
- **Adjudication:** pane 1 adjudicates every disagreement into `labels-adjudicated.jsonl`.
- **What is committed:** packets are never committed, because they hold session text. Only the ids
  (`calls.json`: session, `tool_use_id`, tool name, pinned) and the labels are.

**Live replay** (`need.ts replay --live`, one run, after `need.py ready` exits 0):
- **What it runs:** for each session, `compactMessages(prefix, …)` with `replay.ts`'s options
  (`keepThreshold 0.5`, `maxStateTokens 20000`, `truncateHeadChars 500`) plus
  `preserveRecentMessages 6` and `model: "jev-1.13.0"`.
- **Output:** each call's action (`keep`, `drop_result`, `drop_call`, or pinned) and its two nouls go
  to `decisions.jsonl`, joined by `tool_use_id`. `decisions-pass.json` records requests, input tokens
  and spend at $0.042 per million input tokens.
- **Refusals:** without `--live`, labels, or `TYPESAFE_API_KEY`, it prints `NOT_RUN` or `REFUSED`
  before any call.

**Metrics** (`need.py score`), over unpinned calls, each with counts and a Wilson 95% interval:
- **Primary:** recall on needed calls, where the result is kept verbatim (`keep`).
- **Secondary:** recall on needed calls, where the call is kept with its result verbatim or cut to its
  first 500 characters (`keep` or `drop_result`).
- The whole-call drop rate on not-needed calls (`drop_call`).
- Decisions on undecidable calls, reported and in no rate.
- A per-session table.
- Labeller agreement: exact agreement, and Cohen's kappa on needed vs not-needed.

**Reference bar**, numbers only; nothing changes in code on its account. Compaction would be safe to
turn on for live sessions only if the primary recall's Wilson lower bound is at least 0.80. Below
that, the readout says compaction drops needed context at the measured rate, and no ruling on Jev
is made.

**NO-CLAIM.** Six sessions of one project, one cut point per session, a 40-message horizon (need
beyond the horizon is not counted), labels from packet text that is itself truncated, and one model
pin.
