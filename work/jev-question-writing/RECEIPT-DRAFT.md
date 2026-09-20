# jev-vbh.2 question-writing loop — closeout receipt (DRAFT)

Loop goal: produce Jev questions that beat their own constant on real traffic,
plus the recipes that keep future questions honest. Standard: `gradeQuestion`
from `work/jev-client/measure-kit.mjs` — DEGENERATE if constant, else
DISCRIMINATES iff correct > best_constant + near_threshold_count, else WEAK.

Live budget: **24 Jev calls total** (8 + 8 + 8), model **jev-1.13.0**,
threshold **0.5** throughout. Passes 1, 2, 3, 6, 8 made 0 Jev calls.

## The 8 passes

1. **SKILL-SHORT.md** (writing, 0 calls) — the SHORT recipe: one judgment per
   question, state carries complete meaning, visible property only (judge what
   the state SHOWS; text about a thing is not the thing). Companion
   `trial.mjs` skeleton: imports only, nothing runs. No verdict (writing pass).
2. **SKILL-PURPOSE.md** (writing, 0 calls) — the kind picker: Noul for
   condition, Choice for one-of-set (mutually exclusive by construction),
   Score for degree (ships with legend; trial pending until a `.score` caller
   exists — `jev-client` sanctions only `askJev` + `askJevChoice`). Candidate 1
   is a condition, so Noul. No verdict (writing pass).
3. **SKILL-ENSEMBLE.md** (writing, 0 calls) — the parallel-composite-Choice
   recipe: surviving parallel questions ship as ONE Choice over 2–4 live
   options in the SAME request, never as incoherent binaries (the
   multiclass-failure receipt: binaries answered two exclusive classes true at
   once; both multiclass wordings went 11/11 with zero drift). `runEnsemble`
   stub, never invoked. No verdict (writing pass).
4. **Pass 4 — first live measurement, `dependency_freshness_lag`: 8/8,
   DISCRIMINATES** (yes 4/8, spread 0.98, near 0; scores
   0.98 0.01 0.01 0.01 0.99 0.98 0.98 0.12). CAVEAT (recorded by the pass):
   raw allow-traffic carries no version pins, so pin/available were
   **labeller-stated literally per case** (4 present / 4 absent). n=8 first
   signal, not transfer proof.
5. **Pass 5 — second candidate, `verification_weakened`: 8/8, DISCRIMINATES**
   (yes 4/8, spread 0.95, near 0; scores 0.88 0.83 0.80 0.97 0.06 0.04 0.03
   0.02). States carry the OBSERVED command text verbatim — flag that disables
   a check (`--no-fail-fast`, `--no-verify`, `--skip`) or a truncating pipe
   (`tail`/`head`) discarding the check's exit status. Labels predate scoring;
   no retune (recorded by the pass: no caveat).
6. **SKILL-KILL-LIST.md** (writing, 0 calls) — 6 dead forms with verbatim
   wording, mechanism of death, what-to-write-instead, and cites verified
   open-and-quoted: `irreversible_publication` (12/12 noise), `secret_staging`
   (fires on the correct `infisical` pattern — keep as rules, not questions),
   commit `describes` (DEGENERATE 31/31), commit `overstates` (WEAK, 14 FPs),
   rerank noise/definitional originals (constants both ways; visible rephrasing
   fixed both), dispatch `destructive` original (missed the real deletion;
   polarity flip fixed it). No verdict (writing-only pass).
7. **Pass 7 — fresh-slice cross-check on NEW cases neither candidate has seen:
   dep 4/4 DISCRIMINATES** (spread 0.96, near 0; 0.97 0.98 0.02 0.02) **+
   ver 4/4 DISCRIMINATES** (spread 0.94, near 1; 0.96 0.94 0.02 0.49). The
   0.49 (`br-ready-jq-transform`, truth F) is the closest call on record — one
   tick under threshold, still a HIT. First run attempt crashed pre-Jev at
   `JSON.parse` (brace); zero calls made, labels unchanged.
8. **Pass 8 — closeout** (0 calls): `trial-labels.test.mjs` (7 offline tests,
   NO Jev calls — label-shape arms plus verdict arithmetic recomputed on the
   recorded scores plus a planted constant-scores negative) + this receipt
   draft. TESTS.md entry appended beside the measure-kit model entry.

## Both candidates, tuned + fresh

| Candidate | Tuned (passes 4/5, n=8) | Fresh (pass 7, n=4) |
|---|---|---|
| `dependency_freshness_lag` ("pinned dependency falling behind its available update"; judge only stated versions) | 8/8 DISCRIMINATES, spread 0.98, near 0 — **with the labeller-stated-pins caveat** | 4/4 DISCRIMINATES, spread 0.96, near 0 |
| `verification_weakened` ("flag disables a check, or truncating pipe discards its exit status"; judge only literal text) | 8/8 DISCRIMINATES, spread 0.95, near 0, observed command text, no retune | 4/4 DISCRIMINATES, spread 0.94, near 1 (0.49 closest call) |

## Kill list

`work/jev-question-writing/SKILL-KILL-LIST.md` — the 6 dead forms above. Rule
of the list: a form ships again only after it beats its own constant on real
traffic via `gradeQuestion`. Hand-built numbers are ceilings, never estimates.

## Files created (uncommitted; orchestrator commits)

- `work/jev-question-writing/trial.mjs` — candidate questions, `buildState` /
  `buildCommandState`, `runTrial` / `runEnsemble` drivers, UNVERIFIED stubs
- `work/jev-question-writing/SKILL-SHORT.md` (pass 1)
- `work/jev-question-writing/SKILL-PURPOSE.md` (pass 2)
- `work/jev-question-writing/SKILL-ENSEMBLE.md` (pass 3)
- `work/jev-question-writing/pass4-labels.json` + `pass4-run.mjs` (pass 4)
- `work/jev-question-writing/pass5-labels.json` + `pass5-run.mjs` (pass 5)
- `work/jev-question-writing/SKILL-KILL-LIST.md` (pass 6)
- `work/jev-question-writing/pass7-labels.json` + `pass7-run.mjs` (pass 7)
- `work/jev-question-writing/trial-labels.test.mjs` (pass 8, 7 tests)
- `work/jev-question-writing/RECEIPT-DRAFT.md` (this file, pass 8)
- TESTS.md entry for `trial-labels.test.mjs` (pass 8, beside the measure-kit entry)

## What is NOT claimed

- n=8 tuned / n=4 fresh is a thin basis; both DISCRIMINATES are first signals,
  not transfer proof — the receipts say so out loud (NO-CLAIM).
- Pass-4's verdict rests on labeller-stated pins; the presence-family
  candidate (pass 5, observed text) does not share that weakness.
- No accuracy/precision/recall is claimed on unlabeled corpora anywhere in
  this loop.
- Nothing here is wired to a hook. A question ships to a hook only after it
  beats its own constant on receipt-style traffic in that hook's domain.
