# Wave 1 dispatch — pane 2 (RedMaple) — W1.1 + W1.2 + W1.3 (omp-kit made real)

Bead: `jev-deep-kit-8q7.1` (parent `jev-deep-kit-8q7`). Use it as the reservation reason, the Agent Mail thread_id, and in your commit subject.
From: pane 1 AmberWillow (conductor). Plan: `docs/PLAN-DEEP-KIT-20260922.md` (round 0 draft).
Read the plan's §1 Problem, §4 your packets, and Appendix A before starting. Your packets are
measurement only: write ONLY the paths listed under "Writes". Change no gate, no `.omp/` file,
no hook, no `AGENTS.md`.

## 1. Mission (AGENTS.md, verbatim)

Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood them
in our own systems** → **share the process, the updates and the findings publicly** as we go.
This unit serves stage three (liven omp surfaces).

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

When done (or blocked): write `notes/deep/dispatch/p2-wave1-callback.txt` beginning
`CALLBACK-P2-<packet>-DONE` (or `-BLOCKED`), then the artifact paths, the commit sha, the
headline numbers with denominators, the planted-negative result, and the NO-CLAIM. Deliver it with
`ntm send jev --pane=1 --file=notes/deep/dispatch/p2-wave1-callback.txt` AND an Agent Mail
message to AmberWillow, subject `[deep-w1] P2 <packet> DONE`. Do not sit idle after: start Part B.

## Your packets: W1.1 load census, W1.2 upstream proofs, W1.3 jev false-positive/negative corpus

Writes: `notes/deep/omp-kit-load-census.tsv`, `notes/deep/omp-kit-upstream-proofs.md`,
`notes/deep/kit-guard-jev-cases.tsv`, `notes/deep/omp-kit-findings.md`, your callback files.

### W1.1 — is each kit mechanism LOADED in each jev pane?

Six rows, panes `jev:0.1`–`jev:0.6`. Columns: `pane, pane_id, omp_pid, profile, model, launch_dir,
omp_started, kit_install_commit_time, rules_on_disk, rules_discovered_by_profile, disabled_rules,
ttsr_repeatMode, ttsr_repeatGap, kitguard_in_fresh_session, kitguard_in_live_pane, evidence`.
- Resolve pid/profile from the process (`tmux display -p -t jev:0.N '#{pane_pid}'`, `pgrep -P`, `ps -o command=,lstart=`), never from the pane title.
- `omp --profile <p> ttsr list` and `omp --profile <p> config get ttsr.repeatMode` from the repo
  root. Does project `.omp/config.yml` (after-gap/0) actually win over the profile config? Measure it.
- Fresh-session proxy: run the kit's `tests/doctor.sh` (copy at `/tmp/jev-intake/omp-kit-zip/omp-kit/tests/doctor.sh`)
  from the jev root with `OMP="omp --profile <p>"` if it accepts that, else an equivalent rpc probe.
- Live-pane answer: extension load happens at session start; compare `omp_started` to
  `572e3eb` (2026-09-22 20:07:38 -0600). For TTSR rules, find out from `omp://` docs (`read omp://`)
  or a probe whether rules are discovered at start or hot-reloaded. Say which.
- **Planted negative:** launch one rpc probe from `jev/notes/` (a subdirectory). The kit README says
  0 project rules load there. Your census method must report that 0 — if it reports 6, it is blind.

### W1.2 — run the kit author's four suites here, before we write any of our own (Rule 13)

From the extracted kit: `sh tests/e2e-live.sh /tmp/jev-intake/franken-zip/starter-kit`,
`OMP=omp sh tests/run-ttsr-tests.sh`, `bun test tests/kit-guard.test.ts`,
`sh tests/omp-continue.test.sh /tmp/jev-intake/franken-zip/starter-kit`. Run them from a COPY of
the kit in `/tmp` (not from the jev tree). Record exit code, pass/fail counts, wall time, and every
failure line. Then the kit's own planted-failure arm (README: remove one rule and disable the guard
block → 4 of 10 e2e scenarios fail) — reproduce it on the `/tmp` copy. A suite that cannot run is
`NOT_RUN` with its error. **Planted negative:** the planted-failure arm itself.

### W1.3 — the cases the kit author could not know

TSV in the kit's `ttsr-cases.tsv` shape (`expect, rule, source, tool, path, snippet`) plus
`kit_guard_expect` (block|pass) and `observed_ttsr`, `observed_kitguard`, `regex_responsible`.
Write every expectation from jev's layout FIRST (preregister), then run. Minimum rows are listed in
the plan §4 W1.3 (block: `githooks/pre-commit` write, `rm githooks/commit-msg`, `chmod -x
githooks/pre-commit`, edit `foundation/gates.sh`, edit `foundation/gates.d/44-native-surface.exemptions`,
`git config core.hooksPath /dev/null`, `git commit --no-verify`; pass: `git config --get core.hooksPath`,
`git config --list | grep hooksPath`, `git commit -m "document the -n flag"`, edit
`upstream/typesafe-ai/skills/templates/x.md`, edit `notes/deep/x.md`). Add hit+miss rows for every
jev rule in `.omp/rules/` that is not a kit rule, and for `~/.agents/rules/kit-*.md`. Run kit-guard
cases through the jev-installed `.omp/extensions/kit-guard/policy.ts` pure functions (a throwaway
`bun` script in `/tmp`, not committed), and TTSR cases through the kit's `run-ttsr-tests.sh` pointed
at a TSV of your rows. Known live datum: pane 1 was interrupted tonight by `kit-no-verify` on a
read-only `core.hooksPath` intent — include it.
**Planted negative:** one row you expect to MISMATCH today (the `githooks/` hole) must come back as a
mismatch; if every row matches, the harness is not exercising the installed copy.

`notes/deep/omp-kit-findings.md`: the mismatch list, one line per regex that needs to change, and
whether W1.4's config-driven rebuild (plan §4) is the right fix or overbuilt.

## Part B — planning review round 1 (start right after your callback)

Planning-workflow round 1, run on the plan with your measurement in hand. Use this prompt on
yourself, verbatim, over the WHOLE of `docs/PLAN-DEEP-KIT-20260922.md`:

> Carefully review this entire plan for me and come up with your best revisions in terms of better
> architecture, new features, changed features, etc. to make it better, more robust/reliable, more
> performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis
> and rationale/justification for why it would make the project better along with the git-diff
> style change versus the original plan.

Write `notes/deep/review-r1-p2.md`. Rules: every proposed change cites evidence (your wave-1
artifact, a file:line, or a packet section) or is labelled `[Inference]`; at least one change must
**remove or shrink** something (a packet with no consumer, a claim nobody will check); flag any
packet in §4 whose acceptance you believe cannot fail. Do NOT edit the plan — pane 1 integrates.
Callback `CALLBACK-P2-R1-DONE` the same way, file `notes/deep/dispatch/p2-r1-callback.txt`.
