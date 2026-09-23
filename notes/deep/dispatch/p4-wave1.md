# Wave 1 dispatch — pane 4 (MistyTurtle) — W3.1 (franken mechanisms scored against jev)

Bead: `jev-deep-kit-8q7.3` (parent `jev-deep-kit-8q7`). Use it as the reservation reason, the Agent Mail thread_id, and in your commit subject.
From: pane 1 AmberWillow (conductor). Plan: `docs/PLAN-DEEP-KIT-20260922.md` (round 0 draft).
Read the plan's §1 Problem, §4 your packets, and Appendix A before starting. Your packets are
measurement only: write ONLY the paths listed under "Writes". Change no gate, no `.omp/` file,
no hook, no `AGENTS.md`.

## 1. Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them
in our own systems** → **share the process, the updates and the findings publicly** as we go.
This unit serves stage two (build tools from what survives) and four (dogfood).

Scope (Joshua, 2026-09-22): **the `jev` NTM session only.** Do not read, measure, or write
anything in any other NTM session (`cfsios`, `omp-test`) or under `~/.omp/agent/` or
`~/.omp/profiles/*/agent/`. Read-only reads of the jev panes' own profile config are allowed.

## 2. Inputs (pinned — cite by these, never by memory)

- omp-kit: `/Users/josh/Downloads/omp-kit (1).zip`, sha256 prefix `cea66f8bcb616737`,
  extracted read-only at `/tmp/jev-intake/omp-kit-zip/omp-kit/`.
- franken-assessments: `/Users/josh/Downloads/franken-assessments-44-v8.zip`, sha256 prefix
  `70628b1f9a6d6f61`, extracted read-only at `/tmp/jev-intake/franken-zip/`
  (`RULEBOOK.md`, `packets/*-assessment.md` ×44, `synthesis/*.md`, `synthesis/planning/*.md`,
  `starter-kit/`). If `/tmp/jev-intake` is gone, re-extract with `unzip -oq <zip> -d <dir>`.
- jev HEAD at dispatch: `572e3eb`. Record the HEAD you actually ran at in every receipt.

## 3. Tools, by name, and what each is for

- `rg` for literals; `ast-grep` for structure. **Search both spellings** of any JSON key
  (`"k":` and `"k": `) — the spaced form once matched zero files and produced a false conclusion.
- `ripwire <dir> --grep=<name> --legend=compact` for a symbol's code hits (its `--uses` is blind to
  data names); `ripwire <dir> --quality-delta` before calling any code done.
- `fh search "<mechanism>"` / `fh why <row>` for mentor precedent over the mirror — only when the
  packet text is not enough; cite `repo@sha:path:line`.
- `br show <id>` / `br ready --json` for beads (never hand-edit `.beads/issues.jsonl`).
- `omp --mode=rpc --max-time=<n>` for a fresh-session probe; `negotiate_protocol` first; an empty
  read is `TIMEOUT_UNMEASURED`, never `ABSENT`. It spawns a NEW session, it never attaches to a pane.
- `am file_reservations reserve ~/Developer/jev <YOU> <PATHS>... --exclusive --reason <packet>`
  before writing; conflicts first with `am file_reservations conflicts`.

## 4. Mining process, in order (skipping a step is how four wrong numbers were made in one day)

1. Read the artifact and cite `file:line` for every fact.
2. Write the expectation BEFORE running (preregister in your output file, in a section titled
   `Preregistered` committed before or with the results).
3. Use data you did not author (the archives, the tree, the transcripts) — not a fixture you wrote.
4. Include a feasibility arm that ought to pass, so a zero is distinguishable from a blind instrument.
5. State the denominator beside every number.
6. Report a verdict a non-author can check by re-running your exact command.

## 5. Acceptance shape

- **Positive observable:** the artifact(s) under "Writes", committed at a commit that is an
  ancestor of `main`, with every row carrying its command or `file:line`.
- **Planted negative:** named per packet below — the check that proves your instrument can say no.
- **NO-CLAIM:** one line naming exactly what you did not run or cannot conclude.
- `DEFER`, `BLOCKED`, `REFUSE`, `PREPARED-NOT-MEASURED` are real outcomes and beat a manufactured number.

