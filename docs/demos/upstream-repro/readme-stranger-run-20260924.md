# README.md, run the way a stranger would (bead `jev-lcf`)

ReadmeStrangerRun (background agent of pane 1), 2026-09-24. Keyless lane plus one live lane, model
pinned `jev-1.13.0`. One machine: macOS arm64 (M3 Ultra), Node v22.22.0, `/usr/bin/python3` 3.9.6.

## The question

Can someone who has never seen this repo clone it and run every command README.md tells them to run,
in the README's order, and get what the page says they will get? Tonight the public README carried a
broken hero line for seven hours and nobody had run it from a clean clone.

## How it was run

`work/readme-stranger-run/run.py` does the whole run and writes one JSONL row per command:

- **Clone.** `git clone --local` of the named ref into a fresh `mktemp -d`. No worktree.
- **Stranger environment.** HOME is an empty directory, so there is no `~/.omp` and no `~/.claude`.
  PATH is a bin dir holding only `node`, `npm` and `npx` (all three ship with Node), then
  `/usr/bin:/bin:/usr/sbin:/sbin`. The keyless pass passes no environment variable beyond
  PATH/HOME/LANG/TERM/TMPDIR/USER, so no key can leak in. `--with br` adds `br` once the README names
  it as a prerequisite.
- **Commands.** The runner extracts them from the clone's own README, in page order: every line of a
  `bash` fence, plus every inline code span that starts with `node`, `python3`, `bash`, `./scripts/`,
  `git clone`, `cd`, `npm` or `br`. Repeats run once, and every README line a command appears on is
  recorded. `git clone <github url>` runs verbatim as a real network clone in its own directory.
  The "What you can copy" JS block runs as `node --input-type=module -e`, with `text` defined and the
  result printed.
- **Live setup.** A command on a line about making "real calls" (`npm ci --prefix work/sdk`) is
  skipped by the keyless pass, so every offline claim has to hold without it. The live pass runs it
  first.
- **Live pass.** Runs under `infisical run --silent --projectId=… --` and passes through only
  `TYPESAFE_API_KEY`. It runs every demo whose table row links a live receipt, with `--live` added;
  every command whose README line says "mean to spend", with `--replay <path>` dropped; and the
  snippet.
- **Two extra rows per pass.** `git status --porcelain` after the pass (did the README's commands
  dirty a clean clone?), and whether every relative README link resolves in the clone.

Each command is recorded with its exit code (taken unpiped), wall time, and the first output line
matching error/fail/red/missing (the last line when rc is 0). Full logs stay in the run's
`mktemp -d`. Output is scanned for 40+ character tokens, which are redacted.

**Re-score any table below from committed rows, no key, no network:**

```bash
python3 work/readme-stranger-run/run.py --report work/readme-stranger-run/rows-keyless-postfix-20260924.jsonl
```

(Also `rows-keyless-20260924.jsonl` for before the fixes, and `rows-live-prefix-20260924.jsonl` /
`rows-live-postfix-20260924.jsonl` for the live lane.)

**Re-run from scratch.** Keyless: `python3 work/readme-stranger-run/run.py --ref <sha> --with br --out
rows.jsonl`, about 6 min, mostly `./scripts/sync-docs.sh` and the gates. Live: the same command under
`infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --`, with `--live` and
without `--with br`.

## Result

| pass | ref | rows | rc 0 | nonzero |
|---|---|---:|---:|---:|
| keyless, before fixes | `bbc600d` | 37 | 26 | 11 |
| keyless, after fixes (`--with br`) | `c3019ef` | 39 | 33 | 6, each a documented refusal or a filed bead (below) |
| live, before fixes | `bbc600d` | 20 | 2 | 18 |
| live, after fixes | `5250be4` | 22 | 21 | 1 (`cascade --live`, the divergence its own receipt records) |

The live post-fix pass ran at `5250be4`. The two README commits after it (`82ef55f`, `c3019ef`)
change prose only, not any live command.

### Every failure before the fixes, with its cause

