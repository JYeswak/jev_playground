# Stranger test on docs/RULES.md: TRUE with two fixes (2026-09-20)

Level: `test` (9 commands run verbatim from root, unpiped exit codes; no Jev calls).

## Table (one row per rule)

| # | run | demonstrates? | sha? | fresh-clone? | quoted line |
|---|---|---|---|---|---|
| 1 | RUNS exit 0 | YES (`0/2 ... CLAIM HOLDS`) | fa78767 OK | NO — needs gitignored omp session logs | `perfect (omniscient ceiling) ADOPTED on: 0/2` |
| 2 | RUNS exit 0 | YES (73.7%/31.1% columns present) | (same) | NO — same dependency | `73.7% 31.1% REJECT` |
| 3 | RUNS exit 0 | YES (falsifier commit shown) | 8e43ccb, beb45d5 OK | YES | `measure(retransmit): [pending] section 21 falsifier...` |
| 4 | RUNS exit 0 | YES (44.6% vs 50.0%, p50s) | 61e953b OK | YES (JSON committed) | `falsifier rows 130, fired 58 (44.6%)` |
| 5 | RUNS exit 0 | YES (`repeat scorings ... 0`) | c816150 OK | YES (fixture committed) | `repeat scorings of an identical (input, question, model): 0` |
| 6 | RUNS exit 0 | YES (5/5) | 6ff34bc OK | YES | `# pass 5` |
| 7 | RUNS exit 0 | YES (58/130 + 14/14) | c6eb7ab OK | YES | `falsifier fired 58 / 130` |
| 8 | RUNS exit 0 | YES ("not recoverable" ×2, 15/15) | 6ff34bc OK | YES | `# pass 15` |
| 9 | RUNS exit 0 | YES (5/5 + grep 0) | 959c321, c20da52, e33bd5d OK | YES | `# pass 5` |

## Verdict: TRUE as written, after two cheap fixes (this commit)

1. Header said "Eight rules" for nine — now "Nine rules".
2. Rules 1–2 never disclosed the session-log dependency — each carries the
   caveat line now. Smallest honest fixture question answered: no new artifact
   needed; the caveat is the fix (a fresh clone cannot regenerate another
   machine's sessions).

## NO-CLAIM

Ran on this machine with its session logs present; fresh-clone column is read
from git-tracked status, not from an actual fresh clone. No Jev calls.
