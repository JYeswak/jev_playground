# Honesty pass 8 — the 77 commits since pass 7 (2026-09-20)

Same rule as prior passes. **USER** = a non-lane reader can install, run or read it and get
value; **ENABLER** = it makes USER work possible and something runs it; **PROCESS** = it measures
or describes our own work and nothing branches on it.

## Tally

```
USER 34 · ENABLER 29 · PROCESS 14 · UNKNOWN 0   (77 commits)
USER share 44%   ENABLER share 38%   verdict: HEALTHY
```

Pass 5 36% → 6 45% → 7 52% → **8 44%**. USER share fell and the window is still the strongest of
the session, because **ENABLER nearly doubled and that was the point of the window.** Joshua
asked why we were not hardening the mistakes we keep making; three guards got built. A guard is
ENABLER by this rubric — it is not something an outsider reads — and counting it as USER to
protect a percentage would be exactly the reward-hacking this pass exists to catch.

## What this window actually produced

**Four guards, all wired, none hand-run:**

| instrument | fires on | arms |
|---|---|---:|
| `vgrep.sh` | a proof-grep matching zero lines | 8 |
| `pinned-denominator.sh` | a claimed count ≠ its regeneration | 11 |
| `pin-liveness.sh` | a digest pinned to a file peers append to | 8 |
| `denominator-sweep.sh` | the public claim set, + REFUSE when relocated | 3 |

Stage 80 went 15 → **19 PASS** selftest lines. No new gate stages; instruments stayed frozen.

**Two refusals with triggers instead of guards** — R46 staged-exposure (git has no `pre-checkout`
hook; verified from the git binary, not the argument) and R47 callback-sha (a runtime string no
hook sees, and a presence check false-positives on legitimate `BLOCKED`). The census re-run then
found the ranking **unchanged with no fifth instance**, which is what convergence looks like.

**Public surface got more honest, not more impressive:** the CASS findings page landed and was
then *weakened* by its own review and *re-strengthened* by human calibration; the README's
latency band was replaced after 0 of 10 calls landed inside it; the framing-flip claim became
reproducible for the first time; `INTEGRATIONS.md` now carries a section titled *"Numbers a
reader cannot verify and neither can we."*

## The measurement that answers Joshua's question

```
GATED classes, recurrences this session    TESTS.md 1 · numerals 0 · readme-counts 3 caught
UNGATED classes                            selector/silent-zero 26 · denominator drift 8
```

**Rules did not stop the defects. Commands did.** The sharpest instance is mine: I wrote *"a
pinned digest cannot point at a live shared file"* in a commit message, violated it in that same
batch, and took the lane RED an hour later. `pin-liveness.sh` now fires on the pre-fix
`STATUS.tsv` naming the exact row.

## My own defect count for the window

**Five `vgrep` catches on my own greps**, plus a fourth pipe-exit misread (`| head` → head's
`rc=0`), plus one false-defect-in-progress against a pane's correct work (argv vs shell string).
Every one was a verification error, not a judgment error. **The guards now catch me faster than
I generate the class**, which is the only durable version of "stop making these mistakes".

## Actions

1. The pipe-exit misread is now at four instances and has no guard. It is mechanizable in
   principle (a wrapper that refuses `| head`/`| tail` on a status-bearing command) — next
   hardening candidate, with the same Creation Gate discipline.
2. Keep the panes queued, not tasked. Two idle callbacks this session were mine for dispatching
   single units; queues of 2–3 with "start the next yourself" eliminated it.

## NO-CLAIM

One reader, classifying from commit subjects over a 77-commit window. Guards counted ENABLER
throughout; counting them USER would read ~62% and would be flattering rather than true. Passes
5–8 share a judge with no anchored rubric, so the trend is directional, not metric.
