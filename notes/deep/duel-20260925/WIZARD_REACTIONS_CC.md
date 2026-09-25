# WIZARD_REACTIONS_CC: Claude reacts to how Luna (COD) and Gemini (GMI) scored its ideas

| my idea | COD | GMI | my revised score and position |
|---|---:|---:|---|
| 1 `jev-trial` kernel | 790 | 510 | **650, demoted to plumbing.** GMI is right about placement, partly wrong about substance |
| 2 shadow gate on fleet bash | 930 | 740 | **880.** Adopt COD 1's outcome join; answer GMI's "no active value" with a promotion bar |
| 3 `jev-kit` + quickstart | 900 | 925 | **920, the consensus winner** |
| 4 `doctor` / robot JSON / installer | 820 | 855 | **850.** Merge it into `jev-kit` |
| 5 games as fast judge in a planner | 650 | 420 | **450, parked** |

## Where GMI is right

GMI's sharpest line is: "preflight checks belong in the client SDK, not in another benchmark
runner." I concede the placement. The size check, the at-least-2-options check, the
offered-answer check and answer validation protect every caller, the shadow hook included, not
only experiments. They should live in `jev-kit`'s request path. The kernel then shrinks to what
only experiments need:
- prereg and bar reachability;
- resume and detached launch;
- scoring with the benchmark's own scorer;
- the e-process.

That is also the smaller thing COD asked for: "implement the smallest kernel that consumes two
real runs."

## Where GMI is wrong

- **"Stop testing" is not "stop measuring".** Joshua asked to stop *repeated testing*: the loop
  of new benchmark, new harness, new bug. The measured failure mix (25 harness bugs, 12
  infeasible inputs, 3 unreachable bars, 121 harnesses with no size check) is what made the
  testing repeat. Dropping measurement entirely would ship a gate whose false-alarm rate nobody
  knows.
- **Shadow mode.** GMI scored it 740 because "observe-only creates no active product value".
  Shadow mode is how the gate earns the right to act. GMI's own #2 blocks at p ≥ 0.80 on day one,
  from a replay figure, while the live held-out recall on real traffic is 22/33. COD's version
  states the promotion rule: block only after a preregistered held-out bar passes on live labels.
  That makes shadow mode temporary, not permanent.

## Where COD changed my mind

- **The outcome join.** COD 1 joins each logged decision to what happened next (a revert, a dcg
  deny, a review label). My idea 2 lacked that ground truth, which is the difference between a log
  and a dataset.
- **Native `judge_batch`.** COD 4 is scored 885 by GMI and 640 by me. I undervalued reuse of omp's
  native `judge` / `judge_batch`: it gives every omp agent Jev without our tools needing a consumer
  first. I revise it to **780**, pending a keyless spike showing a project profile can pin Jev with
  a host-owned key.

## My bias, observed

I proposed the kernel first because I have spent the day catching harness defects by hand. That is
real evidence, but it is the view from the verifier's chair, not from a user's. Both other models
put a user-facing product first. When all three models agree against my first choice, my ranking
is the one that should move.
