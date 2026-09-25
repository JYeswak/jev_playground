# omp-jev-review: advisory boundary line, vendored and empty diffs refused (jev-k9z.2), 2026-09-25

Pane 1 (AmberWillow). Extension: `work/omp-jev-review/src/index.ts`. Model `jev-1.13.0`, omp
18.3.1. No merge-gate authority is claimed, and no accuracy on real traffic.

## What changed

1. **Empty diff** is `review_not_applicable` (`empty-diff`), not `review_error`. Nothing to review
   is not a failure.
2. **Vendored sections** are cut before scoring: a path with a directory segment
   `node_modules`, `vendor`, `third_party`, `dist`, `build`, `.venv`, `venv`, `site-packages`,
   `docs-mirror` or `upstream`, or a lockfile. A diff whose only code is vendored is
   `review_not_applicable` (`vendored-diff`). The thin and code checks now run on the full diff
   after that cut; before, they ran on the first 12,000 characters, which the 686-commit draw
   found could turn a substantial diff thin (3 cases).
3. **Advisory line.** A scored diff with boundary >= 0.9 gets one line appended to the same
   call's git output through omp's `tool_result` hook. Nothing else is touched: other calls,
   failed git calls, and scores below 0.9 return undefined. The decision row records `comment`.

**Why 0.9.** Fire rate, not accuracy. On the 125 real code diffs the draw scored, boundary >= 0.9
fired on 3 (2.4%), >= 0.7 on 13 (10.4%). A line on one git call in ten would be a nag.

**What the bead asked for that was not ported.** Subtask 1 asked for jev-review's Score dimension
set from `jev-review/src/evaluation/questions.ts`. That set was measured on 22 real commits and
separated later-corrected commits at AUC 0.625, under its 0.75 bar
(`jev-review-real-diffs-20260919.md`). This extension's third question was cut the same way
(README, "Two questions"). Porting a measured miss would add calls without a finding, so the two
surviving Noul questions stay.

## Offline

`node --experimental-strip-types --test work/omp-jev-review/test/review.test.mjs`: 20/20. New:
empty diff and a 10k-line `node_modules` diff are `applicable:false` with zero Jev calls; the same
vendored section next to our own code is cut before the call (Jev never sees the vendored text)
while our code still scores; `isVendoredPath` does not match `src/vendor.ts` or `src/distance.ts`;
the advisory line fires at exactly 0.9, keeps the git output verbatim, fires once, and stays
silent at 0.89, on another call id and on a failed git call.

Planted defects, each restored byte-identical: vendored cut disabled (2 fail), threshold `>`
instead of `>=` (1), pending entry never cleared so it fires twice (1), comment on a failed git
call (1), empty diff back to `review_error` (1).

## Live, through the real tool path: N = 12 commits, 10 scored

A throwaway driver loaded the extension, ran `git show <sha>` through its `tool_call` handler with
real git and the real client, then fired `tool_result`. Commits come from the draw, where their
boundary scores were recorded on 2026-09-24.

| commit | draw boundary | today | behaviour today | advisory line |
|---|---:|---:|---:|---|
| 0f6cb2d8 | 0.94 | 0.93 | 0.30 | yes |
| a2dca29b | 0.93 | 0.92 | 0.11 | yes |
| 7f5ca256 | 0.91 | 0.91 | 0.10 | yes |
| 959c3ca8 | 0.87 | 0.85 | 0.78 | no |
| 34f1c163 | 0.85 | 0.79 | 0.72 | no |
| bdf970bd | 0.04 | 0.05 | 0.65 | no |
| 1f2e4032 | 0.05 | 0.05 | 0.20 | no |
| 88fd55bd | 0.05 | 0.06 | 0.11 | no |
| 2027b661 | 0.04 | 0.09 | 0.13 | no |
| ff99df89 | 0.05 | 0.05 | 0.78 | no |
| d2314321 | (scored by the old gate) | not applicable, `non-code-diff` | - | no |
| 3e20121e | (scored by the old gate) | not applicable, `non-code-diff` | - | no |

Largest change between the two days: 0.06 (34f1c163). The same three commits cross 0.9 both
days. Latency p50 about 190 ms. Test-retest on 10 diffs is a stability number, not accuracy.

## L3: real omp sessions, both directions

`omp --profile claude -p --mode json --model anthropic/claude-sonnet-5 --thinking off
--no-extensions -e work/omp-jev-review/src/index.ts`, under `infisical run` with the four
provider keys unset, from the repo root. `--no-extensions` keeps every other extension out.

- **Fires**, session `01a0d8db-e3e1-7248-8e03-3030a149b7b0`: the model ran `git show a2dca29b .`;
  the tool result it received ends with `[jev-review advisory, no merge authority] boundary 0.92:
  this diff may touch a security, permission, or authentication boundary. Fires on about 2% of
  code diffs; accuracy unmeasured.`, and its reply quotes that line.
- **Silent**, session `01a0d8dc-a9f0-70ec-99bc-0320e61800a4`: `git show bdf970bd .`, boundary
  0.05; the tool result carries no advisory line and the reply says none appeared.

## NO-CLAIM

- No boundary label exists for any real diff here, so whether a fired line is right is unmeasured.
  Of the three that fire, a reader can check the subjects: redaction and a client gate
  (0f6cb2d8), the first live key use (a2dca29b), a publish export with a secret scan (7f5ca256).
- A keyword pattern also scored 7/7 on the hand-built boundary cases (jev-k9z.2, 2026-09-21);
  it has not been run against these real diffs.
- Not installed for the fleet. Registering it in `.omp/config.yml` is a kit-guard gated edit and
  needs a `KIT_GATE_EDIT=1` session. Until then it runs only where `-e` loads it.