## 6. Commit discipline (AGENTS.md "Save only your work")

Reserve → edit → `git add <your exact paths>` (never `-A`/`.`) → `git diff --cached --stat` must list
only your paths → commit on `main`, never amend, subject carries its level: `[selftest]`, `[test]`,
`[oracle]`, or `[pending]`. The pre-commit and commit-msg hooks in `githooks/` run; if one refuses,
read its stderr and fix the cause.

## 7. Callback

When done (or blocked): write `notes/deep/dispatch/p4-wave1-callback.txt` beginning
`CALLBACK-P4-<packet>-DONE` (or `-BLOCKED`), then the artifact paths, the commit sha, the
headline numbers with denominators, the planted-negative result, and the NO-CLAIM. Deliver it with
`ntm send jev --pane=1 --file=notes/deep/dispatch/p4-wave1-callback.txt` AND an Agent Mail
message to AmberWillow, subject `[deep-w1] P4 <packet> DONE`. Do not sit idle after: start Part B.

## Your packet: W3.1 mechanism transfer matrix

Writes: `notes/deep/mechanism-transfer.tsv`, `notes/deep/mechanism-transfer.md`, your callback files.

Rows — count each source list and state the count in the md so a reader can check completeness:
- 14 concepts: `/tmp/jev-intake/franken-zip/synthesis/cross-pollination.md` §1–§14
- 23 gates: `synthesis/planning/execution-readiness.md` Gate 1–23
- 12 composite items: same file, "Strongest-observed composite checklist"
- 11 negative patterns: `synthesis/negative-patterns.md` P1–P11 (score: does jev exhibit it?)
- 28 checklist items A1–A14, B1–B14: `starter-kit/CHECKLIST.md`, re-scoring `notes/kit-gap-v8.tsv`.
  Known stale row: B5 cites `.git/hooks/commit-msg` and says "no pre-commit hook", but
  `core.hooksPath` is `githooks/` (`.git/config:8`) and `githooks/pre-commit` exists with two lanes
  and no claim canary. Correct it with evidence.

Columns: `id, source(file:section), jev_status(HAVE|PARTIAL|GAP|NA), evidence(path:line or command),
executes(yes|no|unknown), execution_evidence(command + observed output, run by you now),
smallest_honest_version, cost(files/hours), defect_class_it_catches, rule12(adopt|refuse),
refusal_fields(cost; missed defect class; what we lose — all three or blank), falsification_experiment`.

The `executes` column is the point: the synthesis's finding 2 is "mechanism existence is
systematically ahead of execution". That is a claim about jev until you run each HAVE. A HAVE with
`executes=unknown` is PARTIAL. Where a jev stage has `--selftest`, run it and paste the exit code.
Rule 12 binds: a refusal needs all three fields; "we are smaller" is not a field.

**Planted negative:** pick one row you would score HAVE, break its mechanism in a `/tmp` copy of the
file (never the tree), and show your `execution_evidence` command reports the break. If it does not,
your evidence column is measuring existence, not execution.

In the md: the top 5 adoption candidates ranked by (defect class already observed in jev) × (cost),
each with the jev file it would land in.

## Part B — planning review round 1 (start right after your callback)

Planning-workflow round 1, run on the plan with your measurement in hand. Use this prompt on
yourself, verbatim, over the WHOLE of `docs/PLAN-DEEP-KIT-20260922.md`:

> Carefully review this entire plan for me and come up with your best revisions in terms of better
> architecture, new features, changed features, etc. to make it better, more robust/reliable, more
> performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis
> and rationale/justification for why it would make the project better along with the git-diff
> style change versus the original plan.

Write `notes/deep/review-r1-p4.md`. Rules: every proposed change cites evidence (your wave-1
artifact, a file:line, or a packet section) or is labelled `[Inference]`; at least one change must
**remove or shrink** something (a packet with no consumer, a claim nobody will check); flag any
packet in §4 whose acceptance you believe cannot fail. Do NOT edit the plan — pane 1 integrates.
Callback `CALLBACK-P4-R1-DONE` the same way, file `notes/deep/dispatch/p4-r1-callback.txt`.
