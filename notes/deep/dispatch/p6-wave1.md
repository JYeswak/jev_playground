# Wave 1 dispatch — pane 6 (QuietHarbor) — W2.1 (honesty census: B11 + B12 + B13 as numbers)

Bead: `jev-deep-kit-8q7.5` (parent `jev-deep-kit-8q7`). Use it as the reservation reason, the Agent Mail thread_id, and in your commit subject.
From: pane 1 AmberWillow (conductor). Plan: `docs/PLAN-DEEP-KIT-20260922.md` (round 0 draft).
Read the plan's §1 Problem, §4 your packets, and Appendix A before starting. Your packets are
measurement only: write ONLY the paths listed under "Writes". Change no gate, no `.omp/` file,
no hook, no `AGENTS.md`.

## 1. Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them
in our own systems** → **share the process, the updates and the findings publicly** as we go.
This unit serves stage four (dogfood the honesty machinery on ourselves).

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

When done (or blocked): write `notes/deep/dispatch/p6-wave1-callback.txt` beginning
`CALLBACK-P6-<packet>-DONE` (or `-BLOCKED`), then the artifact paths, the commit sha, the
headline numbers with denominators, the planted-negative result, and the NO-CLAIM. Deliver it with
`ntm send jev --pane=1 --file=notes/deep/dispatch/p6-wave1-callback.txt` AND an Agent Mail
message to AmberWillow, subject `[deep-w1] P6 <packet> DONE`. Do not sit idle after: start Part B.

## Your packet: W2.1 honesty census

Writes: `notes/deep/honesty-census.md`, `notes/deep/false-close-census.tsv`, your callback files.

### (a) B13 — false-closure census, all rows, no sampling

Every closed bead in `.beads/issues.jsonl` (68 at dispatch; recount). TSV columns: `id, title,
closed_at, close_reason_len, close_reason, names_command(y/n), names_commit(sha or -),
commit_resolves(git cat-file -e: y/n), names_path(path or -), path_exists(y/n), class
(OK|REPAIRABLE|NO-EVIDENCE), repair_evidence(the commit/receipt you found elsewhere, e.g. by
`git log --all --grep=<id>` or a receipt naming the id)`. Also list the 13 in_progress and 14
blocked rows with `updated_at` age in hours and assignee. Parse with python json, and read both
`"k":` and `"k": ` spellings if you grep. Existing repair beads `jev-qex`, `jev-6fo`, `jev-lqz`
cover 3 rows — mark them. Do NOT edit beads in this wave.

### (b) B12 — claim coverage

Sentences in `README.md` that make a checkable claim (contain a numeral with a unit/ratio, or
"verified", "passes", "beats", "wins", "exits 0"). For each: is it registered in
`foundation/kit/claims.tsv` (by its `readme_pattern`)? Output the fraction with the sentence list.
Preregister the sentence-selection rule before counting.

### (c) B11 — resurrection candidates

Rows in `NEGATIVE_EVIDENCE.md` whose retry predicate names something observable today: a pinned SHA
(check `upstream/MANIFEST.tsv` / the clone's HEAD), a version (check the installed binary), or a
file (check existence). Count total rows with a retry predicate, rows with an observable one, and
rows whose trigger is satisfied NOW. List the satisfied ones with the evidence.

**Planted negative (each part):** (a) a synthetic closed row with `close_reason":"done"` in a
`/tmp` copy of the JSONL must classify NO-EVIDENCE; (b) a planted unregistered numeric sentence in a
`/tmp` README copy must count as uncovered; (c) a planted predicate naming a SHA that differs from
the manifest must count as satisfied. Report all three.

## Part B — planning review round 1 (start right after your callback)

Planning-workflow round 1, run on the plan with your measurement in hand. Use this prompt on
yourself, verbatim, over the WHOLE of `docs/PLAN-DEEP-KIT-20260922.md`:

> Carefully review this entire plan for me and come up with your best revisions in terms of better
> architecture, new features, changed features, etc. to make it better, more robust/reliable, more
> performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis
> and rationale/justification for why it would make the project better along with the git-diff
> style change versus the original plan.

Write `notes/deep/review-r1-p6.md`. Rules: every proposed change cites evidence (your wave-1
artifact, a file:line, or a packet section) or is labelled `[Inference]`; at least one change must
**remove or shrink** something (a packet with no consumer, a claim nobody will check); flag any
packet in §4 whose acceptance you believe cannot fail. Do NOT edit the plan — pane 1 integrates.
Callback `CALLBACK-P6-R1-DONE` the same way, file `notes/deep/dispatch/p6-r1-callback.txt`.
