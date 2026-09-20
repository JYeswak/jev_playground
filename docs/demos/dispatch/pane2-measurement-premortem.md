# P2 — PRE-MORTEM, not an implementation. Kill this design or fix it before anyone writes code.

Joshua: *"I cannot afford another bullshit implementation. I want EVERY tool call measured across
all omp surfaces, observable and reportable, with measurements on how we are improving it."*

**Your job in Unit 1 is to try to kill the design below.** If it survives, we build it. If it
does not, you say so and we do not. A REFUSE here is worth more than a shipped thing.

## What I measured before writing this (open these controls, do not trust them)

```
dcg_allow rows, all profiles          221,722
tool_call_observed rows, jev-lab        3,291
toolCallId occurrences, jev-lab         3,167     <-- FEWER than observed rows
```

**The third line is already a defect in my own baseline.** Observed rows exceed the thing they
observe, so either the observer double-writes, or `toolCallId` is not the right denominator, or
both streams count different events. **I do not know which, and neither does anyone else.**
Resolve that first — every claim about "coverage" is meaningless until the denominator is real.

## The design I think is right, stated so you can attack it

**Claim: we do not need new capture. We need a report over capture we already have.**

- dcg already sees **every bash tool call** — 221,722 decision rows — before execution.
- `tool_call_observed` already exists per tool call in a profile that runs the observer.
- The four `guardpack` classes are **regexes over the same bash strings dcg already reads.**

So the build is: **a reporter over existing session JSONL**, emitting per-surface counts, plus
**golden artifacts** so the report's own shape cannot drift silently.

## Attack these specifically

1. **Is guardpack tier-1 redundant with `omp-harm-rule`?** Harm-rule is four regexes over bash
   strings, observe-only, writing `harm_pass|harm_fire|harm_error` decision rows, profile-scoped,
   with an install receipt — **and it is proven live (115 pass, 14 fire).** Guardpack tier-1 is
   four regexes over bash strings writing to `~/.guardpack/warnings.jsonl`, a private log nothing
   else reads. **My current read: guardpack tier-1 should be deleted and its four classes added
   to the harm-rule extension shape instead.** Argue me out of it or confirm it.
2. **What does "signal to noise" mean here, operationally?** A warning is not a prevented defect.
   We can count firings; we cannot observe whether the agent heeded one. **If S/N is not
   measurable, say so and propose what IS** — e.g. false-positive rate against a labelled sample
   of real commands, which we can do, versus "did it help", which we cannot.
3. **What is the denominator for "every tool call"?** Bash only? Every tool? dcg sees bash; the
   observer sees tool calls in one profile. **A claim of "every" that covers only bash in one
   profile is the kind of overclaim that put `oracle` on 97 commits that never touched a test.**
4. **Does this need a model at all?** Every class so far is a regex. The harm-rule precedent is
   that the model LOST to four regexes by one recall point. **If no class needs judgment, say so
   — a Jev seat here would be ceremony.**

## Golden artifacts, per `/testing-golden-artifacts`

If the design survives, the report gets golden coverage — and the goldens must be **scrubbed**,
because every field we emit is volatile:

| artifact | deterministic? | volatility | strategy |
|---|:---:|:---:|---|
| report shape (headings, class list, column order) | Y | 2 | **exact** |
| per-class counts | N (live corpus) | 5 | **structural** — shape only, never values |
| timestamps / session ids / paths | N | 5 | **scrubbed** → `[TIMESTAMP]` `[ID]` `[PATH]` |
| totals over a PINNED fixture session | Y | 1 | **exact** |

**The pinned-fixture golden is the load-bearing one**: freeze one session JSONL as a fixture, run
the reporter over it, and freeze that output exactly. Live counts get a structural golden only —
an exact golden over a live-monotonic corpus is guaranteed test rot, and we measured that corpus
moving 1,040 → 1,110 in a single session.

`UPDATE_GOLDENS=1` regenerates; **`git diff` on the goldens is the review gate**; CI never
auto-updates. `.gitignore` gets `*.actual`. A `PROVENANCE.md` records the generator command and
the fixture's sha.

## Acceptance for Unit 1

`docs/demos/upstream-repro/measurement-premortem-20260920.md`: the denominator question resolved
with a command, a verdict on each of the four attacks, and one line — **BUILD / NARROW / REFUSE**.
No code in this unit. **If you conclude the honest answer is "fold four regexes into harm-rule
and write one reporter", that is a smaller and better outcome than what I proposed.**

Then stop and fire the callback. I will read it before Unit 2 exists.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-PREMORTEM-<BUILD|NARROW|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
