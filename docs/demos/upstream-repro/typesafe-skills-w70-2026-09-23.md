# typesafe-ai/skills — W7.0 catalogue receipt — 2026-09-23

Fresh run. Class: catalogue/guidance. Tests run: T1 (pin+env) and T3 (entry inventory). No live Jev call. Clone not edited.

Prior receipt `docs/demos/upstream-repro/typesafe-skills-w70-20260922.md` is a lead, never a pass. Depth rule binds: anything not run below carries command + verbatim output + file:line cause + two routes; T2/T4–T9 are NOT-APPLICABLE by catalogue class (not NOT-RUN), so no depth-rule debt is owed on them.

Measured 2026-09-23T03:41:17Z. Worker: Darwin 25.5.0 arm64 (Joshs-Mac-Studio). Parent jev HEAD (short) at read time: `fcbb050`. `TYPESAFE_API_KEY` length in the measurement shell: 0 chars (value never printed). No `infisical run` was issued — assignment forbids live calls, so key presence in Infisical was not probed this run. No `omp` command was run. Live model would have been jev-1.13.0; Jev call N = 0, prevalence = n/a, cost = $0.00, p50/p95 latency = not measured (no calls). Spend this receipt: $0.00.

Evidence level of every claim below: **oracle** (a command output or a file read at the pin), never **test** and never **live**. A number without model + lane + date + N is not in this file.

## T-table

| id | status | deciding evidence |
|---|---|---|
| T1 | PASS | MANIFEST row `skills upstream/typesafe-ai/skills 65a39f3 65a39f3 0 2026-09-18T15:58:49Z`; clone HEAD full SHA `65a39f393687675ce170e6094757de20370365b9` = `origin/main`, subject `Release v0.5.7`, tag `v0.5.7`; `status --porcelain` empty; 6 tracked files, no harness. |
| T2 | NOT-APPLICABLE | Catalogue class runs T1+T3 only. No suite exists to run: no `package.json`/`pyproject.toml`/`tests` in the clone (verified `ls` failure below). Not NOT-RUN. |
| T3 | PASS | Inventory below. Catalogue publishes **1 named skill** (`typesafe-ai`). 9 guidance blocks inventoried (1 skill + 3 primitives + 5 pattern/verify blocks); every block marked guidance-only vs verifiable; every measurable claim paired with its verifying check + whether this tree runs it. |
| T4 | NOT-APPLICABLE | Catalogue; no live call per assignment. Not NOT-RUN. |
| T5 | NOT-APPLICABLE | Floor arms are seat/benchmark. This clone measures nothing. |
| T6 | NOT-APPLICABLE | Incumbent arm is seat/benchmark. No accuracy rows to pair. |
| T7 | NOT-APPLICABLE | Calibration is seat/benchmark. No probabilities collected (N = 0). |
| T8 | NOT-APPLICABLE | Stability is seat/benchmark. No questions asked. |
| T9 | NOT-APPLICABLE | No client, no POST, no key path in the clone (`SKILL.md:99-103` points at docs; `plugin.json:10` is the skills repo URL). No process to fault-kill. |
| T10 | PASS | Verdict, claim statuses, NO-CLAIM, and the not-run distinction are in this file. Nothing was left NOT-RUN. |

## T1 — pin + env

MANIFEST pin (`upstream/MANIFEST.tsv`, skills row):

```
skills	upstream/typesafe-ai/skills	65a39f3	65a39f3	0	2026-09-18T15:58:49Z
```

Commands, run from the jev repo root (read-only; clone never fetched, never edited):

```
grep -P '^skills\t' upstream/MANIFEST.tsv
git -C upstream/typesafe-ai/skills rev-parse HEAD
git -C upstream/typesafe-ai/skills status --porcelain=v1
git -C upstream/typesafe-ai/skills ls-files
git -C upstream/typesafe-ai/skills log -1 --format='fullsha=%H%nauthor_date=%ai%ncommit_date=%ci%nsubject=%s'
git -C upstream/typesafe-ai/skills rev-parse origin/main
ls upstream/typesafe-ai/skills/package.json upstream/typesafe-ai/skills/pyproject.toml upstream/typesafe-ai/skills/tests
```

