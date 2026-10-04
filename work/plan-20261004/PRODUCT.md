# `classifier` — product plan (DRAFT for review; no beads yet)

One CLI that applies typed classifiers (Choice / Score / Noul, calibrated probabilities, an abstain
path) to the work this fleet touches. The backend is a flag, never the name: TypeSafe Jev
(`jev-1.13.0`) or the local Clef server, chosen per task by evidence.

Inputs (read-only research, 2026-10-04, in `specs/`): `classifier-areas.md` (10 areas ranked by our
receipts and 24 external sources), `cli-ergonomics-spec.md`, `cli-doctor-spec.md`,
`cli-installer-spec.md`, `clef-backend-spec.md`. Each cites file:line or a fetched URL; this file
cites them as `[areas §N]`, `[ergo §N]`, `[doctor §N]`, `[install §N]`, `[clef §N]`.

## 1. Decisions already taken

| Decision | Choice | By |
|---|---|---|
| Binary name | `classifier`, short alias `clf` (both free on PATH 2026-10-04). `jev` stays with hermes-jev-skills. Supersedes open decision D-2 in `specs/cli-ergonomics-spec.md` and `specs/cli-installer-spec.md`, which assumed the CLI keeps the `jev` name. | Joshua, conductor chat 2026-10-04 ~03:15Z, verbatim: "you do - its own path - classifier or something that properly names it not to a sspecific model" |
| Backend selection | `--backend jev\|clef\|auto`; `auto` routes to Clef only on a committed per-task win receipt | conductor [clef §3] |
| Exit codes | one dictionary for every command: 0 ok, 1 findings, 4 refused_unsafe, 5 retryable, 6 online_required, 64 usage, 66 no_input, 73, 74; no key = 1 | conductor [ergo §2.4] |
| Output | one envelope `classifier.<cmd>.v1 {ok,schema,status,data,meta,warnings,commands,errors}`; `doctor --json` is the raw doctor report, `--robot` wraps it | conductor [ergo §2.5] |
| Repair | dry-run unless `--apply` | conductor [doctor §3] |

## 2. Command tree

```
classifier                          # human overview, exit 0
classifier overview --json          # mega-command: state of every family, backend, install, anomalies
classifier ready <project-dir>      # the readiness audit for a NEW project (section 4)
classifier doctor | health | repair # [doctor]; every check names its data source
classifier install <target>         # [install]; cli | omp-project | omp-profile | daily | clef | all
classifier capabilities --json | robot-docs | schema   # generated from the family registry
classifier ask choice|score|noul    # raw primitive escape hatch
classifier skillgap mine|status     # ex `jev-skill-gap` (bin kept as a deprecation shim)

classifier <family> [run] <inputs>  # one decision ("run" implied)
classifier <family> batch           # NDJSON in, NDJSON out
classifier <family> explain         # exact request, threshold, calibration; zero calls
classifier <family> cases           # real fire/quiet fixtures for the family
classifier <family> eval            # replay recorded rows against the committed bar; RED = exit 1
classifier <family> calibrate       # fit/show a per-task Platt map; writes only with --apply
classifier <family> watch           # live flag rate vs calibration base rate, Jev-vs-Clef disagreement
```

Uniform flags: `--json/--robot`, `--backend`, `--fake`, `--dry-run`, `--explain`, stdin. Unknown
flags are usage errors with a did-you-mean (today they are silently ignored [ergo §0]).

## 3. The ten families (ranked by evidence [areas §1]; refuted designs never rebuilt [areas §2])

Exposure counts marked [sb] come from the 7-day census committed as a fixed receipt:
`specs/scoreboard-20261004T0230Z.txt` (`python3 work/omp-jev-review/surface-census.py --scoreboard
--days 7`, window ending 2026-10-04T02:17:33Z). Re-running the command gives a different rolling
window, not a check of these numbers.

| # | Family | Decision | Evidence today | Clef status | Ships first as |
|---|---|---|---|---|---|
| 1 | `rank` | top-1 passage/file for a query | omp `find` 32,301 calls/7 d [sb]; 576 vs 5,293 tokens per located file; FiQA top-1 76.2% vs BM25 39.3% | unmeasured | library + CLI; omp native already ON |
| 2 | `screen` | is this text an injection? | 268/300 caught, 5/300 false flags; public 639/662 | unmeasured (nimble/tev1 lose) | omp tool-result hook (shadow) |
| 3 | `gate` | is this command risky? (free cascade first) | cascade clears 133/135 free (PROVISIONAL: EVAL.md:3703 flags a conflicting jev-nr3c row at EVAL.md:3316, 42 scored / 3 cleared, and the verifier resolution is outstanding); Jev signal alone 0/403 harmful (REFUTED as a signal) | unmeasured | advisory hook; rubric must be frozen first [areas key findings] |
| 4 | `route` | which intent/queue, with abstain | Banking77, CLINC150 + abstain | **WIN** acc .962 vs .787, ECE .025 vs .102 | CLI + library; Clef primary |
| 5 | `diff` | is this hunk vendored / license-bearing? | prec .842 rec .640 vs license regex rec .130 (PASS with one preregistered accuracy-delta lock missed by 0.005, EVAL.md:3568); organic prevalence 0/39 | **WIN** AUC .839 vs .827 (raw ECE .311: never uncalibrated) | pre-merge CI check on imported code, not organic commits |
| 6 | `verify` | does the evidence support the claim? | SciFact/FEVER: accuracy tie, better Brier/ECE; numeric claims REFUTED | unmeasured | CLI + library |
| 7 | `memory` | is this recalled memory relevant now? | drop precision .985; 455k tokens removed/7 d (enforcing). Keep side fails: keep precision 0.190-0.242 across designs (NE:4869, 4897, 5019). Long-result keep/drop lost on safety in its first run (EVAL.md:3685) and is EXPLORED-only after (EVAL.md:3692, jev-dau5 replication pending) | too slow for the 1.5 s hook budget | omp extension (ON, drop side only) |
| 8 | `effort` | which model tier / effort for this task | gate-cascade cost win only; usage router and best-of-N LOST | unmeasured | shadow only until a bar passes |
| 9 | `watch` | is this agent idle, stuck, or promising-then-stopping? | idle watcher 10/10 recall, 0/10 false pages; smart stop 0 acts in 4,000 calls/7 d [sb] | unmeasured | fleet watcher (ON) |
| 10 | `score` | grade against a rubric | SST-5, STS-B wins; most judged TTSR rules < 0.80 precision; toxicity below constant | unmeasured | CLI + library |

