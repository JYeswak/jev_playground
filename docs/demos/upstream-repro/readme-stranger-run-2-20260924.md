# README.md run as a stranger would, second pass (2026-09-24)

ReadmeStrangerRun (background agent of pane 1), 2026-09-24. Keyless lane only: no Jev key, no
Anthropic, xAI, OpenAI or OpenRouter key. The TypeSafe account was out of credits during this run,
and nothing here needed it. One machine: macOS arm64, Node v22.22.0, `/usr/bin/python3` 3.9.6.

## The question

The first pass ([`readme-stranger-run-20260924.md`](readme-stranger-run-20260924.md)) left the
README runnable. Since then, about ten re-score commands and many measurement sentences were added
to the page. Does every command still run on a fresh clone with no key? And does each re-score
command print the numbers the README cites beside it?

## How it was run

The runner is `work/readme-stranger-run/run.py`, the same one as pass 1, with two changes made for
this pass:

- **A cited-number check.** For every fenced command, it takes the README's `# comment` beside it,
  extracts each number (skipping digits inside names such as `Banking77`, `SST-5` or `grok-4.20`),
  and records which numbers the command's output does not contain, ignoring commas.
- **Where `git clone` runs.** Only the quick start's clone of this repo, and its `cd`, run in a
  separate directory. A `git clone` of a dependency the README names now runs inside the local
  clone.

The setup is the same as pass 1:
- `git clone --local` of the named commit into a new `mktemp -d`;
- HOME is an empty directory;
- PATH holds `node`, `npm`, `npx` and `br` (the README names `br` as a gate prerequisite) plus
  `/usr/bin:/bin:/usr/sbin:/sbin`;
- no environment variable is passed beyond PATH, HOME, LANG, TERM, TMPDIR and USER.

The quick start's `git clone` of the GitHub URL is a real network clone. In both passes it landed
on the same commit as the local clone. Every command's exit code is taken unpiped.

Rows, one JSON line per command:
- before the fixes, at `1bf5a12`: `work/readme-stranger-run/rows-keyless-run2-20260924.jsonl`;
- after the README fix, at `4d5f011`: `work/readme-stranger-run/rows-keyless-run2-postfix-20260924.jsonl`.

**Re-score, no key, no network:**

```bash
python3 work/readme-stranger-run/run.py --report work/readme-stranger-run/rows-keyless-run2-postfix-20260924.jsonl
```

To re-run from scratch, about 7 minutes (the gates and the doc sync dominate):
`python3 work/readme-stranger-run/run.py --ref <sha> --with br --out rows.jsonl`

## Result

| Pass | Ref | Commands | rc 0 | Nonzero |
|---|---|---:|---:|---:|
| before fixes | `1bf5a12` | 64 | 56 | 8 |
| after the README fix | `4d5f011` | 65 | 58 | 7, all expected (below) |

**Cited numbers.** Twenty-three fenced re-score commands carry numbers in their README comment,
101 tokens in all. The output contained every one of them, in both passes. For 82 of the 101 tokens
(those with two or more digits) that match means something. A single digit such as the `9` in `9/9`
matches almost any output, so the other 19 carry little weight.

Two things about this check:
- The pass-1 rows file was re-derived after the run, from the kept logs, using the fixed
  name-digit rule. The first version of the check had flagged `77` in `Banking77`, `150` in
  `CLINC150` and `4.20` in `grok-4.20` as missing.
- The pass-1 `4/4` on `variance.py` was hollow: that run printed only `NOT_RUN`, and its four cited
  tokens were single digits found in that message.

### What was wrong at `1bf5a12`, and what changed

| # | README line(s) | Finding | Cause | Disposition |
|---|---|---|---|---|
| 26 | L115 | `python3 work/nev-differential/variance-20260924/variance.py` exited **2** with `NOT_RUN: J1 source ... jev-sec-bench/results/injection.json is absent`. The README said this block "re-scores from committed rows with no key". | It reads the public bench's own results file, which is not committed. The scorer refuses honestly (`variance.py:100-106`). | README (`4d5f011`): the block now starts with `git clone https://github.com/Gaurav-Gosain/jev-sec-bench jev-sec-bench && git -C jev-sec-bench checkout fdb16b9` and says why. After the fix: row 24 rc 0 in 0.93 s, row 26 rc 0, and it prints both verdicts (grok-4 STANDS 9/9, Haiku PROVISIONAL 6/6). |
| 24 | L113, L200, L232 | `python3 work/nev-differential/analyze_diff.py` exited 0, but only on this machine. | `analyze_diff.py:9` hard-codes `JEV_SRC = "/Users/josh/Developer/jev/jev-sec-bench/results/injection.json"`. That absolute path exists here and not on a stranger's machine. It is the only README re-score script with such a path; I grepped every one. | Not my file: bead **`jev-x2kv`**, with `variance.py` as the fix pattern. README (`4d5f011`): the injection block says the script fails elsewhere until that bead lands. Method step 7 and the Commands row now point at `fresh-20260923/score.py`, which reads only committed rows. |
| - | L243 | Limitations said "one public corpus, one cut, one run". | Now three runs of Jev and grok-4 and two of Haiku (`jev-rf57`). | README (`4d5f011`): says so. |
| - | L262, L264 | Status said the injection comparison reproduces with no key, and that all seventeen stages pass. | The first needs the bench clone. The second is true on the author's machine; on a fresh clone plain `gates.sh` is rc 1 (row 59) and `--portable` is rc 0 with 4 skips (row 58). | README (`4d5f011`): both scoped. The `--portable` claim is registered (`gates-portable-fresh`, proof: this rows file). |
| 64 | - | `git status` after the pass: `upstream/MANIFEST.tsv` modified by `./scripts/sync-docs.sh`. | The ripwire row changes from `ripwire $HOME/Developer/ripwire f45087a7 60b65f02 479` to `ripwire upstream/ripwire 60b65f0 60b65f0 0`. The committed row names a path on the author's machine and a pin 479 commits behind, and a stranger's sync silently re-pins it. `--check` still passes (114 files, 23 clones). | Not my file: bead **`jev-27mx`** (the same class as the closed `jev-goa`, on another row). Still dirty after the fix (row 64). |

