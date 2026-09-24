# Compaction keep rule: a lower cut or a reworded keep question on fresh sessions (bead `jev-jec6`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. **PREPARED-NOT-MEASURED** until the live
replay. Jev only (`jev-1.13.0`, pinned). No Anthropic API. This is the retry condition of
`NEGATIVE_EVIDENCE.md` R99.

## Preregistered (committed before any session is sampled, labelled or replayed)

**Why.** `jev-x86y` (`290efd7`) found that `fast-jev-compaction` at its default `keepThreshold 0.5`
kept 0/32 needed tool results verbatim (Wilson 0.000–0.107).
- No unpinned `keepResult` reached 0.5; the highest was 0.24.
- The AUC between needed and not-needed was about 0.69 on both keep nouls.

So the scores rank need somewhat, but the cut sits above all of them. Tuning a cut on those 164
labelled calls would fit them. This readout fixes candidate rules now and tests them on sessions
`jev-x86y` did not use. It scores the current rule on the same calls in one replay.

**Rules compared.** Each keeps a call's result verbatim when its score reaches the cut; pinned calls
are always kept.
- **C0, current:** the library's two keep questions (`questionsFor`, unchanged), `keepResult ≥ 0.5`.
- **C1, lower cut:** the same questions and the same answers as C0, with `keepResult ≥ 0.15`.
  - **Disclosed:** 0.15 was chosen by the author from `jev-x86y`'s descriptive distribution (mean
    `keepResult` 0.170 on needed calls, 0.143 on not-needed). It is fixed here and is not moved on
    the fresh set.
- **C2, reworded question:** one noul per candidate call on the same fitted state and batches the
  library uses, with `need ≥ 0.5`.
  - Instructions: *"The output of tool call {id} ({tool}, {n} chars) holds information the assistant
    will read, cite or act on in its next steps, and no later call in the history gives that
    information again."*
  - true: *"A next step would use a value, line, path, error or finding that appears in this output
    and in no later call's input or output."*
  - false: *"The output was exploration the assistant has moved past, or a later call re-read,
    re-ran or restated what it held."*
  - **Disclosed:** this wording restates the need label below, including the adjudicator's
    restatement reading from `jev-x86y`. The candidate asks Jev the question the labellers answer.

**Sessions** (`work/compaction-keep/keep.ts select`, run once after this commit):
- **Eligible:** `jev-x86y`'s eligibility rule (jev omp session files, top level, 200 KB–3 MB, at least
  50 paired tool calls), last written before `CUTOFF = 2026-09-24T17:45:00Z`.
- **Excluded:** every session `jev-x86y` sampled, including the A1-excluded one, and `jev-0c6`'s
  files A and B.
- **Order:** a seeded order (mulberry32, seed 20260925) over the eligible list, taking sessions in
  that order until **6 pass the rider screen**. If fewer than 6 pass, all that pass are used and the
  count is stated; fewer than 3 makes the readout UNDERPOWERED.

**Rider screen, before any labeller sees a packet.** A session is screened out if any tool call in
its prefix or horizon has an input that points into a rider-covered checkout (AGENTS.md
"Rider-Covered Repos").
- `RIDER_PATH` matches a path into `skillranker`, `skillranker-tip`, `dicklesworthstone-mirror`, a
  `franken*` directory or `asupersync`, or a `git -C` or `cd` into one.
- It is conservative: a name-only `git -C skillranker rev-parse` screens a session out too.
- The screen reads tool inputs only and records counts only (`sessions.json`: `screened_out_rider`).
- `packets` re-runs the screen and refuses on any hit.

**Compaction point and need label.** Both are `jev-x86y`'s, unchanged, and imported from
`work/compaction-need/need.ts`:
- the prefix runs through the result of the 40th paired tool call;
- the horizon is the next 40 messages;
- the library pins the last 6 prefix messages;
- labels are `needed`, `not-needed` or `undecidable`, as preregistered at `108d6bd`, plus the
  adjudication principle `jev-x86y` disclosed: a restatement in a later prefix call makes that
  later call the source.

**Labellers.** Two fresh subagents, not the author, blind to each other and to any score. They label
from `/tmp/jec6-packets/`, which is never committed. `labels-1.jsonl` and `labels-2.jsonl` hold one
`{session, tool_use_id, label, horizon}` per call. Pane 1 adjudicates every disagreement into
`labels-adjudicated.jsonl`. `calls.json` holds ids, tool names and the pinned flag only.