| # | command (README line) | rc before | cause (file:line) | disposition | rc after |
|---|---|---:|---|---|---:|
| K9 | `node demos/compact/demo.mjs` (L39) | 1 | `demos/compact/demo.mjs` imports `fast-jev-compaction/dist/index.js`. That sibling clone is gitignored (`.gitignore:10`) and has to be built. | README row now reads `./scripts/bootstrap-compaction.sh && node demos/compact/demo.mjs`, which states the network build (`205f1ee`) | 0 |
| K26, K28, K30, K35; L1–L17, L19 | `node --test work/nev-injection/seat-guard.test.mjs`, `prevalence-check.mjs`, `measure-framing-flip.mjs`, the copy snippet, and every `--live` demo | 1 | `work/jev-client/src/index.ts:28` statically imported `../../sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs`. `work/sdk/` had no tracked manifest, so the SDK existed only on the author's machine and every importer crashed at load, keyless or not. | SDK import made lazy, and `work/sdk/package.json` + `package-lock.json` pin `@typesafe-ai/sdk` 0.6.0 (`1c6d23d`). A missing SDK is its own failure, `sdk-missing`, not `unconfigured` (`4ae90cd`). README L26 says to run `npm ci --prefix work/sdk` before real calls (`205f1ee`). | keyless: 0 / 2 / 2 / 0; live: 0 |
| K29 | `./scripts/sync-docs.sh --check` (L144, L176) | 1 | `.gitignore:63` keeps mirror bytes out of git by design. The README called the mirror present and the check a confirmation. | README says `./scripts/sync-docs.sh` fetches first (network, about 2.5 min) and the Commands table has that row (`205f1ee`) | sync 0, check 0 |
| K31 | `bash foundation/gates.sh` (L161, L175, L201) | 1 | The gates need `.beads/*.db`, which a clone lacks until `br sync --import-only` runs. With `br` supplied, four stages are still RED off the author's machine: 44 needs `ast-grep`; 50 and 60 need foundry `loop-kit` (`foundation/gates.d/50-house-gates.sh:30`, `60-staged-deletion-lane.sh:133`); 80 needs an omp install (`scripts/consumer-check.sh:39`). The same clone with the author's PATH and HOME passes 17/17, rc 0. | README says so plainly (`205f1ee`, `c3019ef`). Too large to patch here, so bead **`jev-fmy`** was filed. | `br` 0; gates 1 (13 PASS, 4 RED, named) |
| K36 | `git status` after the keyless pass | dirty | `work/nev-differential/analyze_diff.py:160` rewrote `DIFF-RECEIPT.json` with today's date on every unchanged re-score. | The date is kept when nothing else moved (`0fe1fae`). | DIFF-RECEIPT clean. The two MANIFEST.tsv files are now dirtied by `sync-docs.sh`; see `jev-goa`. |
| K37 | relative links | 18 missing: the cookbook directory link and 17 cookbook pages | Every cookbook link pointed into the gitignored `docs-mirror/`, so all of them were a 404 on GitHub. | Each one repointed to the `docs.typesafe.ai` URL its `docs-mirror/MANIFEST.tsv` row names; all 17 pages and the index returned HTTP 200 (`205f1ee`). | 0 missing of 48 |
| L9 (post, `205f1ee` pass) | `node demos/hierarchy/demo.mjs --live` | 1 in 0.25 s | `demos/hierarchy/demo.mjs:60-95`: `greedy`/`beam` read the live `scoreFn`'s Promise as probabilities, so `--live` routed on `undefined`. Its committed receipt (`7520249`) recorded that as model "DIVERGENCE". | `await` added (`9a08109`). Receipt and tally correction filed as **`jev-33x`**. | 0 (2/2 OK live) |
| L12 (post, `9a08109` pass) | `node demos/autoformat/demo.mjs --live` | 1 | `demos/autoformat/demo.mjs:55` asked "What kind of content is this block?" for every block without naming it. A one-call probe returned `code` for both a heading and a command. | The question names the block (`5250be4`). Receipt folded into **`jev-33x`**. | 0 (all 6 markers) |
| — | README L26 "Node 20 or newer" | — | With Node 20.20.2 (`/opt/homebrew/opt/node@20`) on a clean clone, `seat-guard.test.mjs`, `verify-claim.mjs` and `measure-framing-flip.mjs` all exit 1 with `ERR_UNKNOWN_FILE_EXTENSION ".ts"`. The guard demo passes. | README says Node 22.18 or newer, and why (`82ef55f`) | not re-run under Node 20 after the edit: the edit is prose |