### Nonzero rows left after the fix, each expected

| # | Command | rc | Why it stays |
|---|---|---:|---|
| 50 | `python3 work/jev-claim-check/score-close.py` | 1 | Its bar failed (R83), and the README comment says it exits 1 for that reason. |
| 53 | `node work/jev-prevalence-first/prevalence-check.mjs rows.jsonl --truth label` | 2 | `rows.jsonl` is a placeholder for your own labelled rows. It fails with one clear line. |
| 56 | `node scripts/measure-framing-flip.mjs` | 2 | It needs a key and says so: `ERROR no key in env. Run under: infisical run ...`. |
| 59 | `bash foundation/gates.sh` | 1 | Four stages need the author's tools; the README says so and points to `--portable` (row 58: rc 0, `GREEN WITH 4 SKIPPED`). |
| 60 | `bash scripts/quickstart.sh --mine` | 2 | "The same questions on your logs". An empty HOME has no logs, and the script says so. |
| 61 | `node demos/<name>/demo.mjs` | 1 | A template in the Commands table, not a runnable line. |
| 64 | `git status --porcelain` after the pass | dirty | `jev-27mx`, above. |

## Commands that need a key, run without one

This checks the rule that a key-needing command must say so and exit nonzero, never print a score.
It covers every README command that needs a key: `jev-probe` without `--replay`,
`measure-framing-flip`, and `--live` on each of the 17 demos with a live receipt. All were run in
the pass-1 clone with no key (script `/tmp/rsr-keyneed.sh`, left in place). None printed a score.

At `1bf5a12`:
- 13 demos and both scripts exited 2 and named the missing key.
- rag, chief, consistency and consistency-noul printed `live lane: NOT_RUN` but exited **0**.
- compact exited **1** on an uncaught throw.

Pane 1 assigned that fix to me as bead **`jev-6smc`**. It landed in `77ff903` `[mutation]`:
- The five demos now exit 2 with `live lane: NOT_RUN — <reason>`, for both `unconfigured` and
  `sdk-missing`.
- A new test, `demos/test/live-refusal.test.mjs`, finds every demo whose source parses `--live`
  (17 today). With no key it requires rc 2 plus a stated reason on `--live`, and rc 0 on the
  recorded lane. It passes 18/18.
- Planting `process.exit(0)` back into rag turned exactly the rag case red. The file was restored
  byte-identical (sha256 `81a7456e…` before and after).
- Against the pre-fix demos (a scratch clone of `c99310d` with the test copied in), exactly chief,
  compact, consistency, consistency-noul and rag are red.

## Commits

| sha | Level | What |
|---|---|---|
| `4d5f011` | [test] | README: injection re-score needs the pinned bench; `analyze_diff.py` path caveat (`jev-x2kv`); Method and Commands use the committed-rows scorer; Limitations and Status corrected; the runner's cited-number check; pass-2 rows; one claim registered, floor 42/76 to 43/77 |
| `77ff903` | [mutation] | jev-6smc: five demos exit 2 on a keyless `--live`, plus the refusal test and its TESTS.md row |

Beads filed for other files: `jev-x2kv` (analyze_diff's absolute path) and `jev-27mx` (the
sync-docs ripwire re-pin).

## Boundary (NO-CLAIM)

- **One machine.** macOS arm64, Node v22.22.0. The stranger environment is simulated: `/usr/bin`
  still carries macOS's git, curl and python3.
- **No live calls.** The TypeSafe account had no credits and the Anthropic account was capped;
  nothing here needed either. No `--live` lane was measured, only its refusal without a key.
- **The cited-number check is a substring test.** It shows the output contains each cited number,
  not that the number sits in the row the sentence means. The 82 multi-digit matches are the
  meaningful part. This pass did not re-check the prose sentences in Measurements against their
  receipts; stage 15's claims registry covers those (145/145 enforced rows passed at `4d5f011`).
- **`analyze_diff.py` exits 0 in both passes** only because this machine has the author's absolute
  path. That result is not a stranger's; `jev-x2kv` tracks it.
- **Scratch left in place:** `/tmp/rsr-keyneed.sh`, `/tmp/rsr-bench-probe.sh`,
  `/tmp/rsr-recite.py`, `/tmp/rsr-6smc*.{py,sh}`, `/tmp/rsr-rag-demo.mjs.bak`, and the run
  directories `$TMPDIR/readme-stranger-*` (logs) and `$TMPDIR/tmp.MW977YAxS6`.
