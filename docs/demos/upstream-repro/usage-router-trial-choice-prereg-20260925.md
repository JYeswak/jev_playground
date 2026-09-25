# Usage router on real traffic: one Choice, three repeats (jev-vbh.4), preregistered 2026-09-25

Frozen before any Jev call. The trial reports measurements against the thresholds below. It
writes no ruling.

## What is asked

`work/jev-usage-router/src/router.mjs` asks one Jev Choice per goal: `local | research | browser |
bypass`, with the router's own `CRITERIA`, `INSTRUCTIONS` and `routeState()` (exported so the
trial sends the exact request the router sends), model `jev-1.13.0`. Policy is the router's:
the action is the choice when confidence >= 0.55 (`config.json` `confidenceFloor`), else `bypass`.

## Corpus: non-authored, labelled by what the agent did

`work/jev-usage-router/harvest_goals.py 2026-09-25T13:00:00Z` writes
`work/jev-usage-router/goals-2026-09-25.jsonl`, sha256
`0d6445dd0e39fa9c7a61e27fc537832aaabf5d268c87a83d60496f1e73a3fd12`: 2,307 goals from 2,812 user
messages in jev's omp sessions (dropped: 305 duplicates, 178 longer than 4,000 characters, 20
private, 2 secret). Each goal is labelled by the tool calls the agent made before the next user
message: `browser` (eval driving browser./tab./computer.), `research` (web_search, a read of an
http(s) URL, curl/wget of a URL), otherwise `local`.

| label | goals | prevalence |
|---|---:|---:|
| local | 2,213 | 95.9% |
| research | 89 | 3.9% |
| browser | 5 | 0.2% |

Short goals (under 200 characters) that were not local: 19, all research. This is the fresh
analogue of the shadow's trap-short class.

## Sample

All 94 non-local goals, plus 94 local goals drawn by a seeded shuffle (mulberry32, seed
20260925, over local goals in file order, first 94). 188 goals, 3 repeats each, 564 requests.
The trial refuses to run if the corpus sha256 differs from the one above.

## Measurements

1. **Incoherent verdicts**: answers the client refuses as off-label or malformed
   (`askJevChoice` reason `no-answers`). Acceptance: 0.
2. **Drift**: goals whose raw choice differs across the 3 repeats. Reported as a count.
3. Per label, the distribution of policy actions (`local`, `research`, `browser`, `bypass`).
4. **Non-local recall**: a research or browser goal routed off local (research or browser).
   **Local false-route rate**: a local goal routed to research or browser.
   **Precision of an off-local route at corpus prevalence**: recall x p / (recall x p + false-route
   x (1 - p)) with p = 94 / 2,307.
5. The same numbers for two baselines on the same 188 goals: always-local, and a lexical rule frozen
   here: `browser` if the goal matches `/\b(browser|click|screenshot|booking|book a)\b/i`, else
   `research` if it matches `/https?:\/\/|\b(web|search|online|internet|arxiv|leaderboard|published|latest|look up|google|browse|website|download)\b/i`,
   else `local`.
6. **Short non-local cell (19 goals)**: routed off local or abstained (`bypass`), on the majority
   action over repeats. The shadow's reversal threshold is 5 of 6, 0.833. The trial states whether
   Jev and the lexical rule each reach it.

Transport failures (timeouts, 5xx) are counted separately and excluded from 3–6. Three
consecutive 401 or 402 answers stop the run. `scripts/key-status.py` runs first and must print OK.

## NO-CLAIM

The label is what the full agent did in these sessions, so agreement measures Jev against the
incumbent agent's own routing, not against what a goal needed. Browser has 5 goals; its numbers
are descriptive. The sample is stratified, so raw agreement on it is not agreement at corpus
prevalence; item 4 converts it. Goals include pane 1's own dispatch messages (337 of 2,307); the
trial reports them separately.

## Run

```bash
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types work/jev-usage-router/trial-choice.mjs
```

## Result (live, 2026-09-25, jev-1.13.0, run after the text above was written)

`KEY: OK`, then 564 requests over 188 goals, 0 stops. Rows (no goal text):
`work/jev-usage-router/trial-rows-2026-09-25.jsonl`, each with `code_sha256` and
`recorded_at_utc`. Latency p50 176 ms, p95 287 ms. The goal corpus stays uncommitted because it
holds session text; its sha256 above pins it, and `harvest_goals.py` regenerates it on this machine.

| measurement | Jev (majority of 3) | always-local | lexical rule |
|---|---:|---:|---:|
| incoherent verdicts | **0** / 564 | - | - |
| transport failures | 0 | - | - |
| goals whose choice drifted across repeats | **4** / 188 | - | - |
| non-local recall (94 goals) | 12 / 94 = 0.128 | 0 | 32 / 94 = 0.340 |
| local false-route rate (94 goals) | 0 / 94 | 0 | 11 / 94 = 0.117 |
| precision of an off-local route at p = 0.0407 | 1.0 (0 false routes observed) | - | 0.110 |
| short non-local: routed off local or abstained (19) | 13 / 19 = 0.684 | 0 / 19 | 4 / 19 = 0.211 |
| reaches the 5-of-6 threshold (0.833) | no | no | no |

Actions by label: local goals 76 local / 18 bypass; research goals 55 local / 26 bypass / 7
research / 1 browser; browser goals 4 research / 1 bypass. The 19 short non-local goals split 6
local, 11 bypass, 1 research, 1 browser, so most of the 13 are abstentions, not routes. On the
75 long non-local goals: 49 local, 16 bypass, 10 research. Of the 29 sampled goals pane 1 wrote
(17 non-local), none was routed off local.

What this shows, within the NO-CLAIM above: with the router's own question and floor, Jev almost
never sends a goal off local that the agent kept local (0 of 94), and it sends most goals the agent
took to the web back to local (55 of 89 research goals). The shadow's reversal threshold for
honouring the router's action is not reached on this fresh set, so the router stays in shadow mode.