Verbatim:

```
skills	upstream/typesafe-ai/skills	65a39f3	65a39f3	0	2026-09-18T15:58:49Z
65a39f393687675ce170e6094757de20370365b9
(empty porcelain)
.claude-plugin/marketplace.json
.claude-plugin/plugin.json
LICENSE
README.md
skills/typesafe-ai/LICENSE
skills/typesafe-ai/SKILL.md
fullsha=65a39f393687675ce170e6094757de20370365b9
author_date=2026-09-12 05:42:05 +0000
commit_date=2026-09-12 05:42:05 +0000
subject=Release v0.5.7
65a39f393687675ce170e6094757de20370365b9
ls: cannot access 'upstream/typesafe-ai/skills/package.json': No such file or directory
ls: cannot access 'upstream/typesafe-ai/skills/pyproject.toml': No such file or directory
ls: cannot access 'upstream/typesafe-ai/skills/tests': No such file or directory
```

Tag at HEAD: `v0.5.7` (`git tag --points-at HEAD`). Plugin version agrees: `.claude-plugin/plugin.json:3` `"version": "0.5.7"`. License: `LICENSE:1` = `MIT License`, nested `skills/typesafe-ai/LICENSE` byte-matches per prior receipt (not re-diffed this run; re-diff is a one-command re-run item below). Behind count 0; HEAD = origin/main. Env: `TYPESAFE_API_KEY` len 0 in shell; no live-call lane exists for this receipt.

## T3 — entry inventory