The line numbers above (L39, L144, …) are from the pre-fix README at `bbc600d`. The post-fix table
uses the post-fix page.

### Nonzero rows left in the post-fix keyless pass, and why each is correct

| row | command | rc | why it stays |
|---|---|---:|---|
| 28 | `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label` | 2 | `rows.jsonl` is a placeholder for your own labelled rows (Method step 2). It fails with one clear line: `ENOENT … 'rows.jsonl'`. |
| 31 | `node scripts/measure-framing-flip.mjs` | 2 | README: "Run it only when you mean to spend." Without a key it refuses with the fix in the message. The live pass ran it: rc 0. |
| 33 | `bash foundation/gates.sh` | 1 | Four stages need the author's tools (above). README now says so. Bead `jev-fmy`. |
| 34 | `bash scripts/quickstart.sh --mine` | 2 | "The same questions on your logs." A stranger's empty HOME has no logs, and the script says exactly that. |
| 35 | `node demos/<name>/demo.mjs` | 1 | A template in the Commands table, not a runnable line. Every concrete demo is its own row. |
| 38 | `git status` after the pass | dirty | `./scripts/sync-docs.sh` rewrites the tracked `docs-mirror/MANIFEST.tsv` and `upstream/MANIFEST.tsv`, and re-pins `system-one-adapter-python` to `e1d4cc9` + `0bb819b` (two rows) where the commit pins `adffc2e`. Filed as **`jev-goa`**, with this evidence as a comment. |

Row 1 of the post-fix pass reports "DIFFERENT commit": by the time it ran, siblings had pushed past
`c3019ef` to `a8cbf6e`. The clone itself succeeded.

### Live lane after the fixes (`5250be4`)

- 21 of 21 commands exit 0 except `cascade --live`.
- `cascade --live` escalates `registration_open_date` at 0.76 and passes `location` at 0.18. That
  is the same divergence its committed live receipt records, and the demo exits 1 on it.
- `date --live` is not stable across passes: rc 1 at `205f1ee` and at `9a08109`, rc 0 at `5250be4`.
  Its one contested item, the kickoff call, sits at 0.33 against the 0.60 review cut. Model
  variance, not a defect.
- The copy snippet returned `ok=true injection=0.97` live, and `reason=unconfigured` keyless: the
  README's missing-key promise holds.
- `measure-framing-flip` moved 0.37 to 0.70 with 10 paired calls per arm. That is the same direction
  as the published 0.21 to 0.59, not the same points.

## Other evidence gathered on the way

