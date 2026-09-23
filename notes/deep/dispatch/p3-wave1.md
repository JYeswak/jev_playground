# Wave 1 dispatch — pane 3 (TopazRaven) — W4.1 + W4.2 (franken evidence on the jev ecosystem)

Bead: `jev-deep-kit-8q7.2` (parent `jev-deep-kit-8q7`). Use it as the reservation reason, the Agent Mail thread_id, and in your commit subject.
From: pane 1 AmberWillow (conductor). Plan: `docs/PLAN-DEEP-KIT-20260922.md` (round 0 draft).
Read the plan's §1 Problem, §4 your packets, and Appendix A before starting. Your packets are
measurement only: write ONLY the paths listed under "Writes". Change no gate, no `.omp/` file,
no hook, no `AGENTS.md`.

## 1. Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them
in our own systems** → **share the process, the updates and the findings publicly** as we go.
This unit serves stage four (dogfood) and five (share findings).

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

When done (or blocked): write `notes/deep/dispatch/p3-wave1-callback.txt` beginning
`CALLBACK-P3-<packet>-DONE` (or `-BLOCKED`), then the artifact paths, the commit sha, the
headline numbers with denominators, the planted-negative result, and the NO-CLAIM. Deliver it with
`ntm send jev --pane=1 --file=notes/deep/dispatch/p3-wave1-callback.txt` AND an Agent Mail
message to AmberWillow, subject `[deep-w1] P3 <packet> DONE`. Do not sit idle after: start Part B.

## Your packets: W4.1 dependency and citation audit, W4.2 rider exposure (facts only)

Writes: `notes/deep/franken-deps.tsv`, `notes/deep/franken-deps.md`, your callback files.

### W4.1

Every place the jev session leans on a franken repo (the 44 names are the `packets/` filenames
without `-assessment.md`; `asupersync` included):
1. **Citations in tracked jev files.** `git ls-files | xargs rg -n -i 'franken|asupersync'`
   (exclude `work/nev-*/*.jsonl` session-log corpora — those are data, not citations; say how many
   you excluded). Known anchors: `AGENTS.md:642`, `AGENTS.md:1576`,
   `foundation/gates.d/85-promotion-contract.sh:17`, `foundation/kit/demotion-rules.md` origins.
2. **Tools the jev panes invoke.** Which franken-derived binaries appear in jev-session transcripts
   (sessions whose cwd is `~/Developer/jev`, under the jev panes' profile session dirs). Count
   invocations per binary; name the repo each binary comes from and how you know.
3. **Shapes we adopted.** For each, the packet's verdict on whether that mechanism EXECUTES in the
   origin repo (claim inventory status, CI class C1–C6, release class R1–R3). Example to check first:
   jev's stage 85 adopted franken_engine's four-gate promotion shape; the synthesis says
   franken_engine's quality/perf workflows had zero runs and CI is red at the pin. Does jev cite the
   shape as proven? Quote both.
TSV columns: `surface, jev_location(file:line or command), franken_repo, how_we_use_it, packet_TRL,
packet_NODUS, packet_CI_class, packet_release_class, claim_we_rely_on, packet_status_of_that_claim
(demonstrated|partially|aspirational|disproven|stale) + packet file:line, rider(yes|no|none),
action(keep|re-tier|pin|monitor|drop), reason`.
**Planted negative:** include one row for a franken repo jev does NOT use (pick one from the 44 with
zero hits) and show your method returns zero for it; include `frankensearch` as the feasibility arm
(it must return hits — `AGENTS.md:642`).

### W4.2

Quote the rider verbatim from at least two `packets/*-assessment.md` license sections that read the
LICENSE text (not the synthesis summary); note wording differences between repos. Then facts only:
pane → model → lab (pane 1 anthropic/claude-opus-5-5; pane 2 xai-oauth/grok-4.7; panes 3–6 Muse
Spark 1.3 — verify from each pane's status line or profile), and which jev activities touch
rider-covered repos (reading packets is reading third-party assessments, not the repos; `fh`
indexing the mirror; copying a shape into a jev file). **No legal conclusion.** End the section with
the exact question for Joshua in one sentence.

## Part B — planning review round 1 (start right after your callback)

Planning-workflow round 1, run on the plan with your measurement in hand. Use this prompt on
yourself, verbatim, over the WHOLE of `docs/PLAN-DEEP-KIT-20260922.md`:

> Carefully review this entire plan for me and come up with your best revisions in terms of better
> architecture, new features, changed features, etc. to make it better, more robust/reliable, more
> performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis
> and rationale/justification for why it would make the project better along with the git-diff
> style change versus the original plan.

Write `notes/deep/review-r1-p3.md`. Rules: every proposed change cites evidence (your wave-1
artifact, a file:line, or a packet section) or is labelled `[Inference]`; at least one change must
**remove or shrink** something (a packet with no consumer, a claim nobody will check); flag any
packet in §4 whose acceptance you believe cannot fail. Do NOT edit the plan — pane 1 integrates.
Callback `CALLBACK-P3-R1-DONE` the same way, file `notes/deep/dispatch/p3-r1-callback.txt`.