Legacy verbs map onto families (`classify`→`route`, `rerank`→`rank`, `verify`, `score`, `gate`;
`jev-skill-gap` → `classifier skillgap`) with a deprecation stage, not a break [ergo §2.6].

## 4. `classifier ready` — what must be true before a new project gets a classifier

The command reads a project and a proposed decision and answers each row with PASS / FAIL / UNKNOWN
and the evidence path. Any FAIL stops the build. Rows from [areas §3], each with its source there:

1. A named decision, action and consumer (something reads the output).
2. Exposure: the case occurs on real traffic, and the positive class is not ~0 (the most common
   failure here: vendor-paste 0/39, compaction, conformal).
3. Enough positives to reject the bar (e.g. >= 30 flags for a 0.90/0.10 bar).
4. The constant (majority) baseline scored on the same rows; the design must beat it.
5. A deterministic incumbent and a shippable LLM incumbent on identical rows.
6. Blind labels, committed before any score exists, by non-authors; two labellers with kappa.
7. The answer is visible in the judged text (recognition, not forecasting: 0/12 forecasting wins).
8. The cost of each error type is written down, and the threshold comes from it.
9. An abstain path: malformed or low-confidence answers take the preregistered safe side.
10. The bar is committed in git before the first call and never moved.
11. A real-traffic corpus with disjoint dev and held-out splits (hash-disjoint replication check).
12. The model is pinned; calibration is fitted per task on dev and versioned with its cut.
13. At least 3 runs of each arm, including the stochastic incumbent.
14. Cost and latency fit the call site (e.g. hook budgets near 1.5 s rule out Clef today).
15. Fail semantics: no key, timeout or 5xx is NOT_RUN, never a silent pass.
16. Monitoring and recurring re-validation: live flag rate vs base rate, a labelled trickle.
17. Two classifiers cross-checked: Jev-vs-Clef disagreement is an anomaly signal, not accuracy.
18. Replay in CI: saved live cases replayed at $0; a coin-flip judge must turn the suite red.

Rows 16-18 are where "done is done, validation recurs": `classifier <family> watch` and
`classifier <family> eval` are the recurring checks, run by the daily job `install daily` sets up.

## 5. Build order (each task: failing test first, a planted negative, an acceptance command)

Detailed task lists with files and commands: [ergo §3] T1-T14, [doctor §5] T1-T11,
[install §3] 14 tasks, [clef §5] T0-T9. The merged order:

1. **Rename and shell** — `classifier`/`clf` bin, argv with did-you-mean, help/version exit 0,
   exit-code module, envelope (ergo T1-T4). Fixes the silent-flag and no-key-exit defects.
2. **Family registry and error rewrites** — `capabilities`, `robot-docs` and `schema` generated
   from one registry (ergo T5); error rewrites from observed transcripts (ergo T6). Needs step 1.
3. **Doctor that tells the truth** — Infisical key resolution, surface inventory from
   `work/jev-inventory/expected.json`, per-surface log freshness, declared-OFF-but-writing check
   (skill-hint), stale-schema writer check (injection v1 rows), cap reasons, file modes (doctor T1-T6).
   Needs step 1.
4. **Backend seam** — server side: Clef weights fingerprint, Clef transport with no auth header,
   per-task calibration files, `auto` evidence gate (clef T0-T5); CLI side: the `--backend` layer
   and provenance meta (ergo T7). `auto` sends 0 calls to Clef until clef T0. Needs steps 1-2.
5. **Families on the seam** — `route`, `rank`, `verify`, `score`, `gate` first (existing verbs),
   then `screen`, `diff`, `memory`, `watch`, `effort`, each with `cases` from real observations and
   `eval` against its committed bar (ergo T8-T12). Needs steps 2 and 4.
6. **Skill-gap migration** — `classifier skillgap mine|status` with the `jev-skill-gap` bin kept as
   a shim (ergo T13). Needs step 2.
7. **`ready`** — the section 4 audit as a command, reusing the existing checkers it names. Needs
   step 5.
8. **Installer** — manifest, idempotent install/uninstall/rollback, verification ladder that proves
   the surface fires, daily job (install T1-T14). Replaces the hand-placed machine-wide installs.
   Needs steps 3 and 5.
9. **Docs** — README "what is ON" rewritten as present state per surface: decision, measurement,
   how it is re-validated, what counts as an anomaly; docs drift check (ergo T14). Needs step 8.

## 6. What this plan does not claim

- No family is shipped by this document. Every row in section 3 cites existing evidence; any new
  claim (Clef on an unmeasured area, a new family's quality) needs a bar committed first.
- Clef is measured on two tasks only. "Prefer Clef" is a routing rule gated on receipts, not a
  default.
- The ten families are a ranking of where evidence exists today, not a promise that each will pass.

## 7. Next step

One non-author review of this file, then Joshua's go, then conversion to beads under one epic with
the section 5 order as edges.