- **`work/jev-client` tests** (with the SDK installed, which is how the repo's own gate runs them):
  `client.test.mjs` 30/30, `measure-kit` 4/4, `uncertain` 4/4. In a clone with no SDK, measured
  before the `sdk-missing` test existed, `client.test.mjs` passed 6 of 29: its transport tests
  drive the SDK. A fresh clone needs `npm ci --prefix work/sdk` before that file, as before this unit.
- **`timeout-leak.test.mjs` is flaky, before and after this unit.** A/B with 12 runs per arm, one
  scratch clone each, SDK symlinked, script `/tmp/rsr-timeout-ab.sh`:

  | client | passes |
  |---|---:|
  | `1c6d23d~1`, before the lazy import (first run) | 7/12 |
  | `1c6d23d~1`, repeated | 7/12 |
  | `1c6d23d`, lazy import, clock started before the SDK load | 12/12 |
  | working tree = the timing that `4ae90cd` ships (clock started after the load, as before the lazy import) | 6/12 |

  The 12/12 arm is unexplained: once the SDK is loaded, its only difference is one awaited
  already-resolved promise inside the timed window. I shipped the pre-change clock placement so
  `latencyMs` measures what it measured before, and did not tune the clock to pass a test.

  Cause: the test floor is `latencyMs >= 40` (`timeout-leak.test.mjs:35`), but `guardedFetch`
  aborts at `timeoutMs - 25` = 25 ms. Filed as **`jev-rw2`**. Another agent already has an
  uncommitted `guardDeadlineMs` hunk in `index.ts`; it is not mine.
- **A fresh full `./scripts/sync-docs.sh` works for a stranger:** 154–169 s across two passes, rc 0, then `--check` PASS
  114/114. It also clones `ripwire` into `$HOME/Developer`, which is the stranger's empty HOME here.

## Spend

Live calls are not metered by most demos. Totals below are calls **[INFERENCE]**, built from each
demo receipt's `call_count` (sum 70 over the 17 demos), plus framing-flip 20, jev-probe 1 and
snippet 1: 92 per full live pass.

| run | calls |
|---|---:|
| Full live passes at `205f1ee`, `9a08109` and `5250be4` | about 276 |
| Pre-fix live pass (only `jev-probe` got past the import) | 1 |
| Direct runs: hierarchy `--live` (about 10) + autoformat `--live` (2) + one autoformat probe (1) | about 13 |
| **Total** | **about 290** |

Tokens were measured only where printed: `jev-probe` shows 629 input tokens per call. No LLM
incumbent arm was run; this unit judges the README, not Jev.

## Commits (all path-limited, all pushed)

| sha | level | what |
|---|---|---|
| `1c6d23d` | [test] | jev-client lazy SDK import; `work/sdk/package.json` + `package-lock.json` pin 0.6.0 |
| `0fe1fae` | [test] | analyze_diff keeps the receipt date on an unchanged re-score |
| `205f1ee` | [test] | README: SDK setup, compaction bootstrap, sync-docs fetch, `br` import, 17 cookbook links; the runner |
| `4ae90cd` | [test] | `sdk-missing` failure reason plus its no-SDK-layout test; TESTS.md row |
| `9a08109` | [live] | hierarchy demo awaits live scores |
| `5250be4` | [live] | autoformat demo names the block in each question |
| `82ef55f` | [test] | README: Node 22.18 or newer |
| `c3019ef` | [test] | README: the gates' machine prerequisites, and `jev-fmy` |

Two corrections to commit subjects, which cannot be amended:

- `9a08109` says "4 calls". The call count was not measured. The demo's structural count, per its
  receipt, is 10.
- `205f1ee` says "cookbook links" without a count. It is 17 links plus the directory link.

## Beads filed

- `jev-33x`: re-record the hierarchy and autoformat live receipts, which record demo bugs as model
  divergence. Then correct `demos/LIVE.md` and the README's "8 of the 17" tally.
- `jev-rw2`: the `timeout-leak` test floor sits above `guardedFetch`'s own deadline.
- `jev-goa`: a fresh `sync-docs.sh` re-pins `system-one-adapter-python` and dirties both MANIFEST files.
- `jev-fmy`: `foundation/gates.sh` is not runnable off the author's machine.

## Boundary (NO-CLAIM)

- One machine, macOS arm64, Node v22.22.0. Linux and Windows were not run. Node 20 was run only to
  measure its failure. Node 22.18 as the lowest working version comes from Node's release notes
  (type stripping on by default); no version between 20.20.2 and 22.22.0 was run here.
- The GitHub clone was checked as a clone only (row 1). Every other command ran in a
  `git clone --local` of the named ref, at the same commit as GitHub at the time, except where row 1
  says otherwise.
- The stranger environment is simulated: an empty HOME, a cut PATH. `/usr/bin` still holds macOS's
  stock `git`, `curl` and `python3`. The machine is not factory-fresh.
- Live results come from 1 to 3 passes of 1 to 20 calls per command. They are smoke tests, not
  measurements. Nothing was compared against an LLM arm.
- `bash foundation/gates.sh` passing 17/17 was measured once with the author's PATH and HOME, on a
  fresh clone after `br sync --import-only`. That is not a stranger's result.
- Not run: `./scripts/sync-docs.sh --docs-only` as a README command (the README does not name it),
  and anything in `demos/START.md` or `demos/LIVE.md`.

## For a spot-checker (three random rows)

Pick any three rows from `rows-keyless-postfix-20260924.jsonl` or `rows-live-postfix-20260924.jsonl`.
Re-run each command verbatim in a fresh `git clone --local` at the row's `sha`, with HOME empty and
PATH cut as described above (live rows under Infisical). Compare the exit code and the recorded
line. A mismatch on `date --live` or `cascade --live` is model variance; see above. Scratch left in
place for Joshua: `/tmp/rsr-timeout-ab.sh`, `/tmp/rsr-beads.sh`, and the run directories
`$TMPDIR/readme-stranger-*` and `$TMPDIR/tmp.*` (clones and logs).
