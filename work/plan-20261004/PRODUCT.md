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
| Exit codes | one dictionary for every command: 0 ok, 1 findings, 3 refused (e.g. an unoffered label), 4 refused_unsafe, 5 retryable, 6 online_required, 64 usage, 66 no_input, 73, 74; no key = 1 | conductor [ergo §2.4]; `3` added 2026-10-04 (converge r2 L4: jev-b35c.1's test already required it) |
| Output | one envelope `classifier.<cmd>.v1 {ok,schema,status,data,meta,warnings,commands,errors}`; `doctor --json` is the raw doctor report, `--robot` wraps it | conductor [ergo §2.5] |
| Repair | dry-run unless `--apply` | conductor [doctor §3] |
| Package and channel | `jev-kit` (kit/package.json) stays the package name and is not published in stage 1: `classifier` is taken on npm, jev-r1vp installs from a fresh clone of origin/main, and publishing is irreversible. bins are exactly `classifier`, `clf` and the `jev-skill-gap` deprecation shim; no `jev` bin (mission rejection, .omp/mission.toml:16). A package-name/channel decision (owner Joshua) is opened only if a later stage needs a published package. | converge r4 (Cli batch), 2026-10-05; reversible plan text |

## 2. Command tree

```
classifier                          # human overview, exit 0
classifier overview --json          # mega-command: state of every family, backend, install, anomalies
classifier ready <project-dir>      # the readiness audit for a NEW project (section 4)
classifier doctor | health | repair # [doctor]; every check names its data source
classifier install <target>         # [install]; cli | omp-project | omp-profile | daily | clef | all
classifier capabilities --json | robot-docs | schema   # generated from the family registry
classifier ask choice|score|noul    # raw primitive escape hatch (one question; the mixed-bundle mode is jev-b35c.11, out of stage 1)
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

## 3. Legacy ten families (evidence only; the plan of record is the sixteen decision families in section 8)

Exposure counts marked [sb] come from the 7-day census committed as a fixed receipt:
`specs/scoreboard-20261004T0230Z.txt` (`python3 work/omp-jev-review/surface-census.py --scoreboard
--days 7`, window ending 2026-10-04T02:17:33Z). Re-running the command gives a different rolling
window, not a check of these numbers.

| # | Family | Decision | Evidence today | Clef status | Ships first as |
|---|---|---|---|---|---|
| 1 | `rank` | top-1 passage/file for a query | omp `find` 32,301 calls/7 d [sb]; 576 vs 5,293 tokens per located file; FiQA top-1 76.2% vs BM25 39.3% | unmeasured | library + CLI; omp native already ON |
| 2 | `screen` | is this text an injection? | 268/300 caught, 5/300 false flags; public 639/662 | unmeasured (nimble/tev1 lose) | omp tool-result hook (shadow) |
| 3 | `gate` | is this command risky? (free cascade first) | cascade clears 133/135 free (PROVISIONAL: EVAL.md:3703 flags a conflicting jev-nr3c row at EVAL.md:3316, 42 scored / 3 cleared, and the verifier resolution is outstanding); Jev signal alone 0/403 harmful (REFUTED as a signal) | unmeasured | advisory hook; rubric must be frozen first [areas key findings] |
| 4 | `route` | which intent/queue, with abstain | Banking77, CLINC150 + abstain (public benchmark only: the route family's receipt is N3's locate bake-off, section 8 row 4; Banking77 is X6's calibration point and never a family receipt) | **Accuracy WIN** .962 vs .787 (McNemar 107/2). Calibration TIE once both get the same dev-fitted Platt map: ECE .0246 vs .0276, diff CI [-.010, +.037] (specs/advanced-mathops.md section A) | CLI + library; Clef primary for accuracy |
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
5. A deterministic incumbent and a free or local LLM incumbent (an OpenRouter `:free` model or a local model through localbench's gateway; ROADMAP.md excludes paid comparators) on identical rows.
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
| **Measurement core** (D2, D3, D4 formula, D5, D7, D16; library only): integration owner | `.10` | `.23`, `.24`, `.25` |
| ↳ symmetric calibration + rerun spread (D2, D7) | `.23` | — |
| ↳ expected-cost and NP cuts, PPV formula, D16 NP bound (D3, D4 formula only, D16); BBSE and KS not built in stage 1 | `.24` | — |
| ↳ conformal sets (D5); D6 and D17 wait for a family PREREG that names them | `.25` | — |
| Backend seam + combine/cascade (D8) | `.4` | `.1`, `.2`, `.10` |
| ↳ free/local general-LLM comparison arm (D10); optional NOT_RUN arm for families | `.15` | `.2`, `.4`, `.10` |
| Families: integration owner of the 16-family registry (D9 do-not-build list) | `.5` | `.16`, `.17`, `.2`, `.4`, `.10` |
| ↳ cohort A (organic labels): result, rank, reread, route, nudge, recover | `.16` | `.2`, `.4`, `.10`, N1-N4, N9, conformance harness |
| ↳ cohort B (planted/blind labels): memory, screen, gate, review, watch, effort | `.17` | `.2`, `.4`, `.10`, N6, N10, X1, X7, X8, harness, metamorphic |
| `classifier gaps` (ranks omp-kit's extractor output; jev's miner retires) | `.6` | `.2`, jev-daily-omp-skill-gap-mining-7jci |
| `ready` | `.7` | `.2`, `.10` |
| Doctor repair (scoped mutation, undo, quarantine; owns `repair --apply`) | `.14` | `.3`, `.18` |
| ~~Installer: integration owner~~ FOLDED into `.22` (converge r4), in_review | `.8` | — |
| ↳ foundation: plan, manifest, lock (bootstrap/package/cosign out of stage 1) | `.18` | `.1` |
| ↳ targets: CLI, omp profile/config, skills | `.19` | `.1`, `.2` (fixture registry) |
| ↳ target: daily job manifests for `omp-kit service install` | `.20` | `.1`, `.2`, `.3`, canary fix, omp-kit rz5.113 (external) |
| ↳ target: local Clef | `.21` | `.1`, `.4`, localbench kit-jtq2 (external) |
| ↳ installer integration owner: verification ladder, docs, completions, e2e | `.22` | `.3`, `.18`-`.21` |
| Docs (doctor-rendered; present-tense fixes are a separate docs-only bead) | `.9` | `.3`, jev-grzn |
| ~~`ask` bundle (D11)~~ OUT OF STAGE 1 (converge r4), in_review: no consumer names a bundled arm | `.11` | `.4` |
| ~~`chain`: integration owner (D12)~~ DROPPED 2026-10-04, in_review: no fleet decision is a pipeline | `.12` | — |
| ~~↳ propose-check-act runner~~ DROPPED, in_review | `.26` | — |
| ~~↳ rank long-document windowed search~~ DROPPED, in_review: no long-document decision | `.27` | — |
| ~~`extract` family (D13)~~ DROPPED, in_review: no extraction decision, no host tool | `.13` | — |
| `overview` mega-command | `.28` | `.1`-`.5`, `.10`, `.18`; localbench kit-jtq2 (external) |

The epic owns D14 and D15 (inherited by every child). Every child `.1`-`.28` must close before the
epic closes. Wave 1 (2026-10-04, five read-only review lanes in `var/agent-tmp/wave1/`) produced these
children, the acceptance rewrites and the binding MATH REVIEW sections; `scripts/bead-lint.py --epic
jev-b35c` reports 29 checked, 0 findings.

Incidents outside the epic: `jev-08hr` (closed: the qpv2 OFF block, not a fault), `jev-35sg` (skill-hint
running while OFF), `jev-s0ve` (memory filter 45.5% deadline-keep). Jev memory enforcement is OFF since
2026-10-04T22:15Z (cacf8b6b); `jev-9cqw` waits on `jev-s0ve` and X8 (P(drop | relevant)).

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
- The sixteen families (section 8) are the fleet's decisions ranked by volume and label availability, not a promise that each will pass.
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
| D3 | Setting cuts | expected-cost cut at projected real prevalence; Neyman–Pearson cut from negatives only where positives are scarce (29/59/149/299 negatives for FPR .10/.05/.02/.01, δ=.05) | Youden on a balanced dev set; fixed 0.5 | the cost/prevalence formula alone: Youden 0.35 projects precision .21 at 5% prevalence [M]; no organic vendored-code precision exists to check it (0/39 positives), and memory-filter keep precision .19-.24 is a different classifier, not a validation; a same-classifier replay (skill veto at known prevalence .29) is `.24`'s acceptance; NP umbrella (Tong et al.) [L K1] | write (order statistic + cost matrix); idea from process_triage expected-loss action [R] | an NP cut on held negatives exceeds its stated FPR bound in replay |
| D4 | Before shipping any bar | project the result to a GIVEN real prevalence (formula) and run a KS alarm on live scores; BBSE only where its label-shift assumption holds, else UNIDENTIFIABLE | trust the demo-set number | skill veto .990 -> .335: the fixed-prevalence projection at the blind-labelled .29 gives .40-.63 (.629/.399), KS p≈.001 [L R4]; BBSE itself returned π̂ .938 vs truth .29 under conditional shift (veto-on-FIT .20 -> .739), so it reports a shift alarm here, never a pass (arXiv:1802.03916) | write; QuaPy as idea [R] | the projection fails to predict a known demo-to-organic drop when replayed. REVERSED by this criterion (converge r4, 2026-10-05): the skill-veto replay projects .399-.629 against the observed .335 under conditional shift, so BBSE and the KS alarm are not built in stage 1; the fixed-prevalence PPV formula stays as a utility of D3 (jev-b35c.24) |
| D5 | Abstain path | split-conformal LAC answer sets (`route --set`), refuse when exchangeability is not declared | top-k lists; a fixed confidence cut | α=.10: coverage .903, mean size 1.67, 58.5% singletons at 94.9% accuracy; worst class .152 (marginal guarantee only); α=.05 degenerate because of exact zeros [L R2] | write the algorithm (small); borrow franken_nlp's exchangeability-memo refusal [R] | coverage on a fresh disjoint split falls outside its finite-sample band |
| D6 | Many tests | Benjamini–Hochberg across the ledger; e-BH within a batch; confidence sequences to stop shadow phases | per-bar α=.05 with no correction | 74 bars at .05 imply ~3.7 false passes [M] | write; e-BH idea from process_triage [R] | — (accounting rule) |
| D7 | Drift and canaries | test against same-model rerun spread | textbook McNemar null | two runs of pinned jev-1.13.0 differ at p=.0076 on 3,080 rows [L R5] | write | — |
| D8 | Combining backends | per-task logistic combination and Jev-first cascade, only with a committed receipt | always one backend | combination AUC .862 vs .828 (p=.005); cascade sends 42% to Clef, .942 vs .962 [M] | write | the combination loses its gain on a disjoint split |
| D9 | Rejected designs | do not build: agreement/Dawid–Skene accuracy estimates, juries, self-consistency, BM25-margin cascade for `find` | — | Dawid–Skene ranks Clef .872 / Jev .924 against true .962 / .787; errors correlated (.182 vs .059) [L R3]; self-consistency AUROC .525 vs 1−conf .843 [L R6]; BM25 cascade −3.4 pp for −20% calls [L R7] | — | new evidence on our rows |
| D10 | Comparison arm | `--backend llm`: a free OpenRouter `:free` model or a local model through localbench's gateway, as an optional general-LLM arm in every `eval` (NOT_RUN when absent); zero-total-mass answers refused (jev-1yqu) | no LLM arm; a paid adapter backend (ROADMAP.md excludes paid comparators) | ML Test Score "simpler model" test [areas]; system-one-adapter-python 0.2.1 returns all-zero maps as answers (issue #45, open) [I] | USE-AS-BASELINE (external process; licence check before vendoring) | — |
| D11 | Multi-question calls | `ask` takes a bundle of mixed questions over one state | one primitive per call | parallel_questions cookbook: 12.2x cheaper, 10x faster (UPSTREAM, not re-run) [I] | write | bundle answers differ from single calls beyond run-to-run spread |
| D12 | Long documents / chained steps | DROPPED 2026-10-04 (`.12`, `.26`, `.27` in_review): no fleet decision is a pipeline or a long-document search | — | 65 mined fleet decision points contain neither (FAMILY-REBUILD section 2); jev-doc-search 2 examples (UPSTREAM); hierarchical beam REFUTED for routing (NE:3604) | — | a fleet decision of this shape appears in the miner |
| D13 | Extraction | DROPPED 2026-10-04 (`.13` in_review): no extraction decision and no host tool | — | 5 of 18 cookbooks use the shape [I]; no organic decision point | — | a host tool with an extraction decision appears |
| D14 | CLI shell, doctor, installer | robot mode, `capabilities --json`, golden schema tests; doctor/health/repair; manifest installer | ad-hoc verbs | coding_agent_session_search robot mode [R]; the three CLI skills (specs/cli-*.md) | borrow conventions; write | — |
| D15 | Dependencies | port algorithms, import nothing heavy | import MAPIE/TorchCP/alibi-detect | licences: alibi-detect BSL, TorchCP LGPL, Jev-Calibration unlicensed [R]; AGENTS.md design decision 6 | port | — |
| D16 | Memory filter | fix the deadline model, then measure P(drop given relevant) on >= 59 sampled relevant memories, then decide enforcement | enforce on drop precision | 45.5% of items time out (1,328/2,921); drop precision .985 vs always-drop .94 (p=.080); relevant dropped 1/6 [M]; relabel 22/30 < 27 (jev-9cqw) | write | — |
| D17 | Labels | prediction-powered inference (PPI++) for prevalence/accuracy on surfaces WITH organic exposure, from a random labelled sample; refuse below k labelled positives; exposure-zero surfaces fail `ready` row 2 instead | label everything / label nothing; plain PPI | PPI (Angelopoulos et al., arXiv:2301.09633) [L]; PPI++ is never wider than the classical interval under its assumptions (arXiv:2311.01453); PPI creates no positives, so it does not rescue m94x/9kmq (~0 organic positives) | write; ppi_py as reference [R] | PPI++ interval wider than labels-only at equal coverage on our data |

## 8. The sixteen decision families (plan of record since 2026-10-04)

Joshua (2026-10-04): this project is about how to understand and use classifier models for the fleet's
decisions, not about Jev. Each family below is a fleet decision mined from 14 days of session logs
(`var/agent-tmp/dogfood/fleet-schema/FAMILY-REBUILD.md`, decision points `DP-n` in
`decision-points.jsonl`; the miner is committed by N0). Jev is one arm in every bake-off; arms run
cheapest first: rule, lexical, embedding probe, encoder, local LM, Jev, general LLM. Score =
occurrences x label availability. Every count comes from the incremental miner (N0), which re-reads
only new log bytes, and every evaluation set is a time-slice manifest (file prefixes and hashes at a
cutoff), so each bar is re-checked on each new weekly slice.

| # | Family (decision) | Occ. 14 d | Outcome labels | Majority constant | Incumbent today | Bake-off bead | Cohort |
|---|---|---|---|---|---|---|---|
| 1 | `result`: keep / spill / drop a long tool result | 99,680 | 4,329 read-backs | not read back .767 | omp size rule; jev-dau5 EXPLORED | N1 | A |
| 2 | `rank`: top `find` hit | 41,002 | 421 touched hits | touched .536 | omp native judge (Jev) | N0 labels; organic rank bake-off in jev-b35c.16 (Jev vs BM25 top-1 on touched-hit rows; FiQA is a public row only) | A |
| 3 | `reread`: skip a repeat read | 36,827 | 20,388 redundant (tautological label) | redundant .553 | read-dedup shadow | N2 | A |
| 4 | `route`: which locate tool / path | 44,086 | 1,250 find->read | grep .776 | rule text only | N3 (+X6 embedding/SetFit arms) | A |
| 5 | `nudge`: should injected guidance fire (legacy `score` merges here) | 22,479 | 1,533 follow/act | .540-.810 per injector | TTSR + Jev judge; omp rules | N9 (X5 SST-5 dropped: benchmark tourism) | A |
| 6 | `recover`: retry, change or re-read after an error | 11,970 | 6,644 next-call outcomes | next call ok .853 / .854 | none | N4 | A |
| 7 | `land`: commit / close ready (legacy `diff` = vendored sub-check) | 6,466 | 652 failures | not failed >= .895 / .827 | guard rules, policy gate | N5 (UPHILL to omp-kit) + X4 | — |
| 8 | `outcome`: user accepted the last answer | 7,536 | 31 corrections (floor) | accepted .996 | none | N6 | B after >= 30 positives |
| 9 | `pin`: files kept through compaction | 1,577 | 1,385 re-reads | re-read .878 | none (omp native) | N7 | B after >= 30 positives |
| 10 | `delegate`: delegate, agent type, tier, accept | 4,362 | 39 | accept .981 | none | N8 | B after >= 30 positives |
| 11 | `review`: verdict holds; finding new (legacy `verify` merges here) | 220 | 0 organic; blind E1 55, E2 85 | repeat .812; not held .618 | rules beat Jev (E2 77/85 vs 49/85; E1 .618 vs .400) | N10 (+X3) | B |
| 12 | `memory`: recalled memory relevant now | 41,025 | 0 organic; blind 6/100 relevant | irrelevant .94 | cap-3 cut (Jev enforcement OFF) | X8 | B |
| 13 | `gate`: command risky (observe layer) | 74,351 | 0 organic; blind 396 rows, 47 harm | no-harm .881 | Jev 47/47 vs rules 7/47 (X7) | X7 | B |
| 14 | `screen`: tool/web result is an injection | 19,835 | 0 organic; planted 1,262 | balanced .5 | Jev 268/300, 5/300 false flags | X1 | B |
| 15 | `watch`: continue, idle, page, keep a job | 13,218 | 0 (decisions not persisted) | stop is fine 1.00 | omp smart stop; fleet watcher STOPPED | N6 | B |
| 16 | `effort`: thinking level / model | 10,756 | 0 | undefined; keyword beat Jev 32/94 vs 12/94 | omp auto-thinking | N6 | B |

Legacy mapping: `route`, `rank`, `gate`, `screen`, `memory`, `watch`, `effort` keep their names;
`verify` merges into `review` (verdict-holds) and `land` (claim/close evidence); `score` into `nudge`;
`diff` into `land` as a shadow sub-check. Every family is a decision contract
(`kit/contracts/<family>.json`) whose adapters all pass the conformance harness (C1-C7,
`specs/conformance-goldens.md`) before a bake-off; the six label-pending families (11-16) also pass the
metamorphic bead (option shuffle, paraphrase, padding). The other 24 decision points stay with code or
people (FAMILY-REBUILD section 4). Stage exit: `jev-uzq1`.
