# vbh.4 shadow router policy v1 (pre-registered BEFORE measuring — 2026-09-20)

Scores: recorded eww run (`/tmp/score32.log`, jev-1.13.0, 32 turns). No new calls.

## Tier mapping

- `heavy` iff P(needs_heavyweight) >= 0.75 AND P(mechanical) < 0.50
- `light` iff P(mechanical) >= 0.75 AND P(needs_heavyweight) < 0.50
- else `abstain` (neutral: neither correct nor wrong)

## Correctness

- `heavy` on heavyweight-true → correct; `light` on mechanical-true → correct.
- Wrong tier → error. Abstain → neutral.
- Baselines: always-abstain (0 correct / 0 wrong / 32 abstain); argmax-always
  (route every turn by higher score, never abstain).

## Kill switch

`ROUTER_KILL=1` (or `--kill`) forces every turn to abstain regardless of scores.
Demonstrated firing in the measurement run (second pass with the flag set).

## Ruling questions (answered after measuring, not before)

1. Does the shadow policy beat always-abstain on correct-minus-wrong?
2. Should `action` ever be honoured live (i.e., does any tier clear the bar
   where routing beats abstaining on the hard classes)?
