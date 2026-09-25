# WIZARD_IDEAS_CC: Claude (pane 1, AmberWillow)

Disclosure: I wrote `NEXT-STAGE-PLAN.md` and I orchestrate this duel, so my ideas carry
author bias. Score them harder, not softer.

Evidence behind these ideas (measured 2026-09-25):
- **Failure mix.** 120 NEGATIVE_EVIDENCE rows: 25 harness bugs, 12 infeasible inputs, 15
  underpowered, 15 process. Only 4 are clean losses by a live Jev arm (`local://failure-taxonomy.md`).
- **Prose rules did not stop repeats.** Written rules failed to stop four failure classes from
  recurring. The only check that did stop a class was one that runs before spend (R114).
- **The e-process has no callers.** It has 0 non-test callers. No `doctor`, no robot JSON and no
  installer exist (`local://doctrine-adoption.md`).
- **Only test callers.** Our Jev omp tools have only test callers (`jev-ja32`).
- **Today's three live-run defects** were all input errors: scroll-text 18/20 where our scorer
  copy said 20/20; `jev-jjwt`'s bar was unreachable; MiniWoB halted on a Choice with one option.

## 1. `jev-trial`: one experiment kernel whose preflight refuses what our rules only describe

**What it is.** A small shared runner, Python first (most harnesses are Python), with a Node
twin later. A benchmark supplies four hooks: a dataset of captured observations, a state
builder, a question builder, and the benchmark's own scorer. The kernel owns everything else.

**What the preflight refuses, keylessly, before any call:**
- a state over the size limit (`jev-state-size`);
- a Choice with fewer than 2 options;
- a question whose solving action is not among the offered options;
- a prereg bar that even a perfect arm cannot reach (`bar-reachable.py`);
- a grader the state builder can import;
- an arm flag with no effect: every arm must change its requests relative to the `none` arm;
- a dirty file among the modules actually imported (hash every repo module in `sys.modules`,
  not one hand-picked file).

**What it owns at run time:** a detached supervised launch, per-episode resume, halt rules, the
e-process monitor for anytime-valid early stop, and one receipt format.

**Why it is the best idea.** Every trap in the pane-1 handoff becomes an error message, and
AGENTS.md can shrink. It turns 25 harness bugs, 12 infeasible inputs and 3 unreachable bars into
refusals that happen before any spend.

**Risk.** It can become a framework. Keep it to about 500 lines with 4 hooks. Migrate MiniWoB
first, since it is live and has the most defects, and prove it by replaying today's three defects
as refusals.

## 2. Jev in the fleet's hot path, shadow mode: the first real consumer

**What it is.** An omp `tool_call` pre-hook that asks Jev about the command gate on every bash
call.
- It never blocks and logs every decision.
- A daily report compares the logged decisions with what happened next (a revert, a dcg deny, a
  "undo that").

**Why.** It turns a measured win (78/100 caught at 1/300 false alarms) into a tool that runs all
day. Fleet traffic then becomes our labelled data, which is Rule 13's external oracle in live
form. It also answers `jev-ja32`: the tools have had no real consumer. The reward is our own
daily use, not a ruling.

**Risk.** Cost and latency on every call. Bash calls only, with a ~1 s timeout and a fail-open
path, and we report calls and spend per session.

## 3. `jev-kit` published, with a 5-minute stranger quickstart and a README generated from receipts

**What it is.** A package on top of the official SDK: size preflight, validator, confidence-gate
policies with a named fail-safe side, a fake asker, `jev-trial`, and the omp hook from idea 2 as
the worked example.
- It is installable from GitHub in one line.
- The nightly stranger run proves clone to first gated decision.
- The README becomes a short quickstart plus a results table rendered from receipts. It stops
  being a 55 KB ledger.

**Why.** This is mission stage 5. Today a stranger faces a 55 KB README.

## 4. An agent-first surface for every tool we keep: `doctor`, robot JSON, one-line install

**What it is.** Jeffrey's tool contract applied to what we ship (`jev-kit`, `jev-trial`, the
hooks):
- `doctor` checks the key, SDK pin, model id, input limit and hook discovery;
- `--robot` gives stable JSON output;
- a one-line installer.

**Why.** The doctrine audit found all three ABSENT. Other agents are our first users, and his
tools spread because agents can drive them without a manual.

## 5. Re-scope games and computer use to Jev-as-fast-judge inside a planner

**What it is.** Stop measuring Jev as the sole policy. Use Jev as a prior, pruner or critic
inside search, for example Jev-PUCT on Jericho, or ranking MiniWoB candidates for a scripted
executor. The comparator is the same planner without Jev.

**Why.** Sole-policy runs keep losing to a button prior (Emerald) or dying on harness plumbing.
The planner shape plays to Jev's price and latency. It also keeps Joshua's "watch it play" goal.

**Risk.** Planners are harness-heavy. Do it only on `jev-trial`.

## Also considered (cut)

- a receipt-driven EVAL generator;
- freezing AGENTS.md at 800 lines;
- converting each trap to a TTSR rule;
- an e-process-only scoring policy;
- mutation-kill ledger CI;
- beads-as-handoff generator;
- a Jev inbox triage for the conductor;
- skill routing with Jev;
- CI log triage;
- the Grok comparator;
- a public dashboard;
- `hub`-supervised live runs;
- reviving the scorer-by-execution MiniWoB feasibility check;
- a fixture provenance hash check;
- deleting unused `work/` dirs;
- daily cost report;
- pre-registration templates;
- the use-case-map surface picker;
- an arm-effect diff test.

Most of these are sub-parts of ideas 1-4.