**Live replay** (`keep.ts replay --live`, one run, after `keep.py ready` exits 0). Per session:
- (A) `compactMessages(prefix)` with `jev-x86y`'s options, whose per-call `keepResult` gives C0 and
  C1;
- (B) the C2 question over the same `fitState` state and `batchCalls` batches.

`decisions.jsonl` gets `keepCall`, `keepResult` and `need` per call. `decisions-pass.json` gets
requests, input tokens and spend at $0.042 per million input tokens. Without `--live`, final labels
or the key, it refuses before any call.

**Metrics** (`keep.py score`), for each rule, over unpinned calls with Wilson 95% intervals:
- recall on needed calls, the result kept verbatim;
- the share of not-needed calls whose result is not kept.

Both are reported for the final labels and for each labeller alone.

**Bar, per rule.** It is met only if both hold:
- **(a)** the Wilson lower bound of recall on needed calls is at least **0.80**;
- **(b)** at least **50%** of not-needed results are not kept (point estimate), so keeping everything
  cannot pass.

A rule that meets the bar is a candidate for the live compaction binding only after a separate
commit with a non-author check. The installed hook yields today and stays that way until then.

**NO-CLAIM.** At most six sessions of one project, one cut point each, a 40-message horizon, and one
model pin. C1's cut and C2's wording were written with knowledge of `jev-x86y`'s aggregate results,
disclosed above. The test of both is these fresh sessions.

## Amendment A1: the rider screen covers every Dicklesworthstone repository (before any labeller)

**What happened.** The first `select` run, never committed, used the preregistered name list and
screened out nothing. The author then counted rider-name lines in the six packets (counts only) and
printed the first 110 characters of each tool input in the blocks that matched, but no result text.
That showed session `01a0c006` reading `eidetic_engine_cli`, a Dicklesworthstone repository the list
did not name, by `ls`, `cat`, `git -C` and `gh issue view --repo Dicklesworthstone/…`. No labeller had
seen a packet, no Jev call had been made, and no score existed.

**The added rule.**
- `RIDER_PATH` is built from `work/compaction-keep/rider-repos.txt`: the 215 public repository names
  of github.com/Dicklesworthstone, from `gh repo list Dicklesworthstone --limit 1000 --json name`,
  which is metadata, not the software. `skillranker-tip` and `dicklesworthstone-mirror` are added.
- A session is screened out when a tool input has a path component equal to one of those names, a
  `git -C` or `cd` into one, or any `Dicklesworthstone/` (a `gh --repo`, a URL).
- No name in the list equals a path component of any file jev tracks, so jev's own paths do not trip
  it. A tool named like a repo but run as a command (`ntm send`, `bun test`, `br`) does not trip it
  either.
- `select` and `packets` now refuse only when their output is committed, so this uncommitted draft
  was re-drawn by the same deterministic command.

**Result of the re-draw** (`sessions.json`). The seeded order is unchanged.
- Two sessions are screened out: `01a0c006` (16 calls into Dicklesworthstone repositories) and
  `01a0d38e` (5).
- **4 sessions pass, 161 prefix calls:** `01a0d0f2` (41), `01a0d11c` (40), `01a0d241` (40) and
  `01a0d288` (40).
- That is fewer than 6 and at least 3, so the readout runs on four sessions, as preregistered.
- The screened-out packets in `/tmp/jec6-packets/` were overwritten with a line saying not to label
  them, and `index.json` lists only the four.

**NO-CLAIM.** Four sessions, not six. The rules, metrics and bar above are unchanged.

**Disclosure: quoted source lines in `01a0d11c`** (pane 1's check against `rider-repos.txt`, before
dispatch, recorded on `jev-jec6`).
- Session `01a0d11c` passes the tool-input screen. It reads a jev file that quotes two single source
  lines, one from `frankengraphdb` and one from `frankensim`, each with repo@sha provenance.
- AGENTS.md allows reading another pane's report, so the session stays in.
- The labellers' packet for it therefore contains those two quoted lines, and the replay will send
  them to Jev inside that file's result.

## Results (live, 2026-09-24)

**Order in history:**
1. `0b74c55`: preregistration.
2. `1d7476a`: amendment A1.
3. `45c34a3`: the sample.
4. `81a00fd`: the 01a0d11c disclosure.
5. `a3d6204`: labeller 1.
6. `8ac6297`: labeller 2.
7. `9a4df90`: pane 1's adjudication of 18 disagreements. The file holds 10 not-needed, 3 needed and
   5 undecidable; the commit subject's counts are wrong, as recorded on `jev-jec6`.
