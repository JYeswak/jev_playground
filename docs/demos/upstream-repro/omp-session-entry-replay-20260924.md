# Compaction replay on omp's on-disk SessionEntry files, live (bead `jev-0c6`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. Live lane, Jev only (`jev-1.13.0`).
This is the acceptance run the bead asked for. It supersedes the before-state in
[`omp-session-entry-adapter-20260919.md`](omp-session-entry-adapter-20260919.md) (`2cde8ac`: 0
`message_end` rows, `FAIL library saw tool calls`, exit 1).

**Code under test.**
- `compaction/src/omp-adapter.ts` at `50c57b7`, which added the SessionEntry `type: message`
  envelope, plus `0dc08bd`, a guard for bare-string content. It is unchanged since and was not
  edited here.
- The replay is `compaction/src/replay.ts`, unchanged, running `compactMessages()` from
  `fast-jev-compaction` at `6e1da50` with `keepThreshold 0.5`, `maxStateTokens 20000` and
  `truncateHeadChars 500`.
- The stream path's own suite still passes unchanged: `node --import tsx --test
  test/adapter.test.ts` gives 7/7.

**Command**, from `compaction/`, once per file:

    infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
      node --import tsx src/replay.ts <session.jsonl> --out <receipt.json>

`ANTHROPIC_API_KEY` and `OPENAI_API_KEY` were unset. A scratch `--import` preload in `/tmp`, not
committed, wrapped `fetch` to record each `api.typesafe.ai` response's status, model and usage. The
receipts' `transcript` paths are written with `~` for the home directory. The session files
themselves are not committed.

| | A: the file `50c57b7` cites | B: a current claude-profile session |
|---|---|---|
| file | `~/.omp/agent/sessions/-Developer-jev/2026-09-19T01-08-23-196Z_01a0b735-….jsonl` | `~/.omp/profiles/claude/agent/sessions/-Developer-jev/2026-09-24T13-42-19-003Z_01a0d3a7-….jsonl` |
| sha256 | `4c3db5bc…f1f2c` | `5f05860a…7dea7` |
| rows, `message` / `message_end` | 21 / 11 / 0 | 324 / 126 / 0 |
| messagesBefore → messagesAfter | 9 → 9 | 58 → 9 |
| tool calls seen / results paired | 1 / 1 | 68 / 68 |
| pinned / dropped by Jev / kept | 0 / 1 / 0 | 5 / 63 / 0 |
| chars before → after | 1,815 → 1,521 | 230,316 → 8,149 |
| requests, all HTTP 200, `jev-1.13.0` | 1 (2 questions) | 1 (126 questions) |
| input / output tokens | 1,155 / 40 | 20,315 / 2,380 |
| replay exit code | 0 | 0 |

**The six invariant checks, PASS on both files:**
1. output texts are a verbatim input subsequence;
2. every non-blank input text survives;
3. no invented ids, and results exact or truncated;
4. vanished messages carried no text;
5. candidates imply requests;
6. the library saw tool calls. This is the check that failed in `2cde8ac`.

Receipts: [`omp-session-entry-replay-20260924-a.json`](omp-session-entry-replay-20260924-a.json) and
[`omp-session-entry-replay-20260924-b.json`](omp-session-entry-replay-20260924-b.json). Both runs were
at 2026-09-24T17:11Z.

**Spend.** 2 Jev requests and 21,470 input tokens. At $0.042 per million input tokens, with output
free (`docs-mirror/typesafe/models.md`), that is **$0.0009**.

**Observed, not ruled on.** On file B, Jev kept none of the 63 unpinned tool calls, so the
compaction cut the transcript from 230,316 to 8,149 characters. The invariants say no text was
invented and nothing with text vanished silently. They do not say the dropped calls were
unimportant, and nothing here measures whether the compacted context would have served the
session.

**NO-CLAIM.** Two files and one request each. This shows the on-disk adapter feeds the library on
files omp wrote. It says nothing about keep/drop quality.
