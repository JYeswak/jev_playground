# MiniWoB AX pruning loss: keyless autopsy

Bead: `jev-9gtw.7`, the loss-depth step for `NEGATIVE_EVIDENCE.md` R107 and `jev-jy7t.1.6`.
Lane: **offline**. No TypeSafe request was made. Inputs are the eight committed row files from the
live run (`2c6cfed` dev, `66b8f61` held-out; live receipt
`miniwob-ax-prune-20260925.md`). The run was 2026-09-25 on `jev-1.13.0`, N=50 per arm per split,
`MAX_STEPS=1`.

Reproduce from one command. It uses local headless Chrome and makes no API call:

```text
env -u TYPESAFE_API_KEY /tmp/jev-miniwob-jev/venv/bin/python work/miniwob-ax-prune/autopsy.py
```

## What the autopsy can see, and what it cannot

**Per-node Noul answers are not recoverable.** `ax_prune.LiveNoulPruner` validates the three Nouls
per node, applies the keep rule, and discards the values. The rows keep only node and byte counts.
This bead's step (1) asked how many nodes each Noul (`relevant`, `required`, `safe_to_omit`) kept
alone. That count **cannot be computed from the committed rows**. Any dev loop on H1 or H2 below
must first replay the dev pruner requests with the per-node answers logged, which is a live call.

What is recoverable keylessly. `autopsy.py` rebuilds every step-0 page in local Chrome with the
pinned `dd04baf` floor. **100/100 pages** reproduce the rows' `full_state_bytes` byte for byte. The
code and random selectors, re-run on those pages, reproduce their rows' `seen_state_bytes` on
**100/100** and **100/100**. So the pages below are the pages the arms saw.

To estimate planner tokens for an observation no arm sent, the autopsy scales the full arm's
measured tokens by the ratio of planner request bytes (state plus questions, built by the pinned v1
planner). On the two arms whose true token counts are known, the aggregate error is
**−0.61% (code) and −1.88% (random)**; the median per-episode error is 2.77% and 0.91% (N=100 each).
Every "est" number below comes from this estimator.

## 1. Where the cut went

| | dev | held-out |
|---|---:|---:|
| Episodes where Jev kept the whole page | 19/50 | 20/50 |
| Median elements on those pages | 6 | 6.5 |
| Median elements on the pages Jev did prune | 16 | 16.5 |
| Of the whole-page episodes, pages with a text input | 5 | 5 |
| Best possible cut on the whole-page episodes (target + ancestors + text), est | 21.8% | 25.3% |
| Best possible cut on all 50, est | 49.7% | 49.8% |
| Episodes whose best possible cut is still under 40% | 26/50 | 26/50 |
| Measured Jev cut | 25.7% | 25.9% |
| Containers among positive nodes (forced back by the closure) | 51.7% | 50.6% |
| Pruner questions spent on text-run elements (answers never read) | 174/2,172 | 195/2,310 |

"Best possible" keeps only the node the full arm acted on, plus its ancestors and attached text:
the smallest observation this closure rule allows that still contains the planner's target. It is
an upper bound on any pruner's cut under this harness. It does not guarantee the planner still
succeeds.

Why Jev kept the whole page on 20/50 held-out episodes: those pages are small (median 6.5 elements
against 16.5 on the pages it did prune). There, even a perfect prune would have cut only about a
quarter of the planner's tokens. Half the positive nodes are containers that the ancestor closure
puts back. And much of the planner's request is question text that pruning the element list
cannot touch: the action instructions and, on text-input pages, up to 255 utterance spans per
input. Even the best possible prune keeps about half the planner's tokens overall (cut 49.8%).
**In each split, 26 of 50 episodes cannot reach a 40% cut under any pruner.** The
aggregate 40% bar was reachable only by pruning the other pages close to the minimum. Jev's
keep-everything answers on small pages lost about a quarter of those pages' tokens, not the bar.

The whole-page tasks: ascending-numbers, bisect-angle, the four choose-date variants, choose-list,
circle-center, click-button-sequence, the four click-collapsible variants, click-menu-2,
click-shades, click-test, copy-paste, count-sides, drag-circle. Held-out adds
click-checkboxes-large.

## 2. Economics

