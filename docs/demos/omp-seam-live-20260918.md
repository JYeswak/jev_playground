# The omp compaction seam, driven end to end with a live Jev call

`AGENTS.md` §4: *"if it is an omp seam: the seam fires in a real omp session, and a known-bad input
makes it refuse — reached rung ≥ L3, with the transcript or frame pasted."* This receipt records how
far that clause is now met, and exactly where it still is not.

## What ran

```bash
cd compaction
infisical run --projectId=… --env=prod --silent -- npx tsx ./live-probe.mjs
```

```
in 13 out 8 ms 1282
decision [["compacted","13 -> 8"]]
```

**One live call against `api.typesafe.ai`, model `jev-latest` → `jev-1.13.0`, 2026-09-18.** The key
came from Infisical through `infisical run` and never entered the tree, a log, or this file;
`live-probe.mjs` reads `process.env.TYPESAFE_API_KEY` and contains no literal.

The input is a **real omp transcript**, `fixtures/omp-session-big-20260917.jsonl`, through
`src/omp-adapter.ts`: 179 events in, 24 messages, 214 thinking characters dropped, 11 tool results
paired, 13 messages out. The binding then compacted those 13 to 8.

## The three paths, and which are proven

| path | driven by | result |
|---|---|---|
| **success** | live Jev, real transcript | **13 → 8 messages, 1,282 ms** |
| **Jev outage** | throwing asker, real transcript | returns `undefined`, reports `passthrough:jev failure: jev is down` |
| **malformed envelope** | stub, no/empty messages | **refuses**, reports `refused:…` |

The middle row is the §4 *"known-bad input makes it refuse"* clause on real data: a dead Jev leaves
the transcript untouched and omp's own summarizer in charge. The third is the same property for a
malformed event.

## Installed, 2026-09-18, on Joshua's instruction

`.omp/hooks/pre/jev-compact.ts` is live. It loads in a real omp session, verified in **separate
non-interactive sessions** (`omp -p`) so a failure could not reach the conductor's own:

```
keyless   omp -p "…"                        -> HOOKLOADTEST2, no load error, registers nothing
keyed     infisical run -- omp -p "…"       -> KEYEDLOAD,     no load error, handler registered
```

**omp fails OPEN on a broken hook, and that is measured rather than assumed.** The first install
used a bare `fast-jev-compaction` specifier, which cannot resolve from `.omp/hooks/pre/`. omp
printed `Failed to load extension …` *and answered the prompt anyway*. The same class of mistake in
`pi` earlier today made every invocation fail. Fixed with a relative import to the package's `dist`
entry; the contrast is recorded because it is the reason this install was safe to attempt.

## What is still not L3

**omp now loads this binding, but has not fired it.** The hook registers in a real session; no real
`session_before_compact` event has yet reached it, because that needs a session long enough to
trigger compaction. Until one does, the handler's behaviour in production is inferred from the three
paths tested above, not observed. The envelope field names still
come from omp's in-session docs rather than a type on disk, because omp ships as a compiled binary.

That install is deliberately gated to a human. A hook at `<cwd>/.omp/hooks/pre/` runs inside the
agent that would have to repair it, and earlier today installing an untested extension into `pi`
made every invocation fail while the documented removal reported success without fixing it.

**So the honest rung is L2+: the seam's logic is proven against real data and a live model, and the
loading half is unproven.** Calling this L3 would be the claim §4 exists to prevent.

## No-claim

- **One call, one transcript, one model version.** Nothing here measures compaction quality: 13 → 8
  is a reduction, not evidence that the eight retained messages are the right eight.
- No latency distribution — 1,282 ms is a single sample including client construction.
- The live **success** path has no committed test, because a test that spends money on every run is
  not a test this suite should own. It is a probe, run deliberately, receipted here.
- `live-probe.mjs` is committed so the run is reproducible, and it **refuses to do anything without
  `TYPESAFE_API_KEY` in the environment**.

## 2026-09-19 — the hook fired in production, and reached L3

Joshua ran a handful of tests and then `/compact`. The hook fired. Five real
`session_before_compact` events later, every assumption this lane held about omp's contract had
been replaced by an observed one. The full progression, each line read from `~/.jev-compact.log`:

| # | decision log line | what it falsified |
|---|---|---|
| 1 | `refused: no messages on the event envelope` | `event.messages` — the documented field — does not exist |
| 2 | `refused: ... envelope keys: type,preparation,branchEntries,customInstructions,signal` | found the real one: `preparation.messagesToSummarize` |
| 3 | `passthrough: ... 'tool of message.toolUses'` | omp's live messages are not `fast-jev-compaction`'s `Message` |
| 4 | `refused: adapter yielded 0 of 1; role=custom parts=string` | `content` can be a bare string; `role` can be `custom` |
| 5 | `passthrough: below minimum reduction: 0% reduction; no tool calls` | nothing — the path runs and declines on the merits |

**The fail-safe property was tested by production, not by us.** The hook was wrong four times in a
row and omp's own summarizer handled every one of those compactions. No transcript was touched.

**Why line 5 is a correct answer and not a failure.** `messagesToSummarize` carries the *older
prefix* omp has chosen to summarize — not the whole session. In a one-shot `omp -p` run that prefix
is a single user message, and this compactor's savings come from tool results and thinking blocks.
Zero tool calls means zero to remove. A run deliberately built to make eight tool calls produced
the same line, which is the useful finding: the tool-call turns were in `recentMessages`, which a
hook **must not** compact, because omp intends to keep them verbatim.

### Rung

**L3 reached** — the seam fires in a real omp session, and known-bad input makes it refuse.
**L4 (a real transcript measurably shrunk in production) is NOT reached** and cannot be reached
from `omp -p`: it needs a long interactive session whose older prefix contains tool calls. The hook
is installed and logging, so the next such `/compact` will record it either way.
