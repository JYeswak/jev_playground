# The file-type doctrine pack: wisdom keyed to what you just opened `[live]`

Joshua, 2026-09-20: *"there are common threads and themes in ALL of Jeffreys work that we run into
ALL the time - why repeat problems he's already solved"* and *"every single type of file we write
has some sort of insight or wisdom that we can inject to guide agents - but it can't be noise."*

## What was wrong with the previous approach

We were atomizing **36,692** individually-addressable doctrine rules and asking, one at a time, *is
this mechanizable as a string match?* Answer: **3.00%** CI[1.59, 5.60], and only **1.00%**
CI[0.34, 2.90] universal — implying 114–967 candidates, of which most fail our prevalence bar
because they address defects **Jeffrey** commits and we may not. Two passes produced **zero** rules.

That framing throws away the signal. Doctrine with no trigger *string* still has a trigger **file
type**, and recurrence across repos is the weight. omp's own 27 builtins are already this shape:
`rs-box-leak` on `tool:edit(*.rs)`, `go-range-int` on `*.go`.

## The trigger, measured before anything was written

```yaml
condition: '\S'
scope: tool:edit(*.rs), tool:write(*.rs)
interruptMode: never
repeatMode: once
```

| probe | result |
|---|---|
| `.rs` edit | FIRES |
| `.rs` write | FIRES |
| `.md` edit | QUIET |
| bash mentioning `cargo` | QUIET |

One injection per session per file type, in-band on the tool result, never interrupting.

## What we write — and the correction that inverted the plan

A first measurement over **3 days in this repo alone** produced `md 1261 / mjs 292 / … py 56`, no
Rust, and the conclusion *"his Rust doctrine is not our leverage."* **Inverted.** Joshua caught it.
Across every git repo under `~/Developer`, 30 days:

```
json 17,915 · rs 17,416 · md 17,287 · sh 7,199 · ts 6,538 · toml 3,470 · py 2,930
```

`omp-orchestrator` 2,782 · `franken-harvest` 1,267 · `frankenmermaid` 1,195 ·
`zeststream-cast` 1,153 · `uds` 494.

Session frequency over **1,778 sessions** spanning 45 session dirs and 6 profiles (codex 899,
claude 493, muse 262, grok 92, jev-lab 57, glm 21 — jev a minority): `md 20.9 · py 8.0 · txt 7.7 ·
rs 6.9 · json 5.0 · sh 4.2 · toml 3.8`. `.rs` is only 6.9% of sessions but top-two by git volume:
Rust work concentrates into fewer, much heavier sessions, which is where a once-per-session
injection pays.

## The anti-duplication step — the point, applied to ourselves

Against omp's 12 builtin `rs-*`/`go-*` rules:

| category | n | disposition |
|---|---|---|
| A — already caught free | 6 | **banned from the file**, with a one-line in-rule note saying why |
| B — partial, gap named | 3 | unsafe discipline, error shape, parking_lot selection |
| C — uncovered | 3 | newtype/typestate, oracle-per-domain, perf techniques |

Category A is the most valuable output: work we did not do.

## Shipped

`~/.agents/rules/ft-{rs,sh,md}-doctrine.md` — system-wide (`agents` provider, profile- and
project-independent), single copy each, every thread cited `repo@sha:file:line`. Bar applied to
every line: **it must name a TOOL, a COMMAND, or a CHECK the reader would otherwise skip.**
Selftest **64 ok / 0 failed**.

Cut rather than crammed: perf-techniques (rs), planted-trip, check.sh-mentions,
verbatim-preservation, mirror-TS, general no-unwrap.

## Live-fire — L3, in fresh sessions outside this repo

`ft-rs-doctrine` fired on a `.rs` write in `/tmp/rsproof` and delivered all five threads with
citations, e.g. *"New domain logic: name its external oracle and differentially test against it;
his sqlite runs against rusqlite (`frankensqlite@b482eddd:crates/fsqlite-e2e/tests/comparison_affinity_oracle_e2e.rs:1`)"*.
`ft-sh-doctrine` and `ft-md-doctrine` fired on `run.sh` and `NOTES.md` in `/tmp/ftproof`.

**Both agents then reported the doctrine did not BIND**, because the files were dictated fixtures
with no verdict, no `rc` capture, and no numeric claim. That is the honest cost of once-per-session
routing and it is the number to watch: the injection is bounded, the applicability is not
guaranteed.

## NO-CLAIM

No nuisance-rate measurement over ordinary work yet — three synthetic live-fires, one machine.
Thread selection is one labeller. `fh` ledger age ~307h, so rows are structural at pinned
revisions rather than fresh. `json`, `toml`, `py` and `ts` have no rule yet; `py` is second by
session frequency and currently carries **zero** threads. Retire any rule whose type falls below
the session-frequency floor for 30 days.
