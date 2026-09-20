# D5 claim-verb rule: mining receipt `[test]`

Un-refused 2026-09-20 by P1 text-corpus notice: assistant claim-verbs were UNMEASURABLE
in the bash-only dcg harvest; they are measurable in omp session JSONL
(`~/.omp/**/sessions/*.jsonl`, text nested in `message.content[]` parts).

## Preregistered bar (written BEFORE measuring, 2026-09-20)

- A class firing above **~5% of assistant-text turns is wallpaper**; below **50 occurrences
  too rare**.
- Rate alone never ships: **hand-label a seeded sample (n≥20) WITH full turn context**
  (same-message toolCalls + neighboring toolResults), report FP.
- **State prevalence beside every score.** Ship-bar: strict-FP ≤0.35 (same bar that
  shipped the shape rule at 0.20).
- TTSR `scope:text` sees the text stream only, not turn history — so the shippable rule
  fires on the VERB; mining must prove the verb predicts the defect (ungrounded claim).
  If verbs are usually grounded, the class REFUSES no matter the rate.

## Corpus (not authored here)

Session JSONL, quoted with count and date at measure time. Assistant turn = one
`type:message` record with `message.role==assistant`; text parts `type:text`,
tool calls `type:toolCall` (name/arguments/intent), results `role:toolResult`.
Mining is read-only; samples quoted minimally; no secrets (claim sentences are generic).

## Results

PENDING MEASUREMENT.

## SUPERSEDED — STOP order, P4 measured first (6480170)

Claim-verb-with-no-prior-command: 329/45,111 turns (0.729%, passes rate bar) REFUSED on
concentration (73% of hits from ONE omp-orchestrator session — a habit, not a class) and
labels (2/24 TP, FP 0.92, seed 20260920P4c). Not re-derived here per STOP; no variant shopped
for a better seed. (My own aborted pass managed 24.8% on chunk-level records with `done`/`working`
in the verb list — a third reason the naive predicate fails: wrong record granularity plus a
loose verb list. Discarded, recorded so nobody repeats it.)

METHOD ADDITION (from this kill): rate + FP is not enough — every future mining pass adds a
**per-session concentration check**. A class carried by one session is a habit, not a rule.
Corpus drifts while measured (1841/45,103 → 1842/45,108 in 20 min; my own walk: 1825 files,
dot-layout-dependent): quote file count + timestamp as the denominator, like the harvest N.
