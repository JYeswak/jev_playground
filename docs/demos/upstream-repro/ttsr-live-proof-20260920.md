# TTSR rules fire live — three environments, two models, one claim of mine corrected `[live]`

The SUGGEST leg, proven where it counts: a real interactive agent session, not a CLI harness.

## Result

| environment | A `glob 2>/dev/null` | B `\| tail; echo $?` | C control (no glob, no pipe) |
|---|---|---|---|
| `omp ttsr test --rule` (CLI harness) | fires | fires | quiet |
| fresh `omp -p` (non-interactive) | **FIRED** `bash-glob-silenced` | — | — |
| **live tmux pane, Muse Spark 1.3** | **FIRED** `bash-glob-silenced` | **FIRED** `bash-pipe-exit` | **QUIET** |

Three environments, two models (Claude and `muse-code/muse-spark-1.3-contributor`), and the
control stays quiet in all three. The rules carry no `agents:` scoping, and the cross-model
result is consistent with that.

## Binding is at session start, measured both ways

The session that **created** the rules never fired on a known-bad. A session started **after**
they landed fires on the identical command. Install is not activation — the same trap as hooks.

## The claim of mine that this corrects

I wrote in `f22f6f7` that TTSR **blocks**: *"the command never executed as written."* That came
from a fresh `omp -p` agent reporting it. **The live pane shows otherwise.** The banner reads:

```
⚠ Injecting rule: bash-pipe-exit  ↶
```

and command B's output is present in the transcript — `verify-other-reasons.sh … rc=0`. It ran.

**So the honest mechanism is INJECTION, not enforcement.** The rule text is pushed into the
agent's context at the moment of the matching tool call; whether the command executes depends
on the agent complying. The `-p` agent complied and re-ran a corrected form, and I read its
compliance as the tool's enforcement. **Same error shape as everything else this session: I
read a downstream effect as proof of an upstream mechanism.**

This weakens the Creation Gate answer I gave. TTSR is not a gate by the boundary test — *does
running code branch on it?* — because the branch is the agent's judgement, not the runtime's.
It is strictly stronger than prose (prose does not appear at the moment of the mistake) and
strictly weaker than `dcg`, which denies the call outright. It sits between them, and the
commit message that called it a gate overstated it.

## What the rules found while proving themselves

Case A's compliant re-run, in the first fresh session: `work/*/package.json` expands to **54
paths, 31 of which do not exist**. Ground truth re-derived here: **23 real files, 54 subdirs.**
The `0` was correct — but `2>/dev/null` would have hidden 31 `No such file or directory`
errors, making "searched 23 files, found nothing" indistinguishable from "searched nothing."

A second fresh agent, complying with the same rule, then reported **"zero package.json files
exist anywhere under work/*/"** — false, and it built a conclusion on it. **A rule that forces
you to look does not guarantee you read what you saw.** It closes the silence failure, not the
misreading failure.

## NO-CLAIM

Three environments, two models, one machine, one repo. No nuisance-rate measurement yet: the
retirement condition for both rules is a 30-day harvest window showing the class below 50
occurrences, and nothing here says how often these fire unhelpfully during ordinary work. The
rules detect a **precondition**, never the mistake — FP floor 0.15 for both, driven by author
intent, which no string scan can see.
