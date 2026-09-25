# OMP `find` latency diagnosis — 2026-09-25

Bead: `jev-l824`
Model source: existing local omp session `model_usage` rows with `provider=typesafe`, purpose
`find`. No new Jev/API call was made for this investigation.

## Receipt

Command:

```bash
python3 scripts/find-latency.py --robot > var/agent-tmp/jev-l824-find-latency.json
```

The script reads local session metadata only and emits no query, path, snippet, or session text.

### Native Jev calls

| Metric | Result |
|---|---:|
| `purpose=find` calls | 1,889 |
| Input tokens p50 / p95 / max | 5,423 / 9,002 / 15,637 |
| Calls near 32k (`>=28k`) | 0 |
| Calls over 32k | 0 |
| Jev latency p50 / p95 / max | 5,867 ms / 28,099 ms / 128,944 ms |
| Recorded Jev spend | $0.410455038 |

The input-token distribution rules out the 32k state limit as the primary cause of the observed
find latency. The measured Jev time is itself large: p50 5.867 s and p95 28.099 s.

### Find tool-result rows

Only 59 session tool-result rows contained retained `find.details.stats`; these are a narrower
instrumented subset, not the 1,889-call denominator.

| Metric | Result |
|---|---:|
| Rows | 59 |
| End-to-end elapsed p50 / p95 / max | 1,069 ms / 4,358 ms / 7,557 ms |
| Aggregate parallel API milliseconds p50 / p95 / max | 2,998 ms / 8,049 ms / 46,439 ms |
| Input-token proxy p50 / p95 / max | 52,848 / 126,980 / 135,790 |
| File bytes p50 / p95 / max | 111,525 / 327,076 / 349,444 |
| Requests p50 / p95 / max | 12 / 23 / 30 |
| Rows with reported errors | 51 |

`apiMs` is the sum of parallel request durations, not wall time; it must not be divided into or
added to end-to-end latency. The tool stats show why the output-level and model-usage-level views
differ: the retained rows include failed/partial cascades and aggregate multiple requests, while
`model_usage` measures successful native Jev calls.

## What omp documents

Source: `omp://tools/find.md`, read before any configuration conclusion.

- `find.enabled` is the documented setting: `auto` (default), `on`, or `off`.
- `auto` enables semantic find only when the `judge` role resolves to a native TypeSafe Jev model.
- The cascade has fixed caps, not documented user knobs for a smaller candidate/snippet setting:
  - 128 filename candidates judged;
  - 20 files read;
  - 24 windows per file;
  - 8 KiB window;
  - 384-byte sketch;
  - 40 passages verified;
  - 16 requests in flight across three dependent waves.
- `omp find --help` exposes only query/path/keyword/hidden/json/quiet flags; no candidate-count or
  snippet-length flag exists.

## Diagnosis

Jev is a substantial part of native semantic-find latency. The state-size hypothesis is false for
this receipt: the 1,889 native calls have no input-token proxy at or above 28k. The expensive shape
is the fixed cascade—filename judging, sketch judging, and passage verification—not oversized
single states.

The only documented knob that removes this Jev cost is `find.enabled: off`; `on` forces the judge
whichever model resolves, and `auto` is the default native-Jev behavior. There is no documented
smaller candidate-count or snippet-length knob to tune. Turning semantic find off would change the
product from semantic ranking to lexical/native search, so a ranking-agreement number would not be
an honest “same find, smaller setting” comparison. No paired replay with the same query/corpus and
off setting is present in the captured session data.

The practical fix is therefore not a guessed token cap. OMP needs an upstream/config surface for a
bounded cascade budget—candidate cap, files-read cap, or a single-phase mode—before this lane can
measure a smaller semantic setting while preserving ranking. Until that exists, `find.enabled: off`
is the documented latency escape hatch, with an explicit quality tradeoff; `auto` remains the
current slow path.

## Boundary

This is a latency diagnosis, not a Jev quality ruling. No new live call, config mutation, ranking
comparison, or user-visible OMP change was made. The receipt does not join whether an agent opened
or edited a ranked result. The existing 1,889 rows are organic session evidence; the 59 detailed
find-result rows are the subset whose session transcript retained `find.details.stats`.