Named skills in the catalogue: **1**. `README.md:36-38` table has one row (`typesafe-ai`). `SKILL.md:2` `name: typesafe-ai`. `marketplace.json:8-13` publishes one plugin (`typesafe`, source `./`). The file `skills/typesafe-ai/SKILL.md` is 149 lines, pure guidance prose + docs links; it contains zero fenced runnable blocks (no ` ```bash/sh/python/js ` run step; the only code-adjacent tokens are prose verbs like "check/verify/test", confirmed by grep hits at `SKILL.md:83,89,121,123,126,141,145` — all sentences, no commands). The clone names **no runnable check**: no script, no test runner, no fixture, no assertion command. Every "test/measure/validate" sentence in the file is advice to the reader, not an executable the tree can run.

The skill itself **uses no Jev primitive** (it is markdown; it makes no API call). It **names three primitives** (Choice / Noul / Score) and **six pattern blocks**. Each row below: claimed capability → primitive → runnable check named in-tree? → measurable outcome? → check that would verify it → does this tree run that check anywhere? → guidance-only vs verifiable.

| # | entry (file:line) | claimed capability | Jev primitive | names runnable check? | measurable outcome + verifying check | tree runs it? | class |
|---|---|---|---|---|---|---|---|
| E0 | `typesafe-ai` skill proper (`SKILL.md:2`, `README.md:38`, `README.md:32` example: route support tickets by department with human review when uncertain) | Design TypeSafe workflows; find current docs/cookbooks; compose typed judgments in code | none used; routes to Choice/Noul/Score | No | No directly measurable outcome (design advice). Would verify via: agent-behavior A/B (skill loaded vs not) scored on task success — no such harness exists here. | No | **guidance-only** |
| E1 | Read-the-live-docs (`SKILL.md:26-53`; task→URL table `:46-53`) | Docs index + `.md` fetching finds current contracts/SDK/cookbooks | none | No (URLs only, and live fetch was out of scope: no live calls) | Measurable in principle: link-rot check (GET each URL, expect 200 + Markdown). | Not run this receipt (would be a network call; assignment says no live calls). `docs-mirror/` exists as a lead only, not a check of these URLs. | **guidance-only** (verifiable-by-link-check, not run) |
| E2 | Route-and-fill (`SKILL.md:66-69`) | A request selects a handler + typed params; ask branch-specific questions up front | Choice (handler select) | No | Measurable: routing accuracy on a labelled request set (Choice accuracy + arg-fill exact match). Check: fixture set + `askJevChoice` + accuracy. | Partial wire exists: `work/jev-client/src/index.ts` exists (verified `ls` this run); `work/jev-question-writing/trial.mjs:19` imports `askJevChoice` from it; `work/omp-jev-review/src/index.ts:21` imports `askJev`. No routing-accuracy fixture for *this* skill's claim was run here. | **guidance-only** (claim verifiable, not verified here) |
| E3 | Select-instead-of-generate (`SKILL.md:70-74`) | Judge selects intended value/span from candidates; code copies/normalizes | Choice | No | Measurable: selection exact-match vs labelled spans. Check: span-fixture + Choice call. | Not run anywhere for this claim this receipt. | **guidance-only** |
| E4 | Find-and-judge-evidence (`SKILL.md:75-77`) | Retrieve candidates, compare relevance, select useful context (rerank) | Choice or Score (graded ranking per `:103`) | No | Measurable: rerank quality (NDCG / top-k hit rate) on a relevance-labelled set. Check: rerank harness over labelled pairs. | Harness-shaped files exist in tree (`work/jev-question-writing/pass*-run.mjs`, `work/omp-jev-*/measure*.mjs` seen in grep) but none was executed or tied to this skill's claim this run — leads, not passes. | **guidance-only** |
| E5 | Reusable-data / composite scoring (`SKILL.md:78-82`) | Score dimensions once; code varies weights/thresholds/views without rerun | Score | No | Measurable: (a) Score-level stability across re-weightings without rerun; (b) feature-lift with labeled outcomes. Check: fixed-question re-score + weight-sweep determinism. | Not run this receipt. | **guidance-only** |
| E6 | Verify-and-escalate (`SKILL.md:83-86`) | Check claims/fields against evidence; escalate uncertain/failing cases | Choice (citation-check shape: supports/contradicts/says_nothing) | No (points at cookbook URL, no command) | Measurable: citation-check precision/recall + escalation calibration at a stated confidence floor (e.g. 0.8). Check: labelled claim-evidence pairs + threshold sweep. | Wire shape exists in tree per prior receipt (`work/citation-check/src/check.ts`, `src/live.ts` — lead, not re-read this run). No threshold re-validation here. | **guidance-only** |
| E7 | Choice (`SKILL.md:101`) | One of a defined set; distribution compares competing options | Choice | No | Measurable: (a) output is exactly one listed option (schema check); (b) distribution concentration tracks alternative-plausibility (calibration-style check). Check: fixture Choice calls + schema assert + confidence-vs-correctness plot. | (a)-shaped callers exist (`askJevChoice` import verified at `trial.mjs:19`); no fixture run this receipt. | **verifiable** (schema half is cheaply checkable) but **not verified here** |
| E8 | Noul (`SKILL.md:102`) | Whether a condition holds; probability of yes; no separate confidence; one per label | Noul | No | Measurable: (a) response carries probability, no confidence field (schema check); (b) `p(yes)≈0.5` cases are genuinely borderline (calibration check, `SKILL.md:134-135`). Check: schema assert + calibration plot on labelled booleans. | (a)-shaped caller exists (`askJev` import verified at `omp-jev-review/src/index.ts:21`, `trial.mjs:18`); no run here. | **verifiable** (schema half) but **not verified here** |
| E9 | Score (`SKILL.md:103`) | Degree along a dimension; probability-weighted position on ordered levels | Score | No | Measurable: score equals probability-weighted level index; comparable per-item Scores rank sensibly. Check: Score fixtures + expected-value recomputation + rank correlation. | Caller-name evidence only (`askJevScore` referenced per prior receipt; not re-grepped this run — lead). No run here. | **verifiable** but **not verified here** |
| E10 | Coverage / no-match (`SKILL.md:119-121`: "the model cannot choose an omitted value") | Include no-match outcome; candidate coverage determines choosability | Choice (constraint) | No | Measurable and falsifiable: omit the gold value from candidates, assert model returns no-match (never the omitted value). Check: omission-probe fixture set. | Not run anywhere this receipt. | **verifiable**, not verified |
| E11 | Parallel independence (`SKILL.md:125-127`: independent questions "run in parallel and cannot see one another's answers") | Batching gives isolation + parallelism | protocol (not a primitive) | No | Measurable: (a) latency < serial sum (timing); (b) answer-invariance vs order / vs seeing siblings (interference probe). Check: batch-timing + shuffle-invariance harness. | Not run this receipt. | **verifiable**, not verified |
| E12 | Confidence semantics (`SKILL.md:132-137`) + calibration (`:142-143`: "trained for calibrated decisions; validate … in the target domain") | Choice/Score confidence = distribution concentration, NOT workflow correctness or permission; Noul 0.5 = borderline, not medium intensity | Choice/Score/Noul (interpretation) | No — explicitly defers validation to the reader ("thresholds evaluated on the user's data", "validate their performance") | Measurable: calibration curves per primitive on domain labels; concentration-vs-correctness dissociation demo. Check: labelled set + reliability plot. | Not run (N = 0). | **verifiable**, not verified; the "validate" sentence is itself guidance-only |
| E13 | Cost/latency discipline (`SKILL.md:130`: "measure actual request budgets, cost, and end-to-end latency") | Measurement practice, no numeric claim | none | No (imperative, no command) | Measurable once a caller exists: $/1k judgments, p50/p95 latency. Check: instrumented batch run. | This receipt records its own zero-spend (N = 0, $0.00, no latency) — the only measured numbers in scope. No caller measured. | **guidance-only** |

Tallies (denominators explicit): named skills 1/1 inventoried; internal guidance blocks 12/12 (E1–E6 patterns/docs + E7–E9 primitives + E10–E13 composition rules) inventoried; blocks naming a runnable check 0/13 (E0 included); blocks with measurable outcomes 9/13 (E2–E4, E6–E12); of those, checks run in this tree this receipt 0/9. Highest status any block can claim here: **guidance-only**, or **verifiable-but-unverified**. Nothing is demonstrated as a Jev behavior.

## Verdict

Result class: **not applicable** (catalogue). The clone is guidance prose at pin `65a39f3`; it answers no labelled question, so it is not SELF, FLOOR, or INCUMBENT. No accuracy number is stated. N = 0 calls, cost $0.00, no latency. Claim statuses: 4/13 guidance-only with no measurable outcome (E0, E1, E5, E13), 9/13 verifiable-but-unverified (E2–E4, E6–E12), 0/13 demonstrated. The tree contains caller-shaped code consistent with E2/E6–E8 (verified imports at `work/jev-question-writing/trial.mjs:18-19`, `work/omp-jev-review/src/index.ts:21`, and `work/jev-client/src/index.ts` existence) — wire existence, not claim verification. Prior-day consumer file:lines (citation-check, beads-eval, router, SDK wire) are leads reused as pointers only, not re-passes.

NO-CLAIM: no live Jev call, no accuracy, no calibration, no cost/latency beyond this receipt's own zero-spend, no proof cookbook thresholds transfer (the skill itself warns at `SKILL.md:148` not to treat them as universal), no proof loading the skill changes agent behavior, no link-check of the docs URLs, no claim the workspace skill copy was installed from this clone.

Nothing was NOT-RUN. T2/T4–T9 are NOT-APPLICABLE by class.

## Boundary

This receipt pins the catalogue at `65a39f3`, reads its one skill, and maps every guidance block to primitive / check / tree-consumer / guidance-vs-verifiable status. It proves no question well-written, no Jev answer, no agent behavior change. It grades no cookbook, clones nothing, edits nothing (porcelain empty before and after; only this receipt file was written), updates no EVAL.md. A rerun that fetches the clone, opens network URLs, or makes a live call is a different receipt.

## Re-run

From the jev repo root, without printing secrets:

```
grep -P '^skills\t' upstream/MANIFEST.tsv
git -C upstream/typesafe-ai/skills rev-parse HEAD
git -C upstream/typesafe-ai/skills status --porcelain=v1
git -C upstream/typesafe-ai/skills ls-files
grep -c -E '```(bash|sh|python|js|ts)' upstream/typesafe-ai/skills/skills/typesafe-ai/SKILL.md
```

Expected: MANIFEST `65a39f3 … 0 2026-09-18T15:58:49Z`; HEAD `65a39f393687675ce170e6094757de20370365b9`; empty porcelain; six tracked paths; fenced-runnable-block count 0.
