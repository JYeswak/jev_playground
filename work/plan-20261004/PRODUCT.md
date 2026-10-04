# `classifier` — product plan (beads: epic jev-b35c; building waits for Joshua's go)

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
| 4 | `route` | which intent/queue, with abstain | Banking77, CLINC150 + abstain | **Accuracy WIN** .962 vs .787 (McNemar 107/2). Calibration TIE once both get the same dev-fitted Platt map: ECE .0246 vs .0276, diff CI [-.010, +.037] (specs/advanced-mathops.md section A) | CLI + library; Clef primary for accuracy |
| 5 | `diff` | is this hunk vendored / license-bearing? | prec .842 rec .640 vs license regex rec .130 (PASS with one preregistered accuracy-delta lock missed by 0.005, EVAL.md:3568); organic prevalence 0/39; cut 0.35 was Youden-tuned on a 60/60 set and predicts precision .21 at 5% prevalence (specs/advanced-mathops.md) | **TIE** AUC .839 vs .827, DeLong p=.67; Jev+Clef logistic combination AUC .862 vs Jev .828 (p=.005) | pre-merge CI check on imported code, not organic commits |
| 6 | `verify` | does the evidence support the claim? | SciFact/FEVER: accuracy tie, better Brier/ECE; numeric claims REFUTED | unmeasured | CLI + library |
| 7 | `memory` | is this recalled memory relevant now? | Drop precision .985 on the blind 30/30 check. Of the ~455k tokens counted over 7 d [sb window], 312k came from the mechanical top-3 cut (`cap3-pruned`, no Jev), 160k are Jev `scored` would-drops that are removed only on enforced turns (368 enforced turns in 7 d), 39k memo. The enforce switch file has been absent since 2026-10-04T01:59Z, so Jev drops are not applied (scoring continues). Keep side fails: keep precision 0.190-0.242 across designs (NE:4869, 4897, 5019). Long-result keep/drop lost on safety in its first run (EVAL.md:3685) and is EXPLORED-only after (EVAL.md:3692, jev-dau5 replication pending) | too slow for the 1.5 s hook budget | omp extension (drop side only; enforcement switch currently off) |
| 8 | `effort` | which model tier / effort for this task | gate-cascade cost win only; usage router and best-of-N LOST | unmeasured | shadow only until a bar passes |
| 9 | `watch` | is this agent idle, stuck, or promising-then-stopping? | idle watcher 10/10 recall, 0/10 false pages; smart stop runs ~4,000 calls/7 d [sb], but its decisions are not persisted (scoreboard receipt line 76), so the only measured outcome is 76 checks / 0 continuations (EVAL.md:3292) and 100 re-asked stops / 0 promise-then-stop (work/jev-nwo1-verdict.md, 8875abfd) | unmeasured | fleet watcher (ON) |
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

Beads (epic `jev-b35c`; edges are real prerequisites only, 0 cycles):

| Step | Bead | Needs |
|---|---|---|
| Rename and shell | `.1` | — |
| Registry and error rewrites | `.2` | `.1` |
| Doctor | `.3` | `.1` |
| **Measurement core** (D2-D7, D17) | `.10` | — |
| Backend seam + combine/cascade/llm (D8, D10) | `.4` | `.1`, `.2`, `.10` |
| Families | `.5` | `.2`, `.4`, `.10` |
| Skill-gap migration | `.6` | `.2`, jev-daily-omp-skill-gap-mining-7jci |
| `ready` | `.7` | `.5`, `.10` |
| Installer | `.8` | `.3`, `.5` |
| Docs | `.9` | `.8` |
| `ask` bundle (D11) | `.11` | `.4` |
| `chain` + rank long-doc (D12) | `.12` | `.2`, `.4` |
| `extract` family (D13) | `.13` | `.2`, `.4` |

Incidents outside the epic: `jev-08hr` (memory enforce switch absent), `jev-35sg` (skill-hint
running while OFF), `jev-s0ve` (memory filter 45.5% deadline-keep; `jev-9cqw` waits on it).

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
- The memory row's ".985 drop precision" is near the always-drop baseline (.94, p=.080); the number
  that decides safety is relevant memories dropped, 1/6 (Wilson [.03, .56]) (specs/advanced-mathops.md).

## 7. Decision register

Every structural choice, with what it beat, the evidence, whether we borrow or write it, and what
would reverse it. Sources: `specs/advanced-mathops.md` [M], `specs/advanced-literature.md` [L],
`specs/advanced-repos.md` [R], `specs/ideas-*.md` [I], the five CLI specs. Every number is a
recomputation on committed rows unless marked as an upstream claim (UPSTREAM).

