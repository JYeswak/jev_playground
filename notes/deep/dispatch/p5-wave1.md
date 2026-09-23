# Wave 1 dispatch — pane 5 (SunnyTiger) — W5.1 (the RULEBOOK pointed at jev)

Bead: `jev-deep-kit-8q7.4` (parent `jev-deep-kit-8q7`). Use it as the reservation reason, the Agent Mail thread_id, and in your commit subject.
From: pane 1 AmberWillow (conductor). Plan: `docs/PLAN-DEEP-KIT-20260922.md` (round 0 draft).
Read the plan's §1 Problem, §4 your packets, and Appendix A before starting. Your packets are
measurement only: write ONLY the paths listed under "Writes". Change no gate, no `.omp/` file,
no hook, no `AGENTS.md`.

## 1. Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them
in our own systems** → **share the process, the updates and the findings publicly** as we go.
This unit serves stage five (share the process and findings publicly).

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

When done (or blocked): write `notes/deep/dispatch/p5-wave1-callback.txt` beginning
`CALLBACK-P5-<packet>-DONE` (or `-BLOCKED`), then the artifact paths, the commit sha, the
headline numbers with denominators, the planted-negative result, and the NO-CLAIM. Deliver it with
`ntm send jev --pane=1 --file=notes/deep/dispatch/p5-wave1-callback.txt` AND an Agent Mail
message to AmberWillow, subject `[deep-w1] P5 <packet> DONE`. Do not sit idle after: start Part B.

## Your packet: W5.1 jev self-assessment packet

Writes: `notes/deep/jev-assessment.md`, your callback files.

Apply `/tmp/jev-intake/franken-zip/RULEBOOK.md` v1.0 to THIS repo exactly as it was applied to the
44 mentor repos. Read two real packets first as exemplars of depth and tone — e.g.
`packets/franken_threed-assessment.md` (the only analyst-executed repro) and
`packets/frankensqlite-assessment.md` — and match their section structure.

Required: header §4.1 (pin = full HEAD hash + commit date at your start; method: what you ran and
what you did not); §4.2 verdict with TRL and NODUS ring per the ring rules; §4.3 claim inventory
≥10 claims drawn from `README.md` and `VERDICT.md` with status (demonstrated / partially /
aspirational / disproven / stale) and evidence tier; §4.4 architecture reconstructed from the tree
(`git ls-files` counts by top dir, `foundation/gates.d` stage count, test counts you actually ran);
§4.5 benchmark and conformance audit (maintainer vs independent — every Jev number in README comes
from our own harness; say so); §4.6 who owns the lane; §4.7 ≥3 strengths, ≥3 weaknesses, bear-case
steelman; §4.8 license (read `LICENSE` verbatim) and governance (bus factor = count distinct human
committers; count agent co-author trailers); §4.9 NODUS factsheet; §4.10 Wardley; §4.11 trajectory
[Inference] with revisit triggers; §4.12 limitations; the eight deepening questions (§5) one
paragraph each; the four lenses (§6); then the §8 QA checklist, every box ticked or failed.

CI class: jev has no `.github/` — classify it honestly (C4 unless something changes before you pin).
Release class: `git tag -l` and `gh release list` for `JYeswak/jev_playground`.
Tiers: a jev claim about jev is `[Maintainer claim]` until YOU re-run the command behind it — then
`[Verified]`. Re-run at least 5 of the 10 (pick the cheapest keyless commands in README's
"The thing to run").

**Planted negative:** the §8 QA checklist must fail at least one box on your first draft if the
draft is incomplete — run it against a copy with §4.12 deleted and confirm your checklist catches it.
Report whether it did.

## Part B — planning review round 1 (start right after your callback)

Planning-workflow round 1, run on the plan with your measurement in hand. Use this prompt on
yourself, verbatim, over the WHOLE of `docs/PLAN-DEEP-KIT-20260922.md`:

> Carefully review this entire plan for me and come up with your best revisions in terms of better
> architecture, new features, changed features, etc. to make it better, more robust/reliable, more
> performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis
> and rationale/justification for why it would make the project better along with the git-diff
> style change versus the original plan.

Write `notes/deep/review-r1-p5.md`. Rules: every proposed change cites evidence (your wave-1
artifact, a file:line, or a packet section) or is labelled `[Inference]`; at least one change must
**remove or shrink** something (a packet with no consumer, a claim nobody will check); flag any
packet in §4 whose acceptance you believe cannot fail. Do NOT edit the plan — pane 1 integrates.
Callback `CALLBACK-P5-R1-DONE` the same way, file `notes/deep/dispatch/p5-r1-callback.txt`.
