# /tmp evidence census — 2026-09-24 (bead `jev-iv9w`)

RedMaple (pane 2). Every `docs/demos/upstream-repro/*.md` citation of a `/tmp` file
ending in `jsonl`, `json`, `csv`, or `tsv` was listed, then classed. Class (a) is
rows, scores, or the file a headline number was computed from. Class (b) is verifier
scratch, a plant, a regenerable dump, or a negative-control path. Class (c) is
deliberately uncommitted (private text or a receipt that said not to commit it).

Rescued files were copied with `cp` and checked with `cmp`. `/tmp` copies were not
deleted. Stage 30 is `foundation/gates.d/30-no-secrets.sh`.

## Already in the tree before this census

| Receipt | Citation | Class | Exists | Action |
|---|---|---|---|---|
| `jev-question-writing-w74-20260923.md` | `/tmp/w74-main.jsonl` | a | yes | already committed at `6d5f9da` as `work/jev-question-writing/w74-scores.jsonl`, `cmp` equal, sha256 `bc1a9bc28cb59bd1a266a37a05b101aba852974219970c05df7e47b77994aff1` |
| same | `/tmp/w74-split.jsonl` | a | yes | already committed as `work/jev-question-writing/w74-lingspam-split.jsonl`, `cmp` equal, sha256 `181dd05b5ee27e92b38e71e79ca6cf7970d856f85d196c480828ee0399f394a6` |


## Rescued this pass (class a, file still existed)

| Receipt | Citation | Tree path | sha256 |
|---|---|---|---|
| `Canny-w70-20260923.md` | `/tmp/canny-w70/t4.json` | `work/tmp-rescue/canny-w70-t4.json.exact` | `32a6ee933e76c56186c63117f70c44441636c557e214a18fa298a404a3d8f9fe` |
| `canny-ledger-stop-20260924.md` | `/tmp/canny-ledger-measure/scored.jsonl` | `work/tmp-rescue/canny-ledger-scored.jsonl` | `be928b7f52c622bb86cdb3f03af16ffc27f1f40ff8b2cfd19f8f4c0e062db595` |
| `jev-benchmark-w70-2026-09-23.md` | `/tmp/w70jb/t4.jsonl` | `work/tmp-rescue/jev-benchmark-w70-t4.jsonl` | `110d22d9fbaf35694e520b87e9cca655436463d1d172b82d3e4db18270e0ed57` |
| `oracle-kit-select-report-20260923.md` | `/tmp/jev-8q77-rows.jsonl` | `work/tmp-rescue/jev-8q77-rows.jsonl` | `b895bf95d1dbe735aca7dfc8c24bbd7b47e1fd2557bae66f15082de0f8b0a7f2` |
| `commit-miner-w70-20260923.md` | `/tmp/cm-w72/results.jsonl` | `work/tmp-rescue/cm-w72-results.jsonl` | `3285458b3a0bb5b36e8d6309cd6ee44830624732a82d1ece74b8956f1a4c54c8` |
| same | `/tmp/cm-w72/corpus.json` | `work/tmp-rescue/cm-w72-corpus.json.exact` | `267181e3616100085a8cd737784afa5850a57f78ec49fb228e88b350b3cebdf8` |
| same | `/tmp/cm-w72/t8set.json` | `work/tmp-rescue/cm-w72-t8set.json.exact` | `6eba80ff6109499622c913a7fd333ec9c51e77ebd3614ac1ad6fbcb662c096f3` |
| `nev-rerank-live-20260924.md` | `/tmp/k9z1-scores.jsonl` | `work/tmp-rescue/k9z1-scores.jsonl` | `c1bc3f6ba680172eb4da91e89ea2b0cc941a8f60796a67eb8703d02c1b166413` |
| `omp-jev-review-detgate-20260924.md` | `/tmp/ompfit/drawlive.jsonl` | `work/tmp-rescue/ompfit-drawlive.jsonl` | `e2cb533deb5e18d838fd1f912e8d7fca45c510b3ee03cb9aa79c331536589871` |
| `jev-curate-w70-20260923.md` | `/tmp/w70-curate/quixbugs-15.jsonl` | `work/tmp-rescue/quixbugs-15.jsonl` | `dba9127994b8e2b79d8dd210b3e782e700e035183db4fbbb4df320034dbb9583` |
| `neo4jev-w70-20260923.md` | `/tmp/neo4jev-w70/labels.jsonl` | `work/tmp-rescue/neo4jev-w70-labels.jsonl` | `80712b783ad4fc67307e2b683d25e0e023c98412c1c511997c95b253686cfdc4` |
| `jev-drone-w70-20260923.md` | `/tmp/jev-drone-w70/live-calls.jsonl` | `work/tmp-rescue/jev-drone-w70-live-calls.jsonl` | `f6151ab9b667c1a81fad73aab8c38f4862a82521b7185a660f30637db4cea884` |
| `benchmark-examples-20260918.md` | `/tmp/typesafe-examples-stub-results.json` | `work/tmp-rescue/typesafe-examples-stub-results.json` | `95182972a287f0160954e6b7398be31162ad839500138105522e220ac20710dc` |
| `gate-observe-hook-20260924.md` | `/tmp/verifier2-l3.json` | `work/tmp-rescue/verifier2-l3.json` | `8dd87b454c7c16266e0a341ad2779888daa1c1f036803962483e2cddd6647d65` |
| `jev-codex-router-w70-20260922.md` | `/tmp/w70-codex-home/.codex/codex-router/jev-router-live.jsonl` | `work/tmp-rescue/jev-router-live.jsonl` | `f7570c73694bb52705923401cd105007f280fe4bc32734e69f1ede3ff483b1d7` |
| `bicameral-gate-hard-cases-prereg-20260924.md` | `/tmp/lfx-hc-labels.jsonl` | `work/tmp-rescue/lfx-hc-labels.jsonl` | `8ce45df0bd4d4b427dd6eb41f4a4e162848d89bb924416e2d2fbbe6040f89a9f` |

