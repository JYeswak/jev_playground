# Draft upstream issue: semantic `omp find` has no bounded cascade budget

Status: **DRAFT / NOT FILED**
Bead: `jev-l824`

## Summary

`omp find` enables semantic judging through the native `judge` role and runs a fixed three-wave
cascade. The documented caps are 128 filename candidates, 20 files, 24 windows/file, 8 KiB
windows, 384-byte sketches, and 40 verified passages, with 16 requests in flight. There is no
user-facing candidate-count, files-read, snippet-length, or fast-cascade setting.

Existing organic session metadata shows 1,889 native `provider=typesafe`, `purpose=find` calls:

- input tokens p50 5,423; p95 9,002; max 15,637;
- no call near 28k or over the 32,768-token limit;
- Jev latency p50 5,867 ms; p95 28,099 ms; max 128,944 ms;
- recorded existing spend $0.410455038.

This rules out a single oversized state as the primary cause. The fixed cascade and parallel
request waves are the remaining measured design suspects.

## Minimal live queue probe

The probe was committed before the live calls in `work/jev-l824-probe`:

- model: `jev-1.13.0`;
- state source: `docs-mirror/typesafe/llms-full.txt`, first 18,000 bytes;
- source SHA-256: `278de4c82484f1535f332c4b6bf0056b39f48aa434431ccdf963230a5f9ec566`;
- actual input: 5,008 tokens/call (100,160 input tokens per arm);
- question: one fixed relevance Noul;
- 20 sequential calls versus 20 calls dispatched with a maximum of 16 in flight.

Final committed-state run:

| Arm | Calls | Call latency p50 | Call latency p95 | Arm wall | Input tokens | Spend |
|---|---:|---:|---:|---:|---:|---:|
| Sequential | 20 | 134 ms | 297 ms | 3,164 ms | 100,160 | $0.004206720 |
| Concurrent, max 16 | 20 | 337 ms | 529 ms | 532 ms | 100,160 | $0.004206720 |

The concurrent arm raises per-request p50 by about 2.5x and p95 by about 1.8x, while reducing
batch wall time by about 6x. This is a raw System One queue/service probe, not a replay of
`find`'s three request waves and not a ranking test.

A first undersized 10,000-byte state run was also made before the committed state was resized:
20 sequential + 20 concurrent calls, 57,600 input tokens per arm, $0.004838400 total. Total
spend across both probe runs: **$0.013251840**. The final 18,000-byte-state run is the result to
use for the queue comparison.

## Why this points at an omp knob

The native docs identify `find.enabled` (`auto|on|off`) as the only documented semantic-find
switch. `omp find --help` has no cascade-budget flags. Turning semantic find off would remove
Jev but also remove semantic ranking, so it is a latency escape hatch, not a smaller equivalent
configuration. The probe shows that 16-way concurrency is not free even for one 5,008-token
request; a three-wave cascade multiplies that behavior.

## Requested change

Expose a bounded, backward-compatible find budget, for example:

```yaml
find:
  enabled: auto
  maxFilenameCandidates: 128
  maxFilesRead: 20
  maxVerifiedPassages: 40
  maxInFlight: 16
  mode: full # fast | full | lexical
```

The exact names are suggestions, not a local claim about omp's implementation. A `fast` mode could
reduce candidate/files/passages caps while retaining the same lexical pre-ranking and output shape.
Every result should report the active budget, request count, input tokens, API aggregate time, wall
time, and whether requests were pruned. A config change must be evaluated on a paired corpus with
ranking agreement and latency; this draft does not supply that ranking result.

## Reproduction

```bash
python3 scripts/find-latency.py --robot
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/jev-l824-probe/probe.mjs
```

The first command reads local session metadata only. The second uses the pinned model and reports
its own input tokens, latency, and spend without printing state or secrets.

## Boundary

This is a draft issue, not a filed issue and not a Jev quality ruling. The probe measures transport
queueing on one real sourced state; it does not prove that every `find` request has the same service
time or that a reduced cascade preserves ranking. The project made no omp configuration mutation.
