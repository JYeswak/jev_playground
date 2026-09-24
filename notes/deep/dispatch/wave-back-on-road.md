# Wave: back on the road — 2026-09-23 evening (from pane 1 AmberWillow)

Joshua: "get this project back on the road", and on 2026-09-23: "this repo needs to PROVE jev work -
and we can only do that by using the API". Panes 2-6 were restarted at 19:04-19:07 so they load the
fixed stop hook (`5563da1`) and the kit rules; pane 2 started fresh (its session was full), panes
3-6 resumed their own sessions.

## Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them in
our own systems** → **share the process, the updates and the findings publicly** as we go.

## Rules for every unit in this wave

- **Live by default.** Any claim about how Jev behaves comes from live calls to the API: pinned
  `jev-1.13.0`, key via `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`,
  never printed. There is no call budget; state calls, latency and cost in the receipt. Keyless runs
  prove our code or a clone's code, never Jev.
- **Bar first:** commit the bar `[pending]` before the first live call. Before any live call on
  labelled rows, run `node work/jev-prevalence-first/prevalence-check.mjs <rows> --truth <label>` and
  paste its three lines.
- **Incumbent arm** (AGENTS.md Rule 14): the same state and questions through
  `upstream/typesafe-ai/system-one-adapter-python` against at least one LLM. Anthropic keys work; the
  OpenAI key returned 401 last night, so use Haiku unless you find a working OpenAI key.
- **Tools:** `rg` / `ast-grep` (search both JSON spellings), `ripwire <dir> --quality-delta` before
  calling code done, `skill://prevalence-first`, `work/oracle-kit`, Rust only via RCH.
- **One main:** commit on `main` only, explicit paths, `git diff -- <shared file>` shows only your
  hunks, never amend, push after each commit (`git push -q origin main`). No branches, no worktrees,
  no stashes; the pre-commit hook refuses commits off `main`.
- **Depth rule** (`DEPTH-DIRECTIVE.md`): a NOT-RUN carries command, verbatim output, `file:line` cause,
  two routes. Use subagents of your own for independent pieces and re-run their decisive commands.
- **Acceptance shape:** positive observable, planted negative, NO-CLAIM. Close a bead only with the
  command and its result; another pane verifies before close.

## Pane 2 — RedMaple (grok, fresh session): finish `jev-deep-kit-8q7.9`, live

You started fresh; your previous session's work is on disk. Read, in order:
`notes/deep/dispatch/p2-w70-new10.md`, `p2-w70-new10-live.md` (the live amendment and its hard safety
limits), `docs/demos/upstream-repro/w70-new10-t4-bar-20260923.md` (your committed bar), and the four
receipts you already wrote (`agent-desktop`, `jev-curate`, `jev-drone`, `typesafe-mario`
`-w70-20260923.md`).

1. **Canny, neo4jev, prism-liquidity-agent:** full W7.0 per the live amendment. Canny is the priority:
   it is the candidate fix for our own close-pump problem.
2. **jev-curate's 422s are a finding about the API contract, not a dead end.** 94 of 94 calls were
   rejected on `reasoning_depth.score.criteria` (list_type). Establish whose shape is wrong: compare
   the clone's request body with `docs-mirror/typesafe/primitives/score.md`, `primitives/advanced.md`
   and the SDK's Score types (`upstream/typesafe-ai/typesafe-sdk-python`), then send one live request
   with the corrected shape and show it scores. Rerun T4 on the same 30 rows with the corrected shape
   in a `/tmp` copy (never edit the clone). Draft, do not file, an upstream issue for the clone.
3. Callback `CALLBACK-P2-W70-NEW10-DONE`: one line per clone for all seven, live N and cost, result
   class. Comment the same on the bead.

## Pane 3 — TopazRaven: close `jev-deep-kit-8q7.6` (the 669-commit draw)

Your blocker is resolved by data: the draw is defined in
`docs/demos/upstream-repro/jev-review-real-diffs-20260919.md:19`, added in commit `02f6c5b`. Pin it
as **the non-merge commits reachable from `02f6c5b~1`** (`git rev-list --no-merges 02f6c5b~1`,
686 at that commit). The receipt's "669" does not reproduce from that commit; record the 17-commit
difference in your receipt and move on, do not chase it.

1. `isThinDiff` over all 686, keyless: thin vs substantial counts.
2. **Live:** the noul applicability gate on every substantial diff. As the bar is written
   (`notes/deep/w74-bars.md`), any substantial refusal fails it; report honestly, do not move the bar.
   Incumbent arm: always-scores on the same draw.
3. Receipt, then ask a non-author pane to verify (`ntm send` to pane 4 or 6) before closing.

## Pane 4 — MistyTurtle: `jev-deep-kit-8q7.8` (structured criteria variant), live

Bar in `notes/deep/w74-bars.md`. Read `docs/demos/upstream-repro/jev-curate-w70-20260923.md` first:
the API rejected jev-curate's Score criteria shape with 422, which is directly about how criteria
must be structured. Run `skill://prevalence-first` on your labelled rows before the first call and
paste its lines. Live calls against the bar, incumbent arm, receipt, non-author verify.

## Pane 5 — SunnyTiger: finish `jev-deep-kit-8q7.7` (select-on-A / report-on-B)

Your uncommitted work is in `work/oracle-kit/index.mjs` and `work/oracle-kit/test.mjs` (also saved in
`refs/backup/pause-20260923/jev-wip-public`). Finish it: tests green, a planted defect that fails
them, a `TESTS.md` row (check `git diff -- TESTS.md` shows only your hunk). Then use it on real live
rows already committed (candidates: `work/nev-differential/fresh-20260923/` injection rows, or the
jevcal threshold fit): pick the threshold on half A, report accuracy on half B, and show how much the
reported number moves compared with fitting and reporting on the same rows. If existing live rows
are too few, make more live calls rather than fewer. Receipt, non-author verify.

## Pane 6 — QuietHarbor: W2.6 CI, then `jev-qsg`

1. `.github/workflows/gates.yml` exists but was never committed: the `.gitignore` allowlist hides it.
   Add `!/.github/` to `.gitignore` and commit both. The workflow runs `foundation/gates.sh` on push to
   `main` with no key; stages that need omp report a typed SKIP counted separately from PASS.
2. Prove both directions on the real runner **without a red commit on main and without a branch**:
   a `workflow_dispatch` input that plants a defect in the runner's checkout must turn the run RED
   naming the plant; a normal push must be green with its typed skips listed. Receipt with both run
   URLs.
3. Then `jev-qsg`: `foundation/kit/packet.md:112` cites the untracked `notes/foundation-packet-p5.md`.
   Commit the draft or reword the line; your call, with the reason.
