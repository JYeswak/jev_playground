# jev_playground

Measure what Jev can actually do before you build on it.

![What this lane has proven so far](visual/hero.jpg)

## TL;DR

**The problem.** [Jev](https://typesafe.ai) is fast and cheap enough to call on every item, which
makes it tempting to build things with it before knowing whether the thing is worth building. Most
"AI could do this" ideas die on a measurement nobody took.

**What this is.** A gauntlet, not a demo factory. Seventeen candidate ideas were adjudicated here and
**zero were promoted** to their own project. The product is the ruling plus the evidence for
everything ruled out.

**What you get.** Three tools that run offline with no API key, and read your own logs:

| Tool | Answers | Verdict it produced |
|---|---|---|
| [`demos/usage-shape`](demos/usage-shape) | Which token lever is worth attacking? | 98.878% of tokens are re-sent context |
| [`demos/routing-backtest`](demos/routing-backtest) | Would a cheaper-model router have paid? | 0.0447%. Candidate ruled out |
| [`demos/retransmit-whatif`](demos/retransmit-whatif) | How much is the top lever worth? | Upper bound only, with residual |

**The table above is reproducible on your own machine in about 20 seconds.** On a corpus of 4,619
real agent sessions, context retransmission dominates and model output is 0.140% of tokens, which
kills three whole classes of cost intervention on that workload before anyone writes code.

## What we learned about using Jev

Seven findings from live calls against `api.typesafe.ai`, each with what it means for the next
implementation. Every one is measured here, and the limits are stated because most of them cost us
a retraction to learn.

- **The measurement is the asset, not the model's prior.** Given a measured usage shape in its
  state, Jev derives the consequence that follows from it. Withhold that shape and ask the same two
  questions, and the verdict flips: `router_pays` moves from 0.21 to 0.59 and the lever it picks
  drops from 0.75 to 0.49 confidence. **Apply it by spending the effort on the measurement and
  giving Jev the state; a judgment model does not discover the lever for you.**
- **Framing leaks through the criteria, not just the state.** A criterion worded
  *"reduce the number of turns, since each re-sends the whole context"* teaches while it asks. The
  answer then tracks your implication rather than the evidence. **Apply it by stripping rationale
  out of criterion text, and by running the same question with your evidence withheld as a control.**
- **Output moves on state content that has nothing to do with the question.** Adding three
  provenance fields to a request shifted `noul` from 0.26 to 0.36 with the question unchanged.
  **Apply it by pinning the exact request bytes and versioning them, the way you would a prompt.**
- **Agreement from a model shown your own summary is same-origin and counts once.** It is not
  independent confirmation, however much it reads like it. **Apply it by treating concurrence as a
  consistency check on your reasoning, never as a second source.**
- **A handful of calls characterises nothing.** Across three runs with three slightly different
  states the same question returned 0.21, 0.26 and 0.36. **Apply it by refusing the word
  "calibrated" until you have run enough trials to earn it.**
- **The typed surface is the reason to use it.** Requests are `{model, state, questions}` with
  `noul` for a probability and `choice` for a ranked set, and both admit a real none-equivalent.
  That is what makes an abstention expressible instead of inferred from a low score. **Apply it by
  designing the question so "none of these" is a first-class answer.**
- **It is fast and cheap enough to run on every item.** Measured 743 to 773 ms per call at 523 to
  629 input tokens. An independent public write-up reports 0.35 to 0.52 s medians against 1.68 to
  4.85 s for a general model at comparable agreement. **Apply it where per-item judgment was
  previously too slow or too expensive to attempt, and not where a deterministic rule already
  works.**

The full retraction, with both sides of the framing test, is in
[`docs/demos/jev-probe/NOTE-framing-leak.md`](docs/demos/jev-probe/NOTE-framing-leak.md).

## What you can run

Each tool takes one command, reads your own logs, and writes a receipt that states its denominator
before any share. No API key. No network.

### `demos/usage-shape` — where does your agent spend go?

```bash
node demos/usage-shape/bin/shape.mjs ~/.claude/projects
```

`~/.claude/projects` is where Claude Code keeps session logs. If you do not use Claude Code, pass
your own `.jsonl` files or a directory of them; the tool takes either and reports how many files and
sessions it actually read.

Measured on one machine, 2026-09-18, over 4,626 files / 4,619 sessions / 488,724 billed turns,
models `claude-opus-5` (408,265 turns), `claude-opus-4-8` (49,842), `claude-fable-5` (15,658) and six
others:

| Share of tokens | Lever | Reduce it by |
|---:|---|---|
| **98.878%** | retransmitted context (cache read) | fewer turns, or less parked in context |
| 0.980% | context first-write | reading less into context at all |
| 0.140% | model output | asking for less output |
| 0.002% | fresh input | shorter prompts |

Mean context re-sent per turn: **341,496 tokens**. Those four figures are **measurements** over the
stated corpus, re-derivable by the command above, and the run that produced them is committed at
[`docs/demos/jev-probe/census-20260918.json`](docs/demos/jev-probe/census-20260918.json) with its
own denominator and skip counts. A reviewer looked for it under `demos/usage-shape/runs/` and found
nothing, which is fair: the receipt was real and undiscoverable from the tool's own directory.

A separate and weaker claim: weighting them by *assumed* relative rates (cache read 0.1x input,
output 5x input) puts retransmission near **84% of cost**. That is an **estimate under assumed
rates, not a measured bill**. The rates are unattributed here and no invoice was observed. It is
labelled because a reviewer caught it sitting beside the measurements with no class distinction,
where it read as measured fact.

### `demos/routing-backtest` — would a cheaper-model router have paid?

```bash
cd demos/routing-backtest
npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out runs/try.json
```

On 30 classifiable turns it measured **0.0447%** savings, and the candidate was **ruled out**. The
verdict is scoped on purpose: it answers *same-turn price substitution*, not turn elimination.

21 tests, and **7/7 planted mutations caught**. Three of those were real holes found under a suite
that was already green, one of them directly beneath the published figure. Reproduce that claim with
`npm run mutate`: it plants seven named mutations one at a time, requires the baseline green first,
restores every file and compares by sha256, and exits non-zero if any mutation survives.

### `demos/retransmit-whatif` — how much is the top lever worth?

An upper bound on per-turn retransmission reduction, with an explicit residual row that reconciles
to zero, and its assumptions stated in both README and receipt: a reduction removes `cacheRead * r`
only, while turns, model behaviour, retrieval quality and tool behaviour all stay unchanged.

A reviewer graded it **rung-2 fail as a demo** ("deterministic calculator; no judgment model
needed") and kept it as an instrument. Its bound does **not** cover turn elimination. Citing it as
though it did would repeat the exact scoping defect the backtest already made once.

## Install

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
./scripts/sync-docs.sh          # fetches the primary sources; safe to re-run
./scripts/sync-docs.sh --check  # verifies every mirrored byte against MANIFEST.tsv
```

No API key needed to install, and none to run any tool above.

## What it does

- Mirrors the primary Jev sources locally, so every claim here cites bytes you can re-fetch
- Adjudicates candidate ideas against a rung ladder, and records the ones that die
- Ships the measurement tools that killed them, so you can re-run the kill on your own data
- Keeps a dead-end ledger with a reopen condition on every entry

## How it works

Each candidate climbs a rung ladder. A candidate that fails a rung is ruled out with a receipt, and
the reason lands in [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md) together with the condition that
would reopen it. `docs/demos/STATUS.tsv` is the machine-readable state of record, one row per
candidate, and `./scripts/lane-status.sh` exits non-zero if any verdict cites a receipt that does
not exist.

Claims carry a class. A measurement over a stated corpus, a benchmark on a stated denominator, a
statistical mean, a negative-control result and an estimate under assumed rates are five different
things, and mixing them is how a number gets believed harder than it earned.

## Quick start

```bash
bash foundation/gates.sh
```

```
PASS 10-fixture-integrity (0s)
PASS 20-receipt-freshness (0s)
PASS 30-no-secrets (1s)
PASS 40-omp-compact-replay (1s)
PASS 50-house-gates (1s)
PASS 60-staged-deletion-lane (3s)
PASS 70-tests-registry-sync (0s)
PASS 80-lane-instrument-selftests (12s)
PASS 90-sidecar-verifier-wrapper (1s)
gates: ALL GREEN
```

Nine stages. Each has a planted bad input that turns it red, listed in [`GATES.md`](GATES.md),
because a gate that cannot fail is not a gate. Re-derive the count from `foundation/gates.d/`; a
number written here goes stale silently, and this one did, having said seven.

**On a fresh clone you get seven of nine, not `ALL GREEN`, and the output above is from a developed
checkout.** Measured by running the suite inside a frozen clone of a pinned commit
(`scripts/verify-frozen.sh`), which exits non-zero for that reason: stages
10/20/30/60/70/80/90 pass from a bare clone. Stage 40 needs
`npm install` inside `compaction/`, so that stage does need the network, contrary to what this line
claimed until it was measured. Stage 50 needs a Beads DAG imported with `br import`, since only
`.beads/issues.jsonl` is tracked and the database is not. Neither is a gate defect; both are state a
clone legitimately does not carry.

## Command reference

| Command | Effect | Needs a key? |
|---|---|---|
| `bash foundation/gates.sh` | nine gate stages over the whole repo | no |
| `bash foundation/gates.sh --selftest` | every stage against its planted bad input | no |
| `bash scripts/verify-frozen.sh [ref]` | runs the suites in a clone pinned to a commit | no |
| `./scripts/lane-status.sh` | renders `docs/demos/STATUS.tsv`, verifies every cited receipt | no |
| `node demos/usage-shape/bin/shape.mjs <dir>` | lever census over session logs | no |
| `cd demos/routing-backtest && npm test` | 21 tests | no |
| `cd demos/routing-backtest && npm run mutate` | 7 planted mutations, restore and compare | no |
| `node scripts/jev-probe.mjs --replay` | decodes a recorded Jev response, no network | no |
| `node scripts/jev-probe.mjs` | one live Jev call | **yes** |

The live call reads `TYPESAFE_API_KEY` from the environment and is meant to be run through a secret
manager so the key never reaches a file:

```bash
infisical run --projectId=<id> --env=prod -- node scripts/jev-probe.mjs
```

## Verify it yourself

```bash
bash foundation/gates.sh --selftest    # every stage proves it can go red
bash scripts/verify-frozen.sh          # suites run against committed bytes, not your worktree
cd demos/routing-backtest && npm run mutate
```

`verify-frozen.sh` exists because every green reported during development was measured in a worktree
that three agents were editing at once. It adds a git worktree pinned to a commit, runs the suites
there, and `cmp`s the executables. Its first run failed and found three stages that pass locally and
cannot pass from a clone, which is how the fresh-clone caveat above got measured instead of assumed.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `SyntaxError` or `Cannot find module` on any tool | node older than 20, or missing | `node --version`, then install node >= 20 |
| `gates.sh` red on `40-omp-compact-replay` | no `compaction/node_modules` in a fresh clone | `npm install --prefix compaction` |
| `gates.sh` red on `50-house-gates` | no Beads database, only the tracked JSONL | `br import` |
| `gates.sh` red on `70-tests-registry-sync` | a test file exists that `TESTS.md` does not name | add its entry to `TESTS.md` |
| `shape.mjs` reports 0 turns | logs are not a Claude Code or omp shape | check one file has `message.usage` keys |
| `jev-probe.mjs` exits 2 | no `TYPESAFE_API_KEY` in the environment | run it under a secret manager, or use `--replay` |
| `ERROR at least one session JSONL is required` | no input path given | pass a file or a directory |

## What you'll need

- `bash`, `git`, `curl`, `python3`, preinstalled on macOS and most Linux
- **`node` >= 20**, required by all three tools. Their `package.json` files declare it, and a
  machine without node fails every one of them, so check `node --version` first
- A `TYPESAFE_API_KEY` **only** for the one live call. Everything else runs without one

Runtimes, measured on an M3 Ultra: `foundation/gates.sh` about 16 s, of which stage 80 alone is 12 s;
`usage-shape` about 19 s over 4,626 files. Nothing here is instant and nothing here needs a network.

## Limitations

**Nothing has been promoted.** Seventeen candidates adjudicated: four ruled out, five cleared, eight
held, **zero promoted** to their own project. That is the deliverable rather than a shortfall, and
every reason lives in [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md), 19 entries, each carrying the
condition that would reopen it. One candidate died there because an MIT-licensed tool already ships
its surface, which is a reason to stop building and not a reason to build faster.

**A fresh clone cannot run two of the nine gate stages**, and the reasons are in Quick start above.
There is no bootstrap step that closes both, so `scripts/verify-frozen.sh` fails at HEAD by design
rather than silently.

**The `~84% of cost` figure is an estimate under assumed rates**, and the rates are unattributed
here. A reader can check that assumed rates were used, not which multiplier.

**`98.878%` is a token share on one corpus.** It is not a cost share, not universal, and the census
cannot distinguish a non-billed record from an assistant turn whose usage block is missing. 1,247,069
records carried no usage block and were skipped, which the tool reports rather than hides.

**The `0.0447%` backtest answers price substitution on a fixed set of turns.** It says nothing about
turn elimination, which the same corpus shows is the dominant lever. Getting the order of the levers
wrong costs more than getting any single lever's number wrong, and this lane made that mistake before
it measured the shape.

**The live Jev probe measures implication-tracking, not lever discovery.** Given the measured shape
in its state it returns the same ranking the logs do; with that shape withheld, the verdict flips.
Agreement from a model shown a summary of your own evidence is same-origin and counts once.
`docs/demos/jev-probe/NOTE-framing-leak.md` carries the retraction and the numbers on both sides.

**Two instruments here gate nothing.** `verify-reason-numerals.sh` is deliberately hand-run, and its
hits require a human ruling; an unruled hit re-fires every run.

## Roadmap

Phase 1 candidate: a conformance suite shared by the three session-log readers, which currently
duplicate a parser between them. Two reader-shaped defects landed in one day, so the next design
step is one contract with its own suite rather than three parsers that agree by coincidence.

Unsupported today: any tool that reads a harness other than Claude Code or omp session JSONL. A tool
pointed at another shape reports zero turns, which is a visible result rather than a silent one.

## About Contributions

*About Contributions:* Please don't take this the wrong way, but I do not accept outside
contributions for any of my projects. I simply don't have the mental bandwidth to review anything,
and it's my name on the thing, so I'm responsible for any problems it causes; thus, the risk-reward
is highly asymmetric from my perspective. I'd also have to worry about other "stakeholders," which
seems unwise for tools I mostly make for myself for free. Feel free to submit issues, and even PRs
if you want to illustrate a proposed fix, but know I won't merge them directly. Instead, I'll have
Claude or Codex review submissions via `gh` and independently decide whether and how to address
them. Bug reports in particular are welcome. Sorry if this offends, but I want to avoid wasted time
and hurt feelings. I understand this isn't in sync with the prevailing open-source ethos that seeks
community contributions, but it's the only way I can move at this velocity and keep my sanity.

## License

MIT. See [`LICENSE`](LICENSE).