| # | Decision | Chosen | Rejected | Evidence | Borrow / write | Reversed if |
|---|---|---|---|---|---|---|
| D1 | Name | `classifier` / `clf`; backend is a flag | `jev` (owned by hermes on PATH); a model name | Joshua verbatim (section 1); `command -v` 2026-10-04 | write | — |
| D2 | Calibrating backends | the same pipeline for every backend: floor probabilities at 0.005, fit on dev (temperature, Platt, isotonic), report ECE with its noise floor and a bootstrap CI, compare with paired tests | calibrate one backend, compare against the other raw | Jev ECE .1017 -> .0276 with the same Platt map [M A]; 181/3,080 Banking77 rows put exactly 0.00 on gold [R]; noise floor ECE ~.045 at n=60 (UPSTREAM jev-exploration) [R]; Guo et al. 2017 [L] | PORT the design of franken_nlp `src/calibration.rs` (digest-bound splits, temperature, isotonic PAV, seeded bootstrap, abstain = exit 0) [R]; write in TS, zero deps | symmetric recalibration on committed rows does not reproduce Jev ECE ~.028 |
| D3 | Setting cuts | expected-cost cut at projected real prevalence; Neyman–Pearson cut from negatives only where positives are scarce (29/59/149/299 negatives for FPR .10/.05/.02/.01, δ=.05) | Youden on a balanced dev set; fixed 0.5 | Youden 0.35 predicts precision .21 at 5% prevalence, matching organic .19-.24 [M]; NP umbrella (Tong et al.) [L K1] | write (order statistic + cost matrix); idea from process_triage expected-loss action [R] | an NP cut on held negatives exceeds its stated FPR bound in replay |
| D4 | Before shipping any bar | project the result to real prevalence (BBSE) and run a KS alarm on live scores | trust the demo-set number | skill veto .990 -> .335 was predictable: projection gives .40-.63, KS p≈.001 [L R4] | write; QuaPy as idea [R] | projection fails to predict a known demo-to-organic drop when replayed |
| D5 | Abstain path | split-conformal LAC answer sets (`route --set`), refuse when exchangeability is not declared | top-k lists; a fixed confidence cut | α=.10: coverage .903, mean size 1.67, 58.5% singletons at 94.9% accuracy; worst class .152 (marginal guarantee only); α=.05 degenerate because of exact zeros [L R2] | write the algorithm (small); borrow franken_nlp's exchangeability-memo refusal [R] | coverage on a fresh disjoint split falls outside its finite-sample band |
| D6 | Many tests | Benjamini–Hochberg across the ledger; e-BH within a batch; confidence sequences to stop shadow phases | per-bar α=.05 with no correction | 74 bars at .05 imply ~3.7 false passes [M] | write; e-BH idea from process_triage [R] | — (accounting rule) |
| D7 | Drift and canaries | test against same-model rerun spread | textbook McNemar null | two runs of pinned jev-1.13.0 differ at p=.0076 on 3,080 rows [L R5] | write | — |
| D8 | Combining backends | per-task logistic combination and Jev-first cascade, only with a committed receipt | always one backend | combination AUC .862 vs .828 (p=.005); cascade sends 42% to Clef, .942 vs .962 [M] | write | the combination loses its gain on a disjoint split |
| D9 | Rejected designs | do not build: agreement/Dawid–Skene accuracy estimates, juries, self-consistency, BM25-margin cascade for `find` | — | Dawid–Skene ranks Clef .872 / Jev .924 against true .962 / .787; errors correlated (.182 vs .059) [L R3]; self-consistency AUROC .525 vs 1−conf .843 [L R6]; BM25 cascade −3.4 pp for −20% calls [L R7] | — | new evidence on our rows |
| D10 | Comparison arm | `--backend llm` through system-one-adapter-python as the shippable-LLM incumbent in every `eval` | no LLM arm | ML Test Score "simpler model" test [areas]; adapter gives the same API over any LLM [I] | USE-AS-BASELINE (external process; licence check before vendoring) | — |
| D11 | Multi-question calls | `ask` takes a bundle of mixed questions over one state | one primitive per call | parallel_questions cookbook: 12.2x cheaper, 10x faster (UPSTREAM, not re-run) [I] | write | bundle answers differ from single calls beyond run-to-run spread |
| D12 | Long documents / chained steps | `chain` (propose, check, act); `rank` long-doc = section tree with a beam of 3 and a Noul check | single flat Choice | jev-doc-search, 2 example questions (UPSTREAM) [R]; hierarchical beam REFUTED for routing (NE:3604), untested for document search | borrow the algorithm idea; write | fails its own committed bar on a doc-search set |
| D13 | Extraction | an `extract` family: code proposes candidates, a Choice picks one, code renders | free-text generation | 5 of 18 cookbooks use this shape [I] | write | — |
| D14 | CLI shell, doctor, installer | robot mode, `capabilities --json`, golden schema tests; doctor/health/repair; manifest installer | ad-hoc verbs | coding_agent_session_search robot mode [R]; the three CLI skills (specs/cli-*.md) | borrow conventions; write | — |
| D15 | Dependencies | port algorithms, import nothing heavy | import MAPIE/TorchCP/alibi-detect | licences: alibi-detect BSL, TorchCP LGPL, Jev-Calibration unlicensed [R]; AGENTS.md design decision 6 | port | — |
| D16 | Memory filter | fix the deadline model, then measure P(drop given relevant) on >= 59 sampled relevant memories, then decide enforcement | enforce on drop precision | 45.5% of items time out (1,328/2,921); drop precision .985 vs always-drop .94 (p=.080); relevant dropped 1/6 [M]; relabel 22/30 < 27 (jev-9cqw) | write | — |
| D17 | Labels | prediction-powered inference for metrics on organic traffic before spending labels | label everything / label nothing | PPI (Angelopoulos et al.) [L]; ~0 organic positives killed m94x, 9kmq | write; ppi_py as reference [R] | PPI interval no narrower than labels-only on our data |