8. The commit carrying this section.

`keep.py ready` exited 0 before the one live run. The run was
`infisical run … node --experimental-strip-types work/compaction-keep/keep.ts replay --live` at
18:12:13Z–18:12:16Z, with `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` unset.

**Spend.** 8 requests on `jev-1.13.0`: 4 library compaction batches and 4 C2 batches. Input was
72,649 tokens, which is **$0.0031**.

**Labels.**
- Final: 161 calls.
- Exact agreement 143/161. Cohen's kappa on needed vs not-needed 0.866 over 151 rows.
- 42 calls are pinned and always kept, in no rate: 19 needed, 21 not-needed, 2 undecidable.
- That leaves **119 unpinned calls: 30 needed, 85 not-needed, 4 undecidable.** Every call received
  a C2 `need` score.

**The three rules, final labels.** Each is counted over unpinned calls.

| Rule | needed kept verbatim | Wilson 95% | not-needed results dropped | Wilson 95% | bar |
|---|---:|---|---:|---|---|
| C0 current, `keepResult ≥ 0.5` | 0/30 | 0.000–0.114 | 85/85 | 0.957–1.000 | NOT MET |
| C1 lower cut, `keepResult ≥ 0.15` | **25/30** | 0.664–0.927 | 34/85 (40%) | 0.302–0.506 | NOT MET |
| C2 reworded, `need ≥ 0.5` | 6/30 | 0.095–0.373 | 79/85 | 0.854–0.967 | NOT MET |

**Against the bar** (recall lower bound of at least 0.80, and at least 50% of not-needed results
dropped), no rule meets it:
- C1 comes closest. It fails both parts: its recall lower bound is 0.664, and it drops 40% of
  not-needed results.
- C0 keeps nothing.
- C2 compacts hard but keeps 6/30 needed results.

**One labeller's labels alone.** Same outcome: no rule meets the bar.

| Labels | needed / not-needed | C0 kept | C1 kept | C1 dropped | C2 kept | C2 dropped |
|---|---|---|---|---|---|---|
| final | 30 / 85 | 0/30 | 25/30 (0.664–0.927) | 34/85 | 6/30 | 79/85 |
| labeller 1 alone | 31 / 83 | 0/31 | 26/31 (0.674–0.929) | 35/83 | 6/31 | 77/83 |
| labeller 2 alone | 32 / 84 | 0/32 | 26/32 (0.647–0.911) | 34/84 | 6/32 | 78/84 |

**Per session.** Pane 1 notes that most of `01a0d0f2`'s prefix results are shaken, which is why 4
of its 7 disputed rows went to undecidable.

| session | unpinned | needed | not-needed | undecidable | C0 kept needed | C1 kept needed | C2 kept needed | C0 dropped nn | C1 dropped nn | C2 dropped nn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01a0d0f2 | 26 | 12 | 11 | 3 | 0 | 10 | 1 | 11 | 7 | 11 |
| 01a0d11c | 34 | 8 | 26 | 0 | 0 | 7 | 4 | 26 | 4 | 25 |
| 01a0d241 | 28 | 8 | 20 | 0 | 0 | 6 | 0 | 20 | 8 | 20 |
| 01a0d288 | 31 | 2 | 28 | 1 | 0 | 2 | 1 | 28 | 15 | 23 |

Disputed rows by session: `01a0d0f2` 7, `01a0d11c` 4, `01a0d241` 4, `01a0d288` 3.

**Descriptive, not preregistered.**

| Score | mean on needed | mean on not-needed | max | AUC needed vs not-needed |
|---|---:|---:|---:|---:|
| `keepResult` | 0.175 | 0.159 | 0.23 | 0.633 |
| C2 `need` | 0.354 | 0.287 | 0.67 | 0.654 |

Both scores rank need weakly and sit in a narrow band. A cut low enough to keep most needed results
also keeps most unneeded ones.

**Rows.** `decisions.jsonl` holds per call: session, `tool_use_id`, pinned, `keepCall`, `keepResult`
and `need`. It holds no session text. Re-score, keyless: `python3 work/compaction-keep/keep.py score`.

**NO-CLAIM.**
- Four sessions of one project, one cut point each, a 40-message horizon, one model pin.
- C1's cut and C2's wording were chosen with knowledge of `jev-x86y`'s aggregates, as disclosed.
- The result says these three rules do not meet the bar here. It says nothing about other wordings
  or other models.
