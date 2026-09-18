# jev_playground

Measure what Jev can actually do before you build on it.

![What this lane has proven so far](visual/hero.jpg)

## Install

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
./scripts/sync-docs.sh          # fetches the primary sources; safe to re-run
./scripts/sync-docs.sh --check  # verifies every mirrored byte against MANIFEST.tsv
```

No API key needed to install, and none to run the gates below.

## Try it in 60 seconds

```bash
bash foundation/gates.sh
```

```
PASS 10-fixture-integrity (0s)
PASS 20-receipt-freshness (0s)
PASS 30-no-secrets (0s)
PASS 40-omp-compact-replay (1s)
PASS 50-house-gates (0s)
PASS 60-staged-deletion-lane (4s)
PASS 70-tests-registry-sync (0s)
gates: ALL GREEN
```

Seven stages, no network, no key. Each one has a planted bad input that turns it red, listed in
[`GATES.md`](GATES.md). A gate that cannot fail is not a gate.

## What it does

- Mirrors the primary Jev sources locally, so every claim here cites bytes you can re-fetch
- Runs seven gates that each refuse a specific known-bad input, not a generic lint
- Records a receipt for every measurement under `compaction/runs/` and `foundation/runs/`
- Blocks any commit whose subject does not name how it was verified

## What you'll need

- `bash`, `git`, `curl`, `python3` — all preinstalled on macOS and most Linux
- A `TYPESAFE_API_KEY` in your environment **only** if you want to make live Jev calls.
  Everything above runs without one.

## What is not here yet

This is an evaluation lane, not a demo library. Read this section before you judge the repo by
its file count.

- **Zero installable demos have shipped.** The backlog is under `docs/demos/`, still being
  scored. A demo counts as shipped only with an install script, tests including a failing arm,
  a receipt, and an `EVAL.md` row.
- **14 usage patterns are mapped, not reproduced.** [`docs/demos/USAGE-MAP.md`](docs/demos/USAGE-MAP.md)
  cites 18 community repos at pinned SHAs. Those citations are transcriptions of other people's
  measurements. An open audit found 37 of 60 numeric claims across our own working files
  **unverifiable** against vendored source, and 4 flatly wrong. Both are filed, not hidden.
- **The community clones are read locally and never committed.** Provenance is tracked; their
  bytes are not.

## Verify it yourself

Every commit subject in this repo names its verification level. That vocabulary is fixed:

| Level | Means |
|---|---|
| `pending` | judgment only, nothing run |
| `selftest` | the thing's own selftest passed |
| `test` | re-derived by running a check that would fail if the claim were wrong |
| `mutation` | a planted defect turned it red, then byte-identical restore |
| `oracle` | an external arbiter agreed |
| `live` | observed against the real service or session |

```bash
git log --oneline -20          # every subject ends in a bracketed level
cat EVAL.md                    # each row carries its own Boundary: what it does not prove
cat NEGATIVE_EVIDENCE.md       # things tried, measured, and rejected, with retry conditions
```

`NEGATIVE_EVIDENCE.md` is the file worth reading first. It records what did **not** work and
what would have to change before trying again. Ten entries so far, including one where a green
eight-arm selftest proved a detector matched its own fixtures while asking the wrong question
entirely.

## How it works

Four surfaces, each independently checkable:

1. **Mirror** — `scripts/sync-docs.sh` vendors the doc site and the first-party SDKs at pinned
   SHAs. It is idempotent, never destructive, and fail-closed: an empty page set is an error, not
   a pass.
2. **Gates** — `foundation/gates.d/` holds one script per refused edge. `GATES.md` names the
   planted bad input for each, and where it is wired.
3. **Hooks** — `githooks/` enforces the verification level at commit time, and refuses a
   path-limited commit that would silently drop a staged deletion.
4. **Receipts** — every measurement writes JSON with its inputs, its counts, and its failures
   array. A claim with no receipt is not a claim.

## Why this exists

The measured lesson from the corpus is that a judgment model's single verdict is the weakest way
to use it. On one public benchmark, the verdict alone scores 62.6% while five signal questions fed
to a small fitted model reach 95.1% (`jev-phishing-bench`, cited in the usage map). So the
interesting question is never "is the model good" but "which question, asked how, with what
threshold, verified against what".

That question needs somewhere honest to ask it. A repo full of demos nobody checked adversarially
would answer it worse than no repo at all. So the honesty scaffolding landed before the first
demo, and a claim here is allowed to say `pending`.

## Who built this

[Joshua Nowak](https://github.com/JYeswak) builds verification substrate for AI systems that
have to be trusted by someone other than their author.

## License

MIT — see [LICENSE](LICENSE).