README claim that depended on a rescued file: tool-call risk triage, keyword rule 58/60 against Jev 52/60, cites `jev-benchmark-w70-2026-09-23.md`. The rows are now in the tree.

## Class (a) withheld

| Receipt | Citation | Exists | Why not committed |
|---|---|---|---|
| `Canny-w70-20260923.md`, `canny-ledger-stop-20260924.md` | `/tmp/canny-w70/rows.jsonl` | yes | `message` is session text, not a licensed corpus. Scores for the 9/24 recount are in the committed t4 file. `/tmp` copy stays. |

A scanner match of `sk-` in that file was a word fragment (`task-sk-…`), not a key value. It was not committed.

## Class (a) gone — NOT RE-SCORABLE

| Receipt | Citation | README claims |
|---|---|---|
| `commit-miner-20260918.md` | `/tmp/tr/mine-out/jev-130.csv` | none found |
| `waved-s19-taste-contracts-20260920.md` | `/tmp/taste-audit.json` | none found |
| `omp-session-entry-adapter-20260919.md` | `/tmp/jev-0c6-real-replay.json` | none found |
| `jev-align-20260919.md` | `/tmp/jeva-ours/failure-cases.csv` | none found |

Each of those receipts now has a `NOT RE-SCORABLE — 2026-09-24` line.

## Class (b) and (c), not rescued

| Citation | Class | Exists | Why |
|---|---|---|---|
| `/tmp/commits.jsonl` | b | no | receipts say `node work/commit-mine/mine.mjs` rebuilds it |
| `/tmp/organic-fires-full.json` | c | no | `commit-learnings-20260919.md` says deliberately not committed |
| `/tmp/lfx-k3k-rows-haiku.jsonl` | b | yes | receipt calls it scratch left in place |
| `/tmp/sr-ws/manifest10.json`, `case-task.json`, `case-neg.json`, `/tmp/sr-ctx-task.json` | b | yes | receipt says scratch, rebuild with the one-liner |
| `/tmp/definitely-not-here.json`, `/tmp/s2.tsv` | b | no | negative-control paths in a stranger check, not evidence |
| `/tmp/jeva-repro-venv-a/.../support-tickets.csv` | b | no | package sample data, reinstallable |
| `/tmp/ee_introspect.json` | b | no | command redirect, regenerable |
| `/tmp/dcg-joined.json` | b | no | named inside a command list, not a score file |
| `/tmp/prism-w70-rows.jsonl`, `/tmp/ad-w70-unlabelled.jsonl`, `/tmp/jev-drone-w70/seeds-unlabeled.jsonl` | b | yes | prevalence inputs, 1–3 rows, unlabelled or not the headline scores |
| `/tmp/canny-w70/extract.mjs`, `/tmp/canny-ledger-measure/extract-all.mjs`, other `*.py`/`*.mjs` under `/tmp` | b | mixed | drivers and plants. Headline bytes are the json/jsonl rows above, not these scripts |
| `/tmp/idx.txt`, `/tmp/dir.txt`, `/tmp/secrets.txt` | b | no | shell one-liners or a command being scored, not a receipt's evidence file |

NO-CLAIM: this census covers file citations matching `jsonl|json|csv|tsv` plus the classes above. It does not copy plant directories (`/tmp/ad-w70-plant2`, `/tmp/bicameral-defect`). A non-author should spot-check 5 rows of the rescued table with `cmp`.

The three `.json.exact` files are the `/tmp` bytes plus one trailing newline. The commit hook refuses a text file that does not end in a newline, so a full `cmp` against `/tmp` fails by that one byte. Every other rescued file `cmp`s equal. For these three, `committed[:-1] == /tmp` was checked before the commit.
