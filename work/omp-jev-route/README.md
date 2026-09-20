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
