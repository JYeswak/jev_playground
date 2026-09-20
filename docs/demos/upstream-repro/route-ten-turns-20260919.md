# Ten distinct turns: 7/10 per question, traps show length leaks but content leads (2026-09-19)

## Protocol (contamination control, as briefed)

Labels written first: `work/omp-jev-route/turns-prelabels-20260919.md`, mtime 19:41:33
local, before the first session (01:41:53 UTC). Scores read only after all ten sessions
completed. Every turn ran in its own session (`omp --profile=jev-lab -p`, 11 rows each).
Provider was usage-limited all evening, so every agent errored without working — rows
still landed (the scorer fires on context events regardless), and the labels are
prompt-based anyway, which is what the scorer sees too.

## Results (turn-level; all 11 rows unanimous within every turn, zero flips, spreads ≤0.09)

| turn | pre-label H/M | scored H | scored M | verdict |
|---|---|---|---|---|
| port-retry-asyncgen | T/F | 0.88–0.89 | 0.11–0.12 | HIT/HIT |
| shared-state-leak | T/F | 0.92–0.93 | 0.08–0.09 | HIT/HIT |
| sqlite-migration-plan | T/F | 0.95–0.96 | 0.11–0.13 | HIT/HIT |
| rename-tmp | F/T | 0.10–0.11 | 0.98 | HIT/HIT |
| typo-funciton | F/T | 0.06 | 0.91–0.93 | HIT/HIT |
| rerun-tests | F/T | 0.50–0.54 | 0.13–0.15 | MISS/MISS |
| TRAP bump-version (short, heavy by construction) | T/F | 0.09–0.11 | 0.94–0.95 | MISS/MISS |
| TRAP auth-grace (short, heavy by construction) | T/F | 0.54–0.58 | 0.61–0.66 | HIT/MISS |
| TRAP verbose-typo (long, trivial) | F/T | 0.06–0.08 | 0.87–0.89 | HIT/HIT |
| TRAP verbose-rename (long, trivial) | F/T | 0.64–0.73 | 0.90–0.92 | MISS/HIT |

Per question (n=10 turns): needs_heavyweight precision 4/6 (0.67), recall 4/5 (0.80);
mechanical precision 4/6 (0.67), recall 4/5 (0.80). FPs: rerun-tests, verbose-rename
(heavy); bump-version, auth-grace (mechanical). FNs: bump-version (heavy); rerun-tests
(mechanical).

## The traps are the finding

The scorer reads content first, length second — but length leaks. Verbose-typo (long,
trivial) scores correctly light on both questions: length alone does not doom a turn.
Verbose-rename (long, trivial) leaks 0.64–0.73 into heavyweight: same trap shape, real
length influence. Short-heavy traps split honestly: bump-version scores light (the hidden
three-artifact compilation is invisible in the prompt, so light is the calibrated answer
to what was asked — my T label used construction knowledge the scorer never had);
auth-grace scores heavyweight 0.54–0.58 at the threshold edge (the auth path IS in the
prompt, and it carried). Rerun-tests is the worst cell (0.50–0.54 heavy on a re-run):
"failing test suite" reads as difficulty though the ask is mechanical.

## NO-CLAIM

Ten prompts authored by me, one labeller, labels prompt-based (outcomes unobserved —
the agents never worked). Still not a stranger's traffic. Stability (zero flips, 110/110
unanimous rows) keeps replicating; accuracy on ten self-authored turns is 7/10 per
question.
