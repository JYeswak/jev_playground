# OMP Extension Inventory

Snapshot: 2026-10-13. This inventory classifies every file currently below `.omp/extensions`.

Evidence: `.omp/config.yml:39-42` names `<cwd>/.omp/extensions` as the native auto-discovery root; lines 84-108 are the explicit project `extensions` list. The OMP extension-loading contract (`omp://extension-loading.md`) says native discovery scans `.ts`/`.js` entries; explicit directories prefer `index.ts`, and configured directory scans do not include sibling files when an index entry exists.

| File | Status | Evidence |
|---|---|---|
| `.omp/extensions/jev-memory-filter.ts` | Loaded | Explicit path at `.omp/config.yml:108`. |
| `.omp/extensions/jev-memory-filter.test.mjs` | Not loaded | `.mjs` is not a native `.ts`/`.js` discovery suffix; no explicit entry. |
| `.omp/extensions/jev-longres-shadow.ts` | Native-discovered | Direct `.ts` under the native discovery root; not in the explicit list. |
| `.omp/extensions/jev-longres-shadow.test.mjs` | Not loaded | `.mjs` is not a native `.ts`/`.js` discovery suffix; no explicit entry. |
| `.omp/extensions/jev-review.ts` | Native-discovered | Direct `.ts` under the native discovery root; not in the explicit list. |
| `.omp/extensions/jev-gate.ts` | Loaded | Explicit path at `.omp/config.yml:107`. |
| `.omp/extensions/jev-classify.ts` | Native-discovered | Direct `.ts` under the native discovery root; not in the explicit list. |
| `.omp/extensions/jev-screen.ts` | Loaded | Explicit path at `.omp/config.yml:87`. |
| `.omp/extensions/jev-rerank.ts` | Loaded | Explicit path at `.omp/config.yml:85`. |
| `.omp/extensions/jev-flag.ts` | Loaded | Explicit path at `.omp/config.yml:86`. |
| `.omp/extensions/jev-claim-check.ts` | Loaded | Explicit path at `.omp/config.yml:88`. |
| `.omp/extensions/kit-guard/index.ts` | Loaded | `.omp/config.yml:89` names the directory; configured directory resolution prefers `index.ts`. |
| `.omp/extensions/kit-guard/policy.ts` | Loaded dependency, not entry | Imported by `kit-guard/index.ts`; not independently discovered or configured. |
| `.omp/extensions/kit-guard/kit-guard.test.ts` | Not loaded | The configured directory resolves to `index.ts`; this sibling test is not an entry. |

`.omp/extensions/fixtures/` is empty; it currently contains no file to classify.

`jev-skill-hint.ts` and its test are outside `.omp/extensions`, under `work/jev-35sg/`; the inventory row in `work/jev-inventory/expected.json:113-122` remains `expect: off` and points to that path. The skill-veto extension and test moved to `work/wbel/` in commit `1b8ea68b`; the current `.omp/config.yml` and extension tree contain no skill-veto entry. Its log `/Users/josh/.local/state/jev/skill-veto-shadow.jsonl` had positive-control count 191 for `[2026-10-04T17:00:20Z,2026-10-05T17:00:20Z)` and count 0 for the last complete 24-hour window `[2026-10-12T00:55:01Z,2026-10-13T00:55:01Z)`.

Hint-log positive control is 838 for `[2026-10-04T00:22:08Z,2026-10-05T00:22:08Z)`. Current tmux/OS mapping resolves pane 0.3 (`%22`, shell PID 37518) to its OMP child PID 37569. Other current OMP processes: pane 0.1 `%20` PID 84233; pane 0.2 `%21` PID 37538; pane 0.4 `%23` PID 37605; pane 0.5 `%25` PID 37625. `ps` reports local MDT starts; converted to UTC, PID 84233 started `2026-10-12T14:39:54Z` and the other four started `2026-10-12T01:39:15Z`. Thus all currently observed OMP sessions postdate the 2026-10-05 cutover, and pane 0.3 identity is resolved. The required 24-hour zero-row window after the latest start, `[2026-10-12T14:39:54Z,2026-10-13T14:39:54Z)`, is incomplete as of `2026-10-13T00:55Z`; the earlier query using local starts as UTC is not valid AC2 evidence. Do not claim AC2 closure until the full interval has elapsed and its count is 0.