Pruner cost fits one term per element: **442.6 input tokens per element, about 147.5 per Noul
question**, intercept −6.2, R² 0.998, N=100 requests. A two-term fit (409.1 per element,
0.385 per state byte, R² 0.998) puts the state, sent once per request, at 28,869 of 340,986
held-out pruner tokens (8.5%). The questions carry the rest.

Break-even: pruning pays when `c × planner tokens saved ≥ pruner tokens`, where `c` is the
planner's input price per token divided by Jev's. With a Jev planner, `c = 1`. Equivalently, `c`
is how many planner calls one prune must serve.

| Design (held-out) | Pruner tokens | Break-even `c` |
|---|---:|---:|
| Measured design, measured cut (25.9%) | 340,986 (measured) | **13.56** |
| Measured design, at the 40% bar | 340,986 | 8.77 |
| Measured design, best possible cut (49.8%) | 340,986 | 7.05 |
| H1 one Noul, best possible cut | 132,908 est | **2.75** |
| H1 one Noul, text runs skipped, best possible cut | 124,125 est | 2.57 |
| H3 node-text-only state, best possible cut | 312,117 est | 6.45 |
| H2 keep cut fitted on dev, best possible cut | 340,986 | 7.05 |
| H1 + H3 + text runs skipped (not one variable) | 95,257 est | 1.97 |

Dev gives the same picture (13.49 / 8.65 / 6.96 / 2.72 / 2.55 / 6.37 / 6.96 / 1.95).

**With a Jev planner at one step per prune, no design in this family can pay, even with a perfect
cut.** The cheapest combination still needs `c ≈ 2`: either a planner at least about twice Jev's
input price per token, or one prune reused across at least two planner calls on an unchanged page.
Both costs grow with page size. The pruner spends about 443 input tokens per element, while the
full planner request averages about 126 (held-out: 1,944.7 tokens over a mean of 15.4 elements).
So the pruner costs about 3.5× the planner per element, and bigger pages should not close the gap
[INFERENCE: not measured on a native AX tree].

## 3. Ranked one-variable hypotheses for a dev loop

Ranked by the break-even `c` each could reach at the best possible cut. Lower is better, and only
`c ≤ 1` pays with a Jev planner.

1. **H1: one Noul (`relevant_to_current_goal ≥ 0.5`) instead of three OR'd.** Pruner cost falls an
   estimated 61% (break-even 2.75). It also removes the OR, under which any one of three "keep"
   signals retains a node, including a `safe_to_omit` below 0.5. Whether the OR is what kept the
   small pages whole is unknown, because the answers were not logged. Falsifier: a dev-seed-200
   replay with per-node answers logged shows the single Noul keeps as many nodes as the OR.
2. **H3: node-text-only pruner state.** It saves only the state part, 8.5% of pruner tokens
   (break-even 6.45). Cheap to test and nearly neutral on its own. Worth carrying only as part of
   H1. Falsifier: the two-term fit's state share is wrong, i.e. a replay with a trimmed state
   saves more or less than about 8.5%.
3. **H2: a keep cut fitted on dev.** It can only move the cut, and the cut's ceiling is 49.8%, so
   break-even stays at 7.05 or above. Even a perfect H2 cannot make the Jev pruner pay against a
   Jev planner. It could still pass the prereg's planner-only 40% bar, because the best possible
   cut (49.8%) clears it. It needs per-node answers from the same logged replay as H1.

Prerequisite for H1 and H2: the dev replay must log per-node answers. That is a live step and not
part of this bead.

## Boundary

- Offline autopsy of committed live rows. No TypeSafe request, no comparator, no new held-out data.
  The pages come from local Chrome at the pinned `dd04baf` floor (`run.py` `e0b0c42886e4ba17`,
  `jev_arm.py` `f6f712fe441cf3ac`, `tasks.json` `af8890bf4877515c`).
- The best-possible cut uses the full arm's chosen target. It is a structural ceiling, not a
  success-preserving prune. One held-out episode chose `none` and is counted at zero cut.
- Pruner token estimates for H1/H3 come from a linear fit over the 100 measured requests. They are
  not measured: no request with one Noul or a trimmed state was sent.
- Nothing here re-scores or changes the preregistered verdict. R107 stays LOSE.
