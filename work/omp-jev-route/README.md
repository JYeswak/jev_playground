# omp-jev-route

Observe-only routing ADVICE for omp. Watches `context` (turn_start proved
content-free live: `{type, turnIndex, timestamp}`, no prompt), extracts the
latest user text from `messages[]`, asks Jev systemOne whether the turn needs
a heavyweight model, writes a decision row. It never routes anything: no
evidence these scores predict anything, and a routing extension acting on an
unvalidated score is exactly what this lane rules against.

```bash
# in an omp profile extensions list:
#   - /path/to/work/omp-jev-route/src/index.ts
export TYPESAFE_API_KEY=...        # without it, rows record route_error, never advice
```

The upstream savings claim for per-turn routing inverts on our sessions — do
not re-litigate that here. The surviving signal was the blockedBy histogram
(a signal about which turns are hard); this extension judges hardness per
turn instead. No routing benefit is claimed or measured.

## Decision rows

| kind | meaning |
|---|---|
| `route_scored` | Jev answered; `probabilities` + `suggested_tier` present |
| `route_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## Real traffic: 24 rows, one turn, effective n=1

The live rows were labelled against what the turn actually became
([receipt](../../docs/demos/upstream-repro/route-rows-labelled-20260919.md),
labels in `labels-20260920.jsonl`).

| | |
|---|---|
| rows | 24 |
| **distinct turns** | **1** |
| hits | 24/24 on both questions, zero FP/FN |
| score range across all 24 | **0.01** (heavy 0.90–0.91, mechanical 0.09–0.11) |

**This is weaker than "24/24" sounds, and the number that matters is the 1.** All 24 rows
judge the same prompt in the same session, 4.5 minutes apart. The tally measures **scorer
stability, not accuracy** — it is one correct judgement repeated, not twenty-four independent
ones. Effective **n=1**.

What it does establish: on the one real turn we have, both questions were right, and the
scorer does not wobble (0.01 range where `argument` in the failure classifier moved 0.47–0.50
on byte-identical input). What it cannot establish: anything about a second turn, because
there isn't one — the `turn_start` era wrote zero scored rows, and the twin session wrote
diagnostics only.

Against the 8/9 hand-built measurement, real traffic says: **correct once, stable always.**

## Ten distinct turns: 7/10 per question, and the traps are the finding

The `n=1` problem above is closed: ten distinct turns were driven through the registered
extension, **labelled from the prompt before the scores were read**
([receipt](../../docs/demos/upstream-repro/route-ten-turns-20260919.md)).

| | precision | recall |
|---|---|---|
| `needs_heavyweight` | 4/6 (0.67) | 4/5 (0.80) |
| `mechanical` | 4/6 (0.67) | 4/5 (0.80) |

**7/10 per question, against 8/9 on hand-built cases.** The degradation is the expected shape
and it is the fifth time tonight a hand-built score failed to survive contact with real input.

### What the traps showed

| trap | shape | result |
|---|---|---|
| `bump-version` | short, heavy by construction | **MISS / MISS** — 0.09–0.11 heavy |
| `auth-grace` | short, heavy | HIT / MISS |
| `verbose-typo` | long, trivial | HIT / HIT |
| `verbose-rename` | long, trivial | **MISS** — 0.64–0.73 leaked into heavyweight |

**The scorer reads content first and length second — but length leaks.** `verbose-typo` proves
length alone does not doom a turn; `verbose-rename`, the same trap shape, leaks into
heavyweight anyway. And `bump-version` — the short prompt hiding real work — misses on both
questions, which is the failure mode that matters most for routing: *the cheap-looking turn
that isn't.*

This is why the extension **routes nothing**. A router acting on these scores would send the
compiled-version bump to a light model at 0.09 confidence.

## Process mirror (skillranker @6a74cca) — unpromoted slice

Copied PROCESS, not their corpus. Receipt:
[`docs/demos/upstream-repro/skillranker-process-mirror-20260919.md`](../../docs/demos/upstream-repro/skillranker-process-mirror-20260919.md).

When a `context` event carries `roster` (and optional injected `scores` / `fit` /
`excluded` / `alreadyLoaded` / `explicit`), the handler also writes
`com.zeststream.omp-jev-route.process.v1` with `decision` in
`ranked | explicit | abstain | unavailable`. No roster → silence on this path.
Never blocks. `binding: log-only`.

### ACCEPTANCE

```bash
node work/omp-jev-route/src/cli.mjs decide --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
node work/omp-jev-route/src/cli.mjs gate --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs
```

`gate` must print `promoted: false`. The 6-row fixture is a contract oracle that
plants every loss class; always-abstain can beat it. That is the control working.

**NO-CLAIM.** Unpromoted. Not working-dogfood. Not a re-score of their corpus.
`diagnostic_synthetic` cannot promote.
